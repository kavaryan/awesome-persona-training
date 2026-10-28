"""Deterministic discovery channels; keyword matches generate leads, never verdicts."""

import os
import re
from datetime import date, timedelta
from urllib.parse import quote

import feedparser

from .store import canonical_url

OA = "https://api.openalex.org"


def reconstruct_abstract(index):
    if not index:
        return ""
    positions = {p: token for token, places in index.items() for p in places}
    return " ".join(positions[p] for p in sorted(positions))


def oa_record(work, provenance):
    loc = work.get("primary_location") or {}
    url = loc.get("landing_page_url") or work.get("doi") or work["id"]
    locations = [work.get("best_oa_location") or {}, *work.get("locations", [])]
    oa = next((x for x in locations if x.get("is_oa") and x.get("pdf_url")), {})
    ids = work.get("ids") or {}
    return {
        "url": canonical_url(url),
        "title": work.get("title") or "",
        "date": work.get("publication_date", ""),
        "doi": work.get("doi") or "",
        "openalex": work["id"],
        "aliases": [v for v in ids.values() if v],
        "authors": [a["author"]["display_name"] for a in work.get("authorships", [])],
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
        "pdf_url": oa.get("pdf_url", ""),
        "license": oa.get("license") or "unspecified",
        "provenance": [provenance],
        "referenced_works": work.get("referenced_works", []),
    }


def oa_headers():
    key = os.getenv("OPENALEX_API_KEY")
    return {"Authorization": f"Bearer {key}"} if key else {}


def openalex_search(client, query, *, since=None, until=None, page=1, per_page=50):
    params = {"search": query, "per_page": per_page, "page": page}
    filters = []
    if since:
        filters.append("from_publication_date:" + since)
    if until:
        filters.append("to_publication_date:" + until)
    if filters:
        params["filter"] = ",".join(filters)
    if since:
        params["sort"] = "publication_date:desc"
    data = client.json(OA + "/works", params=params, headers=oa_headers())
    return [oa_record(w, f"openalex:search:{query}:page={page}") for w in data["results"]], data["meta"][
        "count"
    ]


def resolve_seed(client, seed):
    identifier = seed.get("openalex") or seed.get("doi")
    if not identifier:
        m = re.search(r"\d{4}\.\d{4,5}", seed.get("url", ""))
        if m:
            identifier = "https://doi.org/10.48550/arXiv." + m[0]
    if not identifier:
        return None
    return client.json(OA + "/works/" + quote(identifier, safe=":/"), headers=oa_headers())


def citations(client, seed, state, per_page=50):
    work = resolve_seed(client, seed)
    if not work:
        return [], {"status": "no-indexed-identifier"}
    wid = work["id"].rsplit("/", 1)[-1]
    rows = []
    # Both directions, paged across runs, preserving incomplete traversals.
    refs = work.get("referenced_works", [])
    if not refs:
        # New preprints often have no indexed reference list. Inspect their HTML bibliography.
        match = re.search(r"(\d{4}\.\d{4,5})", seed.get("url", ""))
        if match:
            from bs4 import BeautifulSoup

            try:
                html = client.get("https://arxiv.org/html/" + match[1]).text
            except Exception:
                html = ""  # Forward citation search still runs when HTML is unavailable.
            soup = BeautifulSoup(html, "html.parser")
            for entry in soup.select(".ltx_bibitem"):
                for a in entry.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("https://") and any(
                        h in href for h in ["arxiv.org/abs/", "doi.org/", "aclanthology.org/"]
                    ):
                        rows.append(
                            {"url": canonical_url(href), "provenance": ["fulltext-reference:" + seed["url"]]}
                        )
    offset = state.get("reference_offset", 0)
    chunk = refs[offset : offset + per_page]
    if chunk:
        data = client.json(
            OA + "/works",
            params={
                "filter": "openalex:" + "|".join(x.rsplit("/", 1)[-1] for x in chunk),
                "per_page": per_page,
            },
            headers=oa_headers(),
        )
        rows.extend(oa_record(w, "openalex:reference-of:" + wid) for w in data["results"])
    next_offset = offset + len(chunk)
    page = state.get("citing_page", 1)
    data = client.json(
        OA + "/works",
        params={"filter": "cites:" + wid, "per_page": per_page, "page": page},
        headers=oa_headers(),
    )
    rows.extend(oa_record(w, "openalex:cites:" + wid) for w in data["results"])
    return rows, {
        "reference_offset": next_offset if next_offset < len(refs) else 0,
        "citing_page": page + 1 if page * per_page < data["meta"]["count"] else 1,
        "references_total": len(refs),
        "citing_total": data["meta"]["count"],
        "status": "ok",
    }


def web_search(client, query):
    if os.getenv("BRAVE_API_KEY"):
        data = client.json(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": 20},
            headers={"X-Subscription-Token": os.environ["BRAVE_API_KEY"]},
        )
        items = [{"title": x["title"], "url": x["url"]} for x in data.get("web", {}).get("results", [])]
        provider = "brave"
    elif os.getenv("SERPER_API_KEY"):
        response = client.request(
            "POST",
            "https://google.serper.dev/search",
            headers={"X-API-KEY": os.environ["SERPER_API_KEY"]},
            json={"q": query, "num": 20},
        )
        items = [{"title": x["title"], "url": x["link"]} for x in response.json().get("organic", [])]
        provider = "google-serper"
    else:
        raise RuntimeError("Web search unconfigured: set BRAVE_API_KEY or SERPER_API_KEY")
    return [dict(x, provenance=[f"{provider}:search:{query}"]) for x in items]


def feed(client, source, limit):
    response = client.get(source["url"])
    parsed = feedparser.parse(response.content)
    if not parsed.entries:
        raise ValueError("Feed empty or invalid")
    # Deliberately do not reject on keywords or title. All bounded feed entries reach evidence retrieval.
    return [
        {"url": e.link, "title": e.get("title", ""), "provenance": ["feed:" + source["url"]]}
        for e in parsed.entries[:limit]
        if e.get("link", "").startswith("https://")
    ]


def repository_links(client, url):
    text = client.get(url).text
    urls = re.findall(r"https://(?:arxiv\.org/(?:abs|pdf)/[^\s)>]+|aclanthology\.org/[^\s)>]+)", text)
    return [{"url": canonical_url(u), "provenance": ["repository:" + url]} for u in sorted(set(urls))]


def index_links(client, source, limit):
    from urllib.parse import urljoin, urlsplit

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(client.get(source["url"]).text, "html.parser")
    found = {}
    for a in soup.find_all("a", href=True):
        url = urljoin(source["url"], a["href"])
        if urlsplit(url).hostname != urlsplit(source["url"]).hostname:
            continue
        if re.search(source["path_pattern"], urlsplit(url).path):
            url = canonical_url(url)
            found[url] = {
                "url": url,
                "title": a.get_text(" ", strip=True),
                "provenance": ["research-index:" + source["url"]],
            }
    if not found:
        raise ValueError("Research index yielded no article links")
    return list(found.values())[:limit]


def collect(client, config, state, catalogue, cutoff, historical=False):
    rows, events = [], []
    limits = config["limits"]

    def run(channel, label, fn):
        try:
            data = fn()
            rows.extend(data)
            events.append({"channel": channel, "query": label, "status": "ok", "candidates": len(data)})
            return True
        except Exception as e:
            events.append({"channel": channel, "query": label, "status": "error", "error": str(e)[:220]})
            return False

    day = date.fromisoformat(cutoff).toordinal()
    queries = config["openalex_queries"]
    for n in range(min(limits["openalex_queries"], len(queries))):
        i = (state.get("query_offset", 0) + n) % len(queries)
        query = queries[i]
        # Every third query is a full-history backfill. Others overlap recent publications.
        backfill = historical or n % 3 == 0
        key = "historical:" + query if backfill else "recent:" + query
        page = state.setdefault("pages", {}).get(key, 1) if backfill else 1
        since = (
            None
            if backfill
            else (date.fromisoformat(cutoff) - timedelta(days=config["lookback_days"])).isoformat()
        )
        for _ in range(limits["pages_per_query"]):
            try:
                found, count = openalex_search(
                    client, query, since=since, until=cutoff, page=page, per_page=limits["results_per_page"]
                )
                rows.extend(found)
                events.append(
                    {
                        "channel": "openalex",
                        "query": query,
                        "since": since,
                        "page": page,
                        "total": count,
                        "candidates": len(found),
                        "status": "ok",
                    }
                )
                if page * limits["results_per_page"] >= count:
                    page = 1
                    break
                page += 1
            except Exception as e:
                events.append(
                    {
                        "channel": "openalex",
                        "query": query,
                        "page": page,
                        "status": "error",
                        "error": str(e)[:220],
                    }
                )
                break
        if backfill:
            state["pages"][key] = page
    state["query_offset"] = (state.get("query_offset", 0) + limits["openalex_queries"]) % len(queries)
    web_queries = config["web_queries"]
    for n in range(limits["web_queries"]):
        q = web_queries[(day * limits["web_queries"] + n) % len(web_queries)]
        run("web", q, lambda q=q: web_search(client, q))
    for source in config["feeds"]:
        run("feed", source["name"], lambda s=source: feed(client, s, limits["feed_entries"]))
    for source in config.get("indexes", []):
        run("index", source["name"], lambda s=source: index_links(client, s, limits["feed_entries"]))
    # Weekly repository refresh; initial backfills always include the seed lists.
    if historical or day % 7 == 0:
        for url in config["repositories"]:
            run("repository", url, lambda u=url: repository_links(client, u))
    seeds = [
        r
        for r in catalogue
        if r.get("scope") in {"core", "mechanism"}
        and (r.get("doi") or r.get("openalex") or "arxiv.org" in r["url"])
    ]
    for n in range(min(limits["citation_seeds"], len(seeds))):
        seed = seeds[(state.get("citation_offset", 0) + n) % len(seeds)]
        try:
            found, progress = citations(
                client,
                seed,
                state.setdefault("citations", {}).get(seed["id"], {}),
                limits["results_per_page"],
            )
            rows.extend(found)
            state["citations"][seed["id"]] = progress
            events.append({"channel": "citations", "seed": seed["id"], "candidates": len(found), **progress})
        except Exception as e:
            events.append(
                {"channel": "citations", "seed": seed["id"], "status": "error", "error": str(e)[:220]}
            )
    if seeds:
        state["citation_offset"] = (state.get("citation_offset", 0) + limits["citation_seeds"]) % len(seeds)
    return rows, events

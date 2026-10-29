"""Compile research plans into operational queries and verified source adapters."""

import re
from urllib.parse import parse_qs, urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup

from .runtime.discovery import feed, index_links
from .runtime.net import Client


def query_text(value):
    query = value.strip()
    if query.startswith("search="):
        return parse_qs(query).get("search", [query])[0]
    if query.startswith("https://api.openalex.org/"):
        return parse_qs(urlsplit(query).query).get("search", [""])[0]
    return query


def path_regex(value):
    """URL-template compilation is syntax handling, never relevance classification."""
    alternatives = []
    for item in value.split(";"):
        item = item.strip()
        if not item.startswith(("/", "^/")):
            continue
        if re.search(r"\{[a-zA-Z_]+\}", item):
            item = item.split("?", 1)[0]
            chunks = re.split(r"(\{[a-zA-Z_]+\})", item)
            pattern = ""
            for chunk in chunks:
                if chunk.startswith("{"):
                    name = chunk.strip("{}")
                    pattern += (
                        r"[0-9]{4}"
                        if name == "year"
                        else (
                            r"[0-9]+" if name in {"volume", "version", "paper_number", "pmid"} else r"[^/?#]+"
                        )
                    )
                else:
                    pattern += re.escape(chunk)
            alternatives.append(pattern)
        else:
            re.compile(item)
            alternatives.append(item)
    if not alternatives:
        raise ValueError("No executable URL path pattern")
    return "(?:" + "|".join(alternatives) + ")"


def compile_sources(plan, brief, cutoff, client=None):
    client = client or Client(max_requests=80, seconds=180)
    compiled = dict(plan)
    compiled["openalex_queries"] = list(
        dict.fromkeys(query_text(q) for q in plan["openalex_queries"] if query_text(q))
    )
    compiled["indexes"], compiled["feeds"] = [], []
    audit = {"sources": [], "query_normalizations": [], "temporal_normalizations": []}
    for raw, clean in zip(
        plan["openalex_queries"], [query_text(q) for q in plan["openalex_queries"]], strict=True
    ):
        if raw != clean:
            audit["query_normalizations"].append({"from": raw, "to": clean})
    # Snapshot cutoffs belong in the Python date filter, not a permanent daily exclusion.
    for field in ["include", "exclude", "boundaries"]:
        compiled[field] = []
        for rule in plan[field]:
            if cutoff in rule and cutoff not in brief:
                audit["temporal_normalizations"].append(rule)
            else:
                compiled[field].append(rule)
    seen_feeds, seen_indexes = set(), set()
    for source in plan["feeds"]:
        try:
            entries = feed(client, source, 2)
            compiled["feeds"].append(source)
            seen_feeds.add(source["url"])
            audit["sources"].append(
                {"url": source["url"], "kind": "feed", "status": "verified", "sample_count": len(entries)}
            )
        except Exception as error:
            audit["sources"].append(
                {"url": source["url"], "kind": "feed", "status": "disabled", "error": str(error)[:160]}
            )
    for source in plan["indexes"]:
        try:
            pattern = path_regex(source["path_pattern"])
        except (ValueError, re.error) as error:
            audit["sources"].append(
                {"url": source["url"], "kind": "index", "status": "disabled", "error": str(error)}
            )
            continue
        parsed = urlsplit(source["url"])
        trial_urls = [source["url"]]
        if parsed.path.strip("/"):
            parent = parsed.path.rstrip("/").rsplit("/", 1)[0] or "/"
            trial_urls += [
                urlunsplit((parsed.scheme, parsed.netloc, parent, "", "")),
                urlunsplit((parsed.scheme, parsed.netloc, "/", "", "")),
            ]
        errors = []
        for url in dict.fromkeys(trial_urls):
            candidate = dict(source, url=url, path_pattern=pattern)
            try:
                rows = index_links(client, candidate, 3)
                if (url, pattern) not in seen_indexes:
                    compiled["indexes"].append(candidate)
                    seen_indexes.add((url, pattern))
                audit["sources"].append(
                    {
                        "url": url,
                        "kind": "index",
                        "status": "verified",
                        "sample_urls": [r["url"] for r in rows],
                    }
                )
                break
            except Exception as error:
                errors.append(str(error)[:120])
        else:
            audit["sources"].append(
                {"url": source["url"], "kind": "index", "status": "disabled", "errors": errors}
            )
        # Discover advertised RSS/Atom links from a real page instead of inventing feed URLs.
        try:
            html = client.get(source["url"]).text
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("link", href=True):
                if link.get("type") not in {"application/rss+xml", "application/atom+xml"}:
                    continue
                url = urljoin(source["url"], link["href"])
                if url in seen_feeds:
                    continue
                discovered = {"name": source["name"], "url": url}
                entries = feed(client, discovered, 2)
                compiled["feeds"].append(discovered)
                seen_feeds.add(url)
                audit["sources"].append(
                    {
                        "url": url,
                        "kind": "advertised-feed",
                        "status": "verified",
                        "sample_count": len(entries),
                    }
                )
        except Exception:
            pass
    audit["requests"] = client.count
    return compiled, audit

"""Retrieve actual abstracts or article text; search snippets are never evidence."""

import hashlib
import io
import re
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pypdf import PdfReader

from .store import canonical_url, doi_from_url, today


def text_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def html_evidence(html, url):
    soup = BeautifulSoup(html, "html.parser")

    def meta(name):
        node = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
        return node.get("content", "") if node else ""

    title_node = soup.find("h1") or soup.find("title")
    if title_node:
        for note in title_node.select(".ltx_thanks, .ltx_note, .ltx_tag"):
            note.decompose()
    title = meta("citation_title") or (title_node.get_text(" ", strip=True) if title_node else "")
    title = re.sub(r"^Title:\s*", "", re.sub(r"\s+", " ", title)).strip()
    abstract = soup.select_one(
        "blockquote.abstract, .abstract-content, #abstract .abstract, section.abstract, #abstract, .article-section__abstract"
    )
    authors = [n.get("content") for n in soup.find_all("meta", attrs={"name": "citation_author"})]
    pdf = meta("citation_pdf_url")
    if not pdf:
        for a in soup.find_all("a", href=True):
            if a.get_text(" ", strip=True).casefold() in {
                "pdf",
                "download pdf",
                "view pdf",
                "download the pdf",
            } and (a["href"].split("?")[0].endswith(".pdf") or re.match(r"/pdf/\d{4}", a["href"])):
                pdf = urljoin(url, a["href"])
                break
    date = meta("citation_date") or meta("citation_publication_date") or meta("article:published_time")
    if abstract:
        text = re.sub(r"^Abstract:\s*", "", abstract.get_text(" ", strip=True))
        kind = "abstract"
    else:
        for node in soup.select("script, style, nav, footer, header, noscript, form"):
            node.decompose()
        root = soup.find("article") or soup.find("main") or soup.body or soup
        text = root.get_text(" ", strip=True)
        kind = "full-text"
    return {
        "title": title,
        "authors": authors,
        "date": date[:10].replace("/", "-"),
        "pdf_url": pdf,
        "doi": meta("citation_doi"),
        "text": text,
        "kind": kind,
    }


def retrieve(client, record, cache_dir=Path(".cache/evidence"), prefer_full_text=False):
    """Prefer body text for method facets; retain an honest abstract fallback."""
    from .net import BudgetExceeded

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = record.get("retrieval", {})
    if cached.get("sha256") and re.fullmatch(r"[a-f0-9]{64}", cached["sha256"]):
        cached_path = cache_dir / (cached["sha256"] + ".txt")
        if cached_path.is_file():
            text = cached_path.read_text()
            if text_hash(text) == cached["sha256"] and (
                not prefer_full_text or cached.get("kind") == "full-text"
            ):
                return text, cached

    def save(info, source_url):
        text = re.sub(r"\s+", " ", info["text"]).strip()
        if len(text.split()) < 40 or any(
            x in text[:300].lower() for x in ["just a moment", "access denied", "captcha"]
        ):
            raise ValueError("No usable abstract or full text")
        for key in ["title", "authors", "date", "pdf_url", "doi"]:
            if info.get(key) and (not record.get(key) or key == "title"):
                record[key] = info[key]
        digest = text_hash(text)
        path = cache_dir / (digest + ".txt")
        path.write_text(text)
        evidence = {
            "kind": info["kind"],
            "url": source_url,
            "sha256": digest,
            "retrieved": today(),
            "characters": len(text),
            "local_path": str(path),
        }
        record["retrieval"] = evidence
        return text, evidence

    abstract = record.get("abstract", "")
    if not prefer_full_text and len(abstract.split()) >= 40:
        return save({"text": abstract, "kind": "abstract"}, record.get("openalex") or record["url"])
    urls = []
    source = record.get("evidence_url") or record["url"]
    match = re.search(r"arxiv.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", source)
    if prefer_full_text and match:
        urls.append("https://arxiv.org/html/" + match[1])
    if "openreview.net/forum?" in source:
        urls.append(source.replace("/forum?", "/pdf?"))
    urls.append(canonical_url(source) if "arxiv.org" in source else source)
    if record.get("pdf_url"):
        urls.append(record["pdf_url"])
    errors = []
    for url in dict.fromkeys(urls):
        try:
            response = client.get(url, max_bytes=25_000_000)
            if response.content.startswith(b"%PDF-"):
                reader = PdfReader(io.BytesIO(response.content))
                info = {
                    "text": "\n".join((p.extract_text() or "") for p in reader.pages[:40]),
                    "kind": "full-text",
                    "pdf_url": url,
                }
            else:
                info = html_evidence(response.text, url)
                if prefer_full_text and "/html/" in url:
                    soup = BeautifulSoup(response.text, "html.parser")
                    for node in soup.select("script, style, nav, footer, .ltx_bibliography"):
                        node.decompose()
                    article = soup.find("article") or soup.find("main")
                    if article:
                        info["text"] = article.get_text(" ", strip=True)
                        info["kind"] = "full-text"
            if prefer_full_text and info["kind"] == "abstract" and info.get("pdf_url"):
                try:
                    pdf_response = client.get(info["pdf_url"], max_bytes=25_000_000)
                    if pdf_response.content.startswith(b"%PDF-"):
                        reader = PdfReader(io.BytesIO(pdf_response.content))
                        body = "\n".join((page.extract_text() or "") for page in reader.pages[:40])
                        if len(body.split()) >= 40:
                            return save(dict(info, text=body, kind="full-text"), info["pdf_url"])
                except BudgetExceeded:
                    raise
                except Exception:
                    pass  # Preserve a usable abstract when the full PDF is unavailable.
            return save(info, url)
        except BudgetExceeded:
            raise
        except Exception as error:
            errors.append(str(error)[:100])
    # Publisher access restrictions do not turn a seed title into relevance evidence.
    # Try the indexed primary abstract for an explicit DOI, preserving that source URL.
    doi = record.get("doi") or doi_from_url(source)
    if doi:
        from .discovery import OA, oa_headers, oa_record

        identifier = doi if doi.startswith("https://doi.org/") else "https://doi.org/" + doi
        try:
            work = client.json(OA + "/works/" + identifier, headers=oa_headers())
            indexed = oa_record(work, "openalex:doi-evidence-fallback")
            if len(indexed.get("abstract", "").split()) >= 40:
                for key, value in indexed.items():
                    if value and key != "url" and not record.get(key):
                        record[key] = value
                return save(
                    {"text": indexed["abstract"], "kind": "abstract", "title": indexed["title"]},
                    indexed["openalex"],
                )
        except BudgetExceeded:
            raise
        except Exception as error:
            errors.append(str(error)[:100])
    if len(abstract.split()) >= 40:
        return save({"text": abstract, "kind": "abstract"}, record.get("openalex") or record["url"])
    raise ValueError("No usable abstract or full text: " + "; ".join(errors))

"""Retrieve actual abstracts or article text; search snippets are never evidence."""

import hashlib
import io
import re
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pypdf import PdfReader

from .store import canonical_url, today


def text_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def html_evidence(html, url):
    soup = BeautifulSoup(html, "html.parser")

    def meta(name):
        node = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
        return node.get("content", "") if node else ""

    title_node = soup.find("h1") or soup.find("title")
    title = meta("citation_title") or (title_node.get_text(" ", strip=True) if title_node else "")
    title = re.sub(r"^Title:\s*", "", title)
    abstract = soup.select_one(
        "blockquote.abstract, .abstract-content, #abstract .abstract, section.abstract"
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
        "text": text,
        "kind": kind,
    }


def retrieve(client, record, cache_dir=Path(".cache/evidence")):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    if record.get("abstract") and len(record["abstract"].split()) >= 40:
        info = {"text": record["abstract"], "kind": "abstract"}
        source_url = record.get("openalex") or record["url"]
    else:
        source_url = record.get("evidence_url") or record["url"]
        url = canonical_url(source_url) if "arxiv.org" in source_url else source_url
        response = client.get(url, max_bytes=12_000_000)
        if response.content.startswith(b"%PDF-"):
            reader = PdfReader(io.BytesIO(response.content))
            text = "\n".join((p.extract_text() or "") for p in reader.pages[:30])
            info = {"text": text, "kind": "full-text"}
        else:
            info = html_evidence(response.text, url)
        for k in ["title", "authors", "date", "pdf_url"]:
            if info.get(k) and (not record.get(k) or k == "title"):
                record[k] = info[k]
    text = re.sub(r"\s+", " ", info["text"]).strip()
    if len(text.split()) < 40 or any(
        x in text[:300].lower() for x in ["just a moment", "access denied", "captcha"]
    ):
        raise ValueError("No usable abstract or full text")
    digest = text_hash(text)
    path = cache_dir / f"{digest}.txt"
    path.write_text(text)
    evidence = {
        "kind": info["kind"],
        "url": source_url,
        "sha256": digest,
        "retrieved": today(),
        "characters": len(text),
        "local_path": str(path),
    }
    return text, evidence

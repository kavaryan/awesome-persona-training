"""Verified open-access PDFs and a stable NotebookLM import manifest."""

import hashlib
import io
import re
from pathlib import Path

from pypdf import PdfReader

from .store import today, write_json


def pdf_sources(record):
    urls = []
    for u in [record.get("pdf_url", ""), record.get("url", ""), *record.get("aliases", [])]:
        match = re.search(r"(?:arxiv.org/(?:abs|pdf)/|10\.48550/arxiv\.)(\d{4}\.\d{4,5})", u, re.IGNORECASE)
        if match:
            urls.append("https://arxiv.org/pdf/" + match[1])
        elif u and (u == record.get("pdf_url") or u.split("?")[0].endswith(".pdf")):
            urls.append(u)
    return list(dict.fromkeys(urls))


def validate_pdf(content):
    if not content.startswith(b"%PDF-"):
        raise ValueError("Response is not a PDF")
    reader = PdfReader(io.BytesIO(content))
    if reader.is_encrypted or len(reader.pages) == 0:
        raise ValueError("PDF is encrypted or empty")
    return len(reader.pages)


def download(client, record, directory, max_mb=40):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    dest = directory / (record["id"] + ".pdf")
    previous = record.get("download", {})
    if dest.exists() and previous.get("sha256") == hashlib.sha256(dest.read_bytes()).hexdigest():
        return previous
    errors = []
    for url in pdf_sources(record):
        try:
            response = client.get(url, max_bytes=max_mb * 1_000_000)
            pages = validate_pdf(response.content)
            digest = hashlib.sha256(response.content).hexdigest()
            temp = dest.with_suffix(".pdf.part")
            temp.write_bytes(response.content)
            temp.replace(dest)
            return {
                "status": "downloaded",
                "path": str(dest),
                "sha256": digest,
                "bytes": len(response.content),
                "pages": pages,
                "source_url": url,
                "downloaded": today(),
                "license": record.get("license", "unspecified; original source terms apply"),
            }
        except Exception as e:
            errors.append(str(e)[:160])
    return {"status": "unavailable", "checked": today(), "errors": errors or ["No open-access PDF URL known"]}


def make_manifest(catalogue, path):
    entries = []
    for r in catalogue:
        if r["scope"] not in {"core", "mechanism", "background"}:
            continue
        d = r.get("download", {})
        entries.append(
            {
                "id": r["id"],
                "title": r["title"],
                "url": r["url"],
                "scope": r["scope"],
                "date": r.get("date", ""),
                "status": d.get("status", "pending"),
                "path": d.get("path"),
                "sha256": d.get("sha256"),
                "source_url": d.get("source_url"),
                "license": d.get("license", r.get("license", "unspecified")),
            }
        )
    write_json(path, {"version": 1, "sources": sorted(entries, key=lambda x: x["id"])})
    return entries

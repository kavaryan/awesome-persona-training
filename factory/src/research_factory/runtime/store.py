"""Stable identities and atomic, diff-friendly state."""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def today():
    return datetime.now(UTC).date().isoformat()


def read_json(path, default=None):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else default


def write_json(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_suffix(p.suffix + ".tmp")
    temp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    temp.replace(p)


def canonical_url(url):
    p = urlsplit(url.strip())
    host = (p.hostname or "").lower()
    if host in {"export.arxiv.org", "www.arxiv.org", "arxiv.org"}:
        m = re.search(r"(\d{4}\.\d{4,5})(?:v\d+)?", p.path)
        if m:
            return "https://arxiv.org/abs/" + m[1]
    if host in {"doi.org", "dx.doi.org"}:
        return "https://doi.org/" + p.path.lstrip("/").lower()
    # LW and AF crossposts share a post ID.
    if host in {"lesswrong.com", "www.lesswrong.com", "alignmentforum.org", "www.alignmentforum.org"}:
        m = re.search(r"/posts/([^/]+)", p.path)
        if m:
            return "https://www.lesswrong.com/posts/" + m[1]
    query = [(k, v) for k, v in parse_qsl(p.query) if not k.startswith("utm_") and k not in {"ref", "trk"}]
    return urlunsplit(("https", host, p.path.rstrip("/"), urlencode(query), ""))


def identities(record):
    keys = set()
    for url in [record.get("url", ""), *record.get("aliases", [])]:
        if url:
            keys.add(canonical_url(url))
    for k in ["doi", "arxiv", "openalex"]:
        v = record.get(k)
        if v:
            if k == "doi":
                keys.add("https://doi.org/" + v.lower().removeprefix("https://doi.org/"))
            elif k == "arxiv":
                keys.add("https://arxiv.org/abs/" + re.sub(r"v\d+$", "", v))
            else:
                keys.add(v)
    # DOI/arXiv cross-representations.
    for key in list(keys):
        m = re.search(r"10\.48550/arxiv\.(\d{4}\.\d{4,5})", key, re.IGNORECASE)
        if m:
            keys.add("https://arxiv.org/abs/" + m[1])
    return keys


def record_id(url):
    return hashlib.sha256(canonical_url(url).encode()).hexdigest()[:16]


def merge_candidates(existing, incoming, catalogue=()):
    records = {r["id"]: r for r in existing}
    index = {key: r["id"] for r in records.values() for key in identities(r)}
    accepted = {key for r in catalogue for key in identities(r)}
    for row in incoming:
        keys = identities(row)
        if keys & accepted:
            continue
        matches = sorted({index[k] for k in keys if k in index})
        rid = matches[0] if matches else row.get("id") or record_id(row["url"])
        # A later metadata record can bridge two previously separate versions.
        # Keep audit decisions, but re-review conflicts rather than silently choosing one.
        for duplicate in matches[1:]:
            extra = records.pop(duplicate)
            target = records[rid]
            target["provenance"] = sorted(
                set(target.get("provenance", [])) | set(extra.get("provenance", []))
            )
            target["aliases"] = sorted(identities(target) | identities(extra))
            if extra.get("decision") and extra.get("decision") != target.get("decision"):
                target.setdefault("prior_decisions", []).append(extra["decision"])
                target["status"] = "uncertain"
            for key in identities(extra):
                index[key] = rid
        old = records.get(rid)
        if old:
            # Preserve decisions and evidence; merge discovery routes and new bibliographic metadata.
            old["provenance"] = sorted(set(old.get("provenance", [])) | set(row.get("provenance", [])))
            old["aliases"] = sorted(set(old.get("aliases", [])) | keys)
            for k, v in row.items():
                if v and not old.get(k):
                    old[k] = v
        else:
            row = dict(row, id=rid, first_seen=today(), status="pending")
            records[rid] = row
        for k in keys:
            index[k] = rid
    return sorted(records.values(), key=lambda r: r["id"])


def doi_from_url(url):
    match = re.search(r"(?:doi.org/|/doi/(?:abs/|full/|pdf/|epdf/)?)(10\.\d{4,9}/[^?#]+)", url)
    if match:
        return match[1]
    parsed = urlsplit(url)
    if parsed.hostname in {"nature.com", "www.nature.com"} and parsed.path.startswith("/articles/"):
        return "10.1038/" + parsed.path.split("/articles/", 1)[1]
    return None

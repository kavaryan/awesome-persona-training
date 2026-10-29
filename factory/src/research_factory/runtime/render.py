"""Validate evidence-bearing records and produce portable research exports."""

import csv
import hashlib
import io
import re
from pathlib import Path

from .judge import ACCEPTED, validate_decision
from .store import identities


def validate_catalogue(rows, project):
    seen = set()
    for row in rows:
        for field in ["id", "url", "title", "summary", "rationale", "evidence", "facets", "audit"]:
            if not row.get(field):
                raise ValueError(f"Record missing {field}")
        if not re.fullmatch(r"[a-z0-9-]+", row["id"]) or row["scope"] not in ACCEPTED:
            raise ValueError("Invalid accepted record")
        evidence = row["evidence"]
        if evidence.get("kind") not in {"abstract", "full-text"} or not re.fullmatch(
            r"[a-f0-9]{64}", evidence.get("sha256", "")
        ):
            raise ValueError("Invalid source evidence")
        if set(row["facets"]) != {d["name"] for d in project["dimensions"]}:
            raise ValueError("Missing or unexpected taxonomy dimension")
        decision = {
            k: row[k] for k in ["scope", "confidence", "summary", "rationale", "evidence_quote", "facets"]
        }
        # Schema check and short-quote constraints even on a fresh checkout without fulltext cache.
        cache = Path(".cache/evidence") / (evidence["sha256"] + ".txt")
        if cache.exists():
            source = cache.read_text()
            if hashlib.sha256(source.encode()).hexdigest() != evidence["sha256"]:
                raise ValueError("Source evidence checksum mismatch")
            validate_decision(decision, source, project)
            validate_decision(row["audit"], source, project, audit=True)
        else:
            validate_decision(decision, row["evidence_quote"], project)
            validate_decision(row["audit"], row["audit"]["evidence_quote"], project, audit=True)
        if row["audit"]["scope"] not in ACCEPTED or min(row["confidence"], row["audit"]["confidence"]) < 0.9:
            raise ValueError("Acceptance requires two independent qualifying decisions")
        keys = identities(row)
        if seen & keys:
            raise ValueError("Duplicate accepted work")
        seen.update(keys)


def render(rows, project):
    Path("docs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    lines = [
        "# Research catalogue",
        "",
        "Generated from evidence-reviewed records. The README is a separately maintained selection.",
        "",
    ]
    for scope, heading in [
        ("core", "Directly relevant research"),
        ("supporting", "Supporting methods and foundations"),
    ]:
        lines += ["## " + heading, ""]
        for r in sorted(
            (r for r in rows if r["scope"] == scope),
            key=lambda r: (r.get("date", ""), r["title"]),
            reverse=True,
        ):
            title = r["title"].replace("[", "\\[").replace("]", "\\]")
            lines += [
                f"- [{title}]({r['url']}) ({r.get('date') or 'date unverified'}) — {r['summary']}",
                f"  Scope: {r['rationale']}",
            ]
            for name, facet in r["facets"].items():
                lines.append(f"  {name}: {', '.join(facet['values'])}. {facet['detail']}")
            lines += [
                f"  Evidence: [{r['evidence']['kind']}]({r['evidence']['url']}); review: {r.get('reviewer', 'unknown')}.",
                "",
            ]
    Path("docs/catalogue.md").write_text("\n".join(lines).rstrip() + "\n")
    fields = ["id", "title", "url", "date", "scope", "summary"] + [d["name"] for d in project["dimensions"]]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fields)
    writer.writeheader()
    bib = []
    for row in sorted(rows, key=lambda r: r["id"]):
        flat = {k: row.get(k, "") for k in fields[:6]}
        flat.update({k: ";".join(v["values"]) + ": " + v["detail"] for k, v in row["facets"].items()})
        writer.writerow(flat)

        def safe(s):
            return str(s).replace("{", "").replace("}", "").replace("\\", "").replace("&", r"\&")

        attributes = {
            "title": row["title"],
            "url": row["url"],
            "year": row.get("date", "")[:4],
            "author": " and ".join(row.get("authors", [])),
        }
        bib.append(
            "@misc{work"
            + row["id"]
            + ",\n"
            + ",\n".join("  " + k + " = {" + safe(v) + "}" for k, v in attributes.items() if v)
            + "\n}"
        )
    Path("data/catalogue.csv").write_text(buf.getvalue())
    Path("data/catalogue.bib").write_text("\n\n".join(bib) + "\n")

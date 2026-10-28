"""Generated research indexes; the curated Awesome README is edited by maintainers."""

import csv
import io
import re
from collections import Counter
from pathlib import Path

from .store import identities


def escaped(text):
    return str(text).replace("|", "\\|").replace("\n", " ").replace("[", "\\[").replace("]", "\\]")


def render(catalogue, root=Path(".")):
    root = Path(root)
    groups = [
        ("core", "Character training and its consequences"),
        ("mechanism", "Persona mechanisms and controls"),
        ("background", "Foundations and measurement"),
        ("roleplay", "Role-playing and personalization boundaries"),
    ]
    counts = Counter(r["scope"] for r in catalogue)
    lines = [
        "# Research catalogue",
        "",
        "Generated from [`data/catalogue.json`](../data/catalogue.json). The [README](../README.md) is a separately curated reading list.",
        "",
        "Scope is assigned from abstracts or full text. Inclusion is not an endorsement of findings; preprints and posts are not peer review.",
        "",
        "Tags describe interventions and themes. See [the taxonomy](taxonomy.md). Dates are source publication dates, not discovery dates.",
        "",
        "| Scope | Records |",
        "| --- | ---: |",
    ]
    for scope, label in groups:
        lines.append(f"| {label} | {counts[scope]} |")
    for scope, label in groups:
        lines += ["", "## " + label, ""]
        for r in sorted(
            (r for r in catalogue if r["scope"] == scope),
            key=lambda r: (r.get("date", ""), r["title"]),
            reverse=True,
        ):
            tags = ", ".join(r["interventions"] + r["themes"])
            lines += [
                f"- [{escaped(r['title'])}]({r['url']}) ({r.get('date') or 'date unspecified'}; {r['evidence_type']}) — {r['summary']}",
                f"  Tags: {tags}. Evidence: [{r['evidence']['kind']}]({r['evidence']['url']}); reviewer: {r.get('reviewer', 'initial-editorial-review')}.",
            ]
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs/catalogue.md").write_text("\n".join(lines) + "\n")
    fields = ["id", "title", "date", "url", "scope", "evidence_type", "interventions", "themes", "summary"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fields)
    writer.writeheader()
    for r in sorted(catalogue, key=lambda r: r["id"]):
        writer.writerow({k: ";".join(r[k]) if isinstance(r.get(k), list) else r.get(k, "") for k in fields})
    (root / "data/catalogue.csv").write_text(buf.getvalue())
    bib = []
    for r in sorted(catalogue, key=lambda r: r["id"]):

        def safe(x):
            return str(x).replace("{", "").replace("}", "").replace("\\", "").replace("&", r"\&")

        fields = {
            "title": r["title"],
            "url": r["url"],
            "year": r.get("date", "")[:4],
            "author": " and ".join(r.get("authors", [])),
            "note": r["evidence_type"],
        }
        bib.append(
            "@misc{persona"
            + r["id"]
            + ",\n"
            + ",\n".join("  " + k + " = {" + safe(v) + "}" for k, v in fields.items() if v)
            + "\n}"
        )
    (root / "data/catalogue.bib").write_text("\n\n".join(bib) + "\n")


def validate_catalogue(rows, taxonomy):
    seen = set()
    for r in rows:
        for field in [
            "id",
            "title",
            "url",
            "scope",
            "summary",
            "rationale",
            "evidence_type",
            "evidence",
            "interventions",
            "themes",
        ]:
            if not r.get(field) and field not in {"interventions", "themes"}:
                raise ValueError(f"{r.get('id')}: missing {field}")
        if not re.fullmatch(r"[a-z0-9-]+", r["id"]):
            raise ValueError("Invalid record ID")
        if r["scope"] not in taxonomy["scope"] or r["evidence_type"] not in taxonomy["evidence_types"]:
            raise ValueError("Invalid taxonomy")
        if not set(r["interventions"]) <= set(taxonomy["interventions"]) or not set(r["themes"]) <= set(
            taxonomy["themes"]
        ):
            raise ValueError("Invalid tags")
        if r["evidence"].get("kind") not in {"abstract", "full-text"} or not r["evidence"].get("sha256"):
            raise ValueError("Source evidence missing")
        keys = identities(r)
        if keys & seen:
            raise ValueError(f"Duplicate work: {r['title']}")
        seen.update(keys)

"""Render reviewed configuration into an independent runnable repository."""

import hashlib
import subprocess
from importlib.resources import files
from pathlib import Path

from .compile import query_text
from .runtime.store import read_json, write_json
from .schema import validate_plan

LIMITS = {
    "requests": 240,
    "seconds": 900,
    "discovery_requests": 90,
    "discovery_seconds": 300,
    "openalex_queries": 12,
    "web_queries": 8,
    "citation_seeds": 4,
    "pages_per_query": 2,
    "results_per_page": 50,
    "feed_entries": 20,
    "judge_items": 24,
    "downloads": 12,
    "download_mb": 40,
}


def scaffold(output, brief, plan, cutoff):
    output = Path(output).resolve()
    validate_plan(plan)
    output.mkdir(parents=True, exist_ok=True)
    project = {
        k: plan[k]
        for k in [
            "title",
            "slug",
            "description",
            "include",
            "exclude",
            "boundaries",
            "keywords",
            "dimensions",
            "coverage_limits",
        ]
    }
    project.update(version=1, initialized=cutoff, brief_sha256=hashlib.sha256(brief.encode()).hexdigest())
    discovery = {k: plan[k] for k in ["openalex_queries", "web_queries", "feeds", "indexes", "repositories"]}
    discovery.update(
        version=1, lookback_days=21, limits=LIMITS.copy(), openalex_fields=["all", "title_and_abstract"]
    )
    previous_project = read_json(output / "config/project.json")
    if previous_project:

        def stable(p):
            return {k: p[k] for k in ["include", "exclude", "boundaries", "dimensions", "brief_sha256"]}

        if stable(previous_project) != stable(project):
            raise ValueError(
                "Project scope or taxonomy changed; use a new output directory instead of reinterpreting existing decisions"
            )
        project["initialized"] = previous_project["initialized"]
    write_json(output / "config/project.json", project)
    previous_discovery = read_json(output / "config/discovery.json")
    if previous_discovery:
        for key in ["openalex_queries", "web_queries"]:
            queries = previous_discovery[key] + discovery[key]
            if key == "openalex_queries":
                queries = [query_text(q) for q in queries if query_text(q)]
            discovery[key] = list(dict.fromkeys(queries))
        discovery["limits"].update(previous_discovery.get("limits", {}))
    write_json(output / "config/discovery.json", discovery)
    write_json(output / "reports/bootstrap-plan.json", plan)
    (output / "PROJECT.md").write_text(brief)
    (output / "research_map").mkdir(exist_ok=True)
    for source in files("research_factory.runtime").iterdir():
        if source.name.endswith(".py"):
            (output / "research_map" / source.name).write_text(source.read_text())
    templates = files("research_factory").joinpath("templates")
    (output / ".github/workflows").mkdir(parents=True, exist_ok=True)
    for name in ["discover.yml", "validate.yml"]:
        (output / ".github/workflows" / name).write_text(templates.joinpath(name).read_text())
    for name in ["requirements.txt", "license", "LICENSE-CODE", "package.json", "package-lock.json"]:
        (output / name).write_text(templates.joinpath(name).read_text())
    (output / ".gitignore").write_text(
        ".venv/\nnode_modules/\n__pycache__/\n.cache/\n.bootstrap/\ndownloads/\n.env\n.env.*\n!.env.example\n*.token\n*.key\n"
    )
    (output / ".env.example").write_text(
        "OPENALEX_API_KEY=\nBRAVE_API_KEY=\nSERPER_API_KEY=\nLLM_API_KEY=\nLLM_BASE_URL=\nLLM_MODEL=\n"
    )
    (output / "docs").mkdir(exist_ok=True)
    (output / "contributing.md").write_text(
        "# Contributing\n\nRead PROJECT.md and config/project.json. Propose primary sources with abstracts or full text and an explicit scope rationale. Titles and search snippets do not establish relevance. Preserve uncertain cases and source provenance.\n"
    )
    (output / "docs/automation.md").write_text(
        "# Daily workflow\n\nRuns at 06:17 UTC. Discovery uses concrete OpenAlex/web queries, feeds, indexes, repositories and citations in both directions. "
        "The initial agent compiles configuration; no code agent runs daily. The brief is retained in PROJECT.md.\n\n"
        "Daily limits: 90 discovery requests/300 seconds, then 150 requests/600 seconds for evidence, at most 24 candidates and 48 small-model calls, and 12 PDF attempts. "
        "Sources can fail or truncate; coverage is not exhaustive. Half the review slots favor new arrivals; half advance the historical queue. Unfinished work remains queued.\n\n"
        "Each proposed inclusion needs two independent abstract/body judgments. Validate tags and a literal supporting quote; disagreement or confidence below 0.9 remains uncertain. "
        "Confidence is not calibrated. No title-only fallback. A narrow core and a separately labeled supporting section prevent generic neighboring work being presented as direct evidence.\n\n"
        "Set Actions secrets OPENALEX_API_KEY, BRAVE_API_KEY or SERPER_API_KEY, and LLM_API_KEY; set variables LLM_BASE_URL and LLM_MODEL for a compatible /chat/completions provider. "
        "Without judge credentials, discovery persists candidates and reports degraded service. No model is selected automatically.\n\n"
        "Install with `python -m pip install --require-hashes -r requirements.txt`. Run `python -m research_map.cli run`, `validate`, or `render`. "
        "The daily run commits metadata to main. PDFs and full text are cached, never committed; a checksum-bearing NotebookLM manifest is generated. Uploads are disabled.\n\n"
        "README is a bootstrap reading selection, maintained separately from generated docs/catalogue.md. This AI-assisted list follows Awesome formatting conventions; "
        "it does not claim upstream eligibility or create an upstream pull request. Human curation and upstream requirements still apply.\n"
    )
    (output / "docs/taxonomy.md").write_text(
        "# Project taxonomy\n\n"
        + "\n\n".join(
            f"## {d['name']}\n\n{d['description']}\n\nValues: {', '.join(d['values'])}. Use not-reported for missing evidence."
            for d in plan["dimensions"]
        )
        + "\n"
    )
    for name, initial in [("catalogue", []), ("candidates", []), ("discovery-state", {})]:
        path = output / f"data/{name}.json"
        if not path.exists():
            write_json(path, initial)
    if not (output / ".git").exists():
        subprocess.run(["git", "init", "-b", "main", str(output)], check=True, capture_output=True)
    return project, discovery


def reading_list(output):
    output = Path(output)
    project = read_json(output / "config/project.json")
    catalogue = read_json(output / "data/catalogue.json", [])
    title = project["title"]
    if not title.startswith("Awesome "):
        title = "Awesome " + title
    text = [
        f"# {title} [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        "> " + project["description"],
        "",
        "An evidence-reviewed research map. See [scope](PROJECT.md), [taxonomy](docs/taxonomy.md), and the complete [catalogue](docs/catalogue.md).",
        "",
        "## Contents",
        "",
        "- [Core Research](#core-research)",
        "- [Supporting Research](#supporting-research)",
        "- [Maintenance](#maintenance)",
        "",
    ]
    for scope, heading in [("core", "Core Research"), ("supporting", "Supporting Research")]:
        text += ["## " + heading, ""]
        selected = sorted(
            (r for r in catalogue if r["scope"] == scope),
            key=lambda r: (r.get("date", ""), r["title"]),
            reverse=True,
        )
        for r in selected[:35]:
            summary = r["summary"].rstrip(". ") + "."
            text.append(f"- [{r['title']}]({r['url']}) - {summary}")
        if not selected:
            text.append("No accepted records yet; inspect the pending queue and bootstrap report.")
        text.append("")
    text += [
        "## Maintenance",
        "",
        "The [daily workflow](.github/workflows/discover.yml) updates the generated catalogue and PDF manifest. See [setup](docs/automation.md) and [contribution guidance](contributing.md).",
        "",
        "AI-assisted bootstrap; supporting evidence and review decisions remain auditable. Coverage is not exhaustive. No upstream Awesome submission has been made.",
        "",
    ]
    (output / "README.md").write_text("\n".join(text))

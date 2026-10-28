"""Exercise the production CLI offline in a disposable research workspace.

Only DNS and HTTP transport are mocked. Discovery, evidence extraction, the judge
request/schema checks, downloads, persistence, and exports use production code.
The model answers are fixtures: this checks integration, not model judgment quality.
"""

import argparse
import hashlib
import io
import json
import os
import socket
import sys
from contextlib import chdir
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import requests
from pypdf import PdfWriter

from persona_map.cli import main
from persona_map.store import read_json, write_json

ROOT = Path(__file__).resolve().parents[1]
CORE_URL = "https://arxiv.org/abs/2601.00001"
POST_URL = "https://research.example/post"
ROLE_URL = "https://research.example/roleplay"
EXCLUDE_URL = "https://research.example/exclude"
TEXTS = {
    "core": (
        "We train persistent assistant traits using written constitutions and supervised fine tuning. "
        "We evaluate honesty and robustness across multiple safety tasks, comparing trained models "
        "against prompted baselines. Changes to the intended character trait can affect other "
        "behaviors, and our results depend on the model and evaluation conditions."
    ),
    "roleplay": (
        "We train fictional characters to reproduce dialogue styles in entertainment scenarios. "
        "Our evaluation measures resemblance to a fictional speaker and consistency with a "
        "character biography. The study concerns role playing and does not measure persistent "
        "assistant values, safety generalization, deception, or consequences of training assistant character."
    ),
    "exclude": (
        "We study exercise routines for human actors preparing for theater performances. "
        "Participants rehearse fictional roles over several weeks, and the study measures "
        "their confidence on stage using interviews and surveys. The research does not "
        "involve language models, machine learning systems, artificial intelligence, or assistant training."
    ),
    "mechanism": (
        "We identify activation directions associated with assistant honesty and sycophancy. "
        "Interventions on these directions change behavior under adversarial prompts, although "
        "effects vary by model and task. The article studies a mechanism for controlling "
        "alignment relevant character traits, with no claim that steering alone produces reliable safety."
    ),
    "uncertain": (
        "We discuss a possible connection between character descriptions and training outcomes. "
        "The available document does not explain whether the intervention updates model weights "
        "or supplies a prompt, and its evaluation protocol is missing. More source text "
        "is needed to distinguish assistant character training from fictional role playing."
    ),
    "invalid": (
        "We measure unintended trait changes after assistant character fine tuning. "
        "The study evaluates honesty and sycophancy using held out questions and compares "
        "trained models with prompted controls. It reports mixed results across tasks "
        "and does not establish that any intervention guarantees aligned behavior in deployment."
    ),
}


def work(number, kind, url):
    inverted = {}
    for position, token in enumerate(TEXTS[kind].split()):
        inverted.setdefault(token, []).append(position)
    result = {
        "id": f"https://openalex.org/W{number}",
        # Intentionally misleading titles: the judge request must contain the actual abstract.
        "title": "Character alignment training" if kind == "roleplay" else "Experimental study",
        "publication_date": "2026-01-01",
        "primary_location": {"landing_page_url": url},
        "abstract_inverted_index": inverted,
        "authorships": [{"author": {"display_name": "Fixture Author"}}],
    }
    if kind == "core":
        result["best_oa_location"] = {
            "is_oa": True,
            "pdf_url": "https://arxiv.org/pdf/2601.00001",
            "license": "cc-by",
        }
    return result


def run_smoke(provider="brave", failures=False):
    config = read_json(ROOT / "config/discovery.json")
    taxonomy = read_json(ROOT / "config/taxonomy.json")
    config.update(
        openalex_queries=["fixture character training"],
        web_queries=["fixture persona safety"],
        feeds=[{"name": "Fixture feed", "url": "https://research.example/feed"}],
        indexes=[{"name": "Fixture index", "url": "https://research.example/", "path_pattern": "/post$"}],
        repositories=["https://raw.githubusercontent.com/example/fixture/main/README.md"],
    )
    config["limits"].update(openalex_queries=1, web_queries=1, citation_seeds=1, judge_items=10)
    works = [work(1, "core", CORE_URL), work(2, "roleplay", ROLE_URL), work(3, "exclude", EXCLUDE_URL)]
    urls = [POST_URL]
    if failures:
        urls += [f"https://research.example/{kind}" for kind in ["uncertain", "invalid", "missing"]]
    pdf = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(pdf)
    calls = []
    judge_inputs = []

    def transport(session, method, url, **kwargs):
        calls.append((method, url))
        data, body = None, None
        if url == "https://api.openalex.org/works":
            params = kwargs["params"]
            results = (
                works if "search" in params else ([] if params["filter"].startswith("cites:") else [works[1]])
            )
            data = {"results": results, "meta": {"count": len(results)}}
        elif url == "https://api.openalex.org/works/https://openalex.org/W1":
            data = dict(works[0], referenced_works=["https://openalex.org/W2"])
        elif url == "https://api.search.brave.com/res/v1/web/search":
            assert kwargs["headers"]["X-Subscription-Token"] == "fixture-search-key"
            data = {
                "web": {
                    "results": [
                        {"url": u, "title": "Search title", "description": "NEVER EVIDENCE"} for u in urls
                    ]
                }
            }
        elif url == "https://google.serper.dev/search":
            assert kwargs["headers"]["X-API-KEY"] == "fixture-search-key"
            data = {
                "organic": [{"link": u, "title": "Search title", "snippet": "NEVER EVIDENCE"} for u in urls]
            }
        elif url.endswith("/feed"):
            body = f'<rss version="2.0"><channel><title>Fixture</title><item><title>Feed title</title><link>{POST_URL}</link></item></channel></rss>'.encode()
        elif url == "https://research.example/":
            body = b'<a href="/post">Index title</a>'
        elif url.startswith("https://raw.githubusercontent.com/"):
            body = f"[Paper]({CORE_URL})".encode()
        elif url == "https://arxiv.org/pdf/2601.00001":
            body = pdf.getvalue()
        elif url.startswith("https://research.example/"):
            kind = url.rsplit("/", 1)[-1]
            content = TEXTS.get("mechanism" if kind == "post" else kind, "Title only")
            body = f"<html><h1>Publisher title</h1><article>{content}</article></html>".encode()
        elif url == "https://judge.example/v1/chat/completions":
            assert method == "POST" and kwargs["headers"]["Authorization"] == "Bearer fixture-llm-key"
            payload = kwargs["json"]
            evidence = json.loads(payload["messages"][1]["content"])
            assert evidence["evidence_kind"] in {"abstract", "full-text"}
            assert evidence["source_text"] in TEXTS.values()
            assert "NEVER EVIDENCE" not in evidence["source_text"]
            kind = next(k for k, v in TEXTS.items() if evidence["source_text"] == v)
            judge_inputs.append(kind)
            scope = "core" if kind == "invalid" else kind
            decision = {
                "scope": scope,
                "confidence": 0.5 if kind == "uncertain" else 0.96,
                "summary": "Fixture classification used to verify the complete processing pipeline.",
                "rationale": "The fixture response is grounded in the supplied abstract or article body.",
                "evidence_quote": " ".join(TEXTS[kind].split()[:12]),
                "interventions": ["evaluation"],
                "themes": ["roleplay" if kind == "roleplay" else "measurement"],
            }
            if kind == "invalid":
                decision["evidence_quote"] = (
                    "A fabricated quotation which does not occur anywhere in the source"
                )
            data = {"choices": [{"message": {"content": json.dumps(decision)}}]}
        else:
            raise AssertionError(f"Unexpected HTTP request: {method} {url}")
        response = requests.Response()
        response.status_code = 200
        response.url = url
        response.encoding = "utf-8"
        response.raw = io.BytesIO(body if body is not None else json.dumps(data).encode())
        return response

    env = {
        "LLM_API_KEY": "fixture-llm-key",
        "LLM_BASE_URL": "https://judge.example/v1",
        "LLM_MODEL": "fixture-small-model",
        "BRAVE_API_KEY": "fixture-search-key" if provider == "brave" else "",
        "SERPER_API_KEY": "fixture-search-key" if provider == "serper" else "",
        "OPENALEX_API_KEY": "",
    }
    # No real network calls or real credentials: patches are confined to this process.
    with TemporaryDirectory(prefix="persona-smoke-") as directory, chdir(directory):
        write_json("config/discovery.json", config)
        write_json("config/taxonomy.json", taxonomy)
        with (
            patch.dict(os.environ, env, clear=True),
            patch("requests.sessions.Session.request", transport),
            patch(
                "socket.getaddrinfo",
                return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))],
            ),
            patch("persona_map.cli.sync", side_effect=AssertionError("NotebookLM must stay disabled")),
            patch.object(sys, "argv", ["persona-map", "run", "--until", "2026-10-28", "--backfill"]),
        ):
            main()
            first = read_json("reports/latest-run.json")
            catalogue = read_json("data/catalogue.json")
            candidates = read_json("data/candidates.json")
            assert len(catalogue) == 2
            assert {r["scope"] for r in catalogue} == {"core", "mechanism"}
            assert first["accepted"] == 2 and first["downloaded"] == 1
            assert first["judged"] == (5 if failures else 4)
            assert first["status"] == ("degraded" if failures else "ok")
            assert len(first["judge_errors"]) == (2 if failures else 0)
            by_url = {r["url"]: r for r in candidates}
            assert by_url[ROLE_URL]["status"] == "roleplay"
            assert by_url[EXCLUDE_URL]["status"] == "excluded"
            if failures:
                assert by_url["https://research.example/uncertain"]["status"] == "uncertain"
                assert by_url["https://research.example/invalid"]["status"] == "pending"
                assert by_url["https://research.example/missing"]["status"] == "needs-text"
            manifest = read_json("data/notebooklm-manifest.json")["sources"]
            saved = next(r for r in manifest if r["status"] == "downloaded")
            assert hashlib.sha256(Path(saved["path"]).read_bytes()).hexdigest() == saved["sha256"]
            for record in catalogue:
                evidence = record["evidence"]
                assert (
                    hashlib.sha256(Path(evidence["local_path"]).read_bytes()).hexdigest()
                    == evidence["sha256"]
                )
            generated = {
                p: Path(p).read_bytes()
                for p in [
                    "data/catalogue.json",
                    "data/catalogue.csv",
                    "data/catalogue.bib",
                    "docs/catalogue.md",
                ]
            }
            inputs_before = len(judge_inputs)
            main()
            second = read_json("reports/latest-run.json")
            assert second["judged"] == second["accepted"] == second["downloaded"] == 0
            assert len(judge_inputs) == inputs_before
            assert len(read_json("data/candidates.json")) == len(candidates)
            assert any(e["channel"] == "citations" and e["status"] == "ok" for e in second["events"])
            assert all(Path(p).read_bytes() == content for p, content in generated.items())
            assert sum(url.endswith("/pdf/2601.00001") for _, url in calls) == 1
            assert "notebooklm" not in first and "notebooklm" not in second
    return {
        "provider": provider,
        "failure_fixtures": failures,
        "first_run": {k: first[k] for k in ["status", "judged", "accepted", "downloaded", "pending"]},
        "repeat_run": {k: second[k] for k in ["judged", "accepted", "downloaded"]},
        "network": "mocked; no real credentials used",
        "notebooklm": "disabled",
    }


def smoke_main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["brave", "serper"], default="brave")
    parser.add_argument("--failure-cases", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_smoke(args.provider, args.failure_cases), indent=2))


if __name__ == "__main__":
    smoke_main()

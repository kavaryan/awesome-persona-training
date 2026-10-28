import hashlib
import io
import json
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError
from pypdf import PdfWriter

from persona_map.discovery import citations, reconstruct_abstract, web_search
from persona_map.downloads import download, validate_pdf
from persona_map.evidence import html_evidence, retrieve
from persona_map.judge import judge, validate_decision
from persona_map.net import BudgetExceeded, Client, public_url
from persona_map.notebooklm import sync
from persona_map.store import canonical_url, merge_candidates, read_json

TAXONOMY = json.loads(Path("config/taxonomy.json").read_text())
TEXT = (
    "We train assistant character traits using a written constitution and evaluate safety under distribution shift. "
    "Our experiments compare fine tuning against prompting, and assess honesty and unintended changes to other traits. "
    "The effects depend on the model and evaluation context rather than holding universally."
)


class Response:
    def __init__(self, text="", data=None, content=None):
        self.text = text
        self.content = content if content is not None else text.encode()
        self.data = data

    def json(self):
        return self.data


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        result = next(self.responses)
        if isinstance(result, Exception):
            raise result
        return result

    def json(self, url, **kwargs):
        return self.get(url, **kwargs).json()

    def request(self, method, url, **kwargs):
        return self.get(url, **kwargs)


def decision(**overrides):
    return dict(
        {
            "scope": "core",
            "confidence": 0.95,
            "summary": "Studies constitutional assistant training and its safety consequences.",
            "rationale": "The study changes persistent assistant traits and tests their safety consequences.",
            "evidence_quote": "We train assistant character traits using a written constitution",
            "interventions": ["sft", "evaluation"],
            "themes": ["constitutions", "honesty"],
        },
        **overrides,
    )


def test_merge_arxiv_doi_versions_and_crossposts():
    rows = [
        {"url": "https://arxiv.org/abs/2511.01689v2", "provenance": ["search"]},
        {"url": "https://doi.org/10.48550/arXiv.2511.01689", "provenance": ["citations"]},
        {"url": "https://arxiv.org/pdf/2511.01689", "provenance": ["feed"]},
    ]
    result = merge_candidates([], rows)
    assert len(result) == 1
    assert result[0]["provenance"] == ["citations", "feed", "search"]
    assert canonical_url("https://www.alignmentforum.org/posts/abc/title?utm_source=x") == canonical_url(
        "https://www.lesswrong.com/posts/abc/other"
    )
    assert len(merge_candidates(result, rows)) == 1


def test_verified_published_alias_prevents_double_counting():
    accepted = [
        {"url": "https://arxiv.org/abs/2507.21919", "aliases": ["https://doi.org/10.1038/s41586-026-10410-0"]}
    ]
    assert not merge_candidates([], [{"url": "https://doi.org/10.1038/S41586-026-10410-0"}], accepted)


def test_abstract_reconstruction_uses_positions():
    assert reconstruct_abstract({"safety": [2], "We": [0], "study": [1]}) == "We study safety"


def test_title_and_search_snippet_cannot_replace_source(tmp_path):
    r = {"url": "https://example.org/paper", "title": "Amazing persona alignment", "snippet": TEXT}
    with pytest.raises(ValueError, match="No usable"):
        retrieve(FakeClient([Response("<html><h1>Amazing persona alignment</h1></html>")]), r, tmp_path)


def test_publisher_abstract_is_evidence_and_cited_pdf_is_not_own_pdf(tmp_path):
    html = f'<h1>A paper</h1><blockquote class="abstract">Abstract: {TEXT}</blockquote><a href="https://example.org/cited.pdf">Earlier work</a>'
    r = {"url": "https://example.org/paper"}
    text, e = retrieve(FakeClient([Response(html)]), r, tmp_path)
    assert e["kind"] == "abstract" and e["sha256"] == hashlib.sha256(text.encode()).hexdigest()
    assert not r.get("pdf_url")
    assert (
        html_evidence('<a href="/paper.pdf">Download PDF</a>', "https://example.org/p")["pdf_url"]
        == "https://example.org/paper.pdf"
    )


def test_judge_requires_text_before_network():
    client = FakeClient([])
    with pytest.raises(ValueError, match="Abstract or full text"):
        judge(client, {"title": "Persona"}, "Persona alignment", {}, TAXONOMY)
    assert not client.calls


def test_fabricated_quote_and_unknown_tags_rejected():
    with pytest.raises(ValueError, match="not in supplied"):
        validate_decision(
            decision(evidence_quote="This study proves complete alignment forever"), TEXT, TAXONOMY
        )
    with pytest.raises(ValidationError):
        validate_decision(decision(themes=["invented-category"]), TEXT, TAXONOMY)
    validate_decision(decision(), TEXT, TAXONOMY)


def test_classifier_response_and_input_grounding(monkeypatch):
    for k, v in [
        ("LLM_API_KEY", "fake"),
        ("LLM_BASE_URL", "https://example.org/v1"),
        ("LLM_MODEL", "small-model"),
    ]:
        monkeypatch.setenv(k, v)
    client = FakeClient([Response(data={"choices": [{"message": {"content": json.dumps(decision())}}]})])
    result = judge(
        client,
        {"title": "Untrusted title"},
        TEXT,
        {"url": "https://example.org/p", "kind": "abstract"},
        TAXONOMY,
    )
    assert result["model"] == "small-model"
    request = client.calls[0][1]["json"]
    assert TEXT in request["messages"][1]["content"]
    assert request["max_tokens"] == 650 and result["scope"] == "core"


def test_missing_judge_does_not_make_keyword_decisions(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="unconfigured"):
        judge(FakeClient([]), {"title": "Character training"}, TEXT, {}, TAXONOMY)


def pdf_bytes():
    out = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(out)
    return out.getvalue()


def test_download_rejects_html_and_preserves_working_pdf(tmp_path):
    record = {"id": "paper", "url": "https://arxiv.org/abs/2511.01689"}
    bad = download(FakeClient([Response("<h1>Captcha</h1>")]), record, tmp_path)
    assert bad["status"] == "unavailable" and not list(tmp_path.glob("*.pdf"))
    content = pdf_bytes()
    good = download(FakeClient([Response(content=content)]), record, tmp_path)
    assert good["sha256"] == hashlib.sha256(content).hexdigest()
    record["download"] = good
    assert download(FakeClient([]), record, tmp_path) == good
    with pytest.raises(ValueError):
        validate_pdf(b"not a PDF")


def test_citation_directions_and_resume():
    responses = [
        Response(
            data={
                "id": "https://openalex.org/W1",
                "referenced_works": ["https://openalex.org/W2", "https://openalex.org/W3"],
            }
        ),
        Response(data={"results": [{"id": "https://openalex.org/W2", "title": "Ref"}]}),
        Response(
            data={"results": [{"id": "https://openalex.org/W4", "title": "Citer"}], "meta": {"count": 3}}
        ),
    ]
    client = FakeClient(responses)
    rows, state = citations(
        client, {"openalex": "https://openalex.org/W1", "url": "https://example.org/p"}, {}, 1
    )
    assert len(rows) == 2 and state["reference_offset"] == 1 and state["citing_page"] == 2
    assert client.calls[-1][1]["params"]["filter"] == "cites:W1"
    assert "reference-of" in rows[0]["provenance"][0]


def test_fulltext_references_when_openalex_has_none():
    client = FakeClient(
        [
            Response(data={"id": "https://openalex.org/W1", "referenced_works": []}),
            Response('<li class="ltx_bibitem"><a href="https://arxiv.org/abs/2507.21509">ref</a></li>'),
            Response(data={"results": [], "meta": {"count": 0}}),
        ]
    )
    rows, _ = citations(client, {"url": "https://arxiv.org/abs/2511.01689"}, {}, 50)
    assert len(rows) == 1 and rows[0]["provenance"][0].startswith("fulltext-reference:")


def test_web_results_are_leads_not_evidence(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "fake")
    client = FakeClient(
        [
            Response(
                data={
                    "web": {
                        "results": [{"title": "Persona", "url": "https://example.org/a", "description": TEXT}]
                    }
                }
            )
        ]
    )
    rows = web_search(client, "persona")
    assert (
        rows[0]["url"] == "https://example.org/a" and "abstract" not in rows[0] and "snippet" not in rows[0]
    )


def test_private_network_and_bad_schemes_blocked():
    for url in [
        "file:///etc/passwd",
        "http://example.org",
        "https://127.0.0.1",
        "https://169.254.169.254",
        "https://user:pass@example.org",
    ]:
        with pytest.raises(ValueError):
            public_url(url)


def test_budget_stops_before_request(monkeypatch):
    monkeypatch.setattr("persona_map.net.public_url", lambda u: u)
    client = Client(max_requests=0)
    with pytest.raises(BudgetExceeded):
        client.get("https://example.org")


def test_notebook_remote_reconciliation_prevents_duplicate_after_crash(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NOTEBOOKLM_NOTEBOOK", "projects/123/locations/global/notebooks/abc")
    monkeypatch.setenv("GOOGLE_ACCESS_TOKEN", "fake")
    content = pdf_bytes()
    digest = hashlib.sha256(content).hexdigest()
    Path("downloads").mkdir()
    Path("downloads/paper.pdf").write_bytes(content)
    manifest = [
        {
            "id": "paper",
            "title": "A paper",
            "status": "downloaded",
            "path": "downloads/paper.pdf",
            "sha256": digest,
        }
    ]
    marker = f"persona-paper-{digest[:16]}.pdf"
    client = FakeClient([Response(data={"sources": [{"title": marker, "sourceId": {"id": "remote"}}]})])
    result = sync(client, manifest, "state.json")
    assert result["uploaded"] == 0 and len(client.calls) == 1
    assert read_json("state.json")
    # New upload: no retry of non-idempotent upload; save successful source immediately.
    client = FakeClient([Response(data={"sources": []}), Response(data={"sourceId": {"id": "new"}})])
    assert sync(client, manifest, "state.json")["uploaded"] == 1
    assert client.calls[1][1]["retries"] == 0


def test_notebook_checksum_failure_prevents_upload(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NOTEBOOKLM_NOTEBOOK", "projects/123/locations/global/notebooks/abc")
    monkeypatch.setenv("GOOGLE_ACCESS_TOKEN", "fake")
    Path("downloads").mkdir()
    Path("downloads/p.pdf").write_bytes(b"changed")
    client = FakeClient([Response(data={"sources": []})])
    with pytest.raises(ValueError, match="checksum"):
        sync(
            client,
            [{"id": "p", "status": "downloaded", "path": "downloads/p.pdf", "sha256": "wrong"}],
            "state.json",
        )
    assert len(client.calls) == 1


def test_later_alias_bridges_previously_separate_candidates():
    existing = merge_candidates(
        [],
        [
            {"url": "https://arxiv.org/abs/2507.21919", "provenance": ["arxiv"]},
            {"url": "https://doi.org/10.1038/example", "provenance": ["journal"]},
        ],
    )
    bridge = {
        "url": "https://arxiv.org/abs/2507.21919",
        "aliases": ["https://doi.org/10.1038/example"],
        "provenance": ["verified-link"],
    }
    result = merge_candidates(existing, [bridge])
    assert len(result) == 1
    assert set(result[0]["provenance"]) == {"arxiv", "journal", "verified-link"}


def test_daily_run_without_judge_retains_candidates_and_reports_degradation(tmp_path, monkeypatch):
    from argparse import Namespace

    from persona_map.cli import run
    from persona_map.store import write_json

    config = json.loads(Path("config/discovery.json").read_text())
    config["limits"]["downloads"] = 0
    monkeypatch.chdir(tmp_path)
    write_json("config/discovery.json", config)
    write_json("config/taxonomy.json", TAXONOMY)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setattr(
        "persona_map.cli.collect",
        lambda *a, **k: (
            [{"url": "https://example.org/paper", "title": "Persona safety", "abstract": TEXT}],
            [{"channel": "openalex", "status": "ok", "candidates": 1}],
        ),
    )
    run(Namespace(until="2026-10-28", backfill=False, download_only=False, sync_notebook=False))
    assert read_json("data/candidates.json")[0]["status"] == "pending"
    assert read_json("data/catalogue.json") == []
    assert read_json("reports/latest-run.json")["status"] == "degraded"

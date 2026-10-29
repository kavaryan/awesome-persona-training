import io
import json
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest
from pypdf import PdfWriter

from research_factory.bootstrap import initialize, recover_plan
from research_factory.runtime import cli
from research_factory.runtime.evidence import retrieve
from research_factory.runtime.judge import agreed, classify, validate_decision
from research_factory.runtime.pipeline import apply_decision
from research_factory.runtime.store import read_json
from research_factory.schema import validate_plan

TEXT = (
    "We intervene on complete messages in recorded agent conversations and replay subsequent actions. "
    "We compare the distributions of tool choices before and after removing a message, measuring "
    "changes in harmful outcomes across repeated rollouts. This analyzes observable execution traces "
    "rather than hidden activations, and includes controls for stochastic variation."
)
NEGATIVE = (
    "We study the internal neurons of a transformer language model through causal activation patching. "
    "Our interventions replace hidden representations in individual layers during a single forward pass. "
    "The experiments localize factual associations within network weights, without analyzing conversations, "
    "tool interactions, agent trajectories, external messages, or replaying execution traces."
)


def plan(topic="Causality"):
    return {
        "title": topic + " Research",
        "slug": "awesome-test-research",
        "description": "Research with a precise scope and source-grounded taxonomy.",
        "include": ["Interventions on observable conversational execution traces."],
        "exclude": ["Causal activation patching in model internals."],
        "boundaries": ["A keyword match is a discovery lead, never evidence of relevance."],
        "keywords": [
            {"concept": k, "terms": [k], "reason": "Method vocabulary from the supplied brief."}
            for k in ["replay", "counterfactual", "messages"]
        ],
        "openalex_queries": ["query " + str(n) for n in range(4)],
        "web_queries": ["query " + str(n) for n in range(4)],
        "feeds": [],
        "indexes": [],
        "repositories": [],
        "dimensions": [
            {
                "name": "granularity",
                "description": "Unit changed by an intervention.",
                "values": ["message", "not-reported"],
            },
            {
                "name": "effect",
                "description": "What distribution or outcome is compared.",
                "values": ["action-distribution", "not-reported"],
            },
        ],
        "works": [
            {
                "title": "Misleading causal title",
                "url": f"https://example.org/{n}",
                "seed": n == 0,
                "found_via": "fixture source",
            }
            for n in range(4)
        ],
        "search_log": [
            {
                "query": "fixture query",
                "source": "https://example.org",
                "finding": "Synthetic integration fixture, not real research.",
            }
        ],
        "coverage_limits": ["Fixture results do not establish real-world precision or recall."],
    }


def decision(project, scope="core", text=TEXT):
    return {
        "scope": scope,
        "confidence": 0.98,
        "summary": "Examines observable agent behavior through controlled message interventions.",
        "rationale": "The intervention targets complete conversational messages and subsequent tool actions.",
        "evidence_quote": " ".join(text.split()[:12]),
        "facets": {
            d["name"]: {
                "values": [d["values"][0]],
                "detail": "Compares action distributions under message removal.",
            }
            for d in project["dimensions"]
        },
    }


class Response:
    def __init__(self, text="", content=None, data=None):
        self.text = text
        self.content = content if content is not None else text.encode()
        self.data = data

    def json(self):
        return self.data


class FixtureClient:
    def __init__(self, *args, **kwargs):
        self.count = 0

    def get(self, url, **kwargs):
        self.count += 1
        if url.endswith(".pdf"):
            buf = io.BytesIO()
            writer = PdfWriter()
            writer.add_blank_page(width=100, height=100)
            writer.write(buf)
            return Response(content=buf.getvalue())
        return Response(
            f'<h1>Primary publisher title</h1><article>{TEXT}</article><meta name="citation_pdf_url" content="https://example.org/work.pdf">'
        )


class FixtureAgent:
    model = "fixture-agent"

    def __init__(self, topic="Causality", invalid=False):
        self.project = plan(topic)
        self.calls = []
        self.invalid = invalid

    def call(self, prompt, schema, directory, name, search=False):
        self.calls.append(name)
        if name.startswith("plan"):
            return self.project
        if name.startswith("expansion"):
            return {
                k: self.project[k] if k != "works" else []
                for k in ["works", "openalex_queries", "web_queries", "search_log", "coverage_limits"]
            }
        if name == "taxonomy-review":
            return {
                "dimensions": self.project["dimensions"],
                "requirement_mapping": [
                    {
                        "requested_facet": "requested facets",
                        "dimensions": [d["name"] for d in self.project["dimensions"]],
                    }
                ],
                "unresolved": [],
            }
        assert TEXT in prompt
        assert "No previous catalogue labels" in prompt
        ids = schema["properties"]["decisions"]["items"]["properties"]["id"]["enum"]
        result = decision(self.project)
        if self.invalid:
            result["evidence_quote"] = "An invented quotation that never appears in the actual document"
        if name.startswith("audit"):
            result = {k: result[k] for k in ["scope", "confidence", "rationale", "evidence_quote"]}
        return {"decisions": [{"id": rid, "decision": result} for rid in ids]}


def args(tmp_path, topic="Causality", **changes):
    brief = tmp_path / "brief.md"
    brief.write_text(topic + " project with seed papers")
    values = dict(
        brief=str(brief),
        output=str(tmp_path / "output"),
        until="2026-10-29",
        resume=False,
        plan=None,
        stage="all",
        agent="codex",
        model=None,
        agent_timeout=60,
        agent_budget=120,
        review_limit=4,
        batch_size=2,
        download_limit=4,
    )
    values.update(changes)
    return Namespace(**values)


@pytest.mark.parametrize("topic", ["Causality", "Persona"])
def test_factory_builds_independent_repository_and_checkpointed_reviews(tmp_path, monkeypatch, topic):
    monkeypatch.setattr("research_factory.bootstrap.Client", FixtureClient)
    monkeypatch.setattr("research_factory.bootstrap.collect", lambda *a, **k: ([], []))
    monkeypatch.setattr(
        "research_factory.bootstrap.seed_citation_sweep", lambda *a, **k: ([], {"events": [], "requests": 0})
    )
    agent = FixtureAgent(topic)
    options = args(tmp_path, topic)
    report = initialize(options, agent)
    output = Path(options.output)
    assert report["accepted"] == 4
    assert len([n for n in agent.calls if n.startswith("audit")]) == 2
    assert (output / ".git").is_dir()
    assert (output / "research_map/cli.py").is_file()
    assert not (output / "persona_map").exists()
    assert (output / "PROJECT.md").read_text().startswith(topic)
    assert "--sync-notebook" not in (output / ".github/workflows/discover.yml").read_text()
    assert len(read_json(output / "data/notebooklm-manifest.json")["sources"]) == 4
    proc = subprocess.run(
        [sys.executable, "-m", "research_map.cli", "validate"], cwd=output, capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr
    options.resume = True
    previous = len(agent.calls)
    initialize(options, agent)
    assert len(agent.calls) == previous
    assert len(read_json(output / "data/catalogue.json")) == 4


def test_rejects_title_only_evidence_even_with_a_search_snippet(tmp_path):
    class TitleOnly:
        def get(self, *a, **k):
            return Response("<h1>Causal Agent Conversation Alignment Safety</h1>")

    with pytest.raises(ValueError, match="No usable"):
        retrieve(TitleOnly(), {"url": "https://example.org/p", "snippet": TEXT}, tmp_path)


def test_evidence_quote_and_taxonomy_validation():
    project = plan()
    bad = decision(project)
    bad["evidence_quote"] = "This source certainly guarantees complete alignment in all deployment settings"
    with pytest.raises(ValueError, match="absent"):
        validate_decision(bad, TEXT, project)
    assert validate_decision(decision(project), TEXT, project)


def test_two_readings_must_agree_and_missing_facets_are_not_invented():
    first = decision(plan())
    second = decision(plan(), "exclude")
    assert not agreed(first, second)
    record = {"id": "a", "url": "https://example.org/a"}
    catalogue = []
    apply_decision(record, first, second, {}, catalogue, "2026-10-29", "test")
    assert record["status"] == "uncertain" and not catalogue


def test_invalid_agent_evidence_never_enters_catalogue(tmp_path, monkeypatch):
    monkeypatch.setattr("research_factory.bootstrap.Client", FixtureClient)
    monkeypatch.setattr("research_factory.bootstrap.collect", lambda *a, **k: ([], []))
    monkeypatch.setattr(
        "research_factory.bootstrap.seed_citation_sweep", lambda *a, **k: ([], {"events": [], "requests": 0})
    )
    options = args(tmp_path)
    report = initialize(options, FixtureAgent(invalid=True))
    assert report["accepted"] == 0
    assert read_json(Path(options.output) / "reports/bootstrap-review.json")["errors"]


def test_factory_refuses_existing_nonfactory_directory(tmp_path):
    options = args(tmp_path, resume=True)
    output = Path(options.output)
    output.mkdir()
    (output / "README.md").write_text("Existing user's work")
    with pytest.raises(ValueError, match="non-factory"):
        initialize(options, FixtureAgent())
    assert (output / "README.md").read_text() == "Existing user's work"


def test_resume_rejects_changed_brief(tmp_path, monkeypatch):
    options = args(tmp_path, stage="plan")
    initialize(options, FixtureAgent())
    options.resume = True
    Path(options.brief).write_text("Different scope")
    with pytest.raises(ValueError, match="Brief changed"):
        initialize(options, FixtureAgent())


def test_plan_validation_blocks_credentials_in_urls_and_duplicate_dimensions():
    p = plan()
    p["works"][0]["url"] = "https://user:secret@example.org/paper"
    with pytest.raises(ValueError, match="credential-free"):
        validate_plan(p)
    p = plan()
    p["dimensions"].append(p["dimensions"][0])
    with pytest.raises(ValueError, match="Duplicate"):
        validate_plan(p)


def test_recovery_only_uses_completed_research_events(tmp_path):
    (tmp_path / "plan.events.jsonl").write_text(
        json.dumps({"type": "item.completed", "item": {"type": "web_search", "query": "fixture query"}})
        + "\n"
    )
    assert recover_plan(FixtureAgent(), "brief", "2026-10-29", tmp_path)["slug"].startswith("awesome-")


def test_daily_judge_receives_body_without_title_or_snippet(monkeypatch):
    project = plan()
    for key, value in {
        "LLM_API_KEY": "fixture",
        "LLM_BASE_URL": "https://provider.example/v1",
        "LLM_MODEL": "small-fixture",
    }.items():
        monkeypatch.setenv(key, value)

    class Service:
        def request(self, method, url, **kwargs):
            payload = kwargs["json"]
            evidence = json.loads(payload["messages"][1]["content"])
            assert evidence["source_text"] == TEXT
            assert "Misleading title" not in payload["messages"][1]["content"]
            return Response(data={"choices": [{"message": {"content": json.dumps(decision(project))}}]})

    result = classify(
        Service(),
        project,
        {"title": "Misleading title", "snippet": "bad"},
        TEXT,
        {"url": "https://example.org/p", "kind": "abstract"},
    )
    assert result["scope"] == "core"


def test_daily_run_accepts_grounded_paper_and_rerun_is_idempotent(tmp_path, monkeypatch):
    options = args(tmp_path, stage="plan")
    initialize(options, FixtureAgent())
    monkeypatch.chdir(options.output)
    monkeypatch.setattr(cli, "Client", FixtureClient)
    monkeypatch.setattr(cli, "collect", lambda *a, **k: ([], []))
    monkeypatch.setattr(
        cli, "classify", lambda client, project, row, text, evidence, audit=False: decision(project)
    )
    for key in ["LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"]:
        monkeypatch.setenv(key, "fixture")
    run_args = Namespace(until="2026-10-29", backfill=False, download_only=False)
    first = cli.run(run_args)
    assert first["accepted"] == 4 and first["model_calls"] == 8
    assert first["downloaded"] == 4
    snapshot = Path("data/catalogue.json").read_bytes()
    second = cli.run(run_args)
    assert second["accepted"] == second["model_calls"] == second["downloaded"] == 0
    assert Path("data/catalogue.json").read_bytes() == snapshot


def test_missing_judge_retains_candidates(tmp_path, monkeypatch):
    options = args(tmp_path, stage="plan")
    initialize(options, FixtureAgent())
    monkeypatch.chdir(options.output)
    monkeypatch.setattr(cli, "Client", FixtureClient)
    monkeypatch.setattr(cli, "collect", lambda *a, **k: ([], []))
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    report = cli.run(Namespace(until="2026-10-29", backfill=False, download_only=False))
    assert report["judge"] == "not-configured" and report["pending"] == 4
    assert not read_json("data/catalogue.json")


def test_wire_schema_retains_local_uniqueness_check():
    from research_factory.agent import wire_schema
    from research_factory.runtime.judge import decision_schema

    original = decision_schema(plan())
    wire = wire_schema(original)
    assert "uniqueItems" not in json.dumps(wire)
    assert "uniqueItems" in json.dumps(original)
    assert wire["properties"]["scope"] == original["properties"]["scope"]


def test_taxonomy_change_cannot_reinterpret_existing_workspace(tmp_path):
    from research_factory.scaffold import scaffold

    p = plan()
    scaffold(tmp_path, "brief", p, "2026-10-29")
    p["include"] = ["A different research setting"]
    with pytest.raises(ValueError, match="scope or taxonomy changed"):
        scaffold(tmp_path, "brief", p, "2026-10-29")


def test_operational_query_and_path_compilation():
    import re

    from research_factory.compile import path_regex, query_text

    assert query_text("search=causal+agent&filter=to_publication_date:2026-10-29") == "causal agent"
    assert query_text("persona vectors") == "persona vectors"
    assert re.search(path_regex("/{year}/{slug}/"), "/2026/example-paper/")
    assert re.search(path_regex("/v{volume}/{paper_id}.html"), "/v306/paper26.html")
    with pytest.raises(ValueError, match="executable"):
        path_regex("unverified; resolve later")


def test_explicit_seed_urls_cannot_be_silently_dropped_by_agent():
    from research_factory.seeds import include_input_urls

    p = include_input_urls(
        plan(), "Seed https://arxiv.org/abs/2511.01689 and https://github.com/example/research-list"
    )
    assert any(w["url"] == "https://arxiv.org/abs/2511.01689" and w["seed"] for w in p["works"])
    assert "https://github.com/example/research-list" in p["repositories"]


def test_batch_preserves_other_decisions_when_one_quote_is_invalid(tmp_path):
    from research_factory.bootstrap import batch_review

    class MixedAgent:
        model = "fixture"

        def call(self, *args, **kwargs):
            good = decision(plan())
            bad = dict(good, evidence_quote="This fabricated passage has no support in any supplied evidence")
            return {"decisions": [{"id": "good", "decision": good}, {"id": "bad", "decision": bad}]}

    evidence = {"url": "https://example.org/p", "kind": "abstract"}
    records = [({"id": rid}, TEXT, evidence) for rid in ["good", "bad"]]
    results = batch_review(MixedAgent(), plan(), records, False, tmp_path, "read")
    assert set(results) == {"good"}
    assert "absent" in results.errors["bad"]


def test_unindexed_post_citations_include_nonacademic_sources_but_not_navigation():
    from research_factory.runtime.discovery import citations

    class PostClient:
        def get(self, *args, **kwargs):
            return Response("""<nav><a href="/sign-in">Login</a></nav>
            <article><p>Primary report with references.</p>
            <a href="https://lab.example/constitution">Background constitution</a>
            <a href="https://arxiv.org/abs/1234.56789">Paper</a>
            <a href="#methods">Methods</a><a href="plot.png">Figure</a></article>""")

    rows, progress = citations(PostClient(), {"url": "https://blog.example/report"}, {})
    assert {r["url"] for r in rows} == {
        "https://lab.example/constitution",
        "https://arxiv.org/abs/1234.56789",
    }
    assert progress["status"] == "ok"


def test_resume_normalizes_saved_api_queries_and_preserves_new_vocabulary(tmp_path):
    from research_factory.runtime.store import write_json
    from research_factory.scaffold import scaffold

    project = plan()
    scaffold(tmp_path, "Brief", project, "2026-10-29")
    config = read_json(tmp_path / "config/discovery.json")
    config["openalex_queries"] += ["search=unexpected+vocabulary&filter=type:article"]
    write_json(tmp_path / "config/discovery.json", config)
    _, updated = scaffold(tmp_path, "Brief", project, "2026-10-30")
    assert "unexpected vocabulary" in updated["openalex_queries"]
    assert all(not q.startswith("search=") for q in updated["openalex_queries"])


def test_daily_scheduling_reserves_new_arrivals_without_starving_backlog():
    from research_factory.runtime.pipeline import review_schedule

    old = [{"id": f"old-{n:03}", "status": "pending", "first_seen": "2026-09-01"} for n in range(100)]
    new = [{"id": f"new-{n:03}", "status": "pending", "first_seen": "2026-10-29"} for n in range(20)]
    delayed = {"id": "retry", "status": "uncertain", "retry_after": "2026-11-01"}
    selected = review_schedule(old + new + [delayed], "2026-10-29", 24)
    assert len(selected) == 24
    assert sum(r["id"].startswith("new") for r in selected) == 12
    assert sum(r["id"].startswith("old") for r in selected) == 12
    assert len({r["id"] for r in selected}) == 24


def test_openalex_broad_and_abstract_searches_have_distinct_cursors():
    from research_factory.runtime.discovery import collect
    from research_factory.scaffold import LIMITS

    class SearchClient:
        def __init__(self):
            self.parameters = []

        def json(self, url, **kwargs):
            self.parameters.append(kwargs["params"])
            return {"results": [], "meta": {"count": 0}}

    config = plan()
    config.update(lookback_days=21, limits=dict(LIMITS, openalex_queries=1, web_queries=0, pages_per_query=1))
    client, state = SearchClient(), {}
    rows, events = collect(client, config, state, [], "2026-10-29", historical=True)
    assert not rows and len(events) == 2
    assert "search" in client.parameters[0]
    assert "search.title_and_abstract" in client.parameters[1]
    assert set(state["pages"]) == {"historical:all:query 0", "historical:title_and_abstract:query 0"}


def test_blocked_publisher_seed_can_use_indexed_primary_abstract(tmp_path):
    class BlockedPublisher:
        def get(self, *args, **kwargs):
            raise RuntimeError("HTTP 403 from publisher")

        def json(self, url, **kwargs):
            assert url.endswith("https://doi.org/10.1038/s41586-026-10410-0")
            return {
                "id": "https://openalex.org/W123",
                "title": "Verified primary title",
                "doi": "https://doi.org/10.1038/s41586-026-10410-0",
                "abstract_inverted_index": {
                    word: [i for i, w in enumerate(TEXT.split()) if w == word] for word in TEXT.split()
                },
                "locations": [{"landing_page_url": "https://www.nature.com/articles/s41586-026-10410-0"}],
            }

    record = {"url": "https://www.nature.com/articles/s41586-026-10410-0"}
    text, evidence = retrieve(BlockedPublisher(), record, tmp_path, prefer_full_text=True)
    assert text == TEXT
    assert evidence["kind"] == "abstract" and evidence["url"] == "https://openalex.org/W123"
    assert record["title"] == "Verified primary title"


def test_prior_catalogue_import_does_not_inherit_unverified_decisions(tmp_path):
    from research_factory.seeds import prior_catalogue_leads

    path = tmp_path / "old.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.org/p",
                    "title": "A misleading title",
                    "scope": "core",
                    "status": "accepted",
                    "decision": decision(plan()),
                    "summary": "An unverified summary",
                    "retrieval": {"sha256": "fake"},
                }
            ]
        )
    )
    rows, report = prior_catalogue_leads(path)
    assert rows[0]["prior_source"]
    assert not {"scope", "status", "decision", "summary", "retrieval"} & set(rows[0])
    assert report["candidates"] == 1


def test_rate_limited_host_does_not_consume_the_rest_of_the_run_budget(monkeypatch):
    from research_factory.runtime.net import Client, HTTPFailure

    class LimitedResponse:
        status_code = 429
        is_redirect = False
        ok = False
        headers = {}

        def close(self):
            pass

    class Session:
        headers = {}

        def request(self, *args, **kwargs):
            return LimitedResponse()

    monkeypatch.setattr("research_factory.runtime.net.public_url", lambda url: url)
    monkeypatch.setattr("research_factory.runtime.net.time.sleep", lambda seconds: None)
    client = Client(max_requests=20, session=Session())
    with pytest.raises(HTTPFailure, match="429"):
        client.get("https://limited.example/first")
    assert client.count == 3
    with pytest.raises(HTTPFailure, match="429"):
        client.get("https://limited.example/second")
    assert client.count == 3
    with pytest.raises(HTTPFailure, match="429"):
        client.get("https://another.example/first")
    assert client.count == 6


def test_bounded_quote_repair_preserves_the_relevance_verdict(tmp_path):
    from research_factory.bootstrap import batch_review

    original = decision(plan())
    original["evidence_quote"] = "This unsupported wording was paraphrased rather than copied from the paper"

    class RepairAgent:
        model = "fixture"
        calls = 0

        def call(self, prompt, schema, directory, name, search=False):
            self.calls += 1
            if name.endswith("quote-repair"):
                assert "decisions" not in schema["properties"]
                return {"quotes": [{"id": "work", "quote": " ".join(TEXT.split()[:12])}]}
            return {"decisions": [{"id": "work", "decision": original}]}

    agent = RepairAgent()
    result = batch_review(
        agent,
        plan(),
        [({"id": "work"}, TEXT, {"url": "https://example.org/p", "kind": "abstract"})],
        False,
        tmp_path,
        "read",
    )
    assert agent.calls == 2
    assert result["work"]["scope"] == original["scope"]
    assert result["work"]["confidence"] == original["confidence"]
    assert result["work"]["facets"] == original["facets"]
    assert result["work"]["quote_repaired"] and not result.errors


def test_pdf_download_falls_back_to_an_indexed_open_access_mirror(tmp_path, monkeypatch):
    from research_factory.runtime.downloads import download

    publisher = "https://publisher.example/p.pdf"
    mirror = "https://repository.example/p.pdf"
    monkeypatch.setattr(
        "research_factory.runtime.discovery.resolve_seed",
        lambda *a: {
            "id": "https://openalex.org/W123",
            "locations": [{"is_oa": True, "pdf_url": publisher}, {"is_oa": True, "pdf_url": mirror}],
        },
    )

    class BlockedPublisher(FixtureClient):
        def get(self, url, **kwargs):
            if url == publisher:
                raise RuntimeError("HTTP 403 from publisher.example")
            return super().get(url, **kwargs)

    record = {"id": "work", "url": "https://doi.org/10.1234/p", "pdf_url": publisher}
    result = download(BlockedPublisher(), record, tmp_path)
    assert result["status"] == "downloaded" and result["source_url"] == mirror
    assert Path(result["path"]).is_file()

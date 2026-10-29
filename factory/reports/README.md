# Verification Results

Live verification on 29 October 2026 produced two independent repositories from the supplied briefs. The bootstrap used an authenticated Codex CLI agent, actual web research, OpenAlex, citation expansion, primary-text retrieval, and separate relevance audits. These were staged, checkpointed development runs, not single uninterrupted bootstraps.

| Project | Accepted works | Downloaded PDFs | Regression cases |
| --- | ---: | ---: | ---: |
| [Persona alignment](persona/README.md) | 108 | 91 | 13/13 resolved correctly |
| [Conversational causality](causality/README.md) | 66 | 65 | 9/9 resolved correctly |

These are finite, assistant-labeled tests, not a human-audited gold standard. Final regression results consolidate resolved cases and one retry of unresolved cases: nine persona cases and eight causality cases were reused. Earlier runs had invalid quotations and uncertain decisions; the [persona history](persona/evaluation-history/) and [causality history](causality/evaluation-history/) retain them. No benchmark URLs or expected labels were supplied to discovery or inserted into the accepted catalogue by the evaluator.

Independent persona discovery recovered **54 of the 68** entries previously marked in scope. This does not establish exhaustive coverage. Keyless OpenAlex became rate-limited during supplemental backfill. The previous bibliography was then imported through the explicit migration option, with its labels and summaries discarded. Fresh reviews accepted 61 of those 68 entries and held seven as uncertain. Of the eight previously labeled role-playing entries, seven were excluded and one remained uncertain; none was accepted. See the [item-by-item migration audit](persona/prior-catalogue-audit.json).

The factory has **27 passing tests**, and the original pipeline's **23 tests** still pass. Ruff and the dependency-lock check pass. A wheel was installed into a fresh environment and used to generate a standalone repository. Both generated catalogues validate, and their READMEs pass Awesome content checks. Full GitHub metadata checks apply after publication; formatting does not establish upstream Awesome eligibility.

The [live daily smoke test](installed-daily-smoke.json) discovered candidates and downloaded a PDF. It correctly reported degraded service because no daily LLM credentials were provided. The small-model API contract, acceptance rules, budgets, retries and idempotence are fixture-tested; a real small-model provider was not tested. The larger code-agent reviews and both research briefs were tested live.

Local runnable outputs are `factory/runs/persona/` and `factory/runs/causality/`. A standalone causality copy is at `/home/me/awesome/awesome-causality-llm`. Those generated repositories contain their own Python runtime, configuration, dependency locks and daily GitHub Actions schedule. PDFs and source-text caches are local and excluded from Git; committed manifests record availability and checksums. Two known paper download locations remain inaccessible; most other entries without PDFs are web posts. NotebookLM uploads remain deferred.

See [machine-readable verification](verification.json), [factory usage](../README.md), and each project's compiled discovery configuration. These snapshots preserve current accepted records, not the much larger unreviewed candidate queues.

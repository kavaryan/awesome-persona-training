# Research Map Factory

An installable Python program that turns a Markdown research brief and seed works into an independent, evidence-reviewed research repository.

The bootstrap uses an authenticated Codex CLI agent to research the topic, resolve seed titles, discover vocabulary and sources, and compile a project-specific scope and taxonomy. Python then performs OpenAlex and citation expansion, retrieves primary text, and coordinates independent reviews. Generated daily jobs use deterministic collectors and a small LLM through a compatible Chat Completions endpoint. They do not run Codex or repeat the original research prompt.

## Install and create a repository

Requires Python 3.11+, Git, and an authenticated [Codex CLI](https://learn.chatgpt.com/docs/non-interactive-mode). The CLI is an external bootstrap prerequisite; it is not installed by this Python package. It uses your existing login. No bootstrap OpenAI API key is assumed.

```bash
python -m pip install ./factory
research-factory init causality.md --output ../awesome-causality-llm
```

Or install the built wheel in `factory/dist/`. The package contains all code and templates; it does not import the parent persona project or require its catalogue.

The two included input examples are [`examples/persona.md`](examples/persona.md) and [`examples/causality.md`](examples/causality.md). The latter preserves the supplied causality brief. A new brief may be plain Markdown: describe the research question, include/exclude boundaries, requested taxonomy facets, and seed titles or URLs. No project-specific Python code is needed.

```bash
research-factory init factory/examples/persona.md --output ./persona-map
research-factory init factory/examples/causality.md --output ./causality-map
```

When migrating an existing bibliography, add `--prior-catalogue old/data/catalogue.json`. This imports URLs and bibliographic identifiers only: old relevance labels, summaries and tags are discarded, and primary-text review is required. An independent-discovery snapshot is saved before import, so recovery metrics do not mistake inherited URLs for successful search. This is useful for preserving a previous persona map without trusting its unaudited labels.

Use a new or empty output directory. `--resume` continues a factory workspace with the same brief. It will not overwrite an unrelated repository or silently change the brief behind existing decisions.

## Operational stages

1. **Research and compile.** The code agent resolves seeds, searches multiple formulations and neighboring literatures, examines citations, and records primary URLs, query history, vocabulary, inclusion/exclusion rules, sources and proposed taxonomy. A deadline stops prolonged research. A recovery pass can compile a timed-out search trace into leads; these still require primary-text review.
2. **Audit the taxonomy.** A separate bounded pass maps explicitly requested facets to 2–6 operational dimensions. It must cover measures as well as intervention levels when requested. Missing methods remain `not-reported`; the classifier must explain what variables or distributions a reported measure compares.
3. **Compile and verify sources.** Normalize query syntax and URL patterns, probe feed/index endpoints, and discover advertised RSS links. Preserve every explicit seed URL and supplied repository list. Keep the initial publication cutoff separate from permanent inclusion rules.
4. **Expand discovery.** Run three bounded rotations of concrete OpenAlex queries, API web queries when configured, feeds/indexes, repository links and citations in both directions. These discover candidates; keywords never decide inclusion. Unreviewed graph nodes can supply leads, without becoming accepted sources. Sweep seed citations and primary-page references, including unindexed research posts. Two bounded follow-up agent passes search missing conceptual families and compiles additional queries; it never sees benchmark answers or the previous catalogue.
5. **Read and review.** Fetch abstracts or full text; prefer arXiv HTML or directly available PDFs. If a DOI publisher blocks access, try its indexed abstract. A code-agent review receives actual source text and project criteria. A separate scope audit receives the same evidence without the first judgment. Its compact response contains the scope, confidence, rationale and evidence quote; the first pass supplies the detailed taxonomy. Both must favor inclusion with confidence at least 0.90. Confidence concerns scope relevance, not study quality or completeness of reported methods. It is a heuristic, not a calibrated probability.
6. **Validate and save.** Check JSON, taxonomy values, and a literal 8–24-word supporting quote. The bootstrap permits one bounded repair of an invalid supporting quote, keeping the relevance verdict and tags frozen; an unsupported quote still fails. Preserve disagreements, missing text and errors. Keep a narrow core separate from supporting methods. Checkpoint after each batch.
7. **Generate the repository.** Copy the portable Python runtime, pinned dependency file, daily/validation Actions, project configuration, reading-list README, generated Markdown/CSV/BibTeX, download manifest and audit reports. Initialize a local Git repository on `main`. No remote repository or pull request is created automatically.

The agent model defaults to the locally configured Codex model; `--model` selects an explicit model. Factory calls use medium reasoning effort to keep structured phases bounded. Default limits are 600 seconds per agent call and 3,600 seconds total agent wall-clock budget per invocation, 80 review candidates, batches of six, and 30 PDF attempts. The deadline also elapses during intervening collection and retrieval; separate network budgets apply. Partial work can be resumed. The broad initial research and the small daily updater have separate budgets.

```bash
# Continue without repeating completed planning and decisions:
research-factory init causality.md --output ../awesome-causality-llm --resume

# Inspect configuration and candidates before reviewing:
research-factory init causality.md --output ./new-map --stage discover
research-factory init causality.md --output ./new-map --resume --stage review

# Reuse an inspected, recorded plan (still runs evidence review):
research-factory init causality.md --output ./replay-map --plan path/to/plan.json
```

`--until YYYY-MM-DD` filters known publication dates. It is not a historical snapshot of later-revised paper versions; records with missing dates remain explicitly unverified. `--review-limit`, `--batch-size`, `--discovery-rounds`, `--expansion-rounds`, `--download-limit`, `--agent-timeout` and `--agent-budget` control bootstrap costs. A single bounded run does not promise exhaustive coverage or an empty queue.

## Generated daily operation

From the generated directory:

```bash
python -m pip install --require-hashes -r requirements.txt
python -m research_map.cli run
python -m research_map.cli validate
python -m research_map.cli render
```

The generated schedule is **06:17 UTC daily**, with a manual backfill dispatch. The validation workflow also runs `awesome-lint` under Node 22 using a committed npm lockfile. Upload the generated repository to GitHub and make `main` its default branch to use it. The workflow commits metadata and generated indexes directly to `main`; no PR is opened. Branch protection or organization restrictions may require adjusting that policy. Before publishing, make an initial commit, set a repository description and the `awesome` / `awesome-list` topics, and push `main` with upstream tracking. Full Awesome lint checks include GitHub metadata; an unpublished local repository can only pass the content checks.

| Setting | Actions configuration |
| --- | --- |
| `OPENALEX_API_KEY` | Secret; keyless requests are attempted when absent. |
| `BRAVE_API_KEY` or `SERPER_API_KEY` | Secret; traditional API web search. |
| `LLM_API_KEY` | Secret; small daily relevance classifier. |
| `LLM_BASE_URL` | Variable; HTTPS base URL before `/chat/completions`. |
| `LLM_MODEL` | Variable; provider model identifier. |

Daily limits reserve separate budgets for discovery and evidence processing: 90 requests/300 seconds for discovery, then 150 requests/600 seconds for evidence, model calls and downloads. Up to 24 candidates, 48 model calls and 12 PDF attempts per run. This prevents discovery from using the entire request allowance before reading any source. OpenAlex runs both broad full-text and title/abstract searches, with independent cursors. These are discovery channels, not inclusion decisions ([search API](https://help.openalex.org/api/searching/)). Queries rotate, historical cursors persist, recent searches overlap 21 days, and half the review slots favor new arrivals while half advance the historical queue. Unfinished work remains queued. Missing credentials are reported as degraded service, without title-only fallback decisions. A host that continues returning HTTP 429 is skipped for the rest of that client budget.

PDFs and normalized text are cached and excluded from Git. The NotebookLM manifest records source URLs, paths, retrieval status and SHA-256 checksums. NotebookLM uploads remain deferred.

## Evaluate discovery and classification separately

```bash
research-factory evaluate --repo ./persona-map \
  --benchmark factory/benchmarks/persona.json \
  --reference data/catalogue.json
research-factory evaluate --repo ./causality-map \
  --benchmark factory/benchmarks/causality.json
```

The evaluator fetches primary text, hides expected labels from the agent, and runs the same two-pass acceptance rule. Benchmark URLs are never injected into the discovery queue or catalogue. It records whether each work was discovered **before** evaluation. An optional old catalogue measures recovery separately; its labels are not treated as audited ground truth. `--fail-on-regression` returns a nonzero status for false positives, missed positives or unresolved cases. `--retry-unresolved` retries only unreadable, invalid or uncertain cases from the same benchmark; every evaluation is retained in `reports/evaluation-history/`, and reused decisions are counted explicitly. Retry selection never uses expected labels.

The included small benchmarks target misleading keywords, relevant titles without obvious topic terms, and the distinction between conversation-level and model-internal interventions. Their labels were assigned by an assistant reading primary abstracts/text and remain open to human correction. They are regression cases, not proof of zero false positives or exhaustive discovery. See [`reports/`](reports/) for the actual verification results and limitations.

## Development

```bash
uv sync --project factory --extra dev
uv run --project factory pytest factory/tests -q
uv run --project factory ruff check factory/src factory/tests
uv run --project factory python -m build --wheel factory
```

Code is MIT-licensed, adapted in part from this repository's original daily pipeline. Generated bibliography content uses CC0. Generated lists follow Awesome presentation conventions but do not claim upstream eligibility: AI-assisted generation and the upstream human-curation requirements must be considered before any submission.

# Daily discovery specification

The schedule is **06:17 UTC daily** (`17 6 * * *`), with a manual dispatch option for bounded backfills. GitHub may delay scheduled runs. All progress is committed to `main`; no discovery or upstream pull request is opened. The workflow has a 25-minute ceiling, and the Python collector has a 15-minute budget and 140-request ceiling, including retries and downloads.

## Concrete stages

1. Rotate through 12 of the versioned OpenAlex queries in [config/discovery.json](../config/discovery.json). Retrieve at most two 50-result pages per query. Recent searches overlap 21 days; every third query searches all publication dates and resumes its saved page. The historical scan catches older literature and delayed indexing. `--backfill` makes all selected queries historical.
2. Run eight rotating traditional web searches through Brave Search or Google via Serper. Queries combine topic phrases with dedicated source domains. Search results contribute URLs and discovery provenance only: their snippets are never used as relevance evidence.
3. Read up to 20 entries from each configured research feed and direct publisher index (Anthropic and UK AISI). Refresh the three supplied research-list repositories weekly. Every returned item is a candidate, not an inclusion decision. A failed or invalid feed is recorded; source-specific web queries provide a complementary discovery route.
4. Rotate through four accepted core/mechanism seed papers. Resolve DOI/OpenAlex identifiers, read referenced works, and query works that cite each seed. Advance backward-reference offsets and forward-citation pages across runs. When indexed references are absent, inspect the arXiv HTML bibliography. Missing HTML does not prevent forward citation discovery. This is one hop per seed per run; newly accepted work becomes eligible as a seed.
5. Normalize arXiv versions, DOI URLs, tracking parameters, and LessWrong/Alignment Forum crossposts. Merge verified aliases and discovery routes. Preserve earlier decisions. Similar titles alone are never sufficient to merge distinct papers.
6. Select at most 24 pending candidates, prioritizing never-attempted items before retries. Retrieve an OpenAlex abstract, publisher/arXiv abstract, or article body; if necessary, extract text from a directly available PDF. A usable source needs at least 40 words. A missing abstract/body leaves the item pending for retrieval; it is never rejected based on its title.
7. Make one bounded LLM call per candidate: at most 14,000 source characters, 650 output tokens, no tools, JSON output, a versioned rubric, and a closed taxonomy. For longer documents, supply beginning, middle, and end excerpts. Validate the schema and require a supporting quotation of at most 24 words that occurs in the actual supplied text. Record the source and input hashes. Invalid output is retained as an error, not accepted.
8. Accept high-confidence core/mechanism/background decisions into the generated catalogue. Keep role-play/exclusion decisions in the queue for audit; retain uncertain items for re-review after 30 days. Retrieval or service errors retry after two days. The README is never automatically rewritten.
9. Download up to 12 accepted open-access PDFs per run. Validate the PDF signature and parser, bound each download to 40 MB, write atomically, and retain checksums and source URLs. Persistent Actions caches avoid downloading the same file every day. Failed downloads remain visible in the manifest. Papers with no accessible PDF remain in the catalogue.
10. Write the NotebookLM manifest; optionally upload at most ten files to an explicitly configured Enterprise notebook. Reconcile remote source names before uploading, validate local checksums, and persist successful source IDs immediately. Do not retry an upload blindly.
11. Validate catalogue invariants, regenerate Markdown/CSV/BibTeX, and commit only metadata, reports, and generated indexes. Preserve a 90-day audit artifact. PDFs are not committed or attached to public releases. Runtime failures and missing integrations appear in the run summary and `reports/latest-run.json` as `degraded`.

Budgets are limits, not promises that all queues drain daily. Inspect the pending count and failed/truncated queries. Broad backfills may create a substantial backlog. Increase the judge budget or narrow discovery queries deliberately if incoming candidates persistently exceed processing capacity. Do not delete unread candidates because their titles look irrelevant. Publication indexes, feed retention, search rankings, and source access all impose coverage limits.

## Configuration

| Setting | GitHub location | Purpose |
| --- | --- | --- |
| `OPENALEX_API_KEY` | Secret | Authenticated OpenAlex quota; keyless queries are attempted when absent. |
| `BRAVE_API_KEY` or `SERPER_API_KEY` | Secret | Traditional web discovery. Brave is preferred when both are set. |
| `LLM_API_KEY` | Secret | Small relevance judge with an OpenAI-compatible Chat Completions interface. |
| `LLM_BASE_URL` | Variable | HTTPS provider base URL, excluding `/chat/completions`. |
| `LLM_MODEL` | Variable | Provider-specific model identifier. |
| NotebookLM settings | See [NotebookLM setup](notebooklm.md) | Optional daily source uploads. |

The provided `gh.token` is used only for authorized repository administration during setup. It is ignored by Git and is not an LLM credential. The scheduled workflow uses GitHub's own `GITHUB_TOKEN` for commits. GitHub Models was [retired on 30 July 2026](https://docs.github.com/en/github-models), so it cannot provide the classifier. If no judge is configured, discovery and downloads continue, but no candidates are automatically accepted.

To configure credentials, use the repository's **Settings → Secrets and variables → Actions**. No workflow sends email, Slack messages, or issues. Credentials are passed only to their intended service, not included in article prompts or reports. The classifier cannot execute code or modify configuration. Public HTTPS requests reject private IP destinations; do not treat this as a general-purpose hardened web sandbox.

## Local commands

```bash
uv sync --extra dev
uv run persona-map validate
uv run persona-map render
uv run pytest -q
uv run persona-map run --until 2026-10-28 --backfill
uv run persona-map run --download-only
uv run persona-map run --sync-notebook
npm ci
npm run lint:awesome
```

Export the relevant environment variables before running. `.env.example` documents names; the application deliberately does not execute or automatically load `.env` files. `uv.lock`, `requirements.txt`, `package-lock.json`, and pinned Action revisions make installed versions reviewable. `data/discovery-state.json` stores resumable search/citation progress; `data/candidates.json` stores the decision ledger; `data/catalogue.json` is the accepted source of truth.

A scheduled run that completes with missing services is a successful execution in degraded mode, not proof of full discovery/classification coverage. Read the report, not only the green Actions badge. Tests exercise mocked APIs and failure cases; live integration tests require actual credentials and are reported separately.

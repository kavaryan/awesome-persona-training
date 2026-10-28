# Setup verification

Verified on 28 October 2026.

| Check | Result |
| --- | --- |
| Local regression suite | 19 tests passed, covering evidence grounding, invalid model responses, deduplication and late aliases, citation direction/pagination, PDF integrity/cache repair, request budgets, missing-service behavior, and NotebookLM reconciliation. |
| Python lint | Passed. |
| Catalogue validation and reproducible exports | Passed. |
| Awesome lint | Passed with Node 22 after repository metadata and branch tracking were configured. |
| GitHub validation workflow | [Passed](https://github.com/kavaryan/awesome-persona-training/actions/runs/40724307373). |
| GitHub daily discovery workflow | [Passed](https://github.com/kavaryan/awesome-persona-training/actions/runs/40724435523), including metadata commit, cache, and audit artifact. |
| OpenAlex search and citations | Tested live; initial API rate-limit error was handled and subsequent runs succeeded. |
| Research feeds and publisher indexes | Tested live; invalid guessed feeds were replaced with advertised RSS or direct index parsing. |
| Initial local downloads | 58 PDFs validated by signature, PDF parsing, and SHA-256. |
| LLM classifier | Structured-response and failure handling tested with fixtures. No live provider credential configured during setup. |
| Scheduled traditional web search | Brave/Serper adapters implemented; response handling tested. Credentials not configured during setup. Interactive web discovery was performed for the initial research pass. |
| NotebookLM | Manifest produced; official Enterprise upload, checksum, and remote-deduplication behavior tested with fixtures. No live notebook/account configured. |

A green daily Actions run means the bounded program executed and saved its results. It does not override the `degraded` service status in the [latest report](../reports/latest-run.json). During setup, the absence of LLM and web-search credentials was recorded explicitly; no title-only fallback decisions were made. The [automation setup](automation.md#configuration) lists the required secrets and variables.

The [active workflow](../.github/workflows/discover.yml) schedules runs at 06:17 UTC each day and supports manual dispatch. No pull request was created, either here or upstream.

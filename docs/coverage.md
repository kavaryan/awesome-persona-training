# Coverage audit: 28 October 2026

The initial catalogue contains **76 reviewed works/resources**: 20 core entries, 31 mechanism/control studies, 17 foundations/measurement entries, and 8 explicit role-playing/personalization boundary examples. **58 open-access PDFs** were downloaded and parsed locally. The remaining included alignment entries are primarily posts or resources without their own PDF. The catalogue distinguishes papers, working reports, posts, conceptual work, and specifications.

This is a broad research map, **not a certified exhaustive systematic review**. Unread search results remain in the candidate queue. The queue intentionally includes irrelevant-looking results because titles and keyword matches are not grounds for a relevance decision. The latest operational counts and errors are in [reports/latest-run.json](../reports/latest-run.json); the initial scholarly search audit is in [reports/bootstrap-discovery.json](../reports/bootstrap-discovery.json).

## Discovery performed

- Verified the six supplied paper/report seeds and the reward-hacking post using their abstracts or full text. Linked the warmth paper's 2025 preprint and 2026 Nature version as one work, without combining their numerical findings.
- Read the three supplied repository lists and followed primary-source links. Distinguished OpenCharacter from Open Character Training and retained representative role-playing examples separately.
- Used traditional web search with combinations of character/persona training, alignment, constitutions, reward hacking, warmth, sycophancy, persona selection, assistant identity, and source-specific domains. [The query audit](../reports/initial-web-search.json) records the initial web-search families.
- Queried OpenAlex using six broad query combinations and eight focused combinations. Several result sets exceeded the first 50-result page; the audit explicitly records that truncation. The daily workflow has persistent backfill pagination rather than claiming these sets were fully reviewed.
- Queried forward and backward citation metadata for six seeds. OpenAlex returned no indexed reference list for these seed versions, so references were also extracted directly from the Open Character Training and Synthetic Persona Pretraining full texts and the Persona Selection Model post. Forward citation lookups returned additional candidates. The reusable pipeline includes an arXiv HTML bibliography fallback.
- Retrieved 191 primary-source texts during the first expansion, then fetched the 13 additional scholarly sources and the Teaching Claude Why post used in the final additions. Inclusion decisions were made by reading actual abstracts/body passages, not titles. Evidence hashes, short excerpts, rationales, and review attribution are stored per record.

The broader initial search led to recent additions beyond the supplied seeds, including Risk-Averse Agents, Split Personality Training, ethical-persona projectability, value-training side effects, alignment-generalization prediction, and tests of belief internalization under Open Character Training.

## Source watchlist

| Publisher/community | Daily discovery route |
| --- | --- |
| LessWrong and Alignment Forum | Feeds, site-restricted search, crosspost deduplication. |
| Anthropic Alignment Science | Direct research index and site-restricted search; no working RSS feed was advertised. |
| Anthropic Research | Direct research index and site-restricted search. |
| UK AI Security Institute | Blog index and site-restricted search. |
| Alignment Research Center | Advertised blog RSS and site-restricted search. |
| OpenAI and Google DeepMind | Feeds and site-restricted search. |
| SPAR Research Library | Site-restricted search and seed-report links. |
| METR, Apollo Research, FAR.AI | Site-restricted search. |
| Model Raising | Site-restricted search and persona-pretraining seed links. |
| arXiv, ACL Anthology, scholarly publishers | OpenAlex, citations, web search, and supplied repository lists. |

These routes are complementary, not guarantees of complete ingestion. Feeds can omit older items, indexes can change markup, recent papers can lack citation metadata, and paywalls can prevent full-text retrieval. An accessible abstract is sufficient for scope triage, but may not support a detailed methodological judgment. Missing evidence stays pending. Initial editorial review was performed by an AI assistant, not an undisclosed human reviewer.

## Operating status

The GitHub schedule, live OpenAlex discovery, publisher retrieval, PDF downloading, catalogue generation, and local regression tests were exercised during setup. Web discovery in scheduled runs requires a Brave or Serper key; the initial interactive search did not furnish reusable credentials. Automated relevance decisions use the documented environment variable names for a small-model endpoint and key. Both web providers and the complete classification path are tested locally with simulated API responses. Missing services are explicitly reported and do not trigger keyword-only fallback classification. NotebookLM uploads are deferred at the owner's request; the intended future destination is a personal account. PDF downloads and manifest generation continue.

The NotebookLM upload adapter is covered by mocked checksum, upload, and remote-reconciliation tests. No claim of a live NotebookLM upload is made until an account and destination are configured. Both initial cloud workflows passed; see the [verification record](verification.md) for run links and the distinction between tested code and configured services.

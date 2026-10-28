# Contributing

Please read the [scope and taxonomy](docs/taxonomy.md) before proposing an entry.

1. Read the paper's abstract or full text, or the body of a research post. Search snippets and titles are leads, not evidence.
2. Check `data/catalogue.json` and `data/candidates.json` for an existing DOI, arXiv ID, OpenAlex ID, or crossposted URL.
3. Add or amend a catalogue record with verified metadata, a short original description, scope rationale, intervention/theme tags, publication type, and evidence provenance. Keep any supporting quotation to at most 24 words.
4. Explain what the work contributes to persistent assistant character or its safety consequences. Label role-playing, prompting, and user personalization accurately.
5. Link preprint and published versions in one record when verified. Do not infer equivalence solely from similar titles.
6. Run `python -m persona_map.cli validate`, `python -m persona_map.cli render`, and `pytest`. For README changes, run `npm ci` and `npm run lint:awesome`.
7. Propose a README addition only if it provides a useful, distinct entry point. The research catalogue can be more comprehensive than the curated list.

Do not commit API keys, authentication cookies, downloaded PDFs, the PAC reference project, or scraped full texts. Downloads remain subject to the source's terms; the bibliography's license does not relicense third-party works. Report metadata errors, misclassifications, duplicate versions, and broken links with the source evidence needed to fix them.

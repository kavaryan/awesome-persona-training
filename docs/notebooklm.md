# Downloads and NotebookLM

**Uploads are deferred.** The owner selected a personal NotebookLM account as the intended future destination and asked to skip integration for now. The daily workflow downloads PDFs and generates the manifest, without invoking an uploader or requiring Google credentials. Personal-account authentication and daily imports have not been implemented or enabled.

The pipeline downloads accepted open-access PDFs into `downloads/` and writes [data/notebooklm-manifest.json](../data/notebooklm-manifest.json). Each downloaded entry has a stable work ID, title, source URL, file path, SHA-256, scope, and available license information. A record's download status describes the last successful retrieval; on a fresh checkout the local file must be fetched or restored from cache before import. Git intentionally excludes PDFs and full-text caches.

Run `uv run persona-map run --download-only` to fetch the next bounded batch. Repeat to populate a fresh machine, or raise `limits.downloads` temporarily for a one-time backfill. Failed and unavailable PDFs remain explicit. The initial collection includes local PDF files already downloaded and verified. Research posts without PDFs remain linked sources in the bibliography; the uploader does not pretend that a PDF cited by a blog post is the blog post itself.

## Optional Enterprise adapter (inactive)

Google documents file upload and source management for [NotebookLM Enterprise](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks-sources). This repository implements that API, including remote reconciliation via the [get-notebook endpoint](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks). The API is a preview and may change. This is not a personal-account browser automation integration.

The existing Enterprise adapter is retained as optional code; it does not implement the selected personal-account integration. It is absent from the scheduled workflow. To use it deliberately with an Enterprise account, export these environment variables and invoke `uv run persona-map run --sync-notebook`:

- `NOTEBOOKLM_NOTEBOOK`: `projects/PROJECT_NUMBER/locations/LOCATION/notebooks/NOTEBOOK_ID` for an existing notebook accessible to the authenticated user.
- `NOTEBOOKLM_REGION`: `global`, `eu`, or `us`, matching the API endpoint for that notebook.

Supply a current `GOOGLE_ACCESS_TOKEN`, or `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, and `GOOGLE_OAUTH_REFRESH_TOKEN` for an authorized Google Cloud OAuth user with the necessary NotebookLM access. When explicitly invoked, the adapter exchanges that grant for a short-lived access token. The adapter does not create a Google Cloud project, enroll a paid Enterprise account, obtain user consent, or guess a notebook destination.

The uploader gets the existing notebook's sources before each run. Files use a stable name containing the work ID and a checksum prefix; if that name exists remotely, the upload is skipped even when local state was lost after a successful upload. Successful returned source IDs are stored in `data/notebooklm-state.json`. An ambiguous upload failure is retried only after a later remote reconciliation. Concurrent daily runs are serialized by GitHub Actions.

Imports are additive. No existing notebook source is deleted. If a file is intentionally refreshed and its checksum changes, it is a new source version; older versions are retained for the owner to manage. The pipeline does not continuously redownload already cached PDFs to track revisions. It discovers new works daily; refresh a known work deliberately by clearing its download metadata/file. Source limits and permissions are reported as API failures rather than silently splitting the collection into new notebooks.

The Enterprise adapter is covered by mocked upload/reconciliation tests; no live notebook upload has been performed. For personal NotebookLM, the downloaded PDFs can be imported manually while programmatic integration is deferred. No session cookies have been collected or stored.

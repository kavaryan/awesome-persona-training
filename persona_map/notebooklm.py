"""Optional official Enterprise upload adapter with remote reconciliation.

No personal-account cookie scraping. Notebook destination and access token are explicit.
"""

import hashlib
import os
import re
from pathlib import Path

from .store import read_json, write_json


def destination():
    resource = os.getenv("NOTEBOOKLM_NOTEBOOK", "")
    region = os.getenv("NOTEBOOKLM_REGION", "global")
    if not re.fullmatch(r"projects/[\w-]+/locations/[\w-]+/notebooks/[\w-]+", resource):
        raise ValueError("NOTEBOOKLM_NOTEBOOK must be projects/PROJECT/locations/LOCATION/notebooks/ID")
    if region not in {"global", "us", "eu"}:
        raise ValueError("Invalid NOTEBOOKLM_REGION")
    return f"https://{region}-discoveryengine.googleapis.com", resource


def sync(client, manifest, state_path, limit=10):
    if not os.getenv("NOTEBOOKLM_NOTEBOOK"):
        return {"status": "not-configured", "uploaded": 0}
    host, resource = destination()
    token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not token and all(
        os.getenv(k)
        for k in ["GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN"]
    ):
        response = client.request(
            "POST",
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": os.environ["GOOGLE_OAUTH_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
                "refresh_token": os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"],
                "grant_type": "refresh_token",
            },
            retries=0,
        )
        token = response.json().get("access_token")
    if not token:
        raise ValueError("NotebookLM needs GOOGLE_ACCESS_TOKEN or an authorized OAuth refresh grant")
    headers = {"Authorization": "Bearer " + token}
    # The get-notebook response contains sources. Reconcile every run so a crash
    # after upload but before the state commit does not duplicate a source.
    notebook = client.json(f"{host}/v1alpha/{resource}", headers=headers)
    remote = {s.get("title", ""): s for s in notebook.get("sources", [])}
    state = read_json(state_path, {})
    uploaded = 0
    for item in manifest:
        if item["status"] != "downloaded" or uploaded >= limit:
            continue
        key = resource + ":" + item["id"] + ":" + item["sha256"]
        marker = f"persona-{item['id']}-{item['sha256'][:16]}.pdf"
        if marker in remote:
            state[key] = {"source": remote[marker], "filename": marker}
            continue
        # Local success alone is not enough: remote reconciliation permits repairing deletions.
        path = Path(item["path"]).resolve()
        if not path.is_relative_to(Path("downloads").resolve()) or not path.exists():
            continue
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != item["sha256"]:
            raise ValueError("Import file checksum mismatch")
        response = client.request(
            "POST",
            f"{host}/upload/v1alpha/{resource}/sources:uploadFile",
            headers={
                **headers,
                "X-Goog-Upload-File-Name": marker,
                "X-Goog-Upload-Protocol": "raw",
                "Content-Type": "application/pdf",
            },
            data=content,
            retries=0,
        )
        source = response.json()
        if not source.get("sourceId", {}).get("id"):
            raise ValueError("Upload response has no source identifier")
        state[key] = {"source": source, "filename": marker}
        write_json(state_path, state)
        uploaded += 1
    write_json(state_path, state)
    return {"status": "ok", "uploaded": uploaded}

"""Preserve explicit input URLs and explore seed citations without title decisions."""

import copy
import re
from urllib.parse import urlsplit

from .runtime.discovery import citations
from .runtime.net import Client
from .runtime.store import canonical_url, identities


def include_input_urls(plan, brief):
    result = copy.deepcopy(plan)
    known = set().union(*(identities(w) for w in result["works"])) if result["works"] else set()
    for raw in re.findall(r"https://[^\s<>\])]+", brief):
        url = canonical_url(raw.rstrip(".,;"))
        parsed = urlsplit(url)
        if parsed.hostname == "github.com" and len(parsed.path.strip("/").split("/")) >= 2:
            repo = "https://github.com/" + "/".join(parsed.path.strip("/").split("/")[:2])
            if repo not in result["repositories"]:
                result["repositories"].append(repo)
        elif url not in known:
            result["works"].append(
                {
                    "title": "Input source awaiting primary metadata",
                    "url": url,
                    "seed": True,
                    "found_via": "explicit URL in input brief",
                }
            )
            known.add(url)
    return result


def seed_citation_sweep(seeds, state, pages=4, client=None):
    client = client or Client(max_requests=90, seconds=240)
    rows, events = [], []
    for seed in seeds:
        if not seed.get("seed"):
            continue
        for _ in range(pages):
            try:
                found, progress = citations(
                    client, seed, state.setdefault("citations", {}).get(seed["id"], {}), 50
                )
                rows.extend(found)
                state["citations"][seed["id"]] = progress
                events.append(
                    {
                        "channel": "seed-citation-sweep",
                        "seed": seed["url"],
                        "candidates": len(found),
                        **progress,
                    }
                )
                if progress.get("reference_offset", 0) == 0 and progress.get("citing_page", 1) == 1:
                    break
            except Exception as error:
                events.append(
                    {
                        "channel": "seed-citation-sweep",
                        "seed": seed["url"],
                        "status": "error",
                        "error": str(error)[:180],
                    }
                )
                break
    return rows, {"events": events, "requests": client.count}


def prior_catalogue_leads(path):
    """Import identifiers from a prior bibliography; never inherit its relevance labels."""
    import hashlib
    from pathlib import Path

    from .runtime.store import read_json

    path = Path(path)
    source = read_json(path)
    if not isinstance(source, list):
        raise ValueError("Prior catalogue must be a JSON array of works")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    rows = []
    for item in source:
        if not isinstance(item, dict) or not str(item.get("url", "")).startswith("https://"):
            raise ValueError("Each prior-catalogue work requires an HTTPS URL")
        row = {k: item[k] for k in ["url", "title", "doi", "arxiv", "openalex", "aliases"] if item.get(k)}
        row.update(prior_source=True, provenance=["prior-catalogue:" + digest])
        rows.append(row)
    return rows, {
        "sha256": digest,
        "candidates": len(rows),
        "policy": "Identifiers only; all prior relevance labels, summaries, tags and evidence decisions discarded.",
    }

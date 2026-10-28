import argparse
import os
from datetime import date, timedelta
from pathlib import Path

from .discovery import collect
from .downloads import download, make_manifest
from .evidence import retrieve
from .judge import judge
from .net import BudgetExceeded, Client
from .notebooklm import sync
from .render import render, validate_catalogue
from .store import identities, merge_candidates, read_json, today, write_json


def run(args):
    config = read_json("config/discovery.json")
    taxonomy = read_json("config/taxonomy.json")
    limits = config["limits"]
    client = Client(max_requests=limits["requests"], seconds=limits["seconds"])
    catalogue = read_json("data/catalogue.json", [])
    candidates = read_json("data/candidates.json", [])
    state = read_json("data/discovery-state.json", {})
    report = {
        "date": args.until,
        "events": [],
        "judged": 0,
        "accepted": 0,
        "downloaded": 0,
        "judge_errors": [],
    }
    if not args.download_only:
        rows, events = collect(client, config, state, catalogue, args.until, historical=args.backfill)
        report["events"] = events
        candidates = merge_candidates(candidates, rows, catalogue)
        configured = all(os.getenv(k) for k in ["LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"])
        report["judge"] = "configured" if configured else "not-configured"
        # Round-robin fairness: failed records move behind never-attempted work.
        eligible = [
            r
            for r in candidates
            if r["status"] in {"pending", "uncertain", "needs-text"}
            and (not r.get("retry_after") or r["retry_after"] <= args.until)
        ]
        eligible.sort(key=lambda r: (r.get("last_attempt", ""), r.get("first_seen", ""), r["id"]))
        if configured:
            for r in eligible[: limits["judge_items"]]:
                if any(identities(r) & identities(known) for known in catalogue):
                    r["status"] = "accepted"
                    continue
                r["last_attempt"] = args.until
                try:
                    text, evidence = retrieve(client, r)
                    decision = judge(client, r, text, evidence, taxonomy)
                    r["decision"] = decision
                    report["judged"] += 1
                    if decision["scope"] == "uncertain" or decision["confidence"] < 0.9:
                        r["status"] = "uncertain"
                        r["retry_after"] = (date.fromisoformat(args.until) + timedelta(days=30)).isoformat()
                    elif decision["scope"] in {"exclude", "roleplay"}:
                        r["status"] = "excluded" if decision["scope"] == "exclude" else "roleplay"
                    else:
                        # Discovery metadata is not allowed to manufacture a publication date or authors.
                        if r.get("date") and r["date"][:10] > args.until:
                            r["status"] = "pending"
                            continue
                        accepted = {
                            k: v
                            for k, v in r.items()
                            if k not in {"decision", "abstract", "last_attempt", "retry_after", "status"}
                        }
                        accepted.update(decision)
                        accepted["evidence_type"] = (
                            "preprint"
                            if "arxiv" in r["url"]
                            else (
                                "unverified-publication"
                                if r.get("openalex") or r.get("doi")
                                else "research-post"
                            )
                        )
                        accepted["status"] = "accepted"
                        catalogue.append(accepted)
                        r["status"] = "accepted"
                        report["accepted"] += 1
                except BudgetExceeded:
                    report["budget_exhausted"] = True
                    break
                except Exception as e:
                    r["error"] = str(e)[:220]
                    report["judge_errors"].append({"id": r["id"], "error": r["error"]})
                    r["status"] = "needs-text" if "text" in str(e).lower() else "pending"
                    r["retry_after"] = (date.fromisoformat(args.until) + timedelta(days=2)).isoformat()
    attempts = 0
    for r in sorted(catalogue, key=lambda r: (r.get("download", {}).get("checked", ""), r["id"])):
        if r["scope"] not in {"core", "mechanism", "background"} or attempts >= limits["downloads"]:
            continue
        existing = r.get("download", {})
        if existing.get("status") == "downloaded" and Path(existing["path"]).exists():
            continue
        attempts += 1
        r["download"] = download(client, r, "downloads", limits["download_mb"])
        if r["download"]["status"] == "downloaded":
            report["downloaded"] += 1
    validate_catalogue(catalogue, taxonomy)
    catalogue.sort(key=lambda r: r["id"])
    write_json("data/catalogue.json", catalogue)
    write_json("data/candidates.json", candidates)
    write_json("data/discovery-state.json", state)
    manifest = make_manifest(catalogue, "data/notebooklm-manifest.json")
    if args.sync_notebook:
        try:
            report["notebooklm"] = sync(client, manifest, "data/notebooklm-state.json", limits["uploads"])
        except Exception as e:
            report["notebooklm"] = {"status": "error", "error": str(e)[:220]}
    render(catalogue)
    report["requests"] = client.count
    report["pending"] = sum(r["status"] in {"pending", "uncertain", "needs-text"} for r in candidates)
    failures = [e for e in report["events"] if e["status"] == "error"]
    report["status"] = (
        "degraded"
        if failures
        or report["judge_errors"]
        or report.get("budget_exhausted")
        or report.get("judge") == "not-configured"
        or report.get("notebooklm", {}).get("status") == "error"
        else "ok"
    )
    write_json("reports/latest-run.json", report)
    # GitHub summaries disclose degraded runs instead of quietly claiming full coverage.
    summary = f"Discovery: {report['status']}; {len(report['events'])} source requests, {len(failures)} errors; {report['judged']} judged, {report['accepted']} accepted; {report['downloaded']} PDFs downloaded; {report['pending']} pending.\n"
    print(summary)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(summary)
            if report.get("judge") == "not-configured":
                f.write(
                    "\nRelevance judging needs LLM_API_KEY, LLM_BASE_URL and LLM_MODEL. Candidates are retained without title-only decisions.\n"
                )
            f.writelines(f"\n- {event['channel']}: {event.get('error')}\n" for event in failures)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    daily = sub.add_parser("run")
    daily.add_argument("--until", default=today())
    daily.add_argument("--backfill", action="store_true")
    daily.add_argument("--download-only", action="store_true")
    daily.add_argument("--sync-notebook", action="store_true")
    sub.add_parser("validate")
    sub.add_parser("render")
    args = p.parse_args()
    if args.command == "run":
        date.fromisoformat(args.until)
        run(args)
    elif args.command == "validate":
        validate_catalogue(read_json("data/catalogue.json", []), read_json("config/taxonomy.json"))
        print("Catalogue valid")
    else:
        render(read_json("data/catalogue.json", []))


if __name__ == "__main__":
    main()

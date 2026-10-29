"""Daily bounded discovery: python -m research_map.cli run."""

import argparse
import hashlib
import os
from datetime import date, timedelta
from pathlib import Path

from .discovery import collect
from .downloads import download, make_manifest, pdf_sources
from .evidence import retrieve
from .judge import classify
from .net import BudgetExceeded, Client
from .pipeline import apply_decision, needs_audit, review_schedule
from .render import render, validate_catalogue
from .store import merge_candidates, read_json, today, write_json


def run(args):
    project = read_json("config/project.json")
    config = read_json("config/discovery.json")
    limits = config["limits"]
    catalogue = read_json("data/catalogue.json", [])
    candidates = read_json("data/candidates.json", [])
    state = read_json("data/discovery-state.json", {})
    discovery = Client(max_requests=limits["discovery_requests"], seconds=limits["discovery_seconds"])
    processing = None

    def processor():
        return Client(
            max_requests=limits["requests"] - limits["discovery_requests"],
            seconds=limits["seconds"] - limits["discovery_seconds"],
        )

    report = {
        "date": args.until,
        "events": [],
        "judged": 0,
        "model_calls": 0,
        "accepted": 0,
        "downloaded": 0,
        "errors": [],
    }
    try:
        if not args.download_only:
            rows, events = collect(discovery, config, state, catalogue, args.until, historical=args.backfill)
            report["events"] = events
            candidates = merge_candidates(candidates, rows, catalogue)
            processing = processor()
            configured = all(os.getenv(k) for k in ["LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"])
            report["judge"] = "configured" if configured else "not-configured"
            eligible = review_schedule(candidates, args.until, limits["judge_items"])
            if configured:
                for row in eligible[: limits["judge_items"]]:
                    row["last_attempt"] = args.until
                    retrieved = False
                    try:
                        text, evidence = retrieve(processing, row, prefer_full_text=True)
                        retrieved = True
                        report["model_calls"] += 1
                        first = classify(processing, project, row, text, evidence)
                        second = None
                        if needs_audit(first):
                            report["model_calls"] += 1
                            second = classify(processing, project, row, text, evidence, audit=True)
                        report["judged"] += 1
                        report["accepted"] += apply_decision(
                            row, first, second, evidence, catalogue, args.until, "daily-llm"
                        )
                    except BudgetExceeded:
                        report["budget_exhausted"] = True
                        break
                    except Exception as error:
                        row["status"] = "pending" if retrieved else "needs-text"
                        row["error"] = str(error)[:200]
                        row["retry_after"] = (date.fromisoformat(args.until) + timedelta(days=2)).isoformat()
                        report["errors"].append({"id": row["id"], "stage": "review", "error": row["error"]})
        if processing is None:
            processing = processor()
        attempts = 0
        for row in sorted(catalogue, key=lambda r: (r.get("download", {}).get("checked", ""), r["id"])):
            previous = row.get("download", {})
            if (
                previous.get("path")
                and Path(previous["path"]).is_file()
                and hashlib.sha256(Path(previous["path"]).read_bytes()).hexdigest() == previous.get("sha256")
            ):
                continue
            if attempts >= limits["downloads"]:
                break
            attempts += 1
            row["download"] = download(processing, row, "downloads", limits["download_mb"])
            report["downloaded"] += row["download"]["status"] == "downloaded"
            if row["download"]["status"] != "downloaded" and pdf_sources(row):
                report["errors"].append(
                    {"id": row["id"], "stage": "download", "error": row["download"]["errors"]}
                )
    finally:
        # Preserve discovery and review progress even on an interrupted stage.
        write_json("data/candidates.json", candidates)
        write_json("data/discovery-state.json", state)
        validate_catalogue(catalogue, project)
        write_json("data/catalogue.json", sorted(catalogue, key=lambda r: r["id"]))
        make_manifest(catalogue, "data/notebooklm-manifest.json")
        render(catalogue, project)
        report["requests"] = discovery.count + (processing.count if processing else 0)
        report["pending"] = sum(r["status"] in {"pending", "uncertain", "needs-text"} for r in candidates)
        report["status"] = (
            "degraded"
            if (
                report["errors"]
                or report.get("judge") == "not-configured"
                or report.get("budget_exhausted")
                or any(e["status"] == "error" for e in report["events"])
            )
            else "ok"
        )
        write_json("reports/latest-run.json", report)
        summary = f"Research run: {report['status']}; {report['judged']} reviewed; {report['accepted']} accepted; {report['downloaded']} PDFs; {report['pending']} pending."
        print(summary)
        if os.getenv("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as out:
                out.write(
                    summary + "\n\nSee reports/latest-run.json for service failures and coverage limits.\n"
                )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    daily = sub.add_parser("run")
    daily.add_argument("--until", default=today())
    daily.add_argument("--backfill", action="store_true")
    daily.add_argument("--download-only", action="store_true")
    sub.add_parser("validate")
    sub.add_parser("render")
    args = parser.parse_args()
    if args.command == "run":
        date.fromisoformat(args.until)
        run(args)
    else:
        rows, project = read_json("data/catalogue.json", []), read_json("config/project.json")
        validate_catalogue(rows, project)
        if args.command == "render":
            render(rows, project)
        print("Catalogue valid")


if __name__ == "__main__":
    main()

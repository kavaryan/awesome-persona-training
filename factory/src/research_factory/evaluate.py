"""Measure discovery separately from blinded, primary-text classification."""

import hashlib
import json
import time
from contextlib import chdir
from pathlib import Path

from .agent import CodeAgent
from .bootstrap import batch_review
from .runtime.evidence import retrieve
from .runtime.judge import agreed
from .runtime.net import Client
from .runtime.pipeline import needs_audit
from .runtime.store import identities, read_json, record_id, today, write_json


def evaluate(args, agent=None):
    benchmark_path = Path(args.benchmark).resolve()
    benchmark = read_json(benchmark_path)
    reference = read_json(Path(args.reference).resolve(), []) if args.reference else []
    output = Path(args.repo).resolve()
    agent = agent or CodeAgent(args.agent, args.model, args.agent_timeout, args.agent_budget)
    with chdir(output):
        project = read_json("config/project.json")
        existing = read_json("data/catalogue.json", []) + read_json("data/candidates.json", [])
        discovered_keys = set().union(*(identities(r) for r in existing)) if existing else set()
        independent_snapshot = read_json("reports/independent-discovery.json")
        if independent_snapshot:
            discovered_keys = set(independent_snapshot["identity_keys"])
        cases = benchmark["cases"]
        previous = read_json("reports/evaluation.json")
        carried = []
        if getattr(args, "retry_unresolved", False):
            if (
                not previous
                or previous["benchmark_sha256"] != hashlib.sha256(benchmark_path.read_bytes()).hexdigest()
            ):
                raise ValueError("Retry requires a prior evaluation of exactly this benchmark")
            carried = [
                c
                for c in previous["cases"]
                if c["prediction"] not in {"uncertain", "unreadable", "review-error"}
            ]
            resolved = {c["url"] for c in carried}
            cases = [c for c in cases if c["url"] not in resolved]
        results, records = list(carried), []
        client = Client(max_requests=200, seconds=600)
        known = {key: r for r in existing for key in identities(r)}
        for case in cases:
            base = next((known[k] for k in identities(case) if k in known), {})
            row = dict(base, url=case["url"], id=record_id(case["url"]))
            try:
                text, evidence = retrieve(client, row, prefer_full_text=True)
                records.append((row, text, evidence))
            except Exception as error:
                results.append(
                    {
                        "url": case["url"],
                        "expected": case["expected"],
                        "prediction": "unreadable",
                        "error": str(error)[:200],
                    }
                )
        case_map = {record_id(c["url"]): c for c in cases}
        stamp = str(time.time_ns())
        for offset in range(0, len(records), args.batch_size):
            batch = records[offset : offset + args.batch_size]
            try:
                first = batch_review(
                    agent, project, batch, False, ".bootstrap/evaluation", f"read-{stamp}-{offset}"
                )
                audit_batch = [r for r in batch if r[0]["id"] in first and needs_audit(first[r[0]["id"]])]
                audits = (
                    batch_review(
                        agent, project, audit_batch, True, ".bootstrap/evaluation", f"audit-{stamp}-{offset}"
                    )
                    if audit_batch
                    else {}
                )
                for row, _text, evidence in batch:
                    if row["id"] not in first:
                        results.append(
                            {
                                "url": row["url"],
                                "expected": case_map[row["id"]]["expected"],
                                "prediction": "review-error",
                                "error": first.errors[row["id"]],
                            }
                        )
                        continue
                    decision = first[row["id"]]
                    accepted = row["id"] in audits and agreed(decision, audits[row["id"]])
                    prediction = (
                        (
                            "core"
                            if decision["scope"] == audits[row["id"]]["scope"] == "core"
                            else "supporting"
                        )
                        if accepted
                        else (
                            "exclude"
                            if decision["scope"] == "exclude" and decision["confidence"] >= 0.9
                            else "uncertain"
                        )
                    )
                    case = case_map[row["id"]]
                    results.append(
                        {
                            "url": case["url"],
                            "expected": case["expected"],
                            "prediction": prediction,
                            "discovered_before_evaluation": bool(identities(case) & discovered_keys),
                            "challenge": case.get("challenge", ""),
                            "decision": decision,
                            "audit": audits.get(row["id"]),
                            "evidence": evidence,
                        }
                    )
            except Exception as error:
                results.extend(
                    {
                        "url": r["url"],
                        "expected": case_map[r["id"]]["expected"],
                        "prediction": "review-error",
                        "error": str(error)[:200],
                    }
                    for r, _, _ in batch
                )
            write_json("reports/evaluation-progress.json", results)

        def positive(r):
            return bool(set(r["expected"]) & {"core", "supporting"})

        def accepted(r):
            return r["prediction"] in {"core", "supporting"}

        tp = sum(positive(r) and accepted(r) for r in results)
        fp = sum(not positive(r) and accepted(r) for r in results)
        fn = sum(positive(r) and not accepted(r) for r in results)
        reference_positives = [
            r for r in reference if r.get("scope") in {"core", "mechanism", "background", "supporting"}
        ]
        recovery = [
            {
                "title": r["title"],
                "url": r["url"],
                "prior_scope": r["scope"],
                "rediscovered": bool(identities(r) & discovered_keys),
            }
            for r in reference_positives
        ]
        report = {
            "date": today(),
            "benchmark": benchmark.get("name"),
            "benchmark_sha256": hashlib.sha256(benchmark_path.read_bytes()).hexdigest(),
            "cases": results,
            "reused_resolved_cases": len(carried),
            "retry_policy": "Only unresolved or failed cases retried; expected labels never control retry selection.",
            "metrics": {
                "true_positive": tp,
                "false_positive": fp,
                "false_negative_or_unresolved": fn,
                "precision": tp / (tp + fp) if tp + fp else None,
                "recall": tp / (tp + fn) if tp + fn else None,
                "exact_scope_matches": sum(r["prediction"] in r["expected"] for r in results),
                "unresolved": sum(
                    r["prediction"] in {"uncertain", "unreadable", "review-error"} for r in results
                ),
            },
            "reference_recovery": recovery,
            "limitations": [
                "A finite benchmark cannot prove exhaustive discovery or zero false positives.",
                "Prior catalogue labels are a recovery reference, not audited ground truth.",
                "Evaluation URLs are never injected into the discovery queue or accepted catalogue.",
                "Two independent passes use the same configured agent model; correlated errors remain possible.",
            ],
        }
        if previous:
            write_json(f"reports/evaluation-history/{stamp}-previous.json", previous)
        write_json(f"reports/evaluation-history/{stamp}.json", report)
        write_json("reports/evaluation.json", report)
    print(json.dumps(report["metrics"], indent=2))
    if args.fail_on_regression and (fp or fn or report["metrics"]["unresolved"]):
        raise ValueError("Benchmark regression or unresolved cases; inspect reports/evaluation.json")
    return report

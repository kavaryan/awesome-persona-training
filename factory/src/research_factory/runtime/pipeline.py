"""Shared acceptance rules for agent bootstrap and small-model daily updates."""

from datetime import date, timedelta

from .judge import ACCEPTED, agreed
from .store import identities, today


def apply_decision(record, first, second, evidence, catalogue, cutoff, reviewer):
    record["decision"] = first
    record["last_attempt"] = cutoff
    record.pop("error", None)
    record.pop("retry_after", None)
    if first["scope"] == "exclude" and first["confidence"] >= 0.9:
        record["status"] = "excluded"
    elif second and agreed(first, second):
        if record.get("date", "")[:10] > cutoff:
            record["status"] = "pending"
            record["retry_after"] = record["date"][:10]
            return False
        if any(identities(record) & identities(r) for r in catalogue):
            record["status"] = "accepted"
            return False
        accepted = {
            k: v
            for k, v in record.items()
            if k not in {"abstract", "decision", "error", "retry_after", "last_attempt"}
        }
        accepted.update(
            first,
            scope="core" if first["scope"] == second["scope"] == "core" else "supporting",
            audit=second,
            evidence=evidence,
            reviewer=reviewer,
            reviewed=today(),
            status="accepted",
        )
        catalogue.append(accepted)
        record["status"] = "accepted"
        return True
    else:
        record["status"] = "uncertain"
        record["retry_after"] = (date.fromisoformat(cutoff) + timedelta(days=30)).isoformat()
    if second:
        record["audit"] = second
    return False


def needs_audit(decision):
    return decision["scope"] in ACCEPTED and decision["confidence"] >= 0.9


def review_schedule(candidates, cutoff, limit):
    """Reserve half the bounded daily slots for new arrivals and half for older work."""
    eligible = [
        r
        for r in candidates
        if r["status"] in {"pending", "uncertain", "needs-text"} and r.get("retry_after", "") <= cutoff
    ]
    recent_boundary = (date.fromisoformat(cutoff) - timedelta(days=2)).isoformat()
    recent = sorted(
        (r for r in eligible if r.get("first_seen", "") >= recent_boundary and not r.get("last_attempt")),
        key=lambda r: (r.get("first_seen", ""), r.get("date", ""), r["id"]),
        reverse=True,
    )
    selected = recent[: (limit + 1) // 2]
    selected_ids = {r["id"] for r in selected}
    backlog = sorted(
        (r for r in eligible if r["id"] not in selected_ids),
        key=lambda r: (r.get("last_attempt", ""), r.get("first_seen", ""), r["id"]),
    )
    return (selected + backlog[: limit - len(selected)])[:limit]

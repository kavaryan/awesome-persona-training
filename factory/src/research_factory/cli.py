"""Create a research repository from a Markdown brief and seed papers."""

import argparse
import re
from datetime import date
from pathlib import Path

from .bootstrap import initialize
from .evaluate import evaluate
from .runtime.store import today


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser(
        "init", help="Research the brief, compile configuration and build a runnable repository"
    )
    init.add_argument("brief")
    init.add_argument("--output", help="New directory; defaults to awesome-<brief filename>")
    init.add_argument("--until", default=today())
    init.add_argument("--resume", action="store_true")
    init.add_argument(
        "--prior-catalogue", help="Optional JSON bibliography to re-audit; old labels are discarded"
    )
    init.add_argument("--plan", help="Use an inspected plan JSON instead of rerunning agent planning")
    init.add_argument("--stage", choices=["all", "plan", "discover", "expand", "review"], default="all")
    init.add_argument("--agent", default="codex", help="Path to authenticated Codex CLI")
    init.add_argument(
        "--model", help="Optional explicit agent model; otherwise keep the CLI's configured model"
    )
    init.add_argument("--agent-timeout", type=int, default=600)
    init.add_argument("--agent-budget", type=int, default=3600)
    init.add_argument("--review-limit", type=int, default=80)
    init.add_argument("--batch-size", type=int, default=6)
    init.add_argument("--download-limit", type=int, default=30)
    init.add_argument(
        "--discovery-rounds", type=int, default=3, help="Bounded query/citation rotations during bootstrap"
    )
    init.add_argument(
        "--expansion-rounds",
        type=int,
        default=2,
        help="Bounded agent searches for missing vocabulary and citation neighborhoods",
    )
    ev = sub.add_parser("evaluate", help="Blinded content evaluation and separate discovery-recovery audit")
    ev.add_argument("--repo", required=True)
    ev.add_argument("--benchmark", required=True)
    ev.add_argument(
        "--reference",
        help="Optional previous catalogue; compared for recovery only, not supplied to the agent",
    )
    ev.add_argument("--agent", default="codex")
    ev.add_argument("--model")
    ev.add_argument("--agent-timeout", type=int, default=360)
    ev.add_argument("--agent-budget", type=int, default=2400)
    ev.add_argument("--batch-size", type=int, default=6)
    ev.add_argument("--fail-on-regression", action="store_true")
    ev.add_argument(
        "--retry-unresolved",
        action="store_true",
        help="Retry unresolved cases while preserving evaluation history",
    )
    args = parser.parse_args()
    if args.command == "init":
        date.fromisoformat(args.until)
        if not args.output:
            stem = re.sub(r"[^a-z0-9]+", "-", Path(args.brief).stem.lower()).strip("-") or "research"
            args.output = str(Path.cwd() / (stem if stem.startswith("awesome-") else "awesome-" + stem))
    for name in [
        "agent_timeout",
        "agent_budget",
        "review_limit",
        "batch_size",
        "download_limit",
        "discovery_rounds",
        "expansion_rounds",
    ]:
        if hasattr(args, name) and getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    try:
        report = initialize(args) if args.command == "init" else evaluate(args)
        if report.get("status") == "review-failed":
            parser.exit(
                1, "All attempted reviews failed; inspect the checkpointed bootstrap-review report.\n"
            )
    except (ValueError, RuntimeError, TimeoutError) as error:
        parser.exit(
            1,
            f"Factory stopped: {error}\nProgress remains in the output directory; inspect reports and use --resume.\n",
        )


if __name__ == "__main__":
    main()

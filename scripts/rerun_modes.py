#!/usr/bin/env python3
"""Validate crawl-and-publish rerun modes before any publishing side effects."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

RUN_MODES = {"normal", "dry-run", "restore", "force-replace", "candidate-only"}
SOURCE_REFRESH_POLICIES = {"reuse-same-day", "refresh-missing-stale", "force-refresh"}
WEEK_PATTERN = re.compile(r"^[0-9]{4}-W[0-9]{2}$")
RUN_ID_PATTERN = re.compile(r"^[0-9]+$")


@dataclass(frozen=True)
class ModeDecision:
    run_mode: str
    source_refresh_policy: str
    action: str
    publish_allowed: bool
    crawl_allowed: bool
    reasons: list[str]


def validate_modes(
    *,
    run_mode: str,
    source_refresh_policy: str,
    rebuild_week: str = "",
    source_run_id: str = "",
    publish_release: bool = False,
) -> ModeDecision:
    reasons: list[str] = []
    if run_mode not in RUN_MODES:
        reasons.append(f"invalid run_mode: {run_mode}")
    if source_refresh_policy not in SOURCE_REFRESH_POLICIES:
        reasons.append(f"invalid source_refresh_policy: {source_refresh_policy}")
    if rebuild_week and run_mode != "restore":
        reasons.append("rebuild_week is a restore operation and requires run_mode=restore")
    if rebuild_week and not WEEK_PATTERN.fullmatch(rebuild_week):
        reasons.append("rebuild_week must use YYYY-WNN format")
    if run_mode == "restore" and not rebuild_week:
        reasons.append("run_mode=restore requires rebuild_week=YYYY-WNN")
    if run_mode == "restore" and not source_run_id:
        reasons.append("run_mode=restore requires source_run_id")
    if source_run_id and run_mode != "restore":
        reasons.append("source_run_id is only allowed with run_mode=restore")
    if source_run_id and not RUN_ID_PATTERN.fullmatch(source_run_id):
        reasons.append("source_run_id must be a numeric GitHub Actions workflow run ID")
    if run_mode in {"dry-run", "candidate-only"} and publish_release:
        reasons.append(f"publish_release is not allowed with run_mode={run_mode}")
    if run_mode == "restore" and source_refresh_policy == "force-refresh":
        reasons.append(
            "run_mode=restore hydrates publish artifacts and cannot force-refresh sources"
        )

    publish_allowed = run_mode not in {"dry-run", "candidate-only"}
    crawl_allowed = not rebuild_week
    if run_mode == "dry-run":
        action = "analyze candidate only; never commit or deploy"
    elif run_mode == "candidate-only":
        action = "produce candidate artifacts only; never promote"
    elif run_mode == "restore":
        action = f"restore published artifacts for {rebuild_week} and regenerate through guarded promotion"
    elif run_mode == "force-replace":
        action = "explicit replacement run; promotion still requires all gates"
    else:
        action = "normal guarded crawl, analysis, publish, and deploy"

    return ModeDecision(
        run_mode, source_refresh_policy, action, publish_allowed, crawl_allowed, reasons
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-mode", default="normal")
    parser.add_argument("--source-refresh-policy", default="reuse-same-day")
    parser.add_argument("--rebuild-week", default="")
    parser.add_argument("--source-run-id", default="")
    parser.add_argument("--publish-release", action="store_true")
    parser.add_argument("--summary-json", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    decision = validate_modes(
        run_mode=args.run_mode,
        source_refresh_policy=args.source_refresh_policy,
        rebuild_week=args.rebuild_week.strip(),
        source_run_id=args.source_run_id.strip(),
        publish_release=args.publish_release,
    )
    payload = {
        "run_mode": decision.run_mode,
        "source_refresh_policy": decision.source_refresh_policy,
        "publish_allowed": decision.publish_allowed,
        "crawl_allowed": decision.crawl_allowed,
        "source_run_id": args.source_run_id.strip(),
        "action": decision.action,
        "valid": not decision.reasons,
        "reasons": decision.reasons,
    }
    if args.summary_json:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(payload, sort_keys=True))
    if decision.reasons:
        for reason in decision.reasons:
            print(f"::error::{reason}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

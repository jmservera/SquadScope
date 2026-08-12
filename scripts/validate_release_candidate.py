#!/usr/bin/env python3
"""Validate Claracle release-candidate evidence and revision boundaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess  # nosec B404 - fixed Git argv is required to inspect committed tree objects
from calendar import monthrange
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

DEFAULT_RECORD = Path("data/release/claracle-v1.1-release-candidate.json")
DEFAULT_SCHEMA = Path("data/schemas/release-candidate.schema.json")
EVIDENCE_ONLY_PREFIXES = (
    ".copilot-tracking/",
    "data/release/",
    "docs/review/claracle-post-relaunch/",
)
REQUIRED_REVIEW_ROLES = {
    "DRF-01": {"Amy", "Fry"},
    "DRF-02": {"Amy", "Fry"},
    "DRF-03": {"Amy", "Fry"},
    "DRF-04": {"Fry"},
}


def load_object(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return loaded


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp must include a timezone: {value}")
    return parsed.astimezone(timezone.utc)


def add_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def product_tree_digest(root: Path, revision: str = "HEAD") -> str:
    # Fixed Git argv, no shell, and schema-constrained revisions.
    result = subprocess.run(  # nosec
        ["git", "ls-tree", "-r", "--full-tree", revision],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    digest = hashlib.sha256()
    for line in result.stdout.splitlines():
        _, path = line.split("\t", 1)
        if not path.startswith(EVIDENCE_ONLY_PREFIXES):
            digest.update(f"{line}\n".encode())
    return digest.hexdigest()


def file_sha256(root: Path, relative_path: str) -> str:
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"Evidence path escapes the repository: {relative_path}") from error
    if not candidate.is_file():
        raise ValueError(f"Evidence path does not exist: {relative_path}")
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def validate_review(
    review: dict[str, Any],
    *,
    candidate_sha: str,
    candidate_frozen_at: datetime,
    now: datetime,
) -> None:
    if review["candidate_sha"] != candidate_sha:
        raise ValueError("Owner review does not match candidate SHA")
    reviewed_at = parse_timestamp(review["reviewed_at"])
    if reviewed_at < candidate_frozen_at or reviewed_at > now:
        raise ValueError("Owner review timestamp is outside the candidate review window")
    if review["disposition"] != "pass" or review["unresolved_work"]:
        raise ValueError("Closed finding requires a passing owner review with no unresolved work")
    if any(
        finding["status"] == "open" and finding["severity"] in {1, 2}
        for finding in review["findings"]
    ):
        raise ValueError("Owner review contains an unresolved blocking finding")


def validate(
    payload: dict[str, Any],
    schema: dict[str, Any],
    *,
    now: datetime | None = None,
    root: Path | None = None,
    product_tree_sha256: str | None = None,
    changed_paths: list[str] | None = None,
) -> None:
    errors = sorted(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        path = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
        raise ValueError(f"Schema validation failed at {path}: {errors[0].message}")

    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    candidate_sha = payload["candidate_sha"]
    candidate_digest = payload["candidate_product_tree_sha256"]
    candidate_frozen_value = payload["candidate_frozen_at"]
    status = payload["status"]
    if candidate_sha is None:
        if (
            status != "preparing"
            or candidate_frozen_value is not None
            or candidate_digest is not None
        ):
            raise ValueError("Only a preparing record may omit the candidate boundary")
        candidate_frozen_at = None
    else:
        if candidate_frozen_value is None or candidate_digest is None:
            raise ValueError("A frozen candidate requires timestamp and product-tree digest")
        candidate_frozen_at = parse_timestamp(candidate_frozen_value)
        if candidate_frozen_at > now:
            raise ValueError("Candidate freeze timestamp cannot be in the future")
        if product_tree_sha256 is not None and product_tree_sha256 != candidate_digest:
            raise ValueError("Product tree changed after candidate freeze")

    finding_ids = [finding["id"] for finding in payload["findings"]]
    if finding_ids != [f"DRF-0{index}" for index in range(1, 6)]:
        raise ValueError("Findings must contain DRF-01 through DRF-05 in order")

    for finding in payload["findings"]:
        finding_id = finding["id"]
        for evidence in finding["evidence"]:
            if evidence["candidate_sha"] != candidate_sha:
                raise ValueError(f"{finding_id} evidence does not match candidate SHA")
            if root is not None and file_sha256(root, evidence["path"]) != evidence["sha256"]:
                raise ValueError(f"{finding_id} evidence hash does not match its source")

        if finding["status"] == "closed":
            if candidate_sha is None or candidate_frozen_at is None:
                raise ValueError(f"{finding_id} cannot close before candidate freeze")
            if not finding["evidence"]:
                raise ValueError(f"{finding_id} closure requires evidence")
            required_roles = REQUIRED_REVIEW_ROLES.get(finding_id, set())
            actual_roles = {review["role"] for review in finding["reviews"]}
            if not required_roles.issubset(actual_roles):
                raise ValueError(f"{finding_id} closure lacks required owner reviews")
            for review in finding["reviews"]:
                validate_review(
                    review,
                    candidate_sha=candidate_sha,
                    candidate_frozen_at=candidate_frozen_at,
                    now=now,
                )

        live_review = finding["live_at_review"]
        requires_live_review = finding_id in {"DRF-03", "DRF-05"}
        if finding["status"] == "closed" and requires_live_review:
            if live_review is None or live_review["disposition"] != "pass":
                raise ValueError(f"{finding_id} closure requires a passing live AT review")
            if live_review["candidate_sha"] != candidate_sha:
                raise ValueError(f"{finding_id} live AT review does not match candidate SHA")
            reviewed_at = parse_timestamp(live_review["reviewed_at"])
            if reviewed_at < candidate_frozen_at or reviewed_at > now:
                raise ValueError(f"{finding_id} live AT review timestamp is invalid")
            if live_review["unresolved_work"]:
                raise ValueError(f"{finding_id} live AT review has unresolved work")
            if any(
                item["status"] == "open" and item["severity"] in {1, 2}
                for item in live_review["findings"]
            ):
                raise ValueError(f"{finding_id} live AT review has blocking findings")

    blocking = [
        finding["id"]
        for finding in payload["findings"]
        if finding["severity"] in {1, 2} and finding["status"] != "closed"
    ]
    sponsor = payload["sponsor"]
    go_state = status in {"go", "deployed"}
    if go_state != (sponsor["status"] == "go"):
        raise ValueError("Top-level GO state and sponsor decision must agree")
    if go_state:
        if candidate_sha is None or blocking:
            raise ValueError(f"GO is blocked by unresolved findings: {blocking}")
        if sponsor["candidate_sha"] != candidate_sha:
            raise ValueError("Sponsor decision does not match candidate SHA")
        if not sponsor["reviewer"] or not sponsor["decided_at"]:
            raise ValueError("Sponsor GO requires reviewer and decision timestamp")
        sponsor_at = parse_timestamp(sponsor["decided_at"])
        if candidate_frozen_at is None or sponsor_at < candidate_frozen_at or sponsor_at > now:
            raise ValueError("Sponsor decision timestamp is outside the candidate window")
        rollback = payload["rollback"]
        if rollback["status"] != "tested" or not rollback["evidence"]:
            raise ValueError("Sponsor GO requires tested rollback evidence")
    else:
        sponsor_at = None

    deployment = payload["deployment"]
    deployment_completed = deployment["status"] == "completed"
    if (status == "deployed") != deployment_completed:
        raise ValueError("Deployed status and completed deployment must agree")
    if deployment_completed:
        if sponsor_at is None:
            raise ValueError("Completed deployment requires sponsor GO")
        if not all(
            (
                deployment["merge_sha"],
                deployment["run_id"],
                deployment["deployed_at"],
                deployment["evidence"],
            )
        ):
            raise ValueError("Completed deployment evidence is incomplete")
        deployed_at = parse_timestamp(deployment["deployed_at"])
        if deployed_at < sponsor_at or deployed_at > now:
            raise ValueError("Deployment timestamp must follow sponsor GO")
    else:
        deployed_at = None

    windows = [outcome["window"] for outcome in payload["outcomes"]]
    expected_windows = ["release-day", "seven-day", "28-day", "three-month", "six-month"]
    if windows != expected_windows:
        raise ValueError("Outcome windows are missing, duplicated, or out of order")
    for outcome in payload["outcomes"]:
        if outcome["status"] == "scheduled" and outcome["due_at"] is None:
            raise ValueError(f"{outcome['window']} scheduled outcome requires due_at")
        if outcome["status"] == "completed":
            if not outcome["due_at"] or not outcome["completed_at"] or not outcome["evidence"]:
                raise ValueError(f"{outcome['window']} completed outcome is incomplete")
            completed_at = parse_timestamp(outcome["completed_at"])
            if completed_at < parse_timestamp(outcome["due_at"]):
                raise ValueError(f"{outcome['window']} cannot be completed before its due date")
            if completed_at > now:
                raise ValueError(f"{outcome['window']} cannot be completed in the future")

    if deployed_at is not None:
        expected_due_dates = {
            "release-day": deployed_at,
            "seven-day": deployed_at + timedelta(days=7),
            "28-day": deployed_at + timedelta(days=28),
            "three-month": add_months(deployed_at, 3),
            "six-month": add_months(deployed_at, 6),
        }
        for outcome in payload["outcomes"]:
            due_at = parse_timestamp(outcome["due_at"]) if outcome["due_at"] else None
            if due_at != expected_due_dates[outcome["window"]]:
                raise ValueError(f"{outcome['window']} due date is not deployment-relative")
            required_status = "completed" if outcome["window"] == "release-day" else "scheduled"
            if outcome["status"] != required_status:
                raise ValueError(f"{outcome['window']} has invalid post-deployment status")
    elif any(outcome["status"] != "pending" for outcome in payload["outcomes"]):
        raise ValueError("Outcome windows cannot be scheduled before deployment")

    if candidate_sha and changed_paths is not None:
        invalid = [path for path in changed_paths if not path.startswith(EVIDENCE_ONLY_PREFIXES)]
        if invalid:
            raise ValueError(
                "Product or test files changed after candidate freeze: "
                + ", ".join(sorted(invalid))
            )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--check-git-boundary",
        action="store_true",
        help="Compare the frozen product-tree digest with the current revision.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    record = args.record if args.record.is_absolute() else root / args.record
    schema_path = args.schema if args.schema.is_absolute() else root / args.schema
    payload = load_object(record)
    current_product_digest = None
    if args.check_git_boundary and payload["candidate_sha"]:
        current_product_digest = product_tree_digest(root)
    validate(
        payload,
        load_object(schema_path),
        root=root,
        product_tree_sha256=current_product_digest,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.validate_release_candidate import load_object, validate

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data/release/claracle-v1.1-release-candidate.json"
SCHEMA = ROOT / "data/schemas/release-candidate.schema.json"
CANDIDATE_SHA = "a" * 40


def payload() -> dict:
    return load_object(RECORD)


def freeze(candidate: dict) -> dict:
    candidate["candidate_sha"] = CANDIDATE_SHA
    candidate["candidate_frozen_at"] = "2026-08-12T22:30:00Z"
    return candidate


def close_findings(candidate: dict) -> dict:
    for finding in candidate["findings"]:
        finding["status"] = "closed"
        finding["evidence"] = [
            {
                "type": "automated",
                "path": f"reports/{finding['id'].lower()}.json",
                "candidate_sha": CANDIDATE_SHA,
            }
        ]
    candidate["findings"][-1]["live_at_review"] = {
        "reviewer": "Named reviewer",
        "reviewed_at": "2026-08-12T23:00:00Z",
        "candidate_sha": CANDIDATE_SHA,
        "operating_system": "Windows 11 24H2",
        "browser": "Microsoft Edge 140",
        "assistive_technology": "NVDA 2026.1",
        "scenarios": ["Keyboard navigation", "Dynamic repository filters"],
        "disposition": "pass",
    }
    return candidate


def test_checked_in_preparing_record_is_valid() -> None:
    validate(payload(), load_object(SCHEMA))


def test_rejects_mixed_candidate_evidence() -> None:
    candidate = freeze(payload())
    candidate["findings"][0]["evidence"] = [
        {
            "type": "automated",
            "path": "reports/drf-01.json",
            "candidate_sha": "b" * 40,
        }
    ]
    with pytest.raises(ValueError, match="does not match candidate SHA"):
        validate(candidate, load_object(SCHEMA))


def test_rejects_go_with_open_blocking_findings() -> None:
    candidate = freeze(payload())
    candidate["status"] = "go"
    candidate["sponsor"] = {
        "status": "go",
        "reviewer": "jmservera",
        "decided_at": "2026-08-12T23:30:00Z",
        "candidate_sha": CANDIDATE_SHA,
    }
    with pytest.raises(ValueError, match="unresolved findings"):
        validate(candidate, load_object(SCHEMA))


def test_rejects_drf05_closure_without_live_at_review() -> None:
    candidate = freeze(payload())
    candidate["findings"][-1]["status"] = "closed"
    with pytest.raises(ValueError, match="passing live AT review"):
        validate(candidate, load_object(SCHEMA))


def test_rejects_scheduled_outcome_without_due_date() -> None:
    candidate = payload()
    candidate["outcomes"][1]["status"] = "scheduled"
    with pytest.raises(ValueError, match="requires due_at"):
        validate(candidate, load_object(SCHEMA))


def test_rejects_future_completed_outcome() -> None:
    candidate = payload()
    candidate["outcomes"][0].update(
        {
            "status": "completed",
            "due_at": "2026-08-12T22:00:00Z",
            "completed_at": "2026-08-13T00:00:00Z",
            "evidence": ["live probes"],
        }
    )
    with pytest.raises(ValueError, match="cannot be completed in the future"):
        validate(
            candidate,
            load_object(SCHEMA),
            now=datetime(2026, 8, 12, 23, tzinfo=timezone.utc),
        )


def test_rejects_outcome_completed_before_due_date() -> None:
    candidate = payload()
    candidate["outcomes"][1].update(
        {
            "status": "completed",
            "due_at": "2026-08-20T00:00:00Z",
            "completed_at": "2026-08-13T00:00:00Z",
            "evidence": ["premature probe"],
        }
    )
    with pytest.raises(ValueError, match="before its due date"):
        validate(
            candidate,
            load_object(SCHEMA),
            now=datetime(2026, 8, 21, tzinfo=timezone.utc),
        )


def test_valid_go_and_release_day_transition() -> None:
    candidate = close_findings(freeze(payload()))
    candidate["status"] = "deployed"
    candidate["sponsor"] = {
        "status": "go",
        "reviewer": "jmservera",
        "decided_at": "2026-08-12T23:30:00Z",
        "candidate_sha": CANDIDATE_SHA,
    }
    candidate["deployment"] = {
        "status": "completed",
        "merge_sha": "c" * 40,
        "run_id": 12345,
        "deployed_at": "2026-08-13T00:00:00Z",
        "evidence": ["deployment run"],
    }
    candidate["outcomes"][0].update(
        {
            "status": "completed",
            "due_at": "2026-08-13T00:00:00Z",
            "completed_at": "2026-08-13T00:05:00Z",
            "evidence": ["production probes"],
        }
    )
    for outcome in candidate["outcomes"][1:]:
        outcome["status"] = "scheduled"
        outcome["due_at"] = "2027-02-13T00:00:00Z"

    validate(
        candidate,
        load_object(SCHEMA),
        now=datetime(2026, 8, 13, 1, tzinfo=timezone.utc),
    )


def test_rejects_product_changes_after_candidate_freeze() -> None:
    candidate = freeze(payload())
    with pytest.raises(ValueError, match="Product or test files changed"):
        validate(
            candidate,
            load_object(SCHEMA),
            changed_paths=[
                ".copilot-tracking/reviews/release.md",
                "assets/js/repository-explorer.js",
            ],
        )


def test_allows_evidence_only_changes_after_candidate_freeze() -> None:
    candidate = freeze(payload())
    validate(
        candidate,
        load_object(SCHEMA),
        changed_paths=[
            ".copilot-tracking/reviews/release.md",
            "data/release/claracle-v1.1-release-candidate.json",
            "docs/review/claracle-post-relaunch/release-candidate.md",
        ],
    )

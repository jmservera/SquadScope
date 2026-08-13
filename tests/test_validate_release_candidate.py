from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.validate_release_candidate import load_object, validate

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data/release/claracle-v1.1-release-candidate.json"
SCHEMA = ROOT / "data/schemas/release-candidate.schema.json"
CANDIDATE_SHA = "a" * 40
PRODUCT_TREE_SHA256 = "b" * 64
EVIDENCE_SHA256 = "c" * 64


def payload() -> dict:
    candidate = load_object(RECORD)
    candidate["candidate_sha"] = None
    candidate["candidate_product_tree_sha256"] = None
    candidate["candidate_frozen_at"] = None
    candidate["status"] = "preparing"
    candidate["sponsor"] = {
        "status": "pending",
        "reviewer": None,
        "decided_at": None,
        "candidate_sha": None,
    }
    candidate["rollback"]["status"] = "ready"
    candidate["deployment"] = {
        "status": "pending",
        "merge_sha": None,
        "run_id": None,
        "deployed_at": None,
        "evidence": [],
    }
    for outcome in candidate["outcomes"]:
        outcome["status"] = "pending"
        outcome["due_at"] = None
        outcome["completed_at"] = None
        outcome["evidence"] = []
    for finding in candidate["findings"]:
        finding["status"] = "open"
        finding["evidence"] = []
        finding["reviews"] = []
        finding["live_at_review"] = None
        finding["waiver"] = None
    return candidate


def freeze(candidate: dict) -> dict:
    candidate["candidate_sha"] = CANDIDATE_SHA
    candidate["candidate_product_tree_sha256"] = PRODUCT_TREE_SHA256
    candidate["candidate_frozen_at"] = "2026-08-12T22:30:00Z"
    candidate["status"] = "blocked"
    return candidate


def owner_review(role: str) -> dict:
    return {
        "reviewer": f"{role} reviewer",
        "role": role,
        "reviewed_at": "2026-08-12T23:00:00Z",
        "candidate_sha": CANDIDATE_SHA,
        "disposition": "pass",
        "findings": [],
        "unresolved_work": [],
    }


def live_review() -> dict:
    return {
        "reviewer": "Named human reviewer",
        "reviewed_at": "2026-08-12T23:05:00Z",
        "candidate_sha": CANDIDATE_SHA,
        "operating_system": "Windows 11 24H2",
        "browser": "Microsoft Edge 140",
        "assistive_technology": "NVDA 2026.1",
        "scenarios": ["Keyboard navigation", "Dynamic repository filters"],
        "findings": [],
        "unresolved_work": [],
        "disposition": "pass",
    }


def close_findings(candidate: dict) -> dict:
    roles = {
        "DRF-01": ["Amy", "Fry"],
        "DRF-02": ["Amy", "Fry"],
        "DRF-03": ["Amy", "Fry"],
        "DRF-04": ["Fry"],
        "DRF-05": [],
    }
    for finding in candidate["findings"]:
        finding["status"] = "closed"
        finding["evidence"] = [
            {
                "type": "automated",
                "path": f"reports/{finding['id'].lower()}.json",
                "sha256": EVIDENCE_SHA256,
                "candidate_sha": CANDIDATE_SHA,
            }
        ]
        finding["reviews"] = [owner_review(role) for role in roles[finding["id"]]]
    candidate["findings"][2]["live_at_review"] = live_review()
    candidate["findings"][4]["live_at_review"] = live_review()
    return candidate


def make_go(candidate: dict) -> dict:
    candidate["status"] = "go"
    candidate["sponsor"] = {
        "status": "go",
        "reviewer": "jmservera",
        "decided_at": "2026-08-12T23:30:00Z",
        "candidate_sha": CANDIDATE_SHA,
    }
    candidate["rollback"]["status"] = "tested"
    candidate["rollback"]["evidence"] = ["Rollback rehearsal passed."]
    return candidate


def make_deployed(candidate: dict) -> dict:
    make_go(candidate)
    candidate["status"] = "deployed"
    candidate["deployment"] = {
        "status": "completed",
        "merge_sha": "d" * 40,
        "run_id": 12345,
        "deployed_at": "2026-08-13T00:00:00Z",
        "evidence": ["deployment run"],
    }
    due_dates = {
        "release-day": "2026-08-13T00:00:00Z",
        "seven-day": "2026-08-20T00:00:00Z",
        "28-day": "2026-09-10T00:00:00Z",
        "three-month": "2026-11-13T00:00:00Z",
        "six-month": "2027-02-13T00:00:00Z",
    }
    for outcome in candidate["outcomes"]:
        outcome["due_at"] = due_dates[outcome["window"]]
        outcome["status"] = "scheduled"
    candidate["outcomes"][0].update(
        {
            "status": "completed",
            "completed_at": "2026-08-13T00:05:00Z",
            "evidence": ["production probes"],
        }
    )
    return candidate


def validate_at(candidate: dict) -> None:
    validate(
        candidate,
        load_object(SCHEMA),
        now=datetime(2026, 8, 13, 1, tzinfo=timezone.utc),
    )


def test_checked_in_preparing_record_is_valid() -> None:
    validate(payload(), load_object(SCHEMA), root=ROOT)


def test_rejects_mixed_candidate_evidence() -> None:
    candidate = freeze(payload())
    candidate["findings"][0]["evidence"] = [
        {
            "type": "automated",
            "path": "reports/drf-01.json",
            "sha256": EVIDENCE_SHA256,
            "candidate_sha": "e" * 40,
        }
    ]
    with pytest.raises(ValueError, match="does not match candidate SHA"):
        validate_at(candidate)


def test_rejects_closed_finding_without_evidence() -> None:
    candidate = freeze(payload())
    candidate["findings"][0]["status"] = "closed"
    candidate["findings"][0]["reviews"] = [owner_review("Amy"), owner_review("Fry")]
    with pytest.raises(ValueError, match="closure requires evidence"):
        validate_at(candidate)


def test_rejects_closed_finding_without_required_owner_reviews() -> None:
    candidate = freeze(payload())
    finding = candidate["findings"][0]
    finding["status"] = "closed"
    finding["evidence"] = [
        {
            "type": "automated",
            "path": "reports/drf-01.json",
            "sha256": EVIDENCE_SHA256,
            "candidate_sha": CANDIDATE_SHA,
        }
    ]
    finding["reviews"] = [owner_review("Amy")]
    with pytest.raises(ValueError, match="lacks required owner reviews"):
        validate_at(candidate)


def test_rejects_drf05_closure_without_complete_live_at_review() -> None:
    candidate = freeze(payload())
    finding = candidate["findings"][-1]
    finding["status"] = "closed"
    finding["evidence"] = [
        {
            "type": "live-at",
            "path": "reports/drf-05.json",
            "sha256": EVIDENCE_SHA256,
            "candidate_sha": CANDIDATE_SHA,
        }
    ]
    incomplete = live_review()
    del incomplete["findings"]
    finding["live_at_review"] = incomplete
    with pytest.raises(ValueError, match="Schema validation failed"):
        validate_at(candidate)


def test_rejects_go_with_open_blocking_findings() -> None:
    candidate = make_go(freeze(payload()))
    with pytest.raises(ValueError, match="unresolved findings"):
        validate_at(candidate)


def test_rejects_go_without_matching_sponsor_state() -> None:
    candidate = close_findings(freeze(payload()))
    candidate["status"] = "go"
    with pytest.raises(ValueError, match="must agree"):
        validate_at(candidate)


def test_rejects_go_without_tested_rollback() -> None:
    candidate = close_findings(freeze(payload()))
    make_go(candidate)
    candidate["rollback"]["status"] = "ready"
    with pytest.raises(ValueError, match="tested rollback"):
        validate_at(candidate)


def test_rejects_deployment_before_sponsor_go() -> None:
    candidate = make_deployed(close_findings(freeze(payload())))
    candidate["deployment"]["deployed_at"] = "2026-08-12T23:00:00Z"
    with pytest.raises(ValueError, match="must follow sponsor GO"):
        validate_at(candidate)


def test_rejects_non_relative_outcome_due_date() -> None:
    candidate = make_deployed(close_findings(freeze(payload())))
    candidate["outcomes"][1]["due_at"] = "2026-08-21T00:00:00Z"
    with pytest.raises(ValueError, match="not deployment-relative"):
        validate_at(candidate)


def test_rejects_outcome_completed_before_due_date() -> None:
    candidate = make_deployed(close_findings(freeze(payload())))
    candidate["outcomes"][1].update(
        {
            "status": "completed",
            "completed_at": "2026-08-19T00:00:00Z",
            "evidence": ["premature probe"],
        }
    )
    with pytest.raises(ValueError, match="before its due date"):
        validate_at(candidate)


def test_valid_go_and_release_day_transition() -> None:
    candidate = make_deployed(close_findings(freeze(payload())))
    validate_at(candidate)


def test_rejects_product_tree_change_after_squash_compatible_freeze() -> None:
    candidate = freeze(payload())
    with pytest.raises(ValueError, match="Product tree changed"):
        validate(
            candidate,
            load_object(SCHEMA),
            product_tree_sha256="f" * 64,
        )


def test_accepts_matching_product_tree_without_candidate_ancestry() -> None:
    candidate = freeze(payload())
    validate(
        candidate,
        load_object(SCHEMA),
        product_tree_sha256=PRODUCT_TREE_SHA256,
        candidate_revision_tree_sha256=PRODUCT_TREE_SHA256,
    )


def test_rejects_candidate_sha_not_bound_to_declared_product_tree() -> None:
    candidate = freeze(payload())
    with pytest.raises(ValueError, match="Declared candidate SHA"):
        validate(
            candidate,
            load_object(SCHEMA),
            product_tree_sha256=PRODUCT_TREE_SHA256,
            candidate_revision_tree_sha256="f" * 64,
        )


def test_rejects_missing_or_modified_evidence_source(tmp_path: Path) -> None:
    candidate = freeze(payload())
    evidence_path = tmp_path / "reports" / "drf-01.json"
    evidence_path.parent.mkdir()
    evidence_path.write_text("evidence", encoding="utf-8")
    candidate["findings"][0]["evidence"] = [
        {
            "type": "automated",
            "path": "reports/drf-01.json",
            "sha256": hashlib.sha256(b"different").hexdigest(),
            "candidate_sha": CANDIDATE_SHA,
        }
    ]
    with pytest.raises(ValueError, match="hash does not match"):
        validate(candidate, load_object(SCHEMA), root=tmp_path)


# ---------- Waiver / deferred-status tests ----------


def waiver_obj() -> dict:
    return {
        "approver": "jmservera",
        "rationale": "No screen-reader access or accessibility expert available.",
        "compensating_control": "Automated a11y coverage retained; no further UI changes ship without re-running the suite.",
        "issue_url": "https://github.com/jmservera/SquadScope/issues/999",
        "candidate_sha": CANDIDATE_SHA,
        "decided_at": "2026-08-12T23:00:00Z",
        "expires_at": "2026-11-12T23:00:00Z",
    }


def defer_findings(candidate: dict) -> dict:
    """Close DRF-01/02/04, defer DRF-03/05 with valid waivers."""
    roles = {
        "DRF-01": ["Amy", "Fry"],
        "DRF-02": ["Amy", "Fry"],
        "DRF-03": ["Amy", "Fry"],
        "DRF-04": ["Fry"],
        "DRF-05": [],
    }
    for finding in candidate["findings"]:
        fid = finding["id"]
        if fid in {"DRF-03", "DRF-05"}:
            finding["status"] = "deferred"
            finding["waiver"] = waiver_obj()
        else:
            finding["status"] = "closed"
            finding["waiver"] = None
        finding["evidence"] = (
            [
                {
                    "type": "automated",
                    "path": f"reports/{fid.lower()}.json",
                    "sha256": EVIDENCE_SHA256,
                    "candidate_sha": CANDIDATE_SHA,
                }
            ]
            if fid != "DRF-05"
            else []
        )
        finding["reviews"] = [owner_review(role) for role in roles[fid]]
    # DRF-03/05 still need evidence for DRF-03; DRF-05 has no evidence (matches real pattern)
    return candidate


def test_accepts_deferred_finding_with_valid_waiver() -> None:
    candidate = defer_findings(freeze(payload()))
    validate_at(candidate)


def test_go_succeeds_with_deferred_findings() -> None:
    candidate = make_go(defer_findings(freeze(payload())))
    candidate["rollback"]["status"] = "tested"
    candidate["rollback"]["evidence"] = ["Rollback rehearsal passed."]
    validate_at(candidate)


def test_rejects_deferred_with_null_waiver() -> None:
    candidate = freeze(payload())
    candidate["findings"][2]["status"] = "deferred"
    candidate["findings"][2]["waiver"] = None
    with pytest.raises(ValueError, match="requires a waiver"):
        validate_at(candidate)


def test_rejects_waiver_missing_required_field() -> None:
    candidate = freeze(payload())
    candidate["findings"][2]["status"] = "deferred"
    w = waiver_obj()
    del w["rationale"]
    candidate["findings"][2]["waiver"] = w
    with pytest.raises(ValueError, match="Schema validation failed"):
        validate_at(candidate)


def test_rejects_waiver_candidate_sha_mismatch() -> None:
    candidate = freeze(payload())
    candidate["findings"][2]["status"] = "deferred"
    w = waiver_obj()
    w["candidate_sha"] = "e" * 40
    candidate["findings"][2]["waiver"] = w
    with pytest.raises(ValueError, match="waiver does not match candidate SHA"):
        validate_at(candidate)


def test_rejects_deferral_before_candidate_freeze() -> None:
    candidate = payload()  # no freeze
    candidate["findings"][2]["status"] = "deferred"
    candidate["findings"][2]["waiver"] = waiver_obj()
    with pytest.raises(ValueError, match="cannot defer before candidate freeze"):
        validate_at(candidate)


def test_rejects_expired_waiver() -> None:
    candidate = freeze(payload())
    candidate["findings"][2]["status"] = "deferred"
    w = waiver_obj()
    w["expires_at"] = "2026-08-12T23:30:00Z"  # before now (2026-08-13T01:00)
    candidate["findings"][2]["waiver"] = w
    with pytest.raises(ValueError, match="waiver has expired"):
        validate_at(candidate)


def test_rejects_waiver_expires_before_decided() -> None:
    candidate = freeze(payload())
    candidate["findings"][2]["status"] = "deferred"
    w = waiver_obj()
    w["expires_at"] = "2026-08-12T22:59:00Z"  # before decided_at
    candidate["findings"][2]["waiver"] = w
    with pytest.raises(ValueError, match="expires_at must be after decided_at"):
        validate_at(candidate)


def test_rejects_waiver_decided_before_freeze() -> None:
    candidate = freeze(payload())
    candidate["findings"][2]["status"] = "deferred"
    w = waiver_obj()
    w["decided_at"] = "2026-08-12T22:00:00Z"  # before candidate_frozen_at (22:30)
    candidate["findings"][2]["waiver"] = w
    with pytest.raises(ValueError, match="outside the candidate window"):
        validate_at(candidate)


def test_rejects_waiver_decided_in_future() -> None:
    candidate = freeze(payload())
    candidate["findings"][2]["status"] = "deferred"
    w = waiver_obj()
    w["decided_at"] = "2026-08-13T02:00:00Z"  # after NOW (01:00)
    w["expires_at"] = "2026-11-13T02:00:00Z"
    candidate["findings"][2]["waiver"] = w
    with pytest.raises(ValueError, match="outside the candidate window"):
        validate_at(candidate)


def test_rejects_waiver_with_extra_field() -> None:
    candidate = freeze(payload())
    candidate["findings"][2]["status"] = "deferred"
    w = waiver_obj()
    w["unexpected_field"] = "should fail"
    candidate["findings"][2]["waiver"] = w
    with pytest.raises(ValueError, match="Schema validation failed"):
        validate_at(candidate)


def test_rejects_non_deferred_finding_with_waiver() -> None:
    candidate = freeze(payload())
    candidate["findings"][0]["waiver"] = waiver_obj()
    with pytest.raises(ValueError, match="has a waiver but is not deferred"):
        validate_at(candidate)

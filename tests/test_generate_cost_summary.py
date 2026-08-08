from __future__ import annotations

from datetime import UTC, datetime

import pytest

from scripts import generate_cost_summary as summary


def _record(
    *,
    run_id: str = "100",
    attempt: int = 1,
    stage: str = "analysis",
    model: str = "gpt-5-mini",
    cost: float | None = 0.25,
    timestamp: str = "2026-08-07T12:00:00Z",
) -> dict[str, object]:
    return {
        "timestamp": timestamp,
        "week": "2026-W32",
        "stage": stage,
        "model": model,
        "input_tokens": 100,
        "output_tokens": 20,
        "cost_usd": cost,
        "workflow_run_id": run_id,
        "run_attempt": attempt,
    }


def test_projection_selects_latest_attempt_and_excludes_model_none() -> None:
    records = [
        _record(attempt=1, cost=0.10),
        _record(attempt=2, cost=0.25),
        _record(run_id="101", stage="fallback", model="none", cost=None),
    ]

    projection = summary.build_projection(records, generated_at=datetime(2026, 8, 8, tzinfo=UTC))

    assert projection["totals"] == {"cost": 0.25, "input_tokens": 100, "output_tokens": 20}
    assert projection["exclusions"] == {
        "legacy_unidentified": 0,
        "superseded_attempts": 1,
        "model_none": 1,
    }
    assert projection["reconciliation"]["accepted_records"] == 2
    assert projection["reconciliation"]["billable_records"] == 1


def test_projection_rejects_legacy_rows_by_default() -> None:
    record = _record()
    del record["workflow_run_id"]
    del record["run_attempt"]

    with pytest.raises(ValueError, match="sponsor cutover policy required"):
        summary.build_projection([record], generated_at=datetime(2026, 8, 8, tzinfo=UTC))


def test_projection_can_record_explicit_legacy_exclusion() -> None:
    legacy = _record()
    del legacy["workflow_run_id"]
    del legacy["run_attempt"]

    projection = summary.build_projection(
        [legacy, _record()],
        generated_at=datetime(2026, 8, 8, tzinfo=UTC),
        legacy_policy="exclude-unidentified",
    )

    assert projection["provenance"]["legacy_policy"] == "exclude-unidentified"
    assert projection["exclusions"]["legacy_unidentified"] == 1


def test_projection_rejects_duplicate_accepted_identity() -> None:
    with pytest.raises(ValueError, match="Duplicate accepted identity"):
        summary.build_projection(
            [_record(), _record(cost=0.30)],
            generated_at=datetime(2026, 8, 8, tzinfo=UTC),
        )


def test_projection_rejects_stale_input() -> None:
    with pytest.raises(ValueError, match="stale"):
        summary.build_projection(
            [_record(timestamp="2026-06-01T00:00:00Z")],
            generated_at=datetime(2026, 8, 8, tzinfo=UTC),
        )


def test_projection_is_deterministic() -> None:
    generated_at = datetime(2026, 8, 8, tzinfo=UTC)
    first = summary.build_projection([_record()], generated_at=generated_at)
    second = summary.build_projection([_record()], generated_at=generated_at)

    assert first == second

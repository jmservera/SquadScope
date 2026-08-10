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


def test_projection_rejects_when_legacy_exclusion_leaves_no_identified_records() -> None:
    legacy = _record()
    del legacy["workflow_run_id"]
    del legacy["run_attempt"]

    with pytest.raises(ValueError, match="No identified accepted records"):
        summary.build_projection(
            [legacy],
            generated_at=datetime(2026, 8, 8, tzinfo=UTC),
            legacy_policy="exclude-unidentified",
        )


def test_projection_records_zero_cost_when_only_identified_record_uses_model_none() -> None:
    projection = summary.build_projection(
        [_record(model="none", cost=None)],
        generated_at=datetime(2026, 8, 8, tzinfo=UTC),
    )

    assert projection["totals"] == {"cost": 0, "input_tokens": 0, "output_tokens": 0}
    assert projection["reconciliation"]["accepted_records"] == 1
    assert projection["reconciliation"]["billable_records"] == 0
    assert projection["exclusions"]["model_none"] == 1


def test_projection_excludes_historical_legacy_rows_when_first_identified_run_uses_model_none() -> (
    None
):
    legacy = _record(timestamp="2026-05-25T11:56:08Z")
    del legacy["workflow_run_id"]
    del legacy["run_attempt"]

    projection = summary.build_projection(
        [legacy, _record(model="none", cost=None)],
        generated_at=datetime(2026, 8, 8, tzinfo=UTC),
        legacy_policy="exclude-unidentified",
    )

    assert projection["totals"] == {"cost": 0, "input_tokens": 0, "output_tokens": 0}
    assert projection["reconciliation"]["accepted_records"] == 1
    assert projection["exclusions"]["legacy_unidentified"] == 1
    assert projection["exclusions"]["model_none"] == 1


def test_main_rejects_malformed_ledger_without_writing_output(tmp_path) -> None:
    ledger = tmp_path / "token-usage.jsonl"
    output = tmp_path / "cost-summary.json"
    ledger.write_text("{not-json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Malformed ledger row 1"):
        summary.main(
            [
                "--ledger",
                str(ledger),
                "--output",
                str(output),
                "--generated-at",
                "2026-08-08T00:00:00Z",
                "--legacy-policy",
                "exclude-unidentified",
            ]
        )

    assert not output.exists()


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


def test_projection_fails_closed_on_unpriced_billable_record() -> None:
    with pytest.raises(ValueError, match="lack a reconciled cost_usd value"):
        summary.build_projection(
            [_record(cost=None)],
            generated_at=datetime(2026, 8, 8, tzinfo=UTC),
        )


def test_projection_is_deterministic() -> None:
    generated_at = datetime(2026, 8, 8, tzinfo=UTC)
    first = summary.build_projection([_record()], generated_at=generated_at)
    second = summary.build_projection([_record()], generated_at=generated_at)

    assert first == second

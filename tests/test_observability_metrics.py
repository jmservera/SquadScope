from __future__ import annotations

import json
import tempfile
from pathlib import Path

from scripts.observability_metrics import (
    METRICS_SCHEMA_VERSION,
    AnalysisMetrics,
    CrawlMetrics,
    MapReduceMetrics,
    ObservabilityLedger,
    duration_p95,
    emit_ledger,
    validate_ledger,
)


def sample_ledger() -> ObservabilityLedger:
    return ObservabilityLedger(
        schema_version=METRICS_SCHEMA_VERSION,
        run_id="local",
        week="2026-W21",
        timestamp="2026-05-20T12:00:00Z",
        crawl_metrics=[
            CrawlMetrics(
                duration_seconds=12.4,
                duration_p95_seconds=12.4,
                duration_sample_count=1,
                api_calls=10,
                cache_hits=5,
                cache_misses=10,
                stale_cache_hits=1,
                rate_limit_events=2,
                secondary_rate_limit_hit=False,
                source_type="github",
            )
        ],
        analysis_metrics=AnalysisMetrics(
            duration_seconds=3.2,
            token_ledger={
                "input_tokens": 100,
                "output_tokens": 25,
                "total_tokens": 125,
                "cost_usd": 0.0,
            },
            map_stages=[
                MapReduceMetrics(
                    stage="new_repos",
                    duration_seconds=0.3,
                    input_tokens=50,
                    output_tokens=10,
                    cost_usd=0.0,
                    status="pass",
                    gate_failure_reasons=[],
                )
            ],
            reduce_stage=MapReduceMetrics(
                stage="reduce",
                duration_seconds=0.8,
                input_tokens=10,
                output_tokens=15,
                cost_usd=0.0,
                status="fail",
                gate_failure_reasons=["AI provenance metadata missing"],
            ),
        ),
        environment={"pipeline": "test"},
    )


def test_validate_ledger_reports_missing_required_fields() -> None:
    errors = validate_ledger({"schema_version": METRICS_SCHEMA_VERSION})

    assert "run_id" in errors
    assert "crawl_metrics" in errors
    assert "environment" in errors


def test_duration_p95_uses_high_percentile_sample() -> None:
    assert duration_p95([]) == 0.0
    assert duration_p95([0.5]) == 0.5
    assert duration_p95([0.2, 0.4, 0.6, 0.8, 1.0]) == 1.0


def test_validate_ledger_rejects_schema_version_mismatch() -> None:
    payload = {
        "schema_version": "observability_v0",
        "run_id": "local",
        "week": "2026-W21",
        "timestamp": "2026-05-20T12:00:00Z",
        "crawl_metrics": [],
        "environment": {},
    }

    errors = validate_ledger(payload)
    assert any(e.startswith("schema_version") for e in errors), (
        f"Expected schema_version error, got: {errors}"
    )


def test_emit_ledger_writes_valid_json() -> None:
    tests_root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
        output_path = Path(tmpdir) / "observability.json"
        emit_ledger(sample_ledger(), output_path)

        payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == METRICS_SCHEMA_VERSION
    assert payload["analysis_metrics"]["reduce_stage"]["status"] == "fail"
    assert validate_ledger(payload) == []


def test_representative_fixture_is_valid() -> None:
    fixture_path = (
        Path(__file__).resolve().parent / "fixtures" / "observability" / "2026-W21-full-run.json"
    )
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    assert validate_ledger(payload) == []
    assert payload["environment"]["pass_fail_counts"]["reduce_fail"] == 1

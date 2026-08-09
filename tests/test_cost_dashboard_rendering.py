"""BR-009: About page cost-dashboard rendering against the reconciled schema."""

from __future__ import annotations

import json
import shutil
import subprocess
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Iterator

import pytest

ROOT = Path(__file__).resolve().parents[1]
COST_SUMMARY_PATH = ROOT / "data/metrics/cost-summary.json"

VALID_SUMMARY = {
    "schema_version": "1.0.0",
    "generated_at": "REPLACED",
    "currency": "USD",
    "pricing_basis": "scripts.track_token_usage.MODEL_PRICING_USD_PER_MILLION",
    "provenance": {
        "ledger": "data/metrics/token-usage.jsonl",
        "legacy_policy": "exclude-unidentified",
        "maximum_age_days": 30,
    },
    "covered_period": {
        "start": "2026-W31",
        "end": "2026-W32",
        "latest_record_at": "REPLACED",
    },
    "accepted_identities": [
        {
            "workflow_run_id": "998877",
            "stage": "analysis",
            "run_attempt": 2,
            "week": "2026-W32",
            "model": "gpt-5-mini",
        }
    ],
    "exclusions": {"legacy_unidentified": 12, "superseded_attempts": 1, "model_none": 0},
    "reconciliation": {
        "status": "reconciled",
        "input_records": 14,
        "accepted_records": 1,
        "billable_records": 1,
    },
    "totals": {"cost": 0.42, "input_tokens": 12345, "output_tokens": 678},
}

LEGACY_SUMMARY = {
    "weeks": [{"week": "2026-W19", "cost": 0.32, "tokens_in": 82000, "tokens_out": 3500}],
    "cumulative_cost": 0.95,
    "budget_limit": 10.0,
}


@contextmanager
def cost_summary_fixture(payload: object | None) -> Iterator[None]:
    """Temporarily replace data/metrics/cost-summary.json, restoring its prior state afterward."""
    original = COST_SUMMARY_PATH.read_bytes() if COST_SUMMARY_PATH.exists() else None
    if payload is not None:
        COST_SUMMARY_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        COST_SUMMARY_PATH.unlink(missing_ok=True)
    try:
        yield
    finally:
        if original is not None:
            COST_SUMMARY_PATH.write_bytes(original)
        else:
            COST_SUMMARY_PATH.unlink(missing_ok=True)


def _build_about_page(destination: Path) -> str:
    result = subprocess.run(
        ["hugo", "--minify", "--quiet", "--destination", str(destination)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return (destination / "about/index.html").read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def _require_hugo() -> None:
    if shutil.which("hugo") is None:
        pytest.skip("Hugo binary is required to render the cost dashboard")


def test_about_page_shows_unavailable_when_cost_summary_missing(tmp_path: Path) -> None:
    with cost_summary_fixture(None):
        rendered = _build_about_page(tmp_path / "public")
    assert "Cost data is not currently available" in rendered
    assert "cumulative_cost" not in rendered
    assert "budget_limit" not in rendered


def test_about_page_renders_reconciled_summary_when_valid(tmp_path: Path) -> None:
    now = datetime.now(UTC).replace(microsecond=0)
    payload = json.loads(json.dumps(VALID_SUMMARY))
    payload["generated_at"] = now.isoformat().replace("+00:00", "Z")
    payload["covered_period"]["latest_record_at"] = now.isoformat().replace("+00:00", "Z")

    with cost_summary_fixture(payload):
        rendered = _build_about_page(tmp_path / "public")

    assert "Cost data is not currently available" not in rendered
    assert "0.42" in rendered
    assert "USD" in rendered
    assert "2026-W31" in rendered and "2026-W32" in rendered
    assert "exclude-unidentified" not in rendered  # internal policy value, not user-facing copy
    assert "data/metrics/token-usage.jsonl" in rendered
    assert "gpt-5-mini" in rendered
    assert "998877" in rendered


def test_about_page_shows_unavailable_for_legacy_schema(tmp_path: Path) -> None:
    with cost_summary_fixture(LEGACY_SUMMARY):
        rendered = _build_about_page(tmp_path / "public")
    assert "Cost data is not currently available" in rendered


def test_about_page_shows_unavailable_for_stale_generated_at(tmp_path: Path) -> None:
    stale = datetime.now(UTC).replace(microsecond=0) - timedelta(days=45)
    payload = json.loads(json.dumps(VALID_SUMMARY))
    payload["generated_at"] = stale.isoformat().replace("+00:00", "Z")
    payload["covered_period"]["latest_record_at"] = stale.isoformat().replace("+00:00", "Z")

    with cost_summary_fixture(payload):
        rendered = _build_about_page(tmp_path / "public")

    assert "Cost data is not currently available" in rendered
    assert "0.42" not in rendered


def test_about_page_shows_unavailable_when_nested_field_missing(tmp_path: Path) -> None:
    """A present top-level key with a missing required sub-field must fail closed too."""
    now = datetime.now(UTC).replace(microsecond=0)
    payload = json.loads(json.dumps(VALID_SUMMARY))
    payload["generated_at"] = now.isoformat().replace("+00:00", "Z")
    payload["covered_period"]["latest_record_at"] = now.isoformat().replace("+00:00", "Z")
    del payload["totals"]["cost"]

    with cost_summary_fixture(payload):
        rendered = _build_about_page(tmp_path / "public")

    assert "Cost data is not currently available" in rendered
    assert "<no value>" not in rendered
    assert "0.00" not in rendered


def test_about_page_shows_unavailable_for_future_generated_at(tmp_path: Path) -> None:
    """A future generated_at is not a valid freshness signal and must fail closed."""
    future = datetime.now(UTC).replace(microsecond=0) + timedelta(days=1)
    payload = json.loads(json.dumps(VALID_SUMMARY))
    payload["generated_at"] = future.isoformat().replace("+00:00", "Z")
    payload["covered_period"]["latest_record_at"] = future.isoformat().replace("+00:00", "Z")

    with cost_summary_fixture(payload):
        rendered = _build_about_page(tmp_path / "public")

    assert "Cost data is not currently available" in rendered
    assert "0.42" not in rendered


def test_about_page_shows_unavailable_for_non_string_generated_at(tmp_path: Path) -> None:
    """A malformed (non-string) generated_at must fail closed, not error the build."""
    payload = json.loads(json.dumps(VALID_SUMMARY))
    payload["generated_at"] = 12345
    payload["covered_period"]["latest_record_at"] = 12345

    with cost_summary_fixture(payload):
        rendered = _build_about_page(tmp_path / "public")

    assert "Cost data is not currently available" in rendered
    assert "0.42" not in rendered


def test_about_page_shows_unavailable_when_accepted_identity_malformed(tmp_path: Path) -> None:
    """An accepted identity missing a required key must fail closed, not render <no value>."""
    now = datetime.now(UTC).replace(microsecond=0)
    payload = json.loads(json.dumps(VALID_SUMMARY))
    payload["generated_at"] = now.isoformat().replace("+00:00", "Z")
    payload["covered_period"]["latest_record_at"] = now.isoformat().replace("+00:00", "Z")
    del payload["accepted_identities"][0]["model"]

    with cost_summary_fixture(payload):
        rendered = _build_about_page(tmp_path / "public")

    assert "Cost data is not currently available" in rendered
    assert "<no value>" not in rendered


def test_about_page_shows_unavailable_when_root_is_not_an_object(tmp_path: Path) -> None:
    """A malformed (non-object) root payload must fail closed, not error the build."""
    with cost_summary_fixture([1, 2, 3]):
        rendered = _build_about_page(tmp_path / "public")

    assert "Cost data is not currently available" in rendered


def test_about_page_shows_unavailable_for_non_numeric_maximum_age_days(tmp_path: Path) -> None:
    """A non-numeric maximum_age_days must fail closed, not error int() and the build."""
    now = datetime.now(UTC).replace(microsecond=0)
    payload = json.loads(json.dumps(VALID_SUMMARY))
    payload["generated_at"] = now.isoformat().replace("+00:00", "Z")
    payload["covered_period"]["latest_record_at"] = now.isoformat().replace("+00:00", "Z")
    payload["provenance"]["maximum_age_days"] = "not-a-number"

    with cost_summary_fixture(payload):
        rendered = _build_about_page(tmp_path / "public")

    assert "Cost data is not currently available" in rendered


def test_about_page_shows_unavailable_when_generated_at_is_an_object(tmp_path: Path) -> None:
    """A generated_at shaped as an object must fail closed, not error string() and the build."""
    payload = json.loads(json.dumps(VALID_SUMMARY))
    payload["generated_at"] = {"unexpected": "shape"}

    with cost_summary_fixture(payload):
        rendered = _build_about_page(tmp_path / "public")

    assert "Cost data is not currently available" in rendered

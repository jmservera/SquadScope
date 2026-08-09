"""Schema-conformance contracts for every public JSON artifact (BRD Phase 1).

Each public JSON contract under ``data/schemas/`` must have a representative
fixture that validates successfully, a malformed variant that is rejected, and
(where the schema declares a ``schema_version``) a future-version variant that
is rejected. This closes the Claracle post-relaunch consolidation Phase 1 item:
"Add documented schemas, representative fixtures, deterministic-generation
checks, and future-version rejection for every public JSON contract."
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts import generate_cost_summary as cost_summary
from scripts import generate_repository_url_inventory as repo_inventory
from scripts import generate_yearly_evidence_pack as yearly_evidence

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "data" / "schemas"


def _load_schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def _validate(payload: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(
        payload
    )


# ---------------------------------------------------------------------------
# Repository URL inventory (BR-003)
# ---------------------------------------------------------------------------


def _write_page(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\ntitle: Example\n---\n\nBody\n", encoding="utf-8")


def _repository_url_inventory_fixture(tmp_path: Path) -> dict[str, Any]:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(tmp_path / "content/repo/alpha/index.md")
    return repo_inventory.build_inventory(tmp_path)


def test_repository_url_inventory_matches_schema(tmp_path: Path) -> None:
    schema = _load_schema("repository-url-inventory.schema.json")

    _validate(_repository_url_inventory_fixture(tmp_path), schema)


def test_repository_url_inventory_rejects_malformed_record(tmp_path: Path) -> None:
    schema = _load_schema("repository-url-inventory.schema.json")
    payload = _repository_url_inventory_fixture(tmp_path)
    del payload["records"][0]["source_checksum"]

    with pytest.raises(ValidationError):
        _validate(payload, schema)


def test_repository_url_inventory_rejects_future_schema_version(tmp_path: Path) -> None:
    schema = _load_schema("repository-url-inventory.schema.json")
    payload = _repository_url_inventory_fixture(tmp_path)
    payload["schema_version"] = "2.0.0"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


# ---------------------------------------------------------------------------
# Cost summary (BR-009)
# ---------------------------------------------------------------------------


def _cost_summary_fixture() -> dict[str, Any]:
    record = {
        "timestamp": "2026-08-07T12:00:00Z",
        "week": "2026-W32",
        "stage": "analysis",
        "model": "gpt-5-mini",
        "input_tokens": 100,
        "output_tokens": 20,
        "cost_usd": 0.25,
        "workflow_run_id": "100",
        "run_attempt": 1,
    }
    return cost_summary.build_projection([record], generated_at=datetime(2026, 8, 8, tzinfo=UTC))


def test_cost_summary_matches_schema() -> None:
    schema = _load_schema("cost-summary.schema.json")

    _validate(_cost_summary_fixture(), schema)


def test_cost_summary_rejects_malformed_totals() -> None:
    schema = _load_schema("cost-summary.schema.json")
    payload = _cost_summary_fixture()
    del payload["totals"]["cost"]

    with pytest.raises(ValidationError):
        _validate(payload, schema)


def test_cost_summary_rejects_future_schema_version() -> None:
    schema = _load_schema("cost-summary.schema.json")
    payload = _cost_summary_fixture()
    payload["schema_version"] = "1.1.0"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


def test_cost_summary_rejects_non_rfc3339_generated_at() -> None:
    """Guards against Draft202012Validator silently skipping "format" checks."""
    schema = _load_schema("cost-summary.schema.json")
    payload = _cost_summary_fixture()
    payload["generated_at"] = "not-a-timestamp"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


# ---------------------------------------------------------------------------
# Yearly evidence pack (BR-006)
# ---------------------------------------------------------------------------


def _yearly_evidence_pack_fixture() -> dict[str, Any]:
    pack = {
        "synthesis_version": "1",
        "month": "2026-05",
        "weeks_covered": ["2026-W21"],
        "weeks": [
            {
                "week": "2026-W21",
                "title": "Week 21",
                "summary": "A complete summary.",
                "top_repo": "octo/repo",
                "tags": ["agents"],
                "signal": "A complete signal.",
                "noise": "A complete noise finding.",
                "gaps": "A complete gap.",
                "conclusion": "A complete conclusion.",
            }
        ],
    }
    return yearly_evidence.build_yearly_evidence_pack(2026, [pack])


def test_yearly_evidence_pack_matches_schema() -> None:
    schema = _load_schema("yearly-evidence-pack.schema.json")

    _validate(_yearly_evidence_pack_fixture(), schema)


def test_yearly_evidence_pack_rejects_malformed_claim() -> None:
    schema = _load_schema("yearly-evidence-pack.schema.json")
    payload = _yearly_evidence_pack_fixture()
    payload["claims"][0]["claim_type"] = "unsupported"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


def test_yearly_evidence_pack_rejects_future_schema_version() -> None:
    schema = _load_schema("yearly-evidence-pack.schema.json")
    payload = _yearly_evidence_pack_fixture()
    payload["schema_version"] = "2.0.0"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


# ---------------------------------------------------------------------------
# Observatory envelope (BR-003, BR-004)
# ---------------------------------------------------------------------------


def _observatory_envelope_fixture(artifact_type: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "artifact_type": artifact_type,
        "generated_at": "2026-08-08T00:00:00Z",
        "covered_period": {"start": "2026-08-01", "end": "2026-08-08", "label": "Week 32, 2026"},
        "provenance": {
            "generator": "scripts.generate_data_pages",
            "source_paths": ["data/derived/observatory"],
            "methodology_url": "/methodology/",
        },
        "records": [],
    }


@pytest.mark.parametrize("artifact_type", ["repositories", "ranking"])
def test_observatory_envelope_matches_schema(artifact_type: str) -> None:
    schema = _load_schema("observatory-envelope.schema.json")

    _validate(_observatory_envelope_fixture(artifact_type), schema)


def test_observatory_envelope_rejects_unknown_artifact_type() -> None:
    schema = _load_schema("observatory-envelope.schema.json")
    payload = _observatory_envelope_fixture("repositories")
    payload["artifact_type"] = "leaderboards"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


def test_observatory_envelope_rejects_future_schema_version() -> None:
    schema = _load_schema("observatory-envelope.schema.json")
    payload = _observatory_envelope_fixture("repositories")
    payload["schema_version"] = "2.0.0"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


# ---------------------------------------------------------------------------
# Ranking record (BR-004)
# ---------------------------------------------------------------------------


def _ranking_record_fixture() -> dict[str, Any]:
    return {
        "rank": 1,
        "repository_id": "octo-repo",
        "full_name": "octo/repo",
        "github_url": "https://github.com/octo/repo",
        "metric_key": "stars",
        "metric_value": 4200,
        "metric_label": "4,200 stars",
        "comparison_value": 3800,
        "comparison_label": "3,800 stars last period",
        "context_summary": "octo/repo gained the most stars this period.",
    }


def test_ranking_record_matches_schema() -> None:
    schema = _load_schema("ranking-record.schema.json")

    _validate(_ranking_record_fixture(), schema)


def test_ranking_record_rejects_unsupported_metric_key() -> None:
    schema = _load_schema("ranking-record.schema.json")
    payload = _ranking_record_fixture()
    payload["metric_key"] = "forks"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


def test_ranking_record_rejects_oversized_context_summary() -> None:
    schema = _load_schema("ranking-record.schema.json")
    payload = _ranking_record_fixture()
    payload["context_summary"] = "x" * 241

    with pytest.raises(ValidationError):
        _validate(payload, schema)


# ---------------------------------------------------------------------------
# Repository record (BR-003)
# ---------------------------------------------------------------------------


def _repository_record_fixture() -> dict[str, Any]:
    return {
        "id": "octo-repo",
        "full_name": "octo/repo",
        "name": "repo",
        "owner": "octo",
        "github_url": "https://github.com/octo/repo",
        "language": "Python",
        "topics": ["agents", "ai"],
        "status": "active",
        "first_seen_period": "2026-W01",
        "last_seen_period": "2026-W32",
        "recent_momentum": 12.5,
        "context_summary": "octo/repo is a Python agent framework tracked since week 1.",
        "star_history": [{"period": "2026-W32", "stars": 4200, "delta": 400}],
    }


def test_repository_record_matches_schema() -> None:
    schema = _load_schema("repository-record.schema.json")

    _validate(_repository_record_fixture(), schema)


def test_repository_record_rejects_unsupported_status() -> None:
    schema = _load_schema("repository-record.schema.json")
    payload = _repository_record_fixture()
    payload["status"] = "unknown"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


def test_repository_record_rejects_malformed_star_history() -> None:
    schema = _load_schema("repository-record.schema.json")
    payload = _repository_record_fixture()
    del payload["star_history"][0]["delta"]

    with pytest.raises(ValidationError):
        _validate(payload, schema)


# ---------------------------------------------------------------------------
# Embed summary (BR-007)
# ---------------------------------------------------------------------------


def _embed_summary_fixture() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "repository_id": "octo-repo",
        "full_name": "octo/repo",
        "github_url": "https://github.com/octo/repo",
        "sanitized_summary": "octo/repo is a Python agent framework tracked since week 1.",
        "accessible_text": "octo/repo is a Python agent framework tracked since week 1.",
        "sanitization_source": "scripts.sanitize_repo_content.sanitize_text",
    }


def test_embed_summary_matches_schema() -> None:
    schema = _load_schema("embed-summary.schema.json")

    _validate(_embed_summary_fixture(), schema)


def test_embed_summary_rejects_oversized_display_summary() -> None:
    schema = _load_schema("embed-summary.schema.json")
    payload = _embed_summary_fixture()
    payload["sanitized_summary"] = "x" * 161

    with pytest.raises(ValidationError):
        _validate(payload, schema)


def test_embed_summary_rejects_unsafe_github_url() -> None:
    schema = _load_schema("embed-summary.schema.json")
    payload = _embed_summary_fixture()
    payload["github_url"] = "javascript:alert(1)"

    with pytest.raises(ValidationError):
        _validate(payload, schema)


def test_embed_summary_rejects_future_schema_version() -> None:
    schema = _load_schema("embed-summary.schema.json")
    payload = _embed_summary_fixture()
    payload["schema_version"] = "2.0.0"

    with pytest.raises(ValidationError):
        _validate(payload, schema)

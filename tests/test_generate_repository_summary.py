from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import generate_repository_summary as summary


def _source_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "date": "2026-08-03",
        "repo_slug": "example-tool",
        "repo_full_name": "example/tool",
        "repo_name": "tool",
        "repo_owner": "example",
        "repo_url": "https://github.com/example/tool",
        "repo_description": "A useful <strong>developer</strong> tool.",
        "repo_language": "Python",
        "tags": ["tools", "ai", "tools"],
        "first_seen_week": "2026-W21",
        "last_seen_week": "2026-W32",
        "lifecycle": {"status": "active"},
        "star_history": [
            {"week": "2026-W29", "stars": 100, "delta": None},
            {"week": "2026-W30", "stars": 110, "delta": 10},
            {"week": "2026-W31", "stars": 125, "delta": 15},
            {"week": "2026-W32", "stars": 145, "delta": 20},
        ],
    }
    record.update(overrides)
    return record


def _write_source(root: Path, records: list[dict[str, object]]) -> None:
    path = root / summary.SOURCE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records), encoding="utf-8")


def test_build_payload_is_versioned_sanitized_and_deterministic(tmp_path: Path) -> None:
    _write_source(tmp_path, [_source_record()])

    first = summary.build_payload(tmp_path)
    second = summary.build_payload(tmp_path)

    assert first == second
    assert first["schema_version"] == "1.0.0"
    assert first["artifact_type"] == "repositories"
    assert first["generated_at"] == "2026-08-03T00:00:00Z"
    assert first["covered_period"] == {
        "start": "2026-05-18",
        "end": "2026-08-09",
        "label": "2026-W21–2026-W32",
    }
    record = first["records"][0]
    assert record["topics"] == ["ai", "tools"]
    assert record["context_summary"] == "A useful developer tool."
    assert record["recent_momentum"] == 45
    assert record["star_history"][-1] == {
        "period": "2026-W32",
        "stars": 145,
        "delta": 20,
    }


def test_records_default_to_recent_momentum_order(tmp_path: Path) -> None:
    _write_source(
        tmp_path,
        [
            _source_record(repo_slug="slow", repo_full_name="example/slow"),
            _source_record(
                repo_slug="fast",
                repo_full_name="example/fast",
                star_history=[
                    {"week": "2026-W31", "stars": 100, "delta": None},
                    {"week": "2026-W32", "stars": 200, "delta": 100},
                ],
            ),
        ],
    )

    records = summary.build_payload(tmp_path)["records"]

    assert [record["id"] for record in records] == ["fast", "slow"]


def test_non_github_repository_url_is_rejected(tmp_path: Path) -> None:
    _write_source(tmp_path, [_source_record(repo_url="https://example.com/tool")])

    with pytest.raises(ValueError, match="https://github.com"):
        summary.build_payload(tmp_path)


def test_build_payload_rejects_empty_source(tmp_path: Path) -> None:
    _write_source(tmp_path, [])

    with pytest.raises(ValueError, match="non-empty list"):
        summary.build_payload(tmp_path)


def test_check_mode_requires_both_outputs(tmp_path: Path) -> None:
    _write_source(tmp_path, [_source_record()])
    rendered = summary.rendered_payload(tmp_path)
    first = tmp_path / summary.DEFAULT_OUTPUTS[0]
    first.parent.mkdir(parents=True, exist_ok=True)
    first.write_text(rendered, encoding="utf-8")

    with pytest.raises(SystemExit, match="static/data/repositories.json"):
        summary.main(["--root", str(tmp_path), "--check"])


def test_long_context_summary_stays_bounded(tmp_path: Path) -> None:
    _write_source(tmp_path, [_source_record(repo_description="word " * 100)])

    record = summary.build_payload(tmp_path)["records"][0]

    assert len(record["context_summary"]) <= 240
    assert record["context_summary"].endswith("…")

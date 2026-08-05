from __future__ import annotations

import json
from pathlib import Path

from scripts.summarize_identity_backfill import summarize


def test_summarize_counts_each_status(tmp_path: Path) -> None:
    path = tmp_path / "repo-identity-backfill.json"
    path.write_text(
        json.dumps(
            {
                "entries": {
                    "octo/a": {"status": "found"},
                    "octo/b": {"status": "found"},
                    "octo/c": {"status": "not_found"},
                    "octo/d": {"status": "error"},
                }
            }
        ),
        encoding="utf-8",
    )

    output = summarize(path)

    assert "total entries: 4" in output
    assert "found: 2" in output
    assert "not_found: 1" in output
    assert "error: 1" in output


def test_summarize_tolerates_missing_or_non_string_status(tmp_path: Path) -> None:
    path = tmp_path / "repo-identity-backfill.json"
    path.write_text(
        json.dumps(
            {
                "entries": {
                    "octo/no-status": {},
                    "octo/null-status": {"status": None},
                    "octo/not-a-dict": "unexpected",
                    "octo/found": {"status": "found"},
                }
            }
        ),
        encoding="utf-8",
    )

    output = summarize(path)

    assert "total entries: 4" in output
    assert "found: 1" in output
    assert "unknown: 3" in output

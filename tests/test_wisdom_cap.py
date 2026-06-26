"""Tests for scripts/wisdom_cap.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.wisdom_cap import (
    main,
    parse_heuristics,
    retire_heuristics,
    select_for_retirement,
)

SAMPLE_WISDOM = """\
# Topic Wisdom

## Signal Patterns
- Heuristic one about signals
- Heuristic two about patterns
- Heuristic three about growth

## Noise Patterns
- Noise heuristic one
- Noise heuristic two

## Scoring Adjustments
- Scoring rule one
- Scoring rule two
- Scoring rule three
"""


class TestParseHeuristics:
    def test_parses_all_bullets(self):
        heuristics = parse_heuristics(SAMPLE_WISDOM)
        assert len(heuristics) == 8

    def test_captures_sections(self):
        heuristics = parse_heuristics(SAMPLE_WISDOM)
        sections = {h["section"] for h in heuristics}
        assert "Signal Patterns" in sections
        assert "Noise Patterns" in sections

    def test_empty_content(self):
        assert parse_heuristics("") == []
        assert parse_heuristics("# Just a header\n") == []


class TestSelectForRetirement:
    def test_selects_from_end(self):
        heuristics = parse_heuristics(SAMPLE_WISDOM)
        retired = select_for_retirement(heuristics, bytes_to_free=50)
        # Should select from the end
        assert retired[0]["text"] == "- Scoring rule three"

    def test_respects_bytes_needed(self):
        heuristics = parse_heuristics(SAMPLE_WISDOM)
        retired = select_for_retirement(heuristics, bytes_to_free=1)
        assert len(retired) >= 1


class TestRetireHeuristics:
    def test_under_limit_no_action(self, tmp_path):
        wisdom = tmp_path / "wisdom.md"
        archive = tmp_path / "archive.md"
        wisdom.write_text(SAMPLE_WISDOM)

        result = retire_heuristics(wisdom, archive, limit=10000)
        assert result["status"] == "ok"
        assert not archive.exists()

    def test_over_limit_retires(self, tmp_path):
        wisdom = tmp_path / "wisdom.md"
        archive = tmp_path / "archive.md"
        wisdom.write_text(SAMPLE_WISDOM)
        # Set limit below current size to trigger retirement
        current_size = len(SAMPLE_WISDOM.encode("utf-8"))
        limit = current_size - 50

        result = retire_heuristics(wisdom, archive, limit=limit)
        assert result["status"] == "retired"
        assert result["retired_count"] >= 1
        assert archive.exists()
        # Wisdom should be smaller now
        new_size = len(wisdom.read_text().encode("utf-8"))
        assert new_size < current_size

    def test_dry_run_no_changes(self, tmp_path):
        wisdom = tmp_path / "wisdom.md"
        archive = tmp_path / "archive.md"
        wisdom.write_text(SAMPLE_WISDOM)
        limit = 50  # Way under to force retirement

        result = retire_heuristics(wisdom, archive, limit=limit, dry_run=True)
        assert result["status"] == "dry_run"
        assert result["would_retire"] > 0
        # File should be unchanged
        assert wisdom.read_text() == SAMPLE_WISDOM
        assert not archive.exists()

    def test_missing_wisdom(self, tmp_path):
        wisdom = tmp_path / "nope.md"
        archive = tmp_path / "archive.md"
        result = retire_heuristics(wisdom, archive, limit=5120)
        assert result["status"] == "skip"

    def test_idempotent(self, tmp_path):
        """Running twice produces same result if already under limit."""
        wisdom = tmp_path / "wisdom.md"
        archive = tmp_path / "archive.md"
        wisdom.write_text(SAMPLE_WISDOM)
        limit = len(SAMPLE_WISDOM.encode("utf-8")) - 50

        retire_heuristics(wisdom, archive, limit=limit)
        content_after_first = wisdom.read_text()

        # Running again should be ok (under limit now)
        result = retire_heuristics(wisdom, archive, limit=limit)
        assert result["status"] == "ok"
        assert wisdom.read_text() == content_after_first

    def test_archive_appends(self, tmp_path):
        """Multiple retirements append to archive, never overwrite."""
        wisdom = tmp_path / "wisdom.md"
        archive = tmp_path / "archive.md"
        wisdom.write_text(SAMPLE_WISDOM)

        # First retirement
        retire_heuristics(wisdom, archive, limit=50)
        first_archive = archive.read_text()

        # Add more content and retire again
        current = wisdom.read_text()
        wisdom.write_text(current + "- New heuristic added\n" * 20)
        retire_heuristics(wisdom, archive, limit=50)
        second_archive = archive.read_text()

        assert len(second_archive) > len(first_archive)


class TestMainCLI:
    def test_runs_with_missing_topic(self, tmp_path, monkeypatch):
        monkeypatch.setattr("scripts.wisdom_cap.SQUAD_DIR", tmp_path / ".squad" / "topics")
        rc = main(["--topic", "nonexistent"])
        assert rc == 0  # graceful skip

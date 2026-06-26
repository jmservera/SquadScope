"""Tests for scripts/context_budget.py."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.context_budget import (
    assemble_historical_context,
    compress_stale_trends,
    compress_to_budget,
    keep_top_noise_patterns,
    prune_stale_predictions,
    word_count,
)

# --- word_count tests ---


class TestWordCount:
    def test_empty_string(self):
        assert word_count("") == 0

    def test_single_word(self):
        assert word_count("hello") == 1

    def test_multiple_words(self):
        assert word_count("one two three four five") == 5

    def test_multiline(self):
        text = "line one\nline two\nline three"
        assert word_count(text) == 6

    def test_extra_whitespace(self):
        assert word_count("  hello   world  ") == 2


# --- compress_to_budget tests ---


class TestCompressToBudget:
    def test_empty_text(self):
        assert compress_to_budget("", 100) == ""

    def test_whitespace_only(self):
        assert compress_to_budget("   \n  ", 100) == ""

    def test_within_budget(self):
        text = "This is a short sentence."
        result = compress_to_budget(text, 100)
        assert result == text.strip()
        assert word_count(result) <= 100

    def test_exceeds_budget_truncates(self):
        text = " ".join(f"word{i}" for i in range(100))
        result = compress_to_budget(text, 10)
        assert word_count(result) <= 11  # 10 + possible trailing "..."
        assert result.endswith("...")

    def test_zero_budget(self):
        assert compress_to_budget("hello world", 0) == ""

    def test_negative_budget(self):
        assert compress_to_budget("hello world", -5) == ""

    def test_preserves_line_structure(self):
        text = "line one two\nline three four five\nline six seven eight nine ten"
        result = compress_to_budget(text, 5)
        # Should keep first line (3 words) and partial of second
        assert word_count(result) <= 6  # budget + trailing word
        assert "..." in result or word_count(result) <= 5

    def test_budget_enforcement_strict(self):
        text = " ".join(["word"] * 1000)
        result = compress_to_budget(text, 50)
        # Word count should not greatly exceed budget
        assert word_count(result) <= 51


# --- prune_stale_predictions tests ---


class TestPruneStale:
    def test_drops_old_unconfirmed(self):
        now = datetime(2026, 6, 12, tzinfo=timezone.utc)
        text = "- [2026-03-01] prediction about AI growth\n- [2026-06-01] recent prediction"
        result = prune_stale_predictions(text, now=now)
        assert "2026-03-01" not in result
        assert "2026-06-01" in result

    def test_keeps_confirmed(self):
        now = datetime(2026, 6, 12, tzinfo=timezone.utc)
        text = "- [2026-01-01] old but confirmed ✓"
        result = prune_stale_predictions(text, now=now)
        assert "2026-01-01" in result

    def test_keeps_recent(self):
        now = datetime(2026, 6, 12, tzinfo=timezone.utc)
        recent = (now - timedelta(weeks=2)).strftime("%Y-%m-%d")
        text = f"- [{recent}] recent prediction"
        result = prune_stale_predictions(text, now=now)
        assert recent in result

    def test_empty_text(self):
        assert prune_stale_predictions("") == ""


# --- compress_stale_trends tests ---


class TestCompressStaleTrends:
    def test_compresses_stale_trend(self):
        now = datetime(2026, 6, 12, tzinfo=timezone.utc)
        text = (
            "## Trend: Blockchain hype\n"
            "- [2026-01-01] some old signal\n"
            "- [2026-01-15] another old signal\n"
        )
        result = compress_stale_trends(text, now=now)
        assert "Blockchain hype: no recent signal" in result
        assert "some old signal" not in result

    def test_keeps_active_trend(self):
        now = datetime(2026, 6, 12, tzinfo=timezone.utc)
        recent = (now - timedelta(days=5)).strftime("%Y-%m-%d")
        text = f"## Trend: AI growth\n- [{recent}] strong signal this week\n"
        result = compress_stale_trends(text, now=now)
        assert "strong signal this week" in result

    def test_empty_text(self):
        assert compress_stale_trends("") == ""


# --- keep_top_noise_patterns tests ---


class TestNoisePatterns:
    def test_keeps_only_top_n(self):
        text = (
            "## Noise\n"
            "- noise pattern 1\n"
            "- noise pattern 2\n"
            "- noise pattern 3\n"
            "- noise pattern 4\n"
            "- noise pattern 5\n"
        )
        result = keep_top_noise_patterns(text, max_patterns=3)
        assert "noise pattern 1" in result
        assert "noise pattern 2" in result
        assert "noise pattern 3" in result
        assert "noise pattern 4" not in result
        assert "noise pattern 5" not in result

    def test_fewer_than_max(self):
        text = "## Noise\n- pattern 1\n- pattern 2\n"
        result = keep_top_noise_patterns(text, max_patterns=3)
        assert "pattern 1" in result
        assert "pattern 2" in result

    def test_non_noise_sections_untouched(self):
        text = "## Signals\n- sig 1\n- sig 2\n- sig 3\n- sig 4\n- sig 5\n"
        result = keep_top_noise_patterns(text, max_patterns=3)
        assert "sig 5" in result  # Not filtered


# --- assemble_historical_context tests ---


class TestAssemble:
    def test_assembles_from_files(self, tmp_path):
        rolling = tmp_path / "rolling.md"
        yearly = tmp_path / "yearly.md"
        prev_week = tmp_path / "prev_week.md"

        rolling.write_text("Rolling context with some words here today.")
        yearly.write_text("Yearly summary of important events and trends.")
        prev_week.write_text("Last week's highlights and observations.")

        result = assemble_historical_context(
            rolling_path=str(rolling),
            yearly_path=str(yearly),
            prev_week_path=str(prev_week),
            max_total_words=1500,
        )

        assert "## Rolling Context" in result
        assert "## Yearly Context" in result
        assert "## Previous Week" in result

    def test_handles_missing_files(self, tmp_path):
        result = assemble_historical_context(
            rolling_path=str(tmp_path / "nonexistent.md"),
            yearly_path=None,
            prev_week_path=None,
            max_total_words=1500,
        )
        # Should not crash, returns empty or partial
        assert isinstance(result, str)

    def test_all_none_paths(self):
        result = assemble_historical_context(
            rolling_path=None,
            yearly_path=None,
            prev_week_path=None,
            max_total_words=1500,
        )
        assert result == ""

    def test_budget_enforcement(self, tmp_path):
        # Create a large file that exceeds budget
        large_text = " ".join(["word"] * 2000)
        rolling = tmp_path / "rolling.md"
        rolling.write_text(large_text)

        yearly = tmp_path / "yearly.md"
        yearly.write_text(large_text)

        result = assemble_historical_context(
            rolling_path=str(rolling),
            yearly_path=str(yearly),
            max_total_words=100,
        )
        # Total words should respect the budget (with small margin for headers)
        assert word_count(result) <= 110

    def test_output_is_markdown(self, tmp_path):
        rolling = tmp_path / "rolling.md"
        rolling.write_text("Some rolling context data points here.")

        result = assemble_historical_context(
            rolling_path=str(rolling),
            max_total_words=1500,
        )
        # Should contain markdown headers
        assert result.startswith("## ")

    def test_budget_allocation_scaling(self, tmp_path):
        """Verify budgets scale proportionally with max_total_words."""
        text = " ".join(["word"] * 1000)
        rolling = tmp_path / "rolling.md"
        rolling.write_text(text)

        # With max_total_words=750 (half of default 1500),
        # rolling budget should be ~250 (half of 500)
        result = assemble_historical_context(
            rolling_path=str(rolling),
            max_total_words=750,
        )
        # Section content should be roughly half the default rolling budget
        content = result.replace("## Rolling Context\n\n", "")
        assert word_count(content) <= 280  # ~250 + margin

    def test_pruning_applied_during_assembly(self, tmp_path):
        now = datetime(2026, 6, 12, tzinfo=timezone.utc)
        rolling = tmp_path / "rolling.md"
        rolling.write_text(
            "- [2026-01-01] stale prediction from January\n"
            "- [2026-06-10] fresh prediction from this week\n"
        )

        result = assemble_historical_context(
            rolling_path=str(rolling),
            max_total_words=1500,
            now=now,
        )
        assert "2026-01-01" not in result
        assert "2026-06-10" in result

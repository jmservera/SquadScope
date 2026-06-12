from __future__ import annotations

from pathlib import Path

from scripts.assemble_historical_context import (
    DEFAULT_PROMPT_BUDGET_FRACTION,
    assemble_historical_context,
    build_historical_context,
    compress_to_budget,
    estimate_tokens,
)


def test_assemble_historical_context_reads_expected_sources(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    (content_root / "rolling").mkdir(parents=True)
    (content_root / "monthly" / "2026").mkdir(parents=True)
    (content_root / "yearly").mkdir(parents=True)
    analyzed_dir = tmp_path / "analyzed"
    analyzed_dir.mkdir()

    (content_root / "rolling" / "last-month.md").write_text(
        "## Active Trends\n\n- Skills keep specializing.\n\n## Noise Patterns\n\n- Spam persists.\n",
        encoding="utf-8",
    )
    (content_root / "monthly" / "2026" / "06.md").write_text(
        "---\nsummary: month\n---\n"
        "## Month Overview\n\nJune overview.\n\n"
        "## Trends Observed\n\nJune trends.\n\n"
        "## Key Takeaways\n\nJune takeaways.\n",
        encoding="utf-8",
    )
    (content_root / "yearly" / "2026.md").write_text(
        "## Year in Review\n\nYear review.\n\n"
        "## Biggest Trends\n\nYear trends.\n\n"
        "## Predictions Review\n\nYear predictions.\n",
        encoding="utf-8",
    )
    previous_summary = analyzed_dir / "2026-W24-summary.md"
    previous_summary.write_text(
        "---\nsummary: Prior thesis.\n---\n"
        "## Signal & Noise\n\nSignal notes.\n\n"
        "## Blind Spots\n\nBlind-spot notes.\n\n"
        "## The Week Ahead\n\nWatch-list notes.\n",
        encoding="utf-8",
    )

    result = assemble_historical_context(
        current_datetime="2026-06-12T17:13:50+00:00",
        previous_summary_path=previous_summary,
        content_root=content_root,
        max_words=1500,
        prompt_token_budget=90_000,
    )

    assert "### Rolling Last 4 Weeks" in result
    assert "### Previous Week Takeaways" in result
    assert "Prior weekly thesis: Prior thesis." in result
    assert "### Month In Progress" in result
    assert "### Yearly Narrative" in result


def test_build_historical_context_respects_prompt_fraction_cap(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    (content_root / "rolling").mkdir(parents=True)
    (content_root / "rolling" / "last-month.md").write_text(
        " ".join(["rolling-context"] * 800),
        encoding="utf-8",
    )

    result = build_historical_context(
        current_datetime="2026-06-12T17:13:50+00:00",
        previous_summary_path=None,
        content_root=content_root,
        max_words=1500,
        prompt_token_budget=200,
    )

    assert result.token_estimate <= int(200 * DEFAULT_PROMPT_BUDGET_FRACTION)
    assert estimate_tokens(result.markdown) == result.token_estimate


def test_compress_to_budget_preserves_line_structure() -> None:
    text = "## Heading\n\nFirst bullet point here\nSecond bullet point\n\nThird paragraph with many words"
    result = compress_to_budget(text, 8)
    assert "\n" in result

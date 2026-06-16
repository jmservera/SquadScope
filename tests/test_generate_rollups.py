import io
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import scripts.generate_rollups as generate_rollups
import scripts.generate_yearly_narrative as generate_yearly_narrative


WORKSPACE_ROOT = Path(".test-workspaces")


def make_summary(
    *,
    week: str,
    date: str,
    top_repo: str,
    summary: str,
    signal: str,
    noise: str,
    gaps: str,
    conclusion: str,
    tags: tuple[str, ...] = ("ai", "agents", "developer-tooling"),
    repo_mentions: tuple[str, ...] = (),
) -> str:
    year = int(week[:4])
    rendered_tags = ", ".join(tags)
    linked_mentions = " ".join(
        f"[{repo}](https://github.com/{repo}) is part of the weekly conversation." for repo in repo_mentions
    )
    notable_new = f"A fresh set of launches landed. {linked_mentions}".strip()
    return f'''---
title: "Week {int(week[-2:])}, {year} Analysis"
date: {date}
week: "{week}"
year: {year}
tags: [{rendered_tags}]
categories: [weekly]
repos_featured: 10
top_repo: "{top_repo}"
quality_score: 80
summary: "{summary}"
stars_tracked: 1000
---

## This Week's Trends

Trend analysis for {week}. Developer activity concentrated around practical tooling and infrastructure work.

## Where Industry Meets Code

No press data available for this automated test summary. Developer activity tells a coherent story on its own.

## Signal & Noise

{signal} {noise}

## Blind Spots

{gaps}

## The Week Ahead

{conclusion}

## Key References

### Notable Projects

{notable_new}

### Press & Industry

No press data was provided this week.
'''


def temporary_workspace() -> tempfile.TemporaryDirectory[str]:
    WORKSPACE_ROOT.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(dir=WORKSPACE_ROOT.resolve())


class GenerateRollupsTests(unittest.TestCase):
    def test_generate_rollups_creates_monthly_and_yearly_pages(self) -> None:
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            content_root = base / "content"
            analyzed_dir.mkdir(parents=True)

            (analyzed_dir / "2026-W21-summary.md").write_text(
                make_summary(
                    week="2026-W21",
                    date="2026-05-18T12:07:20+00:00",
                    top_repo="octo/signal-kit",
                    summary="Practical agent tooling led the week.",
                    signal="Teams preferred operational automation over generic hype.",
                    noise="Exploit-heavy projects still added editorial noise.",
                    gaps="Reliable momentum data remained missing.",
                    conclusion="The strongest projects made automation safer to adopt.",
                ),
                encoding="utf-8",
            )

            written = generate_rollups.generate_rollups(analyzed_dir, content_root)

            monthly_path = content_root / "monthly" / "2026" / "05.md"
            yearly_path = content_root / "yearly" / "2026.md"
            self.assertEqual(written, [monthly_path, yearly_path])

            monthly = monthly_path.read_text(encoding="utf-8")
            self.assertIn("Define the Month — May 2026", monthly)
            self.assertIn('categories: ["monthly"]', monthly)
            self.assertIn('weeks_covered: ["2026-W21"]', monthly)
            self.assertIn('total_repos_featured: 1', monthly)
            self.assertIn('---\n\n## Month Synthesis', monthly)
            self.assertIn('## Month Overview', monthly)
            self.assertIn('### Week 2026-W21', monthly)
            self.assertIn('[Week 21, 2026](/weekly/2026/W21/)', monthly)
            self.assertIn('[octo/signal-kit](https://github.com/octo/signal-kit)', monthly)

            yearly = yearly_path.read_text(encoding="utf-8")
            self.assertIn("The Ecosystem Reorganizes", yearly)
            self.assertIn('categories: ["yearly"]', yearly)
            self.assertIn('months_covered: ["2026-05"]', yearly)
            self.assertIn('format: "narrative"', yearly)
            self.assertIn('## Year in Review', yearly)
            self.assertIn('Practical agent tooling led the week.', yearly)
            self.assertNotIn('## Arc', yearly)

    def test_generate_rollups_is_append_only_for_existing_pages(self) -> None:
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            content_root = base / "content"
            analyzed_dir.mkdir(parents=True)

            (analyzed_dir / "2026-W21-summary.md").write_text(
                make_summary(
                    week="2026-W21",
                    date="2026-05-18T12:07:20+00:00",
                    top_repo="octo/signal-kit",
                    summary="Practical agent tooling led the week.",
                    signal="Teams preferred operational automation over generic hype.",
                    noise="Exploit-heavy projects still added editorial noise.",
                    gaps="Reliable momentum data remained missing.",
                    conclusion="The strongest projects made automation safer to adopt.",
                    tags=("alpha",),
                    repo_mentions=("octo/shared-kit",),
                ),
                encoding="utf-8",
            )
            generate_rollups.generate_rollups(analyzed_dir, content_root)
            monthly_path = content_root / "monthly" / "2026" / "05.md"
            yearly_path = content_root / "yearly" / "2026.md"
            first_monthly = monthly_path.read_text(encoding="utf-8")
            first_yearly = yearly_path.read_text(encoding="utf-8")

            (analyzed_dir / "2026-W22-summary.md").write_text(
                make_summary(
                    week="2026-W22",
                    date="2026-05-25T12:07:20+00:00",
                    top_repo="octo/steady-watch",
                    summary="Observability and release safety gained more traction.",
                    signal="Teams doubled down on measurable automation and release health.",
                    noise="Wrapper projects still outnumbered differentiated platforms.",
                    gaps="Defensive tooling still lagged behind orchestration tools.",
                    conclusion="The durable winners reduced toil without hiding trade-offs.",
                    tags=("beta",),
                    repo_mentions=("octo/shared-kit", "octo/deploy-guard"),
                ),
                encoding="utf-8",
            )

            generate_rollups.generate_rollups(analyzed_dir, content_root)
            second_monthly = monthly_path.read_text(encoding="utf-8")
            second_yearly = yearly_path.read_text(encoding="utf-8")

            self.assertIn('weeks_covered: ["2026-W21", "2026-W22"]', second_monthly)
            self.assertIn('total_repos_featured: 4', second_monthly)
            self.assertIn('months_covered: ["2026-05"]', second_yearly)
            for expected in [
                '### Week 2026-W21 — [Week 21, 2026](/weekly/2026/W21/)',
                '- [octo/signal-kit](https://github.com/octo/signal-kit) led the published weekly analysis for 2026-W21.',
                '- Signal: Teams preferred operational automation over generic hype.',
                '- Gap to watch: Reliable momentum data remained missing.',
                '- Recurring themes so far: alpha.',
            ]:
                self.assertIn(expected, second_monthly)
            self.assertIn('- Recurring themes so far: alpha, beta.', second_monthly)
            self.assertIn('format: "narrative"', second_yearly)
            self.assertIn('## Year in Review', second_yearly)
            self.assertIn('Observability and release safety gained more traction.', second_yearly)
            self.assertNotIn('## Arc', second_yearly)
            self.assertEqual(second_monthly.count('### Week 2026-W21'), 4)
            self.assertEqual(second_monthly.count('### Week 2026-W22'), 4)
            self.assertEqual(second_yearly.count('## Year in Review'), 1)
            self.assertNotEqual(first_monthly, second_monthly)
            self.assertNotEqual(first_yearly, second_yearly)

    def test_generate_yearly_narrative_standalone_writes_narrative_format(self) -> None:
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            content_root = base / "content"
            monthly_dir = content_root / "monthly" / "2026"
            monthly_dir.mkdir(parents=True)

            (monthly_dir / "05.md").write_text(
                """---
title: "May 2026 Rollup"
date: "2026-05-25T11:56:08+00:00"
month: 5
year: 2026
categories: ["monthly"]
weeks_covered: ["2026-W21", "2026-W22"]
total_repos_featured: 32
---

## Month Overview

### Week 2026-W21 — [Week 21, 2026](/weekly/2026/W21/)
- Summary: May defined the shift from maturing agent infrastructure toward a visible agent skills economy.
- Repositories featured this week: 17
- Recurring themes so far: agent-skills, mcp, small-models.

## Trends Observed

### Week 2026-W21 — [Week 21, 2026](/weekly/2026/W21/)
- Signal: Agent skills kept widening as a distribution format.
- Noise: Coordinated star-farming distorted discovery.

## Key Takeaways

### Week 2026-W21 — [Week 21, 2026](/weekly/2026/W21/)
- Gap to watch: Agent execution security remained underbuilt.
- Closing read: Skills were likely to spread into more teams.
""",
                encoding="utf-8",
            )
            (monthly_dir / "06.md").write_text(
                """---
title: "June 2026 Rollup"
date: "2026-06-08T12:40:47+00:00"
month: 6
year: 2026
categories: ["monthly"]
weeks_covered: ["2026-W23", "2026-W24"]
total_repos_featured: 36
---

## Month Overview

### Week 2026-W23 — [Week 23, 2026](/weekly/2026/W23/)
- Summary: June pushed agent skills into East Asian workflows, self-hosted AI workspaces, and role-specific verticalization.
- Repositories featured this week: 36
- Recurring themes so far: agent-skills, self-hosted-ai, coding-agents.

## Trends Observed

### Week 2026-W23 — [Week 23, 2026](/weekly/2026/W23/)
- Signal: Agent skills globalized quickly while local-sovereignty tooling gained traction.
- Noise: Fork inflation replaced the earlier star-farming wave.

## Key Takeaways

### Week 2026-W23 — [Week 23, 2026](/weekly/2026/W23/)
- Gap to watch: Prompt-injection and skills supply-chain security still lacked a category winner.
- Closing read: Expect more vertical skills packs and more local-first AI tooling.
""",
                encoding="utf-8",
            )

            written = generate_yearly_narrative.generate_yearly_narratives(content_root)
            yearly_path = content_root / "yearly" / "2026.md"

            self.assertEqual(written, [yearly_path])
            yearly = yearly_path.read_text(encoding="utf-8")
            self.assertIn('When Agents Became Infrastructure', yearly)
            self.assertIn('format: "narrative"', yearly)
            self.assertIn('## Year in Review', yearly)
            self.assertIn('split-screen story', yearly)
            self.assertIn('globalized', yearly)
            self.assertIn('What was confirmed:', yearly)
            self.assertIn('What weakened:', yearly)
            self.assertNotIn('## Arc', yearly)
            self.assertNotIn('agent-skills: infrastructure > economy > globalization > verticalization', yearly)

    def test_generate_yearly_narrative_prefers_month_synthesis_artifacts(self) -> None:
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            content_root = base / "content"
            monthly_dir = content_root / "monthly" / "2026"
            analyzed_dir = base / "data" / "analyzed"
            monthly_dir.mkdir(parents=True)
            analyzed_dir.mkdir(parents=True)

            (monthly_dir / "05.md").write_text(
                """---
title: "May 2026 Rollup"
date: "2026-05-25T11:56:08+00:00"
month: 5
year: 2026
categories: ["monthly"]
weeks_covered: ["2026-W21", "2026-W22"]
total_repos_featured: 32
---

## Month Overview

### Week 2026-W21 — [Week 21, 2026](/weekly/2026/W21/)
- Summary: Fallback monthly summary that should not drive the yearly opening.
- Repositories featured this week: 17
- Recurring themes so far: agent-skills, mcp.
""",
                encoding="utf-8",
            )
            (analyzed_dir / "2026-05-month-synthesis.md").write_text(
                """---
title: "May 2026 Monthly Synthesis"
date: "2026-05-25T11:56:08+00:00"
month: 5
year: 2026
---

## Month Synthesis

May made it clear that teams were no longer evaluating agent skills as demos; they were treating them as operating infrastructure with distribution consequences.

The strongest thread was a shift from raw capability talk toward packaging, trust, and fit inside real workflows.
""",
                encoding="utf-8",
            )

            written = generate_yearly_narrative.generate_yearly_narratives(content_root)
            yearly_path = content_root / "yearly" / "2026.md"

            self.assertEqual(written, [yearly_path])
            yearly = yearly_path.read_text(encoding="utf-8")
            self.assertIn("operating infrastructure with distribution consequences", yearly)
            self.assertNotIn("Fallback monthly summary that should not drive the yearly opening", yearly)

    def test_generate_rollups_replaces_placeholder_and_preserves_unknown_sections(self) -> None:
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            content_root = base / "content"
            analyzed_dir.mkdir(parents=True)
            monthly_path = content_root / "monthly" / "2026" / "05.md"
            monthly_path.parent.mkdir(parents=True, exist_ok=True)
            monthly_path.write_text(
                "---\ntitle: \"May 2026 Rollup\"\n---\n\n## Month Overview\n\n_No updates yet._\n\n## Legacy Notes\n\nKeep this section.\n",
                encoding="utf-8",
            )

            (analyzed_dir / "2026-W21-summary.md").write_text(
                make_summary(
                    week="2026-W21",
                    date="2026-05-18T12:07:20+00:00",
                    top_repo="octo/signal-kit",
                    summary="Practical agent tooling led the week.",
                    signal="Teams preferred operational automation over generic hype.",
                    noise="Exploit-heavy projects still added editorial noise.",
                    gaps="Reliable momentum data remained missing.",
                    conclusion="The strongest projects made automation safer to adopt.",
                ),
                encoding="utf-8",
            )

            generate_rollups.generate_rollups(analyzed_dir, content_root)
            monthly = monthly_path.read_text(encoding="utf-8")

            self.assertNotIn("_No updates yet._\n\n### Week 2026-W21", monthly)
            self.assertIn("### Week 2026-W21", monthly)
            self.assertIn("## Legacy Notes\n\nKeep this section.", monthly)

    def test_generate_rollups_returns_empty_when_no_summaries_exist(self) -> None:
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            content_root = base / "content"
            analyzed_dir.mkdir(parents=True)

            self.assertEqual(generate_rollups.generate_rollups(analyzed_dir, content_root), [])
            stderr = io.StringIO()
            with mock.patch("sys.stderr", stderr):
                self.assertEqual(generate_rollups.main(["--analyzed-dir", str(analyzed_dir), "--content-root", str(content_root)]), 0)
            self.assertIn("No weekly summaries found", stderr.getvalue())

    def test_parse_args_defaults_resolve_from_project_root(self) -> None:
        args = generate_rollups.parse_args([])

        self.assertEqual(args.analyzed_dir, Path(generate_rollups.PROJECT_ROOT / "data" / "analyzed"))
        self.assertEqual(args.content_root, Path(generate_rollups.PROJECT_ROOT / "content"))

    def test_generate_rolling_report_creates_last_month(self) -> None:
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            content_root = base / "content"
            weekly_dir = content_root / "weekly" / "2026"
            weekly_dir.mkdir(parents=True)

            for wnum, date in [
                ("21", "2026-05-21T12:00:00+00:00"),
                ("22", "2026-05-25T12:00:00+00:00"),
                ("23", "2026-06-06T12:00:00+00:00"),
                ("24", "2026-06-08T12:00:00+00:00"),
            ]:
                (weekly_dir / f"W{wnum}.md").write_text(
                    make_summary(
                        week=f"2026-W{wnum}",
                        date=date,
                        top_repo=f"octo/repo-{wnum}",
                        summary=f"Summary for W{wnum}.",
                        signal=f"Signal for W{wnum}.",
                        noise=f"Noise for W{wnum}.",
                        gaps=f"Gaps for W{wnum}.",
                        conclusion=f"Conclusion for W{wnum}.",
                        tags=("ai", "agents") if wnum in ("21", "22") else ("ai", "new-tag"),
                    ),
                    encoding="utf-8",
                )

            result = generate_rollups.generate_rolling_report(content_root)

            self.assertIsNotNone(result)
            self.assertEqual(result, content_root / "rolling" / "last-month.md")
            self.assertTrue(result.exists())

            report = result.read_text(encoding="utf-8")
            self.assertIn("title: Rolling 4-Week Context", report)
            self.assertIn("updated: 2026-W24", report)
            self.assertIn("weeks: [W21, W22, W23, W24]", report)
            self.assertIn("## Active Trends", report)
            self.assertIn("## Trend Velocity", report)
            self.assertIn("## Open Predictions", report)
            self.assertIn("## Noise Patterns", report)
            self.assertIn("Signal for W", report)
            self.assertIn("Noise for W", report)
            self.assertIn("[W24] Gaps for W24.", report)

    def test_generate_rolling_report_returns_none_when_no_content(self) -> None:
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            content_root = base / "content"
            content_root.mkdir(parents=True)

            result = generate_rollups.generate_rolling_report(content_root)
            self.assertIsNone(result)

    def test_rolling_flag_triggers_rolling_report(self) -> None:
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            content_root = base / "content"
            analyzed_dir.mkdir(parents=True)
            weekly_dir = content_root / "weekly" / "2026"
            weekly_dir.mkdir(parents=True)

            summary_text = make_summary(
                week="2026-W21",
                date="2026-05-21T12:00:00+00:00",
                top_repo="octo/signal-kit",
                summary="Test summary.",
                signal="Test signal.",
                noise="Test noise.",
                gaps="Test gaps.",
                conclusion="Test conclusion.",
            )
            (analyzed_dir / "2026-W21-summary.md").write_text(summary_text, encoding="utf-8")
            (weekly_dir / "W21.md").write_text(summary_text, encoding="utf-8")

            ret = generate_rollups.main([
                "--analyzed-dir", str(analyzed_dir),
                "--content-root", str(content_root),
                "--rolling",
            ])
            self.assertEqual(ret, 0)
            self.assertTrue((content_root / "rolling" / "last-month.md").exists())

    def test_velocity_classification(self) -> None:
        tags_by_week = [
            ("2026-W21", {"ai", "agents", "old-tag"}),
            ("2026-W22", {"ai", "agents"}),
            ("2026-W23", {"ai", "new-thing"}),
            ("2026-W24", {"ai", "new-thing"}),
        ]
        velocity = generate_rollups._classify_velocity(tags_by_week)
        self.assertEqual(velocity["ai"], "accelerating")
        self.assertEqual(velocity["old-tag"], "dying")
        self.assertIn(velocity["new-thing"], ("accelerating", "new"))

    def test_extract_summary_in_yearly_frontmatter(self) -> None:
        """Yearly pages must include a summary field in frontmatter."""
        with temporary_workspace() as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            content_root = base / "content"
            analyzed_dir.mkdir(parents=True)

            (analyzed_dir / "2026-W21-summary.md").write_text(
                make_summary(
                    week="2026-W21",
                    date="2026-05-18T12:07:20+00:00",
                    top_repo="octo/signal-kit",
                    summary="Practical agent tooling led the week.",
                    signal="Teams preferred operational automation over generic hype.",
                    noise="Exploit-heavy projects still added editorial noise.",
                    gaps="Reliable momentum data remained missing.",
                    conclusion="The strongest projects made automation safer to adopt.",
                ),
                encoding="utf-8",
            )

            generate_rollups.generate_rollups(analyzed_dir, content_root)
            yearly_path = content_root / "yearly" / "2026.md"
            yearly = yearly_path.read_text(encoding="utf-8")
            self.assertIn("summary:", yearly)
            # Extract summary value and verify length constraint
            for line in yearly.splitlines():
                if line.strip().startswith("summary:"):
                    summary_value = line.split(":", 1)[1].strip().strip('"')
                    self.assertLessEqual(len(summary_value), 155)
                    break
            else:
                self.fail("summary field not found in yearly frontmatter")


class ExtractSummaryTests(unittest.TestCase):
    def test_short_sentence_returned_as_is(self) -> None:
        result = generate_yearly_narrative._extract_summary("Short sentence.")
        self.assertEqual(result, "Short sentence.")

    def test_exclamation_mark_terminates_sentence(self) -> None:
        result = generate_yearly_narrative._extract_summary("Wow! More text follows here.")
        self.assertEqual(result, "Wow!")

    def test_question_mark_terminates_sentence(self) -> None:
        result = generate_yearly_narrative._extract_summary("Why not? The rest is irrelevant.")
        self.assertEqual(result, "Why not?")

    def test_truncation_respects_max_length(self) -> None:
        long = "A" * 200 + "."
        result = generate_yearly_narrative._extract_summary(long, max_length=50)
        self.assertLessEqual(len(result), 50)
        self.assertTrue(result.endswith("…"))

    def test_truncation_at_word_boundary(self) -> None:
        sentence = "This is a moderately long sentence that should be truncated at a word boundary when it exceeds the maximum allowed length for meta descriptions."
        result = generate_yearly_narrative._extract_summary(sentence, max_length=60)
        self.assertLessEqual(len(result), 60)
        self.assertTrue(result.endswith("…"))
        self.assertFalse(result[-2].isspace())

    def test_leading_whitespace_stripped(self) -> None:
        result = generate_yearly_narrative._extract_summary("  Leading spaces. More text.")
        self.assertEqual(result, "Leading spaces.")

    def test_fallback_when_no_sentence_terminator(self) -> None:
        result = generate_yearly_narrative._extract_summary("No punctuation at all")
        self.assertEqual(result, "No punctuation at all")

    def test_fallback_truncation_for_long_text_without_terminator(self) -> None:
        long = "word " * 50
        result = generate_yearly_narrative._extract_summary(long, max_length=30)
        self.assertLessEqual(len(result), 30)
        self.assertTrue(result.endswith("…"))


if __name__ == "__main__":
    unittest.main()

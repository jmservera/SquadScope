import io
import tempfile
import unittest
from pathlib import Path

import scripts.generate_rollups as generate_rollups


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

## Notable New Repositories

{notable_new}

## Trending This Week

Momentum concentrated around practical tooling.

## Trend Analysis

### Signal

{signal}

### Noise

{noise}

## What's Missing

### Gaps

{gaps}

## Conclusion

{conclusion}
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
            self.assertIn('title: "May 2026 Rollup"', monthly)
            self.assertIn('categories: ["monthly"]', monthly)
            self.assertIn('weeks_covered: ["2026-W21"]', monthly)
            self.assertIn('total_repos_featured: 1', monthly)
            self.assertIn('---\n\n## Month Overview', monthly)
            self.assertIn('## Month Overview', monthly)
            self.assertIn('### Week 2026-W21', monthly)
            self.assertIn('[Week 21, 2026](/weekly/2026/W21/)', monthly)
            self.assertIn('[octo/signal-kit](https://github.com/octo/signal-kit)', monthly)

            yearly = yearly_path.read_text(encoding="utf-8")
            self.assertIn('title: "2026 Yearly Rollup"', yearly)
            self.assertIn('categories: ["yearly"]', yearly)
            self.assertIn('months_covered: ["2026-05"]', yearly)
            self.assertIn('## Year in Review', yearly)
            self.assertIn('### May 2026 update — 2026-W21', yearly)
            self.assertIn('[May 2026](/monthly/2026/05/)', yearly)

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
                '- Themes in rotation: alpha.',
            ]:
                self.assertIn(expected, second_monthly if 'Recurring themes' in expected else second_yearly if 'Themes in rotation' in expected else second_monthly)
            self.assertIn('- Recurring themes so far: alpha, beta.', second_monthly)
            self.assertIn('- Themes in rotation: alpha, beta.', second_yearly)
            for expected in [
                '### May 2026 update — 2026-W21',
                '- [May 2026](/monthly/2026/05/) gained a new weekly signal via [Week 21, 2026](/weekly/2026/W21/).',
                '- Featured repo: [octo/signal-kit](https://github.com/octo/signal-kit).',
                '- Working takeaway: The strongest projects made automation safer to adopt.',
            ]:
                self.assertIn(expected, second_yearly)
            self.assertEqual(second_monthly.count('### Week 2026-W21'), 4)
            self.assertEqual(second_monthly.count('### Week 2026-W22'), 4)
            self.assertEqual(second_yearly.count('### May 2026 update — 2026-W21'), 5)
            self.assertEqual(second_yearly.count('### May 2026 update — 2026-W22'), 5)
            self.assertNotEqual(first_monthly, second_monthly)
            self.assertNotEqual(first_yearly, second_yearly)

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
            with unittest.mock.patch("sys.stderr", stderr):
                self.assertEqual(generate_rollups.main(["--analyzed-dir", str(analyzed_dir), "--content-root", str(content_root)]), 0)
            self.assertIn("No weekly summaries found", stderr.getvalue())

    def test_parse_args_defaults_resolve_from_project_root(self) -> None:
        args = generate_rollups.parse_args([])

        self.assertEqual(args.analyzed_dir, Path(generate_rollups.PROJECT_ROOT / "data" / "analyzed"))
        self.assertEqual(args.content_root, Path(generate_rollups.PROJECT_ROOT / "content"))


if __name__ == "__main__":
    unittest.main()

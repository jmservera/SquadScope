import tempfile
import unittest
from pathlib import Path

import scripts.generate_content as generate_content


class GenerateContentTests(unittest.TestCase):
    def test_generate_content_creates_hugo_weekly_page(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            summary_path = base / "data" / "analyzed" / "2026-W21-summary.md"
            summary_path.parent.mkdir(parents=True)
            summary_path.write_text(
                """---
title: \"Week 21, 2026 Analysis\"
date: 2026-05-18T13:20:07.067+02:00
week: \"2026-W21\"
year: 2026
tags: [ai, agents, developer-tooling]
categories: [weekly]
repos_featured: 12
stars_tracked: 3456
top_repo: \"octo/repo\"
quality_score: 88
summary: \"Agent tooling became more operational this week.\"
---

## Notable New Repositories

Body copy.
""",
                encoding="utf-8",
            )

            previous_cwd = Path.cwd()
            try:
                import os

                os.chdir(base)
                output_path = generate_content.generate_content(summary_path)
            finally:
                os.chdir(previous_cwd)

            self.assertEqual(output_path, base / "content" / "weekly" / "2026" / "W21.md")
            rendered = output_path.read_text(encoding="utf-8")
            self.assertIn('title: "Week 21, 2026"', rendered)
            self.assertIn("draft: false", rendered)
            self.assertIn('week: "2026-W21"', rendered)
            self.assertIn('top_repo: "octo/repo"', rendered)
            self.assertIn('summary: "Agent tooling became more operational this week."', rendered)
            self.assertNotIn("quality_score", rendered)
            self.assertNotIn("year:", rendered)
            self.assertIn("## Notable New Repositories", rendered)

    def test_find_latest_summary_uses_week_not_mtime(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            analyzed_dir.mkdir(parents=True)
            latest = analyzed_dir / "2027-W01-summary.md"
            older = analyzed_dir / "2026-W52-summary.md"
            latest.write_text("latest\n", encoding="utf-8")
            older.write_text("older but touched later\n", encoding="utf-8")

            self.assertEqual(generate_content.find_latest_summary(base), latest)

    def test_parse_frontmatter_rejects_missing_required_fields(self) -> None:
        with self.assertRaises(generate_content.GenerationError):
            generate_content.parse_frontmatter(
                """---
title: \"Week 21, 2026 Analysis\"
---

## Notable New Repositories
"""
            )


if __name__ == "__main__":
    unittest.main()

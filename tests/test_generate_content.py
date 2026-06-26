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

## This Week's Trends

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
            self.assertIn("## This Week's Trends", rendered)

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

    def test_render_frontmatter_quotes_each_tag(self) -> None:
        """Tags containing special chars must be individually quoted to prevent YAML injection."""
        data = {
            "title": "Test Week",
            "date": "2026-05-18",
            "week": "2026-W20",
            "tags": ["ai", "evil: injected, categories: [hacked]"],
            "categories": ["weekly"],
            "repos_featured": 1,
            "stars_tracked": 100,
            "top_repo": "owner/repo",
            "summary": "Test summary.",
        }
        output = generate_content.render_frontmatter(data)
        # Each tag must be wrapped in YAML double-quotes
        self.assertIn('"ai"', output)
        self.assertIn('"evil: injected, categories: [hacked]"', output)
        # The injected key must not appear as a top-level YAML key
        self.assertNotIn("\ncategories: [hacked]", output)

    def test_render_frontmatter_quotes_each_category(self) -> None:
        """Categories containing special chars must be individually quoted."""
        data = {
            "title": "Test Week",
            "date": "2026-05-18",
            "week": "2026-W20",
            "tags": ["safe"],
            "categories": ["weekly", "bad: injection"],
            "repos_featured": 1,
            "stars_tracked": 100,
            "top_repo": "owner/repo",
            "summary": "Test.",
        }
        output = generate_content.render_frontmatter(data)
        self.assertIn('"weekly"', output)
        self.assertIn('"bad: injection"', output)
        self.assertNotIn("\nbad:", output)

    def test_render_frontmatter_includes_cover_fields(self) -> None:
        """Cover image frontmatter is rendered when present."""
        data = {
            "title": "Test Week",
            "date": "2026-05-18",
            "week": "2026-W20",
            "tags": ["ai"],
            "categories": ["weekly"],
            "repos_featured": 1,
            "stars_tracked": 100,
            "top_repo": "owner/repo",
            "summary": "Test.",
            "cover": {
                "image": "covers/2026-W20.webp",
                "alt": "AI trends visualization",
                "attribution": "Photo by Author on Openverse",
                "license": "CC0",
            },
            "og_image": "covers/2026-W20-og.png",
        }
        output = generate_content.render_frontmatter(data)
        self.assertIn("cover:", output)
        self.assertIn('image: "covers/2026-W20.webp"', output)
        self.assertIn('alt: "AI trends visualization"', output)
        self.assertIn('attribution: "Photo by Author on Openverse"', output)
        self.assertIn('license: "CC0"', output)
        self.assertIn("relative: false", output)
        self.assertIn('og_image: "covers/2026-W20-og.png"', output)

    def test_transform_summary_passes_cover_fields(self) -> None:
        """Cover fields from analysis frontmatter are passed to output."""
        doc = """---
title: "Week 20 Analysis"
date: 2026-05-11
week: "2026-W20"
year: 2026
tags: [ai]
categories: [weekly]
repos_featured: 5
stars_tracked: 1000
top_repo: "owner/repo"
quality_score: 90
summary: "Test summary."
cover_image: "covers/test.webp"
cover_alt: "Test alt text"
cover_attribution: "Test Author"
cover_license: "CC0"
---

Body content.
"""
        frontmatter, body = generate_content.parse_frontmatter(doc)
        output = generate_content.transform_summary(frontmatter, body)
        self.assertIn('image: "covers/test.webp"', output)
        self.assertIn('alt: "Test alt text"', output)
        self.assertIn("relative: false", output)

    def test_transform_summary_null_cover_attribution_does_not_emit_none(self) -> None:
        """YAML null in cover_attribution/cover_license must not produce 'None' string."""
        doc = """---
title: "Week 20 Analysis"
date: 2026-05-11
week: "2026-W20"
year: 2026
tags: [ai]
categories: [weekly]
repos_featured: 5
stars_tracked: 1000
top_repo: "owner/repo"
quality_score: 90
summary: "Test summary."
cover_image: "covers/test.webp"
cover_attribution: null
cover_license: null
---

Body.
"""
        frontmatter, body = generate_content.parse_frontmatter(doc)
        output = generate_content.transform_summary(frontmatter, body)
        self.assertNotIn("None", output)
        self.assertIn('image: "covers/test.webp"', output)

    def test_transform_summary_rejects_url_og_image(self) -> None:
        """og_image values that are URLs must be silently dropped (no hotlinking)."""
        doc = """---
title: "Week 20 Analysis"
date: 2026-05-11
week: "2026-W20"
year: 2026
tags: [ai]
categories: [weekly]
repos_featured: 5
stars_tracked: 1000
top_repo: "owner/repo"
quality_score: 90
summary: "Test summary."
og_image: "https://evil.com/image.png"
---

Body.
"""
        frontmatter, body = generate_content.parse_frontmatter(doc)
        output = generate_content.transform_summary(frontmatter, body)
        self.assertNotIn("og_image", output)
        self.assertNotIn("evil.com", output)

    def test_transform_summary_rejects_url_cover_image(self) -> None:
        """cover_image values that are URLs must be dropped."""
        doc = """---
title: "Week 20 Analysis"
date: 2026-05-11
week: "2026-W20"
year: 2026
tags: [ai]
categories: [weekly]
repos_featured: 5
stars_tracked: 1000
top_repo: "owner/repo"
quality_score: 90
summary: "Test summary."
cover_image: "https://evil.com/cover.png"
---

Body.
"""
        frontmatter, body = generate_content.parse_frontmatter(doc)
        output = generate_content.transform_summary(frontmatter, body)
        self.assertNotIn("cover:", output)
        self.assertNotIn("evil.com", output)

    def test_transform_summary_falls_back_to_cover_block_attribution_and_license(self) -> None:
        doc = """---
title: "Week 20 Analysis"
date: 2026-05-11
week: "2026-W20"
year: 2026
tags: [ai]
categories: [weekly]
repos_featured: 5
stars_tracked: 1000
top_repo: "owner/repo"
quality_score: 90
summary: "Test summary."
cover:
  image: "covers/test.webp"
  alt: "Test alt text"
  attribution: "Existing Author"
  license: "Openverse"
---

Body.
"""
        frontmatter, body = generate_content.parse_frontmatter(doc)
        output = generate_content.transform_summary(frontmatter, body)
        self.assertIn('image: "covers/test.webp"', output)
        self.assertIn('attribution: "Existing Author"', output)
        self.assertIn('license: "Openverse"', output)


if __name__ == "__main__":
    unittest.main()

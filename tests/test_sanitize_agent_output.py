import unittest

import scripts.sanitize_agent_output as sanitize_agent_output


class SanitizeAgentOutputTests(unittest.TestCase):
    def test_sanitize_text_removes_leaked_agent_summary_lines(self) -> None:
        original = """---
title: \"Week 21, 2026 Analysis\"
quality_score: 76
---

## This Week's Trends

Real article paragraph.

✅ Farnsworth is done. data/analyzed/2026-W21-summary.md is written (88 lines).
Editorial thesis: Genuine agentic coding infrastructure is breaking out.
Quality score: 76/100 — publishable.
"""

        sanitized = sanitize_agent_output.sanitize_text(original)

        self.assertNotIn("✅ Farnsworth is done.", sanitized)
        self.assertNotIn("Editorial thesis:", sanitized)
        self.assertNotIn("Quality score: 76/100", sanitized)
        self.assertIn("Real article paragraph.", sanitized)
        self.assertIn("quality_score: 76", sanitized)

    def test_sanitize_text_preserves_legitimate_article_content(self) -> None:
        original = """---
title: \"Week 21, 2026 Analysis\"
quality_score: 76
summary: \"Quality score caveats belong only in frontmatter.\"
---

## Signal & Noise

The article discusses quality score inflation as a concept without using agent metadata.
"""

        sanitized = sanitize_agent_output.sanitize_text(original)

        self.assertEqual(sanitized, original)


if __name__ == "__main__":
    unittest.main()

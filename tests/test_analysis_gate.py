import unittest

import scripts.analysis_gate as analysis_gate


RAW_PAYLOAD = {"week": "2026-W21"}
CURRENT_DATETIME = "2026-05-18T00:00:00Z"


def make_body(*, alternate_heading: str = "## Where Industry Meets Code", include_todo_app: bool = False) -> str:
    trends = " ".join(
        [
            "This section names the macro trends of the week, explaining what is driving each pattern and why it matters to practitioners tracking real engineering movement."
        ]
        * 4
    )
    industry = " ".join(
        [
            "Developer activity and press coverage aligned around practical tooling, but the narrative reveals where media attention diverged from what engineers are actually building."
        ]
        * 3
    )
    signal_noise = " ".join(
        [
            "The durable pattern is disciplined infrastructure work and credible developer experience improvements. The weak pattern is wrapper churn, shallow agent branding, and launches that borrow attention without demonstrating technical substance or ecosystem fit."
        ]
        * 3
    )
    blind_spots = " ".join(
        [
            "What is missing is more progress on observability, testing ergonomics, and dependable security tooling for smaller teams that still need production discipline."
        ]
        * 3
    )
    week_ahead = " ".join(
        [
            "The week matters because it shows teams rewarding grounded software that reduces toil, while hype-heavy experiments still struggle to prove lasting value."
        ]
        * 2
    )
    if include_todo_app:
        week_ahead += " Several repositories mention todo apps as legitimate examples rather than placeholder notes."
    return f"""
## This Week's Trends

{trends}

{alternate_heading}

{industry}

## Signal & Noise

{signal_noise}

## Blind Spots

{blind_spots}

## The Week Ahead

{week_ahead}

## Key References

### Notable Projects

- [owner/repo-a](https://github.com/owner/repo-a) — anchors the automation trend with practical defaults.
- [owner/repo-b](https://github.com/owner/repo-b) — observability tooling for smaller teams.

### Press & Industry

No press data was provided this week.
""".strip()


def make_analysis(frontmatter: str, body: str) -> str:
    return f"---\n{frontmatter}\n---\n\n{body}\n"


VALID_FRONTMATTER = '''title: "Week 21, 2026 Analysis"
date: 2026-05-18T00:00:00Z
week: 2026-W21
year: 2026
tags:
  - ai
  - agents
  - infrastructure
categories:
  - weekly
repos_featured: 9
stars_tracked: 1200
top_repo: owner/repo
quality_score: 82
summary: "A grounded week focused on practical tools."'''.strip()


class AnalysisGateTests(unittest.TestCase):
    def test_validate_analysis_accepts_block_style_lists(self) -> None:
        errors, word_count = analysis_gate.validate_analysis(
            make_analysis(VALID_FRONTMATTER, make_body()),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertEqual(errors, [])
        self.assertGreaterEqual(word_count, 200)

    def test_validate_analysis_rejects_wrong_week_date_and_types(self) -> None:
        invalid_frontmatter = '''title: "Week 21, 2026 Analysis"
date: 2026-05-12T00:00:00Z
week: 2026-W20
year: "2026"
tags: weekly
categories:
  - analysis
repos_featured: 9
stars_tracked: 1200
top_repo: owner/repo
quality_score: 82
summary: "A grounded week focused on practical tools."'''.strip()

        errors, _ = analysis_gate.validate_analysis(
            make_analysis(invalid_frontmatter, make_body()),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertIn("week must match raw payload week '2026-W21'.", errors)
        self.assertIn("year must be an integer.", errors)
        self.assertIn("tags must be an array of strings.", errors)
        self.assertIn("categories must include 'weekly'.", errors)
        self.assertIn("date must match the current run timestamp.", errors)
        self.assertIn("date must fall within raw payload week 2026-W21.", errors)

    def test_validate_analysis_requires_real_heading_lines(self) -> None:
        body = make_body(
            alternate_heading="The prose references ## Where Industry Meets Code without creating a heading line.",
        )
        errors, _ = analysis_gate.validate_analysis(
            make_analysis(VALID_FRONTMATTER, body),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertIn("Missing required section heading: ## Where Industry Meets Code", errors)

    def test_validate_analysis_allows_legitimate_todo_mentions(self) -> None:
        errors, _ = analysis_gate.validate_analysis(
            make_analysis(VALID_FRONTMATTER, make_body(include_todo_app=True)),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertEqual(errors, [])

    def test_validate_analysis_rejects_todo_placeholders(self) -> None:
        body = make_body() + "\n\nTODO: replace this closing note.\n"
        errors, _ = analysis_gate.validate_analysis(
            make_analysis(VALID_FRONTMATTER, body),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertIn("Analysis body contains prohibited placeholder marker: TODO placeholder marker", errors)


if __name__ == "__main__":
    unittest.main()

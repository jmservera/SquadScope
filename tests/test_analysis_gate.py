import unittest

import scripts.analysis_gate as analysis_gate


RAW_PAYLOAD = {"week": "2026-W21"}
CURRENT_DATETIME = "2026-05-18T00:00:00Z"


def make_body(*, trending_heading: str = "## Trending This Week", include_todo_app: bool = False) -> str:
    notable = " ".join(
        [
            "This section evaluates durable launches, compares architecture choices, and explains why the strongest repositories matter for practitioners tracking real engineering movement."
        ]
        * 4
    )
    trending = " ".join(
        [
            "Attention moved toward practical tooling, but the narrative distinguishes genuine momentum from incumbents that simply remain popular because they already dominate conversation."
        ]
        * 4
    )
    signal = " ".join(
        [
            "The durable pattern is disciplined infrastructure work, careful developer experience improvements, and credible evidence that teams are solving recurring operational pain."
        ]
        * 3
    )
    noise = " ".join(
        [
            "The weak pattern is wrapper churn, shallow agent branding, and launches that borrow attention without demonstrating technical substance or ecosystem fit."
        ]
        * 3
    )
    gaps = " ".join(
        [
            "What is missing is more progress on observability, testing ergonomics, and dependable security tooling for smaller teams that still need production discipline."
        ]
        * 3
    )
    conclusion = " ".join(
        [
            "The week matters because it shows teams rewarding grounded software that reduces toil, while hype-heavy experiments still struggle to prove lasting value."
        ]
        * 2
    )
    if include_todo_app:
        conclusion += " Several repositories mention todo apps as legitimate examples rather than placeholder notes."
    return f"""
## Notable New Repositories

{notable}

{trending_heading}

{trending}

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
            trending_heading="The prose references ## Trending This Week without creating a heading line.",
        )
        errors, _ = analysis_gate.validate_analysis(
            make_analysis(VALID_FRONTMATTER, body),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertIn("Missing required section heading: ## Trending This Week", errors)

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

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

import scripts.check_copilot_pricing_review as pricing_review


class CopilotPricingReviewTests(unittest.TestCase):
    def test_review_not_due_before_two_month_interval(self) -> None:
        status = pricing_review.pricing_status(date(2026, 8, 5))
        self.assertFalse(status["needs_review"])
        self.assertFalse(status["review_due"])
        self.assertEqual(status["due_date"], "2026-08-06")

    def test_review_due_at_two_month_interval(self) -> None:
        status = pricing_review.pricing_status(date(2026, 8, 6))
        self.assertTrue(status["needs_review"])
        self.assertTrue(status["review_due"])

    def test_source_url_mismatch_requires_review(self) -> None:
        status = pricing_review.pricing_status(date(2026, 7, 1), source_url="https://example.invalid/pricing")
        self.assertTrue(status["needs_review"])
        self.assertFalse(status["source_url_matches"])

    def test_source_headers_are_parsed_for_report_metadata(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            headers = Path(tmpdir) / "headers.txt"
            headers.write_text('HTTP/2 200\netag: "abc123"\nlast-modified: Sat, 06 Jun 2026 00:00:00 GMT\n', encoding="utf-8")
            status = pricing_review.pricing_status(date(2026, 7, 1), source_headers=pricing_review.parse_source_headers(headers))
            report = pricing_review.render_report(status)
            self.assertEqual(status["source_headers"]["etag"], '"abc123"')
            self.assertIn("last-modified", report)

    def test_main_writes_report_json_and_github_outputs(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            report_path = base / "report.md"
            json_path = base / "status.json"
            github_output = base / "github-output.txt"

            rc = pricing_review.main(
                [
                    "--current-date",
                    "2026-08-06",
                    "--output",
                    str(report_path),
                    "--json-output",
                    str(json_path),
                    "--github-output",
                    str(github_output),
                ]
            )

            self.assertEqual(rc, 0)
            self.assertIn("does not change pricing automatically", report_path.read_text(encoding="utf-8"))
            status = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertTrue(status["needs_review"])
            self.assertIn("needs_review=true", github_output.read_text(encoding="utf-8"))


class CopilotPricingReviewWorkflowTests(unittest.TestCase):
    def test_workflow_is_scheduled_and_opens_issue_without_changing_pricing(self) -> None:
        workflow_path = Path(".github/workflows/copilot-pricing-review.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        self.assertEqual(workflow["name"], "Copilot Pricing Review")
        self.assertEqual(workflow[True]["schedule"][0]["cron"], "23 9 6 */2 *")
        self.assertIn("workflow_dispatch", workflow[True])
        self.assertEqual(workflow["permissions"], {"contents": "read", "issues": "write"})

        job = workflow["jobs"]["review-pricing"]
        pricing_step = next((step for step in job["steps"] if step.get("id") == "pricing"), None)
        self.assertIsNotNone(pricing_step)
        self.assertIn("scripts/check_copilot_pricing_review.py", pricing_step["run"])
        self.assertIn("--source-headers", pricing_step["run"])
        self.assertIn("--github-output", pricing_step["run"])
        metadata_step = next((step for step in job["steps"] if step.get("name") == "Capture Copilot pricing source metadata"), None)
        self.assertIsNotNone(metadata_step)
        self.assertIn("curl -fsSLI", metadata_step["run"])

        issue_step = next((step for step in job["steps"] if step.get("name") == "Create or update pricing review issue"), None)
        self.assertIsNotNone(issue_step)
        self.assertEqual(issue_step["if"], "steps.pricing.outputs.needs_review == 'true'")
        self.assertIn("gh issue create", issue_step["run"])
        self.assertIn("gh issue comment", issue_step["run"])
        self.assertNotIn("git commit", issue_step["run"])
        self.assertNotIn("git push", issue_step["run"])


if __name__ == "__main__":
    unittest.main()

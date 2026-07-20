import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import scripts.analysis_gate as analysis_gate

RAW_PAYLOAD = {"week": "2026-W23"}
RAW_PAYLOAD_WITH_REPOS = {
    "week": "2026-W23",
    "crawled_at": "2026-06-01T00:00:00Z",
    "new_repos": [{"full_name": "owner/repo", "stars": 1000}],
    "trending_repos": [
        {"full_name": "owner/repo-a", "stars": 300},
        {"full_name": "owner/repo-b", "stars": 200},
    ],
}
CURRENT_DATETIME = "2026-06-01T00:00:00Z"


def make_body(
    *, alternate_heading: str = "## Where Industry Meets Code", include_todo_app: bool = False
) -> str:
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


VALID_FRONTMATTER = '''title: "The Week Local Models Went Mainstream"
date: 2026-06-01T00:00:00Z
week: 2026-W23
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
        invalid_frontmatter = '''title: "The Week Local Models Went Mainstream"
date: 2026-06-01T12:00:00Z
week: 2026-W22
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

        self.assertIn("week must match raw payload week '2026-W23'.", errors)
        self.assertIn("year must be an integer.", errors)
        self.assertIn("tags must be an array of strings.", errors)
        self.assertIn("categories must include 'weekly'.", errors)
        self.assertIn("date must match the current run timestamp.", errors)

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

        self.assertIn(
            "Analysis body contains prohibited placeholder marker: TODO placeholder marker", errors
        )

    def test_validate_analysis_rejects_generic_week_analysis_title(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace(
            'title: "The Week Local Models Went Mainstream"',
            'title: "Week 21, 2026 Analysis"',
        )
        errors, _ = analysis_gate.validate_analysis(
            make_analysis(frontmatter, make_body()),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertIn("title must not use a generic week/year placeholder format.", errors)

    def test_validate_analysis_rejects_generic_week_year_title(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace(
            'title: "The Week Local Models Went Mainstream"',
            'title: "Week 21, 2026"',
        )
        errors, _ = analysis_gate.validate_analysis(
            make_analysis(frontmatter, make_body()),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertIn("title must not use a generic week/year placeholder format.", errors)

    def test_validate_analysis_accepts_prediction_registry(self) -> None:
        frontmatter = (
            VALID_FRONTMATTER
            + "\npredictions:\n  - repo: owner/repo\n    claim_type: signal\n    direction: up\n    confidence: 0.7"
        )

        errors, _ = analysis_gate.validate_analysis(
            make_analysis(frontmatter, make_body()),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertEqual(errors, [])

    def test_repair_analysis_refuses_to_guess_legacy_prediction_claim_type(self) -> None:
        frontmatter = (
            VALID_FRONTMATTER.replace(
                "date: 2026-06-01T00:00:00Z",
                "date: 2026-06-01T12:00:00Z",
            )
            + "\npredictions:\n  - repo: owner/repo\n    direction: up\n    confidence: 0.7"
        )

        repaired_text, actions = analysis_gate.repair_analysis(
            make_analysis(frontmatter, make_body()),
            RAW_PAYLOAD_WITH_REPOS,
            CURRENT_DATETIME,
        )
        errors, _ = analysis_gate.validate_analysis(
            repaired_text, RAW_PAYLOAD_WITH_REPOS, CURRENT_DATETIME
        )
        frontmatter_after, _ = analysis_gate.extract_frontmatter(repaired_text)

        self.assertEqual(errors, ["predictions[1].claim_type must be one of signal, noise, gap."])
        self.assertIn("set date from current run timestamp", actions)
        self.assertNotIn("claim_type", frontmatter_after["predictions"][0])
        self.assertEqual(frontmatter_after["repos_featured"], 3)
        self.assertEqual(frontmatter_after["stars_tracked"], 1500)

    def test_repair_analysis_normalizes_safe_prediction_claim_alias(self) -> None:
        frontmatter = (
            VALID_FRONTMATTER
            + "\npredictions:\n  - repo: owner/repo\n    claim: Signal\n    direction: UP\n    confidence: 0.7"
        )

        repaired_text, actions = analysis_gate.repair_analysis(
            make_analysis(frontmatter, make_body()),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )
        errors, _ = analysis_gate.validate_analysis(repaired_text, RAW_PAYLOAD, CURRENT_DATETIME)
        frontmatter_after, _ = analysis_gate.extract_frontmatter(repaired_text)

        self.assertEqual(errors, [])
        self.assertIn("set predictions[1].claim_type from claim", actions)
        self.assertEqual(frontmatter_after["predictions"][0]["claim_type"], "signal")
        self.assertNotIn("claim", frontmatter_after["predictions"][0])

    def test_validate_analysis_rejects_invalid_prediction_registry(self) -> None:
        frontmatter = (
            VALID_FRONTMATTER
            + "\npredictions:\n  - repo: bad repo\n    claim_type: maybe\n    direction: sideways\n    confidence: 1.3\n    note: nope"
        )

        errors, _ = analysis_gate.validate_analysis(
            make_analysis(frontmatter, make_body()),
            RAW_PAYLOAD,
            CURRENT_DATETIME,
        )

        self.assertIn("predictions[1].repo must use owner/repo format.", errors)
        self.assertIn("predictions[1].claim_type must be one of signal, noise, gap.", errors)
        self.assertIn("predictions[1].direction must be one of up, flat, down.", errors)
        self.assertIn("predictions[1].confidence must be between 0 and 1.", errors)
        self.assertIn("predictions[1] has unexpected fields: note", errors)

    def test_prediction_contract_examples_stay_aligned_with_gate(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        docs = (repo_root / "docs" / "analysis-spec.md").read_text(encoding="utf-8")
        prompt = (repo_root / "prompts" / "analyze-weekly.md").read_text(encoding="utf-8")

        for content in (docs, prompt):
            self.assertIn("{repo, claim_type, direction, confidence}", content)
            self.assertIn("signal|noise|gap", content)
            self.assertNotIn("{repo, direction, confidence}", content)

    def test_gate_report_fingerprint_tolerates_missing_or_invalid_reports(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            workspace = Path(tmpdir)
            missing = workspace / "missing.json"
            invalid = workspace / "invalid.json"
            report = workspace / "report.json"
            invalid.write_text("not json", encoding="utf-8")
            report.write_text(
                json.dumps({"errors_after_repair": ["date must match the current run timestamp."]}),
                encoding="utf-8",
            )

            self.assertEqual(analysis_gate.gate_report_fingerprint(missing), "")
            self.assertEqual(analysis_gate.gate_report_fingerprint(invalid), "")
            self.assertRegex(analysis_gate.gate_report_fingerprint(report), r"^[0-9a-f]{64}$")

    def test_fallback_frontmatter_dump_handles_empty_dict_list_items(self) -> None:
        original_yaml = analysis_gate.yaml
        try:
            analysis_gate.yaml = None
            dumped = analysis_gate.dump_frontmatter({"predictions": [{}]})
        finally:
            analysis_gate.yaml = original_yaml

        self.assertIn("  - {}", dumped)

    def test_repair_exception_still_writes_gate_report(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            workspace = Path(tmpdir)
            analysis_path = workspace / "candidate.md"
            raw_path = workspace / "raw.json"
            report_path = workspace / "report.json"
            analysis_path.write_text(
                make_analysis(VALID_FRONTMATTER + "\npredictions:\n  - {}", make_body()),
                encoding="utf-8",
            )
            raw_path.write_text('{"week": "2026-W23"}', encoding="utf-8")

            with mock.patch.object(
                analysis_gate, "repair_analysis", side_effect=RuntimeError("boom")
            ):
                with self.assertRaises(SystemExit) as raised:
                    analysis_gate.main(
                        [
                            "--analysis-file",
                            str(analysis_path),
                            "--raw-json",
                            str(raw_path),
                            "--current-datetime",
                            CURRENT_DATETIME,
                            "--repair-safe",
                            "--report-json",
                            str(report_path),
                        ]
                    )

            self.assertEqual(raised.exception.code, 1)
            report = analysis_gate.load_json(report_path)
            self.assertEqual(report["repair_actions"], ["repair skipped: boom"])
            self.assertIn(
                "predictions[1].repo must use owner/repo format.", report["errors_after_repair"]
            )

    def test_gate_report_captures_pre_repair_publish_errors_from_original_text(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            workspace = Path(tmpdir)
            analysis_path = workspace / "candidate.md"
            raw_path = workspace / "raw.json"
            report_path = workspace / "report.json"
            original_text = make_analysis(
                VALID_FRONTMATTER.replace(
                    "date: 2026-06-01T00:00:00Z", "date: 2026-06-01T12:00:00Z"
                ),
                make_body(),
            )
            analysis_path.write_text(original_text, encoding="utf-8")
            raw_path.write_text(json.dumps(RAW_PAYLOAD_WITH_REPOS), encoding="utf-8")

            def publish_quality_for(
                text: str,
                raw_payload: dict,
                *,
                source: str,
                model: str,
                press_context_available: bool = False,
            ) -> tuple[list[str], dict]:
                if text == original_text:
                    return ["pre-repair publish-quality failure"], analysis_gate.build_gate_results(
                        ["pre-repair publish-quality failure"]
                    )
                return [], analysis_gate.build_gate_results([])

            with mock.patch.object(
                analysis_gate, "validate_publish_quality", side_effect=publish_quality_for
            ):
                self.assertEqual(
                    analysis_gate.main(
                        [
                            "--analysis-file",
                            str(analysis_path),
                            "--raw-json",
                            str(raw_path),
                            "--current-datetime",
                            CURRENT_DATETIME,
                            "--repair-safe",
                            "--report-json",
                            str(report_path),
                        ]
                    ),
                    0,
                )

            report = analysis_gate.load_json(report_path)
            self.assertIn("pre-repair publish-quality failure", report["errors_before_repair"])
            self.assertNotIn("pre-repair publish-quality failure", report["errors_after_repair"])

    def test_publish_quality_gate_rejects_structurally_valid_low_quality_summary(self) -> None:
        generic = " ".join(
            ["Projects were active this week and many updates appeared across the list."] * 12
        )
        low_quality = f"""
## This Week's Trends

{generic}

## Where Industry Meets Code

{generic}

## Signal & Noise

{generic}

## Blind Spots

{generic}

## The Week Ahead

{generic}

## Key References

### Notable Projects

- [owner/repo-a](https://github.com/owner/repo-a) — appeared in the list.
- [owner/repo-b](https://github.com/owner/repo-b) — appeared in the list.

### Press & Industry

No press data was provided this week.
""".strip()
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, low_quality),
            RAW_PAYLOAD,
            source="copilot-cli",
            model="copilot-default",
        )

        self.assertTrue(any("editorial analysis" in error for error in errors))
        self.assertFalse(gates["editorial_quality"]["passed"])

    def test_publish_quality_gate_accepts_known_good_weekly_outputs(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        fixtures = [
            (
                "2026-W22",
                "2026-05-25T11:56:08Z",
                "perplexityai/bumblebee",
                repo_root / "data/analyzed/2026-W22-summary.md",
            ),
            (
                "2026-W23",
                "2026-06-06T07:49:43Z",
                "pewdiepie-archdaemon/odysseus",
                repo_root / "data/analyzed/2026-W23-summary.md",
            ),
        ]

        for week, crawled_at, repo_name, summary_path in fixtures:
            with self.subTest(week=week):
                raw_payload = {
                    "week": week,
                    "crawled_at": crawled_at,
                    "new_repos": [{"full_name": repo_name, "stars": 100}],
                    "trending_repos": [],
                }
                text = summary_path.read_text(encoding="utf-8")
                linked_repos = sorted(analysis_gate.REPO_LINK_PATTERN.findall(text))
                raw_payload["new_repos"].extend(
                    {"full_name": name, "stars": 100} for name in linked_repos if name != repo_name
                )

                structure_errors, word_count = analysis_gate.validate_analysis(
                    text, raw_payload, crawled_at
                )
                publish_errors, gates = analysis_gate.validate_publish_quality(
                    text,
                    raw_payload,
                    source="copilot-cli",
                    model="copilot-default",
                )

                self.assertEqual(structure_errors, [])
                self.assertGreater(word_count, 200)
                self.assertEqual(publish_errors, [])
                self.assertTrue(all(gate["passed"] for gate in gates.values()))

    def test_copilot_source_without_explicit_model_uses_publishable_default(self) -> None:
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, make_body()),
            RAW_PAYLOAD_WITH_REPOS,
            source="copilot-cli",
            model=analysis_gate.parse_args(
                [
                    "--analysis-file",
                    "candidate.md",
                    "--raw-json",
                    "raw.json",
                    "--current-datetime",
                    CURRENT_DATETIME,
                    "--source",
                    "copilot-cli",
                ]
            ).model,
        )

        self.assertEqual(errors, [])
        self.assertTrue(gates["ai_provenance"]["passed"])

    def test_publish_quality_gate_rejects_missing_evidence_citations(self) -> None:
        body = (
            make_body()
            .replace("[owner/repo-a](https://github.com/owner/repo-a)", "owner/repo-a")
            .replace(
                "[owner/repo-b](https://github.com/owner/repo-b)",
                "owner/repo-b",
            )
        )
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, body),
            RAW_PAYLOAD_WITH_REPOS,
            source="copilot-cli",
            model="copilot-default",
        )

        self.assertIn(
            "evidence citations must include at least one repository link from the raw payload.",
            errors,
        )
        self.assertFalse(gates["evidence_citation"]["passed"])

    def test_publish_quality_gate_rejects_repo_links_outside_current_inventory(self) -> None:
        body = make_body().replace(
            "[owner/repo-a](https://github.com/owner/repo-a)",
            "[other/repo](https://github.com/other/repo)",
        )
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, body),
            RAW_PAYLOAD_WITH_REPOS,
            source="copilot-cli",
            model="copilot-default",
        )

        self.assertIn(
            "repository links must resolve to the current raw evidence inventory: other/repo.",
            errors,
        )
        self.assertFalse(gates["evidence_citation"]["passed"])

    def test_publish_quality_gate_rejects_stale_evidence(self) -> None:
        stale_payload = dict(RAW_PAYLOAD_WITH_REPOS, crawled_at="2026-05-25T00:00:00Z")
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, make_body()),
            stale_payload,
            source="copilot-cli",
            model="copilot-default",
        )

        self.assertTrue(any("raw evidence timestamp week mismatch" in error for error in errors))
        self.assertFalse(gates["evidence_citation"]["passed"])

    def test_publish_quality_gate_prefers_generated_at_for_republished_evidence(self) -> None:
        republished_payload = dict(
            RAW_PAYLOAD_WITH_REPOS,
            crawled_at="2026-05-25T00:00:00Z",
            generated_at="2026-06-01T00:00:00Z",
        )
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, make_body()),
            republished_payload,
            source="copilot-cli",
            model="copilot-default",
        )

        self.assertEqual(errors, [])
        self.assertTrue(gates["evidence_citation"]["passed"])

    def test_publish_quality_gate_rejects_no_ai_provenance(self) -> None:
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, make_body()),
            RAW_PAYLOAD,
            source="no-ai",
            model="none",
        )

        self.assertIn("AI provenance source is not publishable: no-ai.", errors)
        self.assertIn("AI provenance model is not publishable: none.", errors)
        self.assertFalse(gates["ai_provenance"]["passed"])

    def test_publish_quality_gate_rejects_github_models_provenance(self) -> None:
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, make_body()),
            RAW_PAYLOAD,
            source="github-models",
            model="openai/gpt-4o",
        )

        self.assertIn("AI provenance source is not publishable: github-models.", errors)
        self.assertFalse(gates["ai_provenance"]["passed"])

    def test_gate_report_includes_structured_failure_summary(self) -> None:
        errors = [
            "repository links must resolve to the current raw evidence inventory: other/repo."
        ]
        gates = analysis_gate.build_gate_results(errors)
        summary = analysis_gate.build_failure_summary(errors, gates)

        self.assertEqual(summary["failure_class"], "evidence_citation")
        self.assertEqual(summary["failure_categories"], ["evidence_citation"])
        self.assertEqual(summary["error_count"], 1)

    def test_publish_quality_gate_rejects_contradictory_press_claims(self) -> None:
        body = (
            make_body()
            + "\n\nNo press data was provided this week, but TechCrunch reported a major launch."
        )
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, body),
            RAW_PAYLOAD,
            source="copilot-cli",
            model="copilot-default",
        )

        self.assertTrue(any("contradictory claim" in error for error in errors))
        self.assertFalse(gates["editorial_quality"]["passed"])

    def test_stale_press_claim_fails_when_press_context_available(self) -> None:
        """Regression (2026-W30): body claims no press data while a populated press
        context exists → gate must fail with a 'stale press claim:' error."""
        body = "No industry press data was available for this week's analysis."
        errors = analysis_gate.stale_press_claim_errors(body, press_context_available=True)
        self.assertTrue(any(error.startswith("stale press claim:") for error in errors))

    def test_stale_press_claim_ignored_when_no_press_context(self) -> None:
        """Legitimately press-less weeks must NOT false-positive: the same body with
        press_context_available=False produces no stale-press error."""
        body = "No industry press data was available for this week's analysis."
        errors = analysis_gate.stale_press_claim_errors(body, press_context_available=False)
        self.assertEqual(errors, [])

    def test_stale_press_claim_catches_key_references_variant(self) -> None:
        """The 'No press data was provided this week.' Key References phrasing is also
        caught when a populated press context exists."""
        body = "### Press & Industry\n\nNo press data was provided this week."
        errors = analysis_gate.stale_press_claim_errors(body, press_context_available=True)
        self.assertTrue(any(error.startswith("stale press claim:") for error in errors))
        errors_no_press = analysis_gate.stale_press_claim_errors(
            body, press_context_available=False
        )
        self.assertEqual(errors_no_press, [])

    def test_publish_quality_gate_fails_on_stale_press_claim_with_press_available(self) -> None:
        """End-to-end: validate_publish_quality wires stale_press_claim_errors into the
        editorial_quality gate when press context is available."""
        body = make_body() + "\n\nNo industry press data was available for this week's analysis."
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, body),
            RAW_PAYLOAD,
            source="copilot-cli",
            model="copilot-default",
            press_context_available=True,
        )
        self.assertTrue(any(error.startswith("stale press claim:") for error in errors))
        self.assertFalse(gates["editorial_quality"]["passed"])

    def test_publish_quality_gate_allows_no_press_body_when_press_absent(self) -> None:
        """The same body passes the stale-press rule when there is genuinely no press
        context (the default press_context_available=False)."""
        body = make_body() + "\n\nNo industry press data was available for this week's analysis."
        errors, gates = analysis_gate.validate_publish_quality(
            make_analysis(VALID_FRONTMATTER, body),
            RAW_PAYLOAD,
            source="copilot-cli",
            model="copilot-default",
            press_context_available=False,
        )
        self.assertFalse(any(error.startswith("stale press claim:") for error in errors))

    def test_press_context_is_populated_detects_real_and_empty_context(self) -> None:
        """The helper treats missing/empty files and the render sentinel as empty, but
        real content (or a positive token estimate) as populated."""
        self.assertFalse(analysis_gate.press_context_is_populated(None))
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)

            missing = base / "missing-press-context.md"
            self.assertFalse(analysis_gate.press_context_is_populated(missing))

            empty = base / "empty-press-context.md"
            empty.write_text("", encoding="utf-8")
            self.assertFalse(analysis_gate.press_context_is_populated(empty))

            sentinel = base / "sentinel-press-context.md"
            sentinel.write_text("No press data available for this week.", encoding="utf-8")
            self.assertFalse(analysis_gate.press_context_is_populated(sentinel))

            real = base / "real-press-context.md"
            real.write_text(
                "## Press Context\n\n22 relevant articles about AI agents.",
                encoding="utf-8",
            )
            self.assertTrue(analysis_gate.press_context_is_populated(real))

            # A positive token estimate short-circuits to populated even without a file.
            self.assertTrue(analysis_gate.press_context_is_populated(missing, token_estimate=42))


if __name__ == "__main__":
    unittest.main()

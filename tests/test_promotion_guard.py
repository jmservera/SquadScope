import json
import tempfile
import unittest
from pathlib import Path

from scripts import promotion_guard


WEEK = "2026-W23"
RUN_STARTED_AT = "2026-06-05T21:16:49Z"


GOOD_SUMMARY = """---
title: "Good AI Article"
date: 2026-06-05T21:16:49Z
week: "2026-W23"
year: 2026
tags: [ai]
categories: [weekly]
repos_featured: 1
stars_tracked: 100
top_repo: "owner/good"
quality_score: 90
summary: "A good AI-authored weekly summary."
---

## This Week's Trends

Canonical good analysis.
"""

GOOD_CONTENT = """---
title: "Good AI Article"
week: "2026-W23"
draft: false
---

Canonical good rendered content.
"""

VALID_REPLACEMENT_SUMMARY = GOOD_SUMMARY.replace("Good AI Article", "Better AI Article").replace(
    "Canonical good analysis.", "Better candidate analysis."
)
VALID_REPLACEMENT_CONTENT = GOOD_CONTENT.replace("Good AI Article", "Better AI Article").replace(
    "Canonical good rendered content.", "Better candidate rendered content."
)


def write_file(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def install_existing_good_article(root: Path) -> tuple[Path, Path]:
    summary = write_file(root, "data/analyzed/2026-W23-summary.md", GOOD_SUMMARY)
    content = write_file(root, "content/weekly/2026/W23.md", GOOD_CONTENT)
    return summary, content


def write_candidate(root: Path, name: str, summary: str, content: str) -> tuple[Path, Path]:
    summary_path = write_file(root, f"data/staging/{WEEK}/{name}/summary.md", summary)
    content_path = write_file(root, f"data/staging/{WEEK}/{name}/content.md", content)
    return summary_path, content_path


def write_source_artifact(root: Path, name: str = "raw") -> Path:
    return write_file(root, f"data/raw/{WEEK}-{name}.json", json.dumps({"week": WEEK}) + "\n")


def manifest_for(root: Path, name: str, **overrides) -> Path:
    summary_path, content_path = write_candidate(
        root,
        name,
        overrides.pop("summary", VALID_REPLACEMENT_SUMMARY),
        overrides.pop("content", VALID_REPLACEMENT_CONTENT),
    )
    source_artifact = write_source_artifact(root, name)
    manifest = {
        "schema_version": "publish_eligibility_v1",
        "week": WEEK,
        "run_id": f"{WEEK}-{name}",
        "run_started_at": RUN_STARTED_AT,
        "candidate_summary_path": summary_path.relative_to(root).as_posix(),
        "candidate_content_path": content_path.relative_to(root).as_posix(),
        "promotion_eligible": True,
        "ai_provenance": {
            "source": "copilot-cli",
            "model": "copilot-default",
            "degraded": False,
        },
        "gate_results": {
            "analysis_gate": True,
            "editorial_quality_gate": True,
            "evidence_freshness_gate": True,
        },
        "source_artifacts": [
            {
                "path": source_artifact.relative_to(root).as_posix(),
                "checksum": "sha256:test",
                "generated_at": RUN_STARTED_AT,
                "reused_same_day": False,
                "stale": False,
            }
        ],
    }
    for key, value in overrides.items():
        manifest[key] = value
    manifest_path = root / "data" / "staging" / WEEK / name / "publish-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


class PromotionGuardTests(unittest.TestCase):
    def test_failed_degraded_and_no_ai_candidates_do_not_replace_existing_good_article(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            root = Path(tmpdir)
            canonical_summary, canonical_content = install_existing_good_article(root)
            original_summary = canonical_summary.read_text(encoding="utf-8")
            original_content = canonical_content.read_text(encoding="utf-8")

            blocked_manifests = [
                manifest_for(root, "failed", promotion_eligible=False),
                manifest_for(root, "degraded", ai_provenance={"source": "copilot-cli", "model": "copilot-default", "degraded": True}),
                manifest_for(root, "no-ai", ai_provenance={"source": "no-ai", "model": "none", "degraded": False}),
            ]

            for manifest_path in blocked_manifests:
                with self.assertRaises(promotion_guard.PromotionBlocked):
                    promotion_guard.promote_candidate(manifest_path, root=root)
                self.assertEqual(canonical_summary.read_text(encoding="utf-8"), original_summary)
                self.assertEqual(canonical_content.read_text(encoding="utf-8"), original_content)

            self.assertTrue((root / "data/staging/2026-W23/no-ai/summary.md").exists())
            diagnostics = list((root / "data/diagnostics/promotion").glob("*-blocked.json"))
            self.assertTrue(diagnostics)

    def test_missing_malformed_and_stale_manifests_block_promotion(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            root = Path(tmpdir)
            canonical_summary, _ = install_existing_good_article(root)
            original_summary = canonical_summary.read_text(encoding="utf-8")

            with self.assertRaises(promotion_guard.PromotionBlocked) as missing:
                promotion_guard.promote_candidate(root / "data/staging/2026-W23/missing/publish-manifest.json", root=root)
            self.assertIn("Missing publish eligibility manifest", missing.exception.reasons[0])

            malformed = root / "data/staging/2026-W23/malformed/publish-manifest.json"
            malformed.parent.mkdir(parents=True, exist_ok=True)
            malformed.write_text("{not json", encoding="utf-8")
            with self.assertRaises(promotion_guard.PromotionBlocked) as bad_json:
                promotion_guard.promote_candidate(malformed, root=root)
            self.assertIn("Malformed publish eligibility manifest", bad_json.exception.reasons[0])

            stale_manifest = manifest_for(
                root,
                "stale",
                source_artifacts=[
                    {
                        "path": write_source_artifact(root, "stale").relative_to(root).as_posix(),
                        "checksum": "sha256:stale",
                        "generated_at": "2026-06-04T21:16:49Z",
                        "reused_same_day": False,
                        "stale": True,
                    }
                ],
            )
            with self.assertRaises(promotion_guard.PromotionBlocked) as stale:
                promotion_guard.promote_candidate(stale_manifest, root=root)
            self.assertIn("source_artifacts[1] is stale.", stale.exception.reasons)
            self.assertEqual(canonical_summary.read_text(encoding="utf-8"), original_summary)

    def test_same_successful_rerun_is_stable_and_does_not_duplicate_content(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            root = Path(tmpdir)
            install_existing_good_article(root)
            manifest_path = manifest_for(root, "valid")

            first_summary, first_content = promotion_guard.promote_candidate(manifest_path, root=root)
            first_summary_text = first_summary.read_text(encoding="utf-8")
            first_content_text = first_content.read_text(encoding="utf-8")

            second_summary, second_content = promotion_guard.promote_candidate(manifest_path, root=root)

            self.assertEqual(second_summary.read_text(encoding="utf-8"), first_summary_text)
            self.assertEqual(second_content.read_text(encoding="utf-8"), first_content_text)
            self.assertEqual(second_summary.read_text(encoding="utf-8").count("Better candidate analysis."), 1)
            self.assertEqual(second_content.read_text(encoding="utf-8").count("Better candidate rendered content."), 1)

    def test_same_day_reused_source_candidate_can_promote_when_manifest_is_fresh(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            root = Path(tmpdir)
            install_existing_good_article(root)
            source_artifact = write_source_artifact(root, "same-day-reuse")
            manifest_path = manifest_for(
                root,
                "same-day-reuse",
                source_artifacts=[
                    {
                        "path": source_artifact.relative_to(root).as_posix(),
                        "checksum": "sha256:same-day",
                        "generated_at": "2026-06-05T08:00:00Z",
                        "reused_same_day": True,
                        "stale": False,
                    }
                ],
            )

            summary_path, content_path = promotion_guard.promote_candidate(manifest_path, root=root)

            self.assertIn("Better AI Article", summary_path.read_text(encoding="utf-8"))
            self.assertIn("Better AI Article", content_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

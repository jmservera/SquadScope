import csv
import io
import json
import shutil
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import scripts.export_observatory_dataset as export_observatory_dataset

WORKSPACE_ROOT = Path(".test-workspaces")


class ExportObservatoryDatasetTests(unittest.TestCase):
    def test_public_export_allowlists_are_exact_and_synchronized(self) -> None:
        self.assertEqual(
            export_observatory_dataset.PUBLIC_CSV_FIELDS,
            (
                "rank_by_latest_stars",
                "repository",
                "url",
                "primary_language",
                "latest_license",
                "first_seen_week",
                "last_seen_week",
                "weeks_observed",
                "latest_stars",
                "first_observed_stars",
                "observed_star_change",
                "max_forks_observed",
                "seen_in_trending",
                "seen_in_new",
                "top_topics",
            ),
        )
        self.assertEqual(
            export_observatory_dataset.PUBLIC_TOP_REPOSITORY_FIELDS,
            (
                "repository",
                "latest_stars",
                "observed_star_change",
                "weeks_observed",
                "url",
            ),
        )
        self.assertEqual(
            set(export_observatory_dataset.PUBLIC_METADATA_FIELDS),
            {
                "dataset",
                "version",
                "generated_at",
                "source",
                "selection_rule",
                "license",
                "row_count",
                "weeks",
                "weekly_observation_counts",
                "exported_repo_observations",
                "total_source_repo_observations_screened",
                "recurring_repository_count_min_4_weeks",
                "repositories_seen_in_trending",
                "repositories_seen_in_new",
                "top_languages_by_repository_count",
                "top_licenses_by_repository_count",
                "top_topics_by_repository_mentions",
                "top_repositories_by_latest_stars",
                "fields",
                "source_files",
                "public_exposure_review",
            },
        )

    def test_public_export_rejects_unlisted_fields_and_source_paths(self) -> None:
        valid_row = export_observatory_dataset.RepoAggregate(repository="owner/repo").row(1)
        with self.assertRaisesRegex(ValueError, "public allowlist"):
            export_observatory_dataset.validate_exact_keys(
                {**valid_row, "private_note": "not public"},
                export_observatory_dataset.PUBLIC_CSV_FIELDS,
                "CSV row",
            )

        with self.assertRaisesRegex(ValueError, "outside the public export policy"):
            export_observatory_dataset.public_source_path(
                export_observatory_dataset.PROJECT_ROOT / "data/private/repos.json",
                export_observatory_dataset.PROJECT_ROOT / "data",
            )

        summary = export_observatory_dataset.export_dataset(
            output_dir=WORKSPACE_ROOT / "allowlist-validation"
        )
        self.addCleanup(
            lambda: shutil.rmtree(WORKSPACE_ROOT / "allowlist-validation", ignore_errors=True)
        )
        summary["top_languages_by_repository_count"] = [
            {"language": "Python", "count": 1, "private_note": "not public"}
        ]
        with self.assertRaisesRegex(ValueError, "public label/count pairs"):
            export_observatory_dataset.validate_public_summary(summary)

    def test_check_reports_stale_external_output_path(self) -> None:
        external_path = Path("/tmp/claracle-dataset/dataset-metadata.json")
        stderr = io.StringIO()

        with (
            patch.object(export_observatory_dataset, "check_dataset", return_value=[external_path]),
            redirect_stderr(stderr),
        ):
            result = export_observatory_dataset.main(
                ["--check", "--output-dir", str(external_path.parent)]
            )

        self.assertEqual(result, 1)
        self.assertEqual(stderr.getvalue(), f"stale: {external_path}\n")

    def test_export_dataset_writes_public_mit_dataset(self) -> None:
        output_dir = WORKSPACE_ROOT / "observatory-dataset"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))

        summary = export_observatory_dataset.export_dataset(output_dir=output_dir)

        csv_path = output_dir / "top-github-projects.csv"
        metadata_path = output_dir / "dataset-metadata.json"
        license_path = output_dir / "LICENSE.txt"
        citation_path = output_dir / "CITATION.md"

        self.assertTrue(csv_path.exists())
        self.assertTrue(metadata_path.exists())
        self.assertTrue(license_path.exists())
        self.assertTrue(citation_path.exists())
        self.assertEqual(summary["license"], "MIT")
        self.assertEqual(summary["row_count"], 663)
        self.assertEqual(summary["exported_repo_observations"], 1545)
        self.assertIn("PASS", summary["public_exposure_review"])

        with csv_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), summary["row_count"])
        self.assertEqual(tuple(rows[0]), export_observatory_dataset.PUBLIC_CSV_FIELDS)
        self.assertEqual(rows[0]["repository"], "openclaw/openclaw")
        self.assertEqual(rows[0]["seen_in_trending"], "true")
        self.assertIn("ai", rows[0]["top_topics"])

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(set(metadata), set(export_observatory_dataset.PUBLIC_METADATA_FIELDS))
        self.assertEqual(metadata["fields"], list(export_observatory_dataset.PUBLIC_CSV_FIELDS))
        self.assertTrue(
            all(
                set(repository) == set(export_observatory_dataset.PUBLIC_TOP_REPOSITORY_FIELDS)
                for repository in metadata["top_repositories_by_latest_stars"]
            )
        )
        self.assertEqual(
            set(metadata["weekly_observation_counts"]),
            set(metadata["weeks"]),
        )
        self.assertEqual(metadata["source_files"], summary["source_files"])
        self.assertEqual(len(metadata["source_files"]), 11)
        self.assertTrue(
            all(
                source.startswith(("data/raw/", "data/archive/recovered-W23-W29/"))
                for source in metadata["source_files"]
            )
        )
        self.assertIn("MIT License", license_path.read_text(encoding="utf-8"))
        citation = citation_path.read_text(encoding="utf-8")
        self.assertIn(
            "https://claracle.com/datasets/open-source-ai-github-projects-2026/top-github-projects.csv",
            citation,
        )
        self.assertIn("GitHub repository search", citation)

    def test_state_of_page_links_to_dataset_and_hubs_link_back(self) -> None:
        root = export_observatory_dataset.PROJECT_ROOT
        page = (root / "content" / "state-of" / "open-source-ai-2026.md").read_text(
            encoding="utf-8"
        )
        topic_hub = (root / "content" / "topics" / "open-source-llms" / "_index.md").read_text(
            encoding="utf-8"
        )
        topics_index = (root / "content" / "topics" / "_index.md").read_text(encoding="utf-8")

        stable_csv_url = "/datasets/open-source-ai-github-projects-2026/top-github-projects.csv"
        state_of_url = "/state-of/open-source-ai-2026/"
        self.assertIn(stable_csv_url, page)
        self.assertIn("/datasets/open-source-ai-github-projects-2026/LICENSE.txt", page)
        self.assertIn("/datasets/open-source-ai-github-projects-2026/CITATION.md", page)
        self.assertIn("Hermes exposure check: **pass**", page)
        self.assertIn(state_of_url, topic_hub)
        self.assertIn(state_of_url, topics_index)

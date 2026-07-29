import csv
import json
import shutil
import unittest
from pathlib import Path

import scripts.export_observatory_dataset as export_observatory_dataset

WORKSPACE_ROOT = Path(".test-workspaces")


class ExportObservatoryDatasetTests(unittest.TestCase):
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
        self.assertEqual(rows[0]["repository"], "openclaw/openclaw")
        self.assertEqual(rows[0]["seen_in_trending"], "true")
        self.assertIn("ai", rows[0]["top_topics"])

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["source_files"], summary["source_files"])
        self.assertEqual(len(metadata["source_files"]), 11)
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
        topic_hub = (root / "content" / "topics" / "ai-ml" / "_index.md").read_text(
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

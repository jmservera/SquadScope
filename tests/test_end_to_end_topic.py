#!/usr/bin/env python3
"""End-to-end integration test for the SquadScope topic pipeline with ai-ml config.

Exercises the full pipeline: validate → crawl (mocked) → score → quality gate →
prediction ledger → content verification, using realistic AI/ML mock data.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MOCK_REPOS = [
    {
        "full_name": "org/pytorch-trainer",
        "language": "Python",
        "topics": ["machine-learning", "pytorch", "deep-learning"],
        "stars": 500,
        "stars_gained": 50,
        "forks": 80,
        "created_at": "2024-06-01T00:00:00Z",
        "description": "High-performance PyTorch training framework",
    },
    {
        "full_name": "org/llm-finetune",
        "language": "Python",
        "topics": ["llm", "transformers", "machine-learning"],
        "stars": 1200,
        "stars_gained": 200,
        "forks": 150,
        "created_at": "2024-03-15T00:00:00Z",
        "description": "Fine-tuning toolkit for large language models",
    },
    {
        "full_name": "org/neural-notebook",
        "language": "Jupyter Notebook",
        "topics": ["deep-learning", "neural-network"],
        "stars": 80,
        "stars_gained": 30,
        "forks": 12,
        "created_at": "2025-01-10T00:00:00Z",
        "description": "Interactive notebooks for neural network experiments",
    },
    {
        "full_name": "org/ai-image-gen",
        "language": "Python",
        "topics": ["artificial-intelligence", "deep-learning", "transformers"],
        "stars": 3000,
        "stars_gained": 400,
        "forks": 500,
        "created_at": "2023-11-20T00:00:00Z",
        "description": "State-of-the-art image generation with diffusion models",
    },
    {
        "full_name": "org/ml-pipeline",
        "language": "Python",
        "topics": ["machine-learning", "mlops"],
        "stars": 250,
        "stars_gained": 35,
        "forks": 40,
        "created_at": "2024-09-01T00:00:00Z",
        "description": "End-to-end ML pipeline orchestration",
    },
    {
        "full_name": "org/transformer-serving",
        "language": "Python",
        "topics": ["transformers", "llm", "inference"],
        "stars": 900,
        "stars_gained": 120,
        "forks": 95,
        "created_at": "2024-05-01T00:00:00Z",
        "description": "Scalable transformer model serving",
    },
    {
        "full_name": "org/rust-cli-tool",
        "language": "Rust",
        "topics": ["cli-tool", "developer-tools"],
        "stars": 300,
        "stars_gained": 15,
        "forks": 20,
        "created_at": "2024-07-01T00:00:00Z",
        "description": "Fast CLI utility written in Rust",
    },
    {
        "full_name": "org/web-dashboard",
        "language": "JavaScript",
        "topics": ["web", "dashboard", "react"],
        "stars": 400,
        "stars_gained": 25,
        "forks": 50,
        "created_at": "2024-04-01T00:00:00Z",
        "description": "Modern web dashboard framework",
    },
    {
        "full_name": "org/tiny-nn",
        "language": "Python",
        "topics": ["neural-network", "deep-learning"],
        "stars": 150,
        "stars_gained": 45,
        "forks": 25,
        "created_at": "2025-02-01T00:00:00Z",
        "description": "Minimal neural network library for education",
    },
    {
        "full_name": "org/data-viz",
        "language": "JavaScript",
        "topics": ["visualization", "charts"],
        "stars": 600,
        "stars_gained": 20,
        "forks": 70,
        "created_at": "2023-06-01T00:00:00Z",
        "description": "Data visualization library",
    },
]

# Raw data format expected by prediction_ledger
MOCK_RAW_DATA = {
    "week": "2025-W25",
    "new_repos": MOCK_REPOS[:5],
    "trending_repos": MOCK_REPOS[5:],
}

MOCK_SUMMARY_CONTENT = """---
topic: ai-ml
week: 2025-W25
repos_scored: 8
---

# AI & ML Weekly Digest — 2025-W25

## Highlights

- [org/pytorch-trainer](https://github.com/org/pytorch-trainer) — High-performance training
- [org/llm-finetune](https://github.com/org/llm-finetune) — LLM fine-tuning toolkit
- [org/ai-image-gen](https://github.com/org/ai-image-gen) — Diffusion image generation
- [org/transformer-serving](https://github.com/org/transformer-serving) — Model serving at scale
"""


class TestEndToEndTopicPipeline(unittest.TestCase):
    """Full pipeline integration test with ai-ml topic config."""

    def setUp(self):
        """Create temp directory structure with ai-ml config and mock data."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

        # Copy the real ai-ml config
        src_config = REPO_ROOT / "squadscope.topic.yml"
        self.config_path = self.work_dir / "squadscope.topic.yml"
        shutil.copy(src_config, self.config_path)

        # Create data directories
        self.raw_path = self.work_dir / "data" / "raw" / "ai-ml"
        self.analyzed_path = self.work_dir / "data" / "analyzed" / "ai-ml"
        self.metrics_path = self.work_dir / "data" / "metrics" / "ai-ml"
        for d in (self.raw_path, self.analyzed_path, self.metrics_path):
            d.mkdir(parents=True, exist_ok=True)

        # Write mock raw crawl data (list format for score_repos)
        self.raw_json_path = self.raw_path / "2025-W25.json"
        self.raw_json_path.write_text(json.dumps(MOCK_REPOS, indent=2), encoding="utf-8")

        # Write raw data in dict format for prediction_ledger
        self.raw_dict_path = self.raw_path / "2025-W25-full.json"
        self.raw_dict_path.write_text(json.dumps(MOCK_RAW_DATA, indent=2), encoding="utf-8")

        # Write mock summary for prediction ledger
        self.summary_path = self.analyzed_path / "2025-W25-summary.md"
        self.summary_path.write_text(MOCK_SUMMARY_CONTENT, encoding="utf-8")

        # Change to work dir so relative paths in scripts work
        self._orig_cwd = os.getcwd()
        os.chdir(self.work_dir)

    def tearDown(self):
        os.chdir(self._orig_cwd)
        self.temp_dir.cleanup()

    def test_full_pipeline_ai_ml(self):
        """Run the full pipeline: validate → score → quality gate → predictions."""
        import sys

        sys.path.insert(0, str(REPO_ROOT))

        from scripts.prediction_ledger import append_predictions, generate_predictions
        from scripts.quality_gate import check_quality, get_quality_config, write_metric
        from scripts.score_repos import get_scoring_config, load_config, score_repos
        from scripts.validate_topic_config import validate_file

        # --- Stage 1: Validate config ---
        config_model = validate_file(str(self.config_path))
        self.assertEqual(config_model.topic.id, "ai-ml")
        self.assertEqual(config_model.topic.name, "AI & Machine Learning")
        self.assertGreater(len(config_model.queries.primary), 0)
        self.assertIn("Python", config_model.scoring.language_boost)

        # --- Stage 2: Mock crawl data already created in setUp ---
        raw_repos = json.loads(self.raw_json_path.read_text(encoding="utf-8"))
        self.assertEqual(len(raw_repos), 10)

        # --- Stage 3: Score repos ---
        config = load_config(self.config_path)
        scoring_config = get_scoring_config(config)
        scored = score_repos(raw_repos, scoring_config)

        # Verify scoring filters and ranks correctly
        self.assertGreater(len(scored), 0)
        self.assertLessEqual(len(scored), len(raw_repos))

        # All scored repos should meet minimum relevance threshold
        min_score = scoring_config["min_relevance_score"]
        for repo in scored:
            self.assertGreaterEqual(repo["relevance_score"], min_score)
            self.assertIn("relevance_score", repo)

        # Verify sorted descending
        scores = [r["relevance_score"] for r in scored]
        self.assertEqual(scores, sorted(scores, reverse=True))

        # AI/ML repos should score higher than non-AI repos
        ai_repos = [
            r
            for r in scored
            if r["full_name"] in ("org/pytorch-trainer", "org/llm-finetune", "org/ai-image-gen")
        ]
        non_ai_repos = [
            r
            for r in scored
            if r["full_name"] in ("org/rust-cli-tool", "org/web-dashboard", "org/data-viz")
        ]
        if ai_repos and non_ai_repos:
            max_non_ai = max(r["relevance_score"] for r in non_ai_repos)
            min_ai = min(r["relevance_score"] for r in ai_repos)
            self.assertGreater(min_ai, max_non_ai, "AI/ML repos should outscore non-AI repos")

        # Write scored output for quality gate
        scored_path = self.work_dir / "scored.json"
        scored_path.write_text(json.dumps(scored, indent=2), encoding="utf-8")

        # --- Stage 4: Quality gate ---
        quality_config = get_quality_config(config)
        scoring_cfg = config.get("scoring", {})
        metric = check_quality(scored, quality_config, scoring_cfg)

        self.assertIn("repos_scored", metric)
        self.assertIn("repos_passing", metric)
        self.assertIn("status", metric)
        self.assertIn("warnings", metric)
        self.assertGreater(metric["repos_scored"], 0)

        # Write metric file
        week = "2025-W25"
        metric_path = write_metric("ai-ml", metric, week)
        self.assertTrue(metric_path.exists())
        metric_data = json.loads(metric_path.read_text(encoding="utf-8"))
        self.assertEqual(metric_data["topic"], "ai-ml")
        self.assertEqual(metric_data["week"], week)

        # --- Stage 5: Prediction ledger ---
        summary_content = self.summary_path.read_text(encoding="utf-8")
        raw_data = json.loads(self.raw_dict_path.read_text(encoding="utf-8"))
        predictions = generate_predictions(summary_content, raw_data, week)

        self.assertGreaterEqual(len(predictions), 1)
        self.assertLessEqual(len(predictions), 5)

        for pred in predictions:
            self.assertIn("week", pred)
            self.assertIn("repo", pred)
            self.assertIn("prediction", pred)
            self.assertIn("confidence", pred)
            self.assertIn("reason", pred)
            self.assertEqual(pred["week"], week)
            self.assertGreater(pred["confidence"], 0)
            self.assertIn(
                pred["prediction"],
                [
                    "rising_star",
                    "emerging_topic",
                    "momentum_shift",
                    "breakout_candidate",
                    "declining_signal",
                ],
            )

        # Write predictions to ledger
        predictions_path = self.metrics_path / "predictions.jsonl"
        append_predictions(predictions, predictions_path)
        self.assertTrue(predictions_path.exists())

        # Verify JSONL format
        lines = predictions_path.read_text(encoding="utf-8").strip().split("\n")
        self.assertEqual(len(lines), len(predictions))
        for line in lines:
            entry = json.loads(line)
            self.assertIn("repo", entry)
            self.assertIn("prediction", entry)

        # --- Stage 6: Content generation verification ---
        # Verify scored data is suitable for content generation
        top_repos = scored[:5]
        for repo in top_repos:
            self.assertIn("full_name", repo)
            self.assertIn("description", repo)
            self.assertIn("relevance_score", repo)
            # Verify topic-specific content (not generic)
            topics = repo.get("topics", [])
            ai_topics = {
                "machine-learning",
                "deep-learning",
                "artificial-intelligence",
                "neural-network",
                "llm",
                "transformers",
            }
            has_ai_topic = bool(set(t.lower() for t in topics) & ai_topics)
            self.assertTrue(has_ai_topic, f"Top repo {repo['full_name']} should have AI/ML topics")

    def test_config_validation_rejects_invalid(self):
        """Ensure validate rejects malformed configs."""
        import sys

        sys.path.insert(0, str(REPO_ROOT))
        from scripts.validate_topic_config import validate_file

        # Write an invalid config (missing required fields)
        bad_config = self.work_dir / "bad.yml"
        bad_config.write_text("topic:\n  id: INVALID ID WITH SPACES\n", encoding="utf-8")

        with self.assertRaises(Exception):
            validate_file(str(bad_config))

    def test_scoring_respects_language_boost(self):
        """Verify Python repos get a language boost over unlisted languages."""
        import sys

        sys.path.insert(0, str(REPO_ROOT))
        from scripts.score_repos import compute_relevance_score, get_scoring_config, load_config

        config = load_config(self.config_path)
        scoring_config = get_scoring_config(config)

        base_repo = {
            "full_name": "test/repo",
            "stars": 500,
            "stars_gained": 50,
            "topics": ["machine-learning"],
            "created_at": "2024-06-01T00:00:00Z",
        }

        python_repo = {**base_repo, "language": "Python"}
        rust_repo = {**base_repo, "language": "Rust"}

        python_score = compute_relevance_score(python_repo, scoring_config)
        rust_score = compute_relevance_score(rust_repo, scoring_config)

        self.assertGreater(
            python_score, rust_score, "Python should score higher with language_boost configured"
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts import validate_predictions


WORKSPACE_ROOT = Path(__file__).resolve().parent / "_workspace_validate_predictions"


def teardown_module() -> None:
    shutil.rmtree(WORKSPACE_ROOT, ignore_errors=True)


def prepare_workspace(name: str) -> Path:
    workspace = WORKSPACE_ROOT / name
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)
    return workspace


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


WEEKLY_SUMMARY = """---
week: 2026-W21
generated_at: 2026-06-01T00:00:00Z
category: dev-tools
tags:
  - agents
summary: Validation fixture.
quality_score: 74
predictions:
  - repo: acme/launchpad
    claim_type: signal
    direction: up
    confidence: 0.8
  - repo: acme/flashy-kit
    claim_type: noise
    direction: flat
    confidence: 0.7
---

## Signal & Noise

The durable signal this week is [acme/launchpad](https://github.com/acme/launchpad), which is finding repeat users.

The noise this week is [acme/flashy-kit](https://github.com/acme/flashy-kit), which looks more like a demo spike than a habit loop.

## Blind Spots

Small teams still need [acme/gap-tool](https://github.com/acme/gap-tool), but the category is not mature yet.
"""


COMBINED_SUMMARY = """---
week: 2026-W22
generated_at: 2026-06-01T00:00:00Z
category: dev-tools
tags:
  - agents
summary: Second fixture.
quality_score: 81
---

## Signal & Noise

The durable signal this week is [acme/steady-core](https://github.com/acme/steady-core), which has a real operator workflow behind it.

The noise this week is [acme/flashy-kit](https://github.com/acme/flashy-kit), which is already cooling.

## Blind Spots

Nobody has fully solved [acme/gap-tool](https://github.com/acme/gap-tool) yet.
"""


RAW_W21 = {
    "new_repos": [
        {"full_name": "acme/launchpad", "stars": 100},
        {"full_name": "acme/flashy-kit", "stars": 100},
        {"full_name": "acme/gap-tool", "stars": 80},
    ],
    "trending_repos": [],
}

RAW_W22 = {
    "new_repos": [
        {"full_name": "acme/launchpad", "stars": 130},
        {"full_name": "acme/gap-tool", "stars": 100},
    ],
    "trending_repos": [
        {"full_name": "acme/steady-core", "stars": 90},
    ],
}


def test_infer_predictions_from_current_summary_patterns() -> None:
    summary_path = Path("data/analyzed/2026-W23-summary.md")
    predictions = validate_predictions.load_summary_predictions(summary_path)
    claims = {(prediction.claim, prediction.repo) for prediction in predictions}

    assert ("signal", "duncatzat/vigils") in claims
    assert ("signal", "openai/role-specific-plugins") in claims
    assert ("noise", "pewdiepie-archdaemon/odysseus") in claims


def test_frontmatter_predictions_use_explicit_claim_type() -> None:
    workspace = prepare_workspace("frontmatter-claim-type")
    summary_path = workspace / "2026-W21-summary.md"
    summary_text = WEEKLY_SUMMARY.replace(
        "  - repo: acme/launchpad\n    claim_type: signal\n    direction: up\n    confidence: 0.8",
        "  - repo: acme/launchpad\n    claim_type: gap\n    direction: up\n    confidence: 0.8",
    )
    write_file(summary_path, summary_text)

    predictions = validate_predictions.load_summary_predictions(summary_path)
    indexed = {prediction.repo: prediction for prediction in predictions}

    assert indexed["acme/launchpad"].source == "frontmatter"
    assert indexed["acme/launchpad"].claim == "gap"
    assert indexed["acme/launchpad"].direction == "up"
    assert indexed["acme/flashy-kit"].claim == "noise"


def test_missing_baseline_repo_becomes_insufficient_evidence() -> None:
    workspace = prepare_workspace("missing-baseline")
    raw_dir = workspace / "raw"

    prediction = validate_predictions.Prediction(
        week="2026-W21",
        repo="acme/missing-baseline",
        claim="signal",
        direction="up",
        confidence=0.8,
        source="frontmatter",
        source_path="fixture.md",
    )

    write_json(raw_dir / "2026-W21.json", RAW_W21)
    write_json(raw_dir / "2026-W22.json", RAW_W22)

    result = validate_predictions.evaluate_prediction(prediction, raw_dir, weeks_ahead=4)

    assert result.verdict == "insufficient_evidence"
    assert result.baseline_stars is None
    assert result.observed_stars is None
    assert "prediction-week crawl" in result.note



def test_missing_observed_repo_becomes_insufficient_evidence() -> None:
    workspace = prepare_workspace("missing-observed")
    raw_dir = workspace / "raw"

    prediction = validate_predictions.Prediction(
        week="2026-W21",
        repo="acme/flashy-kit",
        claim="noise",
        direction="flat",
        confidence=0.7,
        source="frontmatter",
        source_path="fixture.md",
    )

    write_json(raw_dir / "2026-W21.json", RAW_W21)
    write_json(raw_dir / "2026-W22.json", RAW_W22)

    result = validate_predictions.evaluate_prediction(prediction, raw_dir, weeks_ahead=4)

    assert result.verdict == "insufficient_evidence"
    assert result.baseline_stars == 100
    assert result.observed_stars is None
    assert "later crawl payload" in result.note



def test_run_validation_writes_markdown_and_json_scorecards() -> None:
    workspace = prepare_workspace("run-validation")
    analyzed_dir = workspace / "analyzed"
    raw_dir = workspace / "raw"
    metrics_dir = workspace / "metrics"
    scorecard_dir = workspace / "scorecards"

    write_file(analyzed_dir / "2026-W21-summary.md", WEEKLY_SUMMARY)
    write_file(analyzed_dir / "2026-W22-summary.md", COMBINED_SUMMARY)
    write_json(raw_dir / "2026-W21.json", RAW_W21)
    write_json(raw_dir / "2026-W22.json", RAW_W22)

    summary = validate_predictions.run_validation(
        analyzed_dir=analyzed_dir,
        raw_dir=raw_dir,
        metrics_dir=metrics_dir,
        scorecard_dir=scorecard_dir,
        report_week="2026-W23",
    )

    assert summary.week == "2026-W23"
    assert summary.total_predictions == 5
    assert summary.validated == 1
    assert summary.correct == 1
    assert summary.incorrect == 0
    assert summary.quality_trend["count"] == 2

    markdown_path = scorecard_dir / "2026-W23.md"
    json_path = metrics_dir / "scorecards" / "2026-W23-scorecard.json"

    assert markdown_path.exists()
    assert json_path.exists()
    assert "Prediction Registry Format" in markdown_path.read_text(encoding="utf-8")

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["validated"] == 1
    assert payload["total_validated"] == 1
    assert payload["accuracy"] == 1.0

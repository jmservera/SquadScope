#!/usr/bin/env python3
"""Validate analysis predictions against later raw-star outcomes.

Prediction registry format for future weekly summaries:

```yaml
predictions:
  - repo: owner/repo
    claim_type: signal
    direction: up
    confidence: 0.72
```

Required fields:
- `repo`: GitHub repo in `owner/name` form.
- `claim_type`: one of `signal`, `noise`, or `gap`.
- `direction`: one of `up`, `flat`, or `down`.
- `confidence`: float from 0.0 to 1.0.

The validator will use frontmatter predictions when present. For legacy summaries
without a registry, it infers repo-level calls from Signal/Noise/Gaps prose.
It writes:
- `.squad/reskill/scorecards/YYYY-WNN.md` for editorial review
- `data/metrics/scorecards/YYYY-WNN-scorecard.json` for reskill ingestion
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import analysis_gate, track_quality

DEFAULT_ANALYZED_DIR = ROOT / "data" / "analyzed"
DEFAULT_RAW_DIR = ROOT / "data" / "raw"
DEFAULT_METRICS_DIR = ROOT / "data" / "metrics"
DEFAULT_SCORECARD_DIR = ROOT / ".squad" / "reskill" / "scorecards"
DEFAULT_SNAPSHOTS_DIR = ROOT / "data" / "snapshots"

REPO_LINK_PATTERN = re.compile(r"\[(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\]\(https://github\.com/[^)]+\)")
WEEK_PATTERN = re.compile(r"^(\d{4}-W\d{2})$")
RAW_WEEK_PATTERN = re.compile(r"^(\d{4}-W\d{2})\.json$")
SNAPSHOT_WEEK_PATTERN = re.compile(r"^(\d{4}-W\d{2})-stars\.json$")
HEADING_PATTERN = re.compile(r"(?m)^(#{2,3})\s+(.+?)\s*$")
SIGNAL_HINTS = ("durable signal", "strongest signal", "credible signal", "signal this week")
NOISE_HINTS = ("noise this week", "the noise", "coordination", "spam cluster", "manipulation campaign")
TOP_REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")


@dataclass(frozen=True)
class Prediction:
    week: str
    repo: str
    claim: str
    direction: str
    confidence: float
    source: str
    source_path: str


@dataclass(frozen=True)
class ValidationResult:
    week: str
    repo: str
    claim: str
    direction: str
    confidence: float
    source: str
    source_path: str
    baseline_week: str
    observed_week: str | None
    weeks_observed: int
    baseline_stars: int | None
    observed_stars: int | None
    delta_stars: int | None
    delta_pct: float | None
    score: float | None
    verdict: str
    note: str


@dataclass(frozen=True)
class ScorecardSummary:
    week: str
    date: str
    total_predictions: int
    validated: int
    correct: int
    incorrect: int
    accuracy: float
    by_type: dict[str, dict[str, float | int]]
    by_direction: dict[str, dict[str, float | int]]
    quality_trend: dict[str, Any]
    details: list[dict[str, Any]]
    insufficient_evidence: list[dict[str, Any]]


class ValidationError(ValueError):
    """Raised when a prediction registry entry is malformed."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate weekly Signal/Noise/Gaps calls against later raw star data.")
    parser.add_argument("--analyzed-dir", type=Path, default=DEFAULT_ANALYZED_DIR, help="Directory containing analyzed summaries.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR, help="Directory containing raw weekly JSON payloads.")
    parser.add_argument("--snapshots-dir", type=Path, default=DEFAULT_SNAPSHOTS_DIR, help="Optional legacy snapshots directory; used when raw weekly JSON is unavailable.")
    parser.add_argument("--metrics-dir", type=Path, default=DEFAULT_METRICS_DIR, help="Directory for machine-readable scorecards.")
    parser.add_argument("--scorecard-dir", "--scorecards-dir", dest="scorecard_dir", type=Path, default=DEFAULT_SCORECARD_DIR, help="Directory for markdown scorecards.")
    parser.add_argument("--weeks-ahead", type=int, default=4, help="Maximum lookahead window in ISO weeks (default: 4).")
    parser.add_argument("--report-week", help="Override the scorecard week slug. Defaults to the current ISO week.")
    parser.add_argument("--current-datetime", help="Optional ISO timestamp used to derive the default report week.")
    return parser.parse_args(argv)


def iso_week_to_date(week_str: str) -> datetime:
    year, week_num = week_str.split("-W")
    return datetime.strptime(f"{year}-W{int(week_num):02d}-1", "%G-W%V-%u").replace(tzinfo=UTC)


def current_iso_week(now: datetime | None = None) -> str:
    current = now or datetime.now(tz=UTC)
    year, week, _ = current.isocalendar()
    return f"{year}-W{week:02d}"


def week_offset(week_str: str, offset: int) -> str:
    shifted = iso_week_to_date(week_str) + timedelta(weeks=offset)
    year, week, _ = shifted.isocalendar()
    return f"{year}-W{week:02d}"


def week_distance(start_week: str, end_week: str) -> int:
    return int((iso_week_to_date(end_week) - iso_week_to_date(start_week)).days / 7)


def load_json_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_raw_week(raw_directory: Path, week_str: str) -> dict[str, Any] | None:
    return load_json_file(raw_directory / f"{week_str}.json")


def load_snapshot_week(snapshot_directory: Path | None, week_str: str) -> dict[str, Any] | None:
    if snapshot_directory is None:
        return None
    payload = load_json_file(snapshot_directory / f"{week_str}-stars.json")
    if not payload:
        return None
    stars = payload.get("stars")
    if not isinstance(stars, dict):
        return None
    repos = [{"full_name": repo, "stars": value} for repo, value in stars.items()]
    return {"new_repos": repos, "trending_repos": []}


def list_available_raw_weeks(raw_directory: Path, snapshot_directory: Path | None = None) -> list[str]:
    weeks: set[str] = set()
    if raw_directory.exists():
        for path in raw_directory.glob("*.json"):
            match = RAW_WEEK_PATTERN.match(path.name)
            if match:
                weeks.add(match.group(1))
    if snapshot_directory and snapshot_directory.exists():
        for path in snapshot_directory.glob("*.json"):
            match = SNAPSHOT_WEEK_PATTERN.match(path.name)
            if match:
                weeks.add(match.group(1))
    return sorted(weeks)


def build_repo_stars(raw_data: dict[str, Any]) -> dict[str, int]:
    stars: dict[str, int] = {}
    for section in ("new_repos", "trending_repos"):
        for repo in raw_data.get(section, []):
            full_name = repo.get("full_name")
            if isinstance(full_name, str) and full_name:
                stars[full_name] = int(repo.get("stars", 0) or 0)
    return stars


def build_repo_set(raw_data: dict[str, Any]) -> set[str]:
    return set(build_repo_stars(raw_data))


def extract_repo_links(text: str) -> list[str]:
    seen: set[str] = set()
    repos: list[str] = []
    for match in REPO_LINK_PATTERN.finditer(text):
        repo = match.group("repo")
        if repo not in seen:
            repos.append(repo)
            seen.add(repo)
    return repos


def split_markdown_sections(body: str) -> list[tuple[str, str]]:
    matches = list(HEADING_PATTERN.finditer(body))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        title = match.group(2).strip()
        content = body[start:end].strip()
        sections.append((title, content))
    return sections


def split_paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]


def normalize_direction(value: str) -> str:
    direction = value.strip().lower()
    if direction not in {"up", "flat", "down"}:
        raise ValidationError(f"Unsupported prediction direction: {value!r}")
    return direction


def normalize_confidence(value: Any) -> float:
    if isinstance(value, bool):
        raise ValidationError("confidence must be numeric, not boolean")
    if not isinstance(value, (int, float)):
        raise ValidationError("confidence must be numeric")
    confidence = float(value)
    if confidence < 0.0 or confidence > 1.0:
        raise ValidationError("confidence must be between 0.0 and 1.0")
    return round(confidence, 2)


def normalize_claim_type(value: str) -> str:
    claim_type = value.strip().lower()
    if claim_type not in {"signal", "noise", "gap"}:
        raise ValidationError(f"Unsupported prediction claim_type: {value!r}")
    return claim_type


def normalize_frontmatter_predictions(frontmatter: dict[str, Any], week: str, source_path: str) -> list[Prediction]:
    raw_predictions = frontmatter.get("predictions")
    if raw_predictions is None:
        return []
    if not isinstance(raw_predictions, list):
        raise ValidationError("predictions frontmatter must be a list")

    predictions: list[Prediction] = []
    for entry in raw_predictions:
        if not isinstance(entry, dict):
            raise ValidationError("each predictions entry must be a mapping")
        repo = entry.get("repo")
        if not isinstance(repo, str) or not TOP_REPO_PATTERN.fullmatch(repo.strip()):
            raise ValidationError("predictions repo must use owner/repo format")
        claim = normalize_claim_type(str(entry.get("claim_type", "")))
        direction = normalize_direction(str(entry.get("direction", "")))
        confidence = normalize_confidence(entry.get("confidence"))
        predictions.append(
            Prediction(
                week=week,
                repo=repo.strip(),
                claim=claim,
                direction=direction,
                confidence=confidence,
                source="frontmatter",
                source_path=source_path,
            )
        )
    return predictions


def build_inferred_prediction(week: str, repo: str, claim: str, source_path: str) -> Prediction:
    direction = {"signal": "up", "noise": "flat", "gap": "up"}[claim]
    confidence = {"signal": 0.65, "noise": 0.7, "gap": 0.55}[claim]
    return Prediction(
        week=week,
        repo=repo,
        claim=claim,
        direction=direction,
        confidence=confidence,
        source="inferred",
        source_path=source_path,
    )


def infer_predictions_from_body(body: str, week: str, source_path: str) -> list[Prediction]:
    predictions: list[Prediction] = []
    seen: set[tuple[str, str]] = set()

    def add_prediction(claim: str, repo: str) -> None:
        key = (claim, repo)
        if key in seen:
            return
        seen.add(key)
        predictions.append(build_inferred_prediction(week, repo, claim, source_path))

    for title, content in split_markdown_sections(body):
        lower = title.lower()
        if lower == "signal":
            for repo in extract_repo_links(content):
                add_prediction("signal", repo)
        elif lower == "noise":
            for repo in extract_repo_links(content):
                add_prediction("noise", repo)
        elif lower in {"gaps", "blind spots"} or "what's missing" in lower:
            for repo in extract_repo_links(content):
                add_prediction("gap", repo)
        elif lower == "signal & noise":
            for paragraph in split_paragraphs(content):
                para_lower = paragraph.lower()
                repos = extract_repo_links(paragraph)
                if not repos:
                    continue
                if any(hint in para_lower for hint in NOISE_HINTS):
                    for repo in repos:
                        add_prediction("noise", repo)
                elif any(hint in para_lower for hint in SIGNAL_HINTS) or "signal" in para_lower:
                    for repo in repos:
                        add_prediction("signal", repo)

    return predictions


def load_summary_predictions(summary_path: Path) -> list[Prediction]:
    text = summary_path.read_text(encoding="utf-8")
    frontmatter, body = analysis_gate.extract_frontmatter(text)
    week = frontmatter.get("week")
    if not isinstance(week, str) or not WEEK_PATTERN.fullmatch(week):
        return []

    source_path = str(summary_path.relative_to(ROOT)) if summary_path.is_relative_to(ROOT) else str(summary_path)
    frontmatter_predictions = normalize_frontmatter_predictions(frontmatter, week, source_path)
    if frontmatter_predictions:
        return frontmatter_predictions
    return infer_predictions_from_body(body, week, source_path)


def expected_growth(direction: str, confidence: float, weeks_observed: int) -> float:
    scale = max(weeks_observed, 1) / 4.0
    if direction == "up":
        return max(0.03, (0.12 + (confidence * 0.28)) * scale)
    if direction == "flat":
        return max(0.02, (0.20 - (confidence * 0.12)) * scale)
    return max(0.01, (0.05 - (confidence * 0.03)) * scale)


def locate_observed_week(raw_directory: Path, prediction_week: str, weeks_ahead: int, snapshot_directory: Path | None = None) -> str | None:
    available = list_available_raw_weeks(raw_directory, snapshot_directory)
    candidates = [
        week
        for week in available
        if week_distance(prediction_week, week) > 0 and week_distance(prediction_week, week) <= weeks_ahead
    ]
    return candidates[-1] if candidates else None


def evaluate_prediction(prediction: Prediction, raw_directory: Path, weeks_ahead: int, snapshot_directory: Path | None = None) -> ValidationResult:
    baseline_raw = load_raw_week(raw_directory, prediction.week) or load_snapshot_week(snapshot_directory, prediction.week)
    if baseline_raw is None:
        return ValidationResult(
            week=prediction.week,
            repo=prediction.repo,
            claim=prediction.claim,
            direction=prediction.direction,
            confidence=prediction.confidence,
            source=prediction.source,
            source_path=prediction.source_path,
            baseline_week=prediction.week,
            observed_week=None,
            weeks_observed=0,
            baseline_stars=None,
            observed_stars=None,
            delta_stars=None,
            delta_pct=None,
            score=None,
            verdict="insufficient_evidence",
            note="No raw payload exists for the prediction week.",
        )

    baseline_stars_map = build_repo_stars(baseline_raw)
    if prediction.repo not in baseline_stars_map:
        return ValidationResult(
            week=prediction.week,
            repo=prediction.repo,
            claim=prediction.claim,
            direction=prediction.direction,
            confidence=prediction.confidence,
            source=prediction.source,
            source_path=prediction.source_path,
            baseline_week=prediction.week,
            observed_week=None,
            weeks_observed=0,
            baseline_stars=None,
            observed_stars=None,
            delta_stars=None,
            delta_pct=None,
            score=None,
            verdict="insufficient_evidence",
            note="Repo was not present in the prediction-week crawl, so no baseline comparison is possible.",
        )

    baseline_stars = baseline_stars_map[prediction.repo]
    observed_week = locate_observed_week(raw_directory, prediction.week, weeks_ahead, snapshot_directory)
    if observed_week is None:
        return ValidationResult(
            week=prediction.week,
            repo=prediction.repo,
            claim=prediction.claim,
            direction=prediction.direction,
            confidence=prediction.confidence,
            source=prediction.source,
            source_path=prediction.source_path,
            baseline_week=prediction.week,
            observed_week=None,
            weeks_observed=0,
            baseline_stars=baseline_stars,
            observed_stars=None,
            delta_stars=None,
            delta_pct=None,
            score=None,
            verdict="insufficient_evidence",
            note="No later raw week is available inside the validation window.",
        )

    observed_raw = load_raw_week(raw_directory, observed_week) or load_snapshot_week(snapshot_directory, observed_week)
    if observed_raw is None:
        return ValidationResult(
            week=prediction.week,
            repo=prediction.repo,
            claim=prediction.claim,
            direction=prediction.direction,
            confidence=prediction.confidence,
            source=prediction.source,
            source_path=prediction.source_path,
            baseline_week=prediction.week,
            observed_week=observed_week,
            weeks_observed=week_distance(prediction.week, observed_week),
            baseline_stars=baseline_stars,
            observed_stars=None,
            delta_stars=None,
            delta_pct=None,
            score=None,
            verdict="insufficient_evidence",
            note="Later raw payload could not be parsed.",
        )

    observed_stars_map = build_repo_stars(observed_raw)
    observed_set = set(observed_stars_map)
    weeks_observed = max(week_distance(prediction.week, observed_week), 1)

    if prediction.repo not in observed_set:
        return ValidationResult(
            week=prediction.week,
            repo=prediction.repo,
            claim=prediction.claim,
            direction=prediction.direction,
            confidence=prediction.confidence,
            source=prediction.source,
            source_path=prediction.source_path,
            baseline_week=prediction.week,
            observed_week=observed_week,
            weeks_observed=weeks_observed,
            baseline_stars=baseline_stars,
            observed_stars=None,
            delta_stars=None,
            delta_pct=None,
            score=None,
            verdict="insufficient_evidence",
            note="Repo was not present in the later crawl payload, so the observation window is inconclusive.",
        )

    observed_stars = observed_stars_map[prediction.repo]
    delta_stars = observed_stars - baseline_stars
    delta_pct = (delta_stars / baseline_stars) if baseline_stars > 0 else (1.0 if observed_stars > 0 else 0.0)
    threshold = expected_growth(prediction.direction, prediction.confidence, weeks_observed)

    if prediction.direction == "up":
        score = min(1.0, max(0.0, delta_pct / threshold))
        verdict = "correct" if score >= 0.6 else "incorrect"
        note = f"Expected at least {threshold:.1%} growth over the observed window; saw {delta_pct:.1%}."
    else:
        overshoot = max(0.0, delta_pct - threshold)
        denominator = max(0.05, threshold)
        score = max(0.0, 1.0 - (overshoot / denominator))
        verdict = "correct" if score >= 0.6 else "incorrect"
        comparator = "flat" if prediction.direction == "flat" else "down"
        note = f"Expected {comparator} performance with at most {threshold:.1%} growth; saw {delta_pct:.1%}."

    return ValidationResult(
        week=prediction.week,
        repo=prediction.repo,
        claim=prediction.claim,
        direction=prediction.direction,
        confidence=prediction.confidence,
        source=prediction.source,
        source_path=prediction.source_path,
        baseline_week=prediction.week,
        observed_week=observed_week,
        weeks_observed=weeks_observed,
        baseline_stars=baseline_stars,
        observed_stars=observed_stars,
        delta_stars=delta_stars,
        delta_pct=round(delta_pct, 4),
        score=round(score, 4),
        verdict=verdict,
        note=note,
    )


def summarize_bucket(results: list[ValidationResult], key: str) -> dict[str, dict[str, float | int]]:
    summary: dict[str, dict[str, float | int]] = {}
    for result in results:
        bucket = getattr(result, key)
        entry = summary.setdefault(bucket, {"total": 0, "correct": 0, "incorrect": 0, "accuracy": 0.0})
        entry["total"] += 1
        if result.verdict == "correct":
            entry["correct"] += 1
        elif result.verdict == "incorrect":
            entry["incorrect"] += 1
    for entry in summary.values():
        total = int(entry["total"])
        correct = int(entry["correct"])
        entry["accuracy"] = round((correct / total), 4) if total else 0.0
    return summary


def quality_trend_summary(analyzed_dir: Path) -> dict[str, Any]:
    entries = track_quality.load_quality_entries(analyzed_dir)
    if not entries:
        return {
            "count": 0,
            "average": 0.0,
            "trend": "insufficient history",
            "latest_week": None,
            "latest_score": None,
            "best_week": None,
            "best_score": None,
            "lowest_week": None,
            "lowest_score": None,
        }
    average = round(sum(entry.score for entry in entries) / len(entries), 1)
    best = max(entries, key=lambda entry: entry.score)
    worst = min(entries, key=lambda entry: entry.score)
    latest = entries[-1]
    return {
        "count": len(entries),
        "average": average,
        "trend": track_quality.classify_trend(entries),
        "latest_week": latest.week,
        "latest_score": latest.score,
        "best_week": best.week,
        "best_score": best.score,
        "lowest_week": worst.week,
        "lowest_score": worst.score,
    }


def build_scorecard(results: list[ValidationResult], analyzed_dir: Path, report_week: str) -> ScorecardSummary:
    validated = [result for result in results if result.verdict in {"correct", "incorrect"}]
    insufficient = [result for result in results if result.verdict == "insufficient_evidence"]
    correct = sum(1 for result in validated if result.verdict == "correct")
    incorrect = sum(1 for result in validated if result.verdict == "incorrect")
    accuracy = round((correct / len(validated)), 4) if validated else 0.0
    return ScorecardSummary(
        week=report_week,
        date=datetime.now(tz=UTC).date().isoformat(),
        total_predictions=len(results),
        validated=len(validated),
        correct=correct,
        incorrect=incorrect,
        accuracy=accuracy,
        by_type=summarize_bucket(validated, "claim"),
        by_direction=summarize_bucket(validated, "direction"),
        quality_trend=quality_trend_summary(analyzed_dir),
        details=[asdict(result) for result in validated],
        insufficient_evidence=[asdict(result) for result in insufficient],
    )


def render_percentage(value: float) -> str:
    return f"{int(round(value * 100))}%"


def render_quality_block(quality: dict[str, Any]) -> list[str]:
    if not quality["count"]:
        return ["No `quality_score` history is available yet."]
    return [
        f"- Summaries tracked: {quality['count']}",
        f"- Average quality score: {quality['average']}",
        f"- Trend: {quality['trend']}",
        f"- Latest week: {quality['latest_week']} ({quality['latest_score']})",
        f"- Best week: {quality['best_week']} ({quality['best_score']})",
        f"- Lowest week: {quality['lowest_week']} ({quality['lowest_score']})",
    ]


def render_accuracy_table(summary: dict[str, dict[str, float | int]], label: str) -> list[str]:
    if not summary:
        return [f"No validated {label.lower()} calls yet."]
    lines = [f"| {label} | Correct | Incorrect | Total | Accuracy |", "| --- | ---: | ---: | ---: | ---: |"]
    for bucket, stats in sorted(summary.items()):
        lines.append(
            f"| {bucket} | {int(stats['correct'])} | {int(stats['incorrect'])} | {int(stats['total'])} | {render_percentage(float(stats['accuracy']))} |"
        )
    return lines


def render_details_table(results: list[dict[str, Any]]) -> list[str]:
    if not results:
        return ["No predictions have enough later data to score yet."]
    lines = [
        "| Week | Repo | Claim | Direction | Conf. | Baseline | Observed | Δ Stars | Verdict | Note |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for result in results:
        note = str(result["note"]).replace("|", "\\|")
        observed_week = result.get("observed_week") or "—"
        observed_stars = result.get("observed_stars")
        lines.append(
            f"| {result['week']} → {observed_week} | {result['repo']} | {result['claim']} | {result['direction']} | {float(result['confidence']):.2f} | {result.get('baseline_stars', '—')} | {observed_stars if observed_stars is not None else '—'} | {result.get('delta_stars', '—')} | {result['verdict']} | {note} |"
        )
    return lines


def render_markdown_scorecard(scorecard: ScorecardSummary, weeks_ahead: int) -> str:
    lines = [
        f"# Prediction Scorecard: {scorecard.week}",
        "",
        f"- Date: {scorecard.date}",
        f"- Validation window: up to {weeks_ahead} weeks later, using the furthest raw week available",
        f"- Predictions found: {scorecard.total_predictions}",
        f"- Predictions validated: {scorecard.validated}",
        f"- Overall accuracy: {render_percentage(scorecard.accuracy)} ({scorecard.correct}/{scorecard.validated if scorecard.validated else 0} correct)",
        "",
        "## Prediction Registry Format",
        "",
        "Use `predictions: [{repo, claim_type, direction, confidence}]` in analysis frontmatter. `claim_type` must be `signal`, `noise`, or `gap`; `direction` must be `up`, `flat`, or `down`. When the registry is absent, the validator still infers Signal/Noise/Gaps from article sections.",
        "",
        "## Quality Trend",
        "",
        *render_quality_block(scorecard.quality_trend),
        "",
        "## Accuracy by Claim",
        "",
        *render_accuracy_table(scorecard.by_type, "Claim"),
        "",
        "## Accuracy by Direction",
        "",
        *render_accuracy_table(scorecard.by_direction, "Direction"),
        "",
        "## Validated Calls",
        "",
        *render_details_table(scorecard.details),
        "",
        "## Insufficient Evidence",
        "",
    ]
    if scorecard.insufficient_evidence:
        lines.extend(
            [
                f"- `{result['week']}` `{result['repo']}` ({result['claim']}/{result['direction']}) — {result['note']}"
                for result in scorecard.insufficient_evidence
            ]
        )
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Editorial Readout",
            "",
            "Signal calls are judged by later star growth, noise calls by limited follow-on growth or disappearance, and gap calls by the traction of the related edge repos cited in the blind-spot narrative. Gap scores are therefore weaker proxies than signal/noise scores and should guide reskill discussion rather than act as hard truth.",
            "",
        ]
    )
    return "\n".join(lines)


def save_json_scorecard(scorecard: ScorecardSummary, metrics_dir: Path) -> Path:
    scorecards_dir = metrics_dir / "scorecards"
    scorecards_dir.mkdir(parents=True, exist_ok=True)
    path = scorecards_dir / f"{scorecard.week}-scorecard.json"
    payload = asdict(scorecard)
    payload["total_validated"] = scorecard.validated
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def save_markdown_scorecard(markdown: str, scorecard_dir: Path, report_week: str) -> Path:
    scorecard_dir.mkdir(parents=True, exist_ok=True)
    path = scorecard_dir / f"{report_week}.md"
    path.write_text(markdown, encoding="utf-8")
    return path


def run_validation(
    analyzed_dir: Path = DEFAULT_ANALYZED_DIR,
    raw_dir: Path = DEFAULT_RAW_DIR,
    metrics_dir: Path = DEFAULT_METRICS_DIR,
    scorecard_dir: Path = DEFAULT_SCORECARD_DIR,
    weeks_ahead: int = 4,
    report_week: str | None = None,
    snapshot_dir: Path | None = DEFAULT_SNAPSHOTS_DIR,
) -> ScorecardSummary:
    predictions: list[Prediction] = []
    for summary_path in sorted(analyzed_dir.glob("*-summary.md")):
        predictions.extend(load_summary_predictions(summary_path))

    results = [evaluate_prediction(prediction, raw_dir, weeks_ahead, snapshot_dir) for prediction in predictions]
    summary = build_scorecard(results, analyzed_dir, report_week or current_iso_week())
    save_json_scorecard(summary, metrics_dir)
    save_markdown_scorecard(render_markdown_scorecard(summary, weeks_ahead), scorecard_dir, summary.week)
    return summary


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    now = datetime.fromisoformat(args.current_datetime.replace("Z", "+00:00")) if args.current_datetime else None
    summary = run_validation(
        analyzed_dir=args.analyzed_dir,
        raw_dir=args.raw_dir,
        metrics_dir=args.metrics_dir,
        scorecard_dir=args.scorecard_dir,
        weeks_ahead=args.weeks_ahead,
        report_week=args.report_week or current_iso_week(now),
        snapshot_dir=args.snapshots_dir,
    )
    print(f"Validated {summary.validated} of {summary.total_predictions} predictions for {summary.week}.")
    print(f"Accuracy: {render_percentage(summary.accuracy)} ({summary.correct}/{summary.validated if summary.validated else 0}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

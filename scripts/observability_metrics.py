#!/usr/bin/env python3
"""Observability metrics schema helpers for crawl and analysis pipelines."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OBSERVABILITY_DIR = ROOT / "data" / "metrics" / "observability"
METRICS_SCHEMA_VERSION = "observability_v1"


@dataclass(frozen=True, slots=True)
class CrawlMetrics:
    duration_seconds: float
    api_calls: int
    cache_hits: int
    cache_misses: int
    stale_cache_hits: int
    rate_limit_events: int
    secondary_rate_limit_hit: bool
    source_type: str
    duration_p95_seconds: float | None = None
    duration_sample_count: int = 0


@dataclass(frozen=True, slots=True)
class MapReduceMetrics:
    stage: str
    duration_seconds: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    status: str
    gate_failure_reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class AnalysisMetrics:
    duration_seconds: float
    token_ledger: dict[str, Any]
    map_stages: list[MapReduceMetrics] = field(default_factory=list)
    reduce_stage: MapReduceMetrics | None = None


@dataclass(frozen=True, slots=True)
class ObservabilityLedger:
    schema_version: str
    run_id: str
    week: str
    timestamp: str
    crawl_metrics: list[CrawlMetrics] = field(default_factory=list)
    analysis_metrics: AnalysisMetrics | None = None
    environment: dict[str, Any] = field(default_factory=dict)


def duration_p95(durations: list[float]) -> float:
    """Return a simple p95 duration estimate for a sampled duration series."""
    if not durations:
        return 0.0
    ordered = sorted(float(value) for value in durations)
    index = max(0, math.ceil(len(ordered) * 0.95) - 1)
    return round(ordered[index], 3)


def emit_ledger(ledger: ObservabilityLedger | dict[str, Any], output_path: Path) -> Path:
    """Write a validated observability ledger JSON artifact."""
    payload = to_serializable(ledger)
    errors = validate_ledger(payload)
    if errors:
        raise ValueError(f"Invalid observability ledger: {', '.join(errors)}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def validate_ledger(data: dict[str, Any]) -> list[str]:
    """Return missing or malformed required field paths for an observability ledger."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["ledger"]

    _require(data, "schema_version", errors)
    _require(data, "run_id", errors)
    _require(data, "week", errors)
    _require(data, "timestamp", errors)
    _require(data, "crawl_metrics", errors)
    _require(data, "environment", errors)

    crawl_metrics = data.get("crawl_metrics")
    if crawl_metrics is not None and not isinstance(crawl_metrics, list):
        errors.append("crawl_metrics")
    elif isinstance(crawl_metrics, list):
        for index, metric in enumerate(crawl_metrics):
            if not isinstance(metric, dict):
                errors.append(f"crawl_metrics[{index}]")
                continue
            _validate_required_fields(
                metric,
                [
                    "duration_seconds",
                    "api_calls",
                    "cache_hits",
                    "cache_misses",
                    "stale_cache_hits",
                    "rate_limit_events",
                    "secondary_rate_limit_hit",
                    "source_type",
                ],
                f"crawl_metrics[{index}]",
                errors,
            )

    analysis_metrics = data.get("analysis_metrics")
    if analysis_metrics is not None:
        if not isinstance(analysis_metrics, dict):
            errors.append("analysis_metrics")
        else:
            _validate_required_fields(
                analysis_metrics,
                ["duration_seconds", "token_ledger", "map_stages"],
                "analysis_metrics",
                errors,
            )
            token_ledger = analysis_metrics.get("token_ledger")
            if not isinstance(token_ledger, dict):
                errors.append("analysis_metrics.token_ledger")
            else:
                _validate_required_fields(
                    token_ledger,
                    ["input_tokens", "output_tokens", "total_tokens"],
                    "analysis_metrics.token_ledger",
                    errors,
                )
            map_stages = analysis_metrics.get("map_stages")
            if not isinstance(map_stages, list):
                errors.append("analysis_metrics.map_stages")
            else:
                for index, metric in enumerate(map_stages):
                    _validate_stage(metric, f"analysis_metrics.map_stages[{index}]", errors)
            reduce_stage = analysis_metrics.get("reduce_stage")
            if reduce_stage is not None:
                _validate_stage(reduce_stage, "analysis_metrics.reduce_stage", errors)

    return errors


def to_serializable(value: Any) -> Any:
    """Normalize dataclasses, paths, and containers into JSON-serializable values."""
    if is_dataclass(value):
        return to_serializable(asdict(value))
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): to_serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_serializable(item) for item in value]
    if isinstance(value, tuple):
        return [to_serializable(item) for item in value]
    return value


def _require(data: dict[str, Any], field_name: str, errors: list[str]) -> None:
    if field_name not in data:
        errors.append(field_name)


def _validate_required_fields(
    payload: dict[str, Any],
    field_names: list[str],
    prefix: str,
    errors: list[str],
) -> None:
    for field_name in field_names:
        if field_name not in payload:
            errors.append(f"{prefix}.{field_name}")


def _validate_stage(stage: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(stage, dict):
        errors.append(prefix)
        return
    _validate_required_fields(
        stage,
        [
            "stage",
            "duration_seconds",
            "input_tokens",
            "output_tokens",
            "cost_usd",
            "status",
            "gate_failure_reasons",
        ],
        prefix,
        errors,
    )

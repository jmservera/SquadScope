#!/usr/bin/env python3
"""Validate a squadscope.topic.yml config file against the topic schema.

Usage:
    python scripts/validate_topic_config.py <path-to-yaml>

Exit codes:
    0 — config is valid
    1 — config is invalid (errors printed to stderr)

Schema fields:
    topic (required):
        id        — URL-safe identifier (lowercase alphanumeric + hyphens)
        name      — Human-readable display name
        description — Short description for the topic

    queries (required):
        primary   — List of GitHub search queries (at least one required)
        secondary — Optional list of supplemental queries

    scoring (optional, has defaults):
        min_stars, min_stars_gained, max_age_days, min_relevance_score
        language_boost  — dict of language → multiplier
        topic_relevance — list of relevant GitHub topics

    quality (optional, has defaults):
        min_repos_per_week, max_repos_per_week, min_quality_score

    learning (optional, has defaults):
        wisdom_file, skills_dir, prediction_file, scorecard_dir
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


# --- Pydantic Models ---

URL_SAFE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class TopicInfo(BaseModel):
    """Core topic identification. All fields required."""

    id: str = Field(..., description="URL-safe identifier (lowercase alphanumeric + hyphens)")
    name: str = Field(..., description="Human-readable display name")
    description: str = Field("", description="Short description of the topic")

    @field_validator("id")
    @classmethod
    def id_must_be_url_safe(cls, v: str) -> str:
        if not URL_SAFE_RE.match(v):
            raise ValueError(
                f"topic.id must be URL-safe (lowercase alphanumeric + hyphens), got: '{v}'"
            )
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("topic.name must not be empty")
        return v


class Queries(BaseModel):
    """Search queries for GitHub API. At least one primary query is required."""

    primary: List[str] = Field(..., min_length=1, description="Primary search queries (at least one)")
    secondary: List[str] = Field(default_factory=list, description="Optional secondary queries")

    @field_validator("primary")
    @classmethod
    def primary_not_empty_strings(cls, v: List[str]) -> List[str]:
        for i, q in enumerate(v):
            if not q.strip():
                raise ValueError(f"queries.primary[{i}] must not be an empty string")
        return v


class Scoring(BaseModel):
    """Scoring thresholds and boosts. All fields have sensible defaults."""

    min_stars: int = Field(default=20, ge=0, description="Minimum star count")
    min_stars_gained: int = Field(default=10, ge=0, description="Minimum stars gained in period")
    max_age_days: int = Field(default=365, ge=1, le=3650, description="Max repo age in days")
    min_relevance_score: int = Field(default=40, ge=0, le=100, description="Minimum relevance score (0-100)")
    language_boost: Dict[str, float] = Field(
        default_factory=dict, description="Language → score multiplier"
    )
    topic_relevance: List[str] = Field(
        default_factory=list, description="GitHub topics that boost relevance"
    )

    @field_validator("language_boost")
    @classmethod
    def boost_values_reasonable(cls, v: Dict[str, float]) -> Dict[str, float]:
        for lang, boost in v.items():
            if boost < 0.1 or boost > 10.0:
                raise ValueError(
                    f"scoring.language_boost['{lang}'] must be between 0.1 and 10.0, got {boost}"
                )
        return v


class Quality(BaseModel):
    """Quality gates for output. All fields have sensible defaults."""

    min_repos_per_week: int = Field(default=5, ge=1, description="Minimum repos to include per week")
    max_repos_per_week: int = Field(default=30, ge=1, description="Maximum repos to include per week")
    min_quality_score: int = Field(default=60, ge=0, le=100, description="Minimum quality score (0-100)")

    @model_validator(mode="after")
    def min_less_than_max(self) -> "Quality":
        if self.min_repos_per_week > self.max_repos_per_week:
            raise ValueError(
                f"quality.min_repos_per_week ({self.min_repos_per_week}) "
                f"must be <= max_repos_per_week ({self.max_repos_per_week})"
            )
        return self


class Learning(BaseModel):
    """Paths for learning/feedback loop artifacts. Supports {topic_id} placeholder."""

    wisdom_file: str = Field(
        default="topics/{topic_id}/wisdom.md", description="Path to wisdom markdown"
    )
    skills_dir: str = Field(
        default="topics/{topic_id}/skills/", description="Directory for learned skills"
    )
    prediction_file: str = Field(
        default="topics/{topic_id}/predictions.jsonl", description="Path to predictions log"
    )
    scorecard_dir: str = Field(
        default="topics/{topic_id}/scorecards/", description="Directory for scorecards"
    )


class TopicConfig(BaseModel):
    """Root model for squadscope.topic.yml configuration."""

    topic: TopicInfo
    queries: Queries
    scoring: Scoring = Field(default_factory=Scoring)
    quality: Quality = Field(default_factory=Quality)
    learning: Learning = Field(default_factory=Learning)


# --- CLI Entrypoint ---


def validate_file(path: str) -> TopicConfig:
    """Load and validate a YAML topic config file. Returns the validated model."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(file_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Config file must contain a YAML mapping at the top level")

    return TopicConfig.model_validate(raw)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_topic_config.py <path-to-yaml>", file=sys.stderr)
        return 1

    path = sys.argv[1]
    try:
        config = validate_file(path)
        print(f"✓ Valid topic config: {config.topic.name} ({config.topic.id})")
        return 0
    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"✗ Validation error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        # Pydantic validation errors
        print(f"✗ Validation failed:\n{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

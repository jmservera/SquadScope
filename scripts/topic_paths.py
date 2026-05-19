#!/usr/bin/env python3
"""Topic-aware data path resolution for SquadScope.

Provides a single source of truth for data directory layout:
    data/raw/{topic_id}/
    data/analyzed/{topic_id}/
    data/metrics/{topic_id}/
    data/snapshots/{topic_id}/
    data/cache/{topic_id}/

Backward compatibility: when topic_id is None or "general", paths
resolve to the legacy flat layout (data/raw/, data/analyzed/, etc.).
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_TOPIC = "general"

# Base data root (relative to repo root)
DATA_ROOT = Path("data")


def _resolve(base: Path, topic_id: str | None) -> Path:
    """Return namespaced path, creating parents on first access."""
    tid = (topic_id or DEFAULT_TOPIC).strip().lower()
    if tid == DEFAULT_TOPIC:
        return base
    return base / tid


def raw_dir(topic_id: str | None = None) -> Path:
    """Return the raw data directory for a given topic."""
    return _resolve(DATA_ROOT / "raw", topic_id)


def analyzed_dir(topic_id: str | None = None) -> Path:
    """Return the analyzed data directory for a given topic."""
    return _resolve(DATA_ROOT / "analyzed", topic_id)


def metrics_dir(topic_id: str | None = None) -> Path:
    """Return the metrics directory for a given topic."""
    return _resolve(DATA_ROOT / "metrics", topic_id)


def snapshots_dir(topic_id: str | None = None) -> Path:
    """Return the snapshots directory for a given topic."""
    return _resolve(DATA_ROOT / "snapshots", topic_id)


def cache_dir(topic_id: str | None = None) -> Path:
    """Return the cache directory for a given topic."""
    return _resolve(DATA_ROOT / "cache", topic_id)


def ensure_dirs(topic_id: str | None = None) -> None:
    """Create all data directories for a topic if they don't exist."""
    for fn in (raw_dir, analyzed_dir, metrics_dir, snapshots_dir, cache_dir):
        fn(topic_id).mkdir(parents=True, exist_ok=True)


def load_topic_id(config_path: str | Path = "squadscope.topic.yml") -> str:
    """Load topic.id from a YAML config file. Returns DEFAULT_TOPIC on failure."""
    import yaml

    path = Path(config_path)
    if not path.exists():
        return DEFAULT_TOPIC
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return (data or {}).get("topic", {}).get("id", DEFAULT_TOPIC)
    except Exception:
        return DEFAULT_TOPIC

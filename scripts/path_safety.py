"""Shared path-boundary helpers for security-sensitive pipeline code."""

from __future__ import annotations

from pathlib import Path


def find_symlink_component(path: Path) -> Path | None:
    """Return the first symlink in an absolute path walk, if any."""
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            return current
    return None

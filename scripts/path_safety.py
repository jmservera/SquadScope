"""Shared path-boundary helpers for security-sensitive pipeline code."""

from __future__ import annotations

import os
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


def open_directory_nofollow(path: Path) -> int:
    """Open a directory without following any symlink component."""
    absolute = path.absolute()
    directory_fd = os.open(
        absolute.anchor,
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
    )
    try:
        for component in absolute.parts[1:]:
            next_fd = os.open(
                component,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = next_fd
    except BaseException:
        os.close(directory_fd)
        raise
    return directory_fd

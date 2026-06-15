from __future__ import annotations

from pathlib import Path

NO_CONTINUITY_MESSAGE = "_No learned continuity capsule has been recorded yet._"


def render_continuity(continuity_file: Path) -> str:
    from scripts.sanitize_repo_content import _escape_untrusted_boundaries

    if not continuity_file.exists():
        return NO_CONTINUITY_MESSAGE

    content = continuity_file.read_text(encoding="utf-8").strip()
    if not content:
        return NO_CONTINUITY_MESSAGE
    return _escape_untrusted_boundaries(content)

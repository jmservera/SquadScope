#!/usr/bin/env python3
"""Validate that every embed page's source_page resolves to an existing data page.

A `content/embeds/*` page renders a chart from another page referenced by its
`source_page` front matter. If that target page is missing, the Hugo build aborts
(`layouts/embeds/single.html` and `layouts/shortcodes/observatory-chart.html`
call `errorf`). This check catches a dangling reference before the build, so the
failure surfaces in CI rather than in the production deploy (see issue #627).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCE_PAGE_PATTERN = re.compile(
    r"""^\s*source_page\s*[:=]\s*["']?(?P<value>[^"'\n]+?)["']?\s*$""",
    re.MULTILINE,
)


def _source_page(document: str) -> str | None:
    match = SOURCE_PAGE_PATTERN.search(document)
    return match.group("value").strip() if match else None


def _resolves(content_root: Path, source_page: str) -> bool:
    relative = source_page.strip("/")
    # NFR-012: an embed's source_page must be a data page under content/data/.
    if relative != "data" and not relative.startswith("data/"):
        return False
    target = content_root / relative
    return (target / "index.md").is_file() or (target / "_index.md").is_file()


def check_embed_sources(root: Path = ROOT) -> list[str]:
    """Return a list of human-readable problems, empty when all embeds resolve."""
    content_root = root / "content"
    problems: list[str] = []

    for embed in sorted(content_root.glob("embeds/*/index.md")):
        source_page = _source_page(embed.read_text(encoding="utf-8"))
        relative_embed = embed.relative_to(root).as_posix()
        if not source_page:
            problems.append(f"{relative_embed}: missing source_page")
            continue
        if not _resolves(content_root, source_page):
            problems.append(
                f"{relative_embed}: source_page does not resolve to a content/data page: "
                f"{source_page}"
            )

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), type=Path, help="Repository root")
    args = parser.parse_args(argv)

    problems = check_embed_sources(args.root)
    for problem in problems:
        print(f"::error::{problem}", file=sys.stderr)
    if problems:
        return 1
    print("All embed source_page references resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

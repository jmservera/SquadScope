#!/usr/bin/env python3
"""Build a single reviewable HTML index for a visual regression evidence capture.

`tests/visual/observatory-visual-regression.spec.mjs` writes one directory per
Playwright project, each holding a screenshot per route plus a `metadata.json`.
Reviewing that layout means opening dozens of files across four directories. This
builds one page that groups every route with its desktop/mobile and light/dark
variants side by side, so the named visual review in
`docs/review/data-observatory-relaunch/visual-regression-execution-guide.md` can be
completed in one pass.

The index is generated evidence and is written next to the screenshots, which are
gitignored.
"""

from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = ROOT / "screenshots" / "visual-regression"

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_ERROR = 2

# Widest viewport first so a route's variants read left to right at decreasing size.
PROJECT_ORDER = ("desktop-light", "desktop-dark", "mobile-light", "mobile-dark")

STYLE = """
:root { color-scheme: light dark; }
body { font-family: system-ui, sans-serif; margin: 0 auto; max-width: 1600px; padding: 2rem; }
h1 { margin-bottom: 0.25rem; }
dl.meta { display: grid; grid-template-columns: max-content 1fr; gap: 0.25rem 1rem; }
dl.meta dt { font-weight: 600; }
dl.meta dd { margin: 0; font-family: ui-monospace, monospace; }
.warning { background: #ffe8e8; border-left: 4px solid #c00; color: #600; padding: 0.75rem 1rem; }
section { border-top: 1px solid #8884; margin-top: 2.5rem; padding-top: 1rem; }
.variants { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
figure { margin: 0; }
figcaption { font-family: ui-monospace, monospace; font-size: 0.85rem; padding-bottom: 0.25rem; }
img { background: #8882; border: 1px solid #8884; max-height: 70vh; object-fit: contain;
      object-position: top; width: 100%; }
.missing { color: #c00; font-style: italic; }
"""


def _load_projects(evidence_dir: Path) -> dict[str, dict]:
    projects: dict[str, dict] = {}
    for metadata_path in sorted(evidence_dir.glob("*/metadata.json")):
        projects[metadata_path.parent.name] = json.loads(metadata_path.read_text(encoding="utf-8"))
    return projects


def _ordered_projects(names: list[str]) -> list[str]:
    known = [name for name in PROJECT_ORDER if name in names]
    return known + sorted(name for name in names if name not in PROJECT_ORDER)


def _routes(projects: dict[str, dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for metadata in projects.values():
        for route in metadata.get("routes", []):
            seen.setdefault(route["name"], route)
    return list(seen.values())


def _meta_rows(projects: dict[str, dict]) -> list[tuple[str, str]]:
    reference = next(iter(projects.values()))
    viewports = ", ".join(
        f"{name} {projects[name]['viewport']['width']}x{projects[name]['viewport']['height']}"
        for name in _ordered_projects(list(projects))
    )
    return [
        ("Revision", str(reference.get("revision", "unknown"))),
        ("Branch", str(reference.get("branch", "unknown"))),
        ("Origin", str(reference.get("origin", "unknown"))),
        ("Working tree clean", str(reference.get("workingTreeClean", "unknown"))),
        ("Run ID", str(reference.get("runId") or "none")),
        ("Captured", str(reference.get("timestamp", "unknown"))),
        ("Playwright", str(reference.get("playwrightVersion", "unknown"))),
        ("Viewports", viewports),
    ]


def render_index(evidence_dir: Path, projects: dict[str, dict]) -> str:
    """Render the review index HTML for an already-loaded evidence capture."""
    names = _ordered_projects(list(projects))
    revisions = {metadata.get("revision") for metadata in projects.values()}

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Visual regression evidence</title>",
        f"<style>{STYLE}</style></head><body>",
        "<h1>Visual regression evidence</h1>",
        "<dl class='meta'>",
    ]
    for label, value in _meta_rows(projects):
        parts.append(f"<dt>{escape(label)}</dt><dd>{escape(value)}</dd>")
    parts.append("</dl>")

    if len(revisions) > 1:
        listed = ", ".join(sorted(escape(str(revision)) for revision in revisions))
        parts.append(
            f"<p class='warning'>Mixed revisions in one capture: {listed}. "
            "This evidence set cannot be tied to a single revision.</p>"
        )
    if any(metadata.get("workingTreeClean") is False for metadata in projects.values()):
        parts.append(
            "<p class='warning'>Captured from a dirty working tree. The screenshots "
            "do not correspond to the recorded revision alone.</p>"
        )

    for route in _routes(projects):
        parts.append("<section>")
        parts.append(f"<h2>{escape(route['name'])}</h2>")
        parts.append(f"<p><code>{escape(route['path'])}</code></p>")
        parts.append("<div class='variants'>")
        for name in names:
            image = Path(name) / f"{route['name']}.png"
            parts.append("<figure>")
            parts.append(f"<figcaption>{escape(name)}</figcaption>")
            if (evidence_dir / image).is_file():
                parts.append(
                    f"<img loading='lazy' src='{escape(image.as_posix())}' "
                    f"alt='{escape(route['name'])} on {escape(name)}'>"
                )
            else:
                parts.append("<p class='missing'>screenshot missing</p>")
            parts.append("</figure>")
        parts.append("</div></section>")

    parts.append("</body></html>")
    return "\n".join(parts)


def build_index(evidence_dir: Path, output: Path | None = None) -> Path:
    """Write the review index and return its path."""
    projects = _load_projects(evidence_dir)
    if not projects:
        raise FileNotFoundError(f"No project metadata found under {evidence_dir}")
    target = output or evidence_dir / "index.html"
    target.write_text(render_index(evidence_dir, projects), encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-dir",
        default=DEFAULT_EVIDENCE_DIR,
        type=Path,
        help="Directory holding one subdirectory per Playwright project",
    )
    parser.add_argument(
        "--output", type=Path, help="Index path (default: <evidence-dir>/index.html)"
    )
    args = parser.parse_args(argv)

    try:
        target = build_index(args.evidence_dir, args.output)
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as error:
        print(f"::error::{error}", file=sys.stderr)
        return EXIT_ERROR

    print(f"Wrote {target}")
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())

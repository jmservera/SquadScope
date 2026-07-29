from __future__ import annotations

import shutil
import subprocess
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

import pytest


class HeadMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.description: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.description = attrs_dict.get("content", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def test_rendered_pages_have_unique_titles_and_meta_descriptions(tmp_path: Path) -> None:
    if shutil.which("hugo") is None:
        pytest.skip("Hugo binary is required to render SEO metadata fixtures")

    repo_root = Path(__file__).resolve().parents[1]
    rendered_site = tmp_path / "public"
    subprocess.run(
        ["hugo", "--minify", "--quiet", "--destination", str(rendered_site)],
        cwd=repo_root,
        check=True,
    )

    values: dict[tuple[str, str], list[Path]] = defaultdict(list)
    missing: list[str] = []
    for html_file in sorted(rendered_site.rglob("*.html")):
        parser = HeadMetadataParser()
        parser.feed(html_file.read_text(encoding="utf-8", errors="ignore"))
        title = parser.title
        description = (parser.description or "").strip()
        rel_path = html_file.relative_to(rendered_site)
        if not title:
            missing.append(f"{rel_path}: empty <title>")
        if not description:
            missing.append(f"{rel_path}: empty meta description")
        values[("title", title)].append(rel_path)
        values[("meta description", description)].append(rel_path)

    duplicates = []
    for (kind, value), paths in values.items():
        if value and len(paths) > 1:
            rendered_paths = ", ".join(str(path) for path in paths)
            duplicates.append(f"Duplicate {kind} {value!r}: {rendered_paths}")

    assert not missing
    assert not duplicates

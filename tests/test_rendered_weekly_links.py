from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TARGET_WEEK = "W21"


class WeeklyLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: set[str] = set()
        self.week_navigation: set[str] = set()
        self.in_week_navigation = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name: value or "" for name, value in attrs}
        classes = attrs_dict.get("class", "").split()
        if tag == "nav" and "article-week-nav" in classes:
            self.in_week_navigation = True
        if tag == "a" and attrs_dict.get("href"):
            href = attrs_dict["href"]
            self.hrefs.add(href)
            if self.in_week_navigation:
                self.week_navigation.add(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.in_week_navigation:
            self.in_week_navigation = False


@pytest.fixture(scope="module")
def rendered_weekly_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    if shutil.which("hugo") is None:
        pytest.skip("Hugo binary is required to render weekly link fixtures")

    destination = tmp_path_factory.mktemp("rendered-weekly-links") / "public"
    subprocess.run(
        ["hugo", "--minify", "--quiet", "--destination", str(destination)],
        cwd=ROOT,
        check=True,
    )
    return destination


def _front_matter(path: Path) -> dict[str, object]:
    content = path.read_text(encoding="utf-8")
    _, front_matter, _ = content.split("---", 2)
    parsed = yaml.safe_load(front_matter)
    assert isinstance(parsed, dict)
    return parsed


def _urlize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _required_links(weekly_path: Path) -> tuple[set[str], set[str], set[str]]:
    metadata = _front_matter(weekly_path)
    weekly_pages = sorted(
        ROOT.glob("content/weekly/*/W*.md"),
        key=lambda path: datetime.fromisoformat(str(_front_matter(path)["date"])),
    )
    target_index = weekly_pages.index(weekly_path)
    neighbors = weekly_pages[max(0, target_index - 1) : target_index + 2]
    chronological = {
        f"/weekly/{path.parent.name}/{path.stem.lower()}/"
        for path in neighbors
        if path != weekly_path
    }

    registry = json.loads((ROOT / "data/taxonomy/topics.json").read_text(encoding="utf-8"))
    canonical_topics: set[str] = set()
    for topic in metadata.get("topics", []):
        topic_slug = _urlize(str(topic))
        for slug, entry in registry["terms"].items():
            aliases = {_urlize(str(alias)) for alias in entry.get("aliases", [])}
            if topic_slug in {slug, *aliases} and entry.get("promoted"):
                canonical_slug = entry.get("slug", slug)
                if (ROOT / "content/topics" / canonical_slug / "_index.md").exists():
                    canonical_topics.add(f"/topics/{canonical_slug}/")

    assert chronological
    assert canonical_topics
    return chronological, canonical_topics, set()


def _missing_required_links(required: set[str], actual: set[str]) -> set[str]:
    return required - actual


def test_weekly_pages_include_required_navigation_topic_and_repository_links(
    rendered_weekly_site: Path,
) -> None:
    weekly_path = ROOT / "content/weekly/2026" / f"{TARGET_WEEK}.md"
    chronological, canonical_topics, repositories = _required_links(weekly_path)
    parser = WeeklyLinkParser()
    parser.feed(
        (rendered_weekly_site / f"weekly/2026/{TARGET_WEEK.lower()}/index.html").read_text(
            encoding="utf-8"
        )
    )

    assert not _missing_required_links(chronological, parser.week_navigation)
    assert not _missing_required_links(canonical_topics, parser.hrefs)
    assert not _missing_required_links(repositories, parser.hrefs)


def test_weekly_link_contract_detects_removed_required_link(rendered_weekly_site: Path) -> None:
    weekly_path = ROOT / "content/weekly/2026" / f"{TARGET_WEEK}.md"
    link_groups = _required_links(weekly_path)
    parser = WeeklyLinkParser()
    parser.feed(
        (rendered_weekly_site / f"weekly/2026/{TARGET_WEEK.lower()}/index.html").read_text(
            encoding="utf-8"
        )
    )

    required = set().union(*link_groups)
    removed = next(iter(required))
    remaining = parser.hrefs - {removed}
    assert _missing_required_links(required, remaining) == {removed}

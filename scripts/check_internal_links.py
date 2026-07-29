#!/usr/bin/env python3
from __future__ import annotations

import argparse
import posixpath
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

IGNORED_SCHEMES = {"data", "javascript", "mailto", "tel"}
LINK_ATTRS = {
    "a": ("href",),
    "area": ("href",),
    "iframe": ("src",),
    "img": ("src", "srcset"),
    "link": ("href",),
    "script": ("src",),
    "source": ("src", "srcset"),
}


@dataclass(frozen=True)
class Link:
    source: Path
    target: str
    attribute: str


class InternalLinkParser(HTMLParser):
    def __init__(self, source: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.links: list[Link] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        element_id = attrs_dict.get("id") or attrs_dict.get("name")
        if element_id:
            self.ids.add(element_id)

        for attr in LINK_ATTRS.get(tag.lower(), ()):
            value = attrs_dict.get(attr, "").strip()
            if not value:
                continue
            if attr == "srcset":
                self.links.extend(
                    Link(self.source, candidate, attr) for candidate in parse_srcset(value)
                )
            else:
                self.links.append(Link(self.source, value, attr))


def parse_srcset(value: str) -> list[str]:
    candidates: list[str] = []
    for item in value.split(","):
        url = item.strip().split(maxsplit=1)[0]
        if url:
            candidates.append(url)
    return candidates


def collect_pages(site_root: Path) -> tuple[dict[Path, set[str]], list[Link]]:
    anchors_by_file: dict[Path, set[str]] = {}
    links: list[Link] = []
    for html_file in sorted(site_root.rglob("*.html")):
        parser = InternalLinkParser(html_file)
        parser.feed(html_file.read_text(encoding="utf-8", errors="ignore"))
        anchors_by_file[html_file] = parser.ids
        links.extend(parser.links)
    return anchors_by_file, links


def is_internal_url(url: str, base_netlocs: set[str]) -> bool:
    parsed = urlsplit(url)
    if parsed.scheme.lower() in IGNORED_SCHEMES:
        return False
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return False
    if parsed.netloc and parsed.netloc.lower() not in base_netlocs:
        return False
    return True


def target_file_for_path(site_root: Path, url_path: str) -> Path:
    decoded = unquote(url_path)
    normalized = posixpath.normpath(decoded if decoded.startswith("/") else f"/{decoded}")
    if normalized == "/":
        return site_root / "index.html"

    relative = normalized.lstrip("/")
    candidate = site_root / relative
    if candidate.is_dir() or decoded.endswith("/"):
        return candidate / "index.html"
    if candidate.exists():
        return candidate
    if "." not in Path(relative).name:
        return candidate / "index.html"
    return candidate


def resolve_target(
    site_root: Path, source: Path, target: str, base_netlocs: set[str]
) -> Path | None:
    parsed = urlsplit(target)
    if not is_internal_url(target, base_netlocs):
        return None
    if parsed.netloc or target.startswith("/"):
        return target_file_for_path(site_root, parsed.path or "/")

    source_dir = "/" + str(source.parent.relative_to(site_root))
    normalized = posixpath.normpath(posixpath.join(source_dir, parsed.path or "."))
    return target_file_for_path(site_root, normalized)


def check_links(site_root: Path, base_url: str) -> list[str]:
    anchors_by_file, links = collect_pages(site_root)
    base = urlsplit(base_url)
    base_netlocs = {base.netloc.lower()} if base.netloc else set()
    broken: list[str] = []

    for link in links:
        parsed = urlsplit(link.target)
        target_file = resolve_target(site_root, link.source, link.target, base_netlocs)
        if target_file is None:
            continue

        rel_source = link.source.relative_to(site_root)
        rel_target = (
            target_file.relative_to(site_root)
            if target_file.is_relative_to(site_root)
            else target_file
        )
        if not target_file.exists() or not target_file.is_file():
            broken.append(f"{rel_source}: {link.attribute}={link.target!r} -> missing {rel_target}")
            continue

        if parsed.fragment and parsed.fragment not in anchors_by_file.get(target_file, set()):
            broken.append(
                f"{rel_source}: {link.attribute}={link.target!r} -> missing fragment #{parsed.fragment}"
            )

    return broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check internal links in a rendered static site.")
    parser.add_argument("site_root", type=Path, help="Rendered site directory, usually public/")
    parser.add_argument(
        "--base-url", default="https://claracle.com/", help="Canonical site base URL"
    )
    args = parser.parse_args(argv)

    site_root = args.site_root.resolve()
    if not site_root.is_dir():
        print(f"error: site root does not exist: {site_root}", file=sys.stderr)
        return 2

    broken = check_links(site_root, args.base_url)
    if broken:
        print("Broken internal links found:", file=sys.stderr)
        for item in broken:
            print(f"- {item}", file=sys.stderr)
        return 1

    print("Internal link check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path

from scripts.check_internal_links import check_links


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_internal_link_checker_accepts_existing_pages_and_fragments(tmp_path: Path) -> None:
    write(
        tmp_path / "index.html",
        '<a href="/weekly/2026/w31/">week</a><a href="https://claracle.com/topics/ai-coding-agents/#overview">topic</a>',
    )
    write(tmp_path / "weekly/2026/w31/index.html", "<h1>Week</h1>")
    write(tmp_path / "topics/ai-coding-agents/index.html", '<h1 id="overview">Topic</h1>')

    assert check_links(tmp_path, "https://claracle.com/") == []


def test_internal_link_checker_reports_missing_internal_page(tmp_path: Path) -> None:
    write(tmp_path / "index.html", '<a href="/missing/">missing</a>')

    assert check_links(tmp_path, "https://claracle.com/") == [
        "index.html: href='/missing/' -> missing missing/index.html"
    ]


def test_internal_link_checker_detects_mixed_case_scheme_internal_links(
    tmp_path: Path,
) -> None:
    write(tmp_path / "index.html", '<a href="HTTPS://claracle.com/missing/">missing</a>')

    assert check_links(tmp_path, "https://claracle.com/") == [
        "index.html: href='HTTPS://claracle.com/missing/' -> missing missing/index.html"
    ]


def test_internal_link_checker_reports_missing_fragment(tmp_path: Path) -> None:
    write(tmp_path / "index.html", '<a href="/weekly/#not-there">weekly</a>')
    write(tmp_path / "weekly/index.html", '<h1 id="weekly">Weekly</h1>')

    assert check_links(tmp_path, "https://claracle.com/") == [
        "index.html: href='/weekly/#not-there' -> missing fragment #not-there"
    ]


def test_internal_link_checker_resolves_empty_path_links_to_current_file(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "404.html",
        '<h1 id="top">Not found</h1><a href="#top">top</a><a href="?from=404#top">query</a>',
    )

    assert check_links(tmp_path, "https://claracle.com/") == []

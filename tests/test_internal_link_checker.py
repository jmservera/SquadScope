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


def test_internal_link_checker_reports_missing_fragment(tmp_path: Path) -> None:
    write(tmp_path / "index.html", '<a href="/weekly/#not-there">weekly</a>')
    write(tmp_path / "weekly/index.html", '<h1 id="weekly">Weekly</h1>')

    assert check_links(tmp_path, "https://claracle.com/") == [
        "index.html: href='/weekly/#not-there' -> missing fragment #not-there"
    ]

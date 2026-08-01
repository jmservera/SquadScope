from __future__ import annotations

import tempfile
from pathlib import Path

from scripts.check_embed_sources import check_embed_sources

ROOT = Path(__file__).resolve().parent.parent


def test_repository_embed_sources_all_resolve() -> None:
    assert check_embed_sources(ROOT) == []


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_missing_source_page_is_reported() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "content/embeds/chart/index.md", '+++\ntitle = "Chart"\n+++\n')
        problems = check_embed_sources(root)
        assert any("missing source_page" in problem for problem in problems)


def test_dangling_source_page_is_reported() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(
            root / "content/embeds/chart/index.md",
            '+++\nsource_page = "/data/does-not-exist/"\n+++\n',
        )
        problems = check_embed_sources(root)
        assert any("does not resolve" in problem for problem in problems)


def test_resolving_source_page_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(
            root / "content/embeds/chart/index.md",
            '+++\nsource_page = "/data/live/"\n+++\n',
        )
        _write(root / "content/data/live/index.md", '+++\ntitle = "Live"\n+++\n')
        assert check_embed_sources(root) == []

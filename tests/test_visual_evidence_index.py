from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.design.build_visual_evidence_index import build_index, main


def _capture(
    root: Path,
    *,
    projects: tuple[str, ...] = ("desktop-light", "mobile-dark"),
    revision: str = "abc123",
    working_tree_clean: bool = True,
    routes: list[dict] | None = None,
    with_screenshots: bool = True,
) -> Path:
    routes = routes or [{"name": "home", "path": "/"}, {"name": "topic", "path": "/topics/ai/"}]
    for project in projects:
        directory = root / project
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "metadata.json").write_text(
            json.dumps(
                {
                    "revision": revision,
                    "branch": "feature",
                    "origin": "local",
                    "workingTreeClean": working_tree_clean,
                    "runId": None,
                    "timestamp": "2026-08-07T00:00:00.000Z",
                    "project": project,
                    "colorScheme": "light",
                    "viewport": {"width": 1280, "height": 800},
                    "playwrightVersion": "1.54.2",
                    "routes": routes,
                }
            ),
            encoding="utf-8",
        )
        if with_screenshots:
            for route in routes:
                (directory / f"{route['name']}.png").write_bytes(b"")
    return root


def test_index_lists_every_route_and_project(tmp_path: Path) -> None:
    _capture(tmp_path)

    html = build_index(tmp_path).read_text(encoding="utf-8")

    assert "desktop-light/home.png" in html
    assert "mobile-dark/topic.png" in html
    assert "/topics/ai/" in html
    assert "abc123" in html


def test_missing_screenshot_is_flagged_rather_than_linked(tmp_path: Path) -> None:
    _capture(tmp_path, with_screenshots=False)

    html = build_index(tmp_path).read_text(encoding="utf-8")

    assert "screenshot missing" in html
    assert "<img" not in html


def test_mixed_revisions_are_called_out(tmp_path: Path) -> None:
    _capture(tmp_path, projects=("desktop-light",), revision="aaa")
    _capture(tmp_path, projects=("mobile-dark",), revision="bbb")

    html = build_index(tmp_path).read_text(encoding="utf-8")

    assert "Mixed revisions" in html


def test_dirty_tree_is_called_out(tmp_path: Path) -> None:
    _capture(tmp_path, working_tree_clean=False)

    html = build_index(tmp_path).read_text(encoding="utf-8")

    assert "dirty working tree" in html


def test_route_values_are_escaped(tmp_path: Path) -> None:
    _capture(
        tmp_path,
        routes=[{"name": "home", "path": "/<script>alert(1)</script>/"}],
        with_screenshots=False,
    )

    html = build_index(tmp_path).read_text(encoding="utf-8")

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_empty_capture_exits_with_configuration_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        build_index(tmp_path)

    assert main(["--evidence-dir", str(tmp_path)]) == 2


def test_main_writes_the_requested_output_path(tmp_path: Path) -> None:
    _capture(tmp_path)
    output = tmp_path / "review" / "index.html"
    output.parent.mkdir()

    assert main(["--evidence-dir", str(tmp_path), "--output", str(output)]) == 0
    assert output.is_file()

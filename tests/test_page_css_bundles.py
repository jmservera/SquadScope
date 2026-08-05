from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def stylesheet_path(rendered: str) -> str:
    match = re.search(r"""href=["']?([^"' >]*/assets/css/stylesheet[^"'? >]+\.css)""", rendered)
    assert match, "rendered page is missing its bundled stylesheet"
    return match.group(1).lstrip("/")


def test_static_routes_share_lean_css_without_article_or_chart_visuals() -> None:
    if shutil.which("hugo") is None:
        pytest.skip("hugo binary is not installed in this test environment")

    destination = ROOT / "public-test-page-css"
    shutil.rmtree(destination, ignore_errors=True)
    result = subprocess.run(
        ["hugo", "--minify", "--destination", str(destination)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        assert result.returncode == 0, result.stderr
        lean_routes = [
            "tools/star-velocity-explorer/index.html",
            "search/index.html",
            "about/index.html",
            "methodology/index.html",
            "privacy/index.html",
        ]
        lean_stylesheets = {
            stylesheet_path((destination / route).read_text(encoding="utf-8"))
            for route in lean_routes
        }
        assert len(lean_stylesheets) == 1

        lean_css = (destination / lean_stylesheets.pop()).read_text(encoding="utf-8")
        assert ".article-cover" not in lean_css
        assert ".observatory-chart" not in lean_css
        assert ".search-shell" in lean_css
        assert ".cost-dashboard" in lean_css

        weekly = (destination / "weekly/2026/w22/index.html").read_text(encoding="utf-8")
        full_css = (destination / stylesheet_path(weekly)).read_text(encoding="utf-8")
        assert ".article-cover" in full_css
        assert ".observatory-chart" in full_css
    finally:
        shutil.rmtree(destination, ignore_errors=True)

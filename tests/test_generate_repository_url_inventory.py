from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import generate_repository_url_inventory as inventory


def _write_page(path: Path, *, aliases: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    alias_lines = ""
    if aliases:
        alias_lines = "aliases:\n" + "".join(f"  - {alias}\n" for alias in aliases)
    path.write_text(f"---\ntitle: Example\n{alias_lines}---\n\nBody\n", encoding="utf-8")


def test_build_inventory_includes_index_canonicals_and_aliases(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(tmp_path / "content/repo/alpha/index.md", aliases=["/repo/alpha-old/"])
    _write_page(tmp_path / "content/repo/beta/index.md")

    payload = inventory.build_inventory(tmp_path)

    assert payload["counts"] == {"index": 1, "canonical": 2, "alias": 1, "total": 4}
    assert [record["url"] for record in payload["records"]] == [
        "/repo/",
        "/repo/alpha-old/",
        "/repo/alpha/",
        "/repo/beta/",
    ]
    alias = next(record for record in payload["records"] if record["url_type"] == "alias")
    assert alias["canonical_url"] == "/repo/alpha/"
    assert alias["proposed_disposition"] == "pending"
    assert set(alias["evidence"]) == set(inventory.EVIDENCE_REQUIREMENTS)
    assert all(item["status"] == "not_collected" for item in alias["evidence"].values())


def test_build_inventory_rejects_duplicate_urls(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(tmp_path / "content/repo/alpha/index.md", aliases=["/repo/beta/"])
    _write_page(tmp_path / "content/repo/beta/index.md")

    with pytest.raises(ValueError, match="Duplicate repository URLs"):
        inventory.build_inventory(tmp_path)


def test_check_mode_rejects_stale_inventory(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(tmp_path / "content/repo/alpha/index.md")
    output = tmp_path / "inventory.json"
    output.write_text("{}\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="stale"):
        inventory.main(["--root", str(tmp_path), "--output", str(output), "--check"])


def test_rendered_inventory_is_deterministic(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(tmp_path / "content/repo/beta/index.md")
    _write_page(tmp_path / "content/repo/alpha/index.md")

    first = inventory.rendered_inventory(tmp_path)
    second = inventory.rendered_inventory(tmp_path)

    assert first == second
    assert json.loads(first)["counts"]["total"] == 3

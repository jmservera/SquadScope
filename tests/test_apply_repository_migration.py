from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from scripts import apply_repository_migration as migration


def _record(
    url: str,
    disposition: str,
    path: str,
    content: str,
    *,
    url_type: str = "canonical",
    destination: str = "",
) -> dict[str, str]:
    return {
        "url": url,
        "url_type": url_type,
        "canonical_url": url,
        "source_path": path,
        "source_checksum": hashlib.sha256(content.encode()).hexdigest(),
        "disposition": disposition,
        "destination": destination,
    }


def _migration_data(root: Path) -> dict[str, object]:
    retained_content = "---\ntitle: retained\n---\n"
    target_content = "---\ntitle: target\n---\n"
    retired_content = "---\ntitle: retired\n---\n"
    retained_path = "content/repo/retained/index.md"
    target_path = "content/repo/target/index.md"
    retired_path = "content/repo/retired/index.md"
    for relative, content in (
        (retained_path, retained_content),
        (target_path, target_content),
        (retired_path, retired_content),
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    approved_path = root / migration.APPROVED_MAP
    approved_path.parent.mkdir(parents=True, exist_ok=True)
    approved_path.write_text("{}\n", encoding="utf-8")
    return {
        "approval": {"approved_commit": "abc123"},
        "records": [
            _record("/repo/retained/", "keep", retained_path, retained_content),
            _record(
                "/repo/old/",
                "retire",
                target_path,
                target_content,
                url_type="alias",
            ),
            _record("/repo/target/", "retire", target_path, target_content),
            _record("/repo/retired/", "retire", retired_path, retired_content),
        ],
    }


def test_apply_removes_retired_sources_and_writes_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = _migration_data(tmp_path)
    monkeypatch.setattr(migration, "load_map", lambda _root: data)

    migration.apply(tmp_path)
    migration.check(tmp_path)

    assert not (tmp_path / "content/repo/retired/index.md").exists()
    assert not (tmp_path / "content/repo/target/index.md").exists()
    assert not (tmp_path / "static/_redirects").exists()
    assert (tmp_path / "content/repo/retained/index.md").exists()
    assert (tmp_path / migration.ROLLBACK_MANIFEST).exists()


def test_apply_rejects_changed_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = _migration_data(tmp_path)
    (tmp_path / "content/repo/retired/index.md").write_text("changed\n", encoding="utf-8")
    monkeypatch.setattr(migration, "load_map", lambda _root: data)

    with pytest.raises(ValueError, match="changed before deletion"):
        migration.apply(tmp_path)

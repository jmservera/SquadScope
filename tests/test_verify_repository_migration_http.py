from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import verify_repository_migration_http as verifier


def _write_map(root: Path, records: list[dict[str, str]]) -> None:
    path = root / verifier.APPROVED_MAP
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"records": records}), encoding="utf-8")


def test_verify_once_probes_retained_index_and_representative_retirements(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_map(
        tmp_path,
        [
            {"url": "/repo/", "url_type": "index", "disposition": "keep"},
            {
                "url": "/repo/ruvnet-ruflo/",
                "url_type": "canonical",
                "disposition": "retire",
            },
            {
                "url": "/repo/pewdiepie-archdaemon-odysseus/",
                "url_type": "alias",
                "disposition": "retire",
            },
        ],
    )
    statuses = {
        "https://claracle.com/repo/": 200,
        "https://claracle.com/repo/ruvnet-ruflo/": 404,
        "https://claracle.com/repo/pewdiepie-archdaemon-odysseus/": 404,
    }
    requested: list[str] = []

    def response_for(url: str) -> SimpleNamespace:
        requested.append(url)
        return SimpleNamespace(status=statuses[url])

    monkeypatch.setattr(verifier, "response_for", response_for)

    assert verifier.verify_once(tmp_path, "https://claracle.com") == []
    assert requested == list(statuses)


def test_verify_once_rejects_map_without_retained_explorer(tmp_path: Path) -> None:
    _write_map(
        tmp_path,
        [
            {
                "url": "/repo/ruvnet-ruflo/",
                "url_type": "canonical",
                "disposition": "retire",
            }
        ],
    )

    with pytest.raises(ValueError, match="does not retain the /repo/ explorer"):
        verifier.verify_once(tmp_path, "https://claracle.com")


def test_verify_once_reports_retired_route_that_still_resolves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_map(
        tmp_path,
        [
            {"url": "/repo/", "url_type": "index", "disposition": "keep"},
            {
                "url": "/repo/ruvnet-ruflo/",
                "url_type": "canonical",
                "disposition": "retire",
            },
            {
                "url": "/repo/pewdiepie-archdaemon-odysseus/",
                "url_type": "alias",
                "disposition": "retire",
            },
        ],
    )
    statuses = {
        "https://claracle.com/repo/": 200,
        "https://claracle.com/repo/ruvnet-ruflo/": 200,
        "https://claracle.com/repo/pewdiepie-archdaemon-odysseus/": 404,
    }
    monkeypatch.setattr(verifier, "response_for", lambda url: SimpleNamespace(status=statuses[url]))

    assert verifier.verify_once(tmp_path, "https://claracle.com") == [
        "/repo/ruvnet-ruflo/: expected 404, got 200",
    ]


def test_verify_once_rejects_map_without_required_retirement(tmp_path: Path) -> None:
    _write_map(
        tmp_path,
        [
            {"url": "/repo/", "url_type": "index", "disposition": "keep"},
            {
                "url": "/repo/ruvnet-ruflo/",
                "url_type": "canonical",
                "disposition": "retire",
            },
        ],
    )

    with pytest.raises(ValueError, match="Required direct-404 retirements are missing"):
        verifier.verify_once(tmp_path, "https://claracle.com")

from __future__ import annotations

from datetime import date

import pytest

from scripts import capture_repository_production_snapshot as snapshot


def _inventory() -> dict[str, object]:
    return {
        "records": [
            {
                "url": "/repo/",
                "url_type": "index",
                "canonical_url": "/repo/",
            },
            {
                "url": "/repo/alpha/",
                "url_type": "canonical",
                "canonical_url": "/repo/alpha/",
            },
        ]
    }


def _sitemap(*paths: str) -> bytes:
    entries = "".join(f"<url><loc>https://claracle.com{path}</loc></url>" for path in paths)
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entries}</urlset>"
    ).encode()


def test_build_snapshot_reconciles_sitemap_http_and_production_only_urls() -> None:
    statuses = {
        "https://claracle.com/repo/": 200,
        "https://claracle.com/repo/alpha/": 404,
    }

    payload = snapshot.build_snapshot(
        _inventory(),
        site_origin="https://claracle.com",
        captured_at=date(2026, 8, 10),
        sitemap_data=_sitemap("/repo/", "/repo/production-only/"),
        status_getter=statuses.__getitem__,
    )

    assert payload["counts"] == {
        "local_urls": 2,
        "sitemap_urls": 2,
        "http_200": 1,
        "http_404": 1,
        "http_other_or_unavailable": 0,
        "production_only": 1,
    }
    assert payload["production_only_urls"] == ["/repo/production-only/"]
    assert payload["sources"]["search_analytics"] == "not_collected"


def test_validate_snapshot_rejects_incomplete_coverage() -> None:
    payload = {
        "counts": {"local_urls": 1, "production_only": 0},
        "production_only_urls": [],
        "records": [{"url": "/repo/"}],
    }

    with pytest.raises(ValueError, match="does not cover"):
        snapshot.validate_snapshot(payload, _inventory())


def test_validate_snapshot_rejects_unavailable_http_evidence() -> None:
    payload = {
        "counts": {"local_urls": 2, "production_only": 0},
        "production_only_urls": [],
        "records": [
            {"url": "/repo/", "http_status": 200},
            {"url": "/repo/alpha/", "http_status": 0},
        ],
    }

    with pytest.raises(ValueError, match="unavailable HTTP evidence"):
        snapshot.validate_snapshot(payload, _inventory())

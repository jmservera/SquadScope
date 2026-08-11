from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts import generate_repository_url_inventory as inventory


def test_normalized_url_collapses_root_and_trailing_slashes() -> None:
    assert inventory.normalized_url("/") == "/"
    assert inventory.normalized_url("/repo/alpha-old/") == "/repo/alpha-old/"
    assert inventory.normalized_url("repo/alpha-old") == "/repo/alpha-old/"


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

    assert payload["counts"] == {
        "index": 1,
        "canonical": 2,
        "alias": 1,
        "total": 4,
        "production_sitemap": None,
        "production_http_200": None,
        "production_http_404": None,
        "production_only": None,
    }
    assert [record["url"] for record in payload["records"]] == [
        "/repo/",
        "/repo/alpha-old/",
        "/repo/alpha/",
        "/repo/beta/",
    ]
    alias = next(record for record in payload["records"] if record["url_type"] == "alias")
    assert alias["canonical_url"] == "/repo/alpha/"
    assert alias["proposed_disposition"] == "pending"
    assert alias["candidate_disposition"] == "pending"
    assert alias["candidate_rationale"] == ""
    assert alias["internal_link_count"] is None
    assert alias["production"] == {
        "sitemap_status": "not_collected",
        "http_status": None,
    }
    assert alias["external_metrics"] == {
        "search_clicks": None,
        "search_impressions": None,
        "search_position": None,
        "referral_sessions": None,
        "sampled_inbound_link": None,
    }
    assert alias["inspection"] == {
        "verdict": None,
        "coverage_state": None,
        "last_crawl_time": None,
        "google_canonical": None,
        "user_canonical": None,
    }
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


def test_build_inventory_joins_production_snapshot(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(tmp_path / "content/repo/alpha/index.md")
    snapshot_path = tmp_path / inventory.PRODUCTION_SNAPSHOT
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(
            {
                "captured_at": "2026-08-10",
                "site_origin": "https://claracle.com",
                "sources": {"sitemap": "https://claracle.com/sitemap.xml"},
                "counts": {
                    "sitemap_urls": 1,
                    "http_200": 1,
                    "http_404": 1,
                    "production_only": 0,
                },
                "records": [
                    {
                        "url": "/repo/",
                        "in_sitemap": True,
                        "http_status": 200,
                    },
                    {
                        "url": "/repo/alpha/",
                        "in_sitemap": False,
                        "http_status": 404,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    payload = inventory.build_inventory(tmp_path)

    alpha = next(record for record in payload["records"] if record["url"] == "/repo/alpha/")
    assert alpha["production"] == {
        "sitemap_status": "not_observed",
        "http_status": 404,
    }
    assert alpha["evidence"]["sitemap"] == {
        "status": "not_observed",
        "source": "https://claracle.com/sitemap.xml",
        "window": "2026-08-10",
    }


def test_alias_and_canonical_evidence_are_isolated(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(
        tmp_path / "content/repo/alpha/index.md",
        aliases=["/repo/alpha-old/"],
    )
    snapshot_path = tmp_path / inventory.PRODUCTION_SNAPSHOT
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(
            {
                "captured_at": "2026-08-10",
                "site_origin": "https://claracle.com",
                "sources": {"sitemap": "https://claracle.com/sitemap.xml"},
                "counts": {
                    "sitemap_urls": 2,
                    "http_200": 2,
                    "http_404": 1,
                    "production_only": 0,
                },
                "records": [
                    {"url": "/repo/", "in_sitemap": True, "http_status": 200},
                    {"url": "/repo/alpha/", "in_sitemap": True, "http_status": 200},
                    {"url": "/repo/alpha-old/", "in_sitemap": False, "http_status": 404},
                ],
            }
        ),
        encoding="utf-8",
    )

    records = inventory.build_inventory(tmp_path)["records"]
    canonical = next(record for record in records if record["url"] == "/repo/alpha/")
    alias = next(record for record in records if record["url"] == "/repo/alpha-old/")

    assert canonical["evidence"]["sitemap"]["status"] == "observed"
    assert alias["evidence"]["sitemap"]["status"] == "not_observed"


def test_build_inventory_joins_external_evidence(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(tmp_path / "content/repo/alpha/index.md")
    external_path = tmp_path / inventory.EXTERNAL_EVIDENCE
    external_path.parent.mkdir(parents=True, exist_ok=True)
    external_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "sources": {
                    "search_analytics": {
                        "file": "Pages.csv",
                        "window": "2026-07-27..2026-08-09",
                    },
                    "sampled_links": {
                        "file": "gsc-top-linked-pages.csv",
                        "window": "exported 2026-08-10",
                    },
                    "first_party_referrals": {
                        "file": "ga4-repo-referrals.csv",
                        "window": "2026-07-27..2026-08-11",
                    },
                },
                "search_analytics": {
                    "/repo/alpha/": {
                        "clicks": 0,
                        "impressions": 12,
                        "position": 7.5,
                    }
                },
                "sampled_link_paths": [],
                "first_party_referrals": {},
            }
        ),
        encoding="utf-8",
    )

    records = inventory.build_inventory(tmp_path)["records"]
    alpha = next(record for record in records if record["url"] == "/repo/alpha/")

    assert alpha["evidence"]["search_analytics"] == {
        "status": "observed",
        "source": "Pages.csv",
        "window": "2026-07-27..2026-08-09",
    }
    assert alpha["evidence"]["sampled_links"]["status"] == "not_observed"
    assert alpha["external_metrics"] == {
        "search_clicks": 0,
        "search_impressions": 12,
        "search_position": 7.5,
        "referral_sessions": None,
        "sampled_inbound_link": None,
    }


def test_build_inventory_joins_url_inspection(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(tmp_path / "content/repo/alpha/index.md")
    inspection_path = tmp_path / inventory.URL_INSPECTION
    inspection_path.parent.mkdir(parents=True, exist_ok=True)
    inspection_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "captured_at": "2026-08-11T09:04:05+00:00",
                "site_url": "sc-domain:claracle.com",
                "records": [
                    {
                        "url": "/repo/alpha/",
                        "verdict": "PASS",
                        "coverage_state": "Submitted and indexed",
                        "last_crawl_time": "2026-08-03T02:11:09Z",
                        "google_canonical": "https://claracle.com/repo/alpha/",
                        "user_canonical": "https://claracle.com/repo/alpha/",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    records = inventory.build_inventory(tmp_path)["records"]
    alpha = next(record for record in records if record["url"] == "/repo/alpha/")

    assert alpha["evidence"]["url_inspection"] == {
        "status": "observed",
        "source": "data/derived/observatory/repository-url-inspection.json",
        "window": "2026-08-11T09:04:05+00:00",
    }
    assert alpha["inspection"]["verdict"] == "PASS"
    assert alpha["inspection"]["coverage_state"] == "Submitted and indexed"


def test_build_inventory_joins_pending_disposition_candidate(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    _write_page(tmp_path / "content/repo/alpha/index.md")
    candidate_path = tmp_path / inventory.DISPOSITION_CANDIDATE
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(
        json.dumps(
            {
                "reviewed_at": "2026-08-11",
                "approval_status": "pending",
                "records": [
                    {
                        "url": "/repo/alpha/",
                        "candidate_disposition": "retire",
                        "rationale": "No observed value.",
                        "internal_link_count": 3,
                        "differentiated_content": True,
                        "destination_candidate": "",
                        "destination_equivalence": "none",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    records = inventory.build_inventory(tmp_path)["records"]
    alpha = next(record for record in records if record["url"] == "/repo/alpha/")

    assert alpha["candidate_disposition"] == "retire"
    assert alpha["proposed_disposition"] == "pending"
    assert alpha["approval_status"] == "pending"
    assert alpha["internal_link_count"] == 3
    assert alpha["evidence"]["internal_links"]["status"] == "observed"
    assert alpha["evidence"]["content_review"]["status"] == "observed"
    assert alpha["evidence"]["destination_equivalence"]["status"] == "not_observed"


def test_schema_blocks_retirement_without_collected_evidence(tmp_path: Path) -> None:
    _write_page(tmp_path / "content/repo/_index.md")
    payload = inventory.build_inventory(tmp_path)
    payload["records"][0]["proposed_disposition"] = "retire"
    payload["records"][0]["approval_status"] = "approved"
    schema = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "data/schemas/repository-url-inventory.schema.json"
        ).read_text(encoding="utf-8")
    )

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(payload)

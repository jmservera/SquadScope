from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from jsonschema import ValidationError

from scripts import generate_repository_disposition_candidate as candidate


def _write_repo_page(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        "generated_by: observatory_repo_pages\n"
        "distinct_weekly_issues: 4\n"
        "star_history: [1, 2]\n"
        "weekly_appearances: [1, 2, 3, 4]\n"
        "---\n",
        encoding="utf-8",
    )


def _write_inputs(root: Path) -> None:
    for path in candidate.INPUT_PATHS:
        evidence = root / path
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("{}\n", encoding="utf-8")


def _record(
    url: str,
    *,
    url_type: str = "canonical",
    canonical_url: str | None = None,
    verdict: str = "NEUTRAL",
    impressions: int | None = None,
) -> dict[str, object]:
    slug = url.strip("/").split("/")[-1]
    return {
        "url": url,
        "url_type": url_type,
        "canonical_url": canonical_url or url,
        "source_path": f"content/repo/{slug}/index.md",
        "source_checksum": "0" * 64,
        "production": {"http_status": 200},
        "inspection": {"verdict": verdict, "coverage_state": "test"},
        "external_metrics": {
            "search_impressions": impressions,
            "sampled_inbound_link": None,
            "referral_sessions": None,
        },
    }


def test_build_candidate_keeps_value_redirects_alias_and_retires_rest(
    tmp_path: Path,
) -> None:
    records = [
        {
            **_record("/repo/", url_type="index"),
            "source_path": "content/repo/_index.md",
        },
        _record("/repo/valuable/", verdict="PASS", impressions=1),
        _record("/repo/renamed/"),
        _record(
            "/repo/legacy/",
            url_type="alias",
            canonical_url="/repo/renamed/",
            verdict="PASS",
            impressions=1,
        ),
        _record("/repo/no-value/"),
    ]
    inventory = tmp_path / candidate.INVENTORY_PATH
    inventory.parent.mkdir(parents=True, exist_ok=True)
    inventory.write_text(json.dumps({"records": records}), encoding="utf-8")
    (tmp_path / "content/repo/_index.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "content/repo/_index.md").write_text("---\n---\n", encoding="utf-8")
    for slug in ("valuable", "renamed", "no-value"):
        _write_repo_page(tmp_path / f"content/repo/{slug}/index.md")
    rendered = tmp_path / "public"
    rendered.mkdir()
    (rendered / "index.html").write_text(
        '<a href="/repo/valuable/">Value</a>',
        encoding="utf-8",
    )
    _write_inputs(tmp_path)

    payload = candidate.build_candidate(
        tmp_path,
        rendered,
        reviewed_at=date(2026, 8, 11),
    )
    by_url = {record["url"]: record for record in payload["records"]}

    assert payload["counts"] == {
        "total": 5,
        "keep": 3,
        "redirect": 1,
        "retire": 1,
        "pending_approval": 5,
    }
    assert by_url["/repo/valuable/"]["candidate_disposition"] == "keep"
    assert by_url["/repo/renamed/"]["candidate_disposition"] == "keep"
    assert by_url["/repo/legacy/"]["candidate_disposition"] == "redirect"
    assert by_url["/repo/no-value/"]["candidate_disposition"] == "retire"
    assert by_url["/repo/valuable/"]["internal_link_count"] == 1
    candidate.validate_candidate(payload, {"records": records})
    candidate.validate_freshness(tmp_path, payload)


def test_validate_candidate_rejects_approved_or_index_only_keep(tmp_path: Path) -> None:
    records = [
        {
            **_record("/repo/", url_type="index"),
            "source_path": "content/repo/_index.md",
        },
        _record("/repo/no-demand/", verdict="PASS"),
    ]
    inventory = tmp_path / candidate.INVENTORY_PATH
    inventory.parent.mkdir(parents=True, exist_ok=True)
    inventory.write_text(json.dumps({"records": records}), encoding="utf-8")
    (tmp_path / "content/repo/_index.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "content/repo/_index.md").write_text("---\n---\n", encoding="utf-8")
    _write_repo_page(tmp_path / "content/repo/no-demand/index.md")
    rendered = tmp_path / "public"
    rendered.mkdir()
    _write_inputs(tmp_path)
    payload = candidate.build_candidate(
        tmp_path,
        rendered,
        reviewed_at=date(2026, 8, 11),
    )
    assert payload["records"][1]["candidate_disposition"] == "retire"
    payload["records"][1]["candidate_disposition"] = "keep"
    payload["counts"]["keep"] = 2
    payload["counts"]["retire"] = 0

    with pytest.raises(ValueError, match="Invalid candidate disposition"):
        candidate.validate_candidate(payload, {"records": records})


def test_validate_candidate_rejects_forged_approval(tmp_path: Path) -> None:
    records = [
        {
            **_record("/repo/", url_type="index"),
            "source_path": "content/repo/_index.md",
        }
    ]
    inventory = tmp_path / candidate.INVENTORY_PATH
    inventory.parent.mkdir(parents=True, exist_ok=True)
    inventory.write_text(json.dumps({"records": records}), encoding="utf-8")
    (tmp_path / "content/repo/_index.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "content/repo/_index.md").write_text("---\n---\n", encoding="utf-8")
    rendered = tmp_path / "public"
    rendered.mkdir()
    _write_inputs(tmp_path)
    payload = candidate.build_candidate(
        tmp_path,
        rendered,
        reviewed_at=date(2026, 8, 11),
    )
    payload["approval_status"] = "approved"

    with pytest.raises(ValidationError, match="'pending' was expected"):
        candidate.validate_candidate(payload, {"records": records})

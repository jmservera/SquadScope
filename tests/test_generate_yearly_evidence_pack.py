from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import generate_yearly_evidence_pack as evidence


def _pack(week: str = "2026-W21") -> dict[str, object]:
    return {
        "synthesis_version": "1",
        "month": "2026-05",
        "weeks_covered": [week],
        "weeks": [
            {
                "week": week,
                "title": "Week 21",
                "summary": "A complete summary.",
                "top_repo": "octo/repo",
                "tags": ["agents"],
                "signal": "A complete signal.",
                "noise": "A complete noise finding.",
                "gaps": "A complete gap.",
                "conclusion": "A complete conclusion.",
                "featured_repos": ["octo/repo"],
            }
        ],
    }


def test_evidence_pack_has_stable_claim_source_links() -> None:
    result = evidence.build_yearly_evidence_pack(2026, [_pack()])

    assert result["counts"] == {"sources": 1, "claims": 5}
    assert result["sources"][0]["source_id"] == "SRC-2026-W21"
    assert result["claims"][0] == {
        "claim_id": "CLM-2026-W21-SUMMARY",
        "source_id": "SRC-2026-W21",
        "claim_type": "summary",
        "text": "A complete summary.",
        "status": "resolved",
    }


def test_evidence_pack_rejects_duplicate_week_sources() -> None:
    with pytest.raises(ValueError, match="Duplicate yearly source"):
        evidence.build_yearly_evidence_pack(2026, [_pack(), _pack()])


def test_evidence_pack_rejects_non_list_tags() -> None:
    pack = _pack()
    pack["weeks"][0]["tags"] = None

    with pytest.raises(ValueError, match="Invalid tags"):
        evidence.build_yearly_evidence_pack(2026, [pack])


def test_writer_is_deterministic(tmp_path: Path) -> None:
    analyzed = tmp_path / "data" / "analyzed"
    output = tmp_path / "data" / "derived" / "yearly"
    analyzed.mkdir(parents=True)
    source_path = analyzed / "2026-05-month-synthesis-pack.json"
    source_path.write_text(json.dumps(_pack()), encoding="utf-8")

    evidence.write_yearly_evidence_packs(analyzed, output)
    first = (output / "2026-evidence-pack.json").read_text(encoding="utf-8")
    evidence.write_yearly_evidence_packs(analyzed, output)

    assert (output / "2026-evidence-pack.json").read_text(encoding="utf-8") == first

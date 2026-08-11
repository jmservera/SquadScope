from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import generate_repository_approved_dispositions as approved


def _write_inputs(root: Path) -> None:
    records = []
    inventory = []
    for index in range(274):
        if index < 11:
            disposition = "keep"
        elif index == 11:
            disposition = "redirect"
        else:
            disposition = "retire"
        if index == 10:
            url = "/repo/odysseus-dev-odysseus/"
        elif index == 11:
            url = "/repo/pewdiepie-archdaemon-odysseus/"
        else:
            url = "/repo/" if index == 0 else f"/repo/project-{index}/"
        destination = "/repo/odysseus-dev-odysseus/" if disposition == "redirect" else ""
        records.append(
            {
                "url": url,
                "url_type": "index" if index == 0 else "canonical",
                "canonical_url": url,
                "candidate_disposition": disposition,
                "destination_candidate": destination,
                "rationale": f"{disposition} rationale",
                "approval_status": "pending",
            }
        )
        inventory.append(
            {
                "url": url,
                "source_path": (
                    "content/repo/_index.md"
                    if index == 0
                    else (
                        "content/repo/odysseus-dev-odysseus/index.md"
                        if index in {10, 11}
                        else f"content/repo/project-{index}/index.md"
                    )
                ),
                "source_checksum": hashlib.sha256(url.encode()).hexdigest(),
                "candidate_disposition": disposition,
            }
        )
    candidate = {"approval_status": "pending", "records": records}
    for relative, payload in (
        (approved.CANDIDATE, candidate),
        (approved.INVENTORY, {"records": inventory}),
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_records_exact_approved_map(tmp_path: Path) -> None:
    _write_inputs(tmp_path)

    result = approved.build(tmp_path)

    assert result["counts"] == {"keep": 1, "redirect": 0, "retire": 273, "total": 274}
    assert result["approval"]["approver"] == "jmservera"
    assert result["approval"]["gate_waiver"] is False
    assert result["approval"]["hosting_decision"] == "github_pages_explorer_only"
    assert all(record["approval_status"] == "approved" for record in result["records"])


def test_build_rejects_candidate_inventory_drift(tmp_path: Path) -> None:
    _write_inputs(tmp_path)
    inventory_path = tmp_path / approved.INVENTORY
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["records"][1]["candidate_disposition"] = "retire"
    inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

    with pytest.raises(ValueError, match="Candidate drift"):
        approved.build(tmp_path)

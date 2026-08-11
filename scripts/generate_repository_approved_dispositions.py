"""Generate the immutable approved repository migration map."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

CANDIDATE = Path("data/derived/observatory/repository-disposition-candidate.json")
INVENTORY = Path("data/derived/observatory/repository-url-inventory.json")
SCHEMA = Path("data/schemas/repository-approved-dispositions.schema.json")
DEFAULT_OUTPUT = Path("data/migrations/repository-approved-dispositions.json")
APPROVER = "jmservera"
APPROVED_AT = "2026-08-11"
APPROVED_COMMIT = "05433d5"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return loaded


def build(root: Path) -> dict[str, Any]:
    candidate_path = root / CANDIDATE
    inventory_path = root / INVENTORY
    candidate = load_object(candidate_path)
    inventory = load_object(inventory_path)
    if candidate.get("approval_status") != "pending":
        raise ValueError("The reviewed candidate must remain immutable and pending")
    candidate_records = candidate.get("records", [])
    inventory_records = inventory.get("records", [])
    if len(candidate_records) != 274 or len(inventory_records) != 274:
        raise ValueError("Approval requires exactly 274 reviewed URLs")
    inventory_by_url = {record["url"]: record for record in inventory_records}
    if set(inventory_by_url) != {record["url"] for record in candidate_records}:
        raise ValueError("Candidate and inventory URL sets differ")

    records = []
    for candidate_record in candidate_records:
        url = candidate_record["url"]
        disposition = candidate_record["candidate_disposition"]
        if disposition not in {"keep", "redirect", "retire"}:
            raise ValueError(f"Unapprovable disposition for {url}: {disposition}")
        inventory_record = inventory_by_url[url]
        if inventory_record["candidate_disposition"] != disposition:
            raise ValueError(f"Candidate drift for {url}")
        records.append(
            {
                "url": url,
                "url_type": candidate_record["url_type"],
                "canonical_url": candidate_record["canonical_url"],
                "source_path": inventory_record["source_path"],
                "source_checksum": inventory_record["source_checksum"],
                "disposition": disposition,
                "destination": candidate_record["destination_candidate"],
                "rationale": candidate_record["rationale"],
                "approval_status": "approved",
            }
        )

    counts = {
        name: sum(record["disposition"] == name for record in records)
        for name in ("keep", "redirect", "retire")
    }
    counts["total"] = len(records)
    if counts != {"keep": 11, "redirect": 1, "retire": 262, "total": 274}:
        raise ValueError(f"Unexpected approved counts: {counts}")

    return {
        "schema_version": "1.0.0",
        "approval": {
            "status": "approved",
            "approver": APPROVER,
            "approved_at": APPROVED_AT,
            "approved_commit": APPROVED_COMMIT,
            "gate_waiver": False,
            "authorized_sequence": (
                "Phase 4 may start only after every Phase 3 exit gate passes; "
                "Phase 5 may start only after every Phase 4 exit gate passes."
            ),
            "statement": (
                "Approve and go for Phase 4, once finished you can move to Phase 5 "
                "without asking, but only if all Phase 4 is finished."
            ),
        },
        "inputs": {
            CANDIDATE.as_posix(): sha256(candidate_path),
            INVENTORY.as_posix(): sha256(inventory_path),
        },
        "counts": counts,
        "records": records,
    }


def render(root: Path) -> str:
    result = build(root)
    schema = load_object(root / SCHEMA)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(result), key=lambda error: list(error.path)
    )
    if errors:
        raise ValueError(f"Approved disposition schema validation failed: {errors[0].message}")
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    rendered = render(root)
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"Approved repository dispositions are stale: {output}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

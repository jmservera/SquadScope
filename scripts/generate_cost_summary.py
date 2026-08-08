"""Project the token ledger into a reconciled public cost summary."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_LEDGER = Path("data/metrics/token-usage.jsonl")
DEFAULT_OUTPUT = Path("data/metrics/cost-summary.json")
SCHEMA_VERSION = "1.0.0"
MAX_AGE_DAYS = 30
PRICING_BASIS = "scripts.track_token_usage.MODEL_PRICING_USD_PER_MILLION"


def parse_datetime(value: str) -> datetime:
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    parsed = datetime.fromisoformat(candidate)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def load_ledger(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed ledger row {line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"Ledger row {line_number} must be an object")
        for field in ("timestamp", "week", "stage", "model", "input_tokens", "output_tokens"):
            if field not in record:
                raise ValueError(f"Ledger row {line_number} missing {field}")
        parse_datetime(str(record["timestamp"]))
        records.append(record)
    if not records:
        raise ValueError("Token usage ledger is empty")
    return records


def reconcile_records(
    records: list[dict[str, Any]], *, legacy_policy: str
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    legacy = [
        record
        for record in records
        if record.get("workflow_run_id") in (None, "") or record.get("run_attempt") is None
    ]
    if legacy and legacy_policy == "reject":
        raise ValueError(
            f"{len(legacy)} ledger rows lack workflow run identity; sponsor cutover policy required"
        )

    identified = [record for record in records if record not in legacy]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in identified:
        attempt = record["run_attempt"]
        if not isinstance(attempt, int) or attempt < 1:
            raise ValueError("run_attempt must be a positive integer")
        grouped[(str(record["workflow_run_id"]), str(record["stage"]))].append(record)

    accepted: list[dict[str, Any]] = []
    superseded = 0
    for identity, candidates in grouped.items():
        accepted_attempt = max(int(record["run_attempt"]) for record in candidates)
        winners = [record for record in candidates if record["run_attempt"] == accepted_attempt]
        if len(winners) != 1:
            raise ValueError(
                f"Duplicate accepted identity for run {identity[0]}, stage {identity[1]}, "
                f"attempt {accepted_attempt}"
            )
        accepted.append(winners[0])
        superseded += len(candidates) - 1

    accepted.sort(
        key=lambda record: (
            parse_datetime(str(record["timestamp"])),
            str(record["workflow_run_id"]),
            str(record["stage"]),
        )
    )
    exclusions = {
        "legacy_unidentified": len(legacy),
        "superseded_attempts": superseded,
        "model_none": sum(str(record["model"]).lower() == "none" for record in accepted),
    }
    return accepted, exclusions


def build_projection(
    records: list[dict[str, Any]],
    *,
    generated_at: datetime,
    legacy_policy: str = "reject",
    max_age_days: int = MAX_AGE_DAYS,
) -> dict[str, Any]:
    accepted, exclusions = reconcile_records(records, legacy_policy=legacy_policy)
    billable = [record for record in accepted if str(record["model"]).lower() != "none"]
    if not billable:
        raise ValueError("No identified billable accepted records remain after reconciliation")

    latest = max(parse_datetime(str(record["timestamp"])) for record in accepted)
    age_days = (generated_at.astimezone(UTC) - latest.astimezone(UTC)).total_seconds() / 86_400
    if age_days < 0:
        raise ValueError("Latest ledger record is in the future")
    if age_days > max_age_days:
        raise ValueError(
            f"Token usage ledger is stale ({age_days:.1f} days; maximum {max_age_days})"
        )

    accepted_identities = [
        {
            "workflow_run_id": str(record["workflow_run_id"]),
            "stage": str(record["stage"]),
            "run_attempt": int(record["run_attempt"]),
            "week": str(record["week"]),
            "model": str(record["model"]),
        }
        for record in accepted
    ]
    unpriced = [record for record in billable if record.get("cost_usd") is None]
    if unpriced:
        raise ValueError(
            f"{len(unpriced)} billable accepted records lack a reconciled cost_usd value"
        )
    total_cost = round(sum(float(record["cost_usd"]) for record in billable), 6)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "currency": "USD",
        "pricing_basis": PRICING_BASIS,
        "provenance": {
            "ledger": "data/metrics/token-usage.jsonl",
            "legacy_policy": legacy_policy,
            "maximum_age_days": max_age_days,
        },
        "covered_period": {
            "start": min(str(record["week"]) for record in accepted),
            "end": max(str(record["week"]) for record in accepted),
            "latest_record_at": latest.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        },
        "accepted_identities": accepted_identities,
        "exclusions": exclusions,
        "reconciliation": {
            "status": "reconciled",
            "input_records": len(records),
            "accepted_records": len(accepted),
            "billable_records": len(billable),
        },
        "totals": {
            "cost": total_cost,
            "input_tokens": sum(int(record["input_tokens"]) for record in billable),
            "output_tokens": sum(int(record["output_tokens"]) for record in billable),
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--generated-at", required=True, help="ISO-8601 projection time.")
    parser.add_argument(
        "--legacy-policy",
        choices=("reject", "exclude-unidentified"),
        default="reject",
        help="Treatment for pre-identity rows; exclusion requires sponsor approval.",
    )
    parser.add_argument("--max-age-days", type=int, default=MAX_AGE_DAYS)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    projection = build_projection(
        load_ledger(args.ledger),
        generated_at=parse_datetime(args.generated_at),
        legacy_policy=args.legacy_policy,
        max_age_days=args.max_age_days,
    )
    rendered = json.dumps(projection, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"Cost summary is stale: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

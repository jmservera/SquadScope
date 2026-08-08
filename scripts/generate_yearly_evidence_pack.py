"""Build deterministic yearly claim/source evidence packs from monthly source packs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

MONTH_PACK_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{2})-month-synthesis-pack\.json$")
CLAIM_FIELDS = ("summary", "signal", "noise", "gaps", "conclusion")
SCHEMA_VERSION = "1.0.0"


def load_month_packs(analyzed_dir: Path) -> list[dict[str, Any]]:
    packs: list[dict[str, Any]] = []
    for path in sorted(analyzed_dir.glob("*-month-synthesis-pack.json")):
        match = MONTH_PACK_PATTERN.match(path.name)
        if match is None:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("weeks"), list):
            raise ValueError(f"Invalid monthly synthesis pack: {path}")
        payload["_path"] = path.as_posix()
        packs.append(payload)
    return packs


def build_yearly_evidence_pack(year: int, month_packs: list[dict[str, Any]]) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    claims: list[dict[str, str]] = []
    seen_sources: set[str] = set()
    seen_claims: set[str] = set()

    for pack in sorted(month_packs, key=lambda item: str(item["month"])):
        month = str(pack["month"])
        if not month.startswith(f"{year}-"):
            continue
        for week in pack["weeks"]:
            if not isinstance(week, dict) or not week.get("week"):
                raise ValueError(f"Invalid weekly source in {month}")
            week_slug = str(week["week"])
            source_id = f"SRC-{week_slug}"
            if source_id in seen_sources:
                raise ValueError(f"Duplicate yearly source: {source_id}")
            seen_sources.add(source_id)
            tags = week.get("tags", [])
            if not isinstance(tags, list):
                raise ValueError(f"Invalid tags for {week_slug} in {month}")
            sources.append(
                {
                    "source_id": source_id,
                    "month": month,
                    "week": week_slug,
                    "title": str(week.get("title", "")),
                    "top_repo": str(week.get("top_repo", "")),
                    "tags": [str(tag) for tag in tags],
                }
            )
            for field in CLAIM_FIELDS:
                text = str(week.get(field, "")).strip()
                if not text:
                    continue
                claim_id = f"CLM-{week_slug}-{field.upper()}"
                if claim_id in seen_claims:
                    raise ValueError(f"Duplicate yearly claim: {claim_id}")
                seen_claims.add(claim_id)
                claims.append(
                    {
                        "claim_id": claim_id,
                        "source_id": source_id,
                        "claim_type": field,
                        "text": text,
                        "status": "resolved",
                    }
                )

    if not sources or not claims:
        raise ValueError(f"No complete evidence was found for {year}")
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "yearly-evidence-pack",
        "year": year,
        "months_covered": sorted({source["month"] for source in sources}),
        "sources": sources,
        "claims": claims,
        "counts": {"sources": len(sources), "claims": len(claims)},
    }


def write_yearly_evidence_packs(analyzed_dir: Path, output_dir: Path) -> list[Path]:
    packs = load_month_packs(analyzed_dir)
    years = sorted({int(str(pack["month"])[:4]) for pack in packs})
    written: list[Path] = []
    for year in years:
        payload = build_yearly_evidence_pack(year, packs)
        path = output_dir / f"{year}-evidence-pack.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path)
    return written

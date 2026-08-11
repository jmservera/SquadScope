"""Apply and verify the approved repository URL migration transaction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

APPROVED_MAP = Path("data/migrations/repository-approved-dispositions.json")
ROLLBACK_MANIFEST = Path("data/migrations/repository-migration-rollback.json")


def load_map(root: Path) -> dict[str, Any]:
    path = root / APPROVED_MAP
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if loaded.get("approval", {}).get("status") != "approved":
        raise ValueError("Repository migration map is not approved")
    if loaded.get("counts") != {"keep": 1, "redirect": 0, "retire": 273, "total": 274}:
        raise ValueError("Approved repository migration counts changed")
    return loaded


def validate_no_redirects(records: list[dict[str, Any]]) -> None:
    redirects = [record for record in records if record["disposition"] == "redirect"]
    if redirects:
        raise ValueError(f"No redirects are approved, found {len(redirects)}")


def removed_source_paths(records: list[dict[str, Any]]) -> list[str]:
    return sorted(
        {
            record["source_path"]
            for record in records
            if record["url_type"] == "canonical" and record["disposition"] == "retire"
        }
    )


def render_manifest(root: Path, data: dict[str, Any]) -> str:
    records = data["records"]
    by_path = {record["source_path"]: record for record in records}
    removed = [
        {"path": relative, "sha256": by_path[relative]["source_checksum"]}
        for relative in removed_source_paths(records)
    ]
    return (
        json.dumps(
            {
                "schema_version": "1.0.0",
                "pre_migration_commit": data["approval"]["approved_commit"],
                "approved_map": APPROVED_MAP.as_posix(),
                "approved_map_sha256": hashlib.sha256(
                    (root / APPROVED_MAP).read_bytes()
                ).hexdigest(),
                "removed_sources": removed,
                "rollback": (
                    "Restore the listed files from pre_migration_commit, rebuild, "
                    "and redeploy through GitHub Pages."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def apply(root: Path) -> None:
    data = load_map(root)
    records = data["records"]
    validate_no_redirects(records)
    manifest = render_manifest(root, data)
    for relative in removed_source_paths(records):
        path = root / relative
        if path.exists():
            record = next(
                record
                for record in records
                if record["source_path"] == relative and record["url_type"] == "canonical"
            )
            if hashlib.sha256(path.read_bytes()).hexdigest() != record["source_checksum"]:
                raise ValueError(f"Approved source changed before deletion: {relative}")
            path.unlink()
    redirects = root / "static/_redirects"
    if redirects.exists():
        redirects.unlink()
    manifest_path = root / ROLLBACK_MANIFEST
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(manifest, encoding="utf-8")


def check(root: Path) -> None:
    data = load_map(root)
    records = data["records"]
    validate_no_redirects(records)
    if (root / "static/_redirects").exists():
        raise ValueError("Cloudflare redirect file must be absent")
    for relative in removed_source_paths(records):
        if (root / relative).exists():
            raise ValueError(f"Retired source still exists: {relative}")
    for record in records:
        if record["disposition"] == "keep" and record["url_type"] == "canonical":
            if not (root / record["source_path"]).exists():
                raise ValueError(f"Retained source is missing: {record['source_path']}")
    manifest = root / ROLLBACK_MANIFEST
    if not manifest.exists():
        raise ValueError("Rollback manifest is missing")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    if args.apply:
        apply(root)
    check(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

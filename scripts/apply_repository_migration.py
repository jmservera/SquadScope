"""Apply and verify the approved repository URL migration transaction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

APPROVED_MAP = Path("data/migrations/repository-approved-dispositions.json")
REDIRECTS = Path("static/_redirects")
ROLLBACK_MANIFEST = Path("data/migrations/repository-migration-rollback.json")


def load_map(root: Path) -> dict[str, Any]:
    path = root / APPROVED_MAP
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if loaded.get("approval", {}).get("status") != "approved":
        raise ValueError("Repository migration map is not approved")
    if loaded.get("counts") != {"keep": 11, "redirect": 1, "retire": 262, "total": 274}:
        raise ValueError("Approved repository migration counts changed")
    return loaded


def expected_redirects(records: list[dict[str, Any]]) -> str:
    redirects = [record for record in records if record["disposition"] == "redirect"]
    if len(redirects) != 1:
        raise ValueError("Exactly one redirect is required")
    source = redirects[0]
    target = source["destination"]
    target_record = next((record for record in records if record["url"] == target), None)
    if not target_record or target_record["disposition"] != "keep":
        raise ValueError(f"Redirect target is not retained: {target}")
    if target == source["url"]:
        raise ValueError("Redirect loop detected")
    return f"{source['url']} {target} 301\n"


def removed_source_paths(records: list[dict[str, Any]]) -> list[str]:
    redirected_sources = {
        record["source_path"] for record in records if record["disposition"] == "redirect"
    }
    return sorted(
        {
            record["source_path"]
            for record in records
            if record["url_type"] == "canonical"
            and record["disposition"] == "retire"
            and record["source_path"] not in redirected_sources
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
                    "Restore listed files and content/repo/odysseus-dev-odysseus/index.md "
                    "from pre_migration_commit, remove static/_redirects, rebuild, and redeploy."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def remove_alias(path: Path, alias: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    alias_line = f"- {alias}\n"
    try:
        index = lines.index(alias_line)
    except ValueError as error:
        if alias not in path.read_text(encoding="utf-8"):
            return
        raise ValueError(
            f"Approved alias has an unexpected representation in {path}: {alias}"
        ) from error
    del lines[index]
    if index and lines[index - 1].strip() == "aliases:":
        del lines[index - 1]
    path.write_text("".join(lines), encoding="utf-8")


def apply(root: Path) -> None:
    data = load_map(root)
    records = data["records"]
    manifest = render_manifest(root, data)
    for relative in removed_source_paths(records):
        path = root / relative
        if path.exists():
            record = next(record for record in records if record["source_path"] == relative)
            if hashlib.sha256(path.read_bytes()).hexdigest() != record["source_checksum"]:
                raise ValueError(f"Approved source changed before deletion: {relative}")
            path.unlink()
    for record in records:
        if record["disposition"] == "redirect":
            remove_alias(root / record["source_path"], record["url"])
    redirects = root / REDIRECTS
    redirects.parent.mkdir(parents=True, exist_ok=True)
    redirects.write_text(expected_redirects(records), encoding="utf-8")
    manifest_path = root / ROLLBACK_MANIFEST
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(manifest, encoding="utf-8")


def check(root: Path) -> None:
    data = load_map(root)
    records = data["records"]
    redirects = root / REDIRECTS
    if not redirects.exists() or redirects.read_text(encoding="utf-8") != expected_redirects(
        records
    ):
        raise ValueError("Hosting redirects differ from the approved map")
    for relative in removed_source_paths(records):
        if (root / relative).exists():
            raise ValueError(f"Retired source still exists: {relative}")
    for record in records:
        if record["disposition"] == "keep" and record["url_type"] == "canonical":
            if not (root / record["source_path"]).exists():
                raise ValueError(f"Retained source is missing: {record['source_path']}")
        if record["disposition"] == "redirect":
            text = (root / record["source_path"]).read_text(encoding="utf-8")
            if record["url"] in text:
                raise ValueError(f"Redirect alias still emits a Hugo page: {record['url']}")
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

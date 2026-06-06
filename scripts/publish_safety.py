#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


BACKUP_SCHEMA_VERSION = "publish_backup_v1"


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def relpath_under_root(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        raise SystemExit(f"Path must be relative to repository root: {value}")
    resolved_root = root.resolve()
    resolved_path = (resolved_root / path).resolve()
    try:
        return resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise SystemExit(f"Path must stay under repository root: {value}") from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish-branch backup and restore safeguards.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup = subparsers.add_parser("backup-existing", help="Create an immutable backup manifest for target paths.")
    backup.add_argument("--root", default=".", type=Path)
    backup.add_argument("--week", required=True)
    backup.add_argument("--run-id", required=True)
    backup.add_argument("--kind", required=True, choices=["analysis", "content"])
    backup.add_argument("--manifest", required=True, type=Path, help="Publish eligibility manifest.")
    backup.add_argument("--expected-publish-ref", default="")
    backup.add_argument("--actual-publish-ref", default="")
    backup.add_argument("--backup-root", default=Path("data/backups"), type=Path)
    backup.add_argument("--path", action="append", required=True, help="Published path to snapshot before replacement.")

    restore = subparsers.add_parser("restore-backup", help="Restore files from an immutable publish backup manifest.")
    restore.add_argument("--root", default=".", type=Path)
    restore.add_argument("--backup-manifest", required=True, type=Path)

    return parser.parse_args(argv)


def backup_existing(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    source_manifest_relative = relpath_under_root(root, args.manifest.as_posix())
    source_manifest = root / source_manifest_relative
    source_manifest_payload = load_json(source_manifest)

    backup_root = root / relpath_under_root(root, args.backup_root.as_posix())
    backup_dir = backup_root / args.week / args.run_id / args.kind
    manifest_path = backup_dir / "manifest.json"
    if manifest_path.exists():
        raise SystemExit(f"Refusing to overwrite immutable backup manifest: {manifest_path}")
    backup_dir.mkdir(parents=True, exist_ok=False)

    files_dir = backup_dir / "files"
    entries: list[dict[str, Any]] = []
    for raw_path in args.path:
        relative = relpath_under_root(root, raw_path)
        source = root / relative
        entry: dict[str, Any] = {
            "path": relative.as_posix(),
            "existed": source.exists(),
            "size_bytes": source.stat().st_size if source.exists() and source.is_file() else 0,
            "sha256": sha256_file(source),
        }
        if source.exists() and source.is_file():
            destination = files_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            entry["backup_path"] = destination.relative_to(root).as_posix()
        entries.append(entry)

    manifest = {
        "schema_version": BACKUP_SCHEMA_VERSION,
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "week": args.week,
        "run_id": args.run_id,
        "kind": args.kind,
        "publish_ref": {
            "expected": args.expected_publish_ref,
            "actual": args.actual_publish_ref,
        },
        "source_manifest": {
            "path": source_manifest_relative.as_posix(),
            "sha256": sha256_file(source_manifest),
            "candidate": source_manifest_payload.get("candidate") if source_manifest_payload else None,
            "source_artifacts": source_manifest_payload.get("source_artifacts") if source_manifest_payload else None,
            "analysis": source_manifest_payload.get("analysis") if source_manifest_payload else None,
        },
        "files": entries,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Created immutable publish backup: {manifest_path.relative_to(root).as_posix()}")
    return 0


def restore_backup(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    backup_manifest = args.backup_manifest if args.backup_manifest.is_absolute() else root / args.backup_manifest
    payload = load_json(backup_manifest)
    if payload is None:
        raise SystemExit(f"Backup manifest is missing or malformed: {backup_manifest}")
    if payload.get("schema_version") != BACKUP_SCHEMA_VERSION:
        raise SystemExit(f"Unsupported backup schema: {payload.get('schema_version')!r}")
    files = payload.get("files")
    if not isinstance(files, list):
        raise SystemExit("Backup manifest has no files list.")

    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise SystemExit("Backup file entry is malformed.")
        target_relative = relpath_under_root(root, entry["path"])
        target = root / target_relative
        if entry.get("existed") is True:
            backup_path = entry.get("backup_path")
            if not isinstance(backup_path, str):
                raise SystemExit(f"Backup entry lacks backup_path for {entry['path']}")
            source_relative = relpath_under_root(root, backup_path)
            source = root / source_relative
            if sha256_file(source) != entry.get("sha256"):
                raise SystemExit(f"Backup checksum mismatch for {backup_path}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        else:
            target.unlink(missing_ok=True)
    print(f"Restored publish backup: {backup_manifest.relative_to(root).as_posix()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "backup-existing":
        return backup_existing(args)
    if args.command == "restore-backup":
        return restore_backup(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())

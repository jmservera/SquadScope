#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BACKUP_SCHEMA_VERSION = "publish_backup_v1"
PUBLISH_MANIFEST_SCHEMA_VERSION = "publish_eligibility_v1"
RAW_STORE_SCHEMA_VERSION = "raw_store_v1"
WEEK_PATTERN = re.compile(r"^[0-9]{4}-W[0-9]{2}$")
SAFE_COMPONENT_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


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


def path_under_root(root: Path, value: Path) -> tuple[Path, Path]:
    resolved_root = root.resolve()
    resolved_path = (value if value.is_absolute() else resolved_root / value).resolve()
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise SystemExit(f"Path must stay under repository root: {value}") from exc
    return relative, resolved_path


def require_safe_component(value: str, *, label: str) -> str:
    candidate = value.strip()
    if not candidate or not SAFE_COMPONENT_PATTERN.fullmatch(candidate):
        raise SystemExit(f"Invalid {label}: {value!r}")
    return candidate


def require_week(value: str) -> str:
    week = value.strip()
    if not WEEK_PATTERN.fullmatch(week):
        raise SystemExit(f"Invalid week format. Expected YYYY-WNN, got: {value!r}")
    return week


def require_raw_path(root: Path, value: str) -> tuple[Path, Path]:
    relative = relpath_under_root(root, value)
    if relative.parts[:2] != ("data", "raw"):
        raise SystemExit(f"Raw store paths must live under data/raw/: {value}")
    return relative, root / relative


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish-branch backup and restore safeguards.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup = subparsers.add_parser(
        "backup-existing", help="Create an immutable backup manifest for target paths."
    )
    backup.add_argument("--root", default=".", type=Path)
    backup.add_argument("--week", required=True)
    backup.add_argument("--run-id", required=True)
    backup.add_argument("--kind", required=True, choices=["analysis", "content"])
    backup.add_argument(
        "--manifest", required=True, type=Path, help="Publish eligibility manifest."
    )
    backup.add_argument("--expected-publish-ref", default="")
    backup.add_argument("--actual-publish-ref", default="")
    backup.add_argument("--backup-root", default=Path("data/backups"), type=Path)
    backup.add_argument(
        "--path",
        action="append",
        required=True,
        help="Published path to snapshot before replacement.",
    )

    restore = subparsers.add_parser(
        "restore-backup", help="Restore files from an immutable publish backup manifest."
    )
    restore.add_argument("--root", default=".", type=Path)
    restore.add_argument("--backup-manifest", required=True, type=Path)

    store_raw_parser = subparsers.add_parser(
        "store-raw", help="Store raw evidence under an immutable week/source-run path."
    )
    store_raw_parser.add_argument("--root", default=".", type=Path)
    store_raw_parser.add_argument("--week", required=True)
    store_raw_parser.add_argument("--source-run-id", required=True)
    store_raw_parser.add_argument("--source-artifact-id", required=True)
    store_raw_parser.add_argument("--source-artifact-name", default="raw-data")
    store_raw_parser.add_argument("--source-head-sha", required=True)
    store_raw_parser.add_argument("--store-root", default=Path("data/raw-store"), type=Path)
    store_raw_parser.add_argument(
        "--path",
        action="append",
        required=True,
        help="Week-scoped data/raw file to preserve.",
    )

    restore_raw_parser = subparsers.add_parser(
        "restore-raw", help="Restore hash-verified raw evidence from a source workflow run."
    )
    restore_raw_parser.add_argument("--root", default=".", type=Path)
    restore_raw_parser.add_argument("--week", required=True)
    restore_raw_parser.add_argument("--source-run-id", required=True)
    restore_raw_parser.add_argument("--store-root", default=Path("data/raw-store"), type=Path)

    return parser.parse_args(argv)


def backup_existing(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    source_manifest_relative = relpath_under_root(root, args.manifest.as_posix())
    source_manifest = root / source_manifest_relative
    source_manifest_payload = load_json(source_manifest)
    if source_manifest_payload is None:
        raise SystemExit(
            f"Publish manifest is missing or malformed: {source_manifest_relative.as_posix()}"
        )
    if source_manifest_payload.get("schema_version") != PUBLISH_MANIFEST_SCHEMA_VERSION:
        raise SystemExit(
            f"Unsupported publish manifest schema: {source_manifest_payload.get('schema_version')!r}"
        )
    if not isinstance(source_manifest_payload.get("candidate"), dict):
        raise SystemExit("Publish manifest lacks candidate block.")
    if not isinstance(source_manifest_payload.get("source_artifacts"), list):
        raise SystemExit("Publish manifest lacks source artifact provenance.")
    if not isinstance(source_manifest_payload.get("analysis"), dict):
        raise SystemExit("Publish manifest lacks analysis provenance.")

    entries: list[dict[str, Any]] = []
    for raw_path in args.path:
        relative = relpath_under_root(root, raw_path)
        source = root / relative
        if source.exists() and not source.is_file():
            raise SystemExit(f"Backup target must be a regular file: {relative.as_posix()}")
        entries.append(
            {
                "path": relative.as_posix(),
                "existed": source.exists(),
                "size_bytes": source.stat().st_size if source.exists() else 0,
                "sha256": sha256_file(source),
            }
        )

    backup_root = root / relpath_under_root(root, args.backup_root.as_posix())
    backup_dir = backup_root / args.week / args.run_id / args.kind
    manifest_path = backup_dir / "manifest.json"
    if manifest_path.exists():
        raise SystemExit(f"Refusing to overwrite immutable backup manifest: {manifest_path}")
    backup_dir.mkdir(parents=True, exist_ok=False)

    files_dir = backup_dir / "files"
    for entry in entries:
        relative = Path(entry["path"])
        source = root / relative
        if source.exists():
            destination = files_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            entry["backup_path"] = destination.relative_to(root).as_posix()

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
            "candidate": source_manifest_payload.get("candidate")
            if source_manifest_payload
            else None,
            "source_artifacts": source_manifest_payload.get("source_artifacts")
            if source_manifest_payload
            else None,
            "analysis": source_manifest_payload.get("analysis")
            if source_manifest_payload
            else None,
        },
        "files": entries,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Created immutable publish backup: {manifest_path.relative_to(root).as_posix()}")
    return 0


def restore_backup(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    backup_manifest_relative, backup_manifest = path_under_root(root, args.backup_manifest)
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
    print(f"Restored publish backup: {backup_manifest_relative.as_posix()}")
    return 0


def store_raw(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    week = require_week(args.week)
    source_run_id = require_safe_component(args.source_run_id, label="source_run_id")
    source_artifact_id = args.source_artifact_id.strip()
    source_artifact_name = args.source_artifact_name.strip()
    source_head_sha = args.source_head_sha.strip()
    if not source_artifact_id:
        raise SystemExit("source_artifact_id is required.")
    if not source_artifact_name:
        raise SystemExit("source_artifact_name is required.")
    if not source_head_sha:
        raise SystemExit("source_head_sha is required.")

    sources: list[tuple[Path, Path]] = []
    seen_sources: set[Path] = set()
    for raw_path in args.path:
        relative, source = require_raw_path(root, raw_path)
        if relative in seen_sources:
            raise SystemExit(f"Duplicate raw store source: {relative.as_posix()}")
        seen_sources.add(relative)
        if not source.exists() or not source.is_file():
            raise SystemExit(f"Raw store source must be a regular file: {relative.as_posix()}")
        if relative.name != f"{week}.json" and not relative.name.startswith(f"{week}-"):
            raise SystemExit(f"Raw store source does not belong to {week}: {relative.as_posix()}")
        sources.append((relative, source))

    store_root = root / relpath_under_root(root, args.store_root.as_posix())
    destination = store_root / week / source_run_id
    if destination.exists():
        raise SystemExit(f"Refusing to overwrite immutable raw store: {destination}")
    destination.mkdir(parents=True, exist_ok=False)

    entries: list[dict[str, Any]] = []
    try:
        for relative, source in sorted(sources):
            stored = destination / "files" / relative
            stored.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, stored)
            source_hash = sha256_file(source)
            stored_hash = sha256_file(stored)
            if source_hash is None or stored_hash != source_hash:
                raise SystemExit(f"Raw store checksum mismatch while copying {relative.as_posix()}")
            entries.append(
                {
                    "week": week,
                    "artifact_id": source_artifact_id,
                    "source_run_id": source_run_id,
                    "head_sha": source_head_sha,
                    "original_path": relative.as_posix(),
                    "stored_path": stored.relative_to(root).as_posix(),
                    "size_bytes": stored.stat().st_size,
                    "sha256": stored_hash,
                }
            )

        manifest = {
            "schema_version": RAW_STORE_SCHEMA_VERSION,
            "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "week": week,
            "source_run_id": source_run_id,
            "source_artifact": {
                "id": source_artifact_id,
                "name": source_artifact_name,
                "head_sha": source_head_sha,
                "retention_days": 90,
            },
            "files": entries,
        }
        manifest_path = destination / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except BaseException:
        shutil.rmtree(destination, ignore_errors=True)
        raise

    print(f"Created immutable raw store: {destination.relative_to(root).as_posix()}")
    return 0


def validate_raw_store_manifest(
    root: Path,
    manifest_path: Path,
    *,
    expected_week: str,
    expected_source_run_id: str,
) -> tuple[dict[str, Any], list[tuple[Path, Path, dict[str, Any]]]]:
    root = root.resolve()
    week = require_week(expected_week)
    source_run_id = require_safe_component(expected_source_run_id, label="source_run_id")
    manifest_relative, manifest = path_under_root(root, manifest_path)
    payload = load_json(manifest)
    if payload is None:
        raise SystemExit(f"Raw store manifest is missing or malformed: {manifest_relative}")
    if payload.get("schema_version") != RAW_STORE_SCHEMA_VERSION:
        raise SystemExit(f"Unsupported raw store schema: {payload.get('schema_version')!r}")
    if payload.get("week") != week:
        raise SystemExit(f"Raw store week mismatch: expected {week}, found {payload.get('week')!r}")
    if payload.get("source_run_id") != source_run_id:
        raise SystemExit(
            "Raw store source_run_id mismatch: "
            f"expected {source_run_id}, found {payload.get('source_run_id')!r}"
        )
    source_artifact = payload.get("source_artifact")
    if (
        not isinstance(source_artifact, dict)
        or not source_artifact.get("id")
        or source_artifact.get("name") != "raw-data"
        or not source_artifact.get("head_sha")
    ):
        raise SystemExit("Raw store manifest lacks source artifact provenance.")
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit("Raw store manifest has no files list.")

    verified: list[tuple[Path, Path, dict[str, Any]]] = []
    store_directory = manifest.parent.resolve()
    store_directory_relative = manifest.parent.relative_to(root)
    seen_original_paths: set[Path] = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise SystemExit("Raw store file entry is malformed.")
        original_path = entry.get("original_path")
        stored_path = entry.get("stored_path")
        if not isinstance(original_path, str) or not isinstance(stored_path, str):
            raise SystemExit("Raw store file entry lacks original_path or stored_path.")
        if entry.get("week") != week or entry.get("source_run_id") != source_run_id:
            raise SystemExit(f"Raw store file provenance mismatch for {original_path}")
        if entry.get("artifact_id") != source_artifact.get("id") or entry.get(
            "head_sha"
        ) != source_artifact.get("head_sha"):
            raise SystemExit(f"Raw store artifact provenance mismatch for {original_path}")

        target_relative, target = require_raw_path(root, original_path)
        if target_relative in seen_original_paths:
            raise SystemExit(f"Duplicate raw store original_path: {original_path}")
        seen_original_paths.add(target_relative)
        stored_relative = relpath_under_root(root, stored_path)
        expected_stored_relative = store_directory_relative / "files" / target_relative
        if stored_relative != expected_stored_relative:
            raise SystemExit(f"Raw store stored_path mismatch for {original_path}: {stored_path}")
        stored = root / stored_relative
        try:
            stored.resolve().relative_to(store_directory)
        except ValueError as exc:
            raise SystemExit(
                f"Raw store file must stay under its immutable run directory: {stored_path}"
            ) from exc
        if not stored.exists() or not stored.is_file():
            raise SystemExit(f"Raw store file is missing: {stored_relative.as_posix()}")
        if stored.stat().st_size != entry.get("size_bytes"):
            raise SystemExit(f"Raw store size mismatch for {stored_relative.as_posix()}")
        if sha256_file(stored) != entry.get("sha256"):
            raise SystemExit(f"Raw store checksum mismatch for {stored_relative.as_posix()}")
        verified.append((stored, target, entry))

    required_raw_path = Path("data") / "raw" / f"{week}.json"
    if required_raw_path not in seen_original_paths:
        raise SystemExit(f"Raw store manifest lacks required payload: {required_raw_path}")
    return payload, verified


def restore_raw(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    week = require_week(args.week)
    source_run_id = require_safe_component(args.source_run_id, label="source_run_id")
    store_root = root / relpath_under_root(root, args.store_root.as_posix())
    manifest = store_root / week / source_run_id / "manifest.json"
    _, verified = validate_raw_store_manifest(
        root,
        manifest,
        expected_week=week,
        expected_source_run_id=source_run_id,
    )

    for stored, target, _ in verified:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(stored, target)
    print(
        "Restored hash-verified raw evidence: "
        f"week={week} source_run_id={source_run_id} files={len(verified)}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "backup-existing":
        return backup_existing(args)
    if args.command == "restore-backup":
        return restore_backup(args)
    if args.command == "store-raw":
        return store_raw(args)
    if args.command == "restore-raw":
        return restore_raw(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())

"""Fail closed when a Copilot CLI invocation mutates unexpected workspace paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess  # nosec B404
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

SCHEMA_VERSION = 1
ALLOWED_ARTIFACT_PREFIXES = ("data/candidates/", "data/metrics/")
ALLOWED_ARTIFACT_SUFFIXES = (".log", ".md")


@dataclass(frozen=True)
class FileState:
    kind: str
    mode: int
    sha256: str


@dataclass(frozen=True)
class WorkspaceSnapshot:
    schema_version: int
    root: str
    allowed_paths: list[str]
    directories: list[str]
    files: dict[str, FileState]
    index_sha256: str


class WorkspaceError(ValueError):
    """Raised when the containment contract or workspace state is invalid."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_git(root: Path, *args: str) -> bytes:
    git_path = shutil.which("git")
    if git_path is None:
        raise WorkspaceError("Git executable not found on PATH")
    # The executable is resolved explicitly and invoked with a fixed argv without a shell.
    result = subprocess.run(  # nosec B603
        [git_path, "-C", str(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise WorkspaceError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _normalize_allowed_path(root: Path, raw_path: str, *, check_existing_entry: bool = True) -> str:
    if not raw_path or "\\" in raw_path or any(character in raw_path for character in "*?["):
        raise WorkspaceError(f"invalid allowed path: {raw_path!r}")
    candidate = PurePosixPath(raw_path)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise WorkspaceError(f"allowed path must be a normalized relative file: {raw_path!r}")

    normalized = candidate.as_posix()
    if not normalized.startswith(ALLOWED_ARTIFACT_PREFIXES):
        raise WorkspaceError(f"allowed artifact is outside approved data paths: {normalized}")
    if not normalized.endswith(ALLOWED_ARTIFACT_SUFFIXES):
        raise WorkspaceError(f"allowed artifact has an unsupported file type: {normalized}")
    if any(marker in candidate.name.lower() for marker in ("prompt", "canary")):
        raise WorkspaceError(f"prompt and canary files cannot be allowed: {normalized}")
    absolute = root.joinpath(*candidate.parts)
    if check_existing_entry:
        if absolute.exists() or absolute.is_symlink():
            raise WorkspaceError(f"allowed artifact must be absent at snapshot time: {normalized}")

    parent = absolute.parent.resolve(strict=True)
    try:
        parent.relative_to(root)
    except ValueError as error:
        raise WorkspaceError(f"allowed path escapes workspace: {normalized}") from error
    return normalized


def validate_allowed_paths(
    root: Path,
    raw_paths: Sequence[str],
    *,
    check_existing_entries: bool = True,
) -> list[str]:
    root = root.resolve(strict=True)
    if not (root / ".git").exists():
        raise WorkspaceError(f"workspace is not a Git checkout: {root}")
    normalized = sorted(
        {
            _normalize_allowed_path(root, path, check_existing_entry=check_existing_entries)
            for path in raw_paths
        }
    )
    if len(normalized) != len(raw_paths):
        raise WorkspaceError("allowed paths must be unique")
    return normalized


def _file_state(path: Path) -> FileState:
    metadata = path.lstat()
    mode = stat.S_IMODE(metadata.st_mode)
    if stat.S_ISREG(metadata.st_mode):
        return FileState(kind="file", mode=mode, sha256=_sha256(path.read_bytes()))
    if stat.S_ISLNK(metadata.st_mode):
        return FileState(
            kind="symlink",
            mode=mode,
            sha256=_sha256(os.readlink(path).encode("utf-8", errors="surrogateescape")),
        )
    raise WorkspaceError(f"unsupported workspace entry type: {path}")


def capture_workspace(
    root: Path,
    allowed_paths: Sequence[str],
    *,
    check_allowed_entries: bool = True,
) -> WorkspaceSnapshot:
    root = root.resolve(strict=True)
    allowed = validate_allowed_paths(
        root, allowed_paths, check_existing_entries=check_allowed_entries
    )
    directories: list[str] = []
    files: dict[str, FileState] = {}

    for current, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        directory_names.sort()
        file_names.sort()

        for directory_name in directory_names:
            path = current_path / directory_name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                files[relative] = _file_state(path)
            else:
                directories.append(relative)
        directory_names[:] = [
            name for name in directory_names if not (current_path / name).is_symlink()
        ]
        for file_name in file_names:
            path = current_path / file_name
            files[path.relative_to(root).as_posix()] = _file_state(path)

    index_state = _run_git(root, "ls-files", "--stage", "-z")
    return WorkspaceSnapshot(
        schema_version=SCHEMA_VERSION,
        root=str(root),
        allowed_paths=allowed,
        directories=sorted(directories),
        files=dict(sorted(files.items())),
        index_sha256=_sha256(index_state),
    )


def snapshot_to_payload(snapshot: WorkspaceSnapshot) -> dict[str, Any]:
    payload = asdict(snapshot)
    payload["files"] = {path: asdict(state) for path, state in sorted(snapshot.files.items())}
    return payload


def write_snapshot(snapshot: WorkspaceSnapshot, output: Path) -> None:
    output = output.resolve()
    root = Path(snapshot.root)
    if output == root or root in output.parents:
        raise WorkspaceError("snapshot file must be outside the Copilot workspace")
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        snapshot_to_payload(snapshot), indent=2, sort_keys=True, ensure_ascii=True
    )
    output.write_text(serialized + "\n", encoding="utf-8")


def read_snapshot(path: Path) -> WorkspaceSnapshot:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise WorkspaceError("unsupported snapshot schema version")
        files = {file_path: FileState(**state) for file_path, state in payload["files"].items()}
        return WorkspaceSnapshot(
            schema_version=payload["schema_version"],
            root=payload["root"],
            allowed_paths=payload["allowed_paths"],
            directories=payload["directories"],
            files=files,
            index_sha256=payload["index_sha256"],
        )
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise WorkspaceError(f"invalid snapshot file: {path}") from error


def verify_workspace(snapshot: WorkspaceSnapshot) -> list[dict[str, str]]:
    current = capture_workspace(
        Path(snapshot.root), snapshot.allowed_paths, check_allowed_entries=False
    )
    allowed = set(snapshot.allowed_paths)
    changes: list[dict[str, str]] = []

    if current.index_sha256 != snapshot.index_sha256:
        changes.append({"path": "<git-index>", "change": "modified"})

    old_directories = set(snapshot.directories)
    new_directories = set(current.directories)
    for path in sorted(old_directories - new_directories):
        changes.append({"path": path, "change": "directory-deleted"})
    for path in sorted(new_directories - old_directories):
        changes.append({"path": path, "change": "directory-added"})

    all_files = sorted(set(snapshot.files) | set(current.files))
    for path in all_files:
        before = snapshot.files.get(path)
        after = current.files.get(path)
        if before == after:
            continue
        if path in allowed:
            if after is not None and after.kind != "file":
                changes.append({"path": path, "change": "allowed-path-not-regular-file"})
            continue
        if before is None:
            change = "added"
        elif after is None:
            change = "deleted"
        elif before.kind != after.kind:
            change = "type-changed"
        elif before.mode != after.mode:
            change = "mode-changed"
        else:
            change = "modified"
        changes.append({"path": path, "change": change})
    return changes


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--root", type=Path, required=True)
    snapshot_parser.add_argument("--output", type=Path, required=True)
    snapshot_parser.add_argument("--allow", action="append", default=[])

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--snapshot", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "snapshot":
            snapshot = capture_workspace(args.root, args.allow)
            write_snapshot(snapshot, args.output)
            result = {
                "status": "snapshotted",
                "snapshot": str(args.output.resolve()),
                "allowed_paths": snapshot.allowed_paths,
            }
        else:
            snapshot = read_snapshot(args.snapshot)
            changes = verify_workspace(snapshot)
            result = {"status": "passed" if not changes else "failed", "changes": changes}
            print(json.dumps(result, sort_keys=True))
            return 0 if not changes else 1
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, WorkspaceError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Prepare and verify a minimal writable workspace for a Copilot CLI invocation."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import shutil
import stat
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence

SCHEMA_VERSION = 1


class WorkspaceError(ValueError):
    """Raised when an isolated workspace violates its containment contract."""


@dataclass(frozen=True)
class FileState:
    mode: int
    sha256: str


@dataclass(frozen=True)
class WorkspaceState:
    schema_version: int
    root: str
    directories: dict[str, int]
    files: dict[str, FileState]
    allowed_outputs: list[str]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_relative(raw_path: str, *, label: str) -> str:
    if not raw_path or "\\" in raw_path or any(character in raw_path for character in "*?["):
        raise WorkspaceError(f"invalid {label}: {raw_path!r}")
    candidate = PurePosixPath(raw_path)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise WorkspaceError(f"{label} must be a normalized relative path: {raw_path!r}")
    normalized = candidate.as_posix()
    if normalized == ".git" or normalized.startswith(".git/"):
        raise WorkspaceError(f"{label} cannot use Git metadata paths: {raw_path!r}")
    return normalized


def _reject_symlink_components(path: Path, *, label: str) -> None:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            raise WorkspaceError(f"{label} cannot contain symlink components: {current}")


def _reject_hard_link(path: Path, *, label: str) -> None:
    if path.exists() and path.lstat().st_nlink != 1:
        raise WorkspaceError(f"{label} cannot be hard-linked: {path}")


def _parse_copy_spec(raw_spec: str) -> tuple[Path, str]:
    source_text, separator, destination_text = raw_spec.partition("=")
    if not separator:
        raise WorkspaceError(f"copy specification must be SOURCE=DESTINATION: {raw_spec!r}")
    source_path = Path(source_text)
    _reject_symlink_components(source_path, label="workspace input")
    _reject_hard_link(source_path, label="workspace input")
    source = source_path.resolve(strict=True)
    if not source.is_file():
        raise WorkspaceError(f"workspace input must be a regular non-symlink file: {source}")
    destination = _normalize_relative(destination_text, label="workspace input path")
    return source, destination


def _file_state(path: Path) -> FileState:
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise WorkspaceError(f"workspace entry must be a regular file: {path}")
    if metadata.st_nlink != 1:
        raise WorkspaceError(f"workspace entry must not be hard-linked: {path}")
    return FileState(
        mode=stat.S_IMODE(metadata.st_mode),
        sha256=_sha256(path.read_bytes()),
    )


def _inventory(root: Path) -> tuple[dict[str, int], dict[str, FileState]]:
    directories = {".": stat.S_IMODE(root.stat().st_mode)}
    files: dict[str, FileState] = {}
    for current, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        directory_names.sort()
        file_names.sort()
        for directory_name in directory_names:
            path = current_path / directory_name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise WorkspaceError(f"workspace directory cannot be a symlink: {relative}")
            directories[relative] = stat.S_IMODE(path.stat().st_mode)
        for file_name in file_names:
            path = current_path / file_name
            relative = path.relative_to(root).as_posix()
            files[relative] = _file_state(path)
    return dict(sorted(directories.items())), dict(sorted(files.items()))


def _write_state(state: WorkspaceState, output: Path) -> None:
    _reject_symlink_components(output, label="state output")
    _reject_hard_link(output, label="state output")
    output = output.resolve()
    root = Path(state.root)
    if output == root or root in output.parents:
        raise WorkspaceError("state file must be outside the isolated workspace")
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(state)
    payload["files"] = {path: asdict(value) for path, value in state.files.items()}
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _read_state(path: Path, expected_sha256: str) -> WorkspaceState:
    _reject_symlink_components(path, label="state file")
    _reject_hard_link(path, label="state file")
    serialized = path.read_bytes()
    if not hmac.compare_digest(_sha256(serialized), expected_sha256.lower()):
        raise WorkspaceError("isolated workspace state integrity check failed")
    try:
        payload = json.loads(serialized)
        if payload["schema_version"] != SCHEMA_VERSION:
            raise WorkspaceError("unsupported isolated workspace state schema")
        return WorkspaceState(
            schema_version=payload["schema_version"],
            root=payload["root"],
            directories={name: int(mode) for name, mode in payload["directories"].items()},
            files={name: FileState(**value) for name, value in payload["files"].items()},
            allowed_outputs=payload["allowed_outputs"],
        )
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise WorkspaceError(f"invalid isolated workspace state {path}: {error}") from error


def prepare_workspace(
    root: Path,
    state_path: Path,
    copy_specs: Sequence[str],
    allowed_outputs: Sequence[str],
) -> WorkspaceState:
    _reject_symlink_components(root, label="workspace root")
    root = root.resolve()
    if root.exists():
        if root.is_symlink() or not root.is_dir():
            raise WorkspaceError(f"workspace root must be a directory: {root}")
        if any(root.iterdir()):
            raise WorkspaceError(f"workspace root must be empty: {root}")
    else:
        root.mkdir(parents=True)

    normalized_outputs = sorted(
        {_normalize_relative(path, label="allowed output") for path in allowed_outputs}
    )
    if len(normalized_outputs) != len(allowed_outputs) or not normalized_outputs:
        raise WorkspaceError("allowed outputs must be non-empty and unique")
    for output in normalized_outputs:
        if not output.startswith("output/"):
            raise WorkspaceError(f"allowed output must be under output/: {output}")

    destinations: set[str] = set()
    for raw_spec in copy_specs:
        source, destination = _parse_copy_spec(raw_spec)
        if destination == "output" or destination.startswith("output/"):
            raise WorkspaceError(f"workspace inputs cannot use output paths: {destination}")
        if destination in destinations or destination in normalized_outputs:
            raise WorkspaceError(f"duplicate workspace destination: {destination}")
        destinations.add(destination)
        target = root.joinpath(*PurePosixPath(destination).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target, follow_symlinks=False)
        target.chmod(0o444)

    for output in normalized_outputs:
        target = root.joinpath(*PurePosixPath(output).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            raise WorkspaceError(f"allowed output must be absent before invocation: {output}")

    for directory in sorted(
        (path for path in root.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        relative = directory.relative_to(root).as_posix()
        directory.chmod(0o755 if relative == "output" or relative.startswith("output/") else 0o555)
    root.chmod(0o555)

    directories, files = _inventory(root)
    state = WorkspaceState(
        schema_version=SCHEMA_VERSION,
        root=str(root),
        directories=directories,
        files=files,
        allowed_outputs=normalized_outputs,
    )
    _write_state(state, state_path)
    return state


def verify_workspace(state: WorkspaceState) -> list[dict[str, str]]:
    root_path = Path(state.root)
    try:
        _reject_symlink_components(root_path, label="workspace root")
    except WorkspaceError as error:
        return [{"path": "<workspace>", "change": str(error)}]
    root = root_path.resolve(strict=True)
    changes: list[dict[str, str]] = []
    try:
        directories, files = _inventory(root)
    except WorkspaceError as error:
        return [{"path": "<workspace>", "change": str(error)}]

    if directories != state.directories:
        for path in sorted(set(directories) - set(state.directories)):
            changes.append({"path": path, "change": "unexpected-directory"})
        for path in sorted(set(state.directories) - set(directories)):
            changes.append({"path": path, "change": "directory-deleted"})
        for path in sorted(set(directories) & set(state.directories)):
            if directories[path] != state.directories[path]:
                changes.append({"path": path, "change": "directory-mode-changed"})

    allowed = set(state.allowed_outputs)
    expected_files = set(state.files) | (allowed & set(files))
    for path in sorted(set(files) | expected_files):
        before = state.files.get(path)
        after = files.get(path)
        if path in allowed:
            continue
        if before is None:
            changes.append({"path": path, "change": "unexpected-file"})
        elif after is None:
            changes.append({"path": path, "change": "input-deleted"})
        elif before != after:
            changes.append({"path": path, "change": "input-modified"})
    return changes


def copy_verified_output(
    state: WorkspaceState,
    output: str,
    destination: Path,
    destination_root: Path,
) -> None:
    changes = verify_workspace(state)
    if changes:
        raise WorkspaceError(f"isolated workspace verification failed: {changes}")
    normalized = _normalize_relative(output, label="output")
    if normalized not in state.allowed_outputs:
        raise WorkspaceError(f"output is not allowed by workspace state: {normalized}")

    _reject_symlink_components(destination_root, label="destination root")
    _reject_symlink_components(destination, label="destination")
    _reject_hard_link(destination, label="destination")
    destination_root = destination_root.resolve(strict=True)
    destination = destination.resolve()
    try:
        destination.relative_to(destination_root)
    except ValueError as error:
        raise WorkspaceError(f"destination escapes approved root: {destination}") from error
    destination.parent.mkdir(parents=True, exist_ok=True)
    parent = destination.parent.resolve(strict=True)
    try:
        parent.relative_to(destination_root)
    except ValueError as error:
        raise WorkspaceError(f"destination parent escapes approved root: {parent}") from error

    source = Path(state.root).joinpath(*PurePosixPath(normalized).parts)
    shutil.copyfile(source, destination, follow_symlinks=False)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--root", type=Path, required=True)
    prepare.add_argument("--state", type=Path, required=True)
    prepare.add_argument("--copy", action="append", default=[])
    prepare.add_argument("--allow-output", action="append", default=[])

    verify = subparsers.add_parser("verify")
    verify.add_argument("--state", type=Path, required=True)
    verify.add_argument("--expected-sha256", required=True)

    copy = subparsers.add_parser("copy")
    copy.add_argument("--state", type=Path, required=True)
    copy.add_argument("--expected-sha256", required=True)
    copy.add_argument("--output", required=True)
    copy.add_argument("--destination", type=Path, required=True)
    copy.add_argument("--destination-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            state = prepare_workspace(args.root, args.state, args.copy, args.allow_output)
            result = {"status": "prepared", "allowed_outputs": state.allowed_outputs}
        else:
            state = _read_state(args.state, args.expected_sha256)
            if args.command == "verify":
                changes = verify_workspace(state)
                result = {"status": "passed" if not changes else "failed", "changes": changes}
                print(json.dumps(result, sort_keys=True))
                return 0 if not changes else 1
            copy_verified_output(state, args.output, args.destination, args.destination_root)
            result = {"status": "copied", "output": args.output}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, WorkspaceError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())

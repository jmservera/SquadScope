#!/usr/bin/env python3
"""Snapshot and verify repository filesystem changes around Copilot CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path


def _entry(path: Path) -> dict[str, str]:
    mode = path.lstat().st_mode
    if stat.S_ISLNK(mode):
        return {"type": "symlink", "target": os.readlink(path)}
    if stat.S_ISREG(mode):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return {"type": "file", "sha256": digest.hexdigest()}
    if stat.S_ISDIR(mode):
        return {"type": "directory"}
    return {"type": "special"}


def snapshot(root: Path) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(directory)
        for name in dirnames + filenames:
            path = current / name
            relative = path.relative_to(root).as_posix()
            entries[relative] = _entry(path)
    return entries


def git_worktree_snapshot(root: Path) -> dict[str, dict[str, str]]:
    result = subprocess.run(
        [
            "git",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "core.hooksPath=/dev/null",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        cwd=root,
        check=True,
        capture_output=True,
    )
    entries: dict[str, dict[str, str]] = {}
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative = raw_path.decode("utf-8", errors="surrogateescape")
        path = root / relative
        entries[relative] = _entry(path) if os.path.lexists(path) else {"type": "missing"}
    return entries


def _allowed_paths(root: Path, values: list[str]) -> set[str]:
    allowed: set[str] = set()
    resolved_root = root.resolve()
    for value in values:
        path = (root / value).absolute() if not Path(value).is_absolute() else Path(value)
        relative = path.relative_to(root).as_posix()
        parent = path.parent.resolve()
        if parent != resolved_root and resolved_root not in parent.parents:
            raise ValueError(f"Allowed path escapes repository: {value}")
        allowed.add(relative)
    return allowed


def verify(root: Path, baseline: dict[str, dict[str, str]], allowed: set[str]) -> list[str]:
    current = snapshot(root)
    changed = {
        path for path in baseline.keys() | current.keys() if baseline.get(path) != current.get(path)
    }
    violations = [path for path in sorted(changed) if path not in allowed]
    for path in sorted(changed & allowed):
        entry = current.get(path)
        if entry is None:
            violations.append(f"{path} (allowed output was deleted)")
        elif entry.get("type") != "file":
            violations.append(f"{path} (allowed output must be a regular file)")
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--root", type=Path, required=True)
    snapshot_parser.add_argument("--manifest", type=Path, required=True)
    git_snapshot_parser = subparsers.add_parser("git-snapshot")
    git_snapshot_parser.add_argument("--root", type=Path, required=True)
    git_snapshot_parser.add_argument("--manifest", type=Path, required=True)
    git_verify_parser = subparsers.add_parser("git-verify")
    git_verify_parser.add_argument("--root", type=Path, required=True)
    git_verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--root", type=Path, required=True)
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.add_argument("--allow", action="append", default=[])
    args = parser.parse_args()

    root = args.root.resolve()
    if args.command in {"snapshot", "git-snapshot"}:
        entries = snapshot(root) if args.command == "snapshot" else git_worktree_snapshot(root)
        args.manifest.write_text(
            json.dumps(entries, sort_keys=True),
            encoding="utf-8",
        )
        return 0

    baseline = json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.command == "git-verify":
        current = git_worktree_snapshot(root)
        violations = [
            path
            for path in sorted(baseline.keys() | current.keys())
            if baseline.get(path) != current.get(path)
        ]
        if violations:
            for violation in violations:
                print(f"::error::Copilot modified repository path: {violation}")
            return 1
        return 0

    violations = verify(root, baseline, _allowed_paths(root, args.allow))
    if violations:
        for violation in violations:
            print(f"::error::Copilot modified a non-allowed repository path: {violation}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

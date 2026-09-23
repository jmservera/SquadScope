#!/usr/bin/env python3
"""Run a Copilot agent inside the production read/write mount boundary."""

from __future__ import annotations

import argparse
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import Sequence


class SandboxError(ValueError):
    """Raised when the Copilot runtime cannot be safely mounted."""


# This path exists only inside Bubblewrap's private tmpfs, never on the host.
SANDBOX_TMP = "/tmp"  # nosec B108
SANDBOX_HOME = f"{SANDBOX_TMP}/copilot-home"


def _required_executable(name: str) -> Path:
    executable = shutil.which(name)
    if executable is None:
        raise SandboxError(f"required executable is unavailable: {name}")
    return Path(executable).resolve(strict=True)


def _reject_symlink_components(path: Path, *, label: str) -> None:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            raise SandboxError(f"{label} cannot contain symlink components: {current}")


def build_sandbox_command(
    *,
    workspace: Path,
    agent: str,
    prompt: str,
    share: str | None,
    sudo: Path,
    bwrap: Path,
    node: Path,
    copilot_entry: Path,
) -> list[str]:
    _reject_symlink_components(workspace, label="workspace")
    workspace = workspace.resolve(strict=True)
    output = workspace / "output"
    if not workspace.is_dir():
        raise SandboxError(f"workspace must be a regular directory: {workspace}")
    if output.is_symlink() or not output.is_dir():
        raise SandboxError(f"workspace output must be a regular directory: {output}")

    node = node.resolve(strict=True)
    copilot_entry = copilot_entry.resolve(strict=True)
    node_runtime_root = node.parent.parent
    try:
        copilot_relative = copilot_entry.relative_to(node_runtime_root)
    except ValueError as error:
        raise SandboxError(
            f"Copilot entry {copilot_entry} is outside Node runtime {node_runtime_root}"
        ) from error

    command = [
        str(sudo),
        "--preserve-env=GITHUB_TOKEN,COPILOT_GITHUB_TOKEN",
        str(bwrap),
        "--die-with-parent",
        "--new-session",
        "--unshare-pid",
        "--unshare-ipc",
        "--unshare-uts",
        "--ro-bind",
        "/usr",
        "/usr",
        "--symlink",
        "usr/bin",
        "/bin",
        "--symlink",
        "usr/lib",
        "/lib",
        "--symlink",
        "usr/lib64",
        "/lib64",
        "--dir",
        "/etc",
        "--ro-bind",
        "/etc/ssl",
        "/etc/ssl",
        "--ro-bind",
        "/etc/resolv.conf",
        "/etc/resolv.conf",
        "--ro-bind",
        "/etc/hosts",
        "/etc/hosts",
        "--ro-bind",
        "/etc/nsswitch.conf",
        "/etc/nsswitch.conf",
        "--ro-bind",
        "/etc/passwd",
        "/etc/passwd",
        "--ro-bind",
        "/etc/group",
        "/etc/group",
        "--ro-bind",
        "/etc/ld.so.cache",
        "/etc/ld.so.cache",
        "--ro-bind",
        str(node_runtime_root),
        "/runtime",
        "--ro-bind",
        str(workspace),
        "/workspace",
        "--dev",
        "/dev",
        "--tmpfs",
        SANDBOX_TMP,
        "--dir",
        SANDBOX_HOME,
        "--setenv",
        "HOME",
        SANDBOX_HOME,
        "--setenv",
        "PATH",
        "/runtime/bin:/usr/bin:/bin",
        "--setenv",
        "XDG_CONFIG_HOME",
        f"{SANDBOX_HOME}/.config",
        "--setenv",
        "XDG_CACHE_HOME",
        f"{SANDBOX_HOME}/.cache",
        "--bind",
        str(output),
        "/workspace/output",
        "--chdir",
        "/workspace",
        "/runtime/bin/node",
        f"/runtime/{copilot_relative.as_posix()}",
        "--agent",
        agent,
        "-p",
        prompt,
        "-s",
        "--no-ask-user",
        "--allow-tool=read",
        "--allow-tool=write",
    ]
    if share:
        command.append(f"--share={share}")
    return command


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--share")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        command = build_sandbox_command(
            workspace=args.workspace,
            agent=args.agent,
            prompt=args.prompt,
            share=args.share,
            sudo=_required_executable("sudo"),
            bwrap=_required_executable("bwrap"),
            node=_required_executable("node"),
            copilot_entry=_required_executable("copilot"),
        )
    except (OSError, SandboxError) as error:
        print(f"Copilot sandbox setup failed: {error}", file=sys.stderr)
        return 2
    return subprocess.run(command, check=False).returncode  # nosec B603


if __name__ == "__main__":
    raise SystemExit(main())

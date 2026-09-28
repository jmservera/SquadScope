#!/usr/bin/env python3
"""Run a Copilot agent inside the production read/write mount boundary."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from scripts.path_safety import find_symlink_component


class SandboxError(ValueError):
    """Raised when the Copilot runtime cannot be safely mounted."""


# This path exists only inside Bubblewrap's private tmpfs, never on the host.
SANDBOX_TMP = "/tmp"  # nosec B108
SANDBOX_HOME = f"{SANDBOX_TMP}/copilot-home"
SANDBOX_OUTPUT = "/workspace/output"


def _required_executable(name: str) -> Path:
    executable = shutil.which(name)
    if executable is None:
        raise SandboxError(f"required executable is unavailable: {name}")
    return Path(executable).resolve(strict=True)


def _reject_symlink_components(path: Path, *, label: str) -> None:
    symlink = find_symlink_component(path)
    if symlink is not None:
        raise SandboxError(f"{label} cannot contain symlink components: {symlink}")


def _runtime_root(node: Path) -> Path:
    root = node.parent.parent
    if root == Path(root.anchor):
        raise SandboxError("Node runtime root cannot be the filesystem root")
    return root


def build_sandbox_command(
    *,
    workspace: Path,
    agent: str,
    prompt: str,
    share: str | None,
    sudo: Path,
    bwrap: Path,
    setpriv: Path,
    node: Path,
    copilot_entry: Path,
    runner_uid: int,
    runner_gid: int,
    target_argv: Sequence[str] | None = None,
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
    node_runtime_root = _runtime_root(node)
    if not copilot_entry.is_file() or copilot_entry.suffix != ".js":
        raise SandboxError(f"Copilot entry must be a JavaScript file: {copilot_entry}")
    try:
        copilot_relative = copilot_entry.relative_to(node_runtime_root)
    except ValueError as error:
        raise SandboxError(
            f"Copilot entry {copilot_entry} is outside Node runtime {node_runtime_root}"
        ) from error

    if target_argv is None:
        target_argv = [
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

    command = [
        str(sudo),
        "--preserve-env=GITHUB_TOKEN,COPILOT_GITHUB_TOKEN",
        "--",
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
        "--perms",
        "01777",
        "--tmpfs",
        SANDBOX_TMP,
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
        SANDBOX_OUTPUT,
        "--chdir",
        "/workspace",
        str(setpriv),
        f"--reuid={runner_uid}",
        f"--regid={runner_gid}",
        "--clear-groups",
        "--no-new-privs",
        "--inh-caps=-all",
        "--bounding-set=-all",
        "--",
        *target_argv,
    ]
    if share:
        command.append(f"--share={share}")
    return command


def _sandbox_diagnostic_lines(stderr: str, *, limit: int = 8) -> list[str]:
    diagnostics: list[str] = []
    for raw_line in stderr.splitlines():
        line = raw_line.strip()
        if line.startswith(("bwrap:", "bubblewrap:", "setpriv:")):
            diagnostics.append(line)
            if len(diagnostics) >= limit:
                break
    return diagnostics


def _run_self_test() -> int:
    runner_uid = os.getuid()
    runner_gid = os.getgid()
    script = (
        "set -eu; "
        f'test "$(/usr/bin/id -u)" = "{runner_uid}"; '
        'mkdir -p "$HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"; '
        'test -w /tmp; test -w "$HOME"; '
        f'printf self-test > "{SANDBOX_OUTPUT}/sandbox-self-test"; '
        f'test "$(/usr/bin/stat -c %u "{SANDBOX_OUTPUT}/sandbox-self-test")" = "{runner_uid}"; '
        "/usr/bin/id -u"
    )
    with tempfile.TemporaryDirectory(prefix="copilot-sandbox-self-test-") as workspace_name:
        workspace = Path(workspace_name)
        (workspace / "output").mkdir()
        try:
            command = build_sandbox_command(
                workspace=workspace,
                agent="sandbox-self-test",
                prompt="sandbox self-test",
                share=None,
                sudo=_required_executable("sudo"),
                bwrap=_required_executable("bwrap"),
                setpriv=_required_executable("setpriv"),
                node=_required_executable("node"),
                copilot_entry=_required_executable("copilot"),
                runner_uid=runner_uid,
                runner_gid=runner_gid,
                target_argv=["/usr/bin/sh", "-c", script],
            )
        except (OSError, SandboxError) as error:
            print(f"Copilot sandbox self-test setup failed: {error}", file=sys.stderr)
            return 2
        result = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )  # nosec B603
        if result.returncode != 0:
            print(
                f"Copilot sandbox self-test failed (exit={result.returncode}).",
                file=sys.stderr,
            )
            for line in _sandbox_diagnostic_lines(result.stderr):
                print(f"Sandbox runtime diagnostic: {line}", file=sys.stderr)
            return result.returncode
        output = result.stdout.strip().splitlines()
        if output[-1:] != [str(runner_uid)]:
            print(
                "Copilot sandbox self-test failed: "
                f"expected uid {runner_uid}, got stdout {result.stdout!r}.",
                file=sys.stderr,
            )
            return 1
        output_file = workspace / "output" / "sandbox-self-test"
        try:
            stat = output_file.stat()
        except OSError as error:
            print(
                "Copilot sandbox self-test failed: "
                f"cannot stat output file {output_file}: {error}.",
                file=sys.stderr,
            )
            return 1
        if stat.st_uid != runner_uid or stat.st_gid != runner_gid:
            print(
                "Copilot sandbox self-test failed: output owner "
                f"{stat.st_uid}:{stat.st_gid} != {runner_uid}:{runner_gid}.",
                file=sys.stderr,
            )
            return 1
    print(f"Copilot sandbox self-test passed as uid {runner_uid}.")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--agent")
    parser.add_argument("--prompt")
    parser.add_argument("--share")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the production sandbox mechanics with id(1) and output ownership checks",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.self_test:
        return _run_self_test()
    if args.workspace is None or args.agent is None or args.prompt is None:
        print(
            "Copilot sandbox setup failed: --workspace, --agent, and --prompt are required",
            file=sys.stderr,
        )
        return 2
    try:
        command = build_sandbox_command(
            workspace=args.workspace,
            agent=args.agent,
            prompt=args.prompt,
            share=args.share,
            sudo=_required_executable("sudo"),
            bwrap=_required_executable("bwrap"),
            setpriv=_required_executable("setpriv"),
            node=_required_executable("node"),
            copilot_entry=_required_executable("copilot"),
            runner_uid=os.getuid(),
            runner_gid=os.getgid(),
        )
    except (OSError, SandboxError) as error:
        print(f"Copilot sandbox setup failed: {error}", file=sys.stderr)
        return 2
    return subprocess.run(command, check=False).returncode  # nosec B603


if __name__ == "__main__":
    raise SystemExit(main())

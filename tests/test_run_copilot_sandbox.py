"""Tests for the centralized production Copilot sandbox command."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import run_copilot_sandbox as sandbox


def _runtime(tmp_path: Path) -> tuple[Path, Path, Path]:
    runtime = tmp_path / "node"
    node = runtime / "bin" / "node"
    copilot = runtime / "lib" / "node_modules" / "@github" / "copilot" / "npm-loader.js"
    node.parent.mkdir(parents=True)
    copilot.parent.mkdir(parents=True)
    node.write_text("node\n", encoding="utf-8")
    copilot.write_text("copilot\n", encoding="utf-8")
    return runtime, node, copilot


def test_builds_minimal_read_only_runtime_with_exact_output_bind(tmp_path: Path) -> None:
    runtime, node, copilot = _runtime(tmp_path)
    workspace = tmp_path / "workspace"
    (workspace / "output").mkdir(parents=True)

    command = sandbox.build_sandbox_command(
        workspace=workspace,
        agent="weekly-analysis",
        prompt="Read input/prompt.md.",
        share="output/transcript.md",
        sudo=Path("/usr/bin/sudo"),
        bwrap=Path("/usr/bin/bwrap"),
        node=node,
        copilot_entry=copilot,
        runner_uid=1001,
        runner_gid=1001,
    )

    assert "--ro-bind" in command
    assert ["/usr", "/usr"] == command[command.index("--ro-bind") + 1 :][:2]
    assert "/" not in [
        source
        for index, source in enumerate(command)
        if index > 0 and command[index - 1] == "--ro-bind"
    ]
    assert "--proc" not in command
    assert "/proc" not in command
    assert command[command.index("--user") + 1] == "#1001"
    assert command[command.index("--group") + 1] == "#1001"
    assert "--unshare-user" in command
    assert command[command.index("--uid") + 1] == "0"
    assert command[command.index("--gid") + 1] == "0"
    assert str(runtime) in command
    assert str(workspace) in command
    bind_index = command.index("--bind")
    assert command[bind_index + 1 : bind_index + 3] == [
        str(workspace / "output"),
        "/workspace/output",
    ]
    assert "/runtime/bin/node" in command
    assert "/runtime/lib/node_modules/@github/copilot/npm-loader.js" in command
    assert "--share=output/transcript.md" in command


def test_rejects_copilot_entry_outside_node_runtime(tmp_path: Path) -> None:
    _, node, _ = _runtime(tmp_path)
    copilot = tmp_path / "other" / "copilot.js"
    copilot.parent.mkdir()
    copilot.write_text("copilot\n", encoding="utf-8")
    workspace = tmp_path / "workspace"
    (workspace / "output").mkdir(parents=True)

    with pytest.raises(sandbox.SandboxError, match="outside Node runtime"):
        sandbox.build_sandbox_command(
            workspace=workspace,
            agent="weekly-analysis",
            prompt="prompt",
            share=None,
            sudo=Path("/usr/bin/sudo"),
            bwrap=Path("/usr/bin/bwrap"),
            node=node,
            copilot_entry=copilot,
            runner_uid=1001,
            runner_gid=1001,
        )


def test_rejects_node_runtime_root_of_slash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    node = Path("/bin/node")
    copilot = Path("/lib/node_modules/@github/copilot/npm-loader.js")
    workspace = tmp_path / "workspace"
    (workspace / "output").mkdir(parents=True)

    original_resolve = Path.resolve

    def fake_resolve(self: Path, strict: bool = False) -> Path:
        if self in (node, copilot):
            return self
        return original_resolve(self, strict=strict)

    monkeypatch.setattr(Path, "resolve", fake_resolve)

    with pytest.raises(sandbox.SandboxError, match="filesystem root"):
        sandbox.build_sandbox_command(
            workspace=workspace,
            agent="weekly-analysis",
            prompt="prompt",
            share=None,
            sudo=Path("/usr/bin/sudo"),
            bwrap=Path("/usr/bin/bwrap"),
            node=node,
            copilot_entry=copilot,
            runner_uid=1001,
            runner_gid=1001,
        )


def test_rejects_workspace_with_symlink_component(tmp_path: Path) -> None:
    _, node, copilot = _runtime(tmp_path)
    real_parent = tmp_path / "real-parent"
    workspace = real_parent / "workspace"
    (workspace / "output").mkdir(parents=True)
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)

    with pytest.raises(sandbox.SandboxError, match="symlink components"):
        sandbox.build_sandbox_command(
            workspace=linked_parent / "workspace",
            agent="weekly-analysis",
            prompt="prompt",
            share=None,
            sudo=Path("/usr/bin/sudo"),
            bwrap=Path("/usr/bin/bwrap"),
            node=node,
            copilot_entry=copilot,
            runner_uid=1001,
            runner_gid=1001,
        )


def test_rejects_filesystem_root_as_node_runtime(tmp_path: Path) -> None:
    with pytest.raises(sandbox.SandboxError, match="filesystem root"):
        sandbox._runtime_root(Path("/node"))


def test_rejects_non_javascript_copilot_entry(tmp_path: Path) -> None:
    _, node, _ = _runtime(tmp_path)
    copilot = node.parent / "copilot"
    copilot.write_text("#!/bin/sh\n", encoding="utf-8")
    workspace = tmp_path / "workspace"
    (workspace / "output").mkdir(parents=True)

    with pytest.raises(sandbox.SandboxError, match="JavaScript file"):
        sandbox.build_sandbox_command(
            workspace=workspace,
            agent="weekly-analysis",
            prompt="prompt",
            share=None,
            sudo=Path("/usr/bin/sudo"),
            bwrap=Path("/usr/bin/bwrap"),
            node=node,
            copilot_entry=copilot,
            runner_uid=1001,
            runner_gid=1001,
        )

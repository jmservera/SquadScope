"""Tests for the centralized production Copilot sandbox command."""

from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

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
        setpriv=Path("/usr/bin/setpriv"),
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
    assert command[command.index("--preserve-env=GITHUB_TOKEN,COPILOT_GITHUB_TOKEN") + 1] == "--"
    assert "--unshare-user" not in command
    assert "--uid" not in command
    assert "--gid" not in command
    assert str(runtime) in command
    assert str(workspace) in command
    bind_index = command.index("--bind")
    assert command[bind_index + 1 : bind_index + 3] == [
        str(workspace / "output"),
        "/workspace/output",
    ]
    setpriv_index = command.index("/usr/bin/setpriv")
    assert command[setpriv_index : setpriv_index + 8] == [
        "/usr/bin/setpriv",
        "--reuid=1001",
        "--regid=1001",
        "--clear-groups",
        "--no-new-privs",
        "--inh-caps=-all",
        "--bounding-set=-all",
        "--",
    ]
    assert command[setpriv_index + 8 : setpriv_index + 10] == [
        "/runtime/bin/node",
        "/runtime/lib/node_modules/@github/copilot/npm-loader.js",
    ]
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
            setpriv=Path("/usr/bin/setpriv"),
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
            setpriv=Path("/usr/bin/setpriv"),
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
            setpriv=Path("/usr/bin/setpriv"),
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
            setpriv=Path("/usr/bin/setpriv"),
            node=node,
            copilot_entry=copilot,
            runner_uid=1001,
            runner_gid=1001,
        )


def _stub_self_test_setup(
    monkeypatch: pytest.MonkeyPatch, *, runner_uid: int = 1001, runner_gid: int = 1001
) -> None:
    monkeypatch.setattr(sandbox.os, "getuid", lambda: runner_uid)
    monkeypatch.setattr(sandbox.os, "getgid", lambda: runner_gid)
    monkeypatch.setattr(sandbox, "_required_executable", lambda name: Path(f"/usr/bin/{name}"))


def test_self_test_reports_setup_errors(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_self_test_setup(monkeypatch)
    monkeypatch.setattr(
        sandbox,
        "build_sandbox_command",
        lambda **_kwargs: (_ for _ in ()).throw(sandbox.SandboxError("missing bwrap")),
    )

    assert sandbox._run_self_test() == 2

    captured = capsys.readouterr()
    assert "Copilot sandbox self-test setup failed: missing bwrap" in captured.err


def test_self_test_reports_nonzero_sandbox_exit(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_self_test_setup(monkeypatch)
    monkeypatch.setattr(
        sandbox,
        "build_sandbox_command",
        lambda **kwargs: ["sandbox-command", str(kwargs["workspace"])],
    )

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command[0] == "sandbox-command"
        assert kwargs == {
            "check": False,
            "text": True,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }
        return subprocess.CompletedProcess(
            command, 23, stdout="", stderr="bwrap: operation not permitted\nignored\n"
        )

    monkeypatch.setattr(sandbox.subprocess, "run", fake_run)

    assert sandbox._run_self_test() == 23

    captured = capsys.readouterr()
    assert "Copilot sandbox self-test failed (exit=23)." in captured.err
    assert "Sandbox runtime diagnostic: bwrap: operation not permitted" in captured.err


def test_self_test_rejects_unexpected_uid_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_self_test_setup(monkeypatch, runner_uid=1001)
    monkeypatch.setattr(
        sandbox,
        "build_sandbox_command",
        lambda **kwargs: ["sandbox-command", str(kwargs["workspace"])],
    )
    monkeypatch.setattr(
        sandbox.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(
            command, 0, stdout="1002\n", stderr=""
        ),
    )

    assert sandbox._run_self_test() == 1

    captured = capsys.readouterr()
    assert "expected uid 1001, got stdout '1002\\n'" in captured.err


def test_self_test_rejects_output_owner_mismatch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_self_test_setup(monkeypatch, runner_uid=1001, runner_gid=1001)
    original_stat = Path.stat

    def build_command(**kwargs: object) -> list[str]:
        return ["sandbox-command", str(kwargs["workspace"])]

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        workspace = Path(command[-1])
        (workspace / "output" / "sandbox-self-test").write_text("self-test", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="1001\n", stderr="")

    def fake_stat(self: Path, *args: object, **kwargs: object) -> object:
        if self.name == "sandbox-self-test":
            return SimpleNamespace(st_uid=1001, st_gid=2002)
        return original_stat(self, *args, **kwargs)

    monkeypatch.setattr(sandbox, "build_sandbox_command", build_command)
    monkeypatch.setattr(sandbox.subprocess, "run", fake_run)
    monkeypatch.setattr(Path, "stat", fake_stat)

    assert sandbox._run_self_test() == 1

    captured = capsys.readouterr()
    assert "output owner 1001:2002 != 1001:1001" in captured.err


def test_self_test_reports_missing_output_file(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_self_test_setup(monkeypatch, runner_uid=1001)
    monkeypatch.setattr(
        sandbox,
        "build_sandbox_command",
        lambda **kwargs: ["sandbox-command", str(kwargs["workspace"])],
    )
    monkeypatch.setattr(
        sandbox.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(
            command, 0, stdout="1001\n", stderr=""
        ),
    )

    assert sandbox._run_self_test() == 1

    captured = capsys.readouterr()
    assert "cannot stat output file" in captured.err


def test_self_test_reports_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    runner_uid = sandbox.os.getuid()
    runner_gid = sandbox.os.getgid()
    _stub_self_test_setup(monkeypatch, runner_uid=runner_uid, runner_gid=runner_gid)

    def build_command(**kwargs: object) -> list[str]:
        return ["sandbox-command", str(kwargs["workspace"])]

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        workspace = Path(command[-1])
        (workspace / "output" / "sandbox-self-test").write_text("self-test", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout=f"{runner_uid}\n", stderr="")

    monkeypatch.setattr(sandbox, "build_sandbox_command", build_command)
    monkeypatch.setattr(sandbox.subprocess, "run", fake_run)

    assert sandbox._run_self_test() == 0

    captured = capsys.readouterr()
    assert captured.out == f"Copilot sandbox self-test passed as uid {runner_uid}.\n"

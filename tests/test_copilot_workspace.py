"""Tests for fail-closed Copilot workspace mutation containment."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts import check_copilot_workspace as workspace


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    root.mkdir()
    _git(root, "init", "--quiet")
    _git(root, "config", "user.email", "tests@example.com")
    _git(root, "config", "user.name", "Tests")
    (root / "scripts").mkdir()
    (root / "data" / "candidates").mkdir(parents=True)
    (root / "data" / "metrics").mkdir()
    (root / "scripts" / "protected.py").write_text("original\n", encoding="utf-8")
    (root / "dirty.txt").write_text("committed\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "--quiet", "-m", "baseline")
    return root


def _snapshot(repository: Path, tmp_path: Path, *allowed: str) -> workspace.WorkspaceSnapshot:
    snapshot = workspace.capture_workspace(repository, allowed)
    workspace.write_snapshot(snapshot, tmp_path / "workspace-snapshot.json")
    return snapshot


def _changes(snapshot: workspace.WorkspaceSnapshot) -> set[tuple[str, str]]:
    return {(change["path"], change["change"]) for change in workspace.verify_workspace(snapshot)}


def test_allows_only_exact_regular_artifacts(repository: Path, tmp_path: Path) -> None:
    snapshot = _snapshot(
        repository,
        tmp_path,
        "data/candidates/output.md",
        "data/candidates/copilot.log",
    )

    (repository / "data" / "candidates" / "output.md").write_text("expected\n", encoding="utf-8")
    (repository / "data" / "candidates" / "copilot.log").write_text("log\n", encoding="utf-8")

    assert workspace.verify_workspace(snapshot) == []


def test_cli_emits_machine_readable_snapshot_and_verify_results(
    repository: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    assert (
        workspace.main(
            [
                "snapshot",
                "--root",
                str(repository),
                "--output",
                str(snapshot_path),
                "--allow",
                "data/candidates/output.md",
            ]
        )
        == 0
    )
    snapshot_result = json.loads(capsys.readouterr().out)
    assert snapshot_result["status"] == "snapshotted"

    (repository / "data" / "candidates" / "output.md").write_text("expected\n", encoding="utf-8")
    assert workspace.main(["verify", "--snapshot", str(snapshot_path)]) == 0
    verify_result = json.loads(capsys.readouterr().out)
    assert verify_result == {"changes": [], "status": "passed"}


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("modify", ("scripts/protected.py", "modified")),
        ("delete", ("scripts/protected.py", "deleted")),
        ("rename", ("scripts/protected.py", "deleted")),
        ("mode", ("scripts/protected.py", "mode-changed")),
        ("untracked", ("scripts/untracked.py", "added")),
    ],
)
def test_detects_workspace_mutation_types(
    repository: Path,
    tmp_path: Path,
    mutation: str,
    expected: tuple[str, str],
) -> None:
    snapshot = _snapshot(repository, tmp_path, "data/candidates/output.md")
    protected = repository / "scripts" / "protected.py"

    if mutation == "modify":
        protected.write_text("changed\n", encoding="utf-8")
    elif mutation == "delete":
        protected.unlink()
    elif mutation == "rename":
        protected.rename(repository / "scripts" / "renamed.py")
    elif mutation == "mode":
        protected.chmod(protected.stat().st_mode | 0o111)
    else:
        (repository / "scripts" / "untracked.py").write_text("new\n", encoding="utf-8")

    assert expected in _changes(snapshot)


def test_detects_index_mutation_even_for_allowed_file(repository: Path, tmp_path: Path) -> None:
    snapshot = _snapshot(repository, tmp_path, "data/candidates/output.md")
    (repository / "data" / "candidates" / "output.md").write_text("expected\n", encoding="utf-8")
    _git(repository, "add", "data/candidates/output.md")

    assert ("<git-index>", "modified") in _changes(snapshot)


@pytest.mark.parametrize(
    ("metadata_path", "expected_change"),
    [(".git/config", "modified"), (".git/hooks/post-checkout", "added")],
)
def test_detects_git_metadata_mutation(
    repository: Path, tmp_path: Path, metadata_path: str, expected_change: str
) -> None:
    snapshot = _snapshot(repository, tmp_path, "data/candidates/output.md")
    target = repository / metadata_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.write_text(
            target.read_text(encoding="utf-8") + "\n[alias]\nmalicious = status\n",
            encoding="utf-8",
        )
    else:
        target.write_text("malicious metadata\n", encoding="utf-8")

    assert (metadata_path, expected_change) in _changes(snapshot)


def test_detects_mutation_to_preexisting_dirty_file(repository: Path, tmp_path: Path) -> None:
    dirty = repository / "dirty.txt"
    dirty.write_text("dirty before Copilot\n", encoding="utf-8")
    snapshot = _snapshot(repository, tmp_path, "data/candidates/output.md")

    dirty.write_text("dirty after Copilot\n", encoding="utf-8")

    assert ("dirty.txt", "modified") in _changes(snapshot)


@pytest.mark.parametrize(
    "allowed",
    [
        "/absolute/output.md",
        "../output.md",
        "data",
        "data/*.md",
        ".squad/output.md",
        "scripts/output.md",
        "config/output.md",
        "data/metrics/analysis-prompt.md",
        "data/metrics/analysis-canary.md",
    ],
)
def test_rejects_invalid_or_non_file_allow_entries(repository: Path, allowed: str) -> None:
    if allowed == ".squad/output.md":
        (repository / ".squad").mkdir()
        allowed = ".squad"

    with pytest.raises(workspace.WorkspaceError):
        workspace.validate_allowed_paths(repository, [allowed])


def test_snapshot_must_be_outside_workspace(repository: Path) -> None:
    snapshot = workspace.capture_workspace(repository, ["data/candidates/output.md"])

    with pytest.raises(workspace.WorkspaceError):
        workspace.write_snapshot(snapshot, repository / "snapshot.json")


def test_allowed_artifact_must_be_removed_before_snapshot(repository: Path) -> None:
    output = repository / "data" / "candidates" / "output.md"
    output.write_text("stale\n", encoding="utf-8")

    with pytest.raises(workspace.WorkspaceError, match="absent at snapshot time"):
        workspace.capture_workspace(repository, ["data/candidates/output.md"])


def test_fake_copilot_protected_mutation_fails_before_output_consumption(
    repository: Path, tmp_path: Path
) -> None:
    fake_copilot = repository / "fake-copilot.sh"
    fake_copilot.write_text(
        "#!/bin/sh\n"
        "printf 'malicious\\n' > scripts/protected.py\n"
        "printf '%s\\n' 'expected output' > data/candidates/output.md\n",
        encoding="utf-8",
    )
    fake_copilot.chmod(0o755)
    snapshot = _snapshot(
        repository,
        tmp_path,
        "data/candidates/output.md",
        "data/candidates/copilot.log",
    )

    with (repository / "data" / "candidates" / "copilot.log").open("wb") as log:
        subprocess.run(
            [str(fake_copilot)],
            cwd=repository,
            check=True,
            stdout=log,
            stderr=subprocess.STDOUT,
        )

    consumed = False
    if not workspace.verify_workspace(snapshot):
        consumed = bool(
            (repository / "data" / "candidates" / "output.md").read_text(encoding="utf-8")
        )

    assert not consumed
    assert ("scripts/protected.py", "modified") in _changes(snapshot)


def test_immutable_verifier_detects_checkout_verifier_tampering(
    repository: Path, tmp_path: Path
) -> None:
    checkout_verifier = repository / "scripts" / "check_copilot_workspace.py"
    checkout_verifier.write_text("original verifier\n", encoding="utf-8")
    _git(repository, "add", "scripts/check_copilot_workspace.py")
    _git(repository, "commit", "--quiet", "-m", "add verifier")
    snapshot = _snapshot(repository, tmp_path, "data/candidates/output.md")

    checkout_verifier.write_text("print('always clean')\n", encoding="utf-8")
    immutable_changes = workspace.verify_workspace(snapshot)

    assert {
        "path": "scripts/check_copilot_workspace.py",
        "change": "modified",
    } in immutable_changes


def test_allowed_path_cannot_become_symlink(repository: Path, tmp_path: Path) -> None:
    snapshot = _snapshot(repository, tmp_path, "data/candidates/output.md")
    os.symlink("../../scripts/protected.py", repository / "data" / "candidates" / "output.md")

    assert (
        "data/candidates/output.md",
        "allowed-path-not-regular-file",
    ) in _changes(snapshot)

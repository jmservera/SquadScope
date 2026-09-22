import subprocess
from pathlib import Path

from scripts.copilot_workspace_guard import git_worktree_snapshot, snapshot, verify


def test_verify_allows_only_declared_regular_output(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("git metadata", encoding="utf-8")
    (tmp_path / "input.txt").write_text("safe", encoding="utf-8")
    baseline = snapshot(tmp_path)

    (tmp_path / "output.md").write_text("generated", encoding="utf-8")

    assert verify(tmp_path, baseline, {"output.md"}) == []


def test_verify_rejects_git_metadata_mutation(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    config = tmp_path / ".git" / "config"
    config.write_text("safe", encoding="utf-8")
    baseline = snapshot(tmp_path)

    config.write_text("core.sshCommand = attacker", encoding="utf-8")

    assert verify(tmp_path, baseline, {"output.md"}) == [".git/config"]


def test_verify_rejects_modified_and_untracked_paths(tmp_path: Path):
    (tmp_path / "script.py").write_text("safe", encoding="utf-8")
    baseline = snapshot(tmp_path)

    (tmp_path / "script.py").write_text("compromised", encoding="utf-8")
    (tmp_path / "sitecustomize.py").write_text("compromised", encoding="utf-8")

    assert verify(tmp_path, baseline, {"output.md"}) == [
        "script.py",
        "sitecustomize.py",
    ]


def test_verify_rejects_allowed_symlink(tmp_path: Path):
    baseline = snapshot(tmp_path)
    (tmp_path / "target.txt").write_text("outside output", encoding="utf-8")
    (tmp_path / "output.md").symlink_to("target.txt")

    assert verify(tmp_path, baseline, {"output.md", "target.txt"}) == [
        "output.md (allowed output must be a regular file)"
    ]


def test_verify_rejects_deletion_and_rename(tmp_path: Path):
    original = tmp_path / "input.txt"
    original.write_text("safe", encoding="utf-8")
    baseline = snapshot(tmp_path)

    original.rename(tmp_path / "renamed.txt")

    assert verify(tmp_path, baseline, {"output.md"}) == [
        "input.txt",
        "renamed.txt",
    ]


def test_git_worktree_snapshot_detects_changes_to_already_dirty_paths(tmp_path: Path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    tracked = tmp_path / "tracked.txt"
    untracked = tmp_path / "untracked.txt"
    tracked.write_text("baseline", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=tmp_path, check=True)
    tracked.write_text("already dirty", encoding="utf-8")
    untracked.write_text("already untracked", encoding="utf-8")
    baseline = git_worktree_snapshot(tmp_path)

    tracked.write_text("changed again", encoding="utf-8")
    untracked.write_text("changed again", encoding="utf-8")
    current = git_worktree_snapshot(tmp_path)

    assert baseline["tracked.txt"] != current["tracked.txt"]
    assert baseline["untracked.txt"] != current["untracked.txt"]

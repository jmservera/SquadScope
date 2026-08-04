from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts.atomic_publish_proof import (
    GENERATED_PATHS,
    extract_commit_step,
    generated_tree_manifest,
    run_commit_step,
    run_git,
)

ROOT = Path(__file__).resolve().parent.parent


def test_extract_commit_step_guards_production_contract() -> None:
    script = extract_commit_step(ROOT / ".github/workflows/crawl-and-publish.yml")

    assert 'CURRENT_PUBLISH_SHA=$(git rev-parse "origin/$DATA_BRANCH")' in script
    assert "git diff --cached --quiet && exit 0" in script
    assert script.count("git commit ") == 1
    assert "git push --force-with-lease=" in script


def test_extract_commit_step_fails_closed_when_lease_is_missing(tmp_path: Path) -> None:
    workflow = {
        "jobs": {
            "generate": {
                "steps": [
                    {"name": "Commit generated content to data branch", "run": "git commit test"}
                ]
            }
        }
    }
    path = tmp_path / "workflow.yml"
    path.write_text(yaml.safe_dump(workflow), encoding="utf-8")

    with pytest.raises(ValueError, match="contract changed"):
        extract_commit_step(path)


def test_generated_tree_manifest_tracks_modes_deletions_and_order(tmp_path: Path) -> None:
    run_git(tmp_path, "init")
    run_git(tmp_path, "config", "user.name", "Proof Test")
    run_git(tmp_path, "config", "user.email", "proof@example.invalid")
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "b.txt").write_text("before\n", encoding="utf-8")
    executable = generated / "a.sh"
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    executable.chmod(0o755)
    run_git(tmp_path, "add", "generated")
    run_git(tmp_path, "commit", "-m", "seed")
    committed = generated_tree_manifest(tmp_path, "HEAD", ["generated/"])

    (generated / "b.txt").unlink()
    (generated / "c.txt").write_text("after\n", encoding="utf-8")
    working = generated_tree_manifest(tmp_path, None, ["generated/"])

    assert [entry["path"] for entry in committed["entries"]] == [
        "generated/a.sh",
        "generated/b.txt",
    ]
    assert committed["entries"][0]["mode"] == "100755"
    assert [entry["path"] for entry in working["entries"]] == [
        "generated/a.sh",
        "generated/c.txt",
    ]
    assert committed["digest"] != working["digest"]


def test_commit_step_rejects_non_local_origin(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init")
    run_git(repo, "remote", "add", "origin", "https://github.com/example/repo")

    with pytest.raises(ValueError, match="temporary root"):
        run_commit_step(
            repo,
            "exit 0",
            {"ATOMIC_PROOF_ROOT": str(tmp_path)},
        )


def test_atomic_publish_proof_integration(tmp_path: Path) -> None:
    output_dir = tmp_path / "evidence"
    result = subprocess.run(
        [
            "python3",
            "-m",
            "scripts.atomic_publish_proof",
            "--repo-root",
            str(ROOT),
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout

    evidence = json.loads((output_dir / "atomic-publish-proof.json").read_text("utf-8"))
    scenarios = evidence["scenarios"]
    assert evidence["schema_version"] == "atomic_publish_proof_v1"
    assert scenarios["normal"]["before_sha"] != scenarios["normal"]["after_sha"]
    assert scenarios["normal"]["commit_count"] == 1
    assert scenarios["identical_rerun"]["before_sha"] == scenarios["identical_rerun"]["after_sha"]
    assert scenarios["injected_failure"]["exit_code"] != 0
    assert scenarios["injected_failure"]["before_sha"] == scenarios["injected_failure"]["after_sha"]
    assert (
        scenarios["generated_tree"]["candidate_digest"]
        == scenarios["generated_tree"]["accepted_digest"]
    )
    assert scenarios["hydration"]["accepted_digest"] == scenarios["hydration"]["hydrated_digest"]
    assert scenarios["hydration"]["reference_problems"] == []
    assert all(
        path.startswith(tuple(item.rstrip("/") for item in GENERATED_PATHS) + ("data/backups/",))
        for path in scenarios["normal"]["changed_paths"]
    )
    serialized = json.dumps(evidence)
    assert "github.com" not in serialized
    assert (output_dir / "candidate-tree.json").is_file()
    assert (output_dir / "accepted-tree.json").is_file()
    assert (output_dir / "hydrated-tree.json").is_file()

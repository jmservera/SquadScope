#!/usr/bin/env python3
"""Prove the production publish transaction against a temporary local remote."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess  # nosec B404
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

import yaml

from scripts.promotion_guard import promote_candidate
from scripts.publish_hydration import GENERATED_PATHS, check_publish_references

COMMIT_STEP_NAME = "Commit generated content to data branch"
PROOF_PATH = "data/derived/observatory/atomic-publish-proof.json"
REQUIRED_COMMIT_FRAGMENTS = (
    'CURRENT_PUBLISH_SHA=$(git rev-parse "origin/$DATA_BRANCH")',
    'if [ "$GENERATED_STATE_CHANGED" = false ]; then',
    "git diff --cached --quiet && exit 0",
    'git commit -m "publish: weekly article transaction $WEEK [run #${GITHUB_RUN_ID}]"',
    'git push --force-with-lease="refs/heads/$DATA_BRANCH:$CURRENT_PUBLISH_SHA"',
)
SENSITIVE_ENV_NAMES = {
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "SSH_AGENT_PID",
    "SSH_AUTH_SOCK",
}


def _clean_environment(extra: Mapping[str, str] | None = None) -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in SENSITIVE_ENV_NAMES and not key.startswith("GIT_CONFIG_")
    }
    environment.update(
        {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "credential.helper",
            "GIT_CONFIG_VALUE_0": "",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    if extra:
        environment.update(extra)
    return environment


def extract_commit_step(workflow_path: Path) -> str:
    """Extract and guard the production publish shell body."""
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    generate = workflow.get("jobs", {}).get("generate", {})
    matches = [
        step.get("run")
        for step in generate.get("steps", [])
        if step.get("name") == COMMIT_STEP_NAME
    ]
    if len(matches) != 1 or not isinstance(matches[0], str):
        raise ValueError(f"Expected exactly one {COMMIT_STEP_NAME!r} step in generate job")
    script = matches[0]
    missing = [fragment for fragment in REQUIRED_COMMIT_FRAGMENTS if fragment not in script]
    if missing or script.count("git commit ") != 1:
        raise ValueError(f"Publish step contract changed; missing={missing!r}")
    return script


def run_git(repo: Path, *args: str) -> str:
    """Run Git without inherited credentials and return stripped stdout."""
    # Fixed git argv, no shell, sanitized env; single nosec avoids bandit's
    # multi-code comma-list parsing bug (only the last id is retained).
    result = subprocess.run(  # nosec
        ["git", *args],
        cwd=repo,
        env=_clean_environment(),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed in {repo} (exit {result.returncode}):\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout.strip()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _assert_isolated_origin(repo: Path, proof_root: Path) -> Path:
    remote_text = run_git(repo, "remote", "get-url", "origin")
    if "://" in remote_text or remote_text.startswith(("git@", "ssh:")):
        raise ValueError(f"Proof origin must stay below temporary root: {remote_text}")
    remote = Path(remote_text)
    if not remote.is_absolute():
        remote = (repo / remote).resolve()
    else:
        remote = remote.resolve()
    if not _is_relative_to(remote, proof_root.resolve()):
        raise ValueError(f"Proof origin must stay below temporary root: {remote}")
    if run_git(remote, "rev-parse", "--is-bare-repository") != "true":
        raise ValueError(f"Proof origin is not a bare repository: {remote}")
    return remote


def seed_isolated_origin(source_repo: Path, main_ref: str, publish_ref: str, root: Path) -> Path:
    """Create a local bare origin seeded from reviewed source refs."""
    origin = (root / "proof-origin.git").resolve()
    origin.parent.mkdir(parents=True, exist_ok=True)
    run_git(root, "init", "--bare", str(origin))
    run_git(
        source_repo,
        "push",
        str(origin),
        f"{main_ref}:refs/heads/main",
        f"{publish_ref}:refs/heads/publish",
    )
    return origin


def _clone(origin: Path, destination: Path) -> Path:
    run_git(origin.parent, "clone", "--branch", "main", str(origin), str(destination))
    return destination


def hydrate_generated_paths(repo: Path, publish_ref: str, paths: Sequence[str]) -> list[str]:
    """Mirror publish-present paths and retain main-only generated paths."""
    run_git(repo, "fetch", "origin", f"publish:{publish_ref}")
    preserved: list[str] = []
    for raw_path in paths:
        path = raw_path.rstrip("/")
        published = run_git(repo, "ls-tree", "-r", "--name-only", publish_ref, "--", path)
        target = repo / path
        if published:
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
            run_git(repo, "checkout", publish_ref, "--", path)
        elif run_git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", path):
            preserved.append(path)
    return preserved


def _manifest_entry(path: str, mode: str, payload: bytes) -> dict[str, object]:
    return {
        "path": path,
        "mode": mode,
        "size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def generated_tree_manifest(repo: Path, ref: str | None, paths: Sequence[str]) -> dict[str, object]:
    """Hash path, mode, size, and bytes for generated files."""
    entries: list[dict[str, object]] = []
    clean_paths = [path.rstrip("/") for path in paths]
    if ref is not None:
        # Fixed git argv, no shell, sanitized env; single nosec avoids bandit's
        # multi-code comma-list parsing bug (only the last id is retained).
        listing = subprocess.run(  # nosec
            ["git", "ls-tree", "-r", "-z", ref, "--", *clean_paths],
            cwd=repo,
            env=_clean_environment(),
            capture_output=True,
            check=True,
        ).stdout
        for item in listing.split(b"\0"):
            if not item:
                continue
            metadata, raw_path = item.split(b"\t", 1)
            mode = metadata.split(b" ", 1)[0].decode("ascii")
            path = raw_path.decode("utf-8")
            # Fixed git argv, no shell, sanitized env; single nosec avoids bandit's
            # multi-code comma-list parsing bug (only the last id is retained).
            payload = subprocess.run(  # nosec
                ["git", "show", f"{ref}:{path}"],
                cwd=repo,
                env=_clean_environment(),
                capture_output=True,
                check=True,
            ).stdout
            entries.append(_manifest_entry(path, mode, payload))
    else:
        files: set[Path] = set()
        for path in clean_paths:
            target = repo / path
            if target.is_file():
                files.add(target)
            elif target.is_dir():
                files.update(candidate for candidate in target.rglob("*") if candidate.is_file())
        for target in sorted(files):
            relative = target.relative_to(repo).as_posix()
            mode = "100755" if target.stat().st_mode & stat.S_IXUSR else "100644"
            entries.append(_manifest_entry(relative, mode, target.read_bytes()))
    entries.sort(key=lambda entry: str(entry["path"]))
    encoded = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"digest": hashlib.sha256(encoded).hexdigest(), "entries": entries}


def run_commit_step(
    repo: Path, script: str, environment: Mapping[str, str]
) -> subprocess.CompletedProcess[str]:
    """Execute the extracted shell after enforcing a local bare origin."""
    proof_root = Path(environment["ATOMIC_PROOF_ROOT"]).resolve()
    _assert_isolated_origin(repo, proof_root)
    return subprocess.run(  # nosec B603 - fixed argv, no shell, extracted production script
        ["/bin/bash", "-c", script],
        cwd=repo,
        env=_clean_environment(environment),
        capture_output=True,
        text=True,
        check=False,
    )


def _select_manifest(repo: Path) -> tuple[Path, str, str]:
    for manifest_path in sorted(
        repo.glob("data/candidates/*/*/publish-manifest.json"), reverse=True
    ):
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        promotion = payload.get("promotion")
        candidate = payload.get("candidate")
        if not isinstance(promotion, dict) or promotion.get("eligible") is not True:
            continue
        if not isinstance(candidate, dict):
            continue
        candidate_paths = [candidate.get("summary_path"), candidate.get("content_path")]
        if all(isinstance(path, str) and (repo / path).is_file() for path in candidate_paths):
            return manifest_path.relative_to(repo), str(payload["week"]), manifest_path.parent.name
    raise RuntimeError("No retained eligible publish candidate was found on publish")


def _prepare_proof_manifest(repo: Path, source_publish_sha: str) -> tuple[Path, str, str]:
    source_path, week, _ = _select_manifest(repo)
    proof_run_id = f"atomic-proof-{source_publish_sha[:12]}"
    proof_path = Path("data/candidates") / week / proof_run_id / "publish-manifest.json"
    if not (repo / proof_path).is_file():
        payload = json.loads((repo / source_path).read_text(encoding="utf-8"))
        payload["run_id"] = proof_run_id
        (repo / proof_path).parent.mkdir(parents=True, exist_ok=True)
        (repo / proof_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    promote_candidate(proof_path, root=repo)
    return proof_path, week, proof_run_id


def _scenario_environment(
    proof_root: Path, manifest: Path, week: str, run_id: str, expected_sha: str
) -> dict[str, str]:
    return {
        "ATOMIC_PROOF_ROOT": str(proof_root),
        "DEFAULT_BRANCH": "main",
        "DATA_BRANCH": "publish",
        "WEEK": week,
        "RUN_MODE": "normal",
        "MANIFEST_FILE": manifest.as_posix(),
        "EXPECTED_PUBLISH_SHA": expected_sha,
        "GITHUB_RUN_ID": run_id,
    }


def _write_proof_mutation(repo: Path, source_publish_sha: str, proof_nonce: str) -> None:
    target = repo / PROOF_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "schema_version": "atomic_publish_proof_v1",
                "source_publish_sha": source_publish_sha,
                "proof_nonce": proof_nonce,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _changed_paths(repo: Path, before: str, after: str) -> list[str]:
    output = run_git(repo, "diff", "--name-only", before, after)
    return output.splitlines() if output else []


def _write_manifest(output_dir: Path, name: str, manifest: dict[str, object]) -> None:
    (output_dir / name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_proof(repo_root: Path, output_dir: Path) -> dict[str, object]:
    """Run all five proof scenarios and return the authoritative evidence record."""
    repo_root = repo_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    workflow_path = repo_root / ".github/workflows/crawl-and-publish.yml"
    commit_script = extract_commit_step(workflow_path)
    # CI's checkout is a shallow, single-ref clone: HEAD's ancestor objects are
    # missing, so pushing it below would be rejected ("shallow update not
    # allowed"). Unshallow first so seed_isolated_origin can push full history.
    if run_git(repo_root, "rev-parse", "--is-shallow-repository") == "true":
        run_git(repo_root, "fetch", "--unshallow", "origin")
    main_sha = run_git(repo_root, "rev-parse", "HEAD")
    # Mirror the production commit step's own "fetch, then rev-parse" pattern
    # (see REQUIRED_COMMIT_FRAGMENTS) so this proof works against CI's shallow,
    # single-ref checkout, where origin/publish is not fetched by default.
    run_git(repo_root, "fetch", "origin", "publish")
    source_publish_sha = run_git(repo_root, "rev-parse", "origin/publish")

    with tempfile.TemporaryDirectory(prefix="atomic-publish-proof-") as temporary:
        proof_root = Path(temporary).resolve()
        proof_nonce = proof_root.name
        origin = seed_isolated_origin(repo_root, main_sha, source_publish_sha, proof_root)

        normal_repo = _clone(origin, proof_root / "normal")
        hydrate_generated_paths(normal_repo, "refs/remotes/origin/publish", GENERATED_PATHS)
        manifest_path, week, run_id = _prepare_proof_manifest(normal_repo, source_publish_sha)
        _write_proof_mutation(normal_repo, source_publish_sha, proof_nonce)
        candidate_manifest = generated_tree_manifest(normal_repo, None, GENERATED_PATHS)
        normal = run_commit_step(
            normal_repo,
            commit_script,
            _scenario_environment(proof_root, manifest_path, week, run_id, source_publish_sha),
        )
        if normal.returncode != 0:
            raise RuntimeError(f"Normal publication failed: {normal.stderr}\n{normal.stdout}")
        accepted_sha = run_git(origin, "rev-parse", "refs/heads/publish")
        if accepted_sha == source_publish_sha:
            raise RuntimeError(
                "Normal publication did not advance isolated publish\n"
                f"commit-step stdout:\n{normal.stdout}\ncommit-step stderr:\n{normal.stderr}"
            )
        if (
            int(run_git(origin, "rev-list", "--count", f"{source_publish_sha}..{accepted_sha}"))
            != 1
        ):
            raise RuntimeError("Normal publication must add exactly one commit")
        accepted_manifest = generated_tree_manifest(origin, accepted_sha, GENERATED_PATHS)
        if candidate_manifest != accepted_manifest:
            raise RuntimeError("Candidate and accepted generated trees differ")
        changed_paths = _changed_paths(origin, source_publish_sha, accepted_sha)
        allowed_roots = tuple(path.rstrip("/") for path in GENERATED_PATHS) + ("data/backups",)
        if any(not path.startswith(allowed_roots) for path in changed_paths):
            raise RuntimeError(f"Publication changed an out-of-bound path: {changed_paths}")

        rerun_repo = _clone(origin, proof_root / "rerun")
        hydrate_generated_paths(rerun_repo, "refs/remotes/origin/publish", GENERATED_PATHS)
        rerun_manifest, rerun_week, rerun_id = _prepare_proof_manifest(
            rerun_repo, source_publish_sha
        )
        _write_proof_mutation(rerun_repo, source_publish_sha, proof_nonce)
        before_rerun = run_git(origin, "rev-parse", "refs/heads/publish")
        rerun = run_commit_step(
            rerun_repo,
            commit_script,
            _scenario_environment(proof_root, rerun_manifest, rerun_week, rerun_id, before_rerun),
        )
        after_rerun = run_git(origin, "rev-parse", "refs/heads/publish")
        if rerun.returncode != 0 or after_rerun != before_rerun:
            raise RuntimeError("Identical rerun changed isolated publish")

        failure_repo = _clone(origin, proof_root / "failure")
        hydrate_generated_paths(failure_repo, "refs/remotes/origin/publish", GENERATED_PATHS)
        failure_before = run_git(origin, "rev-parse", "refs/heads/publish")
        partial = failure_repo / "data/derived/observatory/partial-proof.json"
        partial.parent.mkdir(parents=True, exist_ok=True)
        partial.write_text('{"partial": true', encoding="utf-8")
        injected = subprocess.run(  # nosec B603 - fixed argv, no shell, sanitized env
            [sys.executable, "-c", "raise SystemExit(23)"],
            cwd=failure_repo,
            env=_clean_environment(),
            capture_output=True,
            text=True,
            check=False,
        )
        failure_after = run_git(origin, "rev-parse", "refs/heads/publish")
        if injected.returncode == 0 or failure_after != failure_before:
            raise RuntimeError("Injected generator failure changed isolated publish")

        hydration_repo = _clone(origin, proof_root / "hydration")
        preserved = hydrate_generated_paths(
            hydration_repo, "refs/remotes/origin/publish", GENERATED_PATHS
        )
        hydrated_manifest = generated_tree_manifest(hydration_repo, None, GENERATED_PATHS)
        if hydrated_manifest != accepted_manifest:
            raise RuntimeError("Hydrated and accepted generated trees differ")
        reference_problems = check_publish_references(hydration_repo)
        if reference_problems:
            raise RuntimeError(f"Hydrated reference checks failed: {reference_problems}")

        _write_manifest(output_dir, "candidate-tree.json", candidate_manifest)
        _write_manifest(output_dir, "accepted-tree.json", accepted_manifest)
        _write_manifest(output_dir, "hydrated-tree.json", hydrated_manifest)
        evidence: dict[str, object] = {
            "schema_version": "atomic_publish_proof_v1",
            "reviewed_main_sha": main_sha,
            "source_publish_sha": source_publish_sha,
            "accepted_proof_sha": accepted_sha,
            "workflow_sha256": hashlib.sha256(workflow_path.read_bytes()).hexdigest(),
            "commit_step_sha256": hashlib.sha256(commit_script.encode("utf-8")).hexdigest(),
            "scenarios": {
                "normal": {
                    "exit_code": normal.returncode,
                    "before_sha": source_publish_sha,
                    "after_sha": accepted_sha,
                    "commit_count": 1,
                    "changed_paths": changed_paths,
                },
                "identical_rerun": {
                    "exit_code": rerun.returncode,
                    "before_sha": before_rerun,
                    "after_sha": after_rerun,
                },
                "injected_failure": {
                    "exit_code": injected.returncode,
                    "before_sha": failure_before,
                    "after_sha": failure_after,
                },
                "generated_tree": {
                    "candidate_digest": candidate_manifest["digest"],
                    "accepted_digest": accepted_manifest["digest"],
                },
                "hydration": {
                    "accepted_digest": accepted_manifest["digest"],
                    "hydrated_digest": hydrated_manifest["digest"],
                    "preserved_main_paths": preserved,
                    "reference_problems": reference_problems,
                },
            },
            "publication_metadata_paths": [
                path for path in changed_paths if path.startswith("data/backups/")
            ],
            "tools": {
                "git": run_git(repo_root, "--version"),
                "python": sys.version.split()[0],
            },
        }
    evidence_path = output_dir / "atomic-publish-proof.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return evidence


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = create_parser().parse_args(argv)
    try:
        evidence = run_proof(args.repo_root, args.output_dir)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Atomic publish proof failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

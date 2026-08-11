from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path

import yaml

from scripts.publish_hydration import (
    GENERATED_PATHS,
    check_publish_references,
)

ROOT = Path(__file__).resolve().parent.parent
WEEK = "2026-W23"
ARTICLE_PATH = "content/weekly/2026/W23.md"
MANIFEST_PATH = "data/candidates/2026-W23/12345/publish-manifest.json"
PROMOTION_PATH = "data/published/2026-W23/promotion-manifest.json"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _seed_consistent_release(root: Path) -> None:
    """Create a hydrated tree whose promotion record resolves cleanly."""
    article_body = "# Week 23\n\nWeekly through-line.\n"
    manifest_body = json.dumps({"candidate": "eligible"}, sort_keys=True) + "\n"
    _write(root / ARTICLE_PATH, article_body)
    _write(root / MANIFEST_PATH, manifest_body)

    record: dict[str, object] = {
        "schema_version": "promotion_transaction_v1",
        "week": WEEK,
        "run_id": "12345",
        "published_artifacts": [
            {
                "role": "hugo_content",
                "path": ARTICLE_PATH,
                "sha256": _sha256(article_body),
            }
        ],
        "source_manifest": {
            "path": MANIFEST_PATH,
            "sha256": _sha256(manifest_body),
        },
    }
    transaction_bytes = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    record["transaction_id"] = hashlib.sha256(transaction_bytes).hexdigest()
    _write(root / PROMOTION_PATH, json.dumps(record, indent=2) + "\n")


def test_repository_paths_command_lists_generated_paths() -> None:
    # content/data and data/candidates must be hydrated for the checks to see the
    # promotion record and its source manifest.
    assert "content/data/" in GENERATED_PATHS
    assert "data/candidates/" in GENERATED_PATHS
    assert "data/published/" in GENERATED_PATHS
    assert "content/repo/" not in GENERATED_PATHS


def test_consistent_release_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_consistent_release(root)
        assert check_publish_references(root) == []


def test_missing_source_manifest_is_reported() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_consistent_release(root)
        (root / MANIFEST_PATH).unlink()
        problems = check_publish_references(root)
        assert any("source_manifest" in problem for problem in problems)


def test_missing_article_is_reported() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_consistent_release(root)
        (root / ARTICLE_PATH).unlink()
        problems = check_publish_references(root)
        assert any("article_path" in problem for problem in problems)


def test_article_hash_mismatch_is_reported() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_consistent_release(root)
        # Mutate the article after its hash was recorded in the promotion record.
        (root / ARTICLE_PATH).write_text("# Week 23 (edited)\n", encoding="utf-8")
        problems = check_publish_references(root)
        assert any("promotion:" in problem for problem in problems)


def test_missing_promotion_record_is_reported() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        assert any(
            "no retained promotion record" in problem for problem in check_publish_references(root)
        )


def test_dangling_embed_is_reported_in_hydrated_tree() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_consistent_release(root)
        _write(
            root / "content/embeds/chart/index.md",
            '+++\nsource_page = "/data/does-not-exist/"\n+++\n',
        )
        problems = check_publish_references(root)
        assert any(problem.startswith("embed:") for problem in problems)


def _deploy_hydration_paths() -> list[str]:
    workflow = yaml.safe_load((ROOT / ".github/workflows/deploy-site.yml").read_text("utf-8"))
    # Locate the hydration list by content so a step rename does not break the guard.
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            block = re.search(r"GENERATED_PATHS=\((?P<body>.*?)\)", step.get("run", ""), re.DOTALL)
            if block is not None:
                return [line.strip() for line in block.group("body").split("\n") if line.strip()]
    raise AssertionError("deploy hydration GENERATED_PATHS block not found")


def test_generated_paths_match_deploy_workflow() -> None:
    # The CI gate must hydrate the same generated set the deploy does, or it would
    # not reproduce the deploy's publish-hydration (NFR-011).
    assert GENERATED_PATHS == _deploy_hydration_paths()


def test_ci_workflow_runs_publish_hydration_gate() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text("utf-8"))
    assert "publish-hydration-parity" in workflow["jobs"]
    job = workflow["jobs"]["publish-hydration-parity"]
    runs = "\n".join(step.get("run", "") for step in job["steps"])
    assert "git fetch origin publish" in runs
    assert "scripts.publish_hydration paths" in runs
    assert "scripts.publish_hydration check" in runs

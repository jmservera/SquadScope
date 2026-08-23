"""Download a workflow-run artifact with bounded retries and atomic overlay."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess  # nosec B404 - fixed gh argv is required for GitHub artifact downloads
import tempfile
import time
from pathlib import Path


def _workspace_destination(raw_destination: str) -> Path:
    workspace = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
    destination = (workspace / raw_destination).resolve()
    if destination != workspace and workspace not in destination.parents:
        raise ValueError(f"Artifact destination must stay inside GITHUB_WORKSPACE: {destination}")
    return destination


def download_artifact(
    *,
    artifact: str,
    destination: Path,
    repo: str,
    run_id: str,
    attempts: int,
    initial_delay: float,
) -> None:
    if not artifact or "/" in artifact or "\\" in artifact:
        raise ValueError("Artifact name must be a non-empty basename")
    if not run_id.isdigit():
        raise ValueError("Run ID must be numeric")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Repository must use owner/name syntax")
    if not os.environ.get("GH_TOKEN"):
        raise ValueError("GH_TOKEN is required")

    gh_path = shutil.which("gh")
    if not gh_path:
        raise RuntimeError("GitHub CLI is required to download workflow artifacts")

    runner_temp = os.environ.get("RUNNER_TEMP")
    last_error: subprocess.CalledProcessError | None = None
    for attempt in range(1, attempts + 1):
        with tempfile.TemporaryDirectory(dir=runner_temp) as temp_dir:
            try:
                subprocess.run(  # nosec B603 - validated values, fixed argv, no shell
                    [
                        gh_path,
                        "run",
                        "download",
                        run_id,
                        "--repo",
                        repo,
                        "--name",
                        artifact,
                        "--dir",
                        temp_dir,
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError as error:
                last_error = error
            else:
                destination.mkdir(parents=True, exist_ok=True)
                shutil.copytree(temp_dir, destination, dirs_exist_ok=True)
                return

        if attempt < attempts:
            delay = initial_delay * (2 ** (attempt - 1))
            print(
                f"::warning::Artifact {artifact} download failed "
                f"(attempt {attempt}/{attempts}); retrying in {delay:g}s"
            )
            time.sleep(delay)

    raise RuntimeError(
        f"Unable to download artifact {artifact} from run {run_id} after {attempts} attempts"
    ) from last_error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", ""))
    parser.add_argument("--attempts", type=int, default=5)
    parser.add_argument("--initial-delay", type=float, default=5)
    args = parser.parse_args()
    if not args.repo:
        parser.error("--repo or GITHUB_REPOSITORY is required")
    if args.attempts < 1:
        parser.error("--attempts must be at least 1")
    if args.initial_delay < 0:
        parser.error("--initial-delay cannot be negative")
    return args


def main() -> None:
    args = parse_args()
    download_artifact(
        artifact=args.artifact,
        destination=_workspace_destination(args.destination),
        repo=args.repo,
        run_id=args.run_id,
        attempts=args.attempts,
        initial_delay=args.initial_delay,
    )


if __name__ == "__main__":
    main()

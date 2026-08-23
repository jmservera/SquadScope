"""Download a workflow-run artifact with bounded retries and atomic overlay."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import time
import zipfile
from pathlib import Path
from urllib import error, request


def _workspace_destination(raw_destination: str) -> Path:
    workspace = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
    destination = (workspace / raw_destination).resolve()
    if destination != workspace and workspace not in destination.parents:
        raise ValueError(f"Artifact destination must stay inside GITHUB_WORKSPACE: {destination}")
    return destination


def _extract_archive(archive_path: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if target != destination and destination not in target.parents:
                raise ValueError(f"Artifact entry escapes extraction root: {member.filename}")
        archive.extractall(destination)


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
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise ValueError("GH_TOKEN is required")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    list_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100"
    runner_temp = os.environ.get("RUNNER_TEMP")
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        with tempfile.TemporaryDirectory(dir=runner_temp) as temp_dir:
            temp_path = Path(temp_dir)
            try:
                with request.urlopen(
                    request.Request(list_url, headers=headers),
                    timeout=30,  # nosec B310 - validated owner/name and run ID force GitHub HTTPS.
                ) as response:
                    payload = json.load(response)
                artifact_id = next(
                    item["id"]
                    for item in payload["artifacts"]
                    if item["name"] == artifact and not item["expired"]
                )
                archive_path = temp_path / "artifact.zip"
                download_url = (
                    f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact_id}/zip"
                )
                with (
                    request.urlopen(
                        request.Request(download_url, headers=headers),
                        timeout=60,  # nosec B310 - authenticated GitHub response supplies the ID.
                    ) as response,
                    archive_path.open("wb") as archive,
                ):
                    shutil.copyfileobj(response, archive)

                extracted_path = temp_path / "extracted"
                extracted_path.mkdir()
                _extract_archive(archive_path, extracted_path)
            except (
                error.HTTPError,
                error.URLError,
                KeyError,
                StopIteration,
                zipfile.BadZipFile,
            ) as caught:
                last_error = caught
            else:
                destination.mkdir(parents=True, exist_ok=True)
                shutil.copytree(extracted_path, destination, dirs_exist_ok=True)
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

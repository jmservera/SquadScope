import subprocess
from pathlib import Path
from unittest.mock import call, patch

import pytest

from scripts import download_run_artifact


def test_retries_before_atomically_overlaying_artifact(tmp_path: Path) -> None:
    destination = tmp_path / "destination"
    failure = subprocess.CalledProcessError(1, ["/usr/bin/gh"])

    with (
        patch("scripts.download_run_artifact.shutil.which", return_value="/usr/bin/gh"),
        patch(
            "scripts.download_run_artifact.subprocess.run",
            side_effect=[failure, failure, subprocess.CompletedProcess(["gh"], 0)],
        ) as run_mock,
        patch("scripts.download_run_artifact.time.sleep") as sleep_mock,
        patch("scripts.download_run_artifact.shutil.copytree") as copy_mock,
        patch.dict("os.environ", {"GH_TOKEN": "test-token"}),
    ):
        download_run_artifact.download_artifact(
            artifact="raw-data",
            destination=destination,
            repo="jmservera/SquadScope",
            run_id="31985981109",
            attempts=5,
            initial_delay=2,
        )

    assert run_mock.call_count == 3
    command = run_mock.call_args.args[0]
    assert command[:7] == [
        "/usr/bin/gh",
        "run",
        "download",
        "31985981109",
        "--repo",
        "jmservera/SquadScope",
        "--name",
    ]
    assert command[7] == "raw-data"
    assert command[8] == "--dir"
    sleep_mock.assert_has_calls([call(2), call(4)])
    copy_mock.assert_called_once()
    assert copy_mock.call_args.kwargs == {"dirs_exist_ok": True}


def test_raises_after_bounded_attempts(tmp_path: Path) -> None:
    failure = subprocess.CalledProcessError(1, ["/usr/bin/gh"])

    with (
        patch("scripts.download_run_artifact.shutil.which", return_value="/usr/bin/gh"),
        patch("scripts.download_run_artifact.subprocess.run", side_effect=failure),
        patch("scripts.download_run_artifact.time.sleep") as sleep_mock,
        patch.dict("os.environ", {"GH_TOKEN": "test-token"}),
        pytest.raises(RuntimeError, match="after 3 attempts"),
    ):
        download_run_artifact.download_artifact(
            artifact="raw-data",
            destination=tmp_path / "destination",
            repo="jmservera/SquadScope",
            run_id="31985981109",
            attempts=3,
            initial_delay=1,
        )

    assert sleep_mock.call_count == 2


def test_rejects_destination_outside_workspace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("GITHUB_WORKSPACE", str(workspace))

    with pytest.raises(ValueError, match="inside GITHUB_WORKSPACE"):
        download_run_artifact._workspace_destination("../outside")


@pytest.mark.parametrize("artifact", ["", "../raw-data", r"folder\raw-data"])
def test_rejects_unsafe_artifact_names(tmp_path: Path, artifact: str) -> None:
    with pytest.raises(ValueError, match="basename"):
        download_run_artifact.download_artifact(
            artifact=artifact,
            destination=tmp_path,
            repo="jmservera/SquadScope",
            run_id="31985981109",
            attempts=1,
            initial_delay=0,
        )


def test_rejects_unsafe_repository(tmp_path: Path) -> None:
    with (
        patch.dict("os.environ", {"GH_TOKEN": "test-token"}),
        pytest.raises(ValueError, match="owner/name"),
    ):
        download_run_artifact.download_artifact(
            artifact="raw-data",
            destination=tmp_path,
            repo="../other",
            run_id="31985981109",
            attempts=1,
            initial_delay=0,
        )

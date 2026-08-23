import io
import json
import zipfile
from pathlib import Path
from unittest.mock import call, patch
from urllib import error

import pytest

from scripts import download_run_artifact


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def artifact_list_response() -> Response:
    return Response(
        json.dumps({"artifacts": [{"id": 123, "name": "raw-data", "expired": False}]}).encode()
    )


def artifact_response(filename: str = "2026-W34.json") -> Response:
    content = io.BytesIO()
    with zipfile.ZipFile(content, "w") as archive:
        archive.writestr(filename, "{}")
    return Response(content.getvalue())


def test_retries_before_atomically_overlaying_artifact(tmp_path: Path) -> None:
    destination = tmp_path / "destination"
    failure = error.HTTPError("", 403, "Forbidden", {}, None)

    with (
        patch(
            "scripts.download_run_artifact.request.urlopen",
            side_effect=[
                failure,
                failure,
                artifact_list_response(),
                artifact_response(),
            ],
        ) as urlopen_mock,
        patch("scripts.download_run_artifact.time.sleep") as sleep_mock,
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

    assert urlopen_mock.call_count == 4
    sleep_mock.assert_has_calls([call(2), call(4)])
    assert (destination / "2026-W34.json").read_text(encoding="utf-8") == "{}"


def test_raises_after_bounded_attempts(tmp_path: Path) -> None:
    failure = error.HTTPError("", 403, "Forbidden", {}, None)

    with (
        patch("scripts.download_run_artifact.request.urlopen", side_effect=failure),
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


def test_rejects_archive_path_traversal(tmp_path: Path) -> None:
    with (
        patch(
            "scripts.download_run_artifact.request.urlopen",
            side_effect=[artifact_list_response(), artifact_response("../outside")],
        ),
        patch.dict("os.environ", {"GH_TOKEN": "test-token"}),
        pytest.raises(ValueError, match="escapes extraction root"),
    ):
        download_run_artifact.download_artifact(
            artifact="raw-data",
            destination=tmp_path / "destination",
            repo="jmservera/SquadScope",
            run_id="31985981109",
            attempts=1,
            initial_delay=0,
        )

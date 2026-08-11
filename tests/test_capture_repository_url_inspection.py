from __future__ import annotations

import json

from scripts import capture_repository_url_inspection as inspection


def test_build_snapshot_normalizes_index_evidence() -> None:
    inventory = {"records": [{"url": "/repo/"}, {"url": "/repo/alpha/"}]}

    def inspect(url: str) -> dict[str, object]:
        known = url.endswith("/alpha/")
        return {
            "inspectionResult": {
                "inspectionResultLink": f"https://search.google.com/inspect/{known}",
                "indexStatusResult": {
                    "verdict": "PASS" if known else "NEUTRAL",
                    "coverageState": "Submitted and indexed"
                    if known
                    else "URL is unknown to Google",
                    "indexingState": "INDEXING_ALLOWED" if known else "INDEXING_STATE_UNSPECIFIED",
                    "pageFetchState": "SUCCESSFUL" if known else "PAGE_FETCH_STATE_UNSPECIFIED",
                },
            }
        }

    payload = inspection.build_snapshot(
        inventory,
        site_origin="https://claracle.com",
        site_url="sc-domain:claracle.com",
        captured_at="2026-08-11T09:00:00+00:00",
        inspector=inspect,
    )

    assert payload["counts"]["total"] == 2
    assert payload["counts"]["verdicts"] == {"NEUTRAL": 1, "PASS": 1}
    assert payload["records"][1]["coverage_state"] == "Submitted and indexed"


def test_validate_snapshot_rejects_incomplete_coverage() -> None:
    inventory = {"records": [{"url": "/repo/"}]}
    snapshot = {"records": []}

    try:
        inspection.validate_snapshot(snapshot, inventory)
    except ValueError as error:
        assert "does not cover" in str(error)
    else:
        raise AssertionError("Expected incomplete snapshot to fail")


def test_inspect_url_retries_timeout_and_sends_bearer_token(monkeypatch) -> None:
    requests = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self) -> bytes:
            return json.dumps({"inspectionResult": {}}).encode()

    def urlopen(request, timeout):
        requests.append((request, timeout))
        if len(requests) == 1:
            raise TimeoutError("transient")
        return Response()

    monkeypatch.setattr(inspection.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(inspection.time, "sleep", lambda _seconds: None)

    result = inspection.inspect_url(
        "https://claracle.com/repo/",
        site_url="sc-domain:claracle.com",
        token="secret-token",
    )

    assert result == {"inspectionResult": {}}
    assert len(requests) == 2
    assert requests[1][0].get_header("Authorization") == "Bearer secret-token"
    assert requests[1][1] == 30

import json
import unittest
from datetime import UTC, datetime, timedelta
from unittest import mock

from scripts import podcast_dispatch_state as state


class PodcastDispatchStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.identity = state.CanonicalPublicationIdentity(
            "2026-W39", "35561779454", "a" * 64, "b" * 64
        )

    def receipt(self, receipt_state: str = "accepted") -> state.DispatchReceipt:
        return state.DispatchReceipt(
            receipt_id="receipt-1",
            created_at=datetime.now(UTC).isoformat(),
            dispatch_run_id="35562322880",
            attempt_id="35562322880-1",
            identity=self.identity,
            receipt_state=receipt_state,
            api_status=202 if receipt_state == "accepted" else None,
            podcaster_job_id="job-1" if receipt_state == "accepted" else None,
            correlation_id="correlation-1" if receipt_state == "accepted" else None,
            actions_run_url="https://github.com/example/repo/actions/runs/35562322880",
        )

    def terminal(
        self,
        synthesis: str = "started",
        video: str = "succeeded",
        provider: str = "published",
        verified: bool = True,
    ) -> state.TerminalStatus:
        return state.TerminalStatus(
            self.identity,
            "job-1",
            "correlation-1",
            synthesis,
            video,
            provider,
            verified,
        )

    def test_identity_key_uses_manifest_digest(self) -> None:
        other = state.CanonicalPublicationIdentity(
            self.identity.week,
            self.identity.publish_run_id,
            self.identity.article_sha256,
            "c" * 64,
        )
        self.assertNotEqual(
            state.canonical_identity_key(self.identity), state.canonical_identity_key(other)
        )
        self.assertNotEqual(
            state.incident_key(self.identity, "provider", "timeout"),
            state.incident_key(other, "provider", "timeout"),
        )

    def test_receipt_round_trip_is_stable_and_secret_fields_are_rejected(self) -> None:
        receipt = self.receipt()
        encoded = state.serialize_receipt(receipt)
        self.assertEqual(state.serialize_receipt(state.parse_receipt(encoded)), encoded)
        payload = json.loads(encoded)
        payload["api_key"] = "secret"
        with self.assertRaisesRegex(ValueError, "unsupported receipt fields"):
            state.parse_receipt(payload)
        self.assertNotIn("secret", encoded)

    def test_github_request_carries_bearer_token_without_serializing_it(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"{}"
        with mock.patch.object(state.request, "urlopen", return_value=response) as urlopen:
            self.assertEqual(
                state._github_json("https://api.github.com/repos/example/repo", "sentinel-token"),
                {},
            )
        request_object = urlopen.call_args.args[0]
        self.assertEqual(request_object.get_header("Authorization"), "Bearer sentinel-token")
        self.assertNotIn("sentinel-token", json.dumps(request_object.data))

    def test_retry_classification_is_monotonic(self) -> None:
        self.assertEqual(
            state.receipt_retry_classification([self.receipt("attempt_prepared")]),
            "retryable_non_mutation",
        )
        self.assertEqual(
            state.receipt_retry_classification(
                [self.receipt("handoff_entered"), self.receipt("pre_submit_failed")]
            ),
            "blocking",
        )

    def test_v1_parser_never_fabricates_manifest_identity(self) -> None:
        parsed = state.parse_receipt(
            {
                "schema_version": "podcast_dispatch_receipt_v1",
                "receipt_state": "submitted",
                "week": "2026-W39",
                "publish_run_id": "1",
                "article_sha256": "a" * 64,
            }
        )
        self.assertNotIn("manifest_sha256", parsed)

    def test_terminal_success_requires_every_authoritative_stage(self) -> None:
        self.assertTrue(state.evaluate_terminal_status(self.terminal()).success)
        self.assertIsNone(state.evaluate_terminal_status(self.terminal(video="pending")))
        result = state.evaluate_terminal_status(self.terminal(verified=False))
        self.assertEqual(
            (result.success, result.stage, result.state), (False, "provider", "unverified")
        )

    def test_status_validation_rejects_identity_mismatch(self) -> None:
        payload = {
            "schema_version": state.STATUS_SCHEMA_VERSION_V1,
            "identity": {**self.identity.as_dict(), "manifest_sha256": "c" * 64},
            "job_id": "job-1",
            "correlation_id": "correlation-1",
            "synthesis": {"state": "started"},
            "video": {"state": "succeeded"},
            "provider": {"state": "published", "external_verified": True},
        }
        with self.assertRaisesRegex(state.TerminalEvidenceError, "identity mismatch"):
            state.validate_terminal_status(payload, self.identity, "job-1", "correlation-1")

    def test_ledger_receipts_require_expected_repository_workflow(self) -> None:
        receipt = self.receipt()
        ledger = {
            "title": state.LEDGER_TITLE,
            "body": state.LEDGER_MARKER,
            "comments_url": "https://api.github.com/repos/example/repo/issues/9/comments",
        }
        comment = {
            "user": {"login": "github-actions[bot]"},
            "body": state.serialize_receipt(receipt),
            "html_url": "https://github.com/example/repo/issues/9#issuecomment-1",
        }

        def github(url, token, **kwargs):
            if "/issues/9/comments" in url:
                return [comment]
            if f"/actions/runs/{receipt.dispatch_run_id}" in url:
                return {
                    "id": int(receipt.dispatch_run_id),
                    "path": state.EXPECTED_DISPATCH_WORKFLOW_PATH,
                    "repository": {"full_name": "example/repo"},
                }
            raise AssertionError(url)

        with (
            mock.patch.object(state, "_iter_issue_pages", return_value=iter([ledger])),
            mock.patch.object(state, "_github_json", side_effect=github),
        ):
            self.assertEqual(state.list_ledger_receipts("example/repo", "token"), [receipt])

        def wrong_workflow(url, token, **kwargs):
            result = github(url, token, **kwargs)
            if isinstance(result, dict) and "path" in result:
                result["path"] = ".github/workflows/unrelated.yml"
            return result

        with (
            mock.patch.object(state, "_iter_issue_pages", return_value=iter([ledger])),
            mock.patch.object(state, "_github_json", side_effect=wrong_workflow),
        ):
            self.assertEqual(state.list_ledger_receipts("example/repo", "token"), [])

        for field, value in (
            ("repository", {"full_name": "other/repo"}),
            ("id", int(receipt.dispatch_run_id) + 1),
        ):

            def untrusted_run(url, token, **kwargs):
                result = github(url, token, **kwargs)
                if isinstance(result, dict) and "path" in result:
                    result[field] = value
                return result

            with (
                self.subTest(field=field),
                mock.patch.object(state, "_iter_issue_pages", return_value=iter([ledger])),
                mock.patch.object(state, "_github_json", side_effect=untrusted_run),
            ):
                self.assertEqual(state.list_ledger_receipts("example/repo", "token"), [])

        forged = {**comment, "user": {"login": "attacker"}}
        with (
            mock.patch.object(state, "_iter_issue_pages", return_value=iter([ledger])),
            mock.patch.object(state, "_github_json", return_value=[forged]) as github_call,
        ):
            self.assertEqual(state.list_ledger_receipts("example/repo", "token"), [])
        github_call.assert_called_once()

    def test_resolver_prefers_authoritative_accepted_receipt(self) -> None:
        accepted = self.receipt()
        prepared = state.DispatchReceipt(
            **{
                **accepted.__dict__,
                "receipt_id": "receipt-2",
                "created_at": (datetime.now(UTC) + timedelta(seconds=1)).isoformat(),
                "receipt_state": "attempt_prepared",
                "api_status": None,
                "podcaster_job_id": None,
                "correlation_id": None,
            }
        )
        with mock.patch.object(
            state,
            "list_ledger_receipts",
            return_value=[prepared, accepted],
        ):
            self.assertEqual(
                state.resolve_authoritative_receipt("example/repo", "token", self.identity),
                accepted,
            )

    def test_missing_status_contract_fails_visibly(self) -> None:
        result = state.monitor_terminal_outcome(self.receipt(), "", "secret")
        self.assertEqual(
            (result.success, result.stage, result.state), (False, "status_contract", "unavailable")
        )

    def test_monitor_emits_warning_then_times_out_without_synthesis(self) -> None:
        clock = [0.0]
        warnings: list[int] = []

        def monotonic() -> float:
            return clock[0]

        def sleep(seconds: float) -> None:
            clock[0] += seconds

        def fetch(*args):
            return self.terminal(
                synthesis="pending", video="pending", provider="pending", verified=False
            )

        with mock.patch.object(state, "SYNTHESIS_WARNING_SECONDS", 2):
            result = state.monitor_terminal_outcome(
                self.receipt(),
                "https://example.invalid/status",
                "secret",
                fetch=fetch,
                monotonic=monotonic,
                sleep=sleep,
                warning=warnings.append,
                evidence_deadline=5,
                poll_interval=2,
            )
        self.assertEqual((result.stage, result.state), ("synthesis", "timeout"))
        self.assertEqual(warnings, [2])
        self.assertTrue(result.warning_emitted)

    def test_monitor_stops_after_error_budget_and_caps_request_timeout(self) -> None:
        clock = [0.0]
        timeouts: list[float] = []

        def fetch(*args):
            timeouts.append(args[-1])
            clock[0] += args[-1]
            raise OSError("hung")

        result = state.monitor_terminal_outcome(
            self.receipt(),
            "https://example.invalid/status",
            "secret",
            fetch=fetch,
            monotonic=lambda: clock[0],
            sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
            evidence_deadline=45,
            poll_interval=1,
        )
        self.assertEqual(
            (result.stage, result.state), ("evidence_unavailable", "error_budget_exhausted")
        )
        self.assertTrue(all(0 < timeout <= 10 for timeout in timeouts))
        self.assertLessEqual(clock[0], 45)

    def test_monitor_uses_accepted_time_for_deadline_and_cleanup_reserve(self) -> None:
        accepted_at = datetime(2026, 9, 21, 20, 0, tzinfo=UTC)
        receipt = state.DispatchReceipt(
            **{
                **self.receipt().__dict__,
                "created_at": accepted_at.isoformat(),
            }
        )
        clock = [0.0]
        timeouts: list[float] = []

        def fetch(*args):
            timeouts.append(args[-1])
            clock[0] += args[-1]
            return self.terminal(
                synthesis="pending",
                video="pending",
                provider="pending",
                verified=False,
            )

        result = state.monitor_terminal_outcome(
            receipt,
            "https://example.invalid/status",
            "secret",
            fetch=fetch,
            monotonic=lambda: clock[0],
            wall_time=lambda: accepted_at.timestamp() + 3470,
            sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
        )
        self.assertEqual(timeouts, [10])
        self.assertEqual((result.stage, result.state), ("synthesis", "timeout"))
        self.assertEqual(result.cleanup_budget_seconds, 120)

    def test_monitor_restart_reconstructs_latency_warning_from_accepted_time(self) -> None:
        accepted_at = datetime(2026, 9, 21, 20, 0, tzinfo=UTC)
        receipt = state.DispatchReceipt(
            **{
                **self.receipt().__dict__,
                "created_at": accepted_at.isoformat(),
            }
        )
        clock = [0.0]
        warnings: list[int] = []
        result = state.monitor_terminal_outcome(
            receipt,
            "https://example.invalid/status",
            "secret",
            fetch=lambda *args: self.terminal(
                synthesis="pending",
                video="pending",
                provider="pending",
                verified=False,
            ),
            monotonic=lambda: clock[0],
            wall_time=lambda: accepted_at.timestamp() + 700,
            sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
            warning=warnings.append,
            evidence_deadline=705,
            poll_interval=30,
        )
        self.assertEqual(warnings, [700])
        self.assertEqual((result.stage, result.state), ("synthesis", "timeout"))

    def test_monitor_classifies_mismatch_and_missing_stage_without_retries(self) -> None:
        for error_value, expected in (
            (
                state.TerminalEvidenceError(
                    "evidence_mismatch",
                    "rejected",
                    "status identity mismatch",
                ),
                ("evidence_mismatch", "rejected"),
            ),
            (
                state.TerminalEvidenceError(
                    "evidence_schema",
                    "missing_stage",
                    "status stages missing",
                ),
                ("evidence_schema", "missing_stage"),
            ),
        ):
            fetch = mock.Mock(side_effect=error_value)
            result = state.monitor_terminal_outcome(
                self.receipt(),
                "https://example.invalid/status",
                "secret",
                fetch=fetch,
                wall_time=lambda: datetime.now(UTC).timestamp(),
            )
            self.assertEqual((result.stage, result.state), expected)
            fetch.assert_called_once()

    def test_monitor_does_not_treat_video_only_as_success(self) -> None:
        clock = [0.0]
        result = state.monitor_terminal_outcome(
            self.receipt(),
            "https://example.invalid/status",
            "secret",
            fetch=lambda *args: self.terminal(
                synthesis="started", video="succeeded", provider="pending", verified=False
            ),
            monotonic=lambda: clock[0],
            sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
            evidence_deadline=1,
            poll_interval=30,
        )
        self.assertFalse(result.success)
        self.assertEqual((result.stage, result.state), ("provider", "timeout"))

    def test_incident_upsert_deduplicates_existing_marker(self) -> None:
        key = state.incident_key(self.identity, "provider", "timeout")
        existing = {
            "number": 7,
            "html_url": "https://github.com/example/repo/issues/7",
            "body": f"{state.INCIDENT_MARKER_PREFIX}{key} -->",
        }
        with (
            mock.patch.object(state, "_iter_issue_pages", return_value=iter([existing])),
            mock.patch.object(state, "_github_json", return_value={}) as github,
        ):
            url = state.upsert_incident(
                "example/repo", "token", self.identity, "provider", "timeout", {"job_id": "job-1"}
            )
        self.assertEqual(url, existing["html_url"])
        self.assertEqual(github.call_count, 1)
        self.assertIn("/issues/7/comments", github.call_args.args[0])

    def test_incident_requests_are_capped_by_cleanup_deadline(self) -> None:
        clock = [10.0]
        existing = {
            "number": 7,
            "html_url": "https://github.com/example/repo/issues/7",
            "body": (
                f"{state.INCIDENT_MARKER_PREFIX}"
                f"{state.incident_key(self.identity, 'provider', 'timeout')} -->"
            ),
        }
        with (
            mock.patch.object(state, "_iter_issue_pages", return_value=iter([existing])),
            mock.patch.object(state, "_github_json", return_value={}) as github,
        ):
            state.upsert_incident(
                "example/repo",
                "token",
                self.identity,
                "provider",
                "timeout",
                {"job_id": "job-1"},
                deadline=15,
                monotonic=lambda: clock[0],
            )
        self.assertEqual(github.call_args.kwargs["timeout"], 5)


if __name__ == "__main__":
    unittest.main()

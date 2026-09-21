import json
import unittest
from datetime import UTC, datetime
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
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            state.validate_terminal_status(payload, self.identity, "job-1", "correlation-1")

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


if __name__ == "__main__":
    unittest.main()

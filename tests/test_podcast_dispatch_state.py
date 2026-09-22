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

        numeric_identity = json.loads(encoded)
        numeric_identity["identity"]["publish_run_id"] = 35561779454
        with self.assertRaisesRegex(ValueError, "publish_run_id"):
            state.parse_receipt(numeric_identity)

        numeric_dispatch = json.loads(encoded)
        numeric_dispatch["dispatch_run_id"] = 35562322880
        with self.assertRaisesRegex(ValueError, "dispatch_run_id"):
            state.parse_receipt(numeric_dispatch)

        rejected = state.DispatchReceipt(
            **{
                **self.receipt("submission_rejected").__dict__,
                "api_status": 400,
                "api_status_category": "http_rejected_pre_acceptance",
            }
        )
        self.assertEqual(state.parse_receipt(state.serialize_receipt(rejected)), rejected)

    def test_github_request_carries_bearer_token_without_serializing_it(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"{}"
        with mock.patch.object(state.request, "urlopen", return_value=response) as urlopen:
            self.assertEqual(
                state._github_json("https://api.github.com/repos/example/repo", "sentinel-token"),
                {},
            )
        request_object = urlopen.call_args.args[0]
        self.assertEqual(
            request_object.get_header("Authorization"),
            "Bearer sentinel-token",
        )
        self.assertNotIn("sentinel-token", json.dumps(request_object.data))

        response.__enter__.return_value.read.return_value = b"{}"
        with mock.patch.object(state.request, "urlopen", return_value=response) as post:
            state._github_json(
                "https://api.github.com/repos/example/repo/issues",
                "sentinel-token",
                method="POST",
                payload={"title": "incident"},
            )
        self.assertEqual(post.call_args.args[0].get_header("Content-type"), "application/json")

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
        unclassified_rejection = self.receipt("submission_rejected")
        classified_rejection = state.DispatchReceipt(
            **{
                **unclassified_rejection.__dict__,
                "api_status": 400,
                "api_status_category": "http_rejected_pre_acceptance",
            }
        )
        self.assertEqual(
            state.receipt_retry_classification([unclassified_rejection]),
            "ambiguous_exact",
        )
        self.assertEqual(
            state.receipt_retry_classification([classified_rejection]),
            "retryable_non_mutation",
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

    def test_receipt_parser_rejects_numeric_identifiers(self) -> None:
        payload = self.receipt().as_dict()
        payload["dispatch_run_id"] = 123
        with self.assertRaisesRegex(ValueError, "dispatch_run_id"):
            state.parse_receipt(payload)

        payload = self.receipt().as_dict()
        payload["identity"]["publish_run_id"] = 456
        with self.assertRaisesRegex(ValueError, "publish_run_id"):
            state.parse_receipt(payload)

    def test_terminal_success_requires_every_authoritative_stage(self) -> None:
        self.assertTrue(state.evaluate_terminal_status(self.terminal()).success)
        self.assertIsNone(state.evaluate_terminal_status(self.terminal(video="pending")))
        result = state.evaluate_terminal_status(self.terminal(verified=False))
        self.assertEqual(
            (result.success, result.stage, result.state), (False, "provider", "unverified")
        )

    def test_weekly_identity_green_requires_exact_verified_provider_readback(self) -> None:
        self.assertEqual(
            state.derive_weekly_identity_state(self.identity, self.terminal()),
            "published_verified",
        )
        self.assertEqual(
            state.derive_weekly_identity_state(
                self.identity,
                self.terminal(),
                prior_non_green_attempt=True,
            ),
            "published_verified_recovered",
        )
        different_identity = state.CanonicalPublicationIdentity(
            "2026-W38",
            "34806779896",
            "c" * 64,
            "d" * 64,
        )
        self.assertEqual(
            state.derive_weekly_identity_state(different_identity, self.terminal()),
            "publication_unknown",
        )

    def test_weekly_identity_non_green_evidence_never_rewrites_attempt_truth(self) -> None:
        cases = (
            ({"status": self.terminal(video="pending")}, "publication_partial"),
            ({"status": self.terminal(provider="unknown")}, "publication_unknown"),
            ({"status": self.terminal(provider="failed")}, "publication_failed"),
            ({"status": None, "manual_action": True}, "manual_action_required"),
            ({"status": None, "duplicate_ambiguous": True}, "duplicate_ambiguous"),
            ({"status": None}, "readback_missing"),
        )
        for kwargs, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(
                    state.derive_weekly_identity_state(self.identity, **kwargs),
                    expected,
                )
                self.assertIn(expected, state.WEEKLY_NON_GREEN_STATES)

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

    def test_ledger_reader_consolidates_all_matching_issues(self) -> None:
        first = self.receipt("attempt_prepared")
        second = state.DispatchReceipt(
            **{
                **self.receipt().__dict__,
                "receipt_id": "receipt-2",
            }
        )
        ledgers = [
            {
                "title": state.LEDGER_TITLE,
                "body": state.LEDGER_MARKER,
                "comments_url": f"https://api.github.com/repos/example/repo/issues/{number}/comments",
            }
            for number in (9, 10)
        ]
        comments = {
            "/issues/9/comments": [
                {
                    "user": {"login": "github-actions[bot]"},
                    "body": state.serialize_receipt(first),
                    "html_url": "https://github.com/example/repo/issues/9#issuecomment-1",
                }
            ],
            "/issues/10/comments": [
                {
                    "user": {"login": "github-actions[bot]"},
                    "body": state.serialize_receipt(second),
                    "html_url": "https://github.com/example/repo/issues/10#issuecomment-2",
                }
            ],
        }

        def github(url, token, **kwargs):
            for suffix, values in comments.items():
                if suffix in url:
                    return values
            if f"/actions/runs/{first.dispatch_run_id}" in url:
                return {
                    "id": int(first.dispatch_run_id),
                    "path": state.EXPECTED_DISPATCH_WORKFLOW_PATH,
                    "repository": {"full_name": "example/repo"},
                }
            raise AssertionError(url)

        with (
            mock.patch.object(state, "_iter_issue_pages", return_value=iter(ledgers)),
            mock.patch.object(state, "_github_json", side_effect=github),
        ):
            self.assertEqual(
                state.list_ledger_receipts("example/repo", "token"),
                [first, second],
            )

    def test_ledger_creation_rechecks_and_selects_canonical_issue(self) -> None:
        canonical = {"number": 9}
        raced = {"number": 10}
        created = {"number": 11}
        with (
            mock.patch.object(
                state,
                "_ledger_issues",
                side_effect=[[], [raced, canonical]],
            ),
            mock.patch.object(state, "_github_json", return_value=created),
        ):
            self.assertEqual(state._ledger_issue("example/repo", "token"), canonical)

    def test_issue_pagination_exhaustion_fails_closed(self) -> None:
        with (
            mock.patch.object(state, "MAX_GITHUB_PAGES", 2),
            mock.patch.object(state, "_github_json", return_value=[{}] * 100) as github,
            self.assertRaisesRegex(ValueError, "issue pagination limit reached"),
        ):
            list(state._iter_issue_pages("example/repo", "token"))
        self.assertEqual(github.call_count, 2)

    def test_github_json_sets_json_content_type_for_payloads(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"{}"
        with mock.patch.object(state.request, "urlopen", return_value=response) as urlopen:
            state._github_json(
                "https://api.github.com/repos/example/repo/issues",
                "token",
                method="POST",
                payload={"title": "Incident"},
            )
        request_value = urlopen.call_args.args[0]
        self.assertEqual(request_value.get_header("Content-type"), "application/json")

    def test_ledger_comment_pagination_exhaustion_fails_closed(self) -> None:
        ledger = {
            "title": state.LEDGER_TITLE,
            "body": state.LEDGER_MARKER,
            "comments_url": "https://api.github.com/repos/example/repo/issues/9/comments",
        }
        with (
            mock.patch.object(state, "MAX_GITHUB_PAGES", 2),
            mock.patch.object(state, "_iter_issue_pages", return_value=iter([ledger])),
            mock.patch.object(state, "_github_json", return_value=[{}] * 100) as github,
            self.assertRaisesRegex(ValueError, "comment pagination limit reached"),
        ):
            state.list_ledger_receipts("example/repo", "token")
        self.assertEqual(github.call_count, 2)

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

    def test_resolver_preserves_older_ambiguous_rejection(self) -> None:
        rejected = self.receipt("submission_rejected")
        prepared = state.DispatchReceipt(
            **{
                **rejected.__dict__,
                "receipt_id": "receipt-2",
                "created_at": (datetime.now(UTC) + timedelta(seconds=1)).isoformat(),
                "receipt_state": "pre_submit_failed",
            }
        )
        with mock.patch.object(
            state,
            "list_ledger_receipts",
            return_value=[rejected, prepared],
        ):
            self.assertEqual(
                state.resolve_authoritative_receipt("example/repo", "token", self.identity),
                rejected,
            )

    def test_incident_deadline_keeps_minimum_bounded_write_window(self) -> None:
        self.assertEqual(state._bounded_incident_deadline(0, monotonic=lambda: 100), 110)
        self.assertEqual(state._bounded_incident_deadline(25, monotonic=lambda: 100), 125)

    def test_missing_status_contract_fails_visibly(self) -> None:
        result = state.monitor_terminal_outcome(self.receipt(), "", "secret")
        self.assertEqual(
            (result.success, result.stage, result.state), (False, "status_contract", "unavailable")
        )

    def test_status_endpoint_rejects_non_loopback_http_before_sending_key(self) -> None:
        with (
            mock.patch.object(state.request, "urlopen") as urlopen,
            self.assertRaisesRegex(
                state.TerminalEvidenceError,
                "HTTP only for loopback",
            ),
        ):
            state.fetch_terminal_status(
                "http://example.invalid/status",
                "secret",
                self.identity,
                "job-1",
                "correlation-1",
                10,
            )
        urlopen.assert_not_called()

    def test_status_endpoint_rejects_non_2xx_before_parsing_success_payload(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.status = 500
        response.__enter__.return_value.getcode.return_value = 500
        response.__enter__.return_value.read.return_value = json.dumps(
            {
                "schema_version": state.STATUS_SCHEMA_VERSION_V1,
                "identity": self.identity.as_dict(),
                "job_id": "job-1",
                "correlation_id": "correlation-1",
                "synthesis": {"state": "succeeded"},
                "video": {"state": "succeeded"},
                "provider": {"state": "published", "external_verified": True},
            }
        ).encode()
        with (
            mock.patch.object(state.request, "urlopen", return_value=response),
            self.assertRaisesRegex(OSError, "HTTP 500"),
        ):
            state.fetch_terminal_status(
                "https://example.invalid/status",
                "secret",
                self.identity,
                "job-1",
                "correlation-1",
                10,
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

    def test_incident_creation_race_closes_losing_duplicate(self) -> None:
        key = state.incident_key(self.identity, "provider", "timeout")
        marker = f"{state.INCIDENT_MARKER_PREFIX}{key} -->"
        canonical = {
            "number": 7,
            "html_url": "https://github.com/example/repo/issues/7",
            "body": marker,
        }
        created = {
            "number": 8,
            "html_url": "https://github.com/example/repo/issues/8",
            "body": marker,
        }
        with (
            mock.patch.object(
                state,
                "_iter_issue_pages",
                side_effect=[iter([]), iter([created, canonical])],
            ),
            mock.patch.object(
                state,
                "_github_json",
                side_effect=[created, {}, {}],
            ) as github,
        ):
            url = state.upsert_incident(
                "example/repo",
                "token",
                self.identity,
                "provider",
                "timeout",
                {"job_id": "job-1"},
            )
        self.assertEqual(url, canonical["html_url"])
        self.assertIn("/issues/8/comments", github.call_args_list[1].args[0])
        self.assertEqual(
            github.call_args_list[2].kwargs["payload"],
            {"state": "closed", "state_reason": "not_planned"},
        )

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

    def test_incident_upsert_closes_concurrent_duplicate_after_create(self) -> None:
        key = state.incident_key(self.identity, "provider", "timeout")
        canonical = {
            "number": 7,
            "html_url": "https://github.com/example/repo/issues/7",
            "body": f"{state.INCIDENT_MARKER_PREFIX}{key} -->",
        }
        created = {
            "number": 8,
            "html_url": "https://github.com/example/repo/issues/8",
            "body": f"{state.INCIDENT_MARKER_PREFIX}{key} -->",
        }
        with (
            mock.patch.object(
                state,
                "_iter_issue_pages",
                side_effect=[iter([]), iter([canonical, created])],
            ),
            mock.patch.object(state, "_github_json", side_effect=[created, {}, {}]) as github,
        ):
            url = state.upsert_incident(
                "example/repo", "token", self.identity, "provider", "timeout", {"job_id": "job-1"}
            )
        self.assertEqual(url, canonical["html_url"])
        self.assertEqual(github.call_count, 3)
        self.assertIn("/issues/8/comments", github.call_args_list[1].args[0])
        self.assertEqual(github.call_args_list[2].kwargs["method"], "PATCH")
        self.assertEqual(
            github.call_args_list[2].kwargs["payload"],
            {"state": "closed", "state_reason": "not_planned"},
        )

    def test_incident_reconciliation_requires_incident_marker(self) -> None:
        identity_marker = f"* Identity key: `{state.canonical_identity_key(self.identity)}`"
        unrelated = {"number": 7, "body": identity_marker}
        incident = {
            "number": 8,
            "body": f"{state.INCIDENT_MARKER_PREFIX}key -->\n{identity_marker}",
        }
        with (
            mock.patch.object(
                state,
                "_iter_issue_pages",
                return_value=iter([unrelated, incident]),
            ),
            mock.patch.object(state, "_github_json", return_value={}) as github,
        ):
            state.reconcile_identity_incidents("example/repo", "token", self.identity)
        self.assertEqual(github.call_count, 2)
        self.assertTrue(all("/issues/8" in call.args[0] for call in github.call_args_list))


if __name__ == "__main__":
    unittest.main()

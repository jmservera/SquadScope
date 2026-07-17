import unittest

from scripts.rerun_modes import validate_modes


class RerunModeTests(unittest.TestCase):
    def test_normal_mode_allows_guarded_publish_and_reuse_default(self) -> None:
        decision = validate_modes(run_mode="normal", source_refresh_policy="reuse-same-day")

        self.assertFalse(decision.reasons)
        self.assertTrue(decision.publish_allowed)
        self.assertTrue(decision.crawl_allowed)
        self.assertIn("normal guarded", decision.action)

    def test_rebuild_week_requires_explicit_restore_mode(self) -> None:
        decision = validate_modes(
            run_mode="normal",
            source_refresh_policy="reuse-same-day",
            rebuild_week="2026-W21",
        )

        self.assertIn("requires run_mode=restore", decision.reasons[0])

    def test_restore_requires_source_run_id(self) -> None:
        decision = validate_modes(
            run_mode="restore",
            source_refresh_policy="reuse-same-day",
            rebuild_week="2026-W21",
        )

        self.assertTrue(any("requires source_run_id" in reason for reason in decision.reasons))

    def test_restore_accepts_source_bound_week(self) -> None:
        decision = validate_modes(
            run_mode="restore",
            source_refresh_policy="reuse-same-day",
            rebuild_week="2026-W21",
            source_run_id="26753498571",
        )

        self.assertFalse(decision.reasons)
        self.assertFalse(decision.crawl_allowed)
        self.assertTrue(decision.publish_allowed)

    def test_source_run_id_is_restore_only(self) -> None:
        decision = validate_modes(
            run_mode="normal",
            source_refresh_policy="reuse-same-day",
            source_run_id="26753498571",
        )

        self.assertTrue(
            any("only allowed with run_mode=restore" in reason for reason in decision.reasons)
        )

    def test_dry_run_cannot_publish_release(self) -> None:
        decision = validate_modes(
            run_mode="dry-run",
            source_refresh_policy="reuse-same-day",
            publish_release=True,
        )

        self.assertFalse(decision.publish_allowed)
        self.assertTrue(any("publish_release" in reason for reason in decision.reasons))

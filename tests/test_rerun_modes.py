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

    def test_dry_run_cannot_publish_release(self) -> None:
        decision = validate_modes(
            run_mode="dry-run",
            source_refresh_policy="reuse-same-day",
            publish_release=True,
        )

        self.assertFalse(decision.publish_allowed)
        self.assertTrue(any("publish_release" in reason for reason in decision.reasons))

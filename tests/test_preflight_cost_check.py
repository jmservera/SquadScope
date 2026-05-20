import tempfile
import unittest
from pathlib import Path

import scripts.preflight_cost_check as preflight


class PreflightCostCheckTests(unittest.TestCase):
    def _make_file(self, base: Path, name: str, size: int) -> Path:
        p = base / name
        p.write_text("x" * size, encoding="utf-8")
        return p

    def test_passes_under_cap(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            f1 = self._make_file(base, "small.json", 400)
            rc = preflight.main(["--context-files", str(f1)])
            self.assertEqual(rc, 0)

    def test_fails_over_cap(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            # 2M chars → 500k tokens; at $3/M input that's $1.50 — over cap
            f1 = self._make_file(base, "huge.json", 2_000_000)
            rc = preflight.main(["--context-files", str(f1)])
            self.assertEqual(rc, 1)

    def test_custom_cap(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            f1 = self._make_file(base, "medium.json", 40_000)
            # 40k chars → 10k tokens; at $3/M input = $0.03; cap $0.01 should fail
            rc = preflight.main(["--context-files", str(f1), "--hard-cap", "0.01"])
            self.assertEqual(rc, 1)

    def test_unknown_model_fails(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            f1 = self._make_file(base, "a.json", 100)
            rc = preflight.main(["--context-files", str(f1), "--model", "unknown-model"])
            self.assertEqual(rc, 1)

    def test_multiple_files_summed(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            f1 = self._make_file(base, "a.json", 200)
            f2 = self._make_file(base, "b.json", 200)
            tokens = preflight.estimate_input_tokens([f1, f2])
            self.assertEqual(tokens, 100)  # 400 chars / 4 = 100 tokens

    def test_missing_file_counts_zero(self) -> None:
        tokens = preflight.estimate_input_tokens([Path("/nonexistent/path.json")])
        self.assertEqual(tokens, 0)


if __name__ == "__main__":
    unittest.main()

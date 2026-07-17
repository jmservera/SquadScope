import json
import tempfile
import unittest
from pathlib import Path

from scripts import publish_safety


class PublishSafetyTests(unittest.TestCase):
    def write_manifest(self, root: Path) -> Path:
        manifest = root / "data/candidates/2026-W23/99/publish-manifest.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": "publish_eligibility_v1",
                    "candidate": {"summary_sha256": "candidate-sha"},
                    "source_artifacts": [{"path": "data/raw/2026-W23.json", "sha256": "raw-sha"}],
                    "analysis": {"source": "copilot-cli"},
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def test_backup_existing_is_immutable_and_restorable_with_provenance(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            root = Path(tmpdir)
            target = root / "content/weekly/2026/W23.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("known good article\n", encoding="utf-8")
            transaction_manifest = root / "data/published/2026-W23/promotion-manifest.json"
            transaction_manifest.parent.mkdir(parents=True, exist_ok=True)
            transaction_manifest.write_text(
                '{"schema_version":"promotion_transaction_v1","transaction_id":"old"}\n',
                encoding="utf-8",
            )
            source = root / "data/raw/2026-W23.json"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text('{"week":"2026-W23"}\n', encoding="utf-8")
            self.write_manifest(root)

            exit_code = publish_safety.main(
                [
                    "backup-existing",
                    "--root",
                    str(root),
                    "--week",
                    "2026-W23",
                    "--run-id",
                    "99",
                    "--kind",
                    "content",
                    "--manifest",
                    "data/candidates/2026-W23/99/publish-manifest.json",
                    "--expected-publish-ref",
                    "abc",
                    "--actual-publish-ref",
                    "abc",
                    "--path",
                    "content/weekly/2026/W23.md",
                    "--path",
                    "data/published/2026-W23/promotion-manifest.json",
                ]
            )

            self.assertEqual(exit_code, 0)
            backup_manifest = root / "data/backups/2026-W23/99/content/manifest.json"
            payload = json.loads(backup_manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "publish_backup_v1")
            self.assertEqual(payload["publish_ref"]["expected"], "abc")
            self.assertEqual(payload["source_manifest"]["source_artifacts"][0]["sha256"], "raw-sha")
            self.assertRegex(payload["files"][0]["sha256"], r"^[0-9a-f]{64}$")
            backed_up_paths = {entry["path"] for entry in payload["files"]}
            self.assertIn("content/weekly/2026/W23.md", backed_up_paths)
            self.assertIn("data/published/2026-W23/promotion-manifest.json", backed_up_paths)

            with self.assertRaises(SystemExit):
                publish_safety.main(
                    [
                        "backup-existing",
                        "--root",
                        str(root),
                        "--week",
                        "2026-W23",
                        "--run-id",
                        "99",
                        "--kind",
                        "content",
                        "--manifest",
                        "data/candidates/2026-W23/99/publish-manifest.json",
                        "--path",
                        "content/weekly/2026/W23.md",
                    ]
                )

            target.write_text("bad replacement\n", encoding="utf-8")
            transaction_manifest.write_text(
                '{"schema_version":"promotion_transaction_v1","transaction_id":"new"}\n',
                encoding="utf-8",
            )
            self.assertEqual(
                publish_safety.main(
                    [
                        "restore-backup",
                        "--root",
                        str(root),
                        "--backup-manifest",
                        str(backup_manifest),
                    ]
                ),
                0,
            )
            self.assertEqual(target.read_text(encoding="utf-8"), "known good article\n")
            restored_transaction = json.loads(transaction_manifest.read_text(encoding="utf-8"))
            self.assertEqual(restored_transaction["transaction_id"], "old")

    def test_backup_existing_requires_loadable_publish_manifest(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            root = Path(tmpdir)
            target = root / "content/weekly/2026/W23.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("known good article\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                publish_safety.main(
                    [
                        "backup-existing",
                        "--root",
                        str(root),
                        "--week",
                        "2026-W23",
                        "--run-id",
                        "99",
                        "--kind",
                        "content",
                        "--manifest",
                        "data/candidates/2026-W23/99/publish-manifest.json",
                        "--path",
                        "content/weekly/2026/W23.md",
                    ]
                )
            self.assertFalse((root / "data/backups").exists())

            malformed_manifest = root / "data/candidates/2026-W23/99/publish-manifest.json"
            malformed_manifest.parent.mkdir(parents=True, exist_ok=True)
            malformed_manifest.write_text("{not json", encoding="utf-8")

            with self.assertRaises(SystemExit):
                publish_safety.main(
                    [
                        "backup-existing",
                        "--root",
                        str(root),
                        "--week",
                        "2026-W23",
                        "--run-id",
                        "99",
                        "--kind",
                        "content",
                        "--manifest",
                        "data/candidates/2026-W23/99/publish-manifest.json",
                        "--path",
                        "content/weekly/2026/W23.md",
                    ]
                )
            self.assertFalse((root / "data/backups").exists())

    def test_backup_existing_rejects_non_file_targets(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            root = Path(tmpdir)
            self.write_manifest(root)
            target_dir = root / "content/weekly/2026"
            target_dir.mkdir(parents=True, exist_ok=True)

            with self.assertRaises(SystemExit):
                publish_safety.main(
                    [
                        "backup-existing",
                        "--root",
                        str(root),
                        "--week",
                        "2026-W23",
                        "--run-id",
                        "99",
                        "--kind",
                        "content",
                        "--manifest",
                        "data/candidates/2026-W23/99/publish-manifest.json",
                        "--path",
                        "content/weekly/2026",
                    ]
                )
            self.assertFalse((root / "data/backups").exists())

    def test_restore_backup_rejects_manifest_outside_root(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            root = Path(tmpdir)
            outside_manifest = root.parent / f"{root.name}-outside-manifest.json"
            outside_manifest.write_text(
                '{"schema_version":"publish_backup_v1","files":[]}\n', encoding="utf-8"
            )
            try:
                with self.assertRaises(SystemExit):
                    publish_safety.main(
                        [
                            "restore-backup",
                            "--root",
                            str(root),
                            "--backup-manifest",
                            str(outside_manifest),
                        ]
                    )
                with self.assertRaises(SystemExit):
                    publish_safety.main(
                        [
                            "restore-backup",
                            "--root",
                            str(root),
                            "--backup-manifest",
                            "../outside-manifest.json",
                        ]
                    )
            finally:
                outside_manifest.unlink(missing_ok=True)

    def test_raw_store_is_immutable_and_restore_is_hash_verified(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            root = Path(tmpdir)
            raw = root / "data/raw/2026-W23.json"
            raw.parent.mkdir(parents=True, exist_ok=True)
            original_raw = b'{"week":"2026-W23","evidence":"original"}\n'
            raw.write_bytes(original_raw)

            self.assertEqual(
                publish_safety.main(
                    [
                        "store-raw",
                        "--root",
                        str(root),
                        "--week",
                        "2026-W23",
                        "--source-run-id",
                        "26753498571",
                        "--source-artifact-id",
                        "7330965888",
                        "--source-head-sha",
                        "abc123",
                        "--path",
                        "data/raw/2026-W23.json",
                    ]
                ),
                0,
            )
            store = root / "data/raw-store/2026-W23/26753498571"
            manifest = json.loads((store / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], "raw_store_v1")
            self.assertEqual(manifest["source_run_id"], "26753498571")
            self.assertEqual(manifest["source_artifact"]["id"], "7330965888")
            self.assertEqual(manifest["source_artifact"]["retention_days"], 90)
            self.assertEqual(manifest["files"][0]["original_path"], "data/raw/2026-W23.json")
            original_store_bytes = {
                path.relative_to(store): path.read_bytes()
                for path in store.rglob("*")
                if path.is_file()
            }

            raw.write_bytes(b"replacement that must not enter immutable storage\n")
            with self.assertRaisesRegex(SystemExit, "Refusing to overwrite immutable raw store"):
                publish_safety.main(
                    [
                        "store-raw",
                        "--root",
                        str(root),
                        "--week",
                        "2026-W23",
                        "--source-run-id",
                        "26753498571",
                        "--source-artifact-id",
                        "7330965888",
                        "--source-head-sha",
                        "abc123",
                        "--path",
                        "data/raw/2026-W23.json",
                    ]
                )
            self.assertEqual(
                original_store_bytes,
                {
                    path.relative_to(store): path.read_bytes()
                    for path in store.rglob("*")
                    if path.is_file()
                },
            )

            stale_optional = raw.parent / "2026-W23-external-news.json"
            stale_optional.write_bytes(b"stale evidence from a different source run\n")
            self.assertEqual(
                publish_safety.main(
                    [
                        "restore-raw",
                        "--root",
                        str(root),
                        "--week",
                        "2026-W23",
                        "--source-run-id",
                        "26753498571",
                    ]
                ),
                0,
            )
            self.assertEqual(raw.read_bytes(), original_raw)
            self.assertFalse(stale_optional.exists())

            stored_raw = store / "files/data/raw/2026-W23.json"
            stored_raw.write_bytes(b"X" * len(original_raw))
            raw.write_bytes(b"accepted input must remain unchanged\n")
            stale_on_failure = raw.parent / "2026-W23-techcrunch.json"
            stale_on_failure.write_bytes(b"also unchanged when stored verification fails\n")
            with self.assertRaisesRegex(SystemExit, "checksum mismatch"):
                publish_safety.main(
                    [
                        "restore-raw",
                        "--root",
                        str(root),
                        "--week",
                        "2026-W23",
                        "--source-run-id",
                        "26753498571",
                    ]
                )
            self.assertEqual(raw.read_bytes(), b"accepted input must remain unchanged\n")
            self.assertTrue(stale_on_failure.exists())


if __name__ == "__main__":
    unittest.main()

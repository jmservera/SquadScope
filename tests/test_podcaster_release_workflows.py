"""Execute reviewed workflow bodies against the real CLI and local-only boundaries."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WEEK = "2026-W44"
RUN_ID = "40269058395"
ARTICLE_PATH = "content/weekly/2026/W44.md"
ARTICLE_URL = "https://claracle.com/weekly/2026/w44/"
MANIFEST_PATH = f"data/candidates/{WEEK}/{RUN_ID}/publish-manifest.json"
ARTICLE = b"---\ntitle: W44 release\nsummary: Verified weekly news.\n---\n# W44\n\nWeekly news.\n"
WRAPPERS = ("automatic", "manual")

GIT_STUB = """
import json
import sys
from pathlib import Path

root = Path.cwd()
args = sys.argv[1:]
with (root / "git-calls.jsonl").open("a") as log:
    log.write(json.dumps(args) + "\\n")
if (root / "git-failure").exists() and args[0] == (root / "git-failure").read_text():
    sys.exit(1)
if args == ["fetch", "origin", "publish", "--no-tags"]:
    pass
elif args == ["rev-parse", "HEAD"]:
    print("a" * 40)
elif args == ["ls-tree", "-r", "origin/publish", "--name-only"]:
    for path in sorted((root / "publish-fixture").rglob("publish-manifest.json")):
        print(path.relative_to(root / "publish-fixture").as_posix())
elif len(args) == 2 and args[0] == "show" and args[1].startswith("origin/publish:"):
    path = root / "publish-fixture" / args[1].split(":", 1)[1]
    if not path.is_file():
        sys.exit(1)
    sys.stdout.buffer.write(path.read_bytes())
else:
    sys.exit("Unexpected git call: " + repr(args))
"""


class ReleaseWorkspace:
    def __init__(self, root):
        self.root = root
        self.context = {
            "inputs.week": WEEK,
            "inputs.publish_run_id": RUN_ID,
            "inputs.breaking_news": "",
            "inputs.regenerate_of": "",
            "inputs.regeneration_reason": "",
            "inputs.observe_only == true && 'true'": "",
            "vars.PODCAST_AUTO_DISPATCH_PAUSED": "",
            "github.event.before": "",
            "github.event.workflow_run.head_sha": "",
            "github.run_id": "987654321",
            "vars.PODCASTER_ENDPOINT": "",
            "secrets.PODCASTER_API_KEY": "local-fixture-key",
        }
        self.steps = {}
        self.workflows = {}
        for wrapper, filename, job in (
            ("automatic", "auto-podcast-dispatch.yml", "real-generation"),
            ("manual", "trigger-podcast.yml", "trigger-podcast"),
        ):
            workflow = yaml.safe_load(
                (REPO_ROOT / ".github/workflows" / filename).read_text(encoding="utf-8")
            )
            self.workflows[wrapper] = workflow
            self.steps[wrapper] = {
                step["id"]: step for step in workflow["jobs"][job]["steps"] if "id" in step
            }
        scripts = root / "scripts"
        scripts.mkdir()
        for name in (
            "podcaster_handoff.py",
            "auto_dispatch_detect.py",
            "analysis_content_security.py",
            "podcast_dispatch_state.py",
        ):
            shutil.copyfile(REPO_ROOT / "scripts" / name, scripts / name)
        (root / "config").mkdir()
        shutil.copyfile(REPO_ROOT / "config/podcast.json", root / "config/podcast.json")
        self.bin = root / "bin"
        self.bin.mkdir()
        (self.bin / "python3").symlink_to(sys.executable)
        for name, body in (
            ("git", GIT_STUB),
            (
                "gh",
                'raise SystemExit("Unexpected gh call: release preparation is exact-path only")',
            ),
        ):
            executable = self.bin / name
            executable.write_text(f"#!{sys.executable}\n{body}\n", encoding="utf-8")
            executable.chmod(0o755)
        article = root / ARTICLE_PATH
        article.parent.mkdir(parents=True)
        article.write_bytes(ARTICLE)
        self.manifest = {
            "week": WEEK,
            "run_id": RUN_ID,
            "run_mode": "normal",
            "promotion_eligible": True,
            "analysis": {"ai_status": "ai", "preflight": {"publish_eligible": True}},
            "promotion": {"eligible": True, "decision": "promote"},
            "candidate": {
                "content_path": ARTICLE_PATH,
                "content_sha256": hashlib.sha256(ARTICLE).hexdigest(),
            },
        }
        self.write_manifest()

    def write_manifest(self, raw=None):
        path = self.root / "publish-fixture" / MANIFEST_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw if raw is not None else json.dumps(self.manifest).encode())
        self.context.update(
            {
                f"needs.detect.outputs.{key}": value
                for key, value in {
                    "week": WEEK,
                    "publish_run_id": RUN_ID,
                    "article_path": ARTICLE_PATH,
                    "article_url": ARTICLE_URL,
                    "manifest_path": MANIFEST_PATH,
                    "article_sha256": hashlib.sha256(ARTICLE).hexdigest(),
                    "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }.items()
            }
        )
        return path

    def run_step(self, wrapper, step_id):
        step = self.steps[wrapper][step_id]
        output_file = self.root / f"{wrapper}-{step_id}.outputs"
        output_file.write_text("", encoding="utf-8")
        # Do not inherit credentials, Python injection hooks, or provider configuration.
        env = {
            "PATH": f"{self.bin}:/usr/bin:/bin",
            "HOME": str(self.root),
            "TMPDIR": str(self.root),
            "GITHUB_OUTPUT": str(output_file),
            "NO_PROXY": "127.0.0.1,localhost",
        }
        for key, value in step.get("env", {}).items():
            if isinstance(value, str) and value.startswith("${{ "):
                expression = value[4:-3].removesuffix(" || ''")
                env[key] = self.context[expression]
            else:
                env[key] = value
        result = subprocess.run(
            ["bash", "-euo", "pipefail", "-c", step["run"]],
            cwd=self.root,
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        outputs = dict(
            line.split("=", 1) for line in output_file.read_text().splitlines() if "=" in line
        )
        self.context.update(
            {f"steps.{step_id}.outputs.{key}": value for key, value in outputs.items()}
        )
        return result, outputs

    def prepare(self, wrapper):
        result, outputs = self.run_step(wrapper, "derive")
        if result.returncode == 0:
            alias_result, aliases = self.run_step(wrapper, "manifest-locate")
            assert alias_result.returncode == 0, alias_result.stdout + alias_result.stderr
            assert aliases == {
                key: outputs[key]
                for key in ("manifest_path", "manifest_sha256", "article_sha256", "publish_run_id")
            }
        return result, outputs

    def git_calls(self):
        path = self.root / "git-calls.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


@pytest.fixture
def release():
    with tempfile.TemporaryDirectory(
        prefix="release-workflow-", dir=REPO_ROOT / "tests"
    ) as directory:
        yield ReleaseWorkspace(Path(directory))


@pytest.fixture
def receiver(release):
    received = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            received.append(
                (
                    self.path,
                    self.headers.get("x-podcaster-api-key"),
                    json.loads(self.rfile.read(int(self.headers["Content-Length"]))),
                )
            )
            body = b'{"job_id":"podcast-local-fixture","status":"accepted"}'
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    release.context["vars.PODCASTER_ENDPOINT"] = f"http://127.0.0.1:{server.server_port}/handoff"
    try:
        yield received
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_real_wrappers_prepare_hydrate_and_dispatch_same_exact_release(release, receiver, wrapper):
    result, outputs = release.prepare(wrapper)
    assert result.returncode == 0, result.stdout + result.stderr
    assert outputs == {
        key.removeprefix("needs.detect.outputs."): value
        for key, value in release.context.items()
        if key.startswith("needs.detect.outputs.")
    }
    assert (release.root / MANIFEST_PATH).read_bytes() == (
        release.root / "publish-fixture" / MANIFEST_PATH
    ).read_bytes()
    assert release.git_calls() == [
        ["fetch", "origin", "publish", "--no-tags"],
        ["show", f"origin/publish:{MANIFEST_PATH}"],
    ]
    result, handoff_outputs = release.run_step(wrapper, "handoff")
    assert result.returncode == 0, result.stdout + result.stderr
    assert handoff_outputs["podcaster_receipt_state"] == "submitted"
    assert handoff_outputs["podcaster_job_id"] == "podcast-local-fixture"
    assert len(receiver) == 1
    path, key, payload = receiver[0]
    assert path == "/handoff"
    assert key == "local-fixture-key"
    for field in (
        "week",
        "publish_run_id",
        "article_path",
        "article_url",
        "article_sha256",
        "manifest_sha256",
    ):
        assert payload[field] == outputs[field]
    assert payload["publish_mode"] == "normal"
    assert payload["article_title"] == "W44 release"
    assert "Weekly news." in payload["article_content"]
    assert "dry_run" not in payload
    assert "regeneration" not in payload


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (("week",), "2026-W43", "manifest.week"),
        (("run_id",), "40269058396", "manifest.run_id"),
        (("run_mode",), "restore", "run_mode"),
        (("run_mode",), "unknown", "run_mode"),
        (("promotion_eligible",), False, "promotion_eligible"),
        (("analysis", "preflight", "publish_eligible"), False, "publish_eligible"),
        (("analysis", "ai_status"), "no-ai", "not eligible for Podcaster"),
        (("promotion", "eligible"), False, "not eligible for Podcaster"),
        (("promotion", "decision"), "reject", "not eligible for Podcaster"),
        (("candidate", "content_sha256"), "0" * 64, "SHA-256 mismatch"),
        (("candidate", "content_sha256"), None, "missing or invalid"),
        (("analysis",), [], "analysis must be a JSON object"),
        (("analysis", "preflight"), None, "analysis.preflight must be a JSON object"),
        (("candidate",), None, "candidate must be a JSON object"),
        (("promotion",), [], "promotion must be a JSON object"),
    ],
)
def test_real_wrappers_reject_ineligible_or_mismatched_manifest(
    release, wrapper, field, value, message
):
    target = release.manifest
    for key in field[:-1]:
        target = target[key]
    target[field[-1]] = value
    release.write_manifest()
    result, outputs = release.prepare(wrapper)
    assert result.returncode != 0
    assert message in result.stdout + result.stderr
    assert outputs == {}
    assert not (release.root / MANIFEST_PATH).exists()


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize("raw", [b"{", b"[]", b"null", b"\xff"])
def test_real_wrappers_reject_malformed_manifest_before_hydration(release, wrapper, raw):
    release.write_manifest(raw)
    result, outputs = release.prepare(wrapper)
    assert result.returncode != 0
    assert "Publish manifest must be" in result.stdout
    assert outputs == {}
    assert not (release.root / MANIFEST_PATH).exists()


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_real_wrappers_do_not_admit_audited_force_replace_outside_normal_mode(release, wrapper):
    release.manifest["run_mode"] = "restore"
    release.manifest["promotion"]["policy"] = "force-replace"
    release.manifest["audit"] = {"actor": "fixture-owner", "reason": "Correct article"}
    release.write_manifest()
    result, outputs = release.prepare(wrapper)
    assert result.returncode != 0
    assert "run_mode" in result.stdout
    assert outputs == {}
    assert not (release.root / MANIFEST_PATH).exists()


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("week", "2026-W44\ninvalid", "week must match"),
        ("week", "../../outside", "week must match"),
        ("publish_run_id", "latest", "numeric workflow run ID"),
        ("publish_run_id", "../40269058395", "numeric workflow run ID"),
    ],
)
def test_real_wrappers_reject_unsafe_identity_before_git(release, wrapper, field, value, message):
    for prefix in ("inputs.", "needs.detect.outputs."):
        release.context[prefix + field] = value
    result, outputs = release.prepare(wrapper)
    assert result.returncode != 0
    assert message in result.stdout
    assert outputs == {}
    assert release.git_calls() == []


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("article_path", "content/weekly/2026/W43.md", "article_path does not match"),
        ("article_path", "../outside.md", "article_path does not match"),
        ("article_url", "https://example.invalid/weekly/2026/w44/", "article_url does not match"),
        (
            "manifest_path",
            MANIFEST_PATH.replace(RUN_ID, "40269058396"),
            "manifest_path does not match",
        ),
        ("manifest_path", "../outside.json", "manifest_path does not match"),
        ("article_sha256", "BAD", "must be lowercase"),
        ("manifest_sha256", "A" * 64, "must be lowercase"),
        ("article_sha256", "0" * 64, "Merged article SHA-256"),
        ("manifest_sha256", "0" * 64, "Manifest SHA-256"),
    ],
)
def test_automatic_wrapper_rechecks_exact_detection_evidence(release, field, value, message):
    release.context["needs.detect.outputs." + field] = value
    result, outputs = release.prepare("automatic")
    assert result.returncode != 0
    assert message in result.stdout
    assert outputs == {}
    assert not (release.root / MANIFEST_PATH).exists()


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize(
    "failure", ["article_missing", "article_not_utf8", "fetch", "show", "hydrate"]
)
def test_real_wrappers_fail_closed_on_missing_article_lookup_or_hydration(
    release, wrapper, failure
):
    if failure == "article_missing":
        (release.root / ARTICLE_PATH).unlink()
    elif failure == "article_not_utf8":
        (release.root / ARTICLE_PATH).write_bytes(b"\xff")
    elif failure == "hydrate":
        (release.root / "data").write_text("not a directory")
    else:
        (release.root / "git-failure").write_text(failure)
    result, outputs = release.prepare(wrapper)
    assert result.returncode != 0
    assert "Release preparation failed" in result.stdout
    assert outputs == {}
    assert not (release.root / MANIFEST_PATH).exists()


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_real_wrappers_do_not_fall_back_to_another_run(release, wrapper):
    exact = release.root / "publish-fixture" / MANIFEST_PATH
    alternative = exact.parent.parent / "40269058396/publish-manifest.json"
    alternative.parent.mkdir()
    alternative.write_bytes(exact.read_bytes())
    exact.unlink()
    result, outputs = release.prepare(wrapper)
    assert result.returncode != 0
    assert "Could not retrieve the exact publish manifest" in result.stdout
    assert outputs == {}
    assert release.git_calls()[-1] == ["show", f"origin/publish:{MANIFEST_PATH}"]
    assert not (release.root / MANIFEST_PATH).exists()


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize("boundary", ["article", "manifest"])
def test_real_wrappers_reject_symlink_escape_without_touching_target(release, wrapper, boundary):
    # The target stays inside the test fixture, but outside the checked-out repository.
    checkout = release.root / "checkout"
    checkout.mkdir()
    for path in list(release.root.iterdir()):
        if path != checkout:
            path.rename(checkout / path.name)
    release.root = checkout
    release.bin = checkout / "bin"
    outside = checkout.parent / "outside"
    outside.mkdir()
    if boundary == "article":
        article = checkout / ARTICLE_PATH
        article.unlink()
        (outside / "article.md").write_bytes(ARTICLE)
        article.symlink_to(outside / "article.md")
    else:
        (checkout / "data").symlink_to(outside, target_is_directory=True)
    result, outputs = release.prepare(wrapper)
    assert result.returncode != 0
    assert "repository root" in result.stdout
    assert outputs == {}
    assert not (outside / "candidates").exists()
    if boundary == "article":
        assert (outside / "article.md").read_bytes() == ARTICLE


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize("mutation", ["missing", "changed"])
def test_actual_handoff_body_rechecks_merged_article_before_http(
    release, receiver, wrapper, mutation
):
    result, _ = release.prepare(wrapper)
    assert result.returncode == 0, result.stdout + result.stderr
    article = release.root / ARTICLE_PATH
    if mutation == "missing":
        article.unlink()
    else:
        article.write_bytes(ARTICLE + b"Different merged bytes.\n")
    result, outputs = release.run_step(wrapper, "handoff")
    assert result.returncode != 0
    assert outputs["podcaster_receipt_state"] == "pre_submit_failed"
    assert (
        "not present" in result.stdout
        if mutation == "missing"
        else "sha256 mismatch" in result.stdout
    )
    assert receiver == []


def test_actual_detection_wrapper_rejects_ambiguous_lookup_but_manual_selects_exact_run(release):
    second = release.root / "publish-fixture" / MANIFEST_PATH.replace(RUN_ID, "40269058396")
    second.parent.mkdir(parents=True)
    second.write_text(json.dumps({**release.manifest, "run_id": "40269058396"}))
    detection = next(
        step
        for step in release.workflows["automatic"]["jobs"]["detect"]["steps"]
        if step.get("id") == "detect"
    )
    release.steps["automatic"]["detect"] = detection
    result, outputs = release.run_step("automatic", "detect")
    assert result.returncode != 0
    assert "Ambiguous" in result.stderr
    assert outputs["eligible"] == "false"
    assert outputs["reason"] == "ambiguous_manifest"
    assert "publish_run_id" not in outputs
    assert not (release.root / MANIFEST_PATH).exists()
    result, outputs = release.prepare("manual")
    assert result.returncode == 0, result.stdout + result.stderr
    assert outputs["publish_run_id"] == RUN_ID


@pytest.mark.parametrize(
    ("news", "job", "reason"),
    [
        ('Important "news" with $dollars and unicode: café', "", ""),
        ("", "podcast-original_job.1", '  Correct narration: "voice" & pacing  '),
        (
            'Important "news" with $dollars and unicode: café',
            "podcast-original_job.1",
            '  Correct narration: "voice" & pacing  ',
        ),
    ],
)
def test_manual_regeneration_and_breaking_news_survive_actual_dispatch_wiring(
    release, receiver, news, job, reason
):
    release.context.update(
        {
            "inputs.breaking_news": news,
            "inputs.regenerate_of": job,
            "inputs.regeneration_reason": reason,
        }
    )
    result, _ = release.prepare("manual")
    assert result.returncode == 0, result.stdout + result.stderr
    result, _ = release.run_step("manual", "handoff")
    assert result.returncode == 0, result.stdout + result.stderr
    assert len(receiver) == 1
    payload = receiver[0][2]
    if news:
        assert payload["breaking_news"] == news
    else:
        assert "breaking_news" not in payload
    if job:
        assert payload["regeneration"] == {
            "supersedes_job_id": job,
            "reason": reason.strip(),
        }
    else:
        assert "regeneration" not in payload
    assert payload["publish_run_id"] == RUN_ID
    assert payload["article_sha256"] == hashlib.sha256(ARTICLE).hexdigest()


@pytest.mark.parametrize(
    ("job", "reason", "news"),
    [
        ("podcast-original", "", ""),
        ("", "Correct voice", ""),
        ("podcast-original", "   ", ""),
        ("not-a-podcast-job", "Correct voice", ""),
        ("podcast-original", "Correct\nvoice", ""),
        ("podcast-original", "x" * 501, ""),
        ("", "", "x" * 501),
        ("", "", "Injected\nnews"),
    ],
)
def test_manual_wrapper_rejects_invalid_regeneration_and_news_before_lookup(
    release, job, reason, news
):
    release.context.update(
        {
            "inputs.regenerate_of": job,
            "inputs.regeneration_reason": reason,
            "inputs.breaking_news": news,
        }
    )
    result, outputs = release.prepare("manual")
    assert result.returncode != 0
    assert "Release preparation failed" in result.stdout
    assert outputs == {}
    assert release.git_calls() == []

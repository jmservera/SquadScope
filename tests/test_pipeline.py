import io
import json
import tempfile
import unittest
from argparse import Namespace
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

import yaml

import scripts.analysis_gate as analysis_gate
import scripts.analyze_fallback as analyze_fallback
import scripts.crawl as crawl
import scripts.generate_content as generate_content
import scripts.podcaster_handoff as podcaster_handoff


def _uses_action(step: dict, action: str) -> bool:
    """Return True if a step uses ``action``, ignoring the version/SHA ref.

    Tolerates SHA-pinned references such as
    ``actions/download-artifact@<40-hex-sha> # v4`` by comparing only the
    ``owner/repo`` portion before the ``@``.
    """
    uses = step.get("uses")
    if not isinstance(uses, str):
        return False
    return uses.split("@", 1)[0] == action


def _checkout_steps(workflow: dict) -> list[dict]:
    return [
        step
        for job in workflow.get("jobs", {}).values()
        for step in job.get("steps", [])
        if _uses_action(step, "actions/checkout")
    ]


class WorkflowSecurityTests(unittest.TestCase):
    def test_zizmor_uses_pinned_full_workflow_scope(self) -> None:
        workflow = yaml.safe_load(
            Path(".github/workflows/security-scanning.yml").read_text(encoding="utf-8")
        )
        scan_step = next(
            step
            for step in workflow["jobs"]["zizmor-scan"]["steps"]
            if step.get("name") == "Run zizmor security scan"
        )

        self.assertEqual(scan_step["with"]["inputs"], ".github/workflows/")
        self.assertEqual(scan_step["with"]["version"], "1.27.0")
        self.assertEqual(scan_step["with"]["min-severity"], "medium")
        self.assertFalse(scan_step["with"]["advanced-security"])

    def test_squad_checkouts_do_not_persist_credentials(self) -> None:
        workflow_paths = sorted(Path(".github/workflows").glob("squad-*.yml"))
        workflow_paths.append(Path(".github/workflows/sync-squad-labels.yml"))

        for workflow_path in workflow_paths:
            with self.subTest(workflow=workflow_path.name):
                workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
                checkouts = _checkout_steps(workflow)
                self.assertTrue(checkouts)
                for checkout in checkouts:
                    self.assertFalse(checkout.get("with", {}).get("persist-credentials"))
                    self.assertNotIn("token", checkout.get("with", {}))

    def test_squad_promote_scopes_write_and_push_authentication(self) -> None:
        workflow = yaml.safe_load(
            Path(".github/workflows/squad-promote.yml").read_text(encoding="utf-8")
        )

        self.assertEqual(workflow["permissions"], {})
        for job in workflow["jobs"].values():
            self.assertEqual(job["permissions"], {"contents": "write"})
            push_step = next(step for step in job["steps"] if "git push " in step.get("run", ""))
            self.assertEqual(push_step["env"]["GH_TOKEN"], "${{ github.token }}")
            self.assertIn("https://x-access-token:${GH_TOKEN}@github.com/", push_step["run"])

    def test_copilot_cli_install_is_pinned(self) -> None:
        workflow = yaml.safe_load(
            Path(".github/workflows/crawl-and-publish.yml").read_text(encoding="utf-8")
        )
        install_step = next(
            step
            for step in workflow["jobs"]["analyze"]["steps"]
            if step.get("name") == "Install Copilot CLI"
        )

        self.assertIn("npm install -g @github/copilot@1.0.76", install_step["run"])
        self.assertNotIn("npm install -g @github/copilot\n", install_step["run"])


class _FakeHTTPResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


FIXED_RUN_DATETIME = "2026-05-18T08:00:00Z"
FIXED_RUN_TIME = datetime(2026, 5, 18, 8, 0, 0, tzinfo=UTC)


def make_api_repo(full_name: str, *, stars: int, created_at: str, topics: list[str]) -> dict:
    owner, name = full_name.split("/", 1)
    return {
        "name": name,
        "full_name": full_name,
        "description": f"{name} helps teams ship reliable automation.",
        "language": "Python",
        "stargazers_count": stars,
        "forks_count": max(1, stars // 10),
        "created_at": created_at,
        "topics": topics,
        "license": {"spdx_id": "MIT"},
        "html_url": f"https://github.com/{full_name}",
        "owner": {"login": owner},
        "fork": False,
        "is_template": False,
    }


def make_raw_payload() -> dict:
    return {
        "week": "2026-W21",
        "crawled_at": FIXED_RUN_DATETIME,
        "new_repos": [
            {
                "name": "signal-kit",
                "owner": "octo",
                "full_name": "octo/signal-kit",
                "description": "Signal extraction for release teams.",
                "language": "Python",
                "stars": 120,
                "forks": 12,
                "created_at": "2026-05-12T09:00:00Z",
                "topics": ["ai", "automation", "developer-tooling"],
                "license": "MIT",
                "url": "https://github.com/octo/signal-kit",
            }
        ],
        "trending_repos": [
            {
                "name": "momentum-watch",
                "owner": "octo",
                "full_name": "octo/momentum-watch",
                "description": "Observability for weekly launches.",
                "language": "Go",
                "stars": 180,
                "forks": 18,
                "created_at": "2026-05-10T12:00:00Z",
                "topics": ["observability", "analytics", "platform"],
                "license": "Apache-2.0",
                "url": "https://github.com/octo/momentum-watch",
                "stars_gained": 35,
            }
        ],
        "signals": {
            "top_topics": [
                {"topic": "automation", "count": 2},
                {"topic": "observability", "count": 1},
            ]
        },
        "metadata": {
            "api_calls_used": 2,
            "cache_hits": 1,
            "stale_cache_hits": 0,
            "rate_limit_limit": 5000,
            "rate_limit_remaining": 4990,
            "rate_limit_reset": 1747567200,
            "rate_limit_resource": "search",
            "partial_failures": [],
            "snapshot_path": "data/snapshots/2026-W21-stars.json",
        },
    }


def make_analysis_markdown() -> str:
    return f"""---
title: "Reliable Automation Gains Ground"
date: {FIXED_RUN_DATETIME}
week: "2026-W21"
year: 2026
tags: [ai, automation, developer-tooling]
categories: [weekly]
repos_featured: 2
stars_tracked: 300
top_repo: "octo/signal-kit"
quality_score: 86
summary: "Reliable automation and observability projects set the tone for the week."
---

## This Week's Trends

**Operational Automation**: Teams are investing in tools that reduce coordination overhead and improve release confidence. [octo/signal-kit](https://github.com/octo/signal-kit) exemplifies this — it solves release coordination without pretending to be a full platform rewrite. The project packages practical automation, readable defaults, and evidence of disciplined engineering.

**Observability as Infrastructure**: [octo/momentum-watch](https://github.com/octo/momentum-watch) captured attention because the work is grounded in run health and measurement rather than novelty claims. The trend matters because more teams are prioritizing incident feedback loops and durable visibility into developer workflows.

## Where Industry Meets Code

Developer activity aligned with broader industry interest in automation and observability tooling this week. Both [octo/signal-kit](https://github.com/octo/signal-kit) and [octo/momentum-watch](https://github.com/octo/momentum-watch) represent categories where press coverage and developer investment point in the same direction. The more interesting divergence is what the press is not covering: the quiet growth of practical pipeline tooling that makes releases safer without requiring major architectural changes. This type of grounded infrastructure work rarely earns headlines, but this week's developer activity suggests it is where real adoption is happening.

## Signal & Noise

The durable signal this week is a return to automation that lowers toil and gives teams more confidence in repeatable delivery. [octo/signal-kit](https://github.com/octo/signal-kit) and [octo/momentum-watch](https://github.com/octo/momentum-watch) both point toward software that reduces coordination overhead, improves trust in pipelines, and respects how operators actually work. That pattern is more convincing than broad claims about agents replacing engineering judgment.

The noise is the usual rush of products that market autonomy without proving fit, maintenance discipline, or measurable outcomes. This week was healthier than most, but the broader ecosystem still produces wrappers that borrow the language of automation while skipping the hard parts of observability, testing, and operational ownership.

## Blind Spots

The biggest blind spot is stronger investment in security review, test ergonomics, and smaller-team operations tooling that can be adopted without a platform migration. The ecosystem is getting better at coordination, but it still underserves practical defensive tooling and deployment confidence for teams that need reliability before they need spectacle. Neither press nor developer communities are giving this the attention it deserves.

## The Week Ahead

Practical automation won attention on merit this week. If this pattern holds, the next wave of winners will be tools that save teams time, expose real operating signals, and make release quality easier to trust. Watch for observability and pipeline safety tooling to continue gaining ground.

## Key References

### Notable Projects

- [octo/signal-kit](https://github.com/octo/signal-kit) — release coordination automation with practical defaults and disciplined engineering.
- [octo/momentum-watch](https://github.com/octo/momentum-watch) — observability tooling grounded in run health rather than vanity metrics.

### Press & Industry

No press data was provided this week.
"""


class WorkflowConfigTests(unittest.TestCase):
    def test_hugo_install_steps_use_release_urls_and_resilient_retries(self) -> None:
        expected_retry_flags = "--retry 10 --retry-delay 5 --retry-max-time 300 --retry-all-errors"

        for workflow_file in (
            ".github/workflows/deploy-site.yml",
            ".github/workflows/crawl-and-publish.yml",
        ):
            workflow_path = Path(workflow_file)
            workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

            install_step = next(
                (
                    step
                    for job in workflow["jobs"].values()
                    for step in job.get("steps", [])
                    if step.get("name") == "Install Hugo"
                ),
                None,
            )
            self.assertIsNotNone(install_step, f"Install Hugo step not found in {workflow_file}")
            install_run = install_step["run"]
            self.assertIn(
                'RELEASE_URL="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}"',
                install_run,
            )
            self.assertIn('TARBALL="hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz"', install_run)
            self.assertIn('CHECKSUM_FILE="hugo_${HUGO_VERSION}_checksums.txt"', install_run)
            self.assertEqual(install_run.count(expected_retry_flags), 2)

    def test_deploy_workflow_maps_analytics_and_gsc_secrets_to_hugo_params(self) -> None:
        workflow_path = Path(".github/workflows/deploy-site.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        env = workflow["jobs"]["build"]["env"]
        self.assertEqual(env["HUGO_PARAMS_GA_MEASUREMENT_ID"], "${{ secrets.GA_MEASUREMENT_ID }}")
        self.assertEqual(
            env["HUGO_PARAMS_GSC_SITE_VERIFICATION"],
            "${{ secrets.GSC_SITE_VERIFICATION }}",
        )

    def test_production_browser_gate_is_blocking_and_chromium_aligned(self) -> None:
        workflow = yaml.safe_load(Path(".github/workflows/ci.yml").read_text(encoding="utf-8"))
        production = workflow["jobs"]["production-site"]
        self.assertEqual(
            production["env"]["HUGO_PARAMS_GA_MEASUREMENT_ID"],
            "G-TEST-OBSERVATORY",
        )

        steps = production["steps"]
        install = next(
            step for step in steps if step.get("name") == "Install production test dependencies"
        )
        self.assertIn("playwright install --with-deps chromium", install["run"])
        browser_index = next(
            index
            for index, step in enumerate(steps)
            if step.get("name") == "Run axe and responsive browser gates"
        )
        lighthouse_index = next(
            index for index, step in enumerate(steps) if step.get("name") == "Run Lighthouse gates"
        )
        browser_command = steps[browser_index]["run"]
        for spec in (
            "tests/visual/a11y-perf.spec.mjs",
            "tests/visual/observatory-a11y.spec.mjs",
            "tests/visual/observatory-analytics.spec.mjs",
        ):
            self.assertIn(spec, browser_command)
        self.assertLess(browser_index, lighthouse_index)

        config = Path("tests/visual/playwright.config.mjs").read_text(encoding="utf-8")
        self.assertEqual(config.count("devices['Desktop Chrome']"), 2)
        self.assertEqual(config.count("devices['Pixel 5']"), 2)
        self.assertNotIn("iPhone", config)
        self.assertNotIn("webkit", config.lower())

    def test_deploy_invokes_exact_promoted_article_smoke_after_pages(self) -> None:
        workflow = yaml.safe_load(
            Path(".github/workflows/deploy-site.yml").read_text(encoding="utf-8")
        )

        build = workflow["jobs"]["build"]
        resolve_step = next(
            step
            for step in build["steps"]
            if step.get("name") == "Resolve promoted Podcaster release"
        )
        resolve_script = resolve_step["run"]
        self.assertIn('Path("data/published").glob("*/promotion-manifest.json")', resolve_script)
        self.assertIn('record.get("schema_version") != "promotion_transaction_v1"', resolve_script)
        self.assertIn('artifact.get("role") == "hugo_content"', resolve_script)
        self.assertIn("hashlib.sha256(article_path.read_bytes()).hexdigest()", resolve_script)
        self.assertIn('article_sha256 != article.get("sha256")', resolve_script)
        self.assertIn(
            'article_url_from_page_path("https://claracle.com/", article_path.as_posix())',
            resolve_script,
        )

        smoke = workflow["jobs"]["podcaster-release-smoke"]
        self.assertEqual(smoke["needs"], ["build", "deploy"])
        self.assertEqual(smoke["uses"], "./.github/workflows/podcaster-handoff-smoke.yml")
        self.assertEqual(smoke["permissions"], {"contents": "read"})
        self.assertEqual(
            smoke["secrets"], {"PODCASTER_API_KEY": "${{ secrets.PODCASTER_API_KEY }}"}
        )
        self.assertEqual(
            smoke["with"],
            {
                "week": "${{ needs.build.outputs.smoke_week }}",
                "article_url": "${{ needs.build.outputs.smoke_article_url }}",
                "article_path": "${{ needs.build.outputs.smoke_article_path }}",
                "article_sha256": "${{ needs.build.outputs.smoke_article_sha256 }}",
                "promotion_reference": "${{ needs.build.outputs.smoke_promotion_reference }}",
            },
        )
        self.assertIn("podcaster-release-smoke", workflow["jobs"]["notify-failure"]["needs"])

    def test_crawl_workflow_persists_run_counter(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        crawl_job = workflow["jobs"]["crawl"]
        commit_step = None
        for step in crawl_job["steps"]:
            if step.get("name") == "Commit crawl data to data branch":
                commit_step = step
                break

        self.assertIsNotNone(commit_step, "Commit crawl data to data branch step not found")
        run_script = commit_step["run"]
        self.assertIn("COUNTER=$(cat .squad/run-counter.txt", run_script)
        self.assertIn("COUNTER=$((COUNTER + 1))", run_script)
        self.assertIn(".squad/run-counter.txt", run_script)
        self.assertIn("git add data/raw/ data/snapshots/ data/raw-store/", run_script)
        self.assertIn("git add .squad/run-counter.txt", run_script)

    def test_external_news_workflow_passes_deterministic_until(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        crawl_job = workflow["jobs"]["crawl"]
        external_news_step = next(
            (
                step
                for step in crawl_job["steps"]
                if step.get("name") == "Crawl external news RSS feeds"
            ),
            None,
        )

        self.assertIsNotNone(external_news_step, "External news crawl step not found")
        run_script = external_news_step["run"]
        self.assertIn("SINCE=$(date -u -d '7 days ago' +%Y-%m-%d)", run_script)
        self.assertIn("UNTIL=$(date -u +%Y-%m-%d)", run_script)
        self.assertIn('--until "$UNTIL"', run_script)

    def test_crawl_workflow_defines_analyze_job(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        # Reskill jobs have been removed (analysis uses plain copilot-cli)
        self.assertNotIn("reskill-check", workflow["jobs"])
        self.assertNotIn("reskill", workflow["jobs"])

        analyze = workflow["jobs"]["analyze"]
        preflight_step = next(
            (
                s
                for s in analyze["steps"]
                if s.get("name") == "Render and preflight analysis prompt"
            ),
            None,
        )
        self.assertIsNotNone(preflight_step)
        preflight_run = preflight_step["run"]
        self.assertIn("--prompt-token-budget", preflight_run)
        self.assertIn("--preflight-report-json", preflight_run)
        self.assertIn("--preflight-report-md", preflight_run)
        self.assertIn('--print-prompt > "$PROMPT_FILE"', preflight_run)
        self.assertIn('--context-files "$PROMPT_FILE"', preflight_run)
        self.assertIn("promotion_policy=", preflight_run)
        self.assertIn("staged/candidate-only", preflight_run)

        run_analysis_step = next(
            (s for s in analyze["steps"] if s.get("name") == "Run analysis"), None
        )
        self.assertIsNotNone(run_analysis_step)
        run_analysis = run_analysis_step["run"]
        self.assertIn("python3 scripts/track_token_usage.py", run_analysis)
        self.assertIn('ANALYSIS_MODEL="copilot-default"', run_analysis)
        self.assertNotIn("--model claude-sonnet-4", run_analysis)
        self.assertIn("mkdir -p data/metrics", run_analysis)
        self.assertIn("run_quality_gate()", run_analysis)
        self.assertIn("python3 scripts/copilot_failure.py", run_analysis)
        self.assertIn("--create-token-issue", run_analysis)
        self.assertIn('FINAL_FAILURE_CLASS=""', run_analysis)
        self.assertIn("--agent weekly-analysis", run_analysis)
        self.assertIn(
            "Read the file at ${PROMPT_FILE}. Write the complete weekly analysis markdown to ${OUTPUT_FILE}.",
            run_analysis,
        )
        self.assertIn('if ! test -s "$OUTPUT_FILE"; then', run_analysis)
        self.assertIn('FINAL_FAILURE_CLASS="writer_contract_failure"', run_analysis)
        self.assertNotIn("--allow-tool=glob", run_analysis)
        self.assertNotIn("--allow-tool=grep", run_analysis)
        self.assertIn(
            'if [ "$FAILURE_CLASS" = "copilot_token_failure" ] || [ "$FAILURE_CLASS" = "copilot_inaccessible" ]; then',
            run_analysis,
        )
        self.assertIn("failing without no-AI fallback", run_analysis)
        self.assertIn(
            'echo "copilot is not available: command not found" > "$COPILOT_LOG"', run_analysis
        )
        self.assertIn("--exit-code 127", run_analysis)
        self.assertIn("No publishable Copilot summary was produced", run_analysis)
        self.assertIn("current published article can be preserved", run_analysis)
        self.assertIn("python3 scripts/analyze_fallback.py", run_analysis)
        self.assertIn('--press-context "$PRESS_FILE"', run_analysis)
        self.assertIn("--no-ai", run_analysis)
        self.assertIn('ANALYSIS_SOURCE="no-ai"', run_analysis)
        self.assertNotIn('ANALYSIS_SOURCE="github-models"', run_analysis)
        self.assertNotIn("falling back to GitHub Models API", run_analysis)

        manifest_step = next(
            (s for s in analyze["steps"] if s.get("name") == "Emit publish eligibility manifest"),
            None,
        )
        self.assertIsNotNone(manifest_step)
        manifest_run = manifest_step["run"]
        self.assertEqual(
            manifest_step["env"]["PREFLIGHT_REPORT"],
            "${{ steps.prompt-preflight.outputs.preflight_report_json }}",
        )
        self.assertIn('--preflight-report "$PREFLIGHT_REPORT"', manifest_run)

    def test_generate_workflow_runs_rollups_and_commits_all_content(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        deploy_job = workflow["jobs"]["deploy"]
        build_site_step = next(
            (s for s in deploy_job["steps"] if s.get("name") == "Build site"), None
        )
        self.assertIsNotNone(build_site_step)
        self.assertEqual(build_site_step["run"], "hugo --minify")

        pagefind_step = next(
            (s for s in deploy_job["steps"] if s.get("name") == "Build search index"), None
        )
        self.assertIsNotNone(pagefind_step)
        self.assertEqual(pagefind_step["run"], "npx pagefind --site public/")

        generate_job = workflow["jobs"]["generate"]
        generate_rollups_step = next(
            (s for s in generate_job["steps"] if s.get("name") == "Generate rollups"), None
        )
        self.assertIsNotNone(generate_rollups_step)
        self.assertEqual(generate_rollups_step["run"], "python3 scripts/generate_rollups.py")

        commit_step = next(
            (
                s
                for s in generate_job["steps"]
                if s.get("name") == "Commit generated content to data branch"
            ),
            None,
        )
        self.assertIsNotNone(commit_step)
        commit_run = commit_step["run"]
        self.assertIn("content/weekly", commit_run)
        self.assertIn("content/monthly", commit_run)
        self.assertIn("content/yearly", commit_run)
        self.assertIn("content/weekly/", commit_run)
        self.assertIn("content/monthly/", commit_run)
        self.assertIn("content/yearly/", commit_run)
        self.assertIn("GENERATED_PATHS=(", commit_run)
        self.assertIn('tar -cf generated-state.tar "${ARCHIVE_PATHS[@]}"', commit_run)
        self.assertIn("tar -xf generated-state.tar", commit_run)
        # Stage only generated paths that exist; optional outputs (e.g.
        # data/topic-hubs/) are absent when a feature produced nothing (issue #633).
        self.assertIn('git add -A -- "${ADD_PATHS[@]}"', commit_run)
        self.assertNotIn('git add -A -- "${GENERATED_PATHS[@]}" data/backups/', commit_run)
        # A restore must refresh observatory surfaces only and preserve the already-
        # published weekly transaction (issue #640). The commit step reverts those
        # files -- and the rollups that embed the article summary -- to the publish
        # versions before staging when run_mode == restore.
        self.assertIn('if [ "$RUN_MODE" = "restore" ]; then', commit_run)
        self.assertIn("weekly-transaction-paths", commit_run)
        self.assertIn('git checkout HEAD -- "$tx_path"', commit_run)
        self.assertIn("RESTORE_PRESERVE+=(content/monthly content/yearly)", commit_run)
        self.assertEqual(commit_step["env"]["RUN_MODE"], "${{ needs.analyze.outputs.run_mode }}")

        upload_step = next(
            (
                s
                for s in generate_job["steps"]
                if s.get("name") == "Upload generated content artifact"
            ),
            None,
        )
        self.assertIsNotNone(upload_step)
        self.assertIn("content/monthly/", upload_step["with"]["path"])
        self.assertIn("content/yearly/", upload_step["with"]["path"])
        promoted_upload = next(
            (
                s
                for s in generate_job["steps"]
                if s.get("name") == "Upload promoted analyzed artifact"
            ),
            None,
        )
        self.assertIsNotNone(promoted_upload)
        self.assertEqual(promoted_upload["with"]["name"], "promoted-analyzed-data")

    def test_analyze_job_uploads_token_usage_ledger_for_generate_job(self) -> None:
        """The generate job's publish hydration discards data/metrics/ unless the
        analyze job's freshly appended ledger row is passed forward via artifact
        (see the ledger commit-path gap fixed alongside this test)."""
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        analyze_job = workflow["jobs"]["analyze"]
        upload_step = next(
            (s for s in analyze_job["steps"] if s.get("name") == "Upload token usage ledger"),
            None,
        )
        self.assertIsNotNone(upload_step)
        self.assertTrue(_uses_action(upload_step, "actions/upload-artifact"))
        self.assertEqual(upload_step["with"]["name"], "token-usage-ledger")
        self.assertEqual(upload_step["with"]["path"], "data/metrics/token-usage.jsonl")
        self.assertEqual(upload_step["with"]["if-no-files-found"], "error")
        self.assertEqual(upload_step.get("if"), "always()")

        generate_job = workflow["jobs"]["generate"]
        step_names = [s.get("name") for s in generate_job["steps"]]
        for step_name in (
            "Hydrate prior generated state from publish",
            "Download token usage ledger artifact",
            "Generate reconciled cost summary",
            "Commit generated content to data branch",
        ):
            self.assertIn(step_name, step_names)
        hydrate_index = step_names.index("Hydrate prior generated state from publish")
        download_index = step_names.index("Download token usage ledger artifact")
        summary_index = step_names.index("Generate reconciled cost summary")
        commit_index = step_names.index("Commit generated content to data branch")
        # The ledger download must happen after the publish hydration overwrites
        # data/metrics/ and before the projection and commit persist this run's state.
        self.assertGreater(download_index, hydrate_index)
        self.assertLess(download_index, summary_index)
        self.assertLess(summary_index, commit_index)

        download_step = generate_job["steps"][download_index]
        self.assertIn("scripts/download_run_artifact.py", download_step["run"])
        self.assertIn("--artifact token-usage-ledger", download_step["run"])
        self.assertIn("--destination data/metrics/", download_step["run"])
        self.assertNotIn("continue-on-error", download_step)
        self.assertEqual(download_step["env"]["GH_TOKEN"], "${{ secrets.GITHUB_TOKEN }}")

        summary_step = generate_job["steps"][summary_index]
        self.assertEqual(
            summary_step["env"]["CURRENT_DATETIME"],
            "${{ needs.analyze.outputs.current_datetime }}",
        )
        self.assertIn("scripts/generate_cost_summary.py", summary_step["run"])
        self.assertIn('--generated-at "$CURRENT_DATETIME"', summary_step["run"])
        self.assertIn("--legacy-policy exclude-unidentified", summary_step["run"])

    def test_same_run_artifact_downloads_use_retry_helper_with_auth(self) -> None:
        workflow = yaml.safe_load(
            Path(".github/workflows/crawl-and-publish.yml").read_text(encoding="utf-8")
        )

        for job_name in ("analyze", "generate", "deploy", "notify"):
            job = workflow["jobs"][job_name]
            self.assertEqual(job["permissions"]["actions"], "read")
            retry_steps = [
                step
                for step in job["steps"]
                if "scripts/download_run_artifact.py" in step.get("run", "")
            ]
            self.assertTrue(retry_steps, f"{job_name} must use the retrying artifact helper")
            for step in retry_steps:
                with self.subTest(job=job_name, step=step.get("name")):
                    self.assertEqual(step["env"]["GH_TOKEN"], "${{ secrets.GITHUB_TOKEN }}")

    def test_production_quality_build_uses_local_server_base_url(self) -> None:
        workflow_path = Path(".github/workflows/ci.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        production_job = workflow["jobs"]["production-site"]
        self.assertEqual(production_job["env"]["BASE_URL"], "http://127.0.0.1:1313")
        build_step = next(
            step
            for step in production_job["steps"]
            if step.get("name") == "Build site and capture Hugo duration"
        )
        self.assertIn('hugo --minify --baseURL "${BASE_URL}/"', build_step["run"])
        serve_step = next(
            step for step in production_job["steps"] if step.get("name") == "Serve production build"
        )
        self.assertIn("scripts/serve_static.py", serve_step["run"])
        self.assertNotIn("http.server", serve_step["run"])

    def test_publish_transaction_orders_all_observatory_generators(self) -> None:
        workflow = yaml.safe_load(
            Path(".github/workflows/crawl-and-publish.yml").read_text(encoding="utf-8")
        )
        steps = workflow["jobs"]["generate"]["steps"]
        positions = {step.get("name"): index for index, step in enumerate(steps)}

        expected_order = [
            "Hydrate prior generated state from publish",
            "Download analyzed data artifact",
            "Download token usage ledger artifact",
            "Download analysis candidate artifact",
            "Download raw crawl artifact",
            "Generate reconciled cost summary",
            "Generate weekly content candidate",
            "Discover topic candidates",
            "Promote and assign topic hubs",
            "Reconcile weekly topic frontmatter",
            "Rehash and promote final weekly content",
            "Refresh taxonomy registries",
            "Refresh topic candidates after taxonomy updates",
            "Generate rollups",
            "Generate repository pages",
            "Generate data pages",
            "Export Observatory dataset",
            "Export trend explorer data",
            "Verify generated content freshness",
            "Commit generated content to data branch",
        ]
        self.assertTrue(
            all(name in positions for name in expected_order),
            f"Missing transaction steps: {[name for name in expected_order if name not in positions]}",
        )
        self.assertEqual(
            [positions[name] for name in expected_order],
            sorted(positions[name] for name in expected_order),
        )

        rehash = steps[positions["Rehash and promote final weekly content"]]["run"]
        self.assertIn('manifest["candidate"]["content_sha256"]', rehash)
        self.assertIn("scripts/promotion_guard.py", rehash)
        self.assertLess(
            rehash.index('manifest["candidate"]["content_sha256"]'),
            rehash.index("scripts/promotion_guard.py"),
        )

        reconcile = steps[positions["Reconcile weekly topic frontmatter"]]["run"]
        self.assertEqual(reconcile, "python3 scripts/backfill_weekly_topics.py")
        freshness = steps[positions["Verify generated content freshness"]]["run"]
        self.assertIn("python3 scripts/backfill_weekly_topics.py --check", freshness)

    def test_publish_transaction_carries_every_generated_path(self) -> None:
        generated_paths = (
            "content/topics/",
            "content/data/",
            "data/taxonomy/",
            "data/topic-hubs/",
            "data/derived/observatory/",
            "static/datasets/open-source-ai-github-projects-2026/",
            "static/tools/star-velocity-explorer.json",
        )
        crawl = yaml.safe_load(
            Path(".github/workflows/crawl-and-publish.yml").read_text(encoding="utf-8")
        )
        generate_steps = crawl["jobs"]["generate"]["steps"]
        hydrate = next(
            step
            for step in generate_steps
            if step.get("name") == "Hydrate prior generated state from publish"
        )["run"]
        commit = next(
            step
            for step in generate_steps
            if step.get("name") == "Commit generated content to data branch"
        )["run"]
        upload = next(
            step
            for step in generate_steps
            if step.get("name") == "Upload generated content artifact"
        )["with"]["path"]
        inline_deploy_download = next(
            step
            for step in crawl["jobs"]["deploy"]["steps"]
            if step.get("name") == "Download generated content artifact"
        )
        deploy_steps = crawl["jobs"]["deploy"]["steps"]
        deploy = yaml.safe_load(
            Path(".github/workflows/deploy-site.yml").read_text(encoding="utf-8")
        )
        deploy_hydrate = next(
            step
            for step in deploy["jobs"]["build"]["steps"]
            if step.get("name") == "Hydrate generated content from publish"
        )["run"]

        for path in generated_paths:
            with self.subTest(path=path):
                self.assertIn(path, hydrate)
                self.assertIn(path, commit)
                self.assertIn(path, upload)
                self.assertIn(path, deploy_hydrate)

            self.assertIn("data/metrics/", hydrate)
            self.assertIn("data/metrics/", commit)
            self.assertIn("data/metrics/", deploy_hydrate)
            self.assertNotIn("data/metrics/\n", upload)
            self.assertIn("data/metrics/cost-summary.json", upload)

        # Deploy hydration guards each path with git ls-tree so committed content
        # absent from publish is preserved rather than deleted (issues #627, #633).
        self.assertIn('git ls-tree -r --name-only origin/publish -- "$path"', deploy_hydrate)
        self.assertNotIn(
            'git checkout origin/publish -- "$path" 2>/dev/null || true', deploy_hydrate
        )

        self.assertIn("--force-with-lease", commit)
        self.assertIn("git diff --cached --quiet && exit 0", commit)
        self.assertIn("--artifact generated-content", inline_deploy_download["run"])
        self.assertIn("--destination ./", inline_deploy_download["run"])
        deploy_positions = {step.get("name"): index for index, step in enumerate(deploy_steps)}
        self.assertLess(
            deploy_positions["Remove checked-in cost summary"],
            deploy_positions["Download generated content artifact"],
        )
        self.assertLess(
            deploy_positions["Download generated content artifact"],
            deploy_positions["Verify generated cost summary"],
        )
        remove_cost_summary = next(
            step for step in deploy_steps if step.get("name") == "Remove checked-in cost summary"
        )
        self.assertEqual(remove_cost_summary["run"], "rm -f data/metrics/cost-summary.json")
        verify_cost_summary = next(
            step for step in deploy_steps if step.get("name") == "Verify generated cost summary"
        )
        self.assertEqual(verify_cost_summary["run"], "test -s data/metrics/cost-summary.json")

    def test_generate_hydration_preserves_committed_paths_absent_from_publish(self) -> None:
        crawl = yaml.safe_load(
            Path(".github/workflows/crawl-and-publish.yml").read_text(encoding="utf-8")
        )
        hydrate = next(
            step
            for step in crawl["jobs"]["generate"]["steps"]
            if step.get("name") == "Hydrate prior generated state from publish"
        )["run"]
        # Only wipe+restore paths that exist on publish so committed generated files
        # not yet on publish (e.g. data/taxonomy/topics.json) are preserved (issue #627).
        self.assertIn('git ls-tree -r --name-only origin/publish -- "$path"', hydrate)
        self.assertNotIn('git checkout origin/publish -- "$path" 2>/dev/null || true', hydrate)
        self.assertIn('if [ "$path" = "content/topics" ]; then', hydrate)
        self.assertIn("dynamic_topic: true", hydrate)
        self.assertIn("grep '/_index.md$' || true", hydrate)
        self.assertIn('current_frontmatter=""', hydrate)
        self.assertIn('[ ! -f "$hub" ]', hydrate)

    def test_data_page_schedule_is_read_only_freshness_check(self) -> None:
        workflow = yaml.safe_load(
            Path(".github/workflows/generate-data-pages.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(workflow.get("permissions"), {"contents": "read"})
        freshness_steps = workflow["jobs"]["freshness"]["steps"]
        install = next(
            step for step in freshness_steps if step.get("name") == "Install Python dependencies"
        )
        self.assertEqual(install["run"], "pip install -r requirements.txt")
        rendered = Path(".github/workflows/generate-data-pages.yml").read_text(encoding="utf-8")
        self.assertIn("python3 scripts/generate_data_pages.py --check", rendered)
        self.assertIn("python3 scripts/observatory_repos.py --check", rendered)
        self.assertIn("python3 scripts/export_observatory_dataset.py --check", rendered)
        self.assertIn("python3 scripts/export_trend_explorer_data.py --check", rendered)
        self.assertNotIn("gh pr create", rendered)
        self.assertNotIn("git push", rendered)
        self.assertNotIn("contents: write", rendered)
        # Hydration guards each path so committed content absent from publish is
        # preserved rather than deleted (#633).
        hydrate = next(
            step
            for step in freshness_steps
            if step.get("name") == "Hydrate generated state from publish"
        )["run"]
        self.assertIn('git ls-tree -r --name-only origin/publish -- "$path"', hydrate)
        self.assertNotIn('git checkout origin/publish -- "$path" 2>/dev/null || true', hydrate)

    def test_sync_publish_to_main_excludes_squad_state_and_regenerates_rollups(self) -> None:
        workflow_path = Path(".github/workflows/sync-publish-to-main.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        sync_job = workflow["jobs"]["sync"]
        setup_python = next(
            (s for s in sync_job["steps"] if _uses_action(s, "actions/setup-python")), None
        )
        self.assertIsNotNone(setup_python)
        self.assertEqual(setup_python["with"]["python-version"], "3.12")
        install = next(
            (s for s in sync_job["steps"] if s.get("name") == "Install Python dependencies"),
            None,
        )
        self.assertIsNotNone(install)
        self.assertEqual(install["run"], "pip install -r requirements.txt")

        sync_step = next(
            (s for s in sync_job["steps"] if s.get("name") == "Sync data from publish"), None
        )
        self.assertIsNotNone(sync_step)

        sync_run = sync_step["run"]
        for generated_path in (
            "data/raw/",
            "data/analyzed/",
            "data/metrics/",
            "data/topic-hubs/",
            "content/weekly/",
            "content/monthly/",
            "content/yearly/",
            "content/topics/",
        ):
            self.assertIn(generated_path, sync_run)

        self.assertIn("data/taxonomy/tags.json", sync_run)
        self.assertIn("data/taxonomy/topic-candidates.json", sync_run)
        self.assertIn("dynamic_topic: true", sync_run)
        self.assertIn("grep '/_index.md$' || true", sync_run)
        self.assertIn("python3 scripts/taxonomy_registry.py", sync_run)
        self.assertIn("python3 scripts/discover_topic_candidates.py", sync_run)
        self.assertLess(
            sync_run.index("python3 scripts/taxonomy_registry.py"),
            sync_run.index("python3 scripts/discover_topic_candidates.py"),
        )
        self.assertIn('current_frontmatter=""', sync_run)
        self.assertIn('[ ! -f "$hub" ]', sync_run)
        self.assertNotIn("rm -rf content/topics", sync_run)

        self.assertIn("python3 scripts/generate_rollups.py", sync_run)
        self.assertLess(
            sync_run.index("python3 scripts/generate_rollups.py"), sync_run.index("git add -A")
        )
        self.assertIn("Refusing to sync .squad state from publish to main.", sync_run)
        self.assertLess(sync_run.index("Refusing to sync .squad"), sync_run.index("git commit -m"))
        self.assertIn("**Explicitly NOT synced:**", sync_run)
        self.assertIn(".squad/**", sync_run)
        self.assertNotIn("git checkout origin/publish -- .squad", sync_run)
        self.assertNotIn("git ls-tree -r --name-only origin/publish -- .squad", sync_run)
        self.assertNotIn(".squad/decisions.md", sync_run)
        self.assertNotIn(".squad/agents/*/history.md", sync_run)
        self.assertNotIn("squad learnings", sync_run.lower())

    def test_notify_workflow_posts_optional_webhook(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        notify_job = workflow["jobs"]["notify"]
        self.assertEqual(notify_job["needs"], ["analyze", "generate", "deploy"])
        self.assertEqual(
            notify_job["permissions"],
            {"actions": "read", "contents": "write", "discussions": "write"},
        )
        analyzed_download = next(
            (
                s
                for s in notify_job["steps"]
                if s.get("name") == "Download promoted analyzed data artifact"
            ),
            None,
        )
        self.assertIsNotNone(analyzed_download)
        self.assertIn("--artifact promoted-analyzed-data", analyzed_download["run"])
        self.assertIn("--destination data/analyzed/", analyzed_download["run"])
        self.assertEqual(analyzed_download["env"]["GH_TOKEN"], "${{ secrets.GITHUB_TOKEN }}")

        webhook_step = next(
            (s for s in notify_job["steps"] if s.get("name") == "Post to webhook"), None
        )
        self.assertIsNotNone(webhook_step)
        self.assertEqual(webhook_step["if"], "env.WEBHOOK_URL != ''")
        self.assertEqual(webhook_step["env"]["WEBHOOK_URL"], "${{ secrets.WEBHOOK_URL }}")

        release_step = next(
            (s for s in notify_job["steps"] if s.get("name") == "Create GitHub Release"), None
        )
        self.assertIsNotNone(release_step)
        self.assertEqual(
            release_step["env"]["SUMMARY_FILE"], "${{ needs.analyze.outputs.summary_file }}"
        )
        release_run = release_step["run"]
        self.assertIn('gh release view "$TAG"', release_run)
        self.assertIn('gh release edit "$TAG"', release_run)
        self.assertIn('gh release create "$TAG"', release_run)

        webhook_run = webhook_step["run"]
        self.assertIn('curl -s -X POST "$WEBHOOK_URL"', webhook_run)
        self.assertIn("https://claracle.com/weekly/", webhook_run)
        # JSON is now built with jq to prevent injection — check for jq invocation
        self.assertIn("jq -n", webhook_run)
        self.assertIn("📊 **SquadScope Week", webhook_run)
        self.assertIn("Webhook post failed (non-critical)", webhook_run)

    def test_real_podcaster_handoff_is_not_automatic(self) -> None:
        for workflow_path in (
            Path(".github/workflows/crawl-and-publish.yml"),
            Path(".github/workflows/sync-publish-to-main.yml"),
        ):
            workflow = workflow_path.read_text(encoding="utf-8")
            self.assertNotIn("PODCASTER_ENDPOINT", workflow)
            self.assertNotIn("PODCASTER_API_KEY", workflow)
            self.assertNotIn("scripts/podcaster_handoff.py", workflow)

    def test_real_podcaster_workflow_requires_exact_protected_manual_run(self) -> None:
        workflow_path = Path(".github/workflows/trigger-podcast.yml")
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow = yaml.safe_load(workflow_text)

        triggers = workflow.get("on", workflow.get(True))
        self.assertEqual(set(triggers), {"workflow_dispatch"})
        inputs = triggers["workflow_dispatch"]["inputs"]
        self.assertTrue(inputs["publish_run_id"]["required"])

        job = workflow["jobs"]["trigger-podcast"]
        self.assertIn("refs/heads/main", job["if"])
        self.assertEqual(job["environment"]["name"], "podcaster-real-generation")
        self.assertNotEqual(job["environment"]["name"], "podcaster-release-smoke")
        checkout = next(s for s in job["steps"] if _uses_action(s, "actions/checkout"))
        self.assertEqual(checkout["with"]["ref"], "${{ github.event.repository.default_branch }}")

        locate = next(s for s in job["steps"] if s.get("id") == "manifest-locate")
        locate_run = locate["run"]
        self.assertIn("data/candidates/${WEEK}/${PUBLISH_RUN_ID}/publish-manifest.json", locate_run)
        self.assertIn('manifest.get("week") != requested_week', locate_run)
        self.assertIn('str(manifest.get("run_id")) != requested_run_id', locate_run)
        self.assertNotIn("find ", locate_run)
        self.assertNotIn("tail -1", locate_run)
        self.assertNotIn("most recent", locate_run)
        manifest_script = locate_run.split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
        compile(manifest_script, str(workflow_path), "exec")

        handoff = next(s for s in job["steps"] if s.get("id") == "handoff")
        self.assertIn("--require-merged", handoff["run"])
        self.assertNotIn("--podcaster-dry-run", handoff["run"])
        self.assertNotIn("--force", handoff["run"])
        evidence = next(
            s for s in job["steps"] if s.get("name") == "Retain real generation evidence"
        )
        self.assertEqual(evidence["if"], "always()")
        self.assertIn("actions/runs", evidence["env"]["RUN_URL"])
        for field in (
            "MANIFEST_PATH",
            "MANIFEST_SHA256",
            "ARTICLE_SHA256",
            "PODCASTER_JOB_ID",
            "PODCASTER_STATUS",
        ):
            self.assertIn(field, evidence["env"])

    def test_podcaster_smoke_workflow_exercises_real_weekly_payload_shape(self) -> None:
        workflow_path = Path(".github/workflows/podcaster-handoff-smoke.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        triggers = workflow.get("on", workflow.get(True))
        dispatch_inputs = triggers["workflow_dispatch"]["inputs"]
        call_inputs = triggers["workflow_call"]["inputs"]
        expected_inputs = {
            "week",
            "article_url",
            "article_path",
            "article_sha256",
            "promotion_reference",
        }
        self.assertEqual(set(dispatch_inputs), expected_inputs)
        self.assertEqual(set(call_inputs), expected_inputs)
        self.assertTrue(all(details["required"] for details in call_inputs.values()))
        # The reusable workflow must declare PODCASTER_API_KEY so callers can pass
        # the repository secret explicitly (reusable workflows do not inherit it).
        self.assertTrue(triggers["workflow_call"]["secrets"]["PODCASTER_API_KEY"]["required"])

        smoke_job = workflow["jobs"]["smoke"]
        self.assertEqual(smoke_job["environment"]["name"], "podcaster-release-smoke")
        # Code (scripts/, config/) comes from the default branch checkout; the
        # promoted article and its record are hydrated from publish (issue #639).
        checkout = next(s for s in smoke_job["steps"] if _uses_action(s, "actions/checkout"))
        self.assertEqual(checkout["with"]["ref"], "${{ github.event.repository.default_branch }}")
        hydrate = next(
            s
            for s in smoke_job["steps"]
            if s.get("name") == "Hydrate published article from publish"
        )
        self.assertIn("git fetch origin publish", hydrate["run"])
        self.assertIn(
            'git checkout FETCH_HEAD -- "$ARTICLE_PATH" "$PROMOTION_REFERENCE"', hydrate["run"]
        )
        # promotion_transaction_v1 records reference a source manifest whose bytes
        # the handoff tooling verifies, so the smoke must hydrate it too (issue #639).
        self.assertIn("source_manifest", hydrate["run"])
        self.assertIn('git checkout FETCH_HEAD -- "$SOURCE_MANIFEST_PATH"', hydrate["run"])
        # Hydration is restricted to the expected candidate-manifest location so a
        # crafted promotion record cannot overwrite tooling/config (PR #645 review).
        self.assertIn(r"data/candidates/[^/]+/[^/]+/publish-manifest\.json", hydrate["run"])
        smoke_step = next(
            (s for s in smoke_job["steps"] if s.get("name") == "Smoke test Podcaster dry run"), None
        )
        self.assertIsNotNone(smoke_step)
        run_script = smoke_step["run"]
        self.assertNotIn("python3 - <<", run_script)
        self.assertIn("python3 scripts/podcaster_handoff.py", run_script)
        self.assertIn('--promotion-reference "$PROMOTION_REFERENCE"', run_script)
        self.assertIn('--expected-article-sha256 "$ARTICLE_SHA256"', run_script)
        self.assertIn("--podcast-config config/podcast.json", run_script)
        self.assertIn("--podcaster-dry-run", run_script)
        self.assertIn("--exact-article-content", run_script)
        evidence_step = next(
            s for s in smoke_job["steps"] if s.get("name") == "Retain smoke run evidence"
        )
        self.assertEqual(evidence_step["if"], "always()")
        self.assertIn("actions/runs", evidence_step["env"]["RUN_URL"])

    def test_podcaster_release_verifier_executes_checked_in_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with self.assertRaisesRegex(
                podcaster_handoff.PodcasterHandoffError,
                "article_sha256 must be lowercase",
            ):
                podcaster_handoff.verify_release_evidence(
                    week="2026-W23",
                    article_path="content/weekly/2026/W23.md",
                    article_sha256="not-a-sha",
                    promotion_reference=Path("data/published/2026-W23/promotion-manifest.json"),
                    repo_root=root,
                )

    def test_publish_workflow_uses_candidate_manifest_before_promotion(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        analyze = workflow["jobs"]["analyze"]
        self.assertEqual(
            analyze["outputs"]["summary_file"],
            "${{ steps.analysis-context.outputs.published_output_file }}",
        )
        self.assertEqual(
            analyze["outputs"]["candidate_summary_file"],
            "${{ steps.analysis-context.outputs.candidate_output_file }}",
        )
        self.assertEqual(
            analyze["outputs"]["publish_manifest_file"],
            "${{ steps.analysis-context.outputs.publish_manifest_file }}",
        )

        prepare_step = next(
            (s for s in analyze["steps"] if s.get("name") == "Prepare analysis context"), None
        )
        self.assertIsNotNone(prepare_step)
        prepare_run = prepare_step["run"]
        self.assertIn("data/candidates", prepare_run)
        self.assertIn("candidate_output_file", prepare_run)
        self.assertIn("publish_manifest_file", prepare_run)
        self.assertIn("published_output_file=data/analyzed", prepare_run)

        manifest_step = next(
            (s for s in analyze["steps"] if s.get("name") == "Emit publish eligibility manifest"),
            None,
        )
        self.assertIsNotNone(manifest_step)
        manifest_run = manifest_step["run"]
        self.assertIn("scripts/publish_manifest.py create", manifest_run)
        self.assertIn("--analysis-source", manifest_run)
        self.assertIn("--analysis-model", manifest_run)
        self.assertIn('--validation-status "$VALIDATION_STATUS"', manifest_run)
        self.assertIn("--run-mode", manifest_run)
        self.assertIn("--source-refresh-policy", manifest_run)
        self.assertIn('git checkout origin/publish -- "$PUBLISHED_SUMMARY"', manifest_run)

        assert_step = next(
            (
                s
                for s in analyze["steps"]
                if s.get("name") == "Assert candidate is eligible for promotion"
            ),
            None,
        )
        self.assertIsNotNone(assert_step)
        self.assertIn("scripts/publish_manifest.py assert-eligible", assert_step["run"])

        self.assertEqual(
            analyze["outputs"]["publish_head_sha"], "${{ steps.publish-base.outputs.sha }}"
        )
        commit_step = next(
            (
                s
                for s in analyze["steps"]
                if s.get("name") == "Commit analysis and learnings to data branch"
            ),
            None,
        )
        self.assertIsNone(commit_step)

        upload_candidate = next(
            (s for s in analyze["steps"] if s.get("name") == "Upload analysis candidate"), None
        )
        self.assertIsNotNone(upload_candidate)
        self.assertEqual(upload_candidate["if"], "always()")

        generate = workflow["jobs"]["generate"]
        generate_raw_download = next(
            (
                s
                for s in generate["steps"]
                if s.get("name") == "Download raw crawl artifact"
            ),
            None,
        )
        self.assertIsNotNone(generate_raw_download)
        self.assertIn("--artifact raw-data", generate_raw_download["run"])
        self.assertIn("--destination data/raw/", generate_raw_download["run"])
        self.assertEqual(generate_raw_download["env"]["GH_TOKEN"], "${{ secrets.GITHUB_TOKEN }}")

        generate_step = next(
            (s for s in generate["steps"] if s.get("name") == "Generate weekly content candidate"),
            None,
        )
        self.assertIsNotNone(generate_step)
        self.assertIn('assert-eligible --manifest "$MANIFEST_FILE"', generate_step["run"])
        self.assertIn("candidate_content_path", generate_step["run"])
        self.assertIn("scripts/promotion_guard.py --manifest", generate_step["run"])

        content_commit_step = next(
            (
                s
                for s in generate["steps"]
                if s.get("name") == "Commit generated content to data branch"
            ),
            None,
        )
        self.assertIsNotNone(content_commit_step)
        content_commit_run = content_commit_step["run"]
        self.assertIn(
            "Publish branch drifted between analyze and content promotion", content_commit_run
        )
        self.assertIn("backup-existing", content_commit_run)
        self.assertIn('--path "data/published/${WEEK}/promotion-manifest.json"', content_commit_run)
        self.assertIn("promotion-guard-tool.py --manifest", content_commit_run)
        self.assertIn("data/published/", content_commit_run)
        self.assertIn("--force-with-lease", content_commit_run)

    def test_rerun_mode_inputs_and_guards_are_declared(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        inputs = workflow.get("on", workflow.get(True))["workflow_dispatch"]["inputs"]

        self.assertEqual(inputs["run_mode"]["default"], "normal")
        self.assertIn("restore", inputs["run_mode"]["options"])
        self.assertEqual(inputs["source_refresh_policy"]["default"], "reuse-same-day")
        self.assertIn("force-refresh", inputs["source_refresh_policy"]["options"])

        crawl_steps = workflow["jobs"]["crawl"]["steps"]
        validate_step = next(
            (s for s in crawl_steps if s.get("name") == "Validate rerun mode"), None
        )
        self.assertIsNotNone(validate_step)
        self.assertIn("scripts/rerun_modes.py", validate_step["run"])

        run_crawler = next((s for s in crawl_steps if s.get("name") == "Run crawler"), None)
        self.assertIn("--reuse-artifact", run_crawler["run"])
        self.assertIn("--source-refresh-policy", run_crawler["run"])

    def test_notify_failure_job_creates_or_updates_issue(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        notify_failure_job = workflow["jobs"]["notify-failure"]
        self.assertEqual(
            notify_failure_job["needs"], ["crawl", "analyze", "generate", "deploy", "notify"]
        )
        self.assertEqual(
            notify_failure_job["if"], "${{ always() && contains(needs.*.result, 'failure') }}"
        )
        self.assertEqual(notify_failure_job["permissions"], {"actions": "read", "issues": "write"})

        create_issue_step = next(
            (
                s
                for s in notify_failure_job["steps"]
                if s.get("name") == "Create or update failure issue"
            ),
            None,
        )
        self.assertIsNotNone(create_issue_step)
        self.assertEqual(create_issue_step["env"]["GITHUB_TOKEN"], "${{ secrets.GITHUB_TOKEN }}")
        create_issue_run = create_issue_step["run"]
        self.assertIn('gh run view "$RUN_ID" --json jobs', create_issue_run)
        self.assertEqual(create_issue_step["env"]["RUN_ID"], "${{ github.run_id }}")
        self.assertIn("gh issue list --state open --search", create_issue_run)
        self.assertIn('gh issue comment "$ISSUE_NUM"', create_issue_run)
        self.assertIn("gh issue create", create_issue_run)
        self.assertIn("Crawl and publish pipeline failed", create_issue_run)


class PipelineIntegrationTests(unittest.TestCase):
    def test_crawl_script_produces_valid_json_output_schema(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            output_path = base / "data" / "raw" / "2026-W21.json"
            snapshot_dir = base / "data" / "snapshots"
            snapshot_dir.mkdir(parents=True)

            new_repo = make_api_repo(
                "octo/signal-kit",
                stars=120,
                created_at="2026-05-12T09:00:00Z",
                topics=["ai", "automation", "developer-tooling"],
            )
            trending_repo = make_api_repo(
                "octo/momentum-watch",
                stars=180,
                created_at="2026-05-10T12:00:00Z",
                topics=["observability", "analytics", "platform"],
            )

            class FakeClient:
                def __init__(self, token: str, **kwargs) -> None:
                    self.token = token
                    self.api_calls_used = 2
                    self.cache_hits = 1
                    self.stale_cache_hits = 0
                    self.rate_limit_limit = 5000
                    self.rate_limit_remaining = 4990
                    self.rate_limit_reset = 1747567200
                    self.rate_limit_resource = "search"
                    self.errors = []

                def search_repositories(self, query: str, *, max_results: int = 1000):
                    if query.startswith("created:"):
                        return [new_repo]
                    if query.startswith("pushed:"):
                        return [trending_repo]
                    raise AssertionError(f"Unexpected query: {query}")

                def has_readme(self, full_name: str) -> bool:
                    return True

            args = Namespace(
                since="2026-05-11",
                as_of="2026-05-18",
                max_results=10,
                output=str(output_path),
                topic=None,
                config=None,
            )

            with (
                mock.patch.object(crawl, "parse_args", return_value=args),
                mock.patch.dict("os.environ", {"GITHUB_TOKEN": "token"}, clear=False),
                mock.patch.object(crawl, "GitHubClient", FakeClient),
                mock.patch.object(
                    crawl, "load_previous_star_snapshot", return_value={"octo/momentum-watch": 145}
                ),
                mock.patch.object(crawl, "utc_now", return_value=FIXED_RUN_TIME),
                mock.patch.object(crawl, "snapshots_dir", return_value=snapshot_dir),
            ):
                exit_code = crawl.main()

            self.assertEqual(exit_code, 0)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            crawl.validate_payload(payload)
            self.assertEqual(payload["week"], "2026-W21")
            self.assertEqual(payload["trending_repos"][0]["stars_gained"], 35)
            self.assertTrue((snapshot_dir / "2026-W21-stars.json").exists())

    def test_generate_content_produces_valid_hugo_content(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            summary_path = base / "data" / "analyzed" / "2026-W21-summary.md"
            summary_path.parent.mkdir(parents=True)
            summary_path.write_text(make_analysis_markdown(), encoding="utf-8")

            previous_cwd = Path.cwd()
            try:
                import os

                os.chdir(base)
                output_path = generate_content.generate_content(summary_path)
            finally:
                os.chdir(previous_cwd)

            self.assertEqual(output_path, base / "content" / "weekly" / "2026" / "W21.md")
            rendered = output_path.read_text(encoding="utf-8")
            self.assertIn('title: "Reliable Automation Gains Ground"', rendered)
            self.assertIn('week: "2026-W21"', rendered)
            self.assertIn("draft: false", rendered)
            self.assertNotIn("quality_score", rendered)
            self.assertIn("## This Week's Trends", rendered)

    def test_analyze_fallback_no_ai_can_process_raw_data(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw_path = base / "data" / "raw" / "2026-W21.json"
            output_path = base / "data" / "analyzed" / "2026-W21-summary.md"
            raw_path.parent.mkdir(parents=True)
            output_path.parent.mkdir(parents=True)
            raw_path.write_text(json.dumps(make_raw_payload()), encoding="utf-8")

            with mock.patch.object(analyze_fallback.request, "urlopen") as urlopen_mock:
                exit_code = analyze_fallback.main(
                    [
                        "--raw-json",
                        str(raw_path),
                        "--output",
                        str(output_path),
                        "--current-datetime",
                        FIXED_RUN_DATETIME,
                        "--analyzed-dir",
                        str(output_path.parent),
                        "--no-ai",
                    ]
                )

            self.assertEqual(exit_code, 0)
            written = output_path.read_text(encoding="utf-8")
            self.assertIn("Automation, Observability, and This Week's Repo Signals", written)
            self.assertIn("## Signal & Noise", written)
            urlopen_mock.assert_not_called()

    def test_analysis_gate_validates_analysis_output_correctly(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw_path = base / "data" / "raw" / "2026-W21.json"
            raw_path.parent.mkdir(parents=True)
            raw_path.write_text(json.dumps(make_raw_payload()), encoding="utf-8")

            valid_path = base / "data" / "analyzed" / "2026-W21-summary.md"
            valid_path.parent.mkdir(parents=True)
            valid_path.write_text(make_analysis_markdown(), encoding="utf-8")

            self.assertEqual(
                analysis_gate.main(
                    [
                        "--analysis-file",
                        str(valid_path),
                        "--raw-json",
                        str(raw_path),
                        "--current-datetime",
                        FIXED_RUN_DATETIME,
                        "--source",
                        "copilot-cli",
                    ]
                ),
                0,
            )

            # quality_score is now pipeline-owned: a hand-set value is overwritten by the
            # deterministic objective score, so an otherwise-valid summary still passes even
            # when the authored score is low (jmservera/SquadScope#583).
            overwritten_path = base / "data" / "analyzed" / "overwritten-summary.md"
            overwritten_path.write_text(
                make_analysis_markdown().replace("quality_score: 86", "quality_score: 40"),
                encoding="utf-8",
            )
            self.assertEqual(
                analysis_gate.main(
                    [
                        "--analysis-file",
                        str(overwritten_path),
                        "--raw-json",
                        str(raw_path),
                        "--current-datetime",
                        FIXED_RUN_DATETIME,
                        "--source",
                        "copilot-cli",
                    ]
                ),
                0,
            )
            rewritten = overwritten_path.read_text(encoding="utf-8")
            self.assertNotIn("quality_score: 40", rewritten)
            self.assertRegex(rewritten, r"(?m)^quality_score: (?:6[0-9]|[7-9][0-9]|100)$")

            # A genuine gate violation (missing required section heading) must still be rejected.
            invalid_path = base / "data" / "analyzed" / "invalid-summary.md"
            invalid_path.write_text(
                make_analysis_markdown().replace("## The Week Ahead", "## Looking Forward"),
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit) as exc:
                analysis_gate.main(
                    [
                        "--analysis-file",
                        str(invalid_path),
                        "--raw-json",
                        str(raw_path),
                        "--current-datetime",
                        FIXED_RUN_DATETIME,
                        "--source",
                        "copilot-cli",
                    ]
                )

            self.assertEqual(exc.exception.code, 1)


if __name__ == "__main__":
    unittest.main()

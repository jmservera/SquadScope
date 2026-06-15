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
    return f'''---
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
'''


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
            self.assertIn('RELEASE_URL="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}"', install_run)
            self.assertIn('TARBALL="hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz"', install_run)
            self.assertIn('CHECKSUM_FILE="hugo_${HUGO_VERSION}_checksums.txt"', install_run)
            self.assertEqual(install_run.count(expected_retry_flags), 2)

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
        self.assertIn("git add data/raw/ data/snapshots/ .squad/run-counter.txt", run_script)

    def test_external_news_workflow_passes_deterministic_until(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        crawl_job = workflow["jobs"]["crawl"]
        external_news_step = next(
            (
                step for step in crawl_job["steps"]
                if step.get("name") == "Crawl external news RSS feeds"
            ),
            None,
        )

        self.assertIsNotNone(external_news_step, "External news crawl step not found")
        run_script = external_news_step["run"]
        self.assertIn("SINCE=$(date -u -d '7 days ago' +%Y-%m-%d)", run_script)
        self.assertIn("UNTIL=$(date -u +%Y-%m-%d)", run_script)
        self.assertIn('--until "$UNTIL"', run_script)

    def test_crawl_workflow_defines_reskill_jobs(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        
        self.assertIn("reskill-check", workflow["jobs"])
        reskill_check = workflow["jobs"]["reskill-check"]
        self.assertEqual(reskill_check["needs"], ["crawl"])
        
        self.assertIn("reskill", workflow["jobs"])
        reskill = workflow["jobs"]["reskill"]
        self.assertEqual(reskill["needs"], ["reskill-check"])
        self.assertIn("needs.reskill-check.outputs.should_reskill", reskill["if"])
        
        check_step = next((s for s in reskill_check["steps"] if s.get("name") == "Check reskill trigger"), None)
        self.assertIsNotNone(check_step)
        check_run = check_step["run"]
        self.assertIn("reskill=true", check_run)
        self.assertIn("$GITHUB_OUTPUT", check_run)
        
        install_step = next((s for s in reskill["steps"] if s.get("name") == "Install Copilot CLI"), None)
        self.assertIsNotNone(install_step)
        self.assertEqual(install_step["run"], "npm install -g @github/copilot")
        self.assertNotIn("continue-on-error", install_step)

        reskill_step = next((s for s in reskill["steps"] if s.get("name") == "Run reskill"), None)
        self.assertIsNotNone(reskill_step)
        self.assertNotIn("GITHUB_MODELS_MODEL", workflow["env"])
        self.assertEqual(reskill_step["env"]["COPILOT_GITHUB_TOKEN"], "${{ secrets.COPILOT_GH_TOKEN }}")
        reskill_run = reskill_step["run"]
        self.assertIn("python3 scripts/reskill.py --current-datetime", reskill_run)
        self.assertIn("--prompt-output", reskill_run)
        self.assertIn("python3 scripts/track_token_usage.py", reskill_run)
        self.assertIn('RESKILL_MODEL="copilot-default"', reskill_run)
        self.assertNotIn("--model claude-sonnet-4", reskill_run)
        self.assertIn("mkdir -p .squad/skills .squad/reskill", reskill_run)
        self.assertIn("data/metrics", reskill_run)
        self.assertIn("trigger-log.txt", reskill_run)
        self.assertIn("git add .squad/", reskill_run)
        self.assertIn("data/metrics/", reskill_run)
        self.assertIn("no GitHub Models/OpenAI reskill fallback", reskill_run)
        self.assertNotIn("${GITHUB_MODELS_MODEL}", reskill_run)
        self.assertNotIn('RESKILL_SOURCE="github-models"', reskill_run)
        self.assertNotIn("used GitHub Models API fallback", reskill_run)
        self.assertIn("--agent weekly-analysis", reskill_run)
        self.assertIn('Read the file at ${RESKILL_PROMPT}. Write the complete reskill markdown to ${RESKILL_OUTPUT}.', reskill_run)
        self.assertIn('test -s "$RESKILL_OUTPUT"', reskill_run)
        self.assertIn('RESKILL_FAILURE_CLASS="writer_contract_failure"', reskill_run)
        self.assertNotIn("--allow-tool=glob", reskill_run)
        self.assertNotIn("--allow-tool=grep", reskill_run)
        # Prompt is written to a well-known path, not a temp file
        self.assertIn('RESKILL_PROMPT=".squad/reskill/current-prompt.md"', reskill_run)

        analyze = workflow["jobs"]["analyze"]
        preflight_step = next((s for s in analyze["steps"] if s.get("name") == "Render and preflight analysis prompt"), None)
        self.assertIsNotNone(preflight_step)
        preflight_run = preflight_step["run"]
        self.assertIn("--prompt-token-budget", preflight_run)
        self.assertIn("--preflight-report-json", preflight_run)
        self.assertIn("--preflight-report-md", preflight_run)
        self.assertIn("--print-prompt > \"$PROMPT_FILE\"", preflight_run)
        self.assertIn("--context-files \"$PROMPT_FILE\"", preflight_run)
        self.assertIn("promotion_policy=", preflight_run)
        self.assertIn("staged/candidate-only", preflight_run)

        run_analysis_step = next((s for s in analyze["steps"] if s.get("name") == "Run analysis"), None)
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
        self.assertIn('Read the file at ${PROMPT_FILE}. Write the complete weekly analysis markdown to ${OUTPUT_FILE}.', run_analysis)
        self.assertIn('if ! test -s "$OUTPUT_FILE"; then', run_analysis)
        self.assertIn('FINAL_FAILURE_CLASS="writer_contract_failure"', run_analysis)
        self.assertNotIn("--allow-tool=glob", run_analysis)
        self.assertNotIn("--allow-tool=grep", run_analysis)
        self.assertIn('if [ "$FAILURE_CLASS" = "copilot_token_failure" ] || [ "$FAILURE_CLASS" = "copilot_inaccessible" ]; then', run_analysis)
        self.assertIn("failing without no-AI fallback", run_analysis)
        self.assertIn('echo "copilot is not available: command not found" > "$COPILOT_LOG"', run_analysis)
        self.assertIn("--exit-code 127", run_analysis)
        self.assertIn("No publishable Copilot summary was produced", run_analysis)
        self.assertIn("current published article can be preserved", run_analysis)
        self.assertIn("python3 scripts/analyze_fallback.py", run_analysis)
        self.assertIn('--press-context "$PRESS_FILE"', run_analysis)
        self.assertIn("--no-ai", run_analysis)
        self.assertIn('ANALYSIS_SOURCE="no-ai"', run_analysis)
        self.assertNotIn('ANALYSIS_SOURCE="github-models"', run_analysis)
        self.assertNotIn("falling back to GitHub Models API", run_analysis)

        manifest_step = next((s for s in analyze["steps"] if s.get("name") == "Emit publish eligibility manifest"), None)
        self.assertIsNotNone(manifest_step)
        manifest_run = manifest_step["run"]
        self.assertEqual(manifest_step["env"]["PREFLIGHT_REPORT"], "${{ steps.prompt-preflight.outputs.preflight_report_json }}")
        self.assertIn('--preflight-report "$PREFLIGHT_REPORT"', manifest_run)

    def test_generate_workflow_runs_rollups_and_commits_all_content(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        deploy_job = workflow["jobs"]["deploy"]
        build_site_step = next((s for s in deploy_job["steps"] if s.get("name") == "Build site"), None)
        self.assertIsNotNone(build_site_step)
        self.assertEqual(build_site_step["run"], "hugo --minify")

        pagefind_step = next((s for s in deploy_job["steps"] if s.get("name") == "Build search index"), None)
        self.assertIsNotNone(pagefind_step)
        self.assertEqual(pagefind_step["run"], "npx pagefind --site public/")

        generate_job = workflow["jobs"]["generate"]
        generate_rollups_step = next((s for s in generate_job["steps"] if s.get("name") == "Generate rollups"), None)
        self.assertIsNotNone(generate_rollups_step)
        self.assertEqual(generate_rollups_step["run"], "python3 scripts/generate_rollups.py")

        commit_step = next((s for s in generate_job["steps"] if s.get("name") == "Commit generated content to data branch"), None)
        self.assertIsNotNone(commit_step)
        commit_run = commit_step["run"]
        self.assertIn("content/weekly", commit_run)
        self.assertIn("content/monthly", commit_run)
        self.assertIn("content/yearly", commit_run)
        self.assertIn("content/weekly/", commit_run)
        self.assertIn("content/monthly/", commit_run)
        self.assertIn("content/yearly/", commit_run)
        self.assertIn("GITHUB_WORKSPACE", commit_run)
        self.assertIn('case "$PAGE_PATH" in', commit_run)
        self.assertIn("Expected PAGE_PATH under content/weekly/", commit_run)

        upload_step = next((s for s in generate_job["steps"] if s.get("name") == "Upload generated content artifact"), None)
        self.assertIsNotNone(upload_step)
        self.assertIn("content/monthly/", upload_step["with"]["path"])
        self.assertIn("content/yearly/", upload_step["with"]["path"])
        promoted_upload = next((s for s in generate_job["steps"] if s.get("name") == "Upload promoted analyzed artifact"), None)
        self.assertIsNotNone(promoted_upload)
        self.assertEqual(promoted_upload["with"]["name"], "promoted-analyzed-data")

    def test_sync_publish_to_main_excludes_squad_state_and_regenerates_rollups(self) -> None:
        workflow_path = Path(".github/workflows/sync-publish-to-main.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        sync_job = workflow["jobs"]["sync"]
        sync_step = next((s for s in sync_job["steps"] if s.get("name") == "Sync data from publish"), None)
        self.assertIsNotNone(sync_step)

        sync_run = sync_step["run"]
        for generated_path in (
            "data/raw/",
            "data/analyzed/",
            "data/metrics/",
            "content/weekly/",
            "content/monthly/",
            "content/yearly/",
        ):
            self.assertIn(generated_path, sync_run)

        self.assertIn("python3 scripts/generate_rollups.py", sync_run)
        self.assertLess(sync_run.index("python3 scripts/generate_rollups.py"), sync_run.index("git add -A"))
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
        analyzed_download = next((s for s in notify_job["steps"] if _uses_action(s, "actions/download-artifact") and s.get("with", {}).get("path") == "data/analyzed/"), None)
        self.assertIsNotNone(analyzed_download)
        self.assertEqual(analyzed_download["with"]["name"], "promoted-analyzed-data")

        webhook_step = next((s for s in notify_job["steps"] if s.get("name") == "Post to webhook"), None)
        self.assertIsNotNone(webhook_step)
        self.assertEqual(webhook_step["if"], "env.WEBHOOK_URL != ''")
        self.assertEqual(webhook_step["env"]["WEBHOOK_URL"], "${{ secrets.WEBHOOK_URL }}")

        release_step = next((s for s in notify_job["steps"] if s.get("name") == "Create GitHub Release"), None)
        self.assertIsNotNone(release_step)
        self.assertEqual(release_step["env"]["SUMMARY_FILE"], "${{ needs.analyze.outputs.summary_file }}")
        release_run = release_step["run"]
        self.assertIn('gh release view "$TAG"', release_run)
        self.assertIn('gh release edit "$TAG"', release_run)
        self.assertIn('gh release create "$TAG"', release_run)

        webhook_run = webhook_step["run"]
        self.assertIn("curl -s -X POST \"$WEBHOOK_URL\"", webhook_run)
        self.assertIn("https://jmservera.github.io/SquadScope/weekly/", webhook_run)
        # JSON is now built with jq to prevent injection — check for jq invocation
        self.assertIn("jq -n", webhook_run)
        self.assertIn("📊 **SquadScope Week", webhook_run)
        self.assertIn("Webhook post failed (non-critical)", webhook_run)

    def test_podcaster_handoff_runs_only_after_normal_deploy_without_blocking_deploy(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        podcaster_job = workflow["jobs"]["podcaster-handoff"]
        self.assertEqual(podcaster_job["needs"], ["analyze", "generate", "deploy"])
        checkout_step = next((s for s in podcaster_job["steps"] if s.get("name") == "Check out repository"), None)
        self.assertIsNotNone(checkout_step)
        self.assertTrue(_uses_action(checkout_step, "actions/checkout"))
        self.assertFalse(checkout_step["with"]["persist-credentials"])
        download_step = next((s for s in podcaster_job["steps"] if s.get("name") == "Download analysis candidate"), None)
        self.assertIsNotNone(download_step)
        self.assertTrue(_uses_action(download_step, "actions/download-artifact"))
        self.assertEqual(podcaster_job["if"], "${{ needs.analyze.outputs.run_mode == 'normal' }}")
        self.assertNotIn("continue-on-error", podcaster_job)
        self.assertNotIn("force-replace", podcaster_job["if"])
        self.assertNotIn("restore", podcaster_job["if"])

        deploy_job = workflow["jobs"]["deploy"]
        self.assertEqual(deploy_job["needs"], ["crawl", "analyze", "generate"])
        self.assertNotIn("podcaster-handoff", deploy_job["needs"])

        notify_step = next((s for s in podcaster_job["steps"] if s.get("name") == "Notify Podcaster"), None)
        self.assertIsNotNone(notify_step)
        self.assertEqual(notify_step["env"]["PODCASTER_ENDPOINT"], "${{ vars.PODCASTER_ENDPOINT }}")
        self.assertEqual(notify_step["env"]["PODCASTER_API_KEY"], "${{ secrets.PODCASTER_API_KEY }}")
        run_script = notify_step["run"]
        self.assertIn("article_url_from_page_path", run_script)
        self.assertIn("scripts/publish_manifest.py assert-eligible", run_script)
        self.assertIn("publish manifest is not eligible", run_script)
        self.assertIn("scripts/podcaster_handoff.py", run_script)
        self.assertIn('--article-path "$PAGE_PATH"', run_script)
        self.assertIn('--publish-run-id "$PUBLISH_RUN_ID"', run_script)
        self.assertIn('--publish-mode "$RUN_MODE"', run_script)
        self.assertIn('--manifest "$MANIFEST_FILE"', run_script)
        self.assertNotIn("weekly article publication remains complete", run_script)
        self.assertNotIn("--force", run_script)
        self.assertNotIn("--dry-run", run_script)
        self.assertNotIn("echo $PODCASTER_API_KEY", run_script)
        self.assertNotIn("curl", run_script)

    def test_podcaster_smoke_workflow_exercises_real_weekly_payload_shape(self) -> None:
        workflow_path = Path(".github/workflows/podcaster-handoff-smoke.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        inputs = workflow[True]["workflow_dispatch"]["inputs"]
        self.assertIn("week", inputs)
        self.assertIn("article_url", inputs)
        self.assertIn("article_path", inputs)
        self.assertIn("article_sha256", inputs)
        self.assertEqual(inputs["article_sha256"]["default"], "")

        smoke_job = workflow["jobs"]["smoke"]
        smoke_step = next((s for s in smoke_job["steps"] if s.get("name") == "Smoke test Podcaster dry run"), None)
        self.assertIsNotNone(smoke_step)
        run_script = smoke_step["run"]
        self.assertIn('if [ ! -f "$ARTICLE_PATH" ]', run_script)
        self.assertIn("hashlib.sha256(article.read_bytes()).hexdigest()", run_script)
        self.assertIn('"source_artifacts": [', run_script)
        self.assertIn('"same_day_reuse"', run_script)
        self.assertIn("build_payload(", run_script)
        self.assertIn('"podcast_config"', run_script)
        self.assertIn('"script_directions"', run_script)
        self.assertIn('"spotify_publish"', run_script)
        self.assertIn('"article_content"', run_script)
        self.assertIn("--manifest .podcaster-smoke/publish-manifest.json", run_script)
        self.assertIn("--podcast-config config/podcast.json", run_script)
        self.assertIn("--podcaster-dry-run", run_script)

    def test_publish_workflow_uses_candidate_manifest_before_promotion(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        analyze = workflow["jobs"]["analyze"]
        self.assertEqual(analyze["outputs"]["summary_file"], "${{ steps.analysis-context.outputs.published_output_file }}")
        self.assertEqual(
            analyze["outputs"]["candidate_summary_file"],
            "${{ steps.analysis-context.outputs.candidate_output_file }}",
        )
        self.assertEqual(
            analyze["outputs"]["publish_manifest_file"],
            "${{ steps.analysis-context.outputs.publish_manifest_file }}",
        )

        prepare_step = next((s for s in analyze["steps"] if s.get("name") == "Prepare analysis context"), None)
        self.assertIsNotNone(prepare_step)
        prepare_run = prepare_step["run"]
        self.assertIn("data/candidates", prepare_run)
        self.assertIn("candidate_output_file", prepare_run)
        self.assertIn("publish_manifest_file", prepare_run)
        self.assertIn("published_output_file=data/analyzed", prepare_run)

        manifest_step = next((s for s in analyze["steps"] if s.get("name") == "Emit publish eligibility manifest"), None)
        self.assertIsNotNone(manifest_step)
        manifest_run = manifest_step["run"]
        self.assertIn("scripts/publish_manifest.py create", manifest_run)
        self.assertIn("--analysis-source", manifest_run)
        self.assertIn("--analysis-model", manifest_run)
        self.assertIn('--validation-status "$VALIDATION_STATUS"', manifest_run)
        self.assertIn("--run-mode", manifest_run)
        self.assertIn("--source-refresh-policy", manifest_run)
        self.assertIn('git checkout origin/publish -- "$PUBLISHED_SUMMARY"', manifest_run)

        assert_step = next((s for s in analyze["steps"] if s.get("name") == "Assert candidate is eligible for promotion"), None)
        self.assertIsNotNone(assert_step)
        self.assertIn("scripts/publish_manifest.py assert-eligible", assert_step["run"])

        self.assertEqual(analyze["outputs"]["publish_head_sha"], "${{ steps.publish-base.outputs.sha }}")
        commit_step = next((s for s in analyze["steps"] if s.get("name") == "Commit analysis and learnings to data branch"), None)
        self.assertIsNone(commit_step)

        upload_candidate = next((s for s in analyze["steps"] if s.get("name") == "Upload analysis candidate"), None)
        self.assertIsNotNone(upload_candidate)
        self.assertEqual(upload_candidate["if"], "always()")

        generate = workflow["jobs"]["generate"]
        generate_raw_download = next(
            (
                s
                for s in generate["steps"]
                if s.get("name") == "Download raw crawl artifact"
                and _uses_action(s, "actions/download-artifact")
                and s.get("with", {}).get("name") == "raw-data"
                and s.get("with", {}).get("path") == "data/raw/"
            ),
            None,
        )
        self.assertIsNotNone(generate_raw_download)

        generate_step = next((s for s in generate["steps"] if s.get("name") == "Generate weekly content"), None)
        self.assertIsNotNone(generate_step)
        self.assertIn('assert-eligible --manifest "$MANIFEST_FILE"', generate_step["run"])
        self.assertIn("candidate_content_path", generate_step["run"])
        self.assertIn("scripts/promotion_guard.py --manifest", generate_step["run"])

        content_commit_step = next((s for s in generate["steps"] if s.get("name") == "Commit generated content to data branch"), None)
        self.assertIsNotNone(content_commit_step)
        content_commit_run = content_commit_step["run"]
        self.assertIn("Publish branch drifted between analyze and content promotion", content_commit_run)
        self.assertIn("backup-existing", content_commit_run)
        self.assertIn('--path "data/published/${WEEK}/promotion-manifest.json"', content_commit_run)
        self.assertIn("promotion-guard-tool.py --manifest", content_commit_run)
        self.assertIn("data/published/", content_commit_run)
        self.assertIn("--force-with-lease", content_commit_run)

    def test_rerun_mode_inputs_and_guards_are_declared(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        inputs = workflow[True]["workflow_dispatch"]["inputs"]

        self.assertEqual(inputs["run_mode"]["default"], "normal")
        self.assertIn("restore", inputs["run_mode"]["options"])
        self.assertEqual(inputs["source_refresh_policy"]["default"], "reuse-same-day")
        self.assertIn("force-refresh", inputs["source_refresh_policy"]["options"])

        crawl_steps = workflow["jobs"]["crawl"]["steps"]
        validate_step = next((s for s in crawl_steps if s.get("name") == "Validate rerun mode"), None)
        self.assertIsNotNone(validate_step)
        self.assertIn("scripts/rerun_modes.py", validate_step["run"])

        run_crawler = next((s for s in crawl_steps if s.get("name") == "Run crawler"), None)
        self.assertIn("--reuse-artifact", run_crawler["run"])
        self.assertIn("--source-refresh-policy", run_crawler["run"])


    def test_notify_failure_job_creates_or_updates_issue(self) -> None:
        workflow_path = Path(".github/workflows/crawl-and-publish.yml")
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        notify_failure_job = workflow["jobs"]["notify-failure"]
        self.assertEqual(notify_failure_job["needs"], ["crawl", "analyze", "generate", "deploy", "notify"])
        self.assertEqual(notify_failure_job["if"], "${{ always() && contains(needs.*.result, 'failure') }}")
        self.assertEqual(notify_failure_job["permissions"], {"actions": "read", "issues": "write"})

        create_issue_step = next((s for s in notify_failure_job["steps"] if s.get("name") == "Create or update failure issue"), None)
        self.assertIsNotNone(create_issue_step)
        self.assertEqual(create_issue_step["env"]["GITHUB_TOKEN"], "${{ secrets.GITHUB_TOKEN }}")
        create_issue_run = create_issue_step["run"]
        self.assertIn('gh run view "$RUN_ID" --json jobs', create_issue_run)
        self.assertEqual(create_issue_step["env"]["RUN_ID"], "${{ github.run_id }}")
        self.assertIn('gh issue list --state open --search', create_issue_run)
        self.assertIn('gh issue comment "$ISSUE_NUM"', create_issue_run)
        self.assertIn('gh issue create', create_issue_run)
        self.assertIn('Crawl and publish pipeline failed', create_issue_run)


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

            with mock.patch.object(crawl, "parse_args", return_value=args), mock.patch.dict(
                "os.environ", {"GITHUB_TOKEN": "token"}, clear=False
            ), mock.patch.object(crawl, "GitHubClient", FakeClient), mock.patch.object(
                crawl, "load_previous_star_snapshot", return_value={"octo/momentum-watch": 145}
            ), mock.patch.object(crawl, "utc_now", return_value=FIXED_RUN_TIME), mock.patch.object(
                crawl, "snapshots_dir", return_value=snapshot_dir
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

            invalid_path = base / "data" / "analyzed" / "invalid-summary.md"
            invalid_path.write_text(make_analysis_markdown().replace("quality_score: 86", "quality_score: 40"), encoding="utf-8")

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

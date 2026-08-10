from __future__ import annotations

import json
import shutil
import subprocess
import tomllib
from pathlib import Path
from xml.etree import ElementTree

import pytest
import yaml

from scripts.discover_topic_candidates import update_candidate_registry
from scripts.manage_topic_hubs import create_dynamic_hubs

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT / ".test-workspaces" / "topic-hub-lifecycle"

SEED_HUBS = {
    "ai-coding-agents": "AI Coding Agents",
    "mcp-ecosystem": "MCP Ecosystem",
    "open-source-llms": "Open-Source LLMs",
    "developer-tools": "Developer Tools",
    "ai-agents-in-healthcare": "AI Agents in Healthcare",
}


def _write_candidate_fixture(root: Path) -> None:
    (root / "config").mkdir(parents=True)
    (root / "data" / "taxonomy").mkdir(parents=True)
    (root / "config" / "observatory.toml").write_text(
        """[repo_pages]
recurrence_threshold_distinct_weekly_issues = 3

[topic_hubs]
seed_topics = ["AI Coding Agents"]

[topic_hubs.dynamic_creation]
enabled = false
min_weekly_issues = 4
lookback_days = 62
log_path = "data/topic-hubs/dynamic-topic-creation.log"
ignore_topics = ["ignored-candidate"]
""",
        encoding="utf-8",
    )
    (root / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps(
            {
                "terms": {
                    "ai-coding-agents": {
                        "display_name": "AI Coding Agents",
                        "slug": "ai-coding-agents",
                        "aliases": ["ai-agents"],
                        "is_hub": True,
                        "promoted": True,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    for week in range(27, 32):
        weekly = root / "content" / "weekly" / "2026" / f"W{week:02d}.md"
        weekly.parent.mkdir(parents=True, exist_ok=True)
        tags = ["edge-ai", "ignored-candidate", "ai-agents"] if week >= 28 else ["stale-only"]
        weekly.write_text(
            f'---\ntitle: "Week {week}"\ndate: 2026-07-01\nweek: "2026-W{week:02d}"\n'
            f'tags: {json.dumps(tags)}\ncategories: ["weekly"]\n---\nBody\n',
            encoding="utf-8",
        )
        summary = root / "data" / "analyzed" / f"2026-W{week:02d}-summary.md"
        summary.parent.mkdir(parents=True, exist_ok=True)
        heading = "Edge AI" if week >= 28 else "Stale Only"
        summary.write_text(
            f'---\ntitle: "Week {week}"\nweek: "2026-W{week:02d}"\n'
            f"tags: {json.dumps(tags)}\n---\n\n**{heading}.** Supporting analysis.\n",
            encoding="utf-8",
        )
        raw = root / "data" / "raw" / f"2026-W{week:02d}.json"
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw_topic = "edge-ai" if week >= 28 else "stale-only"
        raw.write_text(
            json.dumps(
                {
                    "week": f"2026-W{week:02d}",
                    "new_repos": [{"full_name": "example/edge", "topics": [raw_topic]}],
                    "trending_repos": [],
                    "signals": {"top_topics": [{"topic": raw_topic, "count": 8}]},
                }
            ),
            encoding="utf-8",
        )


def _write_candidate_registry(root: Path, candidates: dict[str, dict[str, object]]) -> None:
    path = root / "data" / "taxonomy" / "topic-candidates.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "as_of_week": "2026-W31",
                "policy": {"min_weekly_issues": 4, "lookback_days": 62},
                "candidates": candidates,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _candidate(title: str, weeks: list[str], *, eligible: bool = True) -> dict[str, object]:
    slug = title.lower().replace(" ", "-")
    return {
        "display_name": title,
        "slug": slug,
        "aliases": [slug],
        "first_seen_week": min(weeks),
        "last_seen_week": max(weeks),
        "weekly_issue_count": len(weeks),
        "evidence_weeks": weeks,
        "sources": [
            {
                "week": week,
                "source_type": "summary_tag",
                "source_path": f"data/analyzed/{week}-summary.md",
                "signal": slug,
            }
            for week in weeks
        ],
        "supporting_signals": [
            {
                "week": weeks[-1],
                "support_type": "analysis-summary",
                "source_path": f"data/analyzed/{weeks[-1]}-summary.md",
                "detail": slug,
            }
        ],
        "eligible": eligible,
    }


def test_candidate_registry_is_auditable_filtered_and_byte_stable(tmp_path: Path) -> None:
    _write_candidate_fixture(tmp_path)
    output = tmp_path / "data" / "taxonomy" / "topic-candidates.json"

    assert update_candidate_registry(root=tmp_path) is True
    first = output.read_bytes()
    assert update_candidate_registry(root=tmp_path) is False
    assert update_candidate_registry(root=tmp_path, check=True) is False
    assert output.read_bytes() == first

    payload = json.loads(first)
    candidate = payload["candidates"]["edge-ai"]
    assert candidate["weekly_issue_count"] == 4
    assert candidate["evidence_weeks"] == [
        "2026-W28",
        "2026-W29",
        "2026-W30",
        "2026-W31",
    ]
    assert candidate["eligible"] is True
    assert {item["support_type"] for item in candidate["supporting_signals"]} == {
        "analysis-summary",
        "recurring-repository-cluster",
    }
    assert "ignored-candidate" not in payload["candidates"]
    assert "ai-agents" not in payload["candidates"]
    assert payload["candidates"]["stale-only"]["eligible"] is False

    output.write_text("{}\n", encoding="utf-8")
    assert update_candidate_registry(root=tmp_path, check=True) is True
    assert output.read_text(encoding="utf-8") == "{}\n"


def test_candidate_registry_converges_after_promotion_mutates_topics(tmp_path: Path) -> None:
    _write_candidate_fixture(tmp_path)
    config_path = tmp_path / "config" / "observatory.toml"
    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace("enabled = false", "enabled = true"),
        encoding="utf-8",
    )
    (tmp_path / "content" / "topics").mkdir(parents=True, exist_ok=True)

    assert update_candidate_registry(root=tmp_path) is True

    created = create_dynamic_hubs(
        root=tmp_path,
        config_path=config_path,
        current_date="2026-08-05T12:00:00Z",
    )
    assert created == [tmp_path / "content" / "topics" / "edge-ai" / "_index.md"]

    registry = json.loads(
        (tmp_path / "data" / "taxonomy" / "topics.json").read_text(encoding="utf-8")
    )
    assert registry["terms"]["edge-ai"]["promoted"] is True

    # Promotion changed discovery input, so the registry is stale until refreshed.
    assert update_candidate_registry(root=tmp_path, check=True) is True
    assert update_candidate_registry(root=tmp_path) is True

    output = tmp_path / "data" / "taxonomy" / "topic-candidates.json"
    refreshed = output.read_bytes()
    assert "edge-ai" not in json.loads(refreshed)["candidates"]
    assert update_candidate_registry(root=tmp_path, check=True) is False
    assert update_candidate_registry(root=tmp_path) is False
    assert output.read_bytes() == refreshed


def test_seed_topic_hubs_have_unique_metadata_and_dataset_links() -> None:
    registry = json.loads((ROOT / "data" / "taxonomy" / "topics.json").read_text(encoding="utf-8"))
    seed_topics = {
        slug: term["display_name"]
        for slug, term in registry["terms"].items()
        if term["is_hub"] and term["promoted"]
    }
    assert seed_topics == SEED_HUBS

    descriptions: set[str] = set()
    for slug, title in seed_topics.items():
        hub_path = ROOT / "content" / "topics" / slug / "_index.md"
        content = hub_path.read_text(encoding="utf-8")
        assert f'title: "{title}"' in content
        assert "description:" in content
        assert "dataset_highlights:" in content
        assert "/state-of/open-source-ai-2026/" in content
        description_line = next(
            line for line in content.splitlines() if line.startswith("description:")
        )
        descriptions.add(description_line)

    assert len(descriptions) == len(SEED_HUBS)


def test_dynamic_topic_creation_is_threshold_driven_and_additive() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "weekly" / "2026").mkdir(parents=True)
    (WORKSPACE / "content" / "topics" / "quiet-existing").mkdir(parents=True)

    (WORKSPACE / "config" / "observatory.toml").write_text(
        """[topic_hubs]
        seed_topics = [
          "AI Coding Agents",
          "MCP Ecosystem",
          "Open-Source LLMs",
          "Developer Tools",
          "AI Agents in Healthcare",
        ]

        [topic_hubs.dynamic_creation]
        enabled = true
        min_weekly_issues = 4
        lookback_days = 62
        log_path = "data/topic-hubs/dynamic-topic-creation.log"
        ignore_topics = []
        """,
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy").mkdir(parents=True)
    (WORKSPACE / "content" / "topics" / "quiet-existing" / "_index.md").write_text(
        '---\ntitle: "Quiet Existing"\n---\n',
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps(
            {
                "terms": {
                    "edge-ai-workflows": {
                        "display_name": "Edge AI Workflows",
                        "slug": "edge-ai-workflows",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 4,
                        "times_used": 4,
                        "weekly_issue_count": 4,
                        "is_hub": False,
                        "promoted": False,
                    },
                    "quiet-existing": {
                        "display_name": "Quiet Existing",
                        "slug": "quiet-existing",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 4,
                        "times_used": 4,
                        "weekly_issue_count": 4,
                        "is_hub": False,
                        "promoted": False,
                    },
                    "forked-candidate-source": {
                        "display_name": "Forked Candidate Source",
                        "slug": "forked-candidate-source",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 0,
                        "times_used": 0,
                        "weekly_issue_count": 0,
                        "is_hub": False,
                        "promoted": False,
                    },
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    weeks = ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]
    _write_candidate_registry(
        WORKSPACE,
        {
            "edge-ai-workflows": _candidate("Edge AI Workflows", weeks),
            "forked-candidate-source": _candidate(
                "Forked Candidate Source", ["2026-W31"], eligible=False
            ),
        },
    )
    for week in weeks:
        weekly = WORKSPACE / "content" / "weekly" / "2026" / f"W{week[-2:]}.md"
        weekly.write_text(
            f'---\ntitle: "{week}"\ndate: 2026-07-27\nweek: "{week}"\n'
            'tags: ["edge-ai-workflows"]\ncategories: ["weekly"]\ntopics: []\n---\nBody\n',
            encoding="utf-8",
        )

    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )

    assert created == [WORKSPACE / "content" / "topics" / "edge-ai-workflows" / "_index.md"]
    new_hub = created[0].read_text(encoding="utf-8")
    assert "Edge AI Workflows" in new_hub
    assert "min_weekly_issues: 4" in new_hub
    assert "persists through quiet weeks" in new_hub.lower()
    assert (WORKSPACE / "content" / "topics" / "quiet-existing" / "_index.md").exists()

    log = (WORKSPACE / "data" / "topic-hubs" / "dynamic-topic-creation.log").read_text(
        encoding="utf-8"
    )
    assert "threshold=4" in log
    assert "create topic='Edge AI Workflows'" in log
    registry = json.loads(
        (WORKSPACE / "data" / "taxonomy" / "topics.json").read_text(encoding="utf-8")
    )
    assert registry["terms"]["edge-ai-workflows"]["is_hub"] is True
    assert registry["terms"]["edge-ai-workflows"]["promoted"] is True
    assert registry["terms"]["edge-ai-workflows"]["weekly_issue_count"] == 4
    for week in weeks:
        weekly = WORKSPACE / "content" / "weekly" / "2026" / f"W{week[-2:]}.md"
        assert 'topics: ["Edge AI Workflows"]' in weekly.read_text(encoding="utf-8")
    from scripts.generate_content import load_topic_vocabulary

    topic_titles, topic_aliases = load_topic_vocabulary(
        registry_path=WORKSPACE / "data" / "taxonomy" / "topics.json"
    )
    assert "Edge AI Workflows" in topic_titles
    assert topic_aliases["edge-ai-workflows"] == "Edge AI Workflows"
    assert not (WORKSPACE / "content" / "topics" / "forked-candidate-source").exists()
    assert not (WORKSPACE / "content" / "topics" / "tag-only-signal").exists()

    _write_candidate_registry(WORKSPACE, {})
    assert (
        create_dynamic_hubs(
            root=WORKSPACE,
            config_path=WORKSPACE / "config" / "observatory.toml",
            current_date="2026-08-05T12:57:30Z",
        )
        == []
    )
    assert created[0].exists()

    current_week = WORKSPACE / "content" / "weekly" / "2026" / "W32.md"
    current_week.write_text(
        '---\ntitle: "2026-W32"\ndate: 2026-08-03\nweek: "2026-W32"\n'
        'tags: ["unrelated"]\ncategories: ["weekly"]\ntopics: []\n---\nBody\n',
        encoding="utf-8",
    )
    raw = WORKSPACE / "data" / "raw" / "2026-W32.json"
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(
        json.dumps(
            {
                "week": "2026-W32",
                "new_repos": [{"full_name": "example/current", "topics": ["edge-ai-workflows"]}],
                "trending_repos": [],
                "signals": {"top_topics": []},
            }
        ),
        encoding="utf-8",
    )
    assert (
        create_dynamic_hubs(
            root=WORKSPACE,
            config_path=WORKSPACE / "config" / "observatory.toml",
            current_date="2026-08-05T12:57:30Z",
        )
        == []
    )
    assert 'topics: ["Edge AI Workflows"]' in current_week.read_text(encoding="utf-8")


def test_preview_dynamic_hubs_reports_without_mutating_and_works_while_disabled() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "weekly" / "2026").mkdir(parents=True)
    (WORKSPACE / "content" / "topics" / "quiet-existing").mkdir(parents=True)

    (WORKSPACE / "config" / "observatory.toml").write_text(
        """[topic_hubs]
        seed_topics = ["AI Coding Agents"]

        [topic_hubs.dynamic_creation]
        enabled = false
        min_weekly_issues = 4
        lookback_days = 62
        log_path = "data/topic-hubs/dynamic-topic-creation.log"
        ignore_topics = ["ignored-candidate"]
        """,
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy").mkdir(parents=True)
    (WORKSPACE / "content" / "topics" / "quiet-existing" / "_index.md").write_text(
        '---\ntitle: "Quiet Existing"\n---\n',
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps({"terms": {}}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    weeks = ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]
    _write_candidate_registry(
        WORKSPACE,
        {
            "edge-ai-workflows": _candidate("Edge AI Workflows", weeks),
            "ignored-candidate": _candidate("Ignored Candidate", weeks),
            "forked-candidate-source": _candidate(
                "Forked Candidate Source", ["2026-W31"], eligible=False
            ),
            "quiet-existing": _candidate("Quiet Existing", weeks),
        },
    )
    for week in weeks:
        weekly = WORKSPACE / "content" / "weekly" / "2026" / f"W{week[-2:]}.md"
        weekly.write_text(
            f'---\ntitle: "{week}"\ndate: 2026-07-27\nweek: "{week}"\n'
            'tags: ["edge-ai-workflows"]\ncategories: ["weekly"]\ntopics: []\n---\nBody\n',
            encoding="utf-8",
        )

    before = {
        path: path.read_text(encoding="utf-8") for path in WORKSPACE.rglob("*") if path.is_file()
    }

    from scripts.manage_topic_hubs import preview_dynamic_hubs

    report = preview_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )
    by_slug = {entry["slug"]: entry for entry in report}

    assert by_slug["edge-ai-workflows"]["action"] == "promote"
    assert (
        by_slug["edge-ai-workflows"]["proposed_hub_path"]
        == "content/topics/edge-ai-workflows/_index.md"
    )
    assert by_slug["edge-ai-workflows"]["proposed_weekly_assignments"] == [
        f"content/weekly/2026/W{week[-2:]}.md" for week in weeks
    ]
    assert by_slug["edge-ai-workflows"]["registry_effect"] == "create-new-term"
    assert by_slug["edge-ai-workflows"]["skip_reason"] is None
    assert by_slug["ignored-candidate"]["action"] == "skip"
    assert by_slug["ignored-candidate"]["skip_reason"] == "existing-or-ignored"
    assert by_slug["quiet-existing"]["skip_reason"] == "existing-or-ignored"
    assert by_slug["forked-candidate-source"]["skip_reason"] == "missing-supporting-evidence"

    # preview must never write anything, even while enabled = false
    after = {
        path: path.read_text(encoding="utf-8") for path in WORKSPACE.rglob("*") if path.is_file()
    }
    assert before == after
    assert not (WORKSPACE / "data" / "topic-hubs").exists()

    # create_dynamic_hubs(dry_run=True) must produce the same report and also
    # write nothing, regardless of the enabled flag.
    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
        dry_run=True,
    )
    assert created == []
    after_dry_run = {
        path: path.read_text(encoding="utf-8") for path in WORKSPACE.rglob("*") if path.is_file()
    }
    assert before == after_dry_run


def test_preview_dynamic_hubs_tolerates_malformed_registry_terms() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "weekly" / "2026").mkdir(parents=True)
    (WORKSPACE / "content" / "topics").mkdir(parents=True)

    (WORKSPACE / "config" / "observatory.toml").write_text(
        """[topic_hubs]
        seed_topics = ["AI Coding Agents"]

        [topic_hubs.dynamic_creation]
        enabled = false
        min_weekly_issues = 4
        lookback_days = 62
        log_path = "data/topic-hubs/dynamic-topic-creation.log"
        ignore_topics = []
        """,
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy").mkdir(parents=True)
    # A malformed registry (terms is a list, not a mapping) must not crash the preview.
    (WORKSPACE / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps({"terms": ["not", "a", "mapping"]}),
        encoding="utf-8",
    )
    weeks = ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]
    _write_candidate_registry(
        WORKSPACE, {"edge-ai-workflows": _candidate("Edge AI Workflows", weeks)}
    )
    for week in weeks:
        weekly = WORKSPACE / "content" / "weekly" / "2026" / f"W{week[-2:]}.md"
        weekly.write_text(
            f'---\ntitle: "{week}"\ndate: 2026-07-27\nweek: "{week}"\n'
            'tags: ["edge-ai-workflows"]\ncategories: ["weekly"]\ntopics: []\n---\nBody\n',
            encoding="utf-8",
        )

    from scripts.manage_topic_hubs import preview_dynamic_hubs

    report = preview_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )
    by_slug = {entry["slug"]: entry for entry in report}
    assert by_slug["edge-ai-workflows"]["registry_effect"] == "create-new-term"


def _write_allowlist_workspace(allow_topics: list[str], *, enabled: bool) -> list[str]:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "weekly" / "2026").mkdir(parents=True)
    (WORKSPACE / "content" / "topics").mkdir(parents=True)
    (WORKSPACE / "data" / "taxonomy").mkdir(parents=True)

    (WORKSPACE / "config" / "observatory.toml").write_text(
        f"""[topic_hubs]
        seed_topics = ["AI Coding Agents"]

        [topic_hubs.dynamic_creation]
        enabled = {str(enabled).lower()}
        min_weekly_issues = 4
        lookback_days = 62
        log_path = "data/topic-hubs/dynamic-topic-creation.log"
        allow_topics = {json.dumps(allow_topics)}
        ignore_topics = []
        """,
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps({"terms": {}}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    weeks = ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]
    _write_candidate_registry(
        WORKSPACE,
        {
            "edge-ai-workflows": _candidate("Edge AI Workflows", weeks),
            "quantum-tooling": _candidate("Quantum Tooling", weeks),
            "wasm-runtimes": _candidate("Wasm Runtimes", weeks),
        },
    )
    for week in weeks:
        weekly = WORKSPACE / "content" / "weekly" / "2026" / f"W{week[-2:]}.md"
        weekly.write_text(
            f'---\ntitle: "{week}"\ndate: 2026-07-27\nweek: "{week}"\n'
            'tags: ["edge-ai-workflows", "quantum-tooling", "wasm-runtimes"]\n'
            'categories: ["weekly"]\ntopics: []\n---\nBody\n',
            encoding="utf-8",
        )
    return weeks


def test_empty_allowlist_leaves_every_eligible_candidate_promotable() -> None:
    _write_allowlist_workspace([], enabled=False)

    from scripts.manage_topic_hubs import preview_dynamic_hubs

    report = preview_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )
    promoted = sorted(entry["slug"] for entry in report if entry["action"] == "promote")
    assert promoted == ["edge-ai-workflows", "quantum-tooling", "wasm-runtimes"]


def test_allowlist_bounds_preview_to_the_reviewed_canary() -> None:
    _write_allowlist_workspace(["quantum-tooling"], enabled=False)

    from scripts.manage_topic_hubs import preview_dynamic_hubs

    report = preview_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )
    by_slug = {entry["slug"]: entry for entry in report}
    assert by_slug["quantum-tooling"]["action"] == "promote"
    assert by_slug["edge-ai-workflows"]["action"] == "skip"
    assert by_slug["edge-ai-workflows"]["skip_reason"] == "not-in-allowlist"
    assert by_slug["wasm-runtimes"]["skip_reason"] == "not-in-allowlist"


def test_allowlist_bounds_the_enabled_promotion_transaction() -> None:
    _write_allowlist_workspace(["quantum-tooling"], enabled=True)

    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )

    assert [path.parent.name for path in created] == ["quantum-tooling"]
    assert (WORKSPACE / "content" / "topics" / "quantum-tooling" / "_index.md").exists()
    assert not (WORKSPACE / "content" / "topics" / "edge-ai-workflows").exists()
    assert not (WORKSPACE / "content" / "topics" / "wasm-runtimes").exists()

    registry = json.loads(
        (WORKSPACE / "data" / "taxonomy" / "topics.json").read_text(encoding="utf-8")
    )
    assert "quantum-tooling" in registry["terms"]
    assert "edge-ai-workflows" not in registry["terms"]
    assert "wasm-runtimes" not in registry["terms"]

    weekly = (WORKSPACE / "content" / "weekly" / "2026" / "W28.md").read_text(encoding="utf-8")
    assert "Quantum Tooling" in weekly
    assert "Edge AI Workflows" not in weekly

    log = (WORKSPACE / "data" / "topic-hubs" / "dynamic-topic-creation.log").read_text(
        encoding="utf-8"
    )
    assert "allowlist=['quantum-tooling']" in log


def test_shipped_config_never_enables_unbounded_dynamic_creation() -> None:
    # Live guard: enabling dynamic creation with an empty allowlist would promote every
    # eligible candidate (~1000+) in a single transaction. Keep the canary bounded.
    raw = tomllib.loads((ROOT / "config" / "observatory.toml").read_text(encoding="utf-8"))
    dynamic = raw["topic_hubs"]["dynamic_creation"]
    allow_topics = dynamic.get("allow_topics", [])
    assert isinstance(allow_topics, list)
    assert all(isinstance(slug, str) and slug for slug in allow_topics)
    if dynamic.get("enabled", False):
        assert allow_topics, (
            "dynamic_creation.enabled is true but allow_topics is empty; this would "
            "promote every eligible candidate in one transaction"
        )


def test_dynamic_topic_creation_does_not_create_below_threshold() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "weekly" / "2026").mkdir(parents=True)
    (WORKSPACE / "content" / "topics").mkdir(parents=True)
    (WORKSPACE / "config" / "observatory.toml").write_text(
        """[topic_hubs]
        seed_topics = [
          "AI Coding Agents",
          "MCP Ecosystem",
          "Open-Source LLMs",
          "Developer Tools",
          "AI Agents in Healthcare",
        ]

        [topic_hubs.dynamic_creation]
        enabled = true
        min_weekly_issues = 4
        lookback_days = 62
        log_path = "data/topic-hubs/dynamic-topic-creation.log"
        ignore_topics = []
        """,
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy").mkdir(parents=True)
    (WORKSPACE / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps(
            {
                "terms": {
                    "three-week-trend": {
                        "display_name": "Three Week Trend",
                        "slug": "three-week-trend",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 3,
                        "times_used": 3,
                        "weekly_issue_count": 3,
                        "is_hub": False,
                        "promoted": False,
                    }
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_candidate_registry(
        WORKSPACE,
        {
            "three-week-trend": _candidate(
                "Three Week Trend", ["2026-W29", "2026-W30", "2026-W31"], eligible=False
            )
        },
    )

    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )

    assert created == []
    assert not (WORKSPACE / "content" / "topics" / "three-week-trend").exists()


def test_disabled_dynamic_topic_creation_preserves_durable_state(
    capsys: pytest.CaptureFixture[str],
) -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    existing_hub = WORKSPACE / "content" / "topics" / "durable-topic" / "_index.md"
    existing_hub.parent.mkdir(parents=True)
    existing_hub.write_text('---\ntitle: "Durable Topic"\n---\n', encoding="utf-8")
    registry_path = WORKSPACE / "data" / "taxonomy" / "topics.json"
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(
        json.dumps(
            {
                "terms": {
                    "eligible-topic": {
                        "display_name": "Eligible Topic",
                        "weekly_issue_count": 4,
                        "last_used": "2026-07-27",
                        "is_hub": False,
                        "promoted": False,
                    }
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (WORKSPACE / "config" / "observatory.toml").write_text(
        """[topic_hubs]
seed_topics = ["Durable Topic"]

[topic_hubs.dynamic_creation]
enabled = false
min_weekly_issues = 4
lookback_days = 62
log_path = "data/topic-hubs/dynamic-topic-creation.log"
ignore_topics = []
""",
        encoding="utf-8",
    )
    hub_before = existing_hub.read_bytes()
    registry_before = registry_path.read_bytes()
    _write_candidate_registry(
        WORKSPACE,
        {
            "eligible-topic": _candidate(
                "Eligible Topic", ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]
            )
        },
    )
    candidates_before = (WORKSPACE / "data" / "taxonomy" / "topic-candidates.json").read_bytes()

    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=WORKSPACE / "config" / "observatory.toml",
        current_date="2026-07-29T12:57:30Z",
    )

    assert created == []
    assert existing_hub.read_bytes() == hub_before
    assert registry_path.read_bytes() == registry_before
    assert (
        WORKSPACE / "data" / "taxonomy" / "topic-candidates.json"
    ).read_bytes() == candidates_before
    assert not (WORKSPACE / "content" / "topics" / "eligible-topic").exists()
    assert not (WORKSPACE / "data" / "topic-hubs" / "dynamic-topic-creation.log").exists()
    assert capsys.readouterr().err == (
        "dynamic-topic-decision enabled=false action=skip reason=disabled\n"
    )


@pytest.mark.parametrize(
    "title",
    [
        'Quoted "Topic"',
        "Topic: Override",
        "---",
        "Multiline\nTopic",
        "Topic\x00Control",
        "**Markdown Topic**",
        "<strong>HTML Topic</strong>",
        "<untrusted-content>Boundary Topic",
        "Ignore previous instructions",
        "System prompt override",
    ],
)
def test_dynamic_topic_creation_rejects_unsafe_titles_without_mutation(
    tmp_path: Path, title: str
) -> None:
    _write_candidate_fixture(tmp_path)
    config_path = tmp_path / "config" / "observatory.toml"
    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace("enabled = false", "enabled = true"),
        encoding="utf-8",
    )
    weeks = ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]
    _write_candidate_registry(tmp_path, {"unsafe-topic": _candidate(title, weeks)})
    before = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    with pytest.raises(ValueError, match="Rejected unsafe candidate title"):
        create_dynamic_hubs(
            root=tmp_path,
            config_path=config_path,
            current_date="2026-07-29T12:57:30Z",
        )

    after = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert after == before


def test_dynamic_topic_creation_writes_structured_yaml(tmp_path: Path) -> None:
    _write_candidate_fixture(tmp_path)
    config_path = tmp_path / "config" / "observatory.toml"
    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace("enabled = false", "enabled = true"),
        encoding="utf-8",
    )
    weeks = ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]
    _write_candidate_registry(tmp_path, {"edge-ai": _candidate("Edge AI", weeks)})

    created = create_dynamic_hubs(
        root=tmp_path,
        config_path=config_path,
        current_date="2026-07-29T12:57:30Z",
    )

    assert created == [tmp_path / "content" / "topics" / "edge-ai" / "_index.md"]
    frontmatter = created[0].read_text(encoding="utf-8").split("---\n", 2)[1]
    parsed = yaml.safe_load(frontmatter)
    assert parsed["title"] == "Edge AI"
    assert parsed["params"]["discovery"]["observed_weeks"] == weeks


def test_dynamic_topic_creation_preserves_parseable_seed_topics_without_trailing_comma() -> None:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    (WORKSPACE / "config").mkdir(parents=True)
    (WORKSPACE / "content" / "topics").mkdir(parents=True)
    (WORKSPACE / "data" / "taxonomy").mkdir(parents=True)
    config_path = WORKSPACE / "config" / "observatory.toml"
    config_path.write_text(
        """[topic_hubs]
seed_topics = [
  "AI Coding Agents"
]

[topic_hubs.dynamic_creation]
enabled = true
min_weekly_issues = 4
lookback_days = 62
log_path = "data/topic-hubs/dynamic-topic-creation.log"
ignore_topics = []
""",
        encoding="utf-8",
    )
    (WORKSPACE / "data" / "taxonomy" / "topics.json").write_text(
        json.dumps(
            {
                "terms": {
                    "edge-ai-workflows": {
                        "display_name": "Edge AI Workflows",
                        "slug": "edge-ai-workflows",
                        "first_seen": "2026-07-01",
                        "last_used": "2026-07-27",
                        "count": 4,
                        "times_used": 4,
                        "weekly_issue_count": 4,
                        "is_hub": False,
                        "promoted": False,
                    }
                }
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_candidate_registry(
        WORKSPACE,
        {
            "edge-ai-workflows": _candidate(
                "Edge AI Workflows", ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]
            )
        },
    )

    created = create_dynamic_hubs(
        root=WORKSPACE,
        config_path=config_path,
        current_date="2026-07-29T12:57:30Z",
    )

    assert created == [WORKSPACE / "content" / "topics" / "edge-ai-workflows" / "_index.md"]
    parsed = tomllib.loads(config_path.read_text(encoding="utf-8"))
    assert parsed["topic_hubs"]["seed_topics"] == ["AI Coding Agents"]
    registry = json.loads((WORKSPACE / "data" / "taxonomy" / "topics.json").read_text())
    assert registry["terms"]["edge-ai-workflows"]["promoted"] is True


@pytest.mark.skipif(shutil.which("hugo") is None, reason="hugo is not installed")
def test_hugo_renders_topic_hubs_with_issue_cards_and_rss() -> None:
    destination = ROOT / ".test-workspaces" / "hugo-topic-hubs-public"
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["hugo", "--minify", "--destination", str(destination)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    page = (destination / "topics" / "ai-coding-agents" / "index.html").read_text(encoding="utf-8")
    assert "Topic hub" in page
    assert "Latest weekly signals" in page
    assert "Recent weekly issues" in page
    assert "Dataset highlights" in page
    assert "2026-W31" in page
    assert "rel=canonical href=https://claracle.com/topics/ai-coding-agents/" in page
    for slug, title in SEED_HUBS.items():
        rss = destination / "topics" / slug / "index.xml"
        assert rss.exists(), f"missing promoted topic feed: {slug}"
        root = ElementTree.parse(rss).getroot()
        rss_content = rss.read_text(encoding="utf-8")
        assert title in rss_content
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] in {"guid", "link"}:
                url = (element.text or "").strip()
                if url:
                    assert url.startswith("https://claracle.com/")

    ai_coding_feed = (destination / "topics" / "ai-coding-agents" / "index.xml").read_text(
        encoding="utf-8"
    )
    assert "Agent Work Moved Into the Operating Room" in ai_coding_feed
    assert "https://claracle.com/topics/ai-coding-agents/" in ai_coding_feed


@pytest.mark.skipif(shutil.which("hugo") is None, reason="hugo is not installed")
def test_hugo_home_topic_display_is_safe_without_topic_content_page() -> None:
    destination = ROOT / ".test-workspaces" / "hugo-unpaged-topic-public"
    temp_weekly = ROOT / "content" / "weekly" / "2026" / "W99.md"
    if destination.exists():
        shutil.rmtree(destination)
    temp_weekly.write_text(
        """---
title: "Temporary Unpaged Topic"
date: 2026-07-28T00:00:00+00:00
week: "2026-W99"
tags: ["temporary"]
categories: ["weekly"]
topics: ["Unpaged Topic"]
repos_featured: 1
stars_tracked: 1
top_repo: "example/repo"
summary: "Temporary taxonomy regression fixture."
draft: false
---
""",
        encoding="utf-8",
    )
    try:
        subprocess.run(
            ["hugo", "--minify", "--destination", str(destination)],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    finally:
        temp_weekly.unlink(missing_ok=True)

    home = (destination / "index.html").read_text(encoding="utf-8")
    assert "Unpaged Topic" in home

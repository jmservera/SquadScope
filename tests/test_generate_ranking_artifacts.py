from __future__ import annotations

import json
import shutil
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts import generate_data_pages, generate_ranking_artifacts

ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sample_repo(
    full_name: str, *, description: str, language: str, stars: int, topics: list[str]
) -> dict:
    owner, name = full_name.split("/", 1)
    return {
        "owner": owner,
        "name": name,
        "full_name": full_name,
        "description": description,
        "language": language,
        "stars": stars,
        "forks": 1,
        "created_at": "2026-01-01T00:00:00Z",
        "topics": topics,
        "url": f"https://github.com/{full_name}",
    }


def ranking_fixture_root(name: str) -> Path:
    root = ROOT / name
    shutil.rmtree(root, ignore_errors=True)
    (root / "data/raw").mkdir(parents=True, exist_ok=True)
    (root / "data/archive/recovered-W23-W29").mkdir(parents=True, exist_ok=True)
    return root


def base_payload(week: str, crawled_at: str, repos: list[dict]) -> dict:
    return {
        "week": week,
        "crawled_at": crawled_at,
        "trending_repos": repos,
        "new_repos": [],
        "metadata": {},
    }


def write_fixture_weeks(root: Path) -> None:
    long_description = (
        "AI agent toolkit for repository analysis with ranking context and search guidance "
        "that keeps growing across multiple observations without embedding unsafe text."
    )
    write_json(
        root / "data/raw/2026-W32.json",
        base_payload(
            "2026-W32",
            "2026-08-03T00:00:00Z",
            [
                sample_repo(
                    "alpha/ai-agent",
                    description=long_description,
                    language="Python",
                    stars=100,
                    topics=["ai", "agents"],
                ),
                sample_repo(
                    "beta/ai-builder",
                    description="AI builder for model orchestration.",
                    language="Rust",
                    stars=100,
                    topics=["ai"],
                ),
                sample_repo(
                    "mcp/tools",
                    description="Model Context Protocol helper for AI agents.",
                    language="TypeScript",
                    stars=90,
                    topics=["mcp"],
                ),
            ],
        ),
    )
    write_json(
        root / "data/raw/2026-W33.json",
        base_payload(
            "2026-W33",
            "2026-08-10T00:00:00Z",
            [
                sample_repo(
                    "alpha/ai-agent",
                    description=long_description,
                    language="Python",
                    stars=145,
                    topics=["ai", "agents"],
                ),
                sample_repo(
                    "beta/ai-builder",
                    description="AI builder for model orchestration.",
                    language="Rust",
                    stars=145,
                    topics=["ai"],
                ),
                sample_repo(
                    "mcp/tools",
                    description="Model Context Protocol helper for AI agents.",
                    language="TypeScript",
                    stars=210,
                    topics=["mcp", "ai"],
                ),
                sample_repo(
                    "delta/steady-project",
                    description="AI research reference project.",
                    language="Go",
                    stars=50,
                    topics=["ai"],
                ),
            ],
        ),
    )


def repo_observation(
    url: str = "https://github.com/example/repo",
) -> generate_data_pages.RepoObservation:
    return generate_data_pages.RepoObservation(
        week="2026-W33",
        crawled_at=generate_data_pages.parse_datetime("2026-08-10T00:00:00Z", "2026-W33"),
        source_bucket="trending_repos",
        source_path=ROOT / "data/raw/2026-W33.json",
        full_name="example/repo",
        display_name="example/repo",
        url=url,
        description="AI repository used for ranking tests.",
        language="Python",
        stars=42,
        forks=1,
        created_at="2026-01-01T00:00:00Z",
        topics=("ai",),
    )


def load_schema(name: str) -> Draft202012Validator:
    payload = json.loads((ROOT / f"data/schemas/{name}").read_text(encoding="utf-8"))
    return Draft202012Validator(payload)


def test_ranking_artifact_is_deterministic() -> None:
    root = ranking_fixture_root(".pytest-ranking-deterministic")
    try:
        write_fixture_weeks(root)
        first = generate_ranking_artifacts.build_outputs(root)
        second = generate_ranking_artifacts.build_outputs(root)
        assert first == second
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ranking_artifact_schema_version() -> None:
    root = ranking_fixture_root(".pytest-ranking-schema")
    try:
        write_fixture_weeks(root)
        payloads = generate_ranking_artifacts.build_ranking_payloads(root)
        envelope_validator = load_schema("observatory-envelope.schema.json")
        record_validator = load_schema("ranking-record.schema.json")
        payload = payloads["top-ai-repositories-this-month"]
        assert payload["schema_version"] == "1.0.0"
        assert payload["artifact_type"] == "ranking"
        envelope_validator.validate(payload)
        for record in payload["records"]:
            record_validator.validate(record)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ranking_artifact_github_url_validated() -> None:
    invalid = repo_observation(url="https://example.com/not-github")

    try:
        generate_ranking_artifacts.ranking_record(
            rank=1,
            obs=invalid,
            metric_key="stars",
            metric_value=42,
            metric_label="42 stars",
        )
    except ValueError as error:
        assert "https://github.com" in str(error)
    else:
        raise AssertionError("expected GitHub URL validation to fail")


def test_ranking_artifact_context_summary_truncated_at_160() -> None:
    source = ("word " * 50) + "unfinishedtoken"
    summary = generate_data_pages.build_context_summary(source)
    accessible_text = generate_data_pages.build_context_accessible_text(source)

    assert len(summary) <= 160
    assert summary.endswith("…")
    assert summary[:-1].split()[-1] == "word"
    assert len(accessible_text) > len(summary)
    assert len(accessible_text) <= 500
    assert accessible_text.endswith("unfinishedtoken")


def test_ranking_artifact_check_mode_passes() -> None:
    root = ranking_fixture_root(".pytest-ranking-check-pass")
    try:
        write_fixture_weeks(root)
        assert generate_ranking_artifacts.main(["--root", str(root)]) == 0
        assert generate_ranking_artifacts.main(["--root", str(root), "--check"]) == 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ranking_artifact_check_mode_fails_when_stale() -> None:
    root = ranking_fixture_root(".pytest-ranking-check-fail")
    try:
        write_fixture_weeks(root)
        assert generate_ranking_artifacts.main(["--root", str(root)]) == 0
        target = root / "static/data/rankings/top-ai-repositories-this-month.json"
        target.write_text(
            target.read_text(encoding="utf-8").replace("145", "144", 1), encoding="utf-8"
        )
        assert generate_ranking_artifacts.main(["--root", str(root), "--check"]) == 1
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ranking_artifact_malformed_raw_skipped() -> None:
    root = ranking_fixture_root(".pytest-ranking-malformed")
    try:
        write_fixture_weeks(root)
        (root / "data/raw/2026-W31.json").write_text("{not-json", encoding="utf-8")
        artifacts = generate_ranking_artifacts.discover_week_artifacts(
            raw_dir=root / "data/raw",
            archive_dir=root / "data/archive/recovered-W23-W29",
        )
        assert [artifact.week for artifact in artifacts] == ["2026-W32", "2026-W33"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ranking_artifact_empty_result_produces_valid_envelope() -> None:
    root = ranking_fixture_root(".pytest-ranking-empty")
    try:
        write_json(
            root / "data/raw/2026-W33.json",
            base_payload(
                "2026-W33",
                "2026-08-10T00:00:00Z",
                [
                    sample_repo(
                        "plain/blockchain-index",
                        description="Blockchain directory with ledger snapshots only.",
                        language="Go",
                        stars=10,
                        topics=["blockchain"],
                    )
                ],
            ),
        )
        payloads = generate_ranking_artifacts.build_ranking_payloads(root)
        top = payloads["top-ai-repositories-this-month"]
        assert top["records"] == []
        load_schema("observatory-envelope.schema.json").validate(top)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ranking_artifact_tied_metric_stable_order() -> None:
    root = ranking_fixture_root(".pytest-ranking-ties")
    try:
        write_fixture_weeks(root)
        payload = generate_ranking_artifacts.build_ranking_payloads(root)[
            "top-ai-repositories-this-month"
        ]
        names = [record["full_name"] for record in payload["records"]]
        assert names.index("alpha/ai-agent") < names.index("beta/ai-builder")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ranking_summary_has_all_three_rankings() -> None:
    root = ranking_fixture_root(".pytest-ranking-summary")
    try:
        write_fixture_weeks(root)
        payloads = generate_ranking_artifacts.build_ranking_payloads(root)
        summary = generate_ranking_artifacts.build_ranking_summary(payloads)
        assert [record["ranking_id"] for record in summary["records"]] == [
            "top-ai-repositories-this-month",
            "most-starred-mcp-projects",
            "fastest-growing-ai-repositories-this-year",
        ]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ranking_artifact_future_version_rejected() -> None:
    root = ranking_fixture_root(".pytest-ranking-future")
    try:
        write_fixture_weeks(root)
        assert generate_ranking_artifacts.main(["--root", str(root)]) == 0
        target = root / "static/data/rankings/top-ai-repositories-this-month.json"
        payload = json.loads(target.read_text(encoding="utf-8"))
        payload["schema_version"] = "2.0.0"
        target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assert generate_ranking_artifacts.main(["--root", str(root), "--check"]) == 1
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_data_page_row_has_context_summary() -> None:
    record = generate_data_pages.row(
        rank=1,
        obs=repo_observation(),
        metric_value=42,
        metric_label="42 stars",
        context="Latest observed in 2026-W33.",
    )

    assert record["context_summary"]
    assert len(record["context_summary"]) <= 160


def test_data_page_row_has_github_url() -> None:
    record = generate_data_pages.row(
        rank=1,
        obs=repo_observation(),
        metric_value=42,
        metric_label="42 stars",
        context="Latest observed in 2026-W33.",
    )

    assert record["github_url"] == "https://github.com/example/repo"

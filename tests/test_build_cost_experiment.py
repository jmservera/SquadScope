from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest
import yaml

from scripts import build_cost_experiment as experiment


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _corpus(root: Path) -> Path:
    _write(
        root / "config/observatory.toml",
        "[repo_pages]\nenabled = false\n[topic_hubs.dynamic_creation]\nenabled = false\n",
    )
    for class_root in ("topics", "data", "repo"):
        _write(root / f"content/{class_root}/_index.md", f"root {class_root}\n")
    for index in range(2):
        _write(root / f"content/topics/topic-{index}/_index.md", f"topic {index}\n")
    _write(root / "content/data/data-0/index.md", "data\n")
    for index in range(3):
        _write(root / f"content/repo/repo-{index}/index.md", f"repo {index}\n")
    _write(root / "hugo.toml", "baseURL = 'https://example.test/'\n")
    return root


def _workload(root: Path) -> dict[str, list[dict[str, object]]]:
    return experiment.discover_workload(root, enforce_expected_counts=False)


def _sample(repetition: int, variant: experiment.Variant, duration: int) -> dict:
    return {
        "schema_version": experiment.SAMPLE_SCHEMA,
        "mode": "report-only",
        "blocking_threshold_ms": None,
        "experiment": {
            "run_id": "1",
            "run_attempt": 1,
            "repetition": repetition,
            "execution_position": 1,
        },
        "provenance": {"main_sha": "a" * 40, "publish_sha": "b" * 40, "workflow_sha": "a" * 40},
        "runner": {"os": "Linux", "arch": "X64", "image_os": "ubuntu24", "image_version": "1"},
        "variant": {
            "name": variant.name,
            "included_classes": list(variant.included_classes),
            "source_pages_total": sum(
                experiment.EXPECTED_CLASS_COUNTS[name] for name in variant.included_classes
            ),
            "source_pages_added": variant.source_pages_added,
            "source_bytes_total": 1,
            "manifest_sha256": hashlib.sha256(variant.name.encode()).hexdigest(),
        },
        "tools": {"hugo": "v0.161.1", "pagefind": "1.5.2", "node": "v24", "python": "3.12"},
        "hugo": {
            "duration_ms": duration,
            "rendered_html_files": 1,
            "output_bytes": 1,
            "exit_code": 0,
        },
        "pagefind": {
            "duration_ms": duration * 2,
            "html_files_scanned": 1,
            "indexed_pages": 1,
            "index_bytes": 1,
            "exit_code": 0,
        },
        "status": "passed",
    }


def _complete_samples() -> list[dict]:
    return [
        _sample(repetition, variant, repetition * 10 + position)
        for repetition in range(1, 4)
        for position, variant in enumerate(experiment.VARIANTS)
    ]


def test_statistics_cover_odd_even_and_nearest_rank() -> None:
    assert experiment._stats([9, 1, 5])["median_ms"] == 5
    assert experiment._stats([1, 3, 7, 9])["median_ms"] == 5
    assert experiment._stats([9, 1, 5])["p95_ms"] == 9


def test_pagefind_log_parser_is_fail_closed() -> None:
    assert experiment.parse_pagefind_log(
        "Found 1,234 files matching **/*.html\nIndexed 987 pages"
    ) == (1234, 987)
    with pytest.raises(experiment.ExperimentError, match="lacks"):
        experiment.parse_pagefind_log("Indexed 12 pages")


def test_pagefind_is_invoked_directly_not_via_npx() -> None:
    source = Path("scripts/build_cost_experiment.py").read_text(encoding="utf-8")
    assert "npx" not in source
    assert '"pagefind", "--version"' in source
    assert '"pagefind", "--site", "public/"' in source


def test_tree_metrics_count_full_hugo_output(tmp_path: Path) -> None:
    _write(tmp_path / "index.html", "html")
    _write(tmp_path / "assets/site.css", "css")
    assert experiment._tree_metrics(tmp_path, "*.html") == (1, 4)
    assert experiment._tree_metrics(tmp_path) == (2, 7)


def test_materialization_is_cumulative_and_preserves_roots(tmp_path: Path) -> None:
    source = _corpus(tmp_path / "source")
    original = {
        path.relative_to(source): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source.rglob("*")
        if path.is_file()
    }
    expected = {"baseline": 0, "topic_hubs": 2, "data_pages": 3, "repository_pages": 6}
    for name, count in expected.items():
        destination = tmp_path / name
        manifest = experiment.materialize_variant(
            source, destination, name, enforce_expected_counts=False
        )
        assert manifest["source_pages_total"] == count
        assert sum(len(entries) for entries in _workload(destination).values()) == count
        for class_root in ("topics", "data", "repo"):
            assert (destination / f"content/{class_root}/_index.md").is_file()
    assert original == {
        path.relative_to(source): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source.rglob("*")
        if path.is_file()
    }


def test_materialization_rejects_escaping_symlink(tmp_path: Path) -> None:
    source = _corpus(tmp_path / "source")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    (source / "assets").mkdir()
    (source / "assets/escape").symlink_to(outside)
    with pytest.raises(experiment.ExperimentError, match="escapes"):
        experiment.materialize_variant(
            source, tmp_path / "destination", "baseline", enforce_expected_counts=False
        )


def test_aggregate_computes_negative_paired_and_marginal_deltas() -> None:
    samples = _complete_samples()
    for sample in samples:
        if sample["variant"]["name"] == "data_pages":
            sample["hugo"]["duration_ms"] -= 5
    summary = experiment.aggregate_samples(samples)
    rows = {row["variant"]: row for row in summary["stages"]["hugo"]}
    assert summary["blocking_threshold_ms"] is None
    assert summary["sample_quality"] == "minimum"
    assert rows["data_pages"]["absolute_delta_ms"] == -4
    assert rows["data_pages"]["paired_deltas_ms"] == [-4, -4, -4]
    assert rows["data_pages"]["marginal_ms_per_added_page"] == pytest.approx(-4 / 3)


@pytest.mark.parametrize("mutation", ["duplicate", "failure", "provenance", "manifest", "missing"])
def test_aggregate_rejects_inconsistent_evidence(mutation: str) -> None:
    samples = _complete_samples()
    if mutation == "duplicate":
        samples.append(samples[0])
    elif mutation == "failure":
        samples[0]["status"] = "failed"
    elif mutation == "provenance":
        samples[0]["provenance"] = {**samples[0]["provenance"], "publish_sha": "c" * 40}
    elif mutation == "manifest":
        samples[0]["variant"] = {**samples[0]["variant"], "manifest_sha256": "f" * 64}
    else:
        samples.pop()
    with pytest.raises(experiment.ExperimentError):
        experiment.aggregate_samples(samples)


def test_zero_predecessor_produces_null_percent_delta() -> None:
    samples = _complete_samples()
    for sample in samples:
        if sample["variant"]["name"] == "baseline":
            sample["hugo"]["duration_ms"] = 0
    summary = experiment.aggregate_samples(samples)
    topic = summary["stages"]["hugo"][1]
    assert topic["percent_delta"] is None


def test_reports_and_checksums_are_stable(tmp_path: Path) -> None:
    summary = experiment.aggregate_samples(_complete_samples())
    first = experiment.render_summary_markdown(summary)
    second = experiment.render_summary_markdown(json.loads(json.dumps(summary, sort_keys=True)))
    assert first == second
    reports = tmp_path / "reports"
    experiment._write_json(reports / "summary.json", summary)
    (reports / "summary.md").write_text(first, encoding="utf-8")
    experiment.write_checksums(reports)
    lines = (reports / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    assert lines == sorted(lines, key=lambda line: line.split("  ", maxsplit=1)[1])


def _sized_corpus(root: Path, *, topics: int, data: int, repos: int) -> Path:
    _write(
        root / "config/observatory.toml",
        "[repo_pages]\nenabled = false\n[topic_hubs.dynamic_creation]\nenabled = false\n",
    )
    for class_root in ("topics", "data", "repo"):
        _write(root / f"content/{class_root}/_index.md", f"root {class_root}\n")
    for index in range(topics):
        _write(root / f"content/topics/topic-{index}/_index.md", f"topic {index}\n")
    for index in range(data):
        _write(root / f"content/data/data-{index}/index.md", f"data {index}\n")
    for index in range(repos):
        _write(root / f"content/repo/repo-{index}/index.md", f"repo {index}\n")
    _write(root / "hugo.toml", "baseURL = 'https://example.test/'\n")
    return root


def _experiment_args(source: Path, reports: Path, expected_repository_pages: str) -> object:
    return experiment.create_parser().parse_args(
        [
            "--source",
            str(source),
            "--reports",
            str(reports),
            "--repetitions",
            "3",
            "--main-sha",
            "a" * 40,
            "--publish-sha",
            "b" * 40,
            "--workflow-sha",
            "a" * 40,
            "--run-id",
            "1",
            "--run-attempt",
            "1",
            "--runner-os",
            "Linux",
            "--runner-arch",
            "X64",
            "--image-os",
            "ubuntu24",
            "--image-version",
            "1",
            "--expected-repository-pages",
            expected_repository_pages,
        ]
    )


def test_parser_expected_repository_pages_defaults_none_and_parses_int() -> None:
    base = [
        "--source",
        "/tmp/x",
        "--reports",
        "/tmp/r",
        "--repetitions",
        "3",
        "--main-sha",
        "a" * 40,
        "--publish-sha",
        "b" * 40,
        "--workflow-sha",
        "a" * 40,
        "--run-id",
        "1",
        "--run-attempt",
        "1",
        "--runner-os",
        "Linux",
        "--runner-arch",
        "X64",
        "--image-os",
        "ubuntu24",
        "--image-version",
        "1",
    ]
    assert experiment.create_parser().parse_args(base).expected_repository_pages is None
    parsed = experiment.create_parser().parse_args(base + ["--expected-repository-pages", "263"])
    assert parsed.expected_repository_pages == 263


def test_run_experiment_rejects_mismatched_expected_repository_pages(tmp_path: Path) -> None:
    source = _sized_corpus(tmp_path / "src", topics=5, data=3, repos=3)
    args = _experiment_args(source, tmp_path / "reports", "5")
    with pytest.raises(experiment.ExperimentError, match="repository_pages count is 3; expected 5"):
        experiment.run_experiment(args)


def test_run_experiment_rejects_non_positive_expected_repository_pages(tmp_path: Path) -> None:
    source = _sized_corpus(tmp_path / "src", topics=5, data=3, repos=3)
    args = _experiment_args(source, tmp_path / "reports", "0")
    with pytest.raises(experiment.ExperimentError, match="positive integer"):
        experiment.run_experiment(args)


def test_discover_workload_merges_partial_expected_counts(tmp_path: Path) -> None:
    _corpus(tmp_path)
    with pytest.raises(experiment.ExperimentError, match="topic_hubs count is 2; expected 5"):
        experiment.discover_workload(tmp_path, expected_counts={"repository_pages": 3})


def test_aggregation_uses_derived_repository_denominator() -> None:
    variants = experiment.build_variants(263)
    durations = {"baseline": 100, "topic_hubs": 110, "data_pages": 120, "repository_pages": 400}
    samples = [
        _sample(repetition, variant, durations[variant.name])
        for repetition in range(1, 4)
        for variant in variants
    ]
    summary = experiment.aggregate_samples(samples)
    repository = next(
        row for row in summary["stages"]["hugo"] if row["variant"] == "repository_pages"
    )
    assert repository["marginal_ms_per_added_page"] == pytest.approx((400 - 120) / 263)


def test_run_experiment_propagates_parsed_count_end_to_end(tmp_path: Path, monkeypatch) -> None:
    source = _sized_corpus(tmp_path / "src", topics=5, data=3, repos=4)
    reports = tmp_path / "reports"
    args = _experiment_args(source, reports, "4")
    sample_schema = experiment.SAMPLE_SCHEMA
    durations = {"baseline": 100, "topic_hubs": 110, "data_pages": 120, "repository_pages": 400}

    def fake_build_sample(
        corpus,
        out_reports,
        variant_data,
        *,
        repetition,
        execution_position,
        provenance,
        runner,
        tools,
        experiment,
    ):
        duration = durations[variant_data["name"]]
        return {
            "schema_version": sample_schema,
            "mode": "report-only",
            "blocking_threshold_ms": None,
            "experiment": {
                "run_id": experiment["run_id"],
                "run_attempt": experiment["run_attempt"],
                "repetition": repetition,
                "execution_position": execution_position,
            },
            "provenance": provenance,
            "runner": runner,
            "tools": tools,
            "variant": {
                "name": variant_data["name"],
                "included_classes": variant_data["included_classes"],
                "source_pages_total": variant_data["source_pages_total"],
                "source_pages_added": variant_data["source_pages_added"],
                "source_bytes_total": variant_data["source_bytes_total"],
                "manifest_sha256": variant_data["manifest_sha256"],
            },
            "hugo": {
                "duration_ms": duration,
                "rendered_html_files": 1,
                "output_bytes": 1,
                "exit_code": 0,
            },
            "pagefind": {
                "duration_ms": duration * 2,
                "html_files_scanned": 1,
                "indexed_pages": 1,
                "index_bytes": 1,
                "exit_code": 0,
            },
            "status": "passed",
        }

    monkeypatch.setattr(experiment, "_tool_version", lambda *args, **kwargs: "stub")
    monkeypatch.setattr(experiment, "build_sample", fake_build_sample)

    experiment.run_experiment(args)

    manifest = json.loads((reports / "manifest.json").read_text(encoding="utf-8"))
    repo_variant = next(v for v in manifest["variants"] if v["name"] == "repository_pages")
    assert repo_variant["source_pages_added"] == 4
    summary = json.loads((reports / "summary.json").read_text(encoding="utf-8"))
    repo_row = next(
        row for row in summary["stages"]["hugo"] if row["variant"] == "repository_pages"
    )
    assert repo_row["marginal_ms_per_added_page"] == pytest.approx((400 - 120) / 4)


def test_workflow_is_manual_read_only_and_pinned() -> None:
    path = Path(".github/workflows/build-cost-experiment.yml")
    text = path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    triggers = workflow.get("on", workflow.get(True))
    assert set(triggers) == {"workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] is False
    assert workflow["jobs"]["report"]["permissions"] == {"contents": "read"}
    uses = re.findall(r"uses:\s+[^@\s]+@([^\s#]+)", text)
    assert uses and all(re.fullmatch(r"[0-9a-f]{40}", revision) for revision in uses)
    assert "persist-credentials: false" in text
    assert "secrets." not in text
    assert "git push" not in text
    assert "permissions: write" not in text


def test_workflow_admits_only_immutable_reviewed_inputs() -> None:
    text = Path(".github/workflows/build-cost-experiment.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    triggers = workflow.get("on", workflow.get(True))
    inputs = triggers["workflow_dispatch"]["inputs"]
    assert set(inputs) == {"reviewed_main_sha", "reviewed_publish_sha", "repetitions"}
    assert inputs["repetitions"]["options"] == ["3", "5"]
    assert "refs/heads/main" in workflow["jobs"]["report"]["if"]
    assert "reviewed_main_sha must equal" in text
    assert "merge-base --is-ancestor" in text
    assert 'git checkout "${REVIEWED_PUBLISH_SHA}"' in text
    topic_exclusion = "if [[ \"${path}\" == 'content/topics' ]]"
    assert topic_exclusion in text
    assert text.index(topic_exclusion) < text.index('rm -rf -- "${path}"')
    assert "scripts.publish_hydration paths" in text
    assert "scripts.publish_hydration check" in text
    assert "--expected-repository-pages" in text
    assert 'git ls-tree -r --name-only "${REVIEWED_PUBLISH_SHA}" -- content/repo' in text


def test_discover_workload_uses_provided_expected_counts(tmp_path: Path) -> None:
    _corpus(tmp_path)
    workload = experiment.discover_workload(
        tmp_path,
        expected_counts={"topic_hubs": 2, "data_pages": 1, "repository_pages": 3},
    )
    assert len(workload["repository_pages"]) == 3

    with pytest.raises(experiment.ExperimentError, match="repository_pages count is 3; expected 5"):
        experiment.discover_workload(
            tmp_path,
            expected_counts={"topic_hubs": 2, "data_pages": 1, "repository_pages": 5},
        )


def test_build_variants_uses_reviewed_repository_count() -> None:
    variants = experiment.build_variants(263)
    repository = next(variant for variant in variants if variant.name == "repository_pages")
    assert repository.source_pages_added == 263
    assert [variant.name for variant in variants] == [
        "baseline",
        "topic_hubs",
        "data_pages",
        "repository_pages",
    ]


def test_workflow_is_report_only_isolated_and_has_no_generators() -> None:
    text = Path(".github/workflows/build-cost-experiment.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    report_job = workflow["jobs"]["report"]
    run_blocks = "\n".join(step.get("run", "") for step in report_job["steps"])
    assert "${{" not in run_blocks
    assert report_job["env"]["BLOCKING_THRESHOLD_MS"] == "null"
    assert "assert_rollouts_disabled" in run_blocks
    assert "--source ." in run_blocks
    assert "--reports reports/build-cost-experiment" in run_blocks
    assert (
        "npx"
        not in text.split("Install exact Pagefind outside measured intervals", maxsplit=1)[1].split(
            "Run isolated report-only experiment", maxsplit=1
        )[0]
    )
    forbidden = (
        "generate_data_pages.py",
        "manage_topic_hubs.py",
        "observatory_repos.py",
        "repo_pages.enabled = true",
        "dynamic_creation.enabled = true",
    )
    assert not any(value in text for value in forbidden)
    upload = next(
        step for step in report_job["steps"] if step["name"] == "Upload report-only evidence"
    )
    assert upload["if"] == "${{ always() }}"
    assert upload["with"]["retention-days"] == 90

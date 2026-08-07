#!/usr/bin/env python3
"""Run an isolated, report-only Hugo and Pagefind build-cost experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import statistics
import subprocess  # nosec B404
import sys
import tempfile
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.baseline_telemetry import percentile

SAMPLE_SCHEMA = "claracle_build_cost_sample_v1"
SUMMARY_SCHEMA = "claracle_build_cost_summary_v1"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
PAGEFIND_FILES_PATTERN = re.compile(r"Found\s+([\d,]+)\s+files?\b", re.IGNORECASE)
PAGEFIND_PAGES_PATTERN = re.compile(r"Indexed\s+([\d,]+)\s+pages?\b", re.IGNORECASE)
EXPECTED_CLASS_COUNTS = {"topic_hubs": 5, "data_pages": 3, "repository_pages": 266}
CLASS_PATTERNS = {
    "topic_hubs": "content/topics/*/_index.md",
    "data_pages": "content/data/*/index.md",
    "repository_pages": "content/repo/*/index.md",
}
COPY_EXCLUDES = {
    ".copilot-tracking",
    ".git",
    ".venv",
    "node_modules",
    "public",
    "reports",
    "resources",
    "screenshots",
    "venv",
}


@dataclass(frozen=True, slots=True)
class Variant:
    """One cumulative source-page workload."""

    name: str
    included_classes: tuple[str, ...]
    source_pages_added: int


VARIANTS = (
    Variant("baseline", (), 0),
    Variant("topic_hubs", ("topic_hubs",), 5),
    Variant("data_pages", ("topic_hubs", "data_pages"), 3),
    Variant(
        "repository_pages",
        ("topic_hubs", "data_pages", "repository_pages"),
        266,
    ),
)


class ExperimentError(RuntimeError):
    """Raised when experiment evidence is unsafe or internally inconsistent."""


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_sha(value: str, label: str) -> str:
    """Return a validated immutable SHA."""
    if not SHA_PATTERN.fullmatch(value):
        raise ExperimentError(f"{label} must be exactly 40 lowercase hexadecimal characters")
    return value


def assert_rollouts_disabled(root: Path) -> None:
    """Fail unless both production rollout controls are boolean false."""
    config = tomllib.loads((root / "config/observatory.toml").read_text(encoding="utf-8"))
    repo_enabled = config.get("repo_pages", {}).get("enabled")
    topic_enabled = config.get("topic_hubs", {}).get("dynamic_creation", {}).get("enabled")
    if repo_enabled is not False or topic_enabled is not False:
        raise ExperimentError("repo pages and dynamic topic creation must both remain disabled")


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=True).relative_to(root.resolve(strict=True)).as_posix()
    except ValueError as exc:
        raise ExperimentError(f"path escapes experiment corpus: {path}") from exc


def validate_corpus_symlinks(root: Path) -> None:
    """Reject symlinks in site inputs that resolve outside the corpus."""
    for relative_root in (
        "archetypes",
        "assets",
        "config",
        "content",
        "data",
        "layouts",
        "static",
        "themes",
    ):
        tree = root / relative_root
        if not tree.exists():
            continue
        for path in tree.rglob("*"):
            if path.is_symlink():
                _safe_relative(path, root)


def discover_workload(
    root: Path, *, enforce_expected_counts: bool = True
) -> dict[str, list[dict[str, Any]]]:
    """Classify source leaves and return their stable hash manifest."""
    resolved_root = root.resolve(strict=True)
    discovered: dict[str, list[dict[str, Any]]] = {}
    seen: set[str] = set()
    for class_name, pattern in CLASS_PATTERNS.items():
        entries: list[dict[str, Any]] = []
        for path in sorted(root.glob(pattern)):
            relative = _safe_relative(path, resolved_root)
            if relative in seen:
                raise ExperimentError(f"workload path belongs to multiple classes: {relative}")
            seen.add(relative)
            payload = path.read_bytes()
            entries.append(
                {
                    "path": relative,
                    "class": class_name,
                    "byte_size": len(payload),
                    "sha256": _sha256_bytes(payload),
                }
            )
        if enforce_expected_counts and len(entries) != EXPECTED_CLASS_COUNTS[class_name]:
            raise ExperimentError(
                f"{class_name} count is {len(entries)}; expected {EXPECTED_CLASS_COUNTS[class_name]}"
            )
        discovered[class_name] = entries
    return discovered


def variant_manifest(workload: dict[str, list[dict[str, Any]]], variant: Variant) -> dict[str, Any]:
    """Build the stable source manifest for one cumulative variant."""
    files = [entry for name in variant.included_classes for entry in workload[name]]
    return {
        "name": variant.name,
        "included_classes": list(variant.included_classes),
        "source_pages_total": len(files),
        "source_pages_added": variant.source_pages_added,
        "source_bytes_total": sum(entry["byte_size"] for entry in files),
        "manifest_sha256": _sha256_bytes(_canonical_json(files).encode()),
        "files": files,
    }


def _copy_ignore(_: str, names: list[str]) -> set[str]:
    return set(names).intersection(COPY_EXCLUDES)


def materialize_variant(
    source: Path,
    destination: Path,
    variant_name: str,
    *,
    enforce_expected_counts: bool = True,
) -> dict[str, Any]:
    """Copy the canonical corpus and remove workload leaves excluded by a variant."""
    variant = next((item for item in VARIANTS if item.name == variant_name), None)
    if variant is None:
        raise ExperimentError(f"unknown variant: {variant_name}")
    validate_corpus_symlinks(source)
    workload = discover_workload(source, enforce_expected_counts=enforce_expected_counts)
    if destination.exists():
        raise ExperimentError(f"destination already exists: {destination}")
    shutil.copytree(source, destination, symlinks=True, ignore=_copy_ignore)
    for class_name, entries in workload.items():
        if class_name in variant.included_classes:
            continue
        for entry in entries:
            leaf = destination / entry["path"]
            leaf.unlink()
            parent = leaf.parent
            class_root = destination / CLASS_PATTERNS[class_name].split("/*/", maxsplit=1)[0]
            while parent != class_root and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
    return variant_manifest(workload, variant)


def parse_pagefind_log(log: str) -> tuple[int, int]:
    """Return Pagefind files-scanned and pages-indexed counters."""
    files_match = PAGEFIND_FILES_PATTERN.search(log)
    pages_match = PAGEFIND_PAGES_PATTERN.search(log)
    if files_match is None or pages_match is None:
        raise ExperimentError("Pagefind log lacks files-scanned or pages-indexed counters")
    return (
        int(files_match.group(1).replace(",", "")),
        int(pages_match.group(1).replace(",", "")),
    )


def _tree_metrics(root: Path, pattern: str = "*") -> tuple[int, int]:
    files = [path for path in root.rglob(pattern) if path.is_file()]
    return len(files), sum(path.stat().st_size for path in files)


def _run_timed(command: list[str], cwd: Path, log_path: Path) -> tuple[int, int, str]:
    started = time.monotonic_ns()
    result = subprocess.run(  # nosec B603 - fixed argv built from reviewed tool paths, no shell
        command, cwd=cwd, capture_output=True, text=True, check=False
    )
    duration_ms = (time.monotonic_ns() - started) // 1_000_000
    log = result.stdout + result.stderr
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(log, encoding="utf-8")
    return duration_ms, result.returncode, log


def build_sample(
    corpus: Path,
    reports: Path,
    variant_data: dict[str, Any],
    *,
    repetition: int,
    execution_position: int,
    provenance: dict[str, str],
    runner: dict[str, str],
    tools: dict[str, str],
    experiment: dict[str, Any],
) -> dict[str, Any]:
    """Measure Hugo and Pagefind for one already-isolated corpus copy."""
    name = variant_data["name"]
    sample_path = reports / "samples" / str(repetition) / f"{name}.json"
    hugo_log = reports / "logs" / str(repetition) / f"{name}-hugo.log"
    pagefind_log = reports / "logs" / str(repetition) / f"{name}-pagefind.log"
    public = corpus / "public"
    hugo_ms, hugo_exit, _ = _run_timed(
        ["hugo", "--minify", "--cleanDestinationDir", "--destination", "public"],
        corpus,
        hugo_log,
    )
    html_count, _ = _tree_metrics(public, "*.html")
    _, output_bytes = _tree_metrics(public)
    pagefind_ms = 0
    pagefind_exit = -1
    scanned = 0
    indexed = 0
    parse_error: str | None = None
    index_bytes = 0
    if hugo_exit == 0:
        pagefind_ms, pagefind_exit, pagefind_output = _run_timed(
            ["npx", "--no-install", "pagefind", "--site", "public/"], corpus, pagefind_log
        )
        try:
            scanned, indexed = parse_pagefind_log(pagefind_output)
        except ExperimentError as exc:
            parse_error = str(exc)
        pagefind_root = public / "pagefind"
        if pagefind_root.exists():
            _, index_bytes = _tree_metrics(pagefind_root)
    else:
        pagefind_log.parent.mkdir(parents=True, exist_ok=True)
        pagefind_log.write_text("Pagefind skipped because Hugo failed.\n", encoding="utf-8")
    status = "passed" if hugo_exit == 0 and pagefind_exit == 0 and parse_error is None else "failed"
    sample = {
        "schema_version": SAMPLE_SCHEMA,
        "mode": "report-only",
        "blocking_threshold_ms": None,
        "experiment": {
            **experiment,
            "repetition": repetition,
            "execution_position": execution_position,
        },
        "provenance": provenance,
        "runner": runner,
        "variant": {key: value for key, value in variant_data.items() if key != "files"},
        "tools": tools,
        "hugo": {
            "duration_ms": hugo_ms,
            "rendered_html_files": html_count,
            "output_bytes": output_bytes,
            "exit_code": hugo_exit,
        },
        "pagefind": {
            "duration_ms": pagefind_ms,
            "html_files_scanned": scanned,
            "indexed_pages": indexed,
            "index_bytes": index_bytes,
            "exit_code": pagefind_exit,
        },
        "status": status,
    }
    if parse_error is not None:
        sample["error"] = parse_error
    _write_json(sample_path, sample)
    if status != "passed":
        raise ExperimentError(f"sample {repetition}/{name} failed; retained logs and JSON")
    return sample


def _stats(values: list[float | int]) -> dict[str, float | int]:
    ordered = sorted(values)
    return {
        "sample_count": len(ordered),
        "median_ms": statistics.median(ordered),
        "p95_ms": percentile([float(value) for value in ordered], 95),
    }


def aggregate_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate and aggregate complete paired samples."""
    if not samples:
        raise ExperimentError("no samples to aggregate")
    expected_names = [variant.name for variant in VARIANTS]
    reference = samples[0]
    repetitions = sorted({sample["experiment"]["repetition"] for sample in samples})
    if len(repetitions) not in (3, 5) or repetitions != list(range(1, len(repetitions) + 1)):
        raise ExperimentError("samples must contain three or five contiguous repetitions")
    seen: set[tuple[int, str]] = set()
    manifests: dict[str, str] = {}
    for sample in samples:
        pair = (sample["experiment"]["repetition"], sample["variant"]["name"])
        if pair in seen:
            raise ExperimentError(f"duplicate repetition/variant pair: {pair}")
        seen.add(pair)
        if sample.get("schema_version") != SAMPLE_SCHEMA or sample.get("status") != "passed":
            raise ExperimentError("all samples must be passed v1 samples")
        if sample.get("mode") != "report-only" or sample.get("blocking_threshold_ms") is not None:
            raise ExperimentError("samples must remain report-only with a null threshold")
        for field in ("provenance", "runner", "tools"):
            if sample[field] != reference[field]:
                raise ExperimentError(f"mixed {field} in samples")
        name = sample["variant"]["name"]
        manifest_sha = sample["variant"]["manifest_sha256"]
        if name in manifests and manifests[name] != manifest_sha:
            raise ExperimentError(f"mixed variant manifest for {name}")
        manifests[name] = manifest_sha
    required_pairs = {(rep, name) for rep in repetitions for name in expected_names}
    if seen != required_pairs:
        raise ExperimentError("samples contain missing or unknown variants")

    by_pair = {
        (sample["experiment"]["repetition"], sample["variant"]["name"]): sample
        for sample in samples
    }
    stages: dict[str, list[dict[str, Any]]] = {"hugo": [], "pagefind": []}
    for stage in stages:
        predecessor: str | None = None
        for variant in VARIANTS:
            values = [by_pair[(rep, variant.name)][stage]["duration_ms"] for rep in repetitions]
            metrics: dict[str, Any] = {"variant": variant.name, **_stats(values)}
            if predecessor is None:
                metrics.update(
                    {
                        "predecessor": None,
                        "absolute_delta_ms": None,
                        "percent_delta": None,
                        "marginal_ms_per_added_page": None,
                        "paired_delta_median_ms": None,
                        "paired_delta_p95_ms": None,
                        "paired_deltas_ms": [],
                    }
                )
            else:
                previous_values = [
                    by_pair[(rep, predecessor)][stage]["duration_ms"] for rep in repetitions
                ]
                previous_median = statistics.median(sorted(previous_values))
                delta = metrics["median_ms"] - previous_median
                paired = [current - previous for current, previous in zip(values, previous_values)]
                paired_stats = _stats(paired)
                metrics.update(
                    {
                        "predecessor": predecessor,
                        "absolute_delta_ms": delta,
                        "percent_delta": None
                        if previous_median == 0
                        else 100 * delta / previous_median,
                        "marginal_ms_per_added_page": delta / variant.source_pages_added,
                        "paired_delta_median_ms": paired_stats["median_ms"],
                        "paired_delta_p95_ms": paired_stats["p95_ms"],
                        "paired_deltas_ms": paired,
                    }
                )
            stages[stage].append(metrics)
            predecessor = variant.name
    return {
        "schema_version": SUMMARY_SCHEMA,
        "mode": "report-only",
        "blocking_threshold_ms": None,
        "sample_count_per_variant": len(repetitions),
        "sample_quality": "preferred" if len(repetitions) == 5 else "minimum",
        "nearest_rank_note": "With three or five samples, nearest-rank p95 is the observed maximum.",
        "provenance": reference["provenance"],
        "runner": reference["runner"],
        "tools": reference["tools"],
        "stages": stages,
    }


def render_summary_markdown(summary: dict[str, Any]) -> str:
    """Render a stable human-readable report."""
    lines = [
        "# Hugo and Pagefind Build-Cost Experiment",
        "",
        "> Report-only evidence. No blocking threshold or rollout authorization is defined.",
        "",
        f"Samples per variant: {summary['sample_count_per_variant']} ({summary['sample_quality']}).",
        "Nearest-rank p95 is the observed maximum with three or five samples.",
    ]
    for stage in ("hugo", "pagefind"):
        lines.extend(
            [
                "",
                f"## {stage.title()}",
                "",
                "| Variant | Median ms | p95 ms | Delta ms | Delta % | Marginal ms/page |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in summary["stages"][stage]:
            values = [
                row["variant"],
                row["median_ms"],
                row["p95_ms"],
                row["absolute_delta_ms"],
                row["percent_delta"],
                row["marginal_ms_per_added_page"],
            ]
            rendered = [
                "null"
                if value is None
                else f"{value:.3f}"
                if isinstance(value, float)
                else str(value)
                for value in values
            ]
            lines.append("| " + " | ".join(rendered) + " |")
    return "\n".join(lines) + "\n"


def write_checksums(reports: Path) -> None:
    """Write stable SHA-256 checksums for retained evidence files."""
    checksum_path = reports / "SHA256SUMS"
    files = sorted(path for path in reports.rglob("*") if path.is_file() and path != checksum_path)
    checksum_path.write_text(
        "".join(
            f"{_sha256_bytes(path.read_bytes())}  {path.relative_to(reports).as_posix()}\n"
            for path in files
        ),
        encoding="utf-8",
    )


def _tool_version(command: list[str]) -> str:
    result = subprocess.run(  # nosec B603 - fixed argv built from reviewed tool paths, no shell
        command, capture_output=True, text=True, check=True
    )
    return (result.stdout or result.stderr).strip().splitlines()[0]


def run_experiment(args: argparse.Namespace) -> None:
    """Materialize, measure, aggregate, and retain the experiment evidence."""
    source = args.source.resolve(strict=True)
    reports = args.reports.resolve()
    if reports.exists():
        raise ExperimentError(f"reports directory already exists: {reports}")
    reports.mkdir(parents=True)
    assert_rollouts_disabled(source)
    workload = discover_workload(source)
    validate_corpus_symlinks(source)
    provenance = {
        "main_sha": validate_sha(args.main_sha, "main_sha"),
        "publish_sha": validate_sha(args.publish_sha, "publish_sha"),
        "workflow_sha": validate_sha(args.workflow_sha, "workflow_sha"),
    }
    runner = {
        "os": args.runner_os,
        "arch": args.runner_arch,
        "image_os": args.image_os,
        "image_version": args.image_version,
    }
    tools = {
        "hugo": _tool_version(["hugo", "version"]),
        "pagefind": _tool_version(["npx", "--no-install", "pagefind", "--version"]),
        "node": _tool_version(["node", "--version"]),
        "python": sys.version.split()[0],
    }
    orders = []
    for repetition in range(1, args.repetitions + 1):
        offset = (repetition - 1) % len(VARIANTS)
        orders.append([item.name for item in VARIANTS[offset:] + VARIANTS[:offset]])
    manifest = {
        "schema_version": "claracle_build_cost_manifest_v1",
        "mode": "report-only",
        "blocking_threshold_ms": None,
        "dispatch": {
            "repetitions": args.repetitions,
            "reviewed_main_sha": args.main_sha,
            "reviewed_publish_sha": args.publish_sha,
        },
        "provenance": provenance,
        "runner": runner,
        "tools": tools,
        "execution_orders": orders,
        "variants": [variant_manifest(workload, variant) for variant in VARIANTS],
    }
    _write_json(reports / "manifest.json", manifest)
    samples: list[dict[str, Any]] = []
    try:
        with tempfile.TemporaryDirectory(prefix="claracle-build-cost-") as temporary:
            temporary_root = Path(temporary)
            for repetition, order in enumerate(orders, start=1):
                for position, name in enumerate(order, start=1):
                    corpus = temporary_root / f"r{repetition}-{name}"
                    variant_data = materialize_variant(source, corpus, name)
                    samples.append(
                        build_sample(
                            corpus,
                            reports,
                            variant_data,
                            repetition=repetition,
                            execution_position=position,
                            provenance=provenance,
                            runner=runner,
                            tools=tools,
                            experiment={"run_id": args.run_id, "run_attempt": args.run_attempt},
                        )
                    )
                    shutil.rmtree(corpus)
        summary = aggregate_samples(samples)
        _write_json(reports / "summary.json", summary)
        (reports / "summary.md").write_text(render_summary_markdown(summary), encoding="utf-8")
    finally:
        write_checksums(reports)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, choices=(3, 5), required=True)
    parser.add_argument("--main-sha", required=True)
    parser.add_argument("--publish-sha", required=True)
    parser.add_argument("--workflow-sha", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", type=int, required=True)
    parser.add_argument("--runner-os", required=True)
    parser.add_argument("--runner-arch", required=True)
    parser.add_argument("--image-os", required=True)
    parser.add_argument("--image-version", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the report-only experiment CLI."""
    try:
        run_experiment(create_parser().parse_args(argv))
    except (ExperimentError, OSError, subprocess.SubprocessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import dataclasses
import importlib.util
import inspect
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pytest

if importlib.util.find_spec("scripts.crawl_shard_experiment") is None:
    pytest.skip("scripts.crawl_shard_experiment is not implemented yet", allow_module_level=True)

from scripts import crawl_shard_experiment as experiment


def _build_instance(factory: Any, **values: Any) -> Any:
    signature = inspect.signature(factory)
    kwargs = {}
    for name, parameter in signature.parameters.items():
        if name in values:
            kwargs[name] = values[name]
        elif parameter.default is inspect._empty and parameter.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            raise AssertionError(f"missing required parameter {name!r} for {factory}")
    return factory(**kwargs)


def _resolve_attr(target: Any, *names: str) -> Any:
    if isinstance(target, dict):
        for name in names:
            if name in target:
                return target[name]
    for name in names:
        if hasattr(target, name):
            return getattr(target, name)
    raise AssertionError(f"could not resolve any of {names!r} on {target!r}")


def _resolve_method(target: Any, *names: str):
    for name in names:
        candidate = getattr(target, name, None)
        if callable(candidate):
            return candidate
    raise AssertionError(f"could not resolve any of {names!r} on {target!r}")


def _make_tracker(cap: int):
    return _build_instance(
        experiment.SharedQuotaTracker,
        cap=cap,
        hard_cap=cap,
        limit=cap,
        quota_cap=cap,
        max_calls=cap,
    )


def _tracker_cap(tracker: Any) -> int:
    return int(_resolve_attr(tracker, "cap", "hard_cap", "limit", "quota_cap", "max_calls"))


def _tracker_count(tracker: Any) -> int:
    return int(_resolve_attr(tracker, "count", "used", "api_calls_used", "value", "calls_used"))


def _consume_quota(tracker: Any) -> bool:
    method = _resolve_method(tracker, "increment", "try_acquire", "acquire", "consume", "record_call")
    try:
        result = method()
    except Exception as exc:  # pragma: no cover
        message = str(exc).lower()
        if "quota" in message or "cap" in message or "limit" in message:
            return False
        raise
    if isinstance(result, bool):
        return result
    if isinstance(result, int):
        return result <= _tracker_cap(tracker)
    return _tracker_count(tracker) <= _tracker_cap(tracker)


def _reset_tracker(tracker: Any) -> None:
    _resolve_method(tracker, "reset", "clear")()


def _make_budget(seconds: float):
    return _build_instance(
        experiment.WallClockBudget,
        budget_s=seconds,
        budget_seconds=seconds,
        seconds=seconds,
        limit_s=seconds,
    )


def _budget_exceeded(budget: Any) -> bool:
    status = _resolve_method(budget, "is_exceeded", "expired", "timed_out", "should_stop", "exhausted")
    return bool(status())


def _elapsed_seconds(budget: Any) -> float:
    for name in ("elapsed_s", "elapsed_seconds", "elapsed"):
        if hasattr(budget, name):
            value = getattr(budget, name)
            return float(value() if callable(value) else value)
    raise AssertionError(f"could not resolve elapsed time on {budget!r}")


def _make_shard_result(*, repos_found: list[dict[str, Any]], api_calls: int, errors: list[str], wall_clock_s: float):
    return _build_instance(
        experiment.ShardResult,
        shard_id="github:new-repos:q1",
        repos_found=repos_found,
        repos=repos_found,
        api_calls=api_calls,
        api_calls_used=api_calls,
        errors=errors,
        wall_clock_s=wall_clock_s,
        duration_s=wall_clock_s,
        rate_limit_detected=False,
        rate_limit_events=0,
    )


def _extract_repos(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    for name in ("repos", "repos_found", "items", "results", "merged_repos"):
        if isinstance(payload, dict) and name in payload:
            return payload[name]
        if hasattr(payload, name):
            return getattr(payload, name)
    raise AssertionError(f"could not extract merged repos from {payload!r}")


def _metric(result: Any, *names: str) -> Any:
    return _resolve_attr(result, *names)


def _percent(value: Any) -> float:
    numeric = float(value)
    return numeric * 100.0 if abs(numeric) <= 1.0 else numeric


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def _make_report(comparison: dict[str, Any]):
    report_cls = experiment.ExperimentReport
    for factory_name in ("from_comparison", "from_metrics", "evaluate", "build"):
        factory = getattr(report_cls, factory_name, None)
        if callable(factory):
            signature = inspect.signature(factory)
            if "comparison" in signature.parameters:
                return factory(comparison=comparison)
            if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
                return factory(**comparison)
            allowed = {name: value for name, value in comparison.items() if name in signature.parameters}
            return factory(**allowed)
    signature = inspect.signature(report_cls)
    if "comparison" in signature.parameters:
        return report_cls(comparison=comparison)
    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
        return report_cls(**comparison)
    allowed = {name: value for name, value in comparison.items() if name in signature.parameters}
    return report_cls(**allowed)


def _verdict(report: Any) -> str:
    return str(_resolve_attr(report, "verdict", "status")).lower()


@pytest.fixture
def repo_alpha() -> dict[str, Any]:
    return {
        "full_name": "octo/alpha",
        "name": "alpha",
        "owner": "octo",
        "stars": 150,
        "stars_gained": 42,
        "language": "Python",
        "topics": ["ai", "testing"],
        "url": "https://github.com/octo/alpha",
    }


@pytest.fixture
def repo_beta() -> dict[str, Any]:
    return {
        "full_name": "octo/beta",
        "name": "beta",
        "owner": "octo",
        "stars": 120,
        "stars_gained": 15,
        "language": "Go",
        "topics": ["infra"],
        "url": "https://github.com/octo/beta",
    }


@pytest.fixture
def repo_gamma() -> dict[str, Any]:
    return {
        "full_name": "tools/gamma",
        "name": "gamma",
        "owner": "tools",
        "stars": 220,
        "stars_gained": 5,
        "language": "Rust",
        "topics": ["developer-tools"],
        "url": "https://github.com/tools/gamma",
    }


class TestSharedQuotaTracker:
    def test_thread_safe_increment_and_cap_enforcement(self) -> None:
        tracker = _make_tracker(cap=10)
        with ThreadPoolExecutor(max_workers=8) as pool:
            successes = list(pool.map(lambda _: _consume_quota(tracker), range(25)))
        assert sum(bool(result) for result in successes) == 10
        assert _tracker_count(tracker) == 10
        assert _consume_quota(tracker) is False

    def test_reset_clears_accumulated_usage(self) -> None:
        tracker = _make_tracker(cap=3)
        assert _consume_quota(tracker) is True
        assert _consume_quota(tracker) is True
        assert _tracker_count(tracker) == 2
        _reset_tracker(tracker)
        assert _tracker_count(tracker) == 0
        assert _consume_quota(tracker) is True


class TestWallClockBudget:
    def test_budget_not_exceeded_before_deadline(self, monkeypatch: pytest.MonkeyPatch) -> None:
        clock = {"now": 100.0}
        monkeypatch.setattr(experiment.time, "monotonic", lambda: clock["now"])
        budget = _make_budget(5.0)
        clock["now"] = 104.9
        assert _elapsed_seconds(budget) == pytest.approx(4.9)
        assert _budget_exceeded(budget) is False

    def test_budget_exceeded_triggers_graceful_stop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        clock = {"now": 250.0}
        monkeypatch.setattr(experiment.time, "monotonic", lambda: clock["now"])
        budget = _make_budget(5.0)
        clock["now"] = 255.1
        assert _elapsed_seconds(budget) == pytest.approx(5.1)
        assert _budget_exceeded(budget) is True


def test_shard_result_dataclass_contract(repo_alpha: dict[str, Any]) -> None:
    assert dataclasses.is_dataclass(experiment.ShardResult)
    field_names = {field.name for field in dataclasses.fields(experiment.ShardResult)}
    assert {"repos_found", "api_calls", "errors", "wall_clock_s"}.issubset(field_names)
    result = _make_shard_result(repos_found=[repo_alpha], api_calls=4, errors=[], wall_clock_s=1.75)
    assert _resolve_attr(result, "repos_found", "repos") == [repo_alpha]
    assert _resolve_attr(result, "api_calls", "api_calls_used") == 4
    assert result.errors == []
    assert _resolve_attr(result, "wall_clock_s", "duration_s") == pytest.approx(1.75)


class TestDeterministicMerge:
    def test_deduplicates_by_full_name_and_preserves_star_gain(
        self, repo_alpha: dict[str, Any], repo_beta: dict[str, Any], repo_gamma: dict[str, Any]
    ) -> None:
        first = _make_shard_result(repos_found=[repo_alpha, repo_beta], api_calls=3, errors=[], wall_clock_s=1.1)
        duplicate_alpha = {**repo_alpha, "stars": 999, "stars_gained": 42}
        second = _make_shard_result(repos_found=[duplicate_alpha, repo_gamma], api_calls=2, errors=[], wall_clock_s=1.2)
        merged = experiment.deterministic_merge([first, second])
        merged_repos = _extract_repos(merged)
        assert [repo["full_name"] for repo in merged_repos].count("octo/alpha") == 1
        assert {repo["full_name"] for repo in merged_repos} == {"octo/alpha", "octo/beta", "tools/gamma"}
        alpha = next(repo for repo in merged_repos if repo["full_name"] == "octo/alpha")
        assert alpha["stars_gained"] == 42

    def test_same_inputs_produce_byte_identical_output_regardless_of_shard_order(
        self, repo_alpha: dict[str, Any], repo_beta: dict[str, Any], repo_gamma: dict[str, Any]
    ) -> None:
        shard_a = _make_shard_result(repos_found=[repo_alpha, repo_gamma], api_calls=3, errors=[], wall_clock_s=1.0)
        shard_b = _make_shard_result(repos_found=[repo_beta], api_calls=2, errors=[], wall_clock_s=1.0)
        merged_ab = experiment.deterministic_merge([shard_a, shard_b])
        merged_ba = experiment.deterministic_merge([shard_b, shard_a])
        assert _canonical_json(merged_ab) == _canonical_json(merged_ba)


class TestCompareResults:
    def test_calculates_speedup_and_api_growth(self, repo_alpha: dict[str, Any], repo_beta: dict[str, Any]) -> None:
        canonical = {"repos": [repo_alpha, repo_beta], "metadata": {"note": "stable"}}
        baseline = {"wall_clock_s": 100.0, "api_calls": 100, "output": canonical, "canonical_output": canonical}
        shard = {"wall_clock_s": 70.0, "api_calls": 108, "output": canonical, "canonical_output": canonical}
        comparison = experiment.compare_results(baseline, shard)
        assert _percent(_metric(comparison, "speedup_pct", "speedup_percent", "speedup")) == pytest.approx(30.0)
        assert _percent(_metric(comparison, "api_growth_pct", "api_growth_percent", "api_growth")) == pytest.approx(8.0)

    def test_output_stability_ignores_timestamp_fields(
        self, repo_alpha: dict[str, Any], repo_beta: dict[str, Any]
    ) -> None:
        baseline = {
            "wall_clock_s": 100.0,
            "api_calls": 100,
            "output": {
                "week": "2026-W24",
                "crawled_at": "2026-06-13T12:00:00Z",
                "report_generated_at": "2026-06-13T12:00:01Z",
                "repos": [repo_alpha, repo_beta],
            },
        }
        shard = {
            "wall_clock_s": 75.0,
            "api_calls": 105,
            "output": {
                "week": "2026-W24",
                "crawled_at": "2026-06-13T12:10:00Z",
                "report_generated_at": "2026-06-13T12:10:01Z",
                "repos": [repo_alpha, repo_beta],
            },
        }
        comparison = experiment.compare_results(baseline, shard)
        assert bool(_metric(comparison, "output_stable", "stable_output", "is_output_stable")) is True


class TestExperimentReport:
    def test_pass_verdict_when_all_guardrails_are_met(self) -> None:
        report = _make_report(
            {
                "speedup_pct": 30.0,
                "api_growth_pct": 8.0,
                "rate_limit_regression": False,
                "output_stable": True,
                "partial_data": False,
                "baseline_complete": True,
                "shard_complete": True,
            }
        )
        assert _verdict(report) == "pass"

    def test_fail_verdict_when_any_required_criterion_fails(self) -> None:
        report = _make_report(
            {
                "speedup_pct": 20.0,
                "api_growth_pct": 8.0,
                "rate_limit_regression": False,
                "output_stable": True,
                "partial_data": False,
                "baseline_complete": True,
                "shard_complete": True,
            }
        )
        assert _verdict(report) == "fail"

    def test_inconclusive_verdict_for_partial_data(self) -> None:
        report = _make_report(
            {
                "speedup_pct": None,
                "api_growth_pct": None,
                "rate_limit_regression": False,
                "output_stable": False,
                "partial_data": True,
                "baseline_complete": True,
                "shard_complete": False,
            }
        )
        assert _verdict(report) == "inconclusive"

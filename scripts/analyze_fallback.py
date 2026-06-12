#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib import error, parse, request

try:
    from scripts.assemble_historical_context import DEFAULT_CONTENT_ROOT, assemble_historical_context
    from scripts.sanitize_repo_content import sanitize_repo_payload
except ModuleNotFoundError:  # pragma: no cover - script execution path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.assemble_historical_context import DEFAULT_CONTENT_ROOT, assemble_historical_context
    from scripts.sanitize_repo_content import sanitize_repo_payload

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROMPT_TEMPLATE = ROOT / "prompts" / "analyze-weekly.md"
DEFAULT_ANALYZED_DIR = ROOT / "data" / "analyzed"
DEFAULT_WISDOM_FILE = ROOT / ".squad" / "identity" / "wisdom.md"
DEFAULT_SKILLS_DIR = ROOT / ".squad" / "skills"
DEFAULT_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
DEFAULT_MODELS_MODEL = "openai/gpt-4o"
DEFAULT_MODELS_TIMEOUT = 30
ALLOWED_MODELS_HOSTS: frozenset[str] = frozenset({"models.github.ai"})
_JITTER_RANDOM = secrets.SystemRandom()
NO_AI_DIAGNOSTIC_QUALITY_SCORE = 40
DEFAULT_PROMPT_TOKEN_BUDGET = 90_000
COMPACTED_NEW_REPOS_LIMIT = 25
COMPACTED_TRENDING_REPOS_LIMIT = 25
COMPACTED_PREVIOUS_SUMMARY_CHARS = 8_000
COMPACTED_WISDOM_CHARS = 8_000
COMPACTED_SKILLS_CHARS = 10_000
COMPACTED_PRESS_CONTEXT_CHARS = 14_000
COMPACTED_HISTORICAL_CONTEXT_CHARS = 12_000


@dataclass
class PromptComponent:
    name: str
    path: str | None
    included: bool
    inclusion_reason: str
    compaction_decision: str
    bytes: int
    token_estimate: int
    checksum_sha256: str


@dataclass
class EvidenceRepoRef:
    full_name: str
    url: str | None
    description: str | None
    language: str | None
    topics: list[str]
    source: str
    stars: int | None
    stars_gained: int | None
    created_at: str | None


@dataclass
class EvidencePressRef:
    title: str | None
    url: str
    source: str | None
    published_at: str | None
    categories: list[str]
    relevance_score: float | None
    correlation_repos: list[str]


@dataclass
class EvidenceInventory:
    name: str
    path: str
    item_count: int
    bytes: int
    token_estimate: int
    checksum_sha256: str
    repos: list[EvidenceRepoRef]


@dataclass
class PressInventory:
    name: str
    path: str | None
    item_count: int
    bytes: int
    token_estimate: int
    checksum_sha256: str
    articles: list[EvidencePressRef]


@dataclass
class EvidenceSliceRef:
    name: str
    path: str | None
    item_count: int
    bytes: int
    token_estimate: int
    checksum_sha256: str
    provenance: dict[str, Any]
    validation_errors: list[str]


@dataclass
class PromptPreflight:
    schema_version: str
    prompt_token_budget: int
    prompt_tokens: int
    prompt_bytes: int
    prompt_checksum_sha256: str
    rendered_prompt_estimate: dict[str, int | str]
    prompt_within_budget: bool
    degraded: bool
    publish_eligible: bool
    promotion_policy: str
    degradation_reason: str | None
    fallback_policy: str
    components: list[PromptComponent]
    deterministic_slices: list[str]
    generated_evidence_slices: list[EvidenceSliceRef]
    evidence_slice_payloads: dict[str, dict[str, Any]]
    evidence_inventories: list[EvidenceInventory]
    press_inventories: list[PressInventory]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render/preflight weekly analysis prompts or generate diagnostic no-AI output.")
    parser.add_argument("--raw-json", required=True, type=Path, help="Path to the weekly raw JSON payload.")
    parser.add_argument("--output", required=True, type=Path, help="Path to write the analyzed markdown output.")
    parser.add_argument("--current-datetime", required=True, help="ISO-8601 timestamp for the analysis run.")
    parser.add_argument(
        "--prompt-template",
        type=Path,
        default=DEFAULT_PROMPT_TEMPLATE,
        help="Prompt template path (defaults to prompts/analyze-weekly.md).",
    )
    parser.add_argument(
        "--analyzed-dir",
        type=Path,
        default=DEFAULT_ANALYZED_DIR,
        help="Directory containing prior weekly summaries.",
    )
    parser.add_argument(
        "--wisdom-file",
        type=Path,
        default=DEFAULT_WISDOM_FILE,
        help="Path to the learned wisdom markdown file.",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=DEFAULT_SKILLS_DIR,
        help="Directory containing learned skill markdown files.",
    )
    parser.add_argument(
        "--content-root",
        type=Path,
        default=DEFAULT_CONTENT_ROOT,
        help="Path to the content root used for historical context assembly.",
    )
    parser.add_argument(
        "--press-context",
        type=Path,
        default=None,
        help="Path to rendered press context markdown (appended to prompt).",
    )
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="Render the prompt to stdout without calling GitHub Models.",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Generate a data-only summary without calling any AI API.",
    )
    parser.add_argument(
        "--prompt-token-budget",
        type=int,
        default=DEFAULT_PROMPT_TOKEN_BUDGET,
        help=f"Maximum rendered prompt tokens before model invocation (default: {DEFAULT_PROMPT_TOKEN_BUDGET}).",
    )
    parser.add_argument(
        "--preflight-report-json",
        type=Path,
        help="Write deterministic rendered-prompt preflight details as JSON.",
    )
    parser.add_argument(
        "--preflight-report-md",
        type=Path,
        help="Write deterministic rendered-prompt preflight details as Markdown.",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def estimate_tokens(text: str) -> int:
    """Deterministic local estimate used for preflight bounds."""
    return (len(text.encode("utf-8")) + 3) // 4


def checksum_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def checksum_payload(payload: Any) -> str:
    return checksum_text(stable_json(payload))


def _component(
    *,
    name: str,
    content: str,
    path: Path | None,
    included: bool,
    inclusion_reason: str,
    compaction_decision: str,
) -> PromptComponent:
    return PromptComponent(
        name=name,
        path=path.as_posix() if path else None,
        included=included,
        inclusion_reason=inclusion_reason,
        compaction_decision=compaction_decision,
        bytes=len(content.encode("utf-8")),
        token_estimate=estimate_tokens(content),
        checksum_sha256=checksum_text(content),
    )


def _repo_int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _repo_topics(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(topic) for topic in value if isinstance(topic, (str, int, float)) and str(topic).strip()]


REQUIRED_REPO_SLICE_FIELDS = (
    "full_name",
    "url",
    "description",
    "language",
    "topics",
    "stars",
    "stars_gained",
    "created_at",
)


def compact_repo_record(repo: dict[str, Any], *, source: str) -> dict[str, Any]:
    full_name = str(repo.get("full_name") or "").strip()
    url = repo.get("url")
    return {
        "full_name": full_name,
        "url": url if isinstance(url, str) and url.strip() else (f"https://github.com/{full_name}" if full_name else None),
        "description": repo.get("description") if isinstance(repo.get("description"), str) else None,
        "language": repo.get("language") if isinstance(repo.get("language"), str) else None,
        "topics": _repo_topics(repo.get("topics")),
        "stars": _repo_int(repo.get("stars")),
        "stars_gained": _repo_int(repo.get("stars_gained")),
        "created_at": repo.get("created_at") if isinstance(repo.get("created_at"), str) else None,
        "source": source,
    }


def _inventory_repo_refs(payload: dict[str, Any], field: str) -> list[EvidenceRepoRef]:
    repos = payload.get(field)
    if not isinstance(repos, list):
        return []
    refs: list[EvidenceRepoRef] = []
    for repo in repos:
        if not isinstance(repo, dict):
            continue
        full_name = repo.get("full_name")
        if not isinstance(full_name, str) or "/" not in full_name:
            continue
        url = repo.get("url")
        refs.append(
            EvidenceRepoRef(
                full_name=full_name.strip(),
                url=url if isinstance(url, str) and url.strip() else None,
                description=repo.get("description") if isinstance(repo.get("description"), str) else None,
                language=repo.get("language") if isinstance(repo.get("language"), str) else None,
                topics=_repo_topics(repo.get("topics")),
                source=field,
                stars=_repo_int(repo.get("stars")),
                stars_gained=_repo_int(repo.get("stars_gained")),
                created_at=repo.get("created_at") if isinstance(repo.get("created_at"), str) else None,
            )
        )
    return refs


def _evidence_inventory(name: str, payload: dict[str, Any], field: str, path: Path) -> EvidenceInventory:
    content = json.dumps(payload.get(field, []), indent=2, ensure_ascii=False)
    repos = _inventory_repo_refs(payload, field)
    return EvidenceInventory(
        name=name,
        path=path.as_posix(),
        item_count=len(repos),
        bytes=len(content.encode("utf-8")),
        token_estimate=estimate_tokens(content),
        checksum_sha256=checksum_text(content),
        repos=repos,
    )


def _press_paths_for_context(press_context_path: Path | None, week: str) -> tuple[Path | None, Path | None]:
    if press_context_path is None:
        return None, None
    data_dir = press_context_path.parent.parent
    external_path = data_dir / "raw" / f"{week}-external-news.json"
    legacy_path = data_dir / "raw" / f"{week}-techcrunch.json"
    corr_path = data_dir / "analyzed" / f"{week}-correlations.json"
    news_path = external_path if external_path.exists() else legacy_path if legacy_path.exists() else None
    return news_path, corr_path if corr_path.exists() else None


def _safe_load_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _article_inventory(news_payload: dict[str, Any] | None, correlation_payload: dict[str, Any] | None, path: Path | None) -> PressInventory:
    articles = news_payload.get("articles", []) if news_payload else []
    correlations = correlation_payload.get("correlations", []) if correlation_payload else []
    repo_by_url: dict[str, set[str]] = {}
    for corr in correlations if isinstance(correlations, list) else []:
        if not isinstance(corr, dict):
            continue
        repo = corr.get("repo")
        for url in corr.get("matched_articles", []) if isinstance(corr.get("matched_articles"), list) else []:
            if isinstance(url, str) and isinstance(repo, str):
                repo_by_url.setdefault(url, set()).add(repo)
        for detail in corr.get("matched_article_details", []) if isinstance(corr.get("matched_article_details"), list) else []:
            if isinstance(detail, dict) and isinstance(detail.get("url"), str) and isinstance(repo, str):
                repo_by_url.setdefault(detail["url"], set()).add(repo)
    refs: list[EvidencePressRef] = []
    for article in articles if isinstance(articles, list) else []:
        if not isinstance(article, dict) or not isinstance(article.get("url"), str) or not article["url"].strip():
            continue
        categories = article.get("categories") if isinstance(article.get("categories"), list) else []
        relevance = article.get("relevance_score")
        refs.append(
            EvidencePressRef(
                title=article.get("title") if isinstance(article.get("title"), str) else None,
                url=article["url"],
                source=article.get("source") if isinstance(article.get("source"), str) else None,
                published_at=article.get("published_at") if isinstance(article.get("published_at"), str) else None,
                categories=[str(category) for category in categories],
                relevance_score=float(relevance) if isinstance(relevance, (int, float)) and not isinstance(relevance, bool) else None,
                correlation_repos=sorted(repo_by_url.get(article["url"], set())),
            )
        )
    content = stable_json([asdict(ref) for ref in refs])
    return PressInventory(
        name="press_articles",
        path=path.as_posix() if path else None,
        item_count=len(refs),
        bytes=len(content.encode("utf-8")),
        token_estimate=estimate_tokens(content),
        checksum_sha256=checksum_text(content),
        articles=refs,
    )


def _source_ref(path: Path | None, content: str | None = None) -> dict[str, Any] | None:
    if path is None and content is None:
        return None
    if content is None:
        if path is None or not path.exists():
            return None
        data = path.read_bytes()
        return {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    encoded = content.encode("utf-8")
    return {
        "path": path.as_posix() if path else None,
        "bytes": len(encoded),
        "sha256": checksum_text(content),
    }


def _slice_checksum_payload(payload: dict[str, Any]) -> dict[str, Any]:
    stripped = dict(payload)
    stripped.pop("checksum_sha256", None)
    return stripped


def validate_evidence_slice(payload: dict[str, Any], *, expected_checksum: str | None = None) -> list[str]:
    errors: list[str] = []
    for field in ("schema_version", "slice_name", "component", "records", "provenance", "checksum_sha256"):
        if field not in payload:
            errors.append(f"slice missing {field}")
    checksum = payload.get("checksum_sha256")
    if isinstance(checksum, str):
        actual = checksum_payload(_slice_checksum_payload(payload))
        if checksum != actual:
            errors.append("slice checksum mismatch")
        if expected_checksum is not None and checksum != expected_checksum:
            errors.append("slice checksum does not match manifest reference")
    elif "checksum_sha256" in payload:
        errors.append("slice checksum_sha256 must be a string")
    records = payload.get("records")
    if not isinstance(records, list):
        errors.append("slice records must be a list")
        records = []
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("slice provenance must be an object")
    else:
        sources = provenance.get("sources")
        if not isinstance(sources, dict) or not sources:
            errors.append("slice provenance sources missing")
        else:
            for name, source in sources.items():
                if not isinstance(source, dict) or not source.get("sha256") or not isinstance(source.get("bytes"), int):
                    errors.append(f"slice provenance source {name} missing checksum/bytes")
    if payload.get("component") in {"new_repos", "trending_repos"}:
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"record {index} must be an object")
                continue
            for field in REQUIRED_REPO_SLICE_FIELDS:
                if field not in record:
                    errors.append(f"record {index} missing {field}")
    return errors


def _build_slice(name: str, records: list[dict[str, Any]], provenance: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": "analysis_evidence_slice_v1",
        "slice_name": name,
        "component": name,
        "records": records,
        "provenance": provenance,
    }
    payload["checksum_sha256"] = checksum_payload(payload)
    return payload


def build_evidence_slices(
    *,
    week: str,
    raw_path: Path,
    sanitized_payload: dict[str, Any],
    payload_for_prompt: dict[str, Any],
    press_context_path: Path | None,
    press_content: str,
    previous_summary_path: Path | None,
    previous_summary_content: str,
) -> dict[str, dict[str, Any]]:
    raw_source = _source_ref(raw_path)
    press_source = _source_ref(press_context_path, press_content) if press_content else None
    previous_source = _source_ref(previous_summary_path, previous_summary_content) if previous_summary_content else None
    news_path, corr_path = _press_paths_for_context(press_context_path, week)
    news_payload = _safe_load_json(news_path)
    corr_payload = _safe_load_json(corr_path)
    news_source = _source_ref(news_path)
    corr_source = _source_ref(corr_path)
    base_provenance = {"week": week, "sources": {"raw_json": raw_source} if raw_source else {}}
    slices = {
        "new_repos": _build_slice(
            "new_repos",
            [compact_repo_record(repo, source="new_repos") for repo in payload_for_prompt.get("new_repos", []) if isinstance(repo, dict)],
            base_provenance,
        ),
        "trending_repos": _build_slice(
            "trending_repos",
            [
                compact_repo_record(repo, source="trending_repos")
                for repo in payload_for_prompt.get("trending_repos", [])
                if isinstance(repo, dict)
            ],
            base_provenance,
        ),
    }
    press_sources = {}
    for key, source in (("raw_json", raw_source), ("press_context", press_source), ("external_news", news_source), ("correlations", corr_source)):
        if source:
            press_sources[key] = source
    press_records: list[dict[str, Any]] = []
    correlations = corr_payload.get("correlations", []) if corr_payload else []
    for corr in correlations if isinstance(correlations, list) else []:
        if isinstance(corr, dict):
            press_records.append(
                {
                    "repo": corr.get("repo"),
                    "matched_articles": corr.get("matched_articles", []),
                    "matched_article_details": corr.get("matched_article_details", []),
                    "match_type": corr.get("match_type"),
                    "correlation_confidence": corr.get("correlation_confidence"),
                    "correlation_strength": corr.get("correlation_strength"),
                    "hype_risk": corr.get("hype_risk"),
                }
            )
    if not press_records and press_content:
        urls = sorted(set(re.findall(r"https?://[^\s)\]]+", press_content)))
        press_records = [{"url": url.rstrip(".,"), "source": "rendered_press_context"} for url in urls]
    slices["press_correlations"] = _build_slice(
        "press_correlations",
        press_records,
        {"week": week, "sources": press_sources},
    )
    prior_sources = {"raw_json": raw_source} if raw_source else {}
    if previous_source:
        prior_sources["prior_summary"] = previous_source
    slices["prior_continuity"] = _build_slice(
        "prior_continuity",
        [
            {
                "source_path": previous_summary_path.as_posix() if previous_summary_path else None,
                "present": bool(previous_summary_content),
                "excerpt": previous_summary_content[:1000],
            }
        ],
        {"week": week, "sources": prior_sources},
    )
    return slices


def write_evidence_slices(slices: dict[str, dict[str, Any]], manifest_path: Path | None) -> list[EvidenceSliceRef]:
    refs: list[EvidenceSliceRef] = []
    output_dir = manifest_path.parent / "evidence-slices" if manifest_path else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    for name in sorted(slices):
        payload = slices[name]
        checksum = str(payload["checksum_sha256"])
        text = stable_json(payload)
        path = output_dir / f"{name}-{checksum[:12]}.json" if output_dir else None
        if path:
            path.write_text(text, encoding="utf-8")
        refs.append(
            EvidenceSliceRef(
                name=name,
                path=path.as_posix() if path else None,
                item_count=len(payload.get("records", [])) if isinstance(payload.get("records"), list) else 0,
                bytes=len(text.encode("utf-8")),
                token_estimate=estimate_tokens(text),
                checksum_sha256=checksum,
                provenance=payload.get("provenance", {}) if isinstance(payload.get("provenance"), dict) else {},
                validation_errors=validate_evidence_slice(payload),
            )
        )
    return refs


def truncate_with_notice(content: str, limit: int, label: str) -> tuple[str, str]:
    if len(content) <= limit:
        return content, "included"
    omitted = len(content) - limit
    return (
        content[:limit].rstrip()
        + f"\n\n[Preflight compaction: truncated {label}; omitted {omitted} characters to stay within prompt budget.]",
        "compacted",
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return {}
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        payload = yaml.safe_load(f) or {}
    return payload if isinstance(payload, dict) else {}


def _resolve_existing_path(configured: str | None, fallback: Path) -> Path:
    candidates: list[Path] = []
    if configured:
        configured_path = Path(configured)
        candidates.append(configured_path if configured_path.is_absolute() else ROOT / configured_path)
        if not configured_path.is_absolute():
            candidates.append(ROOT / ".squad" / configured_path)
    candidates.append(fallback)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else fallback


def resolve_analysis_context_paths() -> tuple[Path, Path]:
    """Resolve analysis-specific learned context, avoiding unrelated squad workflow context."""
    config = _load_yaml(ROOT / "squadscope.topic.yml")
    topic = config.get("topic") if isinstance(config.get("topic"), dict) else {}
    learning = config.get("learning") if isinstance(config.get("learning"), dict) else {}
    topic_id = str(topic.get("id") or "general")
    wisdom_path = _resolve_existing_path(
        learning.get("wisdom_file"),
        ROOT / ".squad" / "topics" / topic_id / "wisdom.md",
    )
    skills_path = _resolve_existing_path(
        learning.get("skills_dir"),
        ROOT / ".squad" / "topics" / topic_id / "skills",
    )
    return wisdom_path, skills_path


def find_previous_summary(current_week: str, analyzed_dir: Path) -> Path | None:
    if not analyzed_dir.exists():
        return None

    candidates = []
    for path in analyzed_dir.glob("*-summary.md"):
        week = path.name.removesuffix("-summary.md")
        if week < current_week:
            candidates.append(path)
    return max(candidates, default=None)


def render_wisdom(wisdom_file: Path) -> str:
    if not wisdom_file.exists():
        return "_No learned wisdom has been recorded yet._"

    content = wisdom_file.read_text(encoding="utf-8").strip()
    if not content:
        return "_No learned wisdom has been recorded yet._"
    # Sanitize boundary markers to prevent fence escape from prior LLM output
    from scripts.sanitize_repo_content import _escape_untrusted_boundaries
    return _escape_untrusted_boundaries(content)


def iter_skill_files(skills_dir: Path) -> list[Path]:
    if not skills_dir.exists():
        return []
    return sorted(path for path in skills_dir.rglob("*.md") if path.is_file())


def render_skills(skills_dir: Path) -> str:
    skill_files = iter_skill_files(skills_dir)
    if not skill_files:
        return "_No learned skills have been extracted yet._"

    from scripts.sanitize_repo_content import _escape_untrusted_boundaries

    blocks = []
    for path in skill_files:
        relative_path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        # Sanitize boundary markers to prevent fence escape from prior LLM output
        content = _escape_untrusted_boundaries(content)
        blocks.append(f"--- Skill Source: {relative_path} ---\n{content}")
    return "\n\n".join(blocks) if blocks else "_No learned skills have been extracted yet._"


def _sort_repos_for_compaction(repos: list[dict[str, Any]], score_key: str) -> list[dict[str, Any]]:
    return sorted(
        repos,
        key=lambda repo: (
            int(repo.get(score_key) or 0),
            int(repo.get("stars") or 0),
            str(repo.get("full_name") or ""),
        ),
        reverse=True,
    )


def compact_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    compacted = dict(payload)
    decisions = {"new_repos": "included", "trending_repos": "included"}
    new_repos = payload.get("new_repos")
    if isinstance(new_repos, list) and len(new_repos) > COMPACTED_NEW_REPOS_LIMIT:
        compacted["new_repos"] = _sort_repos_for_compaction(new_repos, "stars")[:COMPACTED_NEW_REPOS_LIMIT]
        decisions["new_repos"] = f"compacted to top {COMPACTED_NEW_REPOS_LIMIT} repos by stars"
    trending_repos = payload.get("trending_repos")
    if isinstance(trending_repos, list) and len(trending_repos) > COMPACTED_TRENDING_REPOS_LIMIT:
        compacted["trending_repos"] = _sort_repos_for_compaction(trending_repos, "stars_gained")[
            :COMPACTED_TRENDING_REPOS_LIMIT
        ]
        decisions["trending_repos"] = f"compacted to top {COMPACTED_TRENDING_REPOS_LIMIT} repos by stars_gained/stars"
    if decisions["new_repos"] != "included" or decisions["trending_repos"] != "included":
        compacted["_preflight_compaction"] = {
            "reason": "Rendered prompt exceeded explicit token budget before model invocation.",
            "new_repos_original_count": len(new_repos) if isinstance(new_repos, list) else 0,
            "trending_repos_original_count": len(trending_repos) if isinstance(trending_repos, list) else 0,
            "new_repos_decision": decisions["new_repos"],
            "trending_repos_decision": decisions["trending_repos"],
        }
    return compacted, decisions


def _build_prompt(
    *,
    prompt_template_path: Path,
    raw_json_path: Path,
    output_path: Path,
    current_datetime: str,
    analyzed_dir: Path,
    content_root: Path = DEFAULT_CONTENT_ROOT,
    wisdom_file: Path = DEFAULT_WISDOM_FILE,
    skills_dir: Path = DEFAULT_SKILLS_DIR,
    press_context_path: Path | None = None,
    prompt_token_budget: int = DEFAULT_PROMPT_TOKEN_BUDGET,
    allow_compaction: bool = True,
) -> tuple[str, PromptPreflight]:
    payload = load_json(raw_json_path)
    sanitized_payload = sanitize_repo_payload(payload)
    current_week = sanitized_payload["week"]
    previous_summary_path = find_previous_summary(current_week, analyzed_dir)
    previous_summary_content = previous_summary_path.read_text(encoding="utf-8") if previous_summary_path else ""
    historical_context_content = assemble_historical_context(
        current_datetime=current_datetime,
        previous_summary_path=previous_summary_path,
        content_root=content_root,
        max_words=1_500,
        prompt_token_budget=prompt_token_budget,
    ).strip()
    from scripts.sanitize_repo_content import _escape_untrusted_boundaries

    historical_context_content = _escape_untrusted_boundaries(historical_context_content)
    if not historical_context_content:
        historical_context_content = "_No historical context was available beyond the current weekly payload._"
    wisdom_content = render_wisdom(wisdom_file)
    skills_content = render_skills(skills_dir)
    press_content = (
        press_context_path.read_text(encoding="utf-8").strip()
        if press_context_path and press_context_path.exists() and press_context_path.stat().st_size > 0
        else ""
    )
    payload_for_prompt = sanitized_payload
    raw_decisions = {"new_repos": "included", "trending_repos": "included"}
    previous_decision = "included" if previous_summary_path else "not included: no previous summary"
    historical_context_decision = (
        "included"
        if historical_context_content != "_No historical context was available beyond the current weekly payload._"
        else "not included: no historical sources available"
    )
    wisdom_decision = "included" if wisdom_file.exists() else "not included: no analysis-specific wisdom file"
    skills_decision = "included" if skills_dir.exists() and iter_skill_files(skills_dir) else "not included: no analysis-specific skills"
    press_decision = "included" if press_content else "not included: no press context"
    degraded = False

    def assemble() -> str:
        raw_json_content = json.dumps(payload_for_prompt, indent=2, ensure_ascii=False)
        current_year, _, week_number = current_week.partition("-W")
        generic_title_example = (
            f"Week {int(week_number)}, {current_year} Analysis" if week_number.isdigit() else "Week NN, YYYY Analysis"
        )
        prompt = prompt_template_path.read_text(encoding="utf-8")
        replacements = {
            "{{CURRENT_DATETIME}}": current_datetime,
            "{{CURRENT_WEEK}}": current_week,
            "{{CURRENT_YEAR}}": current_year,
            "{{TITLE_TEMPLATE_HINT}}": (
                f"Specific editorial headline about {current_week}'s dominant themes "
                f"(not \"{generic_title_example}\")"
            ),
            "{{RAW_JSON_PATH}}": str(raw_json_path),
            "{{OUTPUT_PATH}}": str(output_path),
            "{{PREVIOUS_SUMMARY_PATH_OR_NONE}}": str(previous_summary_path) if previous_summary_path else "None",
            "{{HISTORICAL_CONTEXT}}": historical_context_content,
            "{{RAW_JSON_CONTENT}}": raw_json_content,
            "{{PREVIOUS_SUMMARY_CONTENT_OR_EMPTY}}": previous_summary_content.strip(),
            "{{WISDOM}}": wisdom_content,
            "{{SKILLS}}": skills_content,
        }
        for needle, value in replacements.items():
            prompt = prompt.replace(needle, value)
        if press_content:
            prompt += f"\n\n---\n## Press Context\n\n{press_content}\n"
        return prompt

    prompt = assemble()
    if allow_compaction and estimate_tokens(prompt) > prompt_token_budget:
        degraded = True
        payload_for_prompt, raw_decisions = compact_payload(sanitized_payload)
        previous_summary_content, previous_decision = truncate_with_notice(
            previous_summary_content, COMPACTED_PREVIOUS_SUMMARY_CHARS, "prior continuity"
        )
        if historical_context_decision == "included":
            historical_context_content, historical_context_decision = truncate_with_notice(
                historical_context_content,
                COMPACTED_HISTORICAL_CONTEXT_CHARS,
                "historical context",
            )
        wisdom_content, wisdom_decision = truncate_with_notice(wisdom_content, COMPACTED_WISDOM_CHARS, "analysis wisdom")
        skills_content, skills_decision = truncate_with_notice(skills_content, COMPACTED_SKILLS_CHARS, "analysis skills")
        press_content, press_decision = truncate_with_notice(
            press_content, COMPACTED_PRESS_CONTEXT_CHARS, "press correlations"
        )
        prompt = assemble()

    raw_json_content = json.dumps(payload_for_prompt, indent=2, ensure_ascii=False)
    current_year, _, week_number = current_week.partition("-W")
    components = [
        _component(
            name="prompt_template",
            content=prompt_template_path.read_text(encoding="utf-8"),
            path=prompt_template_path,
            included=True,
            inclusion_reason="Base weekly analysis instructions.",
            compaction_decision="included",
        ),
        _component(
            name="new_repos",
            content=json.dumps(payload_for_prompt.get("new_repos", []), indent=2, ensure_ascii=False),
            path=raw_json_path,
            included=True,
            inclusion_reason="Deterministic mapper slice: newly discovered repositories.",
            compaction_decision=raw_decisions["new_repos"],
        ),
        _component(
            name="trending_repos",
            content=json.dumps(payload_for_prompt.get("trending_repos", []), indent=2, ensure_ascii=False),
            path=raw_json_path,
            included=True,
            inclusion_reason="Deterministic mapper slice: continuing/trending repositories.",
            compaction_decision=raw_decisions["trending_repos"],
        ),
        _component(
            name="raw_metadata",
            content=raw_json_content,
            path=raw_json_path,
            included=True,
            inclusion_reason=f"Sanitized current weekly payload for {current_year}-W{week_number}.",
            compaction_decision="included" if not degraded else "included with compacted repo slices",
        ),
        _component(
            name="prior_continuity",
            content=previous_summary_content,
            path=previous_summary_path,
            included=bool(previous_summary_path),
            inclusion_reason="Deterministic mapper slice: prior weekly continuity.",
            compaction_decision=previous_decision,
        ),
        _component(
            name="historical_context",
            content=historical_context_content,
            path=content_root,
            included=bool(historical_context_content),
            inclusion_reason="Bounded historical context synthesized from rolling, previous-week, monthly, and yearly reports.",
            compaction_decision=historical_context_decision,
        ),
        _component(
            name="analysis_wisdom",
            content=wisdom_content,
            path=wisdom_file,
            included=wisdom_file.exists(),
            inclusion_reason="Analysis-specific wisdom capsule from topic learning state.",
            compaction_decision=wisdom_decision,
        ),
        _component(
            name="analysis_skills",
            content=skills_content,
            path=skills_dir,
            included=skills_dir.exists() and bool(iter_skill_files(skills_dir)),
            inclusion_reason="Analysis-specific learned skill capsule from topic learning state.",
            compaction_decision=skills_decision,
        ),
        _component(
            name="press_correlations",
            content=press_content,
            path=press_context_path,
            included=bool(press_content),
            inclusion_reason="Deterministic mapper slice: press/developer correlation context.",
            compaction_decision=press_decision,
        ),
        _component(
            name="rendered_prompt",
            content=prompt,
            path=None,
            included=True,
            inclusion_reason="Exact prompt that will be passed to Copilot CLI.",
            compaction_decision="included" if not degraded else "included after deterministic compaction",
        ),
    ]
    prompt_tokens = estimate_tokens(prompt)
    prompt_within_budget = prompt_tokens <= prompt_token_budget
    degradation_reason = (
        "Prompt was deterministically compacted to fit the configured token budget." if degraded else None
    )
    evidence_slices = build_evidence_slices(
        week=current_week,
        raw_path=raw_json_path,
        sanitized_payload=sanitized_payload,
        payload_for_prompt=payload_for_prompt,
        press_context_path=press_context_path,
        press_content=press_content,
        previous_summary_path=previous_summary_path,
        previous_summary_content=previous_summary_content,
    )
    news_path, corr_path = _press_paths_for_context(press_context_path, current_week)
    press_inventory = _article_inventory(_safe_load_json(news_path), _safe_load_json(corr_path), news_path)
    slice_refs = write_evidence_slices(evidence_slices, None)
    preflight = PromptPreflight(
        schema_version="analysis_input_manifest_v1",
        prompt_token_budget=prompt_token_budget,
        prompt_tokens=prompt_tokens,
        prompt_bytes=len(prompt.encode("utf-8")),
        prompt_checksum_sha256=checksum_text(prompt),
        rendered_prompt_estimate={
            "bytes": len(prompt.encode("utf-8")),
            "tokens": prompt_tokens,
            "checksum_sha256": checksum_text(prompt),
        },
        prompt_within_budget=prompt_within_budget,
        degraded=degraded,
        publish_eligible=prompt_within_budget and not degraded,
        promotion_policy=(
            "normal-promotion"
            if not degraded
            else "staged/candidate-only by default; degraded compacted output requires an explicit future promotion policy."
        ),
        degradation_reason=degradation_reason,
        fallback_policy=(
            "copilot-only; no GitHub Models/OpenAI fallback. no-ai is diagnostic/staged-only and publish-ineligible. "
            "degraded/compacted prompts are staged/candidate-only by default."
        ),
        components=components,
        deterministic_slices=["new_repos", "trending_repos", "press_correlations", "prior_continuity"],
        generated_evidence_slices=slice_refs,
        evidence_slice_payloads=evidence_slices,
        evidence_inventories=[
            _evidence_inventory("raw_new_repos", sanitized_payload, "new_repos", raw_json_path),
            _evidence_inventory("raw_trending_repos", sanitized_payload, "trending_repos", raw_json_path),
            _evidence_inventory("prompt_new_repos", payload_for_prompt, "new_repos", raw_json_path),
            _evidence_inventory("prompt_trending_repos", payload_for_prompt, "trending_repos", raw_json_path),
        ],
        press_inventories=[press_inventory],
    )
    return prompt, preflight


def render_prompt(
    *,
    prompt_template_path: Path,
    raw_json_path: Path,
    output_path: Path,
    current_datetime: str,
    analyzed_dir: Path,
    content_root: Path = DEFAULT_CONTENT_ROOT,
    wisdom_file: Path = DEFAULT_WISDOM_FILE,
    skills_dir: Path = DEFAULT_SKILLS_DIR,
    press_context_path: Path | None = None,
) -> str:
    prompt, _ = _build_prompt(
        prompt_template_path=prompt_template_path,
        raw_json_path=raw_json_path,
        output_path=output_path,
        current_datetime=current_datetime,
        analyzed_dir=analyzed_dir,
        content_root=content_root,
        wisdom_file=wisdom_file,
        skills_dir=skills_dir,
        press_context_path=press_context_path,
        allow_compaction=False,
    )
    return prompt


def write_preflight_reports(preflight: PromptPreflight, json_path: Path | None, md_path: Path | None) -> None:
    if json_path and preflight.evidence_slice_payloads:
        preflight.generated_evidence_slices = write_evidence_slices(preflight.evidence_slice_payloads, json_path)
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(asdict(preflight), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if md_path:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            "# Analysis Prompt Preflight",
            "",
            f"- Prompt budget: `{preflight.prompt_token_budget}` tokens",
            f"- Rendered prompt: `{preflight.prompt_tokens}` tokens / `{preflight.prompt_bytes}` bytes",
            f"- Prompt checksum: `{preflight.prompt_checksum_sha256}`",
            f"- Degraded/compacted: `{str(preflight.degraded).lower()}`",
            f"- Degradation reason: {preflight.degradation_reason or 'none'}",
            f"- Publish eligible: `{str(preflight.publish_eligible).lower()}`",
            f"- Promotion policy: {preflight.promotion_policy}",
            f"- Fallback policy: {preflight.fallback_policy}",
            f"- Deterministic slices: {', '.join(preflight.deterministic_slices)}",
            "",
            "| Component | Included | Bytes | Tokens | Checksum | Path | Inclusion reason | Compaction decision |",
            "| --- | --- | ---: | ---: | --- | --- | --- | --- |",
        ]
        for component in preflight.components:
            rows.append(
                "| "
                + " | ".join(
                    [
                        component.name,
                        str(component.included).lower(),
                        str(component.bytes),
                        str(component.token_estimate),
                        component.checksum_sha256,
                        component.path or "",
                        component.inclusion_reason.replace("|", "\\|"),
                        component.compaction_decision.replace("|", "\\|"),
                    ]
                )
                + " |"
            )
        md_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def extract_markdown(response_payload: dict[str, Any]) -> str:
    choices = response_payload.get("choices") or []
    if not choices:
        raise ValueError("GitHub Models response did not include any choices.")

    message = choices[0].get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return content.strip() + "\n"

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("output_text")
                if text:
                    parts.append(text)
        if parts:
            return "\n".join(parts).strip() + "\n"

    text = choices[0].get("text")
    if isinstance(text, str) and text.strip():
        return text.strip() + "\n"

    raise ValueError("GitHub Models response did not contain markdown output.")


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
NON_RETRYABLE_STATUS_CLASSES = {400, 401, 403, 404}
MAX_RETRIES = 3
BASE_DELAY = 2  # seconds


def validate_https_url(url: str, *, label: str, allowed_hosts: frozenset[str] | None = None) -> None:
    parsed = parse.urlparse(url)
    if parsed.scheme.lower() != "https":
        raise ValueError(f"{label} must use HTTPS: {url}")
    if parsed.username or parsed.password:
        raise ValueError(f"{label} must not include credentials: {url}")
    if not parsed.hostname:
        raise ValueError(f"{label} must include a hostname: {url}")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{label} has an invalid port: {url}") from exc
    if port not in (None, 443):
        raise ValueError(f"{label} must not use unexpected ports: {url}")
    if allowed_hosts is not None and parsed.hostname.lower() not in allowed_hosts:
        raise ValueError(f"{label} host must be one of {sorted(allowed_hosts)}: {url}")


def validate_output_safety(output: str, canary: str | None = None) -> list[str]:
    """Check generated analysis output for canary leaks and injection artifacts.

    Returns a list of security violation messages (empty = safe).
    """
    from scripts.canary_token import check_output_for_leak, check_output_for_any_canary

    violations: list[str] = []

    # Check for specific canary leak
    if canary:
        result = check_output_for_leak(output, canary)
        if result.leaked:
            violations.append(
                f"Canary token leaked at position {result.match_position}: "
                f"model may have been manipulated by injected instructions"
            )

    # Check for any canary pattern (catches leaks from prior invocations)
    any_result = check_output_for_any_canary(output)
    if any_result.leaked and (not canary or any_result.canary.lower() != canary.lower()):
        violations.append(
            f"Unknown canary pattern '{any_result.canary}' found at position "
            f"{any_result.match_position}: possible cross-invocation leak"
        )

    # Check for boundary marker leaks (model reproduced internal framing)
    from scripts.sanitize_repo_content import BOUNDARY_OPEN, BOUNDARY_CLOSE
    if BOUNDARY_OPEN in output:
        violations.append(
            "Output contains <untrusted-content> boundary marker — "
            "model may have leaked prompt structure"
        )
    if BOUNDARY_CLOSE in output:
        violations.append(
            "Output contains </untrusted-content> boundary marker — "
            "model may have leaked prompt structure"
        )

    return violations


def call_github_models(prompt: str) -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required for GitHub Models fallback.")

    # Inject canary token for output leak detection
    from scripts.canary_token import generate_canary, inject_canary
    canary = generate_canary()
    prompt = inject_canary(prompt, canary)

    endpoint = os.environ.get("GITHUB_MODELS_ENDPOINT", DEFAULT_MODELS_ENDPOINT)
    validate_https_url(endpoint, label="GitHub Models endpoint", allowed_hosts=ALLOWED_MODELS_HOSTS)
    model = os.environ.get("GITHUB_MODELS_MODEL", DEFAULT_MODELS_MODEL)
    timeout = int(os.environ.get("GITHUB_MODELS_TIMEOUT", str(DEFAULT_MODELS_TIMEOUT)))
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }
    body = json.dumps(payload).encode("utf-8")

    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=timeout) as response:  # nosec B310
                response_payload = json.load(response)
            markdown = extract_markdown(response_payload)
            # Validate output for canary leak and injection artifacts
            violations = validate_output_safety(markdown, canary)
            if violations:
                msg = f"Output safety violations detected: {'; '.join(violations)}"
                # Full canary leak = prompt injection confirmed; block publishing
                canary_leaked = any("Canary token leaked" in v for v in violations)
                if canary_leaked:
                    raise RuntimeError(f"BLOCKED: {msg}")
                # Partial/boundary leaks are warnings — log but allow
                print(f"::warning::{msg}", file=sys.stderr)
            return markdown
        except error.HTTPError as exc:
            if exc.code not in RETRYABLE_STATUS_CODES or attempt == MAX_RETRIES:
                detail = exc.read().decode("utf-8", errors="replace")
                retry_class = (
                    "non-retryable"
                    if exc.code in NON_RETRYABLE_STATUS_CLASSES or exc.code not in RETRYABLE_STATUS_CODES
                    else "retry-exhausted"
                )
                access_hint = " GitHub Models access is unavailable for this model." if exc.code == 403 else ""
                raise RuntimeError(
                    f"GitHub Models API request failed ({exc.code}, {retry_class}): {detail}{access_hint}"
                ) from exc
            # Determine delay: respect Retry-After header on 429
            retry_after = exc.headers.get("Retry-After") if exc.code == 429 and exc.headers is not None else None
            if retry_after is not None:
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = BASE_DELAY ** (attempt + 1)
            else:
                delay = BASE_DELAY ** (attempt + 1)
            jitter = _JITTER_RANDOM.uniform(0, 1)
            total_delay = delay + jitter
            print(
                f"[retry] GitHub Models API returned {exc.code}, "
                f"retrying in {total_delay:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})",
                file=sys.stderr,
            )
            last_exc = exc
            time.sleep(total_delay)
        except error.URLError as exc:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"GitHub Models API request failed: {exc.reason}"
                ) from exc
            delay = BASE_DELAY ** (attempt + 1) + _JITTER_RANDOM.uniform(0, 1)
            print(
                f"[retry] GitHub Models API network error: {exc.reason}, "
                f"retrying in {delay:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})",
                file=sys.stderr,
            )
            last_exc = exc
            time.sleep(delay)

    # Should not be reached, but satisfy type checkers
    raise RuntimeError("GitHub Models API request failed after retries") from last_exc


def _strip_ai_instructions(content: str) -> str:
    """Remove AI-facing instruction blocks from a rendered press context string.

    Strips:
    - The "### Instructions" section (from that heading to the next "###" or EOF)
    - The "#### Divergence Instructions" block (heading + bullet items)
    - Truncates the "### Correlation Summary" list to the first 10 entries,
      appending a "…and N more" summary line when truncation occurs.
    """
    import re  # noqa: PLC0415

    # Strip ### Instructions section (to next ### heading or EOF)
    content = re.sub(
        r"\n### Instructions\n.*?(?=\n###|\Z)",
        "",
        content,
        flags=re.DOTALL,
    )

    # Strip #### Divergence Instructions block (to next #### / ### heading or EOF)
    content = re.sub(
        r"\n#### Divergence Instructions\n.*?(?=\n####|\n###|\Z)",
        "",
        content,
        flags=re.DOTALL,
    )

    # Truncate correlations list to top 10
    corr_match = re.search(
        r"(### Correlation Summary\n[^\n]*\n)((?:- [^\n]*\n?)+)",
        content,
    )
    if corr_match:
        header = corr_match.group(1)
        list_block = corr_match.group(2)
        list_lines = [ln for ln in list_block.splitlines() if ln.startswith("- ")]
        total = len(list_lines)
        if total > 10:
            omitted = total - 10
            truncated = "\n".join(list_lines[:10])
            truncated += f"\n…and {omitted} more repos with press correlation\n"
            content = (
                content[: corr_match.start()]
                + header
                + truncated
                + content[corr_match.end() :]
            )

    # Truncate divergence lists to top 10 items each
    for section_header in (
        r"#### 🔍 Tech Trends Without Dev Activity",
        r"#### 🚀 Dev Activity Without Press Coverage",
    ):
        div_match = re.search(
            rf"({re.escape(section_header)}\n[^\n]*\n\n?)((?:- [^\n]*\n?)+)",
            content,
        )
        if div_match:
            header = div_match.group(1)
            list_block = div_match.group(2)
            list_lines = [ln for ln in list_block.splitlines() if ln.startswith("- ")]
            total = len(list_lines)
            if total > 10:
                omitted = total - 10
                truncated = "\n".join(list_lines[:10])
                truncated += f"\n- …and {omitted} more topics\n"
                content = (
                    content[: div_match.start()]
                    + header
                    + truncated
                    + content[div_match.end() :]
                )

    # Add reader-friendly conclusion if divergences exist but instructions were stripped
    if "### Divergence Analysis" in content and "Divergence Instructions" not in content:
        if "These divergences highlight" not in content:
            content = content.rstrip()
            content += (
                "\n\nThese divergences highlight gaps between what the tech industry "
                "is reporting and what developers are actually building.\n"
            )

    return content.strip()


def _render_press_section_no_ai(press_context_path: Path | None) -> str:
    """Render press context data for the no-AI summary (reader-facing)."""
    if not press_context_path or not press_context_path.exists() or press_context_path.stat().st_size == 0:
        return (
            "No industry press data was available for this week's analysis. "
            "Future runs with TechCrunch integration enabled will provide "
            "correlation analysis between developer activity and industry coverage, "
            "highlighting press-driven hype versus organic growth patterns."
        )

    # Try to re-render from raw data using reader_mode=True so the narrative
    # divergence format (from PR #136) is used instead of the AI-prompt format.
    stem = press_context_path.stem  # e.g. "2026-W21-press-context"
    week = stem.replace("-press-context", "")  # e.g. "2026-W21"
    data_dir = press_context_path.parent.parent  # data/analyzed/ -> data/
    external_path = data_dir / "raw" / f"{week}-external-news.json"
    legacy_path = data_dir / "raw" / f"{week}-techcrunch.json"
    tc_path = external_path if external_path.exists() else legacy_path
    corr_path = data_dir / "analyzed" / f"{week}-correlations.json"

    if tc_path.exists():
        from scripts.render_press_context import render_press_context, load_json as rpc_load_json
        tc_data = rpc_load_json(tc_path)
        corr_data = rpc_load_json(corr_path) if corr_path.exists() else {}
        if tc_data is not None:
            return render_press_context(tc_data, corr_data or {}, week, reader_mode=True)

    # Fallback: strip AI instructions from the pre-rendered file.
    content = press_context_path.read_text(encoding="utf-8").strip()
    return _strip_ai_instructions(content)


def generate_no_ai_summary(raw_json_path: Path, current_datetime: str, press_context_path: Path | None = None) -> str:
    """Generate a valid summary from raw JSON without any AI API calls."""
    payload = sanitize_repo_payload(load_json(raw_json_path))
    week = payload["week"]
    new_repos = payload.get("new_repos", [])
    trending_repos = payload.get("trending_repos", [])
    signals = payload.get("signals", {})
    raw_topics = signals.get("top_topics", [])
    top_topics = [t["topic"] if isinstance(t, dict) else str(t) for t in raw_topics]

    total_stars = sum(r.get("stars", 0) for r in new_repos + trending_repos)
    repos_featured = len(new_repos) + len(trending_repos)

    all_repos = sorted(new_repos + trending_repos, key=lambda r: r.get("stars", 0), reverse=True)
    top_repo = all_repos[0]["full_name"] if all_repos else "unknown/unknown"

    tags = top_topics[:5] if len(top_topics) >= 3 else ["open-source", "developer-tools", "automation"]

    # Notable new repos
    notable_new = sorted(new_repos, key=lambda r: r.get("stars", 0), reverse=True)[:10]
    notable_lines = []
    for repo in notable_new:
        desc = repo.get("description") or "No description provided"
        lang = repo.get("language") or "Unknown"
        notable_lines.append(
            f"- [{repo['full_name']}]({repo.get('url', '#')}) ({lang}, "
            f"{repo.get('stars', 0):,} stars): {desc}"
        )
    notable_section = "\n".join(notable_lines) if notable_lines else "No new repositories were captured this week."

    # Trending repos
    top_trending = sorted(trending_repos, key=lambda r: r.get("stars", 0), reverse=True)[:10]
    trending_lines = []
    for repo in top_trending:
        desc = repo.get("description") or "No description provided"
        lang = repo.get("language") or "Unknown"
        trending_lines.append(
            f"- [{repo['full_name']}]({repo.get('url', '#')}) ({lang}, "
            f"{repo.get('stars', 0):,} stars): {desc}"
        )
    trending_section = "\n".join(trending_lines) if trending_lines else "No trending repositories were captured this week."

    # Language breakdown
    lang_counts: dict[str, int] = {}
    for repo in all_repos:
        lang = repo.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    top_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    lang_summary = ", ".join(f"{lang} ({count})" for lang, count in top_langs) if top_langs else "diverse mix of languages"

    year_str = week.split("-W")[0]
    week_num = week.split("-W")[1]
    topics_str = ", ".join(top_topics[:8]) if top_topics else "not available from this crawl"
    title_topics = [topic.replace("-", " ").title() for topic in top_topics[:2] if topic]
    if len(title_topics) == 2:
        fallback_title = f"{title_topics[0]}, {title_topics[1]}, and This Week's Repo Signals"
    elif len(title_topics) == 1:
        fallback_title = f"{title_topics[0]} Leads This Week's Repo Signals"
    else:
        fallback_title = f"{top_repo.split('/')[-1]} Leads This Week's Repo Signals"

    markdown = f'''---
title: "{fallback_title}"
date: {current_datetime}
week: "{week}"
year: {int(year_str)}
tags: [{", ".join(tags)}]
categories: [weekly]
repos_featured: {repos_featured}
stars_tracked: {total_stars}
top_repo: "{top_repo}"
quality_score: {NO_AI_DIAGNOSTIC_QUALITY_SCORE}
summary: "Automated data-only summary for {week}. AI analysis was unavailable; this report presents raw crawl statistics and top repositories without editorial commentary."
---

## This Week's Trends

Without AI-powered analysis, this section reports observed patterns from crawl data rather than synthesized editorial trends. The top community topics this week are {topics_str}, and the dominant languages are {lang_summary}. These signals point to where developer attention is concentrated, though qualitative interpretation of which patterns are durable versus incidental requires a full AI-enabled analysis run.

The crawler captured {repos_featured} repositories this week ({len(new_repos)} new, {len(trending_repos)} trending) with {total_stars:,} cumulative stars. The top repository by star count is [{top_repo}](https://github.com/{top_repo}). Raw patterns suggest continued investment in {lang_summary}, but without editorial judgment these should be treated as directional rather than conclusive.

## Where Industry Meets Code

{_render_press_section_no_ai(press_context_path)}

## Signal & Noise

The primary observable signal this week comes from language and topic distribution. The top languages are {lang_summary}. The top community topics are {topics_str}. These patterns indicate where developer attention is concentrating and what categories are gaining traction relative to prior weeks.

Without AI-powered filtering, distinguishing signal from noise requires manual review. Some repositories in the crawl may represent low-quality forks, exploit tools, or promotional projects that inflate topic counts without contributing meaningful innovation. Future AI-enabled runs will provide better noise filtering and critical editorial judgment.

## Blind Spots

This automated summary lacks the editorial judgment that AI analysis would normally provide. Specific blind spots in this report include: comparative trend analysis against prior weeks, qualitative assessment of repository significance, identification of emerging ecosystem patterns not visible from raw metrics, and filtering of low-signal entries that inflate topic counts. The raw data is preserved for future re-analysis when AI capabilities become available.

## The Week Ahead

Week {week_num} of {year_str} captured {repos_featured} repositories with {total_stars:,} cumulative stars tracked. The top repository is [{top_repo}](https://github.com/{top_repo}). This summary was generated without AI assistance and presents factual crawl statistics only. A full analytical run should be attempted when AI model access is restored to provide trend synthesis and editorial judgment.

## Key References

### Notable Projects

{notable_section}

### Press & Industry

{_render_press_section_no_ai(press_context_path) if press_context_path else "No press data was provided this week."}
'''
    return markdown.strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    wisdom_file = args.wisdom_file
    skills_dir = args.skills_dir
    if wisdom_file == DEFAULT_WISDOM_FILE and skills_dir == DEFAULT_SKILLS_DIR:
        wisdom_file, skills_dir = resolve_analysis_context_paths()

    prompt, preflight = _build_prompt(
        prompt_template_path=args.prompt_template,
        raw_json_path=args.raw_json,
        output_path=args.output,
        current_datetime=args.current_datetime,
        analyzed_dir=args.analyzed_dir,
        content_root=args.content_root,
        wisdom_file=wisdom_file,
        skills_dir=skills_dir,
        press_context_path=args.press_context,
        prompt_token_budget=args.prompt_token_budget,
        allow_compaction=True,
    )
    write_preflight_reports(preflight, args.preflight_report_json, args.preflight_report_md)

    if not preflight.prompt_within_budget:
        print(
            "::error::Rendered analysis prompt exceeds explicit budget after deterministic compaction: "
            f"{preflight.prompt_tokens}/{preflight.prompt_token_budget} tokens.",
            file=sys.stderr,
        )
        return 1

    if args.print_prompt:
        sys.stdout.write(prompt)
        return 0

    if args.no_ai:
        markdown = generate_no_ai_summary(args.raw_json, args.current_datetime, args.press_context)
    else:
        print(
            "::error::GitHub Models/OpenAI analysis fallback is disabled; use Copilot CLI or --no-ai for staged diagnostics.",
            file=sys.stderr,
        )
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

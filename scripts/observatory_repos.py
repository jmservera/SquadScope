"""Generate read-only Claracle Data Observatory repository pages from checked-in crawl data."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import tomllib
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path
from typing import Any

import yaml

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import taxonomy_registry

DEFAULT_CONFIG = Path("config/observatory.toml")
DEFAULT_LIFECYCLE_LEDGER = Path("data/derived/observatory/repository-lifecycle.json")
DEFAULT_IDENTITY_BACKFILL = Path("data/derived/observatory/repo-identity-backfill.json")
GENERATED_BY = "observatory_repo_pages"
LIFECYCLE_SCHEMA_VERSION = 1
WEEKLY_LINK_PREFIX = "/weekly"


@dataclass(frozen=True)
class RepoObservation:
    week: str
    source_bucket: str
    owner: str
    name: str
    full_name: str
    url: str
    description: str | None
    language: str | None
    stars: int | None
    forks: int | None
    created_at: str | None
    topics: tuple[str, ...]
    source_path: str
    github_id: str | None = None
    node_id: str | None = None
    archived: bool = False
    disabled: bool = False
    updated_at: str | None = None
    pushed_at: str | None = None
    api_url: str | None = None


@dataclass
class RepositoryHistory:
    key: str
    github_id: str | None
    node_id: str | None
    display_name: str
    owner: str
    name: str
    slug: str
    url: str
    description: str | None = None
    observations: list[RepoObservation] = field(default_factory=list)
    topics: Counter[str] = field(default_factory=Counter)
    languages: Counter[str] = field(default_factory=Counter)
    lifecycle: dict[str, Any] = field(default_factory=dict)
    prior_full_names: set[str] = field(default_factory=set)
    prior_slugs: set[str] = field(default_factory=set)
    qualified: bool = False
    related_repos: list[dict[str, Any]] = field(default_factory=list)

    @property
    def distinct_weeks(self) -> set[str]:
        return {observation.week for observation in self.observations}

    @property
    def first_seen_week(self) -> str:
        return min(self.distinct_weeks)

    @property
    def last_seen_week(self) -> str:
        return max(self.distinct_weeks)

    @property
    def latest_observation(self) -> RepoObservation:
        # Tie-break same-week observations by source_path, matching
        # lifecycle_ledger_payload()'s serialization order, so the chosen "latest"
        # observation is stable whether histories are freshly computed from raw
        # weeks or reloaded from a persisted ledger round-trip.
        return max(self.observations, key=lambda item: (item.week, item.source_path))

    @property
    def star_history(self) -> list[dict[str, int | str | None]]:
        by_week: dict[str, int | None] = {}
        for observation in sorted(self.observations, key=lambda item: item.week):
            if observation.stars is not None:
                by_week[observation.week] = observation.stars
        history: list[dict[str, int | str | None]] = []
        previous: int | None = None
        for week, stars in sorted(by_week.items()):
            delta = None if previous is None or stars is None else stars - previous
            history.append({"week": week, "stars": stars, "delta": delta})
            previous = stars
        return history


def slug_component(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9-]+", "-", normalized.lower())
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or "repo"


def repo_slug(full_name: str) -> str:
    owner, name = split_full_name(full_name)
    return f"{slug_component(owner)}-{slug_component(name)}"


def split_full_name(full_name: str) -> tuple[str, str]:
    if "/" not in full_name:
        return "unknown", full_name
    owner, name = full_name.split("/", 1)
    return owner, name


def normalize_full_name(full_name: str) -> str:
    return full_name.strip().lower()


def repository_key(github_id: object, full_name: str) -> str:
    if github_id is not None and str(github_id).strip():
        return str(github_id).strip()
    return f"name:{normalize_full_name(full_name)}"


def topic_slug(topic: str) -> str:
    return taxonomy_registry.slugify(topic)


def weekly_permalink(week: str) -> str:
    year, week_id = week.split("-", 1)
    return f"{WEEKLY_LINK_PREFIX}/{year}/{week_id.lower()}/"


def week_start_date(week: str) -> date:
    year, week_id = week.split("-W", 1)
    return date.fromisocalendar(int(year), int(week_id), 1)


def add_years(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        return day.replace(month=2, day=28, year=day.year + years)


def deletion_retention(
    lifecycle: dict[str, Any], *, as_of: date, retention_years: int, identity: str
) -> tuple[date, date]:
    confirmed_text = lifecycle.get("deletion_confirmed_at")
    if not isinstance(confirmed_text, str) or not confirmed_text.strip():
        raise ValueError(f"Deleted repository {identity} requires deletion_confirmed_at")
    try:
        confirmed = date.fromisoformat(confirmed_text)
    except ValueError as error:
        raise ValueError(
            f"Deleted repository {identity} has invalid deletion_confirmed_at: {confirmed_text}"
        ) from error
    if confirmed > as_of:
        raise ValueError(
            f"Deleted repository {identity} has future deletion_confirmed_at: {confirmed_text}"
        )
    retained_until = add_years(confirmed, retention_years)
    supplied_retained_until = lifecycle.get("retained_until")
    if supplied_retained_until is not None:
        try:
            supplied = date.fromisoformat(str(supplied_retained_until))
        except ValueError as error:
            raise ValueError(
                f"Deleted repository {identity} has invalid retained_until: "
                f"{supplied_retained_until}"
            ) from error
        if supplied < retained_until:
            raise ValueError(
                f"Deleted repository {identity} retained_until {supplied} shortens "
                f"configured retention through {retained_until}"
            )
    return confirmed, retained_until


def validate_lifecycle_overrides(
    lifecycle: dict[str, Any], *, as_of: date, retention_years: int
) -> None:
    for identity, override in lifecycle.items():
        if isinstance(override, dict) and override.get("status") == "deleted":
            deletion_retention(
                override,
                as_of=as_of,
                retention_years=retention_years,
                identity=identity,
            )


def load_config(root: Path, config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or root / DEFAULT_CONFIG
    data: dict[str, Any] = {}
    if path.exists():
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    repo_pages = data.get("repo_pages", {})
    threshold = int(repo_pages.get("recurrence_threshold_distinct_weekly_issues", 3))
    operator = repo_pages.get("recurrence_threshold_operator", ">")
    if operator != ">":
        raise ValueError("repo page recurrence threshold currently supports only '>' semantics")
    return {
        "enabled": bool(repo_pages.get("enabled", False)),
        "threshold": threshold,
        "operator": operator,
        "minimum_weeks": threshold + 1,
        "retention_years": int(repo_pages.get("retention_years", 3)),
        "lifecycle": repo_pages.get("lifecycle", {}),
        "ledger_path": root / DEFAULT_LIFECYCLE_LEDGER,
        "identity_backfill_path": root / DEFAULT_IDENTITY_BACKFILL,
        "topics_registry_path": root / "data" / "taxonomy" / "topics.json",
    }


def load_identity_backfill(path: Path) -> dict[str, dict[str, Any]]:
    """Load reviewed GitHub-API identity check results keyed by normalized full_name.

    Entries carry status "found" (resolved github_id/node_id) or "not_found" (a
    verified 404 from the GitHub API, treated as reviewed deletion evidence).
    """
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries")
    if not isinstance(entries, dict):
        raise ValueError("Repository identity backfill entries must be an object")
    return {str(key): value for key, value in entries.items() if isinstance(value, dict)}


def merge_identity_backfill_overrides(
    lifecycle: dict[str, Any] | None, identity_backfill: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Fold confirmed-not-found identity backfill entries in as deletion overrides.

    A verified GitHub API 404 is reviewed deletion evidence, the same as a manual
    override. Manual `[repo_pages.lifecycle]` overrides always win when both exist
    for the same repository, so a human reviewer can supersede the automated check.
    """
    merged: dict[str, Any] = {}
    for full_name, entry in identity_backfill.items():
        if entry.get("status") == "not_found":
            merged[full_name] = {
                "status": "deleted",
                "deletion_confirmed_at": entry.get("checked_at"),
                "status_evidence": "github_api_404_identity_backfill",
            }
    merged.update(lifecycle or {})
    return merged


def raw_week_files(root: Path) -> list[Path]:
    candidates: dict[str, Path] = {}
    raw_dir = root / "data" / "raw"
    for path in sorted(raw_dir.glob("*.json")):
        candidates[path.stem] = path
    archive_dir = root / "data" / "archive" / "recovered-W23-W29"
    for path in sorted(archive_dir.glob("*/**/*.json")):
        candidates.setdefault(path.stem, path)
    return [candidates[week] for week in sorted(candidates)]


def observation_from_record(
    week: str, bucket: str, record: dict[str, Any], source_path: Path, root: Path
) -> RepoObservation | None:
    full_name = str(record.get("full_name") or "").strip()
    if not full_name:
        owner = str(record.get("owner") or "").strip()
        name = str(record.get("name") or "").strip()
        full_name = f"{owner}/{name}" if owner and name else ""
    if not full_name:
        return None
    owner, name = split_full_name(full_name)
    raw_topics = record.get("topics") or []
    topics = tuple(
        sorted({str(topic).strip().lower() for topic in raw_topics if str(topic).strip()})
    )
    stars = record.get("stars")
    forks = record.get("forks")
    return RepoObservation(
        week=week,
        source_bucket=bucket,
        owner=str(record.get("owner") or owner),
        name=str(record.get("name") or name),
        full_name=full_name,
        url=str(record.get("url") or f"https://github.com/{full_name}"),
        description=record.get("description"),
        language=record.get("language"),
        stars=int(stars) if isinstance(stars, int | float) else None,
        forks=int(forks) if isinstance(forks, int | float) else None,
        created_at=record.get("created_at"),
        topics=topics,
        source_path=str(source_path.relative_to(root)),
        github_id=str(record["id"]) if record.get("id") is not None else None,
        node_id=str(record["node_id"]) if record.get("node_id") is not None else None,
        archived=bool(record.get("archived", False)),
        disabled=bool(record.get("disabled", False)),
        updated_at=record.get("updated_at"),
        pushed_at=record.get("pushed_at"),
        api_url=record.get("api_url"),
    )


def observation_to_dict(observation: RepoObservation) -> dict[str, Any]:
    return {
        "week": observation.week,
        "source_bucket": observation.source_bucket,
        "owner": observation.owner,
        "name": observation.name,
        "full_name": observation.full_name,
        "url": observation.url,
        "description": observation.description,
        "language": observation.language,
        "stars": observation.stars,
        "forks": observation.forks,
        "created_at": observation.created_at,
        "topics": list(observation.topics),
        "source_path": observation.source_path,
        "github_id": observation.github_id,
        "node_id": observation.node_id,
        "archived": observation.archived,
        "disabled": observation.disabled,
        "updated_at": observation.updated_at,
        "pushed_at": observation.pushed_at,
        "api_url": observation.api_url,
    }


def observation_from_ledger(raw: dict[str, Any]) -> RepoObservation:
    return RepoObservation(
        week=str(raw["week"]),
        source_bucket=str(raw.get("source_bucket") or "ledger"),
        owner=str(raw.get("owner") or ""),
        name=str(raw.get("name") or ""),
        full_name=str(raw["full_name"]),
        url=str(raw.get("url") or f"https://github.com/{raw['full_name']}"),
        description=raw.get("description"),
        language=raw.get("language"),
        stars=raw.get("stars") if isinstance(raw.get("stars"), int) else None,
        forks=raw.get("forks") if isinstance(raw.get("forks"), int) else None,
        created_at=raw.get("created_at"),
        topics=tuple(str(topic) for topic in raw.get("topics", [])),
        source_path=str(raw.get("source_path") or ""),
        github_id=str(raw["github_id"]) if raw.get("github_id") is not None else None,
        node_id=str(raw["node_id"]) if raw.get("node_id") is not None else None,
        archived=bool(raw.get("archived", False)),
        disabled=bool(raw.get("disabled", False)),
        updated_at=raw.get("updated_at"),
        pushed_at=raw.get("pushed_at"),
        api_url=raw.get("api_url"),
    )


def load_lifecycle_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": LIFECYCLE_SCHEMA_VERSION, "repositories": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != LIFECYCLE_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported repository lifecycle schema: {payload.get('schema_version')}"
        )
    if not isinstance(payload.get("repositories"), dict):
        raise ValueError("Repository lifecycle ledger repositories must be an object")
    return payload


def add_observation(history: RepositoryHistory, observation: RepoObservation) -> bool:
    identity = (observation.week, observation.source_path)
    if any((item.week, item.source_path) == identity for item in history.observations):
        return False
    if history.display_name != observation.full_name:
        history.prior_full_names.add(history.display_name)
        history.prior_slugs.add(history.slug)
    history.observations.append(observation)
    history.github_id = observation.github_id or history.github_id
    history.node_id = observation.node_id or history.node_id
    history.display_name = observation.full_name
    history.owner = observation.owner
    history.name = observation.name
    history.slug = repo_slug(observation.full_name)
    history.url = observation.url
    history.description = observation.description or history.description
    history.topics.update(observation.topics)
    if observation.language:
        history.languages.update([observation.language])
    return True


def history_from_ledger(key: str, raw: dict[str, Any]) -> RepositoryHistory | None:
    observations = [
        observation_from_ledger(item)
        for item in raw.get("observations", [])
        if isinstance(item, dict) and item.get("week") and item.get("full_name")
    ]
    if not observations:
        return None
    # Tie-break same-week observations by source_path, matching latest_observation
    # and lifecycle_ledger_payload()'s serialization order.
    latest = max(observations, key=lambda item: (item.week, item.source_path))
    history = RepositoryHistory(
        key=key,
        github_id=str(raw["github_id"]) if raw.get("github_id") is not None else latest.github_id,
        node_id=raw.get("node_id") or latest.node_id,
        display_name=str(raw.get("current_full_name") or latest.full_name),
        owner=latest.owner,
        name=latest.name,
        slug=str(raw.get("current_slug") or repo_slug(latest.full_name)),
        url=str(raw.get("last_successful_url") or latest.url),
        description=latest.description,
        lifecycle=dict(raw.get("lifecycle") or {}),
        prior_full_names=set(str(value) for value in raw.get("prior_full_names", [])),
        prior_slugs=set(str(value) for value in raw.get("prior_slugs", [])),
        qualified=bool(raw.get("qualified", False)),
    )
    for observation in observations:
        history.observations.append(observation)
        history.topics.update(observation.topics)
        if observation.language:
            history.languages.update([observation.language])
    return history


def apply_configured_renames(histories: dict[str, RepositoryHistory]) -> None:
    for source_key, source in list(histories.items()):
        if source.lifecycle.get("status") != "renamed":
            continue
        renamed_to = str(source.lifecycle.get("renamed_to") or "").strip()
        if not renamed_to:
            continue
        target = next(
            (
                history
                for history in histories.values()
                if normalize_full_name(history.display_name) == normalize_full_name(renamed_to)
            ),
            None,
        )
        if target is None:
            owner, name = split_full_name(renamed_to)
            target_key = repository_key(None, renamed_to)
            target = RepositoryHistory(
                key=target_key,
                github_id=None,
                node_id=None,
                display_name=renamed_to,
                owner=owner,
                name=name,
                slug=repo_slug(renamed_to),
                url=f"https://github.com/{renamed_to}",
                description=source.description,
            )
            histories[target_key] = target
        target.prior_full_names.update(source.prior_full_names | {source.display_name})
        target.prior_slugs.update(source.prior_slugs | {source.slug})
        target.qualified = target.qualified or source.qualified
        for observation in source.observations:
            if observation not in target.observations:
                target.observations.append(observation)
                target.topics.update(observation.topics)
                if observation.language:
                    target.languages.update([observation.language])
        histories.pop(source_key, None)


def consolidate_ledger_duplicate_identities(histories: dict[str, RepositoryHistory]) -> None:
    """Merge ledger-preloaded fallback (name:) histories into a stable-ID history sharing the
    same display_name.

    Identity backfill resolves a fallback observation's github_id at raw-week processing time,
    but a "name:"-keyed history already committed to the ledger under the same display_name
    (from before its github_id was known) is never visited by that per-observation logic, so it
    would otherwise persist as an orphaned duplicate that collides on slug with the resolved
    stable-ID history once both are eligible.
    """
    groups: dict[str, list[RepositoryHistory]] = {}
    for history in histories.values():
        groups.setdefault(normalize_full_name(history.display_name), []).append(history)
    for duplicates in groups.values():
        if len(duplicates) < 2:
            continue
        stable = [history for history in duplicates if not history.key.startswith("name:")]
        fallback = [history for history in duplicates if history.key.startswith("name:")]
        if len(stable) != 1 or not fallback:
            continue
        canonical = stable[0]
        previous_display_name = canonical.display_name
        previous_slug = canonical.slug
        for source in fallback:
            canonical.prior_full_names.update(source.prior_full_names)
            canonical.prior_slugs.update(source.prior_slugs)
            canonical.prior_full_names.add(source.display_name)
            canonical.prior_slugs.add(source.slug)
            canonical.qualified = canonical.qualified or source.qualified
            for observation in source.observations:
                identity = (observation.week, observation.source_path)
                if any(
                    (item.week, item.source_path) == identity for item in canonical.observations
                ):
                    continue
                canonical.observations.append(observation)
                canonical.topics.update(observation.topics)
                if observation.language:
                    canonical.languages.update([observation.language])
            histories.pop(source.key, None)
        canonical.prior_full_names.add(previous_display_name)
        canonical.prior_slugs.add(previous_slug)
        latest = canonical.latest_observation
        canonical.display_name = latest.full_name
        canonical.owner = latest.owner
        canonical.name = latest.name
        canonical.slug = repo_slug(latest.full_name)
        canonical.url = latest.url
        canonical.description = latest.description or canonical.description
        # The final identity must never also be listed as one of its own priors -
        # e.g. a merged source's own prior_full_names/prior_slugs can already contain
        # the value that ends up being the combined history's current name/slug.
        canonical.prior_full_names.discard(canonical.display_name)
        canonical.prior_slugs.discard(canonical.slug)


def load_repository_histories(
    root: Path,
    lifecycle: dict[str, Any] | None = None,
    ledger: dict[str, Any] | None = None,
    identity_backfill: dict[str, dict[str, Any]] | None = None,
) -> dict[str, RepositoryHistory]:
    identity_backfill = identity_backfill or {}
    histories: dict[str, RepositoryHistory] = {}
    for key, raw in (ledger or {}).get("repositories", {}).items():
        if isinstance(raw, dict) and (history := history_from_ledger(str(key), raw)):
            histories[str(key)] = history
    # Step 1.1: Build full_name -> current key reverse index to detect migrations across passes
    full_name_to_key: dict[str, str] = {
        normalize_full_name(history.display_name): history.key for history in histories.values()
    }
    current_keys: set[str] = set()
    for path in raw_week_files(root):
        payload = json.loads(path.read_text(encoding="utf-8"))
        week = str(payload.get("week") or path.stem)
        seen_this_week: set[tuple[str, str]] = set()
        for bucket in ("trending_repos", "new_repos"):
            for record in payload.get(bucket, []) or []:
                observation = observation_from_record(week, bucket, record, path, root)
                if observation is None:
                    continue
                if observation.github_id is None:
                    backfilled = identity_backfill.get(normalize_full_name(observation.full_name))
                    if (
                        backfilled
                        and backfilled.get("status") == "found"
                        and backfilled.get("github_id")
                    ):
                        observation = replace(
                            observation,
                            github_id=str(backfilled["github_id"]),
                            node_id=str(backfilled["node_id"])
                            if backfilled.get("node_id")
                            else observation.node_id,
                        )
                key = repository_key(observation.github_id, observation.full_name)
                legacy_key = f"name:{normalize_full_name(observation.full_name)}"
                if key != legacy_key and key not in histories and legacy_key in histories:
                    history = histories.pop(legacy_key)
                    history.key = key
                    history.github_id = observation.github_id
                    history.node_id = observation.node_id or history.node_id
                    histories[key] = history
                    # Step 1.2: Update reverse index when migration happens mid-pass
                    full_name_to_key[normalize_full_name(observation.full_name)] = key
                if (key, week) in seen_this_week:
                    continue
                seen_this_week.add((key, week))
                current_keys.add(key)
                history = histories.get(key)
                if history is None:
                    # Step 1.1: Check reverse index for a migrated history before minting a duplicate
                    canonical_key = full_name_to_key.get(normalize_full_name(observation.full_name))
                    if canonical_key is not None:
                        history = histories[canonical_key]
                        current_keys.add(canonical_key)
                    else:
                        history = RepositoryHistory(
                            key=key,
                            github_id=observation.github_id,
                            node_id=observation.node_id,
                            display_name=observation.full_name,
                            owner=observation.owner,
                            name=observation.name,
                            slug=repo_slug(observation.full_name),
                            url=observation.url,
                            description=observation.description,
                        )
                        histories[key] = history
                        full_name_to_key[normalize_full_name(observation.full_name)] = key
                observation_added = add_observation(history, observation)
                if observation.archived:
                    history.lifecycle.update(
                        {
                            "status": "archived",
                            "status_evidence": "github_archived_field",
                            "archived_at": observation.updated_at
                            or week_start_date(week).isoformat(),
                        }
                    )
                elif observation.disabled:
                    history.lifecycle.update(
                        {
                            "status": "disabled",
                            "status_evidence": "github_disabled_field",
                            "disabled_at": observation.updated_at
                            or week_start_date(week).isoformat(),
                        }
                    )
                elif (
                    observation_added
                    and history.lifecycle.get("status") == "deleted"
                    and (
                        not history.lifecycle.get("deletion_confirmed_at")
                        or week_start_date(observation.week)
                        > date.fromisoformat(history.lifecycle["deletion_confirmed_at"])
                    )
                ):
                    history.lifecycle = {
                        "status": "active",
                        "status_evidence": "github_observation",
                    }
    for configured_name, override in (lifecycle or {}).items():
        if not isinstance(override, dict):
            continue
        normalized = normalize_full_name(configured_name)
        for history in histories.values():
            known_names = {normalize_full_name(history.display_name)} | {
                normalize_full_name(name) for name in history.prior_full_names
            }
            if normalized in known_names:
                history.lifecycle.update(override)
                history.lifecycle.setdefault("status_evidence", "reviewed_config_override")
    for history in histories.values():
        if history.key in current_keys and not history.lifecycle:
            history.lifecycle = {"status": "active", "status_evidence": "github_observation"}
    # A ledger-preloaded fallback (name:) history is only visited by the reverse-index
    # migration above when a raw-week observation drives it; a stable-ID sibling whose
    # *final* display_name (settled after all observations are applied) matches a
    # fallback entry that received no new observations this pass would otherwise persist
    # as an orphaned duplicate, so this runs last, against final state.
    consolidate_ledger_duplicate_identities(histories)
    apply_configured_renames(histories)
    return histories


def eligible_repositories(
    histories: dict[str, RepositoryHistory], minimum_weeks: int
) -> list[RepositoryHistory]:
    return sorted(
        [
            history
            for history in histories.values()
            if history.qualified or len(history.distinct_weeks) >= minimum_weeks
        ],
        key=lambda history: (-len(history.distinct_weeks), history.display_name.lower()),
    )


def attach_related_repositories(
    histories: dict[str, RepositoryHistory], eligible: list[RepositoryHistory]
) -> None:
    eligible_keys = {history.key for history in eligible}
    weeks: dict[str, list[str]] = defaultdict(list)
    for key, history in sorted(histories.items()):
        for week in sorted(history.distinct_weeks):
            weeks[week].append(key)

    related: dict[str, Counter[str]] = {key: Counter() for key in eligible_keys}
    for keys in weeks.values():
        sorted_keys = sorted(keys)
        present_eligible = [key for key in sorted_keys if key in eligible_keys]
        for source in present_eligible:
            for target in sorted_keys:
                if source != target and target in eligible_keys:
                    related[source][target] += 1

    topic_sets = {key: set(history.topics) for key, history in histories.items()}
    for source in sorted(eligible_keys):
        source_topics = topic_sets[source]
        if not source_topics:
            continue
        for target, target_topics in sorted(topic_sets.items()):
            if source == target or target not in eligible_keys:
                continue
            overlap = source_topics.intersection(target_topics)
            if overlap:
                related[source][target] += min(len(overlap), 4)

    for history in eligible:
        entries: list[dict[str, Any]] = []
        ordered_related = sorted(
            related[history.key].items(),
            key=lambda item: (-item[1], histories[item[0]].display_name.lower()),
        )
        for target, score in ordered_related[:8]:
            target_history = histories[target]
            shared_weeks = sorted(
                history.distinct_weeks.intersection(target_history.distinct_weeks)
            )
            shared_topics = sorted(set(history.topics).intersection(target_history.topics))[:6]
            entries.append(
                {
                    "full_name": target_history.display_name,
                    "slug": target_history.slug,
                    "url": target_history.url,
                    "score": score,
                    "shared_weeks": shared_weeks[:6],
                    "shared_topics": shared_topics,
                }
            )
        history.related_repos = entries


def page_params(
    history: RepositoryHistory,
    config: dict[str, Any],
    rename_aliases: dict[str, list[str]],
    tag_display_names: dict[str, str],
    promoted_topic_aliases: dict[str, dict[str, str]],
) -> dict[str, Any]:
    latest = history.latest_observation
    top_tags = [
        {
            "slug": taxonomy_registry.slugify(topic),
            "display_name": tag_display_names.get(taxonomy_registry.slugify(topic), topic),
        }
        for topic, _count in sorted(
            history.topics.items(),
            key=lambda item: (-item[1], taxonomy_registry.slugify(item[0])),
        )[:12]
    ]
    lifecycle_status = history.lifecycle.get("status") or (
        "archived" if latest.archived else "active"
    )
    retained_until = history.lifecycle.get("retained_until")
    topic_links_by_slug: dict[str, dict[str, str]] = {}
    for raw_topic in history.topics:
        mapped = promoted_topic_aliases.get(taxonomy_registry.slugify(raw_topic))
        if mapped:
            topic_links_by_slug[mapped["slug"]] = mapped
    title = f"{history.display_name} repository trend history"
    description = (
        f"Evergreen Claracle Observatory page for {history.display_name}: "
        f"{len(history.distinct_weeks)} weekly appearances, stars, velocity, topics, and related repos."
    )
    params: dict[str, Any] = {
        "title": title,
        "description": description,
        "date": week_start_date(history.last_seen_week).isoformat(),
        "draft": False,
        "layout": "repo",
        "generated_by": GENERATED_BY,
        "repo_owner": history.owner,
        "repo_name": history.name,
        "repo_full_name": history.display_name,
        "repo_url": history.url,
        "repo_slug": history.slug,
        "repo_description": history.description or "",
        "repo_language": history.languages.most_common(1)[0][0] if history.languages else "",
        "tags": [tag["display_name"] for tag in top_tags],
        "first_seen_week": history.first_seen_week,
        "last_seen_week": history.last_seen_week,
        "as_of_week": history.last_seen_week,
        "source_paths": sorted({observation.source_path for observation in history.observations}),
        "distinct_weekly_issues": len(history.distinct_weeks),
        "recurrence_threshold": {
            "operator": config["operator"],
            "distinct_weekly_issues": config["threshold"],
            "minimum_weeks": config["minimum_weeks"],
        },
        "star_history": history.star_history,
        "weekly_appearances": [
            {"week": week, "url": weekly_permalink(week)} for week in sorted(history.distinct_weeks)
        ],
        "tag_links": [
            {"name": tag["display_name"], "url": f"/tags/{tag['slug']}/"} for tag in top_tags
        ],
        "topic_links": [topic_links_by_slug[slug] for slug in sorted(topic_links_by_slug)],
        "related_repos": history.related_repos,
        "lifecycle": {
            "status": lifecycle_status,
            "as_of_week": history.last_seen_week,
            "retention_years": config["retention_years"],
            "retained_until": retained_until,
            "renamed_from": sorted(history.prior_full_names)[-1]
            if history.prior_full_names
            else None,
            "prior_full_names": sorted(history.prior_full_names),
            "renamed_to": history.lifecycle.get("renamed_to"),
            "status_evidence": history.lifecycle.get("status_evidence"),
            "archived_at": history.lifecycle.get("archived_at"),
            "disabled_at": history.lifecycle.get("disabled_at"),
            "deletion_confirmed_at": history.lifecycle.get("deletion_confirmed_at"),
            "note": history.lifecycle.get("note", ""),
        },
        "methodology_url": "/methodology/",
    }
    aliases = rename_aliases.get(history.key, [])
    if aliases:
        params["aliases"] = aliases
    return params


def markdown_body(params: dict[str, Any]) -> str:
    name = params["repo_full_name"]
    status = params["lifecycle"]["status"]
    lines = [
        f"{name} has appeared in {params['distinct_weekly_issues']} Claracle weekly issues.",
        "",
    ]
    if status == "archived":
        lines.extend(
            [
                f"Lifecycle note: this repository is marked archived as of {params['as_of_week']}.",
                "",
            ]
        )
    if status == "deleted":
        lines.extend(
            [
                "Lifecycle note: this repository is marked deleted or inaccessible; current availability is not claimed.",
                f"This page is retained until at least {params['lifecycle']['retained_until']} based on the last seen week {params['last_seen_week']}.",
                "",
            ]
        )
    lines.extend(
        [
            "See the generated Observatory sections below for growth history, derived star velocity, weekly appearances, related repositories, and provenance.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_yaml_page(path: Path, params: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = yaml.safe_dump(params, sort_keys=False, allow_unicode=True, width=120)
    path.write_text(f"---\n{frontmatter}---\n\n{markdown_body(params)}", encoding="utf-8")


def rename_aliases(histories: dict[str, RepositoryHistory]) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = defaultdict(list)
    for history in histories.values():
        aliases[history.key].extend(f"/repo/{slug}/" for slug in sorted(history.prior_slugs))
    return aliases


def load_promoted_topic_aliases(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    terms = json.loads(path.read_text(encoding="utf-8")).get("terms", {})
    aliases: dict[str, dict[str, str]] = {}
    for slug, raw in terms.items():
        if not isinstance(raw, dict) or not raw.get("promoted"):
            continue
        canonical_slug = str(raw.get("slug") or slug)
        link = {
            "name": str(raw.get("display_name") or canonical_slug),
            "slug": canonical_slug,
            "url": f"/topics/{canonical_slug}/",
        }
        for value in [canonical_slug, raw.get("display_name"), *raw.get("aliases", [])]:
            if isinstance(value, str):
                aliases[taxonomy_registry.slugify(value)] = link
    return aliases


def lifecycle_ledger_payload(histories: dict[str, RepositoryHistory]) -> dict[str, Any]:
    repositories: dict[str, Any] = {}
    for key, history in sorted(histories.items()):
        repositories[key] = {
            "github_id": history.github_id,
            "node_id": history.node_id,
            "current_full_name": history.display_name,
            "current_slug": history.slug,
            "prior_full_names": sorted(history.prior_full_names),
            "prior_slugs": sorted(history.prior_slugs),
            "first_seen_week": history.first_seen_week,
            "last_seen_week": history.last_seen_week,
            "last_successful_url": history.url,
            "qualified": history.qualified,
            "lifecycle": history.lifecycle,
            "observations": [
                observation_to_dict(item)
                for item in sorted(
                    history.observations, key=lambda item: (item.week, item.source_path)
                )
            ],
        }
    return {"schema_version": LIFECYCLE_SCHEMA_VERSION, "repositories": repositories}


def existing_repository_identities(root: Path) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    page_identities: set[tuple[str, str]] = set()
    for path in sorted((root / "content" / "repo").glob("*/index.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        params = yaml.safe_load(text.split("---", 2)[1])
        if not isinstance(params, dict) or params.get("generated_by") != GENERATED_BY:
            continue
        page_identities.add((str(params.get("repo_full_name")), str(params.get("repo_slug"))))

    derived_path = root / "data" / "derived" / "observatory" / "repositories.json"
    derived = json.loads(derived_path.read_text(encoding="utf-8"))
    if not isinstance(derived, list):
        raise ValueError("Derived repository data must be an array")
    derived_identities = {
        (str(item.get("repo_full_name")), str(item.get("repo_slug")))
        for item in derived
        if isinstance(item, dict)
    }
    return page_identities, derived_identities


def write_json_atomically(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            json.dump(payload, temporary, indent=2, sort_keys=True)
            temporary.write("\n")
            temporary.flush()
            temporary_path = Path(temporary.name)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def seed_lifecycle(
    root: Path, config_path: Path | None = None, *, as_of: date | None = None
) -> dict[str, int]:
    config = load_config(root, config_path)
    if config["enabled"] and config_path is None:
        raise ValueError("Lifecycle seed requires repo_pages.enabled = false")
    effective_as_of = as_of or date.today()
    identity_backfill = load_identity_backfill(config["identity_backfill_path"])
    effective_lifecycle = merge_identity_backfill_overrides(config["lifecycle"], identity_backfill)
    validate_lifecycle_overrides(
        effective_lifecycle,
        as_of=effective_as_of,
        retention_years=config["retention_years"],
    )
    ledger = load_lifecycle_ledger(config["ledger_path"])
    histories = load_repository_histories(root, effective_lifecycle, ledger, identity_backfill)
    for history in histories.values():
        if len(history.distinct_weeks) >= config["minimum_weeks"]:
            history.qualified = True
        if history.lifecycle.get("status") == "deleted":
            confirmed, retained_until = deletion_retention(
                history.lifecycle,
                as_of=effective_as_of,
                retention_years=config["retention_years"],
                identity=history.display_name,
            )
            history.lifecycle["deletion_confirmed_at"] = confirmed.isoformat()
            history.lifecycle["retained_until"] = retained_until.isoformat()

    qualified_identities = {
        (history.display_name, history.slug) for history in histories.values() if history.qualified
    }
    page_identities, derived_identities = existing_repository_identities(root)
    if qualified_identities != page_identities or qualified_identities != derived_identities:
        raise ValueError(
            "Lifecycle seed parity mismatch: "
            f"qualified={len(qualified_identities)}, pages={len(page_identities)}, "
            f"derived={len(derived_identities)}"
        )

    write_json_atomically(config["ledger_path"], lifecycle_ledger_payload(histories))
    counts = {
        "fallback_histories": sum(key.startswith("name:") for key in histories),
        "stable_id_histories": sum(not key.startswith("name:") for key in histories),
        "qualified_histories": len(qualified_identities),
        "existing_pages": len(page_identities),
        "mismatches": 0,
    }
    print(
        "Seeded lifecycle ledger: " + ", ".join(f"{name}={value}" for name, value in counts.items())
    )
    return counts


def reconcile_lifecycle(
    histories: dict[str, RepositoryHistory], config: dict[str, Any], as_of: date
) -> list[RepositoryHistory]:
    expired: list[RepositoryHistory] = []
    deletion_dates = {
        history.key: deletion_retention(
            history.lifecycle,
            as_of=as_of,
            retention_years=config["retention_years"],
            identity=history.display_name,
        )
        for history in histories.values()
        if history.lifecycle.get("status") == "deleted"
    }
    for history in histories.values():
        if len(history.distinct_weeks) >= config["minimum_weeks"]:
            history.qualified = True
        if history.lifecycle.get("status") != "deleted":
            continue
        confirmed, retained_until = deletion_dates[history.key]
        history.lifecycle["deletion_confirmed_at"] = confirmed.isoformat()
        history.lifecycle["retained_until"] = retained_until.isoformat()
        if as_of > retained_until:
            expired.append(history)
    for history in expired:
        histories.pop(history.key)
    return expired


def repository_index_content(generated_count: int, config: dict[str, Any]) -> str:
    params = {
        "title": "Repository Observatory",
        "description": "Evergreen Claracle pages for recurring GitHub repositories tracked across weekly issues.",
        "generated_by": GENERATED_BY,
        "repo_pages_generated": generated_count,
        "recurrence_threshold": {
            "operator": config["operator"],
            "distinct_weekly_issues": config["threshold"],
            "minimum_weeks": config["minimum_weeks"],
        },
    }
    frontmatter = yaml.safe_dump(params, sort_keys=False, width=120)
    return (
        f"---\n{frontmatter}---\n\n"
        "Claracle generates repository pages only after a project appears in more than three distinct weekly issues.\n"
    )


def write_repository_pages(
    root: Path,
    histories: dict[str, RepositoryHistory],
    config: dict[str, Any],
    *,
    check: bool = False,
    expired: list[RepositoryHistory] | None = None,
) -> list[Path]:
    if check:
        tags_path = root / "data" / "taxonomy" / "tags.json"
    else:
        _topics_path, tags_path = taxonomy_registry.update_taxonomy_registries(
            root=root, config_path=root / DEFAULT_CONFIG
        )
    tag_display_names = taxonomy_registry.load_display_names(tags_path)
    promoted_topic_aliases = load_promoted_topic_aliases(config["topics_registry_path"])
    eligible = eligible_repositories(histories, config["minimum_weeks"])
    attach_related_repositories(histories, eligible)
    aliases = rename_aliases(histories)
    content_repo = root / "content" / "repo"
    expected: dict[Path, str] = {
        content_repo / "_index.md": repository_index_content(len(eligible), config)
    }
    written: list[Path] = []
    derived: list[dict[str, Any]] = []
    # Step 1.3: Track seen slugs to detect collisions
    seen_slugs: dict[str, str] = {}
    for history in eligible:
        # Step 1.3: Raise if two different history keys resolve to the same slug (collision guard)
        if history.slug in seen_slugs and seen_slugs[history.slug] != history.key:
            raise ValueError(
                f"Slug collision detected: both history key {seen_slugs[history.slug]!r} "
                f"and {history.key!r} produce slug {history.slug!r}"
            )
        seen_slugs[history.slug] = history.key
        params = page_params(history, config, aliases, tag_display_names, promoted_topic_aliases)
        output_path = content_repo / history.slug / "index.md"
        frontmatter = yaml.safe_dump(params, sort_keys=False, allow_unicode=True, width=120)
        expected[output_path] = f"---\n{frontmatter}---\n\n{markdown_body(params)}"
        written.append(output_path)
        derived.append(params)
    derived_path = root / "data" / "derived" / "observatory" / "repositories.json"
    ledger_path = config["ledger_path"]
    expected[derived_path] = json.dumps(derived, indent=2, sort_keys=True) + "\n"
    expected[ledger_path] = (
        json.dumps(lifecycle_ledger_payload(histories), indent=2, sort_keys=True) + "\n"
    )
    stale = [
        path
        for path, content in expected.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    obsolete_pages = [
        content_repo / slug / "index.md"
        for history in histories.values()
        for slug in history.prior_slugs
        if (content_repo / slug / "index.md").exists()
    ]
    expired_pages = [
        content_repo / history.slug / "index.md"
        for history in expired or []
        if (content_repo / history.slug / "index.md").exists()
    ]
    if check:
        return sorted(set(stale + obsolete_pages + expired_pages))
    for path, content in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    for obsolete_page in obsolete_pages:
        if f"generated_by: {GENERATED_BY}" in obsolete_page.read_text(encoding="utf-8"):
            obsolete_page.unlink()
    for history in expired or []:
        expired_page = content_repo / history.slug / "index.md"
        if expired_page.exists() and f"generated_by: {GENERATED_BY}" in expired_page.read_text(
            encoding="utf-8"
        ):
            expired_page.unlink()
            print(
                f"Removed expired repository tombstone {history.display_name}: "
                f"retention ended {history.lifecycle['retained_until']}"
            )
    return written


def generate(
    root: Path,
    config_path: Path | None = None,
    *,
    check: bool = False,
    as_of: date | None = None,
) -> list[Path]:
    config = load_config(root, config_path)
    if not config["enabled"]:
        print(
            "repository-page-decision disabled; "
            "no repository pages created or durable pages deleted"
        )
        return []
    effective_as_of = as_of or date.today()
    identity_backfill = load_identity_backfill(config["identity_backfill_path"])
    effective_lifecycle = merge_identity_backfill_overrides(config["lifecycle"], identity_backfill)
    validate_lifecycle_overrides(
        effective_lifecycle,
        as_of=effective_as_of,
        retention_years=config["retention_years"],
    )
    ledger = load_lifecycle_ledger(config["ledger_path"])
    histories = load_repository_histories(root, effective_lifecycle, ledger, identity_backfill)
    expired = reconcile_lifecycle(histories, config, effective_as_of)
    return write_repository_pages(root, histories, config, check=check, expired=expired)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, default=None)
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument(
        "--check", action="store_true", help="Fail when generated repository files are stale."
    )
    operation.add_argument(
        "--seed-lifecycle",
        action="store_true",
        help="Validate repository parity and atomically seed only the lifecycle ledger.",
    )
    parser.add_argument("--as-of", type=date.fromisoformat, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.seed_lifecycle:
        seed_lifecycle(args.root.resolve(), args.config, as_of=args.as_of)
        return 0
    written = generate(args.root.resolve(), args.config, check=args.check, as_of=args.as_of)
    if args.check and written:
        for path in written:
            print(f"Out of date: {path.relative_to(args.root.resolve())}")
        return 1
    print(f"Generated {len(written)} repository pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

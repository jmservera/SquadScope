#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urljoin, urlparse


AUTH_HEADER = "x-podcaster-api-key"
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_PODCAST_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "podcast.json"
REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_ARTICLE_CONTENT_CHARS = 50_000


class PodcasterHandoffError(RuntimeError):
    pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Notify Podcaster after a SquadScope weekly article is published.")
    parser.add_argument("--week", required=True, help="ISO week slug, e.g. 2026-W23.")
    parser.add_argument("--article-url", required=True, help="Published SquadScope article URL.")
    parser.add_argument("--article-path", required=True, help="Published SquadScope article content path.")
    parser.add_argument("--publish-run-id", required=True, help="GitHub Actions run ID that published the article.")
    parser.add_argument("--publish-mode", default="normal", help="Publish mode; only normal is eligible for Podcaster handoff.")
    parser.add_argument("--manifest", type=Path, help="Optional publish manifest used for article hash/source artifact metadata.")
    parser.add_argument("--podcaster-dry-run", action="store_true", help="Ask Podcaster to validate without generating an episode; intended only for the manual smoke workflow.")
    parser.add_argument("--podcast-config", type=Path, default=None, help="Path to podcast config JSON (default: config/podcast.json relative to repo root).")
    parser.add_argument("--endpoint", default=os.environ.get("PODCASTER_ENDPOINT", ""))
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    return parser.parse_args(argv)


WEEKLY_CONTENT_PREFIX = "content/weekly/"


def normalize_page_path(page_path: str) -> str:
    """Reduce an absolute Actions page path to its repo-relative form.

    The generate job emits page_path as an absolute runner path on GitHub
    Actions (see scripts/generate_content.py); mirror the workflow's
    GITHUB_WORKSPACE normalization by reducing any absolute path to the
    repo-relative segment beginning at content/weekly/.
    """
    path = page_path.strip().replace("\\", "/")
    index = path.find(WEEKLY_CONTENT_PREFIX)
    if index != -1:
        path = path[index:]
    return path.lstrip("/")


def article_url_from_page_path(base_url: str, page_path: str) -> str:
    base = base_url.rstrip("/") + "/"
    path = normalize_page_path(page_path)
    if not path.startswith(WEEKLY_CONTENT_PREFIX) or not path.endswith(".md"):
        raise PodcasterHandoffError(f"Cannot derive weekly article URL from page path: {page_path}")
    slug = path.removeprefix(WEEKLY_CONTENT_PREFIX).removesuffix(".md").lower()
    return urljoin(base, f"weekly/{slug}/")


def validate_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise PodcasterHandoffError("PODCASTER_ENDPOINT must be an absolute HTTP(S) URL.")
    if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise PodcasterHandoffError(
            "PODCASTER_ENDPOINT may use HTTP only for localhost or loopback addresses (127.0.0.1, ::1)."
        )


def _load_manifest(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        raise PodcasterHandoffError(
            f"Publish manifest path was provided but does not exist: {path}"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PodcasterHandoffError(f"Publish manifest could not be read: {path}") from exc
    if not isinstance(payload, dict):
        raise PodcasterHandoffError(f"Publish manifest must be a JSON object: {path}")
    return payload


def _load_podcast_config(path: Path | None) -> dict[str, Any]:
    """Load the podcast config file containing podcast_config and script_directions."""
    config_path = path if path is not None else DEFAULT_PODCAST_CONFIG_PATH
    if not config_path.exists():
        return {}
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PodcasterHandoffError(f"Podcast config could not be read: {config_path}") from exc
    if not isinstance(payload, dict):
        raise PodcasterHandoffError(f"Podcast config must be a JSON object: {config_path}")
    return payload


def _source_artifact_refs(manifest: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for artifact in manifest.get("source_artifacts", []):
        if not isinstance(artifact, dict):
            continue
        ref: dict[str, str] = {}
        for key in ("role", "path", "sha256", "generated_at"):
            value = artifact.get(key)
            if isinstance(value, str) and value:
                ref[key] = value
        freshness = artifact.get("freshness")
        if isinstance(freshness, dict) and isinstance(freshness.get("status"), str):
            ref["freshness_status"] = freshness["status"]
        for key in ("url", "artifact_url"):
            value = artifact.get(key)
            if isinstance(value, str) and value.startswith(("https://", "http://localhost:", "http://127.0.0.1:")):
                ref[key] = value
        if ref:
            refs.append(ref)
    return refs


def _extract_title(content: str) -> str | None:
    """Extract article title from YAML front matter or first # heading."""
    # Try YAML front matter first
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            frontmatter = content[3:end]
            match = re.search(r"^title:\s*(.+)$", frontmatter, re.MULTILINE)
            if match:
                title = match.group(1).strip().strip("\"'")
                if title:
                    return title
    # Fall back to first # heading
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def _extract_frontmatter_field(content: str, field_name: str) -> str | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    frontmatter = content[3:end]
    match = re.search(rf"^{re.escape(field_name)}:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip().strip("\"'")
    return value or None


def _render_template_value(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return {key: _render_template_value(item, context) for key, item in value.items()}
    if isinstance(value, list):
        return [_render_template_value(item, context) for item in value]
    if not isinstance(value, str):
        return value
    exact_match = re.fullmatch(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", value)
    if exact_match:
        key = exact_match.group(1)
        if key in context:
            return context[key]
    try:
        return value.format(**context)
    except KeyError as exc:
        missing = exc.args[0]
        raise PodcasterHandoffError(f"spotify_publish template references unknown field: {missing}") from exc


def _resolve_spotify_publish(config: dict[str, Any], *, week: str, article_title: str | None, article_summary: str | None) -> dict[str, Any]:
    match = re.fullmatch(r"(?P<year>\d{4})-W(?P<week>\d{1,2})", week)
    if not match:
        raise PodcasterHandoffError(f"Week must use YYYY-WNN format for spotify_publish templating: {week}")
    context: dict[str, Any] = {
        "year": int(match.group("year")),
        "week": int(match.group("week")),
        "article_title": article_title or "",
        "article_summary": article_summary or "",
    }
    return _render_template_value(config, context)


def _read_article_content(article_path: str, repo_root: Path = REPO_ROOT) -> tuple[str | None, str | None, str | None]:
    """Read article file content and extract title.

    Returns (content, title, summary). Content is truncated to MAX_ARTICLE_CONTENT_CHARS.
    Returns (None, None, None) if the file does not exist.
    Raises PodcasterHandoffError if the file exists but cannot be read, or if
    the resolved path escapes the repo root (path traversal prevention).
    """
    resolved = (repo_root / article_path).resolve()
    # Prevent path traversal — resolved path must stay within repo_root.
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        raise PodcasterHandoffError(
            f"article_path resolves outside the repository root: {article_path}"
        )
    if not resolved.exists():
        return None, None, None
    try:
        content = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise PodcasterHandoffError(
            f"Article file exists but could not be read: {resolved} ({exc})"
        )
    if not content.strip():
        return None, None, None
    title = _extract_frontmatter_field(content, "title") or _extract_title(content)
    summary = _extract_frontmatter_field(content, "summary")
    if len(content) > MAX_ARTICLE_CONTENT_CHARS:
        content = content[:MAX_ARTICLE_CONTENT_CHARS]
    return content, title, summary


def _manifest_allows_handoff(manifest: dict[str, Any], *, week: str, publish_mode: str) -> bool:
    if not manifest:
        return True
    analysis = manifest.get("analysis")
    promotion = manifest.get("promotion")
    return (
        manifest.get("week") == week
        and manifest.get("run_mode") == "normal"
        and publish_mode == "normal"
        and isinstance(analysis, dict)
        and analysis.get("ai_status") == "ai"
        and isinstance(promotion, dict)
        and promotion.get("eligible") is True
        and promotion.get("decision") == "promote"
    )


def build_payload(
    *,
    week: str,
    article_url: str,
    article_path: str,
    publish_run_id: str,
    publish_mode: str = "normal",
    manifest_path: Path | None = None,
    podcast_config_path: Path | None = None,
    podcaster_dry_run: bool = False,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    if not _manifest_allows_handoff(manifest, week=week, publish_mode=publish_mode):
        raise PodcasterHandoffError("Publish manifest is not eligible for Podcaster handoff.")
    normalized_path = normalize_page_path(article_path)
    payload: dict[str, Any] = {
        "week": week,
        "article_url": article_url,
        "article_path": normalized_path,
        "publish_run_id": publish_run_id,
        "publish_mode": publish_mode,
    }

    # Read article content and extract title
    root = repo_root if repo_root is not None else REPO_ROOT
    content, title, summary = _read_article_content(normalized_path, repo_root=root)
    if content:
        payload["article_content"] = content
    if title:
        payload["article_title"] = title
    if summary:
        payload["article_summary"] = summary
    article_sha = (
        manifest.get("candidate", {}).get("summary_sha256")
        if isinstance(manifest.get("candidate"), dict)
        else None
    )
    if isinstance(article_sha, str) and len(article_sha) == 64 and article_sha.lower() == article_sha:
        payload["article_sha256"] = article_sha
    source_refs = _source_artifact_refs(manifest)
    if source_refs:
        payload["source_artifacts"] = source_refs

    podcast_cfg = _load_podcast_config(podcast_config_path)
    if "podcast_config" in podcast_cfg:
        val = podcast_cfg["podcast_config"]
        if not isinstance(val, dict):
            raise PodcasterHandoffError("podcast_config must be a JSON object")
        payload["podcast_config"] = val
    if "script_directions" in podcast_cfg:
        val = podcast_cfg["script_directions"]
        if not isinstance(val, dict):
            raise PodcasterHandoffError("script_directions must be a JSON object")
        payload["script_directions"] = val
    if "spotify_publish" in podcast_cfg:
        val = podcast_cfg["spotify_publish"]
        if not isinstance(val, dict):
            raise PodcasterHandoffError("spotify_publish must be a JSON object")
        payload["spotify_publish"] = _resolve_spotify_publish(
            val,
            week=week,
            article_title=title,
            article_summary=summary,
        )

    if podcaster_dry_run:
        payload["dry_run"] = True
    return payload


SUCCESS_RESPONSE_STATUSES = {"accepted", "dry_run"}


def validate_response(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PodcasterHandoffError("Podcaster response must be a JSON object.")
    status = payload.get("status")
    errors = payload.get("errors", [])
    if status not in SUCCESS_RESPONSE_STATUSES:
        raise PodcasterHandoffError(
            f"Podcaster response status was not a known success status "
            f"(expected one of {sorted(SUCCESS_RESPONSE_STATUSES)}): {status!r}."
        )
    if isinstance(errors, list) and errors:
        raise PodcasterHandoffError("Podcaster response contained errors.")
    if errors not in ([], None) and not isinstance(errors, list):
        raise PodcasterHandoffError("Podcaster response errors field must be a list when present.")
    if not isinstance(payload.get("job_id"), str) or not payload["job_id"].strip():
        raise PodcasterHandoffError("Podcaster response is missing job_id.")
    return payload


def post_handoff(endpoint: str, api_key: str, payload: dict[str, Any], *, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict[str, Any]:
    validate_endpoint(endpoint)
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    req = request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            AUTH_HEADER: api_key,
            "User-Agent": "SquadScope-Podcaster-Handoff/1.0",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:  # nosec B310
            status_code = getattr(response, "status", response.getcode())
            response_body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        raise PodcasterHandoffError(f"Podcaster handoff failed with HTTP {exc.code}.") from exc
    except error.URLError as exc:
        raise PodcasterHandoffError(f"Podcaster handoff failed: {exc.reason}") from exc

    if status_code < 200 or status_code >= 300:
        raise PodcasterHandoffError(f"Podcaster handoff failed with HTTP {status_code}.")
    try:
        response_payload = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise PodcasterHandoffError("Podcaster response was not valid JSON.") from exc
    return validate_response(response_payload)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    endpoint = args.endpoint.strip()
    api_key = os.environ.get("PODCASTER_API_KEY", "").strip()
    if not endpoint or not api_key:
        print("::notice::Podcaster handoff skipped because PODCASTER_ENDPOINT and PODCASTER_API_KEY are not both configured.")
        return 0

    if args.publish_mode != "normal":
        print(f"::notice::Podcaster handoff skipped for publish mode {args.publish_mode}.")
        return 0

    try:
        payload = build_payload(
            week=args.week,
            article_url=args.article_url,
            article_path=args.article_path,
            publish_run_id=args.publish_run_id,
            publish_mode=args.publish_mode,
            manifest_path=args.manifest,
            podcast_config_path=args.podcast_config,
            podcaster_dry_run=args.podcaster_dry_run,
        )
        post_handoff(endpoint, api_key, payload, timeout=args.timeout)
    except PodcasterHandoffError as exc:
        print(f"::warning::{exc}")
        return 1
    print("::notice::Podcaster handoff accepted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

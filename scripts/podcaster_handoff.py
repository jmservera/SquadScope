#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urljoin, urlparse


AUTH_HEADER = "x-podcaster-api-key"
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_PODCAST_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "podcast.json"
REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_ARTICLE_CONTENT_CHARS = 50_000
MAX_SPOTIFY_TITLE_CHARS = 200
MAX_SPOTIFY_DESCRIPTION_CHARS = 4_000
MAX_MONTH_SYNTHESIS_WORDS = 300
MAX_YEARLY_NARRATIVE_WORDS = 500
_VOID_HTML_TAGS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
)


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
    parser.add_argument("--breaking-news", default=None, help="Optional last-moment news or important information to include in this podcast episode.")
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


def _source_artifact_refs(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    def _string_list(value: Any) -> list[str] | None:
        if not isinstance(value, list):
            return None
        filtered = [item for item in value if isinstance(item, str) and item]
        return filtered or None

    refs: list[dict[str, Any]] = []
    for artifact in manifest.get("source_artifacts", []):
        if not isinstance(artifact, dict):
            continue
        ref: dict[str, Any] = {}
        for key in (
            "role",
            "path",
            "name",
            "sha256",
            "artifact_checksum",
            "week",
            "crawled_at",
            "generated_at",
            "source_status",
            "source_config_checksum",
            "schema_checksum",
        ):
            value = artifact.get(key)
            if isinstance(value, str) and value:
                ref[key] = value
        exists = artifact.get("exists")
        if isinstance(exists, bool):
            ref["exists"] = exists
        size_bytes = artifact.get("size_bytes")
        if isinstance(size_bytes, int) and not isinstance(size_bytes, bool) and size_bytes >= 0:
            ref["size_bytes"] = size_bytes
        for key in ("url", "href", "uri"):
            value = artifact.get(key)
            if isinstance(value, str) and value.startswith(("https://", "http://localhost:", "http://127.0.0.1:")):
                ref[key] = value
        artifact_url = artifact.get("artifact_url")
        if (
            "url" not in ref
            and isinstance(artifact_url, str)
            and artifact_url.startswith(("https://", "http://localhost:", "http://127.0.0.1:"))
        ):
            ref["url"] = artifact_url
        for key in (
            "freshness",
            "provenance",
            "same_day_reuse",
            "source_artifact_provenance",
            "source_reuse_summary",
        ):
            value = artifact.get(key)
            if isinstance(value, dict):
                ref[key] = value
        for key in ("sources_requested", "sources_succeeded", "sources_failed"):
            filtered = _string_list(artifact.get(key))
            if filtered is not None:
                ref[key] = filtered
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
    except (ValueError, IndexError) as exc:
        raise PodcasterHandoffError(f"spotify_publish template has invalid format syntax: {value!r}") from exc


class _HTMLTruncator(HTMLParser):
    def __init__(self, max_length: int) -> None:
        super().__init__(convert_charrefs=False)
        self.max_length = max_length
        self.parts: list[str] = []
        self.open_tags: list[str] = []
        self.current_length = 0
        self.truncated = False

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        self._append_tag(self.get_starttag_text(), tag, push=True)

    def handle_startendtag(self, tag: str, attrs) -> None:  # type: ignore[override]
        self._append_tag(self.get_starttag_text(), tag, push=False)

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        normalized = tag.lower()
        if self.truncated or normalized not in self.open_tags:
            return

        closings: list[str] = []
        while self.open_tags:
            open_tag = self.open_tags.pop()
            closings.append(f"</{open_tag}>")
            if open_tag == normalized:
                break

        for closing in closings:
            self._append(closing)

    def handle_data(self, data: str) -> None:
        self._append_text(data)

    def handle_entityref(self, name: str) -> None:
        self._append_atomic(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._append_atomic(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self._append_atomic(f"<!--{data}-->")

    def _append_tag(self, raw_tag: str | None, tag: str, *, push: bool) -> None:
        if self.truncated or not raw_tag:
            return

        normalized = tag.lower()
        budget = self._closing_budget(extra_tag=normalized if push else None)
        if self.current_length + len(raw_tag) + budget > self.max_length:
            self.truncated = True
            return

        self._append(raw_tag)
        if push and normalized not in _VOID_HTML_TAGS:
            self.open_tags.append(normalized)

    def _append_atomic(self, token: str) -> None:
        if self.truncated or not token:
            return
        available = self.max_length - self.current_length - self._closing_budget()
        if len(token) > available:
            self.truncated = True
            return
        self._append(token)

    def _append_text(self, text: str) -> None:
        if self.truncated or not text:
            return

        available = self.max_length - self.current_length - self._closing_budget()
        if available <= 0:
            self.truncated = True
            return

        piece = text[:available]
        if piece:
            self._append(piece)
        if len(piece) < len(text):
            self.truncated = True

    def _closing_budget(self, *, extra_tag: str | None = None) -> int:
        budget = sum(len(f"</{tag}>") for tag in self.open_tags)
        if extra_tag and extra_tag not in _VOID_HTML_TAGS:
            budget += len(f"</{extra_tag}>")
        return budget

    def _append(self, text: str) -> None:
        self.parts.append(text)
        self.current_length += len(text)

    def finish(self) -> str:
        for tag in reversed(self.open_tags):
            self._append(f"</{tag}>")
        return "".join(self.parts)


def truncate_html(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value

    truncator = _HTMLTruncator(limit)
    truncator.feed(value)
    truncator.close()
    return truncator.finish()


def _truncate_text(value: str, limit: int) -> str:
    return value[:limit]


def _truncate_words(value: str, limit: int) -> str:
    words = value.split()
    return " ".join(words[:limit])


def _strip_frontmatter(content: str) -> str:
    if not content.startswith("---"):
        return content.strip()
    end = content.find("\n---", 3)
    if end == -1:
        return content.strip()
    return content[end + 4 :].strip()


def _extract_markdown_sections(content: str, headings: tuple[str, ...]) -> str | None:
    body = _strip_frontmatter(content)
    sections: list[str] = []
    for heading in headings:
        match = re.search(
            rf"^##\s+{re.escape(heading)}\s*$\n?(.*?)(?=^##\s+|\Z)",
            body,
            re.MULTILINE | re.DOTALL,
        )
        if not match:
            continue
        section_body = match.group(1).strip()
        section = f"## {heading}"
        if section_body:
            section += f"\n\n{section_body}"
        sections.append(section)
    combined = "\n\n".join(sections).strip()
    return combined or None


def _read_historical_context(week: str, repo_root: Path) -> dict[str, str] | None:
    match = re.fullmatch(r"(?P<year>\d{4})-W(?P<week>\d{1,2})", week)
    if not match:
        raise PodcasterHandoffError(f"Week must use YYYY-WNN format for historical context lookup: {week}")

    year = int(match.group("year"))
    week_number = int(match.group("week"))
    monday = date.fromisocalendar(year, week_number, 1)

    month_synthesis_path = repo_root / "data" / "analyzed" / f"{year}-{monday.month:02d}-month-synthesis.md"
    yearly_narrative_path = repo_root / "content" / "yearly" / f"{year}.md"

    historical_context: dict[str, str] = {}

    if month_synthesis_path.exists():
        try:
            month_synthesis = month_synthesis_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PodcasterHandoffError(
                f"Month synthesis file exists but could not be read: {month_synthesis_path} ({exc})"
            ) from exc
        extracted_sections = _extract_markdown_sections(month_synthesis, ("Month Synthesis", "Trend Arc"))
        if extracted_sections:
            historical_context["month_synthesis"] = _truncate_words(
                extracted_sections,
                MAX_MONTH_SYNTHESIS_WORDS,
            )

    if yearly_narrative_path.exists():
        try:
            yearly_narrative = yearly_narrative_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PodcasterHandoffError(
                f"Yearly narrative file exists but could not be read: {yearly_narrative_path} ({exc})"
            ) from exc
        extracted_yearly = _extract_markdown_sections(yearly_narrative, ("Year in Review",))
        if extracted_yearly:
            historical_context["yearly_narrative"] = _truncate_words(
                extracted_yearly,
                MAX_YEARLY_NARRATIVE_WORDS,
            )

    return historical_context or None


def _resolve_spotify_publish(config: dict[str, Any], *, week: str, article_title: str | None, article_summary: str | None) -> dict[str, Any]:
    """Render spotify_publish templates into concrete values for the Podcaster API.

    Design: SquadScope resolves templates (title_template, description_template)
    into final strings before sending. Podcaster receives ready-to-use metadata,
    not raw templates — this keeps rendering logic in the source-of-truth repo.
    """
    match = re.fullmatch(r"(?P<year>\d{4})-W(?P<week>\d{1,2})", week)
    if not match:
        raise PodcasterHandoffError(f"Week must use YYYY-WNN format for spotify_publish templating: {week}")
    context: dict[str, Any] = {
        "year": int(match.group("year")),
        "week": int(match.group("week")),
        "article_title": article_title or "",
        "article_summary": article_summary or "",
    }
    resolved = _render_template_value(config, context)
    title = resolved.pop("title_template", None)
    if isinstance(title, str):
        resolved["title"] = _truncate_text(title, MAX_SPOTIFY_TITLE_CHARS)
    elif title is not None:
        resolved["title"] = title
    description = resolved.pop("description_template", None)
    if isinstance(description, str):
        resolved["description"] = truncate_html(description, MAX_SPOTIFY_DESCRIPTION_CHARS)
    elif description is not None:
        resolved["description"] = description
    return resolved


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
    breaking_news: str | None = None,
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
    historical_context = _read_historical_context(week, root)
    if historical_context:
        if "script_directions" not in payload:
            payload["script_directions"] = {}
        payload["script_directions"]["historical_context"] = historical_context
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

    if breaking_news:
        payload["breaking_news"] = breaking_news

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
        try:
            raw = exc.read(1024)
            error_body = raw.decode("utf-8", errors="replace")
            # Sanitize for GitHub Actions: strip workflow-command sequences and newlines
            error_body = error_body.replace("::", "").replace("\r", " ").replace("\n", " ")
        except Exception:
            error_body = "<unreadable>"
        raise PodcasterHandoffError(
            f"Podcaster handoff failed with HTTP {exc.code}. Response body: {error_body}"
        ) from exc
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
            breaking_news=args.breaking_news,
        )
        post_handoff(endpoint, api_key, payload, timeout=args.timeout)
    except PodcasterHandoffError as exc:
        print(f"::error::Podcaster handoff failed: {exc}")
        return 1
    print("::notice::Podcaster handoff accepted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

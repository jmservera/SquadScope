#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urljoin, urlparse


AUTH_HEADER = "x-podcaster-api-key"
DEFAULT_TIMEOUT_SECONDS = 30


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
    podcaster_dry_run: bool = False,
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    if not _manifest_allows_handoff(manifest, week=week, publish_mode=publish_mode):
        raise PodcasterHandoffError("Publish manifest is not eligible for Podcaster handoff.")
    payload: dict[str, Any] = {
        "week": week,
        "article_url": article_url,
        "article_path": normalize_page_path(article_path),
        "publish_run_id": publish_run_id,
        "publish_mode": publish_mode,
    }
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
    if podcaster_dry_run:
        payload["dry_run"] = True
    return payload


SUCCESS_RESPONSE_STATUSES = {"accepted"}


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

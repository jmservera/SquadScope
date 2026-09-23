from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib import parse

_CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x20\x7f]")
_INVALID_PERCENT_PATTERN = re.compile(r"%(?![0-9A-Fa-f]{2})")
_PLAIN_HTTP_URL_PATTERN = re.compile(r"https?://[^\s<>()\[\]{}\"']+", re.IGNORECASE)
_PLAIN_WWW_URL_PATTERN = re.compile(r"\bwww\.[^\s<>()\[\]{}\"']+", re.IGNORECASE)
_MARKDOWN_DESTINATION_PATTERN = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?")
_MARKDOWN_REFERENCE_DEFINITION_PATTERN = re.compile(r"(?m)^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)>?")
_MARKDOWN_LINK_TEXT_PATTERN = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_AUTOLINK_PATTERN = re.compile(r"<([A-Za-z][A-Za-z0-9+.-]*:[^>\s]+)>")
_HTML_QUOTED_URL_ATTRIBUTE_PATTERN = re.compile(
    r"\b(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE
)
_HTML_UNQUOTED_URL_ATTRIBUTE_PATTERN = re.compile(
    r"\b(?:href|src)\s*=\s*([^\s\"'=<>`]+)", re.IGNORECASE
)
_EXPLICIT_SCHEME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_CHARACTER_REFERENCE_PATTERN = re.compile(r"&(?:#[0-9]+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]+);")
_MARKDOWN_CONTROL_PATTERN = re.compile(r"[*_~`]+")
_HTML_COMMENT_PATTERN = re.compile(r"<!--(.*?)-->", re.DOTALL)
_HTML_TAG_PATTERN = re.compile(r"<[^>]*>")
_ZERO_WIDTH_PATTERN = re.compile(r"[\u200b-\u200f\u2060\ufeff]")

_DIRECTIVE_PATTERNS = (
    (
        re.compile(r"(?mi)^\s*(?:system|developer|assistant|user)\s*:"),
        "generated content contains a role-prefixed instruction line.",
    ),
    (
        re.compile(r"(?i)</?untrusted-content>"),
        "generated content contains an internal prompt-boundary marker.",
    ),
    (
        re.compile(r"(?i)\bignore\s+(?:all\s+|the\s+)?(?:previous|above)\s+instructions?\b"),
        "generated content contains an instruction-override phrase.",
    ),
    (
        re.compile(r"(?mi)^\s*(?:new|updated|replacement|override)\s+instructions?\s*:"),
        "generated content contains an instruction-replacement phrase.",
    ),
    (
        re.compile(r"(?i)\boverride\s+(?:all\s+|the\s+)?(?:previous\s+)?instructions?\b"),
        "generated content contains an instruction-replacement phrase.",
    ),
    (
        re.compile(
            r"(?i)\bdo\s+not\s+follow\s+(?:the\s+)?(?:previous|above|original)?\s*instructions?\b"
        ),
        "generated content contains an instruction-bypass phrase.",
    ),
    (
        re.compile(r"(?i)\b(?:you|the\s+assistant|the\s+model)\s+(?:are|must|should)\s+now\b"),
        "generated content contains a role-change directive.",
    ),
    (
        re.compile(
            r"(?i)\b(?:you|the\s+assistant|the\s+model)\s+"
            r"(?:are|become|will\s+be|must\s+be|should\s+be)\s+(?:now\s+)?"
            r"(?:the\s+|an?\s+)?(?:podcast\s+)?"
            r"(?:host|presenter|podcaster|narrator|assistant|system|developer|model)\b"
        ),
        "generated content contains a role-change directive.",
    ),
    (
        re.compile(
            r"(?i)\b(?:pretend\s+to\s+be|roleplay\s+as|"
            r"act\s+as(?:\s+if\s+you\s+(?:are|were))?)\s+"
            r"(?:the\s+|an?\s+)?(?:podcast\s+)?"
            r"(?:host|presenter|podcaster|narrator|assistant|system|developer|model)\b"
        ),
        "generated content contains a role-change directive.",
    ),
    (
        re.compile(
            r"(?i)\b(?:podcast|podcaster|audio\s+episode|episode)\s+"
            r"(?:instructions?|directions?|commands?|tasks?)\b"
        ),
        "generated content contains downstream podcast instructions.",
    ),
    (
        re.compile(
            r"(?mi)^\s*(?:instructions?|directions?|commands?|tasks?)\s+for\s+"
            r"(?:the\s+)?(?:podcast|podcaster|audio\s+episode|episode)\s*:"
        ),
        "generated content contains downstream podcast instructions.",
    ),
    (
        re.compile(
            r"(?i)\b(?:follow|use|obey|apply)\s+(?:these\s+|the\s+)?"
            r"(?:instructions?|directions?|commands?|tasks?)\s+for\s+"
            r"(?:the\s+)?(?:podcast|podcaster|audio\s+episode|episode)\b"
        ),
        "generated content contains downstream podcast instructions.",
    ),
    (
        re.compile(r"(?mi)^\s*script\s+directions?\s*:"),
        "generated content contains downstream script directions.",
    ),
    (
        re.compile(
            r"(?i)\b(?:tell|ask|instruct|have|make|direct|require)\s+"
            r"(?:the\s+)?(?:hosts?|presenters?|podcasters?|narrators?)\s+"
            r"(?:to\s+)?(?:read|say|follow|include|visit|open|click|execute|perform|obey|use)\b"
        ),
        "generated content contains a downstream host directive.",
    ),
    (
        re.compile(
            r"(?i)\b(?:the\s+)?(?:hosts?|presenters?|podcasters?|narrators?)\s+"
            r"(?:must|should|need\s+to|are\s+required\s+to)\s+"
            r"(?:read|say|follow|include|visit|open|click|execute|perform|obey|use)\b"
        ),
        "generated content contains a downstream host directive.",
    ),
    (
        re.compile(
            r"(?i)\bfor\s+the\s+(?:podcast|audio\s+episode|episode)\s*,\s*"
            r"(?:tell|ask|instruct|have|make|direct|require|read|say|follow|include|"
            r"visit|open|click|execute|perform|obey|use)\b"
        ),
        "generated content contains a downstream podcast directive.",
    ),
    (
        re.compile(
            r"(?i)\b(?:during|in|for)\s+(?:the\s+)?"
            r"(?:podcast|audio\s+episode|episode)\s*[:,]\s*"
            r"(?:announce|read|say|tell|ask|instruct|include|visit|open|click|"
            r"execute|perform|obey|use)\b"
        ),
        "generated content contains a downstream podcast directive.",
    ),
    (
        re.compile(r"(?i)\bread\s+(?:this|the\s+following)\s+verbatim\b"),
        "generated content contains a downstream narration directive.",
    ),
    (
        re.compile(
            r"(?i)\b(?:hosts?|presenters?|podcasters?|narrators?)\s*[:,]\s*"
            r"(?:read|say|follow|include|visit|open|click|execute|perform|obey|use)\b"
        ),
        "generated content contains a downstream host directive.",
    ),
)


def normalize_evidence_url(value: str) -> str | None:
    candidate = value.strip()
    if not candidate or _CONTROL_CHARACTER_PATTERN.search(candidate):
        return None
    if "\\" in candidate or _INVALID_PERCENT_PATTERN.search(candidate):
        return None
    try:
        parsed = parse.urlsplit(candidate)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return None
    if parsed.netloc.endswith(":"):
        return None
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"} or not hostname:
        return None
    if parsed.netloc.endswith(":"):
        return None
    if parsed.username is not None or parsed.password is not None:
        return None
    try:
        normalized_host = hostname.encode("idna").decode("ascii").lower()
    except UnicodeError:
        return None
    if ":" in normalized_host and not normalized_host.startswith("["):
        normalized_host = f"[{normalized_host}]"
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = normalized_host if port is None or default_port else f"{normalized_host}:{port}"
    path = parsed.path or "/"
    return parse.urlunsplit((scheme, netloc, path, parsed.query, ""))


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"unable to read external evidence artifact {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"external evidence artifact is invalid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"external evidence artifact must contain a JSON object: {path}")
    return payload


def _collect_article_urls(payload: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    articles = payload.get("articles")
    if isinstance(articles, list):
        for article in articles:
            if isinstance(article, dict) and isinstance(article.get("url"), str):
                urls.append(article["url"])
    correlations = payload.get("correlations")
    if isinstance(correlations, list):
        for correlation in correlations:
            if not isinstance(correlation, dict):
                continue
            matched_articles = correlation.get("matched_articles")
            if isinstance(matched_articles, list):
                urls.extend(url for url in matched_articles if isinstance(url, str))
            details = correlation.get("matched_article_details")
            if isinstance(details, list):
                for detail in details:
                    if isinstance(detail, dict) and isinstance(detail.get("url"), str):
                        urls.append(detail["url"])
    return urls


def load_external_url_allowlist(paths: list[Path | None]) -> tuple[set[str], list[str]]:
    allowed: set[str] = set()
    errors: list[str] = []
    for path in paths:
        if path is None:
            continue
        try:
            payload = _load_json_object(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for value in _collect_article_urls(payload):
            normalized = normalize_evidence_url(value)
            if normalized is None:
                errors.append(
                    f"external evidence artifact contains an invalid URL: {path}: {value}"
                )
            else:
                allowed.add(normalized)
    return allowed, errors


def _strip_trailing_plain_url_punctuation(value: str) -> str:
    return value.rstrip(".,;:!?")


def extract_document_url_targets(document: str) -> set[str]:
    targets = {
        match.group(1).strip()
        for pattern in (
            _MARKDOWN_DESTINATION_PATTERN,
            _MARKDOWN_REFERENCE_DEFINITION_PATTERN,
            _AUTOLINK_PATTERN,
            _HTML_QUOTED_URL_ATTRIBUTE_PATTERN,
            _HTML_UNQUOTED_URL_ATTRIBUTE_PATTERN,
        )
        for match in pattern.finditer(document)
    }
    targets.update(
        _strip_trailing_plain_url_punctuation(match.group(0))
        for match in _PLAIN_HTTP_URL_PATTERN.finditer(document)
    )
    targets.update(
        f"https://{_strip_trailing_plain_url_punctuation(match.group(0))}"
        for match in _PLAIN_WWW_URL_PATTERN.finditer(document)
    )
    return {target for target in targets if target}


def external_url_provenance_errors(
    document: str,
    allowed_external_urls: set[str],
    allowed_github_repositories: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    allowed_github_urls = {
        candidate
        for repository in allowed_github_repositories or set()
        for candidate in (
            f"https://github.com/{repository}",
            f"https://github.com/{repository}/",
        )
    }
    for raw_target in sorted(extract_document_url_targets(document)):
        target = html.unescape(raw_target)
        if target != raw_target or _CHARACTER_REFERENCE_PATTERN.search(raw_target):
            errors.append(f"generated content contains an ambiguously encoded URL: {raw_target}")
            continue
        if _CONTROL_CHARACTER_PATTERN.search(target) or "\\" in target:
            errors.append(f"generated content contains a malformed external URL: {raw_target}")
            continue
        if target.startswith("//"):
            errors.append(f"external URL uses unsupported scheme-relative syntax: {target}")
            continue
        if target.startswith(("#", "/", "./", "../")):
            continue
        explicit_scheme = _EXPLICIT_SCHEME_PATTERN.match(target)
        if explicit_scheme and explicit_scheme.group(0)[:-1].lower() not in {"http", "https"}:
            errors.append(f"generated content contains an unsupported URL scheme: {target}")
            continue
        if explicit_scheme and not target.lower().startswith(("http://", "https://")):
            errors.append(f"generated content contains a malformed external URL: {target}")
            continue
        if not target.lower().startswith(("http://", "https://")):
            continue
        normalized = normalize_evidence_url(target)
        if normalized is None:
            errors.append(f"generated content contains a malformed external URL: {target}")
            continue
        if normalized not in allowed_external_urls and normalized not in allowed_github_urls:
            errors.append(
                f"external URL must resolve to the current run-scoped evidence inventory: {target}"
            )
    return errors


def _normalize_directive_text(document: str) -> str:
    normalized = html.unescape(unicodedata.normalize("NFKC", document))
    normalized = _ZERO_WIDTH_PATTERN.sub("", normalized)
    normalized = _MARKDOWN_LINK_TEXT_PATTERN.sub(r"\1", normalized)
    normalized = _HTML_COMMENT_PATTERN.sub(r"\1", normalized)
    normalized = _HTML_TAG_PATTERN.sub("", normalized)
    normalized = _MARKDOWN_CONTROL_PATTERN.sub("", normalized)
    return re.sub(r"[^\S\n]+", " ", normalized)


def downstream_directive_errors(document: str) -> list[str]:
    normalized = _normalize_directive_text(document)
    return [message for pattern, message in _DIRECTIVE_PATTERNS if pattern.search(normalized)]


def generated_content_security_errors(
    document: str, allowed_external_urls: set[str] | None = None
) -> list[str]:
    errors = downstream_directive_errors(document)
    if allowed_external_urls is not None:
        errors.extend(external_url_provenance_errors(document, allowed_external_urls))
    return errors

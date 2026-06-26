#!/usr/bin/env python3
"""Validate that published content does not hotlink external images.

Scans Markdown content files and frontmatter for:
- Remote image URLs (http/https) in Markdown image syntax or HTML img tags
- External og:image or cover_image values in YAML frontmatter
- SAS tokens, credentials, or tracking parameters in image URLs
- References to images not present in the image registry

Exit code 0 = clean, 1 = violations found.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CONTENT_DIR = Path("content")
REGISTRY_PATH = Path("data/image-registry.json")

# Patterns that indicate remote/external image references
REMOTE_URL_PATTERN = re.compile(r"https?://[^\s\"'>)\]]+", re.IGNORECASE)
MD_IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_IMG_PATTERN = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE)

# Frontmatter fields that reference images
IMAGE_FRONTMATTER_FIELDS = ("cover_image", "og_image", "image", "thumbnail")

# Patterns indicating secrets/credentials in URLs
SECRET_PATTERNS = [
    re.compile(r"[?&](?:sig|sv|se|sp|spr|srt|ss)=", re.IGNORECASE),  # Azure SAS
    re.compile(r"[?&](?:token|api_key|apikey|secret|password)=", re.IGNORECASE),
    re.compile(
        r"[?&](?:utm_source|utm_medium|utm_campaign|fbclid|gclid)=", re.IGNORECASE
    ),  # Tracking
]


def _is_remote_url(value: str) -> bool:
    return value.startswith(("http://", "https://", "//"))


def _extract_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML frontmatter image fields (simple key: value parsing)."""
    fields: dict[str, str] = {}
    if not text.startswith("---"):
        return fields
    end = text.find("\n---", 3)
    if end == -1:
        return fields
    fm_block = text[3:end]
    for line in fm_block.splitlines():
        for field in IMAGE_FRONTMATTER_FIELDS:
            if line.strip().startswith(f"{field}:"):
                value = line.split(":", 1)[1].strip().strip("\"'")
                if value:
                    fields[field] = value
    return fields


def _check_secrets_in_url(url: str) -> list[str]:
    """Check for credentials or tracking params in a URL."""
    issues = []
    for pat in SECRET_PATTERNS:
        if pat.search(url):
            issues.append(f"URL contains suspicious parameters: {url[:120]}")
            break
    return issues


def validate_file(filepath: Path) -> list[str]:
    """Validate a single content file. Returns list of violations."""
    violations: list[str] = []
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return violations

    # Check frontmatter image fields
    fm_fields = _extract_frontmatter(text)
    for field, value in fm_fields.items():
        if _is_remote_url(value):
            violations.append(
                f"{filepath}: frontmatter '{field}' hotlinks external URL: {value[:100]}"
            )
        violations.extend(
            f"{filepath}: frontmatter '{field}' {issue}" for issue in _check_secrets_in_url(value)
        )

    # Check Markdown image syntax ![alt](url)
    for match in MD_IMAGE_PATTERN.finditer(text):
        url = match.group(2).strip()
        if _is_remote_url(url):
            violations.append(f"{filepath}: Markdown image hotlinks external URL: {url[:100]}")
        violations.extend(f"{filepath}: {issue}" for issue in _check_secrets_in_url(url))

    # Check HTML <img src="...">
    for match in HTML_IMG_PATTERN.finditer(text):
        url = match.group(1).strip()
        if _is_remote_url(url):
            violations.append(f"{filepath}: HTML img hotlinks external URL: {url[:100]}")
        violations.extend(f"{filepath}: {issue}" for issue in _check_secrets_in_url(url))

    return violations


def validate_content(content_dir: Path = CONTENT_DIR) -> list[str]:
    """Scan all .md files under content_dir for image policy violations."""
    all_violations: list[str] = []
    if not content_dir.exists():
        return all_violations
    for md_file in sorted(content_dir.rglob("*.md")):
        all_violations.extend(validate_file(md_file))
    return all_violations


def validate_registry_references(
    content_dir: Path = CONTENT_DIR,
    registry_path: Path = REGISTRY_PATH,
) -> list[str]:
    """Verify local image references in frontmatter exist in the registry."""
    violations: list[str] = []
    if not registry_path.exists():
        violations.append(f"Image registry file not found: {registry_path}")
        return violations
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        violations.append(f"Cannot parse registry: {registry_path}")
        return violations

    # Build a normalized set for matching. Hugo resolves covers via resources.Get
    # using asset-relative paths (e.g., "covers/foo.webp"), while on-disk files
    # live under "assets/covers/". Register both forms for consistent matching.
    registered_files: set[str] = set()
    for img in registry.get("images", []):
        filename = img.get("filename", "")
        registered_files.add(filename)
        if filename.startswith("assets/"):
            registered_files.add(filename[len("assets/") :])
        else:
            registered_files.add(f"assets/{filename}")

    if not content_dir.exists():
        return violations

    for md_file in sorted(content_dir.rglob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm_fields = _extract_frontmatter(text)
        for field, value in fm_fields.items():
            if not _is_remote_url(value) and value and value not in registered_files:
                # Only flag non-generated assets (covers/ prefix indicates registry-managed)
                if value.startswith("covers/") or value.startswith("assets/covers/"):
                    violations.append(
                        f"{md_file}: frontmatter '{field}' references unregistered image: {value}"
                    )
    return violations


def main() -> int:
    violations = validate_content()
    violations.extend(validate_registry_references())

    if violations:
        print("Image policy violations found:", file=sys.stderr)
        for v in violations:
            print(f"  FAIL: {v}", file=sys.stderr)
        return 1

    print("Content image validation passed: no hotlinks, secrets, or unregistered covers found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Manage the SquadScope image registry (data/image-registry.json).

Tracks locally-hosted cover images with license, attribution, and usage metadata.
Enforces the no-hotlinking policy: only locally-hosted images are registered.

Usage:
    python scripts/manage_image_registry.py add \\
        --filename assets/covers/2026-W24.webp \\
        --license CC0 \\
        --source-url https://openverse.org/image/abc \\
        --attribution "Photo by Author on Openverse" \\
        --added-by operator

    python scripts/manage_image_registry.py validate

    python scripts/manage_image_registry.py list
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REGISTRY_PATH = Path("data/image-registry.json")
ALLOWED_LICENSES = ("CC0", "CC-BY-4.0", "CC-BY-SA-4.0", "Openverse", "local-asset", "custom")


def load_registry(path: Path = REGISTRY_PATH) -> dict:
    if not path.exists():
        return {"images": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(registry: dict, path: Path = REGISTRY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _is_safe_local_path(filename: str) -> tuple[bool, str]:
    """Check that filename is a safe local relative path."""
    if filename.startswith(("http://", "https://", "//")):
        return False, "filename is a URL (no hotlinking allowed)"
    if filename.startswith("/"):
        return False, "filename is an absolute path (must be relative)"
    if ".." in filename.split("/"):
        return False, "filename contains path traversal (..)"
    return True, ""


def add_image(args: argparse.Namespace) -> int:
    registry = load_registry()

    # Validate license
    if args.license not in ALLOWED_LICENSES:
        print(f"ERROR: Invalid license '{args.license}'. Must be one of: {', '.join(ALLOWED_LICENSES)}", file=sys.stderr)
        return 1

    # Validate path safety
    safe, reason = _is_safe_local_path(args.filename)
    if not safe:
        print(f"ERROR: {reason}: {args.filename}", file=sys.stderr)
        return 1

    # Check file exists locally
    if not Path(args.filename).exists():
        print(f"WARNING: File '{args.filename}' does not exist locally yet.", file=sys.stderr)

    # Check for duplicates
    existing = [img for img in registry["images"] if img["filename"] == args.filename]
    if existing:
        print(f"ERROR: Image '{args.filename}' already in registry.", file=sys.stderr)
        return 1

    entry = {
        "filename": args.filename,
        "license": args.license,
        "added_by": args.added_by,
        "added_at": date.today().isoformat(),
    }
    if args.source_url:
        entry["source_url"] = args.source_url
    if args.attribution:
        entry["attribution"] = args.attribution

    registry["images"].append(entry)
    save_registry(registry)
    print(f"Added '{args.filename}' to image registry.")
    return 0


def validate_registry(args: argparse.Namespace) -> int:
    registry = load_registry()
    errors: list[str] = []

    for i, img in enumerate(registry["images"]):
        if not img.get("filename"):
            errors.append(f"Entry {i}: missing filename")
        if not img.get("license"):
            errors.append(f"Entry {i}: missing license")
        elif img["license"] not in ALLOWED_LICENSES:
            errors.append(f"Entry {i}: invalid license '{img['license']}'")
        if not img.get("added_by"):
            errors.append(f"Entry {i}: missing added_by")

        # Verify no hotlinking and path safety
        filename = img.get("filename", "")
        safe, reason = _is_safe_local_path(filename)
        if not safe:
            errors.append(f"Entry {i}: {reason}: {filename}")

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print(f"Image registry valid: {len(registry['images'])} entries.")
    return 0


def list_images(args: argparse.Namespace) -> int:
    registry = load_registry()
    if not registry["images"]:
        print("No images registered.")
        return 0
    for img in registry["images"]:
        license_str = img.get("license", "unknown")
        print(f"  {img['filename']}  [{license_str}]  by {img.get('added_by', '?')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage SquadScope image registry")
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Register a new image")
    add_p.add_argument("--filename", required=True, help="Local path to the image file")
    add_p.add_argument("--license", required=True, choices=ALLOWED_LICENSES, help="Image license")
    add_p.add_argument("--source-url", default="", help="Original source URL")
    add_p.add_argument("--attribution", default="", help="Attribution text")
    add_p.add_argument("--added-by", required=True, help="Who added this image")

    sub.add_parser("validate", help="Validate the image registry")
    sub.add_parser("list", help="List registered images")

    args = parser.parse_args(argv)
    if args.command == "add":
        return add_image(args)
    elif args.command == "validate":
        return validate_registry(args)
    elif args.command == "list":
        return list_images(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

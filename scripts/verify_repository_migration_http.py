"""Verify approved repository migration behavior at the production origin."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

APPROVED_MAP = Path("data/migrations/repository-approved-dispositions.json")


def response_for(url: str) -> Any:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "claracle.com":
        raise ValueError(f"Production checks require https://claracle.com: {url}")
    try:
        return urllib.request.urlopen(url, timeout=30)  # nosec B310 - exact HTTPS origin above
    except urllib.error.HTTPError as error:
        return error


def verify_once(root: Path, origin: str) -> list[str]:
    data = json.loads((root / APPROVED_MAP).read_text(encoding="utf-8"))
    records = data["records"]
    retained = next(
        record
        for record in records
        if record["disposition"] == "keep" and record["url_type"] == "canonical"
    )
    # The clean artifact check covers every route; production probes sample both a
    # formerly retained canonical URL and the former alias to catch stale deployment.
    required_retirements = (
        "/repo/ruvnet-ruflo/",
        "/repo/pewdiepie-archdaemon-odysseus/",
    )
    retired_urls = {record["url"] for record in records if record["disposition"] == "retire"}
    missing = set(required_retirements) - retired_urls
    if missing:
        raise ValueError(f"Required direct-404 retirements are missing: {sorted(missing)}")
    problems = []
    checks = ((retained["url"], 200), *((url, 404) for url in required_retirements))
    for url, expected in checks:
        response = response_for(origin + url)
        if response.status != expected:
            problems.append(f"{url}: expected {expected}, got {response.status}")
    return problems


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--origin", default="https://claracle.com")
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--delay", type=float, default=0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    origin = args.origin.rstrip("/")
    for attempt in range(1, args.attempts + 1):
        problems = verify_once(args.root.resolve(), origin)
        if not problems:
            return 0
        if attempt < args.attempts:
            time.sleep(args.delay)
    raise SystemExit("\n".join(problems))


if __name__ == "__main__":
    raise SystemExit(main())

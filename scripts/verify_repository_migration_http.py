"""Verify approved repository migration behavior at the production origin."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

APPROVED_MAP = Path("data/migrations/repository-approved-dispositions.json")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def response_for(url: str, *, follow_redirects: bool = True) -> Any:
    opener = (
        urllib.request.build_opener()
        if follow_redirects
        else urllib.request.build_opener(NoRedirect())
    )
    try:
        return opener.open(url, timeout=30)
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
    retired = next(
        record
        for record in records
        if record["disposition"] == "retire" and record["url_type"] == "canonical"
    )
    redirected = next(record for record in records if record["disposition"] == "redirect")
    problems = []
    for record, expected in ((retained, 200), (retired, 404)):
        response = response_for(origin + record["url"])
        if response.status != expected:
            problems.append(f"{record['url']}: expected {expected}, got {response.status}")
    response = response_for(origin + redirected["url"], follow_redirects=False)
    expected_location = origin + redirected["destination"]
    location = response.headers.get("Location")
    resolved_location = urljoin(origin + redirected["url"], location or "")
    if response.status != 301 or resolved_location != expected_location:
        problems.append(
            f"{redirected['url']}: expected 301 to {expected_location}, "
            f"got {response.status} to {location}"
        )
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

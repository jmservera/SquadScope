"""Capture Search Console URL Inspection evidence for repository URLs."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SCHEMA_VERSION = "1.0.0"
INVENTORY_PATH = Path("data/derived/observatory/repository-url-inventory.json")
OUTPUT_PATH = Path("data/derived/observatory/repository-url-inspection.json")
ENDPOINT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"


def inspect_url(
    inspection_url: str,
    *,
    site_url: str,
    token: str,
    attempts: int = 4,
) -> dict[str, Any]:
    body = json.dumps(
        {
            "inspectionUrl": inspection_url,
            "siteUrl": site_url,
            "languageCode": "en-US",
        }
    ).encode()
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Claracle/BR-003",
        },
    )
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == attempts - 1:
                detail = error.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"URL Inspection failed for {inspection_url}: HTTP {error.code}: {detail}"
                ) from error
            time.sleep(2**attempt)
        except (TimeoutError, urllib.error.URLError) as error:
            if attempt == attempts - 1:
                raise RuntimeError(
                    f"URL Inspection network failure for {inspection_url}: {error}"
                ) from error
            time.sleep(2**attempt)
    raise RuntimeError(f"URL Inspection failed for {inspection_url}")


def build_snapshot(
    inventory: dict[str, Any],
    *,
    site_origin: str,
    site_url: str,
    captured_at: str,
    inspector: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    items = inventory["records"]
    inspection_urls = [f"{site_origin}{item['url']}" for item in items]
    with ThreadPoolExecutor(max_workers=4) as executor:
        responses = list(executor.map(inspector, inspection_urls))

    records = []
    for item, inspection_url, response in zip(
        items,
        inspection_urls,
        responses,
        strict=True,
    ):
        result = response.get("inspectionResult", {})
        index = result.get("indexStatusResult", {})
        records.append(
            {
                "url": item["url"],
                "inspection_url": inspection_url,
                "inspection_result_link": result.get("inspectionResultLink"),
                "verdict": index.get("verdict"),
                "coverage_state": index.get("coverageState"),
                "robots_txt_state": index.get("robotsTxtState"),
                "indexing_state": index.get("indexingState"),
                "page_fetch_state": index.get("pageFetchState"),
                "last_crawl_time": index.get("lastCrawlTime"),
                "user_canonical": index.get("userCanonical"),
                "google_canonical": index.get("googleCanonical"),
                "referring_urls": index.get("referringUrls", []),
                "sitemaps": index.get("sitemap", []),
            }
        )

    verdicts = Counter(record["verdict"] or "UNSPECIFIED" for record in records)
    coverage = Counter(record["coverage_state"] or "UNSPECIFIED" for record in records)
    return {
        "schema_version": SCHEMA_VERSION,
        "captured_at": captured_at,
        "site_origin": site_origin,
        "site_url": site_url,
        "counts": {
            "total": len(records),
            "verdicts": dict(sorted(verdicts.items())),
            "coverage_states": dict(sorted(coverage.items())),
        },
        "records": records,
    }


def validate_snapshot(snapshot: dict[str, Any], inventory: dict[str, Any]) -> None:
    expected = {record["url"] for record in inventory["records"]}
    actual = {record["url"] for record in snapshot.get("records", [])}
    if expected != actual or len(snapshot.get("records", [])) != len(expected):
        raise ValueError("URL Inspection snapshot does not cover the current inventory")
    incomplete = [
        record["url"]
        for record in snapshot["records"]
        if not record["verdict"] or not record["coverage_state"]
    ]
    if incomplete:
        raise ValueError("URL Inspection returned incomplete evidence: " + ", ".join(incomplete))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--site-origin", default="https://claracle.com")
    parser.add_argument("--site-url", default="sc-domain:claracle.com")
    parser.add_argument("--token-file", type=Path)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    inventory = json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
    output = root / OUTPUT_PATH
    if args.check:
        if not output.exists():
            raise SystemExit(f"URL Inspection snapshot is missing: {OUTPUT_PATH}")
        validate_snapshot(json.loads(output.read_text(encoding="utf-8")), inventory)
        return 0
    if args.token_file is None:
        raise SystemExit("--token-file is required when capturing URL Inspection evidence")
    token = args.token_file.read_text(encoding="utf-8").strip()
    if not token:
        raise SystemExit("URL Inspection token file is empty")
    snapshot = build_snapshot(
        inventory,
        site_origin=args.site_origin.rstrip("/"),
        site_url=args.site_url,
        captured_at=datetime.now(timezone.utc).isoformat(),
        inspector=lambda url: inspect_url(url, site_url=args.site_url, token=token),
    )
    validate_snapshot(snapshot, inventory)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

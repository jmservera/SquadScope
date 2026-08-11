"""Capture the live repository URL surface for BR-003 migration review."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
INVENTORY_PATH = Path("data/derived/observatory/repository-url-inventory.json")
OUTPUT_PATH = Path("data/derived/observatory/repository-production-snapshot.json")


def _sitemap_paths(data: bytes, site_origin: str) -> set[str]:
    root = ET.fromstring(data)
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {
        element.text.removeprefix(site_origin)
        for element in root.findall("s:url/s:loc", namespace)
        if element.text and element.text.startswith(f"{site_origin}/repo/")
    }


def _http_status(url: str) -> int:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Claracle/BR-003"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return int(response.status)
    except urllib.error.HTTPError as error:
        return int(error.code)
    except urllib.error.URLError:
        return 0


def build_snapshot(
    inventory: dict[str, Any],
    *,
    site_origin: str,
    captured_at: date,
    sitemap_data: bytes,
    status_getter: Any = _http_status,
) -> dict[str, Any]:
    sitemap_url = f"{site_origin}/sitemap.xml"
    sitemap_paths = _sitemap_paths(sitemap_data, site_origin)
    urls = [record["url"] for record in inventory["records"]]
    with ThreadPoolExecutor(max_workers=12) as executor:
        statuses = dict(
            zip(
                urls,
                executor.map(lambda path: status_getter(f"{site_origin}{path}"), urls),
                strict=True,
            )
        )
    records = [
        {
            "url": record["url"],
            "url_type": record["url_type"],
            "canonical_url": record["canonical_url"],
            "in_sitemap": record["url"] in sitemap_paths,
            "http_status": statuses[record["url"]],
        }
        for record in inventory["records"]
    ]
    local_urls = set(urls)
    production_only = sorted(sitemap_paths - local_urls)
    return {
        "schema_version": SCHEMA_VERSION,
        "captured_at": captured_at.isoformat(),
        "site_origin": site_origin,
        "sources": {
            "sitemap": sitemap_url,
            "http_method": "HEAD",
            "url_inspection": "not_collected",
            "search_analytics": "not_collected",
            "sampled_links": "not_collected",
            "first_party_referrals": "not_collected",
        },
        "counts": {
            "local_urls": len(local_urls),
            "sitemap_urls": len(sitemap_paths),
            "http_200": sum(record["http_status"] == 200 for record in records),
            "http_404": sum(record["http_status"] == 404 for record in records),
            "http_other_or_unavailable": sum(
                record["http_status"] not in {200, 404} for record in records
            ),
            "production_only": len(production_only),
        },
        "production_only_urls": production_only,
        "records": records,
    }


def validate_snapshot(snapshot: dict[str, Any], inventory: dict[str, Any]) -> None:
    inventory_urls = {record["url"] for record in inventory["records"]}
    snapshot_urls = {record["url"] for record in snapshot.get("records", [])}
    if inventory_urls != snapshot_urls:
        raise ValueError("Production snapshot does not cover the current repository URL inventory")
    if snapshot["counts"]["local_urls"] != len(inventory_urls):
        raise ValueError("Production snapshot local URL count is inconsistent")
    if snapshot["counts"]["production_only"] != len(snapshot["production_only_urls"]):
        raise ValueError("Production-only URL count is inconsistent")
    unavailable = [record["url"] for record in snapshot["records"] if record["http_status"] == 0]
    if unavailable:
        raise ValueError(
            "Production snapshot contains unavailable HTTP evidence: " + ", ".join(unavailable)
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--site-origin", default="https://claracle.com")
    parser.add_argument("--captured-at", type=date.fromisoformat)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    inventory = json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
    output = root / OUTPUT_PATH
    if args.check:
        if not output.exists():
            raise SystemExit(f"Repository production snapshot is missing: {OUTPUT_PATH}")
        validate_snapshot(json.loads(output.read_text(encoding="utf-8")), inventory)
        return 0
    if args.captured_at is None:
        raise SystemExit("--captured-at is required when capturing production evidence")
    sitemap_url = f"{args.site_origin}/sitemap.xml"
    with urllib.request.urlopen(sitemap_url, timeout=30) as response:
        sitemap_data = response.read()
    snapshot = build_snapshot(
        inventory,
        site_origin=args.site_origin.rstrip("/"),
        captured_at=args.captured_at,
        sitemap_data=sitemap_data,
    )
    validate_snapshot(snapshot, inventory)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

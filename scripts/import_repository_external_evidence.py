"""Normalize repository migration evidence exported from GSC and GA4."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

OUTPUT_PATH = Path("data/derived/observatory/repository-external-evidence.json")
SCHEMA_VERSION = "1.0.0"
HEADER_ALIASES = {
    "search_page": ("Pages les plus populaires", "Top pages", "Page"),
    "clicks": ("Clics", "Clicks"),
    "impressions": ("Impressions",),
    "position": ("Position",),
    "link_target": ("Page cible", "Target page", "Page"),
    "landing_page": (
        "Landing page + query string",
        "Page de destination + chaîne de requête",
        "Landing page",
    ),
    "sessions": ("Sessions", "Sessions avec engagement"),
    "filter": ("Filtre", "Filter"),
    "value": ("Valeur", "Value"),
}
FRENCH_MONTHS = {
    "janv": 1,
    "févr": 2,
    "mars": 3,
    "avr": 4,
    "mai": 5,
    "juin": 6,
    "juil": 7,
    "août": 8,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "déc": 12,
}
REPOSITORY_PATH = re.compile(r"^/repo(?:/[a-z0-9-]+)?/$")


def _rows(
    path: Path,
    *,
    required: tuple[str, ...],
    allow_metadata_only: bool = False,
) -> list[dict[str, str]]:
    lines = [
        line
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if not lines:
        if allow_metadata_only:
            return []
        raise ValueError(f"CSV export has no header: {path}")
    reader = csv.DictReader(lines)
    headers = set(reader.fieldnames or [])
    for key in required:
        if not headers.intersection(HEADER_ALIASES[key]):
            raise ValueError(f"CSV export missing {key} header: {path}")
    return list(reader)


def _path(value: str) -> str:
    parsed = urlparse(value.strip())
    normalized = f"/{parsed.path.strip('/')}/"
    return "/" if normalized == "//" else normalized


def _repository_path(value: str, source: str) -> str:
    path = _path(value)
    if not REPOSITORY_PATH.fullmatch(path):
        raise ValueError(f"{source} row has an invalid repository path: {value}")
    return path


def _integer(value: str) -> int:
    normalized = (value or "").replace(",", "").strip()
    if not normalized:
        raise ValueError("Expected an integer value in evidence export")
    return int(normalized)


def _float(value: str) -> float:
    normalized = (value or "").replace(",", ".").strip()
    if not normalized:
        raise ValueError("Expected a numeric value in evidence export")
    return float(normalized)


def _first(row: dict[str, str], names: tuple[str, ...]) -> str:
    for name in names:
        if name in row:
            return row[name]
    return ""


def _search_window(filters_path: Path) -> str:
    rows = _rows(filters_path, required=("filter", "value"))
    filters = {
        _first(row, HEADER_ALIASES["filter"]): _first(row, HEADER_ALIASES["value"]) for row in rows
    }
    search_type = filters.get("Type de recherche", filters.get("Search type", ""))
    page_filter = filters.get("Page", "")
    if search_type.casefold() != "web":
        raise ValueError(f"Search Console export is not Web search: {search_type}")
    if "/repo/" not in page_filter:
        raise ValueError(f"Search Console export is not scoped to /repo/: {page_filter}")

    window = filters.get("Date", "")
    match = re.fullmatch(
        r"(\d{1,2})\s+([^\s]+)\s+(\d{4})-(\d{1,2})\s+([^\s]+)\s+(\d{4})",
        window,
    )
    if not match:
        raise ValueError(f"Unsupported Search Console date window: {window}")
    start_day, start_month, start_year, end_day, end_month, end_year = match.groups()

    def iso(day: str, month: str, year: str) -> str:
        month_number = FRENCH_MONTHS.get(month.rstrip(".").casefold())
        if month_number is None:
            raise ValueError(f"Unsupported Search Console month: {month}")
        return date(int(year), month_number, int(day)).isoformat()

    return f"{iso(start_day, start_month, start_year)}..{iso(end_day, end_month, end_year)}"


def _referral_window(referrals_path: Path) -> str:
    text = referrals_path.read_text(encoding="utf-8-sig")
    match = re.search(r"(?m)^#\s*(\d{8})-(\d{8})\s*$", text)
    if not match:
        raise ValueError(f"GA4 export is missing its date window: {referrals_path}")

    def iso(value: str) -> str:
        return date(int(value[:4]), int(value[4:6]), int(value[6:])).isoformat()

    return f"{iso(match.group(1))}..{iso(match.group(2))}"


def build_payload(
    *,
    pages_path: Path,
    links_path: Path,
    referrals_path: Path,
    filters_path: Path,
    links_window: str,
) -> dict[str, object]:
    search_rows: dict[str, dict[str, object]] = {}
    for row in _rows(
        pages_path,
        required=("search_page", "clicks", "impressions", "position"),
    ):
        url = _first(row, HEADER_ALIASES["search_page"])
        if not url:
            continue
        path = _repository_path(url, "Search Analytics")
        if path in search_rows:
            raise ValueError(f"Duplicate Search Analytics page: {path}")
        search_rows[path] = {
            "clicks": _integer(_first(row, HEADER_ALIASES["clicks"])),
            "impressions": _integer(_first(row, HEADER_ALIASES["impressions"])),
            "position": _float(_first(row, HEADER_ALIASES["position"])),
        }

    linked_paths = set()
    for row in _rows(links_path, required=("link_target",)):
        target = _first(row, HEADER_ALIASES["link_target"])
        if target and _path(target).startswith("/repo/"):
            linked_paths.add(_repository_path(target, "Sampled links"))

    referral_paths: dict[str, int] = {}
    for row in _rows(
        referrals_path,
        required=("landing_page", "sessions"),
        allow_metadata_only=True,
    ):
        target = _first(row, HEADER_ALIASES["landing_page"])
        if not target or not _path(target).startswith("/repo/"):
            continue
        target_path = _repository_path(target, "First-party referrals")
        sessions = _integer(_first(row, HEADER_ALIASES["sessions"]))
        referral_paths[target_path] = referral_paths.get(target_path, 0) + sessions

    search_window = _search_window(filters_path)
    referral_window = _referral_window(referrals_path)

    return {
        "schema_version": SCHEMA_VERSION,
        "sources": {
            "search_analytics": {
                "file": pages_path.name,
                "filters_file": filters_path.name,
                "window": search_window,
                "scope": "Web Search exact pages matching /repo/",
            },
            "sampled_links": {
                "file": links_path.name,
                "window": links_window,
                "scope": "Search Console sampled top linked pages export",
            },
            "first_party_referrals": {
                "file": referrals_path.name,
                "window": referral_window,
                "scope": "GA4 repository landing-page referrals export",
            },
        },
        "search_analytics": search_rows,
        "sampled_link_paths": sorted(linked_paths),
        "first_party_referrals": referral_paths,
        "summary": {
            "search_urls_observed": len(search_rows),
            "search_clicks": sum(int(row["clicks"]) for row in search_rows.values()),
            "search_impressions": sum(int(row["impressions"]) for row in search_rows.values()),
            "linked_repository_urls_observed": len(linked_paths),
            "referred_repository_urls_observed": len(referral_paths),
            "referral_sessions": sum(referral_paths.values()),
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--links-window", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_dir = args.input_dir.resolve()
    payload = build_payload(
        pages_path=input_dir / "Pages.csv",
        links_path=input_dir / "gsc-top-linked-pages.csv",
        referrals_path=input_dir / "ga4-repo-referrals.csv",
        filters_path=input_dir / "Filtres.csv",
        links_window=args.links_window,
    )
    output = args.root.resolve() / OUTPUT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

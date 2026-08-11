"""Generate the evidence-first repository URL migration inventory."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "1.0.0"
PRODUCTION_SNAPSHOT = Path("data/derived/observatory/repository-production-snapshot.json")
EVIDENCE_REQUIREMENTS = (
    "url_inspection",
    "search_analytics",
    "sampled_links",
    "first_party_referrals",
    "internal_links",
    "sitemap",
    "content_review",
    "destination_equivalence",
)


def load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"Missing YAML front matter: {path}")
    _, frontmatter, _ = text.split("---", 2)
    loaded = yaml.safe_load(frontmatter)
    if not isinstance(loaded, dict):
        raise ValueError(f"Invalid YAML front matter: {path}")
    return loaded


def normalized_url(value: str) -> str:
    stripped = value.strip().strip("/")
    return f"/{stripped}/" if stripped else "/"


def evidence_placeholders() -> dict[str, dict[str, str]]:
    return {
        requirement: {"status": "not_collected", "source": "", "window": ""}
        for requirement in EVIDENCE_REQUIREMENTS
    }


def canonical_record(root: Path, page: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    params = load_frontmatter(page)
    repository_id = page.parent.name
    canonical_url = f"/repo/{repository_id}/"
    source_path = page.relative_to(root).as_posix()
    source_checksum = hashlib.sha256(page.read_bytes()).hexdigest()
    record = {
        "url": canonical_url,
        "url_type": "canonical",
        "repository_id": repository_id,
        "canonical_url": canonical_url,
        "source_path": source_path,
        "source_checksum": source_checksum,
        "differentiated_content": "pending_review",
        "destination_candidate": "",
        "proposed_disposition": "pending",
        "approval_status": "pending",
        "evidence": evidence_placeholders(),
    }
    aliases = []
    for alias in params.get("aliases", []):
        alias_record = copy.deepcopy(record)
        aliases.append(
            {
                **alias_record,
                "url": normalized_url(str(alias)),
                "url_type": "alias",
                "canonical_url": canonical_url,
                "source_checksum": source_checksum,
            }
        )
    return record, aliases


def load_production_snapshot(root: Path) -> dict[str, Any] | None:
    path = root / PRODUCTION_SNAPSHOT
    if not path.exists():
        return None
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Invalid production snapshot: {path}")
    return loaded


def build_inventory(root: Path) -> dict[str, Any]:
    repo_root = root / "content/repo"
    records: list[dict[str, Any]] = [
        {
            "url": "/repo/",
            "url_type": "index",
            "repository_id": None,
            "canonical_url": "/repo/",
            "source_path": "content/repo/_index.md",
            "source_checksum": hashlib.sha256((repo_root / "_index.md").read_bytes()).hexdigest(),
            "differentiated_content": "pending_review",
            "destination_candidate": "",
            "proposed_disposition": "pending",
            "approval_status": "pending",
            "evidence": evidence_placeholders(),
        }
    ]
    for page in sorted(repo_root.glob("*/index.md")):
        record, aliases = canonical_record(root, page)
        records.append(record)
        records.extend(aliases)

    records.sort(key=lambda item: item["url"])
    urls = [item["url"] for item in records]
    duplicates = sorted({url for url in urls if urls.count(url) > 1})
    if duplicates:
        raise ValueError(f"Duplicate repository URLs: {', '.join(duplicates)}")

    counts = {
        "index": sum(item["url_type"] == "index" for item in records),
        "canonical": sum(item["url_type"] == "canonical" for item in records),
        "alias": sum(item["url_type"] == "alias" for item in records),
        "total": len(records),
    }
    snapshot = load_production_snapshot(root)
    production_by_url = {record["url"]: record for record in (snapshot or {}).get("records", [])}
    for record in records:
        production = production_by_url.get(record["url"])
        if production:
            record["production"] = {
                "sitemap_status": "observed" if production["in_sitemap"] else "not_observed",
                "http_status": production["http_status"],
            }
            record["evidence"]["sitemap"] = {
                "status": "observed" if production["in_sitemap"] else "not_observed",
                "source": (snapshot or {}).get("sources", {}).get("sitemap", ""),
                "window": (snapshot or {}).get("captured_at", ""),
            }
        else:
            record["production"] = {
                "sitemap_status": "not_collected",
                "http_status": None,
            }
    production_counts = (snapshot or {}).get("counts", {})
    counts.update(
        {
            "production_sitemap": production_counts.get("sitemap_urls"),
            "production_http_200": production_counts.get("http_200"),
            "production_http_404": production_counts.get("http_404"),
            "production_only": production_counts.get("production_only"),
        }
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_from": "content/repo/",
        "production_snapshot": {
            "path": PRODUCTION_SNAPSHOT.as_posix(),
            "captured_at": (snapshot or {}).get("captured_at", ""),
            "site_origin": (snapshot or {}).get("site_origin", ""),
        },
        "evidence_requirements": list(EVIDENCE_REQUIREMENTS),
        "counts": counts,
        "records": records,
    }


def rendered_inventory(root: Path) -> str:
    return json.dumps(build_inventory(root), indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/derived/observatory/repository-url-inventory.json"),
    )
    parser.add_argument("--check", action="store_true", help="Fail when the inventory is stale.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    rendered = rendered_inventory(root)
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"Repository URL inventory is stale: {output}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

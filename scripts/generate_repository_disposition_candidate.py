"""Generate the evidence-backed repository migration disposition candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import yaml
from jsonschema import Draft202012Validator

SCHEMA_VERSION = "1.0.0"
INVENTORY_PATH = Path("data/derived/observatory/repository-url-inventory.json")
OUTPUT_PATH = Path("data/derived/observatory/repository-disposition-candidate.json")
SCHEMA_PATH = Path("data/schemas/repository-disposition-candidate.schema.json")
INPUT_PATHS = (
    Path("data/derived/observatory/repository-production-snapshot.json"),
    Path("data/derived/observatory/repository-external-evidence.json"),
    Path("data/derived/observatory/repository-url-inspection.json"),
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def _page_url(rendered_root: Path, page: Path) -> str:
    relative = page.relative_to(rendered_root).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return f"/{relative.removesuffix('index.html')}"
    return f"/{relative}"


def internal_link_counts(rendered_root: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for page in sorted(rendered_root.rglob("*.html")):
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        base = f"https://claracle.com{_page_url(rendered_root, page)}"
        for href in parser.links:
            target = urlparse(urljoin(base, href))
            if target.netloc not in {"", "claracle.com"}:
                continue
            path = f"/{target.path.strip('/')}/"
            if path.startswith("/repo/"):
                counts[path] += 1
    return counts


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    _, raw, _ = text.split("---", 2)
    loaded = yaml.safe_load(raw)
    if not isinstance(loaded, dict):
        raise ValueError(f"Invalid repository front matter: {path}")
    return loaded


def _differentiated(root: Path, record: dict[str, Any]) -> bool:
    if record["url_type"] == "index":
        return True
    if record["url_type"] == "alias":
        return False
    params = _frontmatter(root / record["source_path"])
    return (
        params.get("generated_by") == "observatory_repo_pages"
        and int(params.get("distinct_weekly_issues", 0)) >= 4
        and len(params.get("star_history", [])) >= 2
        and len(params.get("weekly_appearances", [])) >= 4
    )


def _observed_value(record: dict[str, Any]) -> bool:
    return (
        (record["external_metrics"]["search_impressions"] or 0) > 0
        or record["external_metrics"]["sampled_inbound_link"] is True
        or (record["external_metrics"]["referral_sessions"] or 0) > 0
    )


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inventory_evidence_sha256(inventory: dict[str, Any]) -> str:
    evidence = [
        {
            "url": record["url"],
            "url_type": record["url_type"],
            "canonical_url": record["canonical_url"],
            "source_checksum": record["source_checksum"],
            "production": record["production"],
            "external_metrics": record["external_metrics"],
            "inspection": record["inspection"],
        }
        for record in inventory["records"]
    ]
    encoded = json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_candidate(
    root: Path,
    rendered_root: Path,
    *,
    reviewed_at: date,
) -> dict[str, Any]:
    inventory = json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
    link_counts = internal_link_counts(rendered_root)
    records_by_url = {record["url"]: record for record in inventory["records"]}
    valuable_alias_targets = {
        record["canonical_url"]
        for record in inventory["records"]
        if record["url_type"] == "alias" and _observed_value(record)
    }

    candidates = []
    for record in inventory["records"]:
        differentiated = _differentiated(root, record)
        observed_value = _observed_value(record)
        destination = ""
        equivalence = "not_applicable"
        if record["url_type"] == "index":
            disposition = "keep"
            rationale = "Authoritative consolidated repository explorer."
        elif record["url_type"] == "alias" and observed_value:
            disposition = "redirect"
            destination = record["canonical_url"]
            equivalence = "equivalent"
            rationale = "Observed-value legacy alias has an identity-equivalent canonical URL."
        elif record["url_type"] == "canonical" and (
            (differentiated and observed_value) or record["url"] in valuable_alias_targets
        ):
            disposition = "keep"
            rationale = (
                "Repository-specific trend evidence has observed Google value."
                if observed_value
                else "Retained as the identity-equivalent destination for a valuable legacy alias."
            )
        else:
            disposition = "retire"
            equivalence = "none"
            rationale = (
                "No observed search, sampled-link, or referral value and no genuine replacement."
            )
        candidates.append(
            {
                "url": record["url"],
                "url_type": record["url_type"],
                "canonical_url": record["canonical_url"],
                "candidate_disposition": disposition,
                "destination_candidate": destination,
                "destination_equivalence": equivalence,
                "differentiated_content": differentiated,
                "internal_link_count": link_counts[record["url"]],
                "inspection_verdict": record["inspection"]["verdict"],
                "coverage_state": record["inspection"]["coverage_state"],
                "search_impressions": record["external_metrics"]["search_impressions"],
                "sampled_inbound_link": record["external_metrics"]["sampled_inbound_link"],
                "referral_sessions": record["external_metrics"]["referral_sessions"],
                "approval_status": "pending",
                "rationale": rationale,
            }
        )

    dispositions = Counter(record["candidate_disposition"] for record in candidates)
    url_digest = hashlib.sha256("\n".join(sorted(records_by_url)).encode("utf-8")).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "reviewed_at": reviewed_at.isoformat(),
        "reviewer": "SquadScope automated evidence review",
        "approval_authority": "jmservera",
        "approval_status": "pending",
        "inputs": {
            **{path.as_posix(): _file_sha256(root / path) for path in INPUT_PATHS},
            "inventory_evidence_sha256": _inventory_evidence_sha256(inventory),
        },
        "inventory_url_set_sha256": url_digest,
        "counts": {
            "total": len(candidates),
            "keep": dispositions["keep"],
            "redirect": dispositions["redirect"],
            "retire": dispositions["retire"],
            "pending_approval": sum(
                record["approval_status"] == "pending" for record in candidates
            ),
        },
        "records": candidates,
    }


def validate_candidate(
    candidate: dict[str, Any],
    inventory: dict[str, Any],
    *,
    schema_path: Path = SCHEMA_PATH,
) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(candidate)
    expected_urls = {record["url"] for record in inventory["records"]}
    actual_urls = {record["url"] for record in candidate.get("records", [])}
    if expected_urls != actual_urls or len(candidate.get("records", [])) != len(expected_urls):
        raise ValueError("Disposition candidate does not cover the current URL inventory")
    expected_digest = hashlib.sha256("\n".join(sorted(expected_urls)).encode("utf-8")).hexdigest()
    if candidate.get("inventory_url_set_sha256") != expected_digest:
        raise ValueError("Disposition candidate URL-set checksum is stale")
    dispositions = Counter(record["candidate_disposition"] for record in candidate["records"])
    if candidate["counts"]["total"] != len(candidate["records"]):
        raise ValueError("Disposition candidate total count is inconsistent")
    if candidate["counts"]["pending_approval"] != len(candidate["records"]):
        raise ValueError("Disposition candidate pending count is inconsistent")
    for disposition in ("keep", "redirect", "retire"):
        if candidate["counts"][disposition] != dispositions[disposition]:
            raise ValueError(f"Disposition candidate {disposition} count is inconsistent")
    records_by_url = {record["url"]: record for record in candidate["records"]}
    inventory_by_url = {record["url"]: record for record in inventory["records"]}
    valuable_alias_targets = {
        record["canonical_url"]
        for record in candidate["records"]
        if record["url_type"] == "alias" and record["candidate_disposition"] == "redirect"
    }
    for record in candidate["records"]:
        source = inventory_by_url[record["url"]]
        expected_evidence = {
            "url_type": source["url_type"],
            "canonical_url": source["canonical_url"],
            "inspection_verdict": source["inspection"]["verdict"],
            "coverage_state": source["inspection"]["coverage_state"],
            "search_impressions": source["external_metrics"]["search_impressions"],
            "sampled_inbound_link": source["external_metrics"]["sampled_inbound_link"],
            "referral_sessions": source["external_metrics"]["referral_sessions"],
        }
        for field, expected_value in expected_evidence.items():
            if record[field] != expected_value:
                raise ValueError(f"Candidate evidence mismatch for {record['url']}: {field}")
        value = (
            (record["search_impressions"] or 0) > 0
            or record["sampled_inbound_link"] is True
            or (record["referral_sessions"] or 0) > 0
        )
        if record["approval_status"] != "pending":
            raise ValueError("Disposition candidate cannot contain approved rows")
        if record["url_type"] == "index":
            expected = "keep"
        elif record["url_type"] == "alias" and value:
            expected = "redirect"
        elif record["url_type"] == "canonical" and (
            (record["differentiated_content"] and value) or record["url"] in valuable_alias_targets
        ):
            expected = "keep"
        else:
            expected = "retire"
        if record["candidate_disposition"] != expected:
            raise ValueError(f"Invalid candidate disposition for {record['url']}")
        expected_rationale = {
            "keep": (
                "Authoritative consolidated repository explorer."
                if record["url_type"] == "index"
                else (
                    "Repository-specific trend evidence has observed Google value."
                    if value
                    else "Retained as the identity-equivalent destination for a valuable legacy alias."
                )
            ),
            "redirect": "Observed-value legacy alias has an identity-equivalent canonical URL.",
            "retire": (
                "No observed search, sampled-link, or referral value and no genuine replacement."
            ),
        }[expected]
        if record["rationale"] != expected_rationale:
            raise ValueError(f"Invalid candidate rationale for {record['url']}")
        if expected == "redirect":
            destination = records_by_url.get(record["destination_candidate"])
            if (
                record["destination_candidate"] != record["canonical_url"]
                or record["destination_equivalence"] != "equivalent"
                or not destination
                or destination["candidate_disposition"] != "keep"
            ):
                raise ValueError(f"Invalid redirect destination for {record['url']}")
        elif record["destination_candidate"]:
            raise ValueError(f"Unexpected destination for {record['url']}")


def validate_freshness(root: Path, candidate: dict[str, Any]) -> None:
    for path in INPUT_PATHS:
        expected = candidate.get("inputs", {}).get(path.as_posix())
        if expected != _file_sha256(root / path):
            raise ValueError(f"Disposition candidate evidence is stale: {path}")
    inventory = json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
    if candidate["inputs"].get("inventory_evidence_sha256") != _inventory_evidence_sha256(
        inventory
    ):
        raise ValueError("Disposition candidate inventory evidence is stale")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--rendered-root", type=Path)
    parser.add_argument("--reviewed-at", type=date.fromisoformat)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    inventory = json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
    schema_path = root / SCHEMA_PATH
    output = root / OUTPUT_PATH
    if args.check:
        if not output.exists():
            raise SystemExit(f"Disposition candidate is missing: {OUTPUT_PATH}")
        candidate = json.loads(output.read_text(encoding="utf-8"))
        validate_candidate(candidate, inventory, schema_path=schema_path)
        validate_freshness(root, candidate)
        return 0
    if args.rendered_root is None or args.reviewed_at is None:
        raise SystemExit("--rendered-root and --reviewed-at are required when generating")
    payload = build_candidate(
        root,
        args.rendered_root.resolve(),
        reviewed_at=args.reviewed_at,
    )
    validate_candidate(payload, inventory, schema_path=schema_path)
    validate_freshness(root, payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

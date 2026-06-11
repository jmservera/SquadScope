from __future__ import annotations

import argparse
import csv
import re
import warnings
from pathlib import Path

import yaml

from scripts.topic_paths import analyzed_dir

FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n(.*)\Z", re.DOTALL)
WEEK_PATTERN = re.compile(r"^(?P<year>\d{4})-W(?P<week>\d{2})$")
SUMMARY_SUFFIX = "-summary.md"
ANALYSIS_SUFFIX = " Analysis"
REQUIRED_ANALYSIS_FIELDS = {
    "title",
    "date",
    "week",
    "year",
    "tags",
    "categories",
    "repos_featured",
    "stars_tracked",
    "top_repo",
    "quality_score",
    "summary",
}


class GenerationError(ValueError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Hugo weekly content page from an analyzed summary markdown file."
    )
    parser.add_argument(
        "summary",
        nargs="?",
        default=None,
        help="Path to data/analyzed/YYYY-WNN-summary.md. Defaults to the newest analyzed summary.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional explicit output path. Defaults to content/weekly/YYYY/WNN.md.",
    )
    return parser.parse_args()


def parse_week(value: str) -> tuple[int, int]:
    match = WEEK_PATTERN.fullmatch(value)
    if not match:
        raise GenerationError(f"Invalid week value: {value}")
    return int(match.group("year")), int(match.group("week"))


def week_from_summary_path(path: Path) -> tuple[int, int]:
    if not path.name.endswith(SUMMARY_SUFFIX):
        raise GenerationError(f"Invalid summary filename: {path.name}")
    return parse_week(path.name.removesuffix(SUMMARY_SUFFIX))


def find_latest_summary(root: Path, topic_id: str | None = None) -> Path:
    search_dir = analyzed_dir(topic_id)
    # When using default (relative) path, resolve via root for backward compat
    if topic_id is None:
        candidates = list(root.glob(f"data/analyzed/*{SUMMARY_SUFFIX}"))
    else:
        candidates = list(search_dir.glob(f"*{SUMMARY_SUFFIX}"))
    if not candidates:
        # Fallback: try the other approach
        candidates = list(search_dir.glob(f"*{SUMMARY_SUFFIX}")) if topic_id is None else list(root.glob(f"data/analyzed/*{SUMMARY_SUFFIX}"))
    if not candidates:
        raise GenerationError("No analyzed summaries found under data/analyzed/.")
    return max(candidates, key=week_from_summary_path)


def parse_scalar(value: str):
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in csv.reader([inner], skipinitialspace=True).__next__()]
    if value.startswith(('"', "'")) and value.endswith(('"', "'")):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value


def parse_frontmatter(document: str) -> tuple[dict[str, object], str]:
    match = FRONTMATTER_PATTERN.match(document)
    if not match:
        raise GenerationError("Summary is missing YAML frontmatter.")

    frontmatter_text, body = match.groups()
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        raise GenerationError(f"Invalid YAML frontmatter: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise GenerationError("Frontmatter must be a YAML mapping.")

    missing = REQUIRED_ANALYSIS_FIELDS.difference(frontmatter)
    if missing:
        raise GenerationError(f"Missing required analysis fields: {', '.join(sorted(missing))}")

    return frontmatter, body.strip() + "\n"


def normalize_title(title: str) -> str:
    if title.endswith(ANALYSIS_SUFFIX):
        return title[: -len(ANALYSIS_SUFFIX)]
    return title


def ensure_list(value: object, *, field_name: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise GenerationError(f"{field_name} must be a non-empty list of strings.")
    return value


def infer_output_path(week: str, root: Path) -> Path:
    year, week_number = parse_week(week)
    return root / "content" / "weekly" / str(year) / f"W{week_number:02d}.md"


def yaml_quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def optional_string(value: object) -> str:
    return "" if value is None else str(value)


def is_local_asset_path(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if value.startswith(("http://", "https://", "//")):
        return False
    asset_path = Path(value)
    if asset_path.is_absolute():
        return False
    if ".." in asset_path.parts:
        return False
    return True


def render_frontmatter(data: dict[str, object]) -> str:
    lines = [
        "---",
        f'title: {yaml_quote(str(data["title"]))}',
        f'date: {data["date"]}',
        f'week: {yaml_quote(str(data["week"]))}',
        f'tags: [{", ".join(yaml_quote(t) for t in data["tags"])}]',
        f'categories: [{", ".join(yaml_quote(c) for c in data["categories"])}]',
        f'repos_featured: {data["repos_featured"]}',
        f'stars_tracked: {data["stars_tracked"]}',
        f'top_repo: {yaml_quote(str(data["top_repo"]))}',
        f'summary: {yaml_quote(str(data["summary"]))}',
        "draft: false",
    ]

    # Cover image frontmatter (PaperMod convention)
    cover = data.get("cover")
    if cover and isinstance(cover, dict):
        lines.append("cover:")
        if cover.get("image"):
            lines.append(f'  image: {yaml_quote(str(cover["image"]))}')
        if cover.get("alt"):
            lines.append(f'  alt: {yaml_quote(str(cover["alt"]))}')
        if cover.get("caption"):
            lines.append(f'  caption: {yaml_quote(str(cover["caption"]))}')
        if cover.get("attribution"):
            lines.append(f'  attribution: {yaml_quote(str(cover["attribution"]))}')
        if cover.get("license"):
            lines.append(f'  license: {yaml_quote(str(cover["license"]))}')
        lines.append("  relative: true")

    # Explicit OG image override
    if data.get("og_image"):
        lines.append(f'og_image: {yaml_quote(str(data["og_image"]))}')

    lines.extend(["---", ""])
    return "\n".join(lines)


def transform_summary(frontmatter: dict[str, object], body: str) -> str:
    tags = ensure_list(frontmatter["tags"], field_name="tags")
    categories = ensure_list(frontmatter["categories"], field_name="categories")
    if "weekly" not in categories:
        categories = [*categories, "weekly"]

    page_frontmatter: dict[str, object] = {
        "title": normalize_title(str(frontmatter["title"])),
        "date": str(frontmatter["date"]),
        "week": str(frontmatter["week"]),
        "tags": tags,
        "categories": categories,
        "repos_featured": int(frontmatter["repos_featured"]),
        "stars_tracked": int(frontmatter["stars_tracked"]),
        "top_repo": str(frontmatter["top_repo"]),
        "summary": str(frontmatter["summary"]),
    }

    # Pass through cover image fields if present
    cover_image = frontmatter.get("cover_image") or frontmatter.get("cover", {}).get("image") if isinstance(frontmatter.get("cover"), dict) else frontmatter.get("cover_image")
    if cover_image:
        cover_alt = frontmatter.get("cover_alt") or frontmatter.get("cover", {}).get("alt", "") if isinstance(frontmatter.get("cover"), dict) else frontmatter.get("cover_alt", "")
        cover_attribution = frontmatter.get("cover_attribution")
        cover_license = frontmatter.get("cover_license")
        page_frontmatter["cover"] = {
            "image": str(cover_image),
            "alt": str(cover_alt) if cover_alt else "",
            "attribution": optional_string(cover_attribution),
            "license": optional_string(cover_license),
        }

    # Pass through OG image override — reject URLs to enforce no-hotlinking policy
    og_image = frontmatter.get("og_image")
    if og_image:
        if is_local_asset_path(og_image):
            page_frontmatter["og_image"] = str(og_image)
        else:
            warnings.warn(f"Skipping non-local og_image value: {og_image}", stacklevel=2)

    return render_frontmatter(page_frontmatter) + "\n" + body.lstrip()


def generate_content(summary_path: Path, output_path: Path | None = None) -> Path:
    root = Path.cwd()
    document = summary_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(document)
    target_path = output_path or infer_output_path(str(frontmatter["week"]), root)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(transform_summary(frontmatter, body), encoding="utf-8")
    return target_path


def main() -> int:
    args = parse_args()
    root = Path.cwd()
    summary_path = Path(args.summary) if args.summary else find_latest_summary(root)
    output_path = Path(args.output) if args.output else None

    if not summary_path.exists():
        raise SystemExit(f"Summary file not found: {summary_path}")

    written_path = generate_content(summary_path, output_path)
    print(f"Generated {written_path} from {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

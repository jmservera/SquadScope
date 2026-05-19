from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

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
    frontmatter: dict[str, object] = {}
    for line in frontmatter_text.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise GenerationError(f"Malformed frontmatter line: {line}")
        key, raw_value = line.split(":", 1)
        frontmatter[key.strip()] = parse_scalar(raw_value)

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


def render_frontmatter(data: dict[str, object]) -> str:
    lines = [
        "---",
        f'title: {yaml_quote(str(data["title"]))}',
        f'date: {data["date"]}',
        f'week: {yaml_quote(str(data["week"]))}',
        f'tags: [{", ".join(data["tags"])}]',
        f'categories: [{", ".join(data["categories"])}]',
        f'repos_featured: {data["repos_featured"]}',
        f'stars_tracked: {data["stars_tracked"]}',
        f'top_repo: {yaml_quote(str(data["top_repo"]))}',
        f'summary: {yaml_quote(str(data["summary"]))}',
        "draft: false",
        "---",
        "",
    ]
    return "\n".join(lines)


def transform_summary(frontmatter: dict[str, object], body: str) -> str:
    tags = ensure_list(frontmatter["tags"], field_name="tags")
    categories = ensure_list(frontmatter["categories"], field_name="categories")
    if "weekly" not in categories:
        categories = [*categories, "weekly"]

    page_frontmatter = {
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

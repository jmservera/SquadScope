#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.analysis_gate as analysis_gate

SUMMARY_SUFFIX = "-summary.md"
WEEK_PATTERN = re.compile(r"^(?P<year>\d{4})-W(?P<week>\d{2})$")
MONTHLY_SECTIONS = [
    "Month Overview",
    "Top Repos This Month",
    "Trends Observed",
    "Key Takeaways",
]
YEARLY_SECTIONS = [
    "Year in Review",
    "Biggest Trends",
    "Most Impactful Repos",
    "What Changed",
    "Predictions Review",
]
MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}
SECTION_HEADING_PATTERN = re.compile(r"(?m)^##\s+(.+?)\s*$")
SUBSECTION_HEADING_TEMPLATE = r"(?ms)^###\s+{title}\s*$\n(.*?)(?=^###\s+|\Z)"


class RollupError(ValueError):
    pass


@dataclass(frozen=True)
class WeeklySummary:
    source_path: Path
    title: str
    date: object
    week: str
    year: int
    month: int
    tags: tuple[str, ...]
    repos_featured: int
    top_repo: str
    summary: str
    signal: str
    noise: str
    gaps: str
    conclusion: str

    @property
    def week_number(self) -> int:
        match = WEEK_PATTERN.fullmatch(self.week)
        if not match:
            raise RollupError(f"Invalid week slug: {self.week}")
        return int(match.group("week"))

    @property
    def week_title(self) -> str:
        return f"Week {self.week_number}, {self.year}"

    @property
    def week_link(self) -> str:
        return f"/weekly/{self.year}/W{self.week_number:02d}/"

    @property
    def month_slug(self) -> str:
        return f"{self.year}-{self.month:02d}"

    @property
    def month_title(self) -> str:
        return f"{MONTH_NAMES[self.month]} {self.year}"

    @property
    def month_link(self) -> str:
        return f"/monthly/{self.year}/{self.month:02d}/"


@dataclass(frozen=True)
class RollupEntry:
    marker: str
    text: str


@dataclass(frozen=True)
class RollupPage:
    path: Path
    frontmatter: dict[str, Any]
    sections: dict[str, list[RollupEntry]]
    section_order: list[str]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate append-only monthly and yearly rollups from weekly analyses.")
    parser.add_argument("--analyzed-dir", type=Path, default=Path("data/analyzed"), help="Directory containing weekly summary markdown files.")
    parser.add_argument("--content-root", type=Path, default=Path("content"), help="Root content directory for generated rollups.")
    return parser.parse_args(argv)


def yaml_quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def yaml_value(value: Any) -> str:
    if isinstance(value, str):
        return yaml_quote(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        rendered = ", ".join(yaml_value(item) for item in value)
        return f"[{rendered}]"
    return str(value)


def render_frontmatter(frontmatter: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {yaml_value(value)}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def split_sections(body: str) -> tuple[str, dict[str, str]]:
    matches = list(SECTION_HEADING_PATTERN.finditer(body))
    if not matches:
        return body.rstrip(), {}

    intro = body[: matches[0].start()].rstrip()
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group(1).strip()] = body[start:end].strip("\n")
    return intro, sections


def get_section_text(body: str, heading: str) -> str:
    matches = list(SECTION_HEADING_PATTERN.finditer(body))
    for index, match in enumerate(matches):
        if match.group(1).strip() != heading:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        return body[start:end].strip()
    return ""


def get_subsection_text(section_body: str, heading: str) -> str:
    pattern = re.compile(SUBSECTION_HEADING_TEMPLATE.format(title=re.escape(heading)))
    match = pattern.search(section_body)
    return re.sub(r"\s+", " ", match.group(1).strip()) if match else ""


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def repo_markdown(repo: str) -> str:
    return f"[{repo}](https://github.com/{repo})"


def load_summary(path: Path) -> WeeklySummary:
    frontmatter, body = analysis_gate.extract_frontmatter(path.read_text(encoding="utf-8"))
    week = str(frontmatter.get("week", ""))
    match = WEEK_PATTERN.fullmatch(week)
    if not match:
        raise RollupError(f"Invalid weekly summary filename: {path.name}")

    date = analysis_gate.parse_datetime(frontmatter["date"])
    month = date.month
    trend_analysis = get_section_text(body, "Trend Analysis")
    signal = get_subsection_text(trend_analysis, "Signal")
    noise = get_subsection_text(trend_analysis, "Noise")
    gaps = get_subsection_text(get_section_text(body, "What's Missing"), "Gaps")
    conclusion = normalize_text(get_section_text(body, "Conclusion"))

    return WeeklySummary(
        source_path=path,
        title=str(frontmatter["title"]),
        date=date,
        week=week,
        year=int(frontmatter["year"]),
        month=month,
        tags=tuple(str(tag) for tag in frontmatter.get("tags", [])),
        repos_featured=int(frontmatter["repos_featured"]),
        top_repo=str(frontmatter["top_repo"]),
        summary=normalize_text(str(frontmatter["summary"])),
        signal=signal,
        noise=noise,
        gaps=gaps,
        conclusion=conclusion,
    )


def load_weekly_summaries(analyzed_dir: Path) -> list[WeeklySummary]:
    summaries = [load_summary(path) for path in sorted(analyzed_dir.glob(f"*{SUMMARY_SUFFIX}"))]
    if not summaries:
        raise RollupError(f"No weekly summaries found in {analyzed_dir}")
    return sorted(summaries, key=lambda item: (item.date, item.week))


def monthly_entries(weekly: WeeklySummary, tags_counter: Counter[str]) -> dict[str, RollupEntry]:
    common_tags = ", ".join(tag for tag, _ in tags_counter.most_common(3)) or "none yet"
    repo_link = repo_markdown(weekly.top_repo)
    page_link = f"[{weekly.week_title}]({weekly.week_link})"
    marker = f"### Week {weekly.week}"
    return {
        "Month Overview": RollupEntry(
            marker=marker,
            text=(
                f"{marker} — {page_link}\n"
                f"- Summary: {weekly.summary}\n"
                f"- Repositories featured this week: {weekly.repos_featured}\n"
                f"- Recurring themes so far: {common_tags}."
            ),
        ),
        "Top Repos This Month": RollupEntry(
            marker=marker,
            text=(
                f"{marker} — {page_link}\n"
                f"- {repo_link} led the published weekly analysis for {weekly.week}.\n"
                f"- Detailed breakdown: {page_link}."
            ),
        ),
        "Trends Observed": RollupEntry(
            marker=marker,
            text=(
                f"{marker} — {page_link}\n"
                f"- Signal: {weekly.signal}\n"
                f"- Noise: {weekly.noise}"
            ),
        ),
        "Key Takeaways": RollupEntry(
            marker=marker,
            text=(
                f"{marker} — {page_link}\n"
                f"- Gap to watch: {weekly.gaps}\n"
                f"- Closing read: {weekly.conclusion}"
            ),
        ),
    }


def yearly_entries(weekly: WeeklySummary, tags_counter: Counter[str]) -> dict[str, RollupEntry]:
    common_tags = ", ".join(tag for tag, _ in tags_counter.most_common(5)) or "none yet"
    repo_link = repo_markdown(weekly.top_repo)
    month_link = f"[{weekly.month_title}]({weekly.month_link})"
    week_link = f"[{weekly.week_title}]({weekly.week_link})"
    marker = f"### {weekly.month_title} update — {weekly.week}"
    return {
        "Year in Review": RollupEntry(
            marker=marker,
            text=(
                f"{marker}\n"
                f"- {month_link} gained a new weekly signal via {week_link}.\n"
                f"- Snapshot: {weekly.summary}"
            ),
        ),
        "Biggest Trends": RollupEntry(
            marker=marker,
            text=(
                f"{marker}\n"
                f"- Themes in rotation: {common_tags}.\n"
                f"- Signal from {week_link}: {weekly.signal}"
            ),
        ),
        "Most Impactful Repos": RollupEntry(
            marker=marker,
            text=(
                f"{marker}\n"
                f"- Featured repo: {repo_link}.\n"
                f"- Month summary: {month_link}."
            ),
        ),
        "What Changed": RollupEntry(
            marker=marker,
            text=(
                f"{marker}\n"
                f"- Friction noted in {week_link}: {weekly.noise}"
            ),
        ),
        "Predictions Review": RollupEntry(
            marker=marker,
            text=(
                f"{marker}\n"
                f"- Open question carried forward from {month_link}: {weekly.gaps}\n"
                f"- Working takeaway: {weekly.conclusion}"
            ),
        ),
    }


def build_monthly_pages(summaries: list[WeeklySummary], content_root: Path) -> list[RollupPage]:
    grouped: dict[tuple[int, int], list[WeeklySummary]] = defaultdict(list)
    for summary in summaries:
        grouped[(summary.year, summary.month)].append(summary)

    pages: list[RollupPage] = []
    for (year, month), items in sorted(grouped.items()):
        items = sorted(items, key=lambda item: (item.date, item.week))
        tags_counter: Counter[str] = Counter(tag for item in items for tag in item.tags)
        page_entries: dict[str, list[RollupEntry]] = {section: [] for section in MONTHLY_SECTIONS}
        for item in items:
            for section, entry in monthly_entries(item, tags_counter).items():
                page_entries[section].append(entry)
        pages.append(
            RollupPage(
                path=content_root / "monthly" / str(year) / f"{month:02d}.md",
                frontmatter={
                    "title": f"{MONTH_NAMES[month]} {year} Rollup",
                    "date": items[-1].date.isoformat(),
                    "month": month,
                    "year": year,
                    "categories": ["monthly"],
                    "weeks_covered": [item.week for item in items],
                    "total_repos_featured": sum(item.repos_featured for item in items),
                },
                sections=page_entries,
                section_order=MONTHLY_SECTIONS,
            )
        )
    return pages


def build_yearly_pages(summaries: list[WeeklySummary], content_root: Path) -> list[RollupPage]:
    grouped: dict[int, list[WeeklySummary]] = defaultdict(list)
    for summary in summaries:
        grouped[summary.year].append(summary)

    pages: list[RollupPage] = []
    for year, items in sorted(grouped.items()):
        items = sorted(items, key=lambda item: (item.date, item.week))
        tags_counter: Counter[str] = Counter(tag for item in items for tag in item.tags)
        page_entries: dict[str, list[RollupEntry]] = {section: [] for section in YEARLY_SECTIONS}
        for item in items:
            for section, entry in yearly_entries(item, tags_counter).items():
                page_entries[section].append(entry)
        months_covered = sorted({item.month_slug for item in items})
        pages.append(
            RollupPage(
                path=content_root / "yearly" / f"{year}.md",
                frontmatter={
                    "title": f"{year} Yearly Rollup",
                    "date": items[-1].date.isoformat(),
                    "year": year,
                    "categories": ["yearly"],
                    "months_covered": months_covered,
                },
                sections=page_entries,
                section_order=YEARLY_SECTIONS,
            )
        )
    return pages


def merge_sections(path: Path, section_order: list[str], new_entries: dict[str, list[RollupEntry]]) -> str:
    intro = ""
    existing_sections: dict[str, str] = {}
    if path.exists():
        existing_text = path.read_text(encoding="utf-8")
        try:
            _, body = analysis_gate.extract_frontmatter(existing_text)
        except ValueError:
            body = ""
        intro, existing_sections = split_sections(body)

    rendered_sections: list[str] = []
    for section in section_order:
        content = existing_sections.get(section, "")
        for entry in new_entries[section]:
            if entry.marker in content:
                continue
            content = f"{content.rstrip()}\n\n{entry.text}" if content.strip() else entry.text
        section_body = content.strip()
        if not section_body:
            section_body = "_No updates yet._"
        rendered_sections.append(f"## {section}\n\n{section_body}")

    if intro.strip():
        return intro.rstrip() + "\n\n" + "\n\n".join(rendered_sections) + "\n"
    return "\n\n".join(rendered_sections) + "\n"


def write_rollup(page: RollupPage) -> None:
    page.path.parent.mkdir(parents=True, exist_ok=True)
    body = merge_sections(page.path, page.section_order, page.sections)
    page.path.write_text(render_frontmatter(page.frontmatter) + body, encoding="utf-8")


def generate_rollups(analyzed_dir: Path, content_root: Path) -> list[Path]:
    summaries = load_weekly_summaries(analyzed_dir)
    written: list[Path] = []
    for page in [*build_monthly_pages(summaries, content_root), *build_yearly_pages(summaries, content_root)]:
        write_rollup(page)
        written.append(page.path)
    return written


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    written = generate_rollups(args.analyzed_dir, args.content_root)
    for path in written:
        print(f"Generated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

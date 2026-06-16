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
from scripts.generate_yearly_narrative import build_yearly_narrative_pages
from scripts.month_synthesis import ensure_month_synthesis

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_SUFFIX = "-summary.md"
WEEK_PATTERN = re.compile(r"^(?P<year>\d{4})-W(?P<week>\d{2})$")
REPO_LINK_PATTERN = re.compile(r"https://github\.com/(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")
NO_UPDATES_PLACEHOLDER = "_No updates yet._"
MONTHLY_SECTIONS = [
    "Month Synthesis",
    "Month Overview",
    "Top Repos This Month",
    "Trends Observed",
    "Key Takeaways",
]
YEARLY_SECTIONS = [
    "Year in Review",
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
    featured_repos: tuple[str, ...]
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
    replace_existing_sections: bool = False
    preserve_unknown_sections: bool = True
    replace_sections: frozenset[str] = frozenset()


ACRONYMS = {"ai", "mcp", "ci", "cd", "api", "sdk", "llm", "rag", "ml"}


def _titlecase_tag(tag: str) -> str:
    words = tag.replace("-", " ").split()
    return " ".join(w.upper() if w.lower() in ACRONYMS else w.title() for w in words)


def generate_monthly_title(synthesis: Any, month: int, year: int) -> str:
    """Generate an SEO-friendly editorial title (max 70 chars) from synthesis data."""
    month_year = f"{MONTH_NAMES[month]} {year}"
    accel = [_titlecase_tag(t) for t in synthesis.accelerating_themes[:2]]
    weak = [_titlecase_tag(t) for t in synthesis.weakening_themes[:1]]
    themes = [_titlecase_tag(t) for t in synthesis.themes[:2]]

    if len(accel) >= 2:
        title = f"{accel[0]} and {accel[1]} Surge — {month_year}"
    elif accel and weak:
        title = f"{accel[0]} Surges While {weak[0]} Fades — {month_year}"
    elif accel:
        title = f"{accel[0]} Takes Center Stage — {month_year}"
    elif len(themes) >= 2:
        title = f"{themes[0]} and {themes[1]} Define the Month — {month_year}"
    elif themes:
        title = f"{themes[0]} Leads the Month — {month_year}"
    else:
        title = f"Trends Shift and Settle — {month_year}"

    if len(title) > 70:
        if accel:
            title = f"{accel[0]} Surges — {month_year}"
        elif themes:
            title = f"{themes[0]} Leads — {month_year}"
        if len(title) > 70:
            title = title[:67] + "…"

    return title


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate append-only monthly and yearly rollups from weekly analyses. Defaults resolve from the repository root."
    )
    parser.add_argument(
        "--analyzed-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "analyzed",
        help="Directory containing weekly summary markdown files.",
    )
    parser.add_argument(
        "--content-root",
        type=Path,
        default=PROJECT_ROOT / "content",
        help="Root content directory for generated rollups.",
    )
    parser.add_argument(
        "--rolling",
        action="store_true",
        default=False,
        help="Generate the rolling 4-week context report after rollups.",
    )
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
    lines.extend(["---", "", ""])
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


def extract_featured_repos(body: str, top_repo: str) -> tuple[str, ...]:
    repos = [top_repo]
    seen = {top_repo}
    for match in REPO_LINK_PATTERN.finditer(body):
        repo = match.group("repo")
        if repo in seen:
            continue
        seen.add(repo)
        repos.append(repo)
    return tuple(repos)


def load_summary(path: Path) -> WeeklySummary:
    frontmatter, body = analysis_gate.extract_frontmatter(path.read_text(encoding="utf-8"))
    week = str(frontmatter.get("week", ""))
    match = WEEK_PATTERN.fullmatch(week)
    if not match:
        raise RollupError(f"Invalid weekly summary filename: {path.name}")

    date = analysis_gate.parse_datetime(frontmatter["date"])
    month = date.month

    # New structure: try new heading names first, fall back to old for backward compat
    signal_noise_section = get_section_text(body, "Signal & Noise")
    if signal_noise_section:
        signal = normalize_text(signal_noise_section)
        noise = ""
    else:
        trend_analysis = get_section_text(body, "Trend Analysis")
        signal = get_subsection_text(trend_analysis, "Signal")
        noise = get_subsection_text(trend_analysis, "Noise")

    blind_spots = get_section_text(body, "Blind Spots")
    if blind_spots:
        gaps = normalize_text(blind_spots)
    else:
        gaps = get_subsection_text(get_section_text(body, "What's Missing"), "Gaps")

    week_ahead = get_section_text(body, "The Week Ahead")
    if week_ahead:
        conclusion = normalize_text(week_ahead)
    else:
        conclusion = normalize_text(get_section_text(body, "Conclusion"))
    top_repo = str(frontmatter["top_repo"])

    return WeeklySummary(
        source_path=path,
        title=str(frontmatter["title"]),
        date=date,
        week=week,
        year=int(frontmatter["year"]),
        month=month,
        tags=tuple(str(tag) for tag in frontmatter.get("tags", [])),
        repos_featured=int(frontmatter["repos_featured"]),
        top_repo=top_repo,
        featured_repos=extract_featured_repos(body, top_repo),
        summary=normalize_text(str(frontmatter["summary"])),
        signal=signal,
        noise=noise,
        gaps=gaps,
        conclusion=conclusion,
    )


def load_weekly_summaries(analyzed_dir: Path) -> list[WeeklySummary]:
    summaries = [load_summary(path) for path in sorted(analyzed_dir.glob(f"*{SUMMARY_SUFFIX}"))]
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
                f"- Signal: {weekly.signal}"
                + (f"\n- Noise: {weekly.noise}" if weekly.noise else "")
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


def _build_monthly_crosslinks(year: int, _month: int, items: list[WeeklySummary]) -> str:
    """Build navigation cross-links for a monthly page."""
    links = []
    links.append(f"[{year} Year in Review](/yearly/{year}/)")
    for item in items:
        links.append(f"[{item.week_title}]({item.week_link})")
    return f"*Part of {links[0]}* · Weekly: {' · '.join(links[1:])}\n"


def build_monthly_pages(summaries: list[WeeklySummary], content_root: Path, analyzed_dir: Path) -> list[RollupPage]:
    grouped: dict[tuple[int, int], list[WeeklySummary]] = defaultdict(list)
    for summary in summaries:
        grouped[(summary.year, summary.month)].append(summary)

    pages: list[RollupPage] = []
    for (year, month), items in sorted(grouped.items()):
        items = sorted(items, key=lambda item: (item.date, item.week))
        tags_counter: Counter[str] = Counter()
        page_entries: dict[str, list[RollupEntry]] = {section: [] for section in MONTHLY_SECTIONS}

        synthesis = ensure_month_synthesis(items, analyzed_dir)

        crosslinks = _build_monthly_crosslinks(year, month, items)
        synthesis_text = crosslinks + "\n" + synthesis.narrative
        if synthesis.trend_arc:
            synthesis_text += f"\n\n### Trend Arc\n\n{synthesis.trend_arc}"
        page_entries["Month Synthesis"].append(
            RollupEntry(marker="month-synthesis", text=synthesis_text)
        )

        for item in items:
            tags_counter.update(item.tags)
            for section, entry in monthly_entries(item, tags_counter).items():
                page_entries[section].append(entry)

        title = generate_monthly_title(synthesis, month, year)

        pages.append(
            RollupPage(
                path=content_root / "monthly" / str(year) / f"{month:02d}.md",
                frontmatter={
                    "title": title,
                    "date": items[-1].date.isoformat(),
                    "month": month,
                    "year": year,
                    "categories": ["monthly"],
                    "weeks_covered": [item.week for item in items],
                    "total_repos_featured": len({repo for item in items for repo in item.featured_repos}),
                    "summary": synthesis.summary,
                    "themes": list(synthesis.themes),
                    "persistent_themes": list(synthesis.persistent_themes),
                    "accelerating_themes": list(synthesis.accelerating_themes),
                    "weakening_themes": list(synthesis.weakening_themes),
                    "key_gaps": list(synthesis.key_gaps),
                    "top_repos": list(synthesis.top_repos),
                },
                sections=page_entries,
                section_order=MONTHLY_SECTIONS,
                replace_sections=frozenset({"Month Synthesis"}),
            )
        )
    return pages


def build_yearly_pages(summaries: list[WeeklySummary], content_root: Path) -> list[RollupPage]:
    pages: list[RollupPage] = []
    target_years = sorted({summary.year for summary in summaries})
    for page in build_yearly_narrative_pages(content_root, target_years):
        pages.append(
            RollupPage(
                path=page.path,
                frontmatter=page.frontmatter,
                sections={
                    "Year in Review": [RollupEntry(marker=f"{page.year}-year-in-review", text=page.narrative)],
                },
                section_order=YEARLY_SECTIONS,
                replace_existing_sections=True,
                preserve_unknown_sections=False,
            )
        )
    return pages


def merge_sections(
    path: Path,
    section_order: list[str],
    new_entries: dict[str, list[RollupEntry]],
    *,
    replace_existing_sections: bool = False,
    preserve_unknown_sections: bool = True,
    replace_sections: frozenset[str] = frozenset(),
) -> str:
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
        if replace_existing_sections or section in replace_sections:
            content = ""
        else:
            content = existing_sections.get(section, "")
        if content.strip() == NO_UPDATES_PLACEHOLDER:
            content = ""
        for entry in new_entries[section]:
            if entry.marker in content:
                continue
            content = f"{content.rstrip()}\n\n{entry.text}" if content.strip() else entry.text
        section_body = content.strip() or NO_UPDATES_PLACEHOLDER
        rendered_sections.append(f"## {section}\n\n{section_body}")

    if preserve_unknown_sections:
        for section, content in existing_sections.items():
            if section in section_order:
                continue
            section_body = content.strip() or NO_UPDATES_PLACEHOLDER
            rendered_sections.append(f"## {section}\n\n{section_body}")

    if intro.strip():
        return intro.rstrip() + "\n\n" + "\n\n".join(rendered_sections) + "\n"
    return "\n\n".join(rendered_sections) + "\n"


def write_rollup(page: RollupPage) -> None:
    page.path.parent.mkdir(parents=True, exist_ok=True)
    body = merge_sections(
        page.path,
        page.section_order,
        page.sections,
        replace_existing_sections=page.replace_existing_sections,
        preserve_unknown_sections=page.preserve_unknown_sections,
        replace_sections=page.replace_sections,
    )
    page.path.write_text(render_frontmatter(page.frontmatter) + body, encoding="utf-8")


def generate_rollups(analyzed_dir: Path, content_root: Path) -> list[Path]:
    summaries = load_weekly_summaries(analyzed_dir)
    if not summaries:
        return []

    written: list[Path] = []
    monthly_pages = build_monthly_pages(summaries, content_root, analyzed_dir)
    for page in monthly_pages:
        write_rollup(page)
        written.append(page.path)

    for page in build_yearly_pages(summaries, content_root):
        write_rollup(page)
        written.append(page.path)
    return written


ROLLING_SECTIONS = [
    "Active Trends",
    "Trend Velocity",
    "Open Predictions",
    "Noise Patterns",
]

VELOCITY_LABELS = ("accelerating", "new", "decelerating", "dying")


def _load_weekly_content(content_root: Path) -> list[WeeklySummary]:
    """Load weekly summaries directly from content/weekly/ (published pages).

    Falls back to data/analyzed/ format. Handles content/weekly files that
    may lack 'year' frontmatter by extracting it from the 'week' field.
    """
    weekly_dir = content_root / "weekly"
    if not weekly_dir.exists():
        return []
    paths = sorted(weekly_dir.rglob("W*.md"))
    summaries: list[WeeklySummary] = []
    for path in paths:
        if path.name == "_index.md":
            continue
        try:
            summaries.append(_load_weekly_summary(path))
        except (RollupError, KeyError, ValueError):
            continue
    return sorted(summaries, key=lambda s: (s.year, s.week_number))


def _load_weekly_summary(path: Path) -> WeeklySummary:
    """Load a weekly summary from content/weekly/, tolerating missing 'year'."""
    frontmatter, body = analysis_gate.extract_frontmatter(path.read_text(encoding="utf-8"))
    week = str(frontmatter.get("week", ""))
    match = WEEK_PATTERN.fullmatch(week)
    if not match:
        raise RollupError(f"Invalid week slug in {path.name}")

    year = int(frontmatter.get("year", match.group("year")))
    date = analysis_gate.parse_datetime(frontmatter["date"])

    signal_noise_section = get_section_text(body, "Signal & Noise")
    if signal_noise_section:
        signal = normalize_text(signal_noise_section)
        noise = ""
    else:
        trend_analysis = get_section_text(body, "Trend Analysis")
        signal = get_subsection_text(trend_analysis, "Signal")
        noise = get_subsection_text(trend_analysis, "Noise")

    # Pull structured noise from frontmatter if available (newer format)
    signal_noise_fm = frontmatter.get("signal_noise")
    if signal_noise_fm and isinstance(signal_noise_fm, dict):
        noise_items = signal_noise_fm.get("noise", [])
        if noise_items and isinstance(noise_items, list):
            noise = "; ".join(str(n) for n in noise_items)

    blind_spots = get_section_text(body, "Blind Spots")
    if blind_spots:
        gaps = normalize_text(blind_spots)
    else:
        gaps = get_subsection_text(get_section_text(body, "What's Missing"), "Gaps")

    week_ahead = get_section_text(body, "The Week Ahead")
    if week_ahead:
        conclusion = normalize_text(week_ahead)
    else:
        conclusion = normalize_text(get_section_text(body, "Conclusion"))

    top_repo = str(frontmatter.get("top_repo", ""))

    return WeeklySummary(
        source_path=path,
        title=str(frontmatter.get("title", "")),
        date=date,
        week=week,
        year=year,
        month=date.month,
        tags=tuple(str(tag) for tag in frontmatter.get("tags", [])),
        repos_featured=int(frontmatter.get("repos_featured", 0)),
        top_repo=top_repo,
        featured_repos=extract_featured_repos(body, top_repo) if top_repo else (),
        summary=normalize_text(str(frontmatter.get("summary", ""))),
        signal=signal,
        noise=noise,
        gaps=gaps,
        conclusion=conclusion,
    )


def _classify_velocity(tags_by_week: list[tuple[str, set[str]]]) -> dict[str, str]:
    """Classify trend velocity based on tag presence across weeks.

    Returns a mapping of tag -> velocity label.
    """
    if len(tags_by_week) < 2:
        all_tags = set()
        for _, tags in tags_by_week:
            all_tags.update(tags)
        return {tag: "new" for tag in all_tags}

    all_tags: set[str] = set()
    for _, tags in tags_by_week:
        all_tags.update(tags)

    velocity: dict[str, str] = {}
    for tag in sorted(all_tags):
        presence = [tag in tags for _, tags in tags_by_week]
        first_seen = next((i for i, p in enumerate(presence) if p), len(presence))
        last_seen = next(
            (len(presence) - 1 - i for i, p in enumerate(reversed(presence)) if p),
            0,
        )

        if first_seen >= len(presence) - 1:
            velocity[tag] = "new"
        elif last_seen < len(presence) - 2:
            velocity[tag] = "dying"
        elif sum(presence[len(presence) // 2 :]) >= sum(presence[: len(presence) // 2]):
            velocity[tag] = "accelerating"
        else:
            velocity[tag] = "decelerating"
    return velocity


def _synthesize_rolling_report(summaries: list[WeeklySummary]) -> str:
    """Synthesize a compact rolling report from up to 4 weekly summaries."""
    week_labels = [f"W{s.week_number}" for s in summaries]
    current_week = summaries[-1].week

    # Frontmatter
    lines = [
        "---",
        "title: Rolling 4-Week Context",
        f"updated: {current_week}",
        f"weeks: [{', '.join(week_labels)}]",
        "---",
        "",
    ]

    # Active Trends: synthesize from signals across weeks
    lines.append("## Active Trends")
    lines.append("")
    seen_signals: list[str] = []
    for s in summaries:
        if s.signal and s.signal not in seen_signals:
            # Truncate long signals to keep report compact
            signal_text = s.signal[:200] + "…" if len(s.signal) > 200 else s.signal
            seen_signals.append(signal_text)
    # Keep only most recent/relevant signals (last 4-5)
    for signal in seen_signals[-5:]:
        lines.append(f"- {signal}")
    lines.append("")

    # Trend Velocity: classify tags by presence pattern
    lines.append("## Trend Velocity")
    lines.append("")
    tags_by_week = [(s.week, set(s.tags)) for s in summaries]
    velocity = _classify_velocity(tags_by_week)
    for label in VELOCITY_LABELS:
        tags_for_label = [t for t, v in velocity.items() if v == label]
        if tags_for_label:
            lines.append(f"- **{label.capitalize()}:** {', '.join(tags_for_label)}")
    lines.append("")

    # Open Predictions: synthesize from conclusions/gaps
    lines.append("## Open Predictions")
    lines.append("")
    for s in summaries[-3:]:
        if s.gaps:
            gap_text = s.gaps[:150] + "…" if len(s.gaps) > 150 else s.gaps
            lines.append(f"- [W{s.week_number}] {gap_text}")
    lines.append("")

    # Noise Patterns: synthesize from noise fields
    lines.append("## Noise Patterns")
    lines.append("")
    seen_noise: list[str] = []
    for s in summaries:
        if s.noise and s.noise not in seen_noise:
            noise_text = s.noise[:200] + "…" if len(s.noise) > 200 else s.noise
            seen_noise.append(noise_text)
    for noise in seen_noise[-4:]:
        lines.append(f"- {noise}")
    if not seen_noise:
        lines.append("- No distinct noise patterns isolated in structured data.")
    lines.append("")

    return "\n".join(lines)


def generate_rolling_report(content_root: Path) -> Path | None:
    """Generate a rolling last-4-weeks report from content/weekly/.

    Reads the most recent 4 weekly summaries, synthesizes them into a compact
    context report, and writes to content/rolling/last-month.md (overwritten
    each week).

    Returns the path written, or None if insufficient data.
    """
    summaries = _load_weekly_content(content_root)
    if not summaries:
        return None

    # Take the last 4 weeks
    recent = summaries[-4:]
    if not recent:
        return None

    report = _synthesize_rolling_report(recent)

    rolling_dir = content_root / "rolling"
    rolling_dir.mkdir(parents=True, exist_ok=True)
    output_path = rolling_dir / "last-month.md"
    output_path.write_text(report, encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    written = generate_rollups(args.analyzed_dir, args.content_root)

    if args.rolling:
        rolling_path = generate_rolling_report(args.content_root)
        if rolling_path:
            written.append(rolling_path)
        else:
            print("No weekly content found for rolling report.", file=sys.stderr)

    if not written:
        print(f"No weekly summaries found in {args.analyzed_dir}; skipping rollup generation.", file=sys.stderr)
        return 0
    for path in written:
        print(f"Generated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

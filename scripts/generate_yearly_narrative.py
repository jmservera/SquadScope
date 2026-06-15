#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.analysis_gate as analysis_gate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTENT_ROOT = PROJECT_ROOT / "content"
MONTH_SECTION_PATTERN = re.compile(r"(?m)^##\s+(.+?)\s*$")
WEEK_BLOCK_PATTERN = re.compile(r"(?ms)^###\s+.+?\s*$\n(.*?)(?=^###\s+|\Z)")
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
WORD_PATTERN = re.compile(r"\S+")

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

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "while",
    "with",
}


@dataclass(frozen=True)
class MonthSnapshot:
    path: Path
    year: int
    month: int
    title: str
    date: str
    summaries: tuple[str, ...]
    themes: tuple[str, ...]
    signals: tuple[str, ...]
    noise: tuple[str, ...]
    gaps: tuple[str, ...]
    closing_reads: tuple[str, ...]
    synthesis_narrative: str = ""

    @property
    def month_name(self) -> str:
        return MONTH_NAMES[self.month]

    @property
    def month_slug(self) -> str:
        return f"{self.year}-{self.month:02d}"

    @property
    def link(self) -> str:
        return f"/monthly/{self.year}/{self.month:02d}/"

    @property
    def text_blob(self) -> str:
        return " ".join(
            [
                self.title,
                *self.summaries,
                *self.themes,
                *self.signals,
                *self.noise,
                *self.gaps,
                *self.closing_reads,
                self.synthesis_narrative,
            ]
        )


@dataclass(frozen=True)
class YearlyNarrativePage:
    year: int
    path: Path
    frontmatter: dict[str, Any]
    narrative: str
    arc_lines: tuple[str, ...]


@dataclass(frozen=True)
class TrendFamily:
    key: str
    label: str
    keywords: tuple[str, ...]
    stages: tuple[tuple[str, tuple[str, ...]], ...]


TREND_FAMILIES = (
    TrendFamily(
        key="agent-skills",
        label="agent-skills",
        keywords=("agent skill", "agent-skills", "skills pack", "skill package", "skill"),
        stages=(
            ("infrastructure", ("maturing", "infrastructure", "mcp", "small model", "small-model")),
            ("economy", ("economy", "distribution format", "marketplace", "skills layer", "skills packs")),
            (
                "globalization",
                ("east asian", "chinese", "global", "globalization", "xiaohongshu", "wechat", "cultural", "linguistic"),
            ),
            (
                "verticalization",
                ("verticalization", "vertical", "domain-specific", "role-specific", "legal", "medical", "finance", "education"),
            ),
        ),
    ),
    TrendFamily(
        key="platform-gaming",
        label="platform-gaming",
        keywords=("star-farming", "fork inflation", "spam", "activator", "cheat", "prediction-market bot", "seo-farming"),
        stages=(
            ("star-farming", ("star-farming", "star farming", "seo-farming")),
            ("fork-inflation", ("fork inflation", "fork-inflation", "inflated fork", "implausibly inflated")),
            ("activator-spam", ("activator", "activated", "kms", "copy-trading", "keyword-repetition", "bot cluster")),
            ("fraud-cheat noise", ("fraud", "wallet-spoofer", "game cheat", "crypto fraud", "software unlock", "prediction-market bot")),
        ),
    ),
    TrendFamily(
        key="security-gap",
        label="security-gap",
        keywords=("security gap", "prompt injection", "supply-chain", "supply chain", "agent execution security", "agent isolation", "permission-scoping"),
        stages=(
            ("identified", ("security signal", "security gap", "agent execution security", "permission-scoping", "agent isolation")),
            ("widening", ("still holds", "remains", "widening", "become exploitable", "not attracting commensurate attention")),
            ("unresolved", ("no tooling exists", "gap that will become exploitable", "does not exist", "stayed missing")),
        ),
    ),
    TrendFamily(
        key="self-hosted-ai",
        label="self-hosted-ai",
        keywords=("self-hosted", "local-sovereignty", "local sovereignty", "local-sovereignty", "billing friction", "workspace", "local-first"),
        stages=(
            ("friction", ("billing friction", "cost", "copilot billing")),
            ("self-hosted workspaces", ("self-hosted", "workspace launch", "workspace")),
            ("local sovereignty", ("local-sovereignty", "local sovereignty", "local-first", "sandboxd", "memory", "control")),
        ),
    ),
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate yearly narrative pages from monthly rollups.")
    parser.add_argument(
        "--content-root",
        type=Path,
        default=DEFAULT_CONTENT_ROOT,
        help="Root content directory containing monthly/ and yearly/.",
    )
    parser.add_argument(
        "--year",
        type=int,
        action="append",
        dest="years",
        help="Optional year to regenerate. May be passed multiple times.",
    )
    return parser.parse_args(argv)


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def yaml_value(value: Any) -> str:
    if isinstance(value, str):
        return yaml_quote(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return f"[{', '.join(yaml_value(item) for item in value)}]"
    return str(value)


def render_frontmatter(frontmatter: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {yaml_value(value)}")
    lines.extend(["---", "", ""])
    return "\n".join(lines)


def strip_markdown(text: str) -> str:
    cleaned = LINK_PATTERN.sub(r"\1", text)
    cleaned = cleaned.replace("**", "").replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", cleaned).strip()


def split_sections(body: str) -> dict[str, str]:
    matches = list(MONTH_SECTION_PATTERN.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group(1).strip()] = body[start:end].strip("\n")
    return sections


def extract_labeled_values(section_body: str, label: str) -> list[str]:
    values: list[str] = []
    for block in WEEK_BLOCK_PATTERN.finditer(section_body):
        for line in block.group(1).splitlines():
            if not line.startswith(f"- {label}:"):
                continue
            value = strip_markdown(line.split(":", 1)[1])
            if value:
                values.append(value)
    return values


def dedupe_preserving_order(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def month_synthesis_path(content_root: Path, year: int, month: int) -> Path:
    return content_root.parent / "data" / "analyzed" / f"{year}-{month:02d}-month-synthesis.md"


def extract_month_synthesis_narrative(content_root: Path, year: int, month: int) -> str:
    synthesis_path = month_synthesis_path(content_root, year, month)
    if not synthesis_path.is_file():
        return ""
    _, body = analysis_gate.extract_frontmatter(synthesis_path.read_text(encoding="utf-8"))
    return split_sections(body).get("Month Synthesis", "").strip()


def load_month_snapshot(path: Path, content_root: Path) -> MonthSnapshot:
    frontmatter, body = analysis_gate.extract_frontmatter(path.read_text(encoding="utf-8"))
    sections = split_sections(body)
    themes: list[str] = []
    for raw in extract_labeled_values(sections.get("Month Overview", ""), "Recurring themes so far"):
        themes.extend(part.strip() for part in raw.rstrip(".").split(",") if part.strip())
    year = int(frontmatter["year"])
    month = int(frontmatter["month"])
    return MonthSnapshot(
        path=path,
        year=year,
        month=month,
        title=str(frontmatter.get("title", path.stem)),
        date=str(frontmatter["date"]),
        summaries=tuple(extract_labeled_values(sections.get("Month Overview", ""), "Summary")),
        themes=tuple(dedupe_preserving_order(themes)),
        signals=tuple(extract_labeled_values(sections.get("Trends Observed", ""), "Signal")),
        noise=tuple(extract_labeled_values(sections.get("Trends Observed", ""), "Noise")),
        gaps=tuple(extract_labeled_values(sections.get("Key Takeaways", ""), "Gap to watch")),
        closing_reads=tuple(extract_labeled_values(sections.get("Key Takeaways", ""), "Closing read")),
        synthesis_narrative=extract_month_synthesis_narrative(content_root, year, month),
    )


def load_month_snapshots(content_root: Path, years: Iterable[int] | None = None) -> list[MonthSnapshot]:
    if years:
        paths = []
        for year in sorted(set(years)):
            paths.extend(sorted((content_root / "monthly" / str(year)).glob("*.md")))
    else:
        paths = sorted((content_root / "monthly").glob("*/*.md"))
    snapshots = [load_month_snapshot(path, content_root) for path in paths if path.is_file()]
    return sorted(snapshots, key=lambda item: (item.year, item.month))


def word_count(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def trim_words(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text.strip()
    return " ".join(words[:limit]).rstrip(",;:.") + "…"


def compress_phrase(text: str, limit: int = 24) -> str:
    cleaned = strip_markdown(text)
    cleaned = re.sub(r"^(Week \d+\s+|W\d+\s+)", "", cleaned)
    cleaned = re.sub(r"^(The durable signal this week |This week |Week \d+ |W\d+ )", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(".")
    return trim_words(cleaned, limit)


def keyword_score(text: str, keywords: Iterable[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword in lowered)


def detect_family_arc(months: list[MonthSnapshot], family: TrendFamily) -> list[str]:
    stages: list[str] = []
    family_seen = False
    for month in months:
        lowered = month.text_blob.lower()
        if keyword_score(lowered, family.keywords):
            family_seen = True
        for stage, keywords in family.stages:
            if any(keyword in lowered for keyword in keywords) and stage not in stages:
                stages.append(stage)
    if family_seen and not stages:
        stages.append("emerging")
    return stages


def build_theme_sentence(year: int, arcs: dict[str, list[str]]) -> str:
    has_skills = bool(arcs.get("agent-skills"))
    has_noise = bool(arcs.get("platform-gaming"))
    has_security = bool(arcs.get("security-gap"))
    has_local = bool(arcs.get("self-hosted-ai"))
    if has_skills and has_noise:
        sentence = (
            f"{year} has been a split-screen story: agent tooling kept solidifying into a real distribution layer "
            "while GitHub discovery got easier to game."
        )
    elif has_skills:
        sentence = f"{year} has mainly been the year agent tooling stopped looking experimental and started behaving like infrastructure."
    else:
        sentence = f"{year} has so far been defined less by single launches than by shifts in how the ecosystem is organizing itself."
    if has_security:
        sentence += " The ecosystem moved faster on capability than on trust."
    elif has_local:
        sentence += " Control, cost, and local execution kept gaining weight."
    return sentence


def summarize_month(month: MonthSnapshot) -> str:
    month_arcs = {family.key: detect_family_arc([month], family) for family in TREND_FAMILIES}
    parts: list[str] = []

    agent_arc = month_arcs.get("agent-skills", [])
    if "globalization" in agent_arc and "verticalization" in agent_arc:
        parts.append("agent skills globalized and started splitting into tighter verticals")
    elif "economy" in agent_arc and "infrastructure" in agent_arc:
        parts.append("agent skills hardened from plumbing into an economy")
    elif "economy" in agent_arc:
        parts.append("agent skills started looking like a real market layer")
    elif "infrastructure" in agent_arc:
        parts.append("agent tooling kept hardening into infrastructure")

    local_arc = month_arcs.get("self-hosted-ai", [])
    if "local sovereignty" in local_arc:
        parts.append("self-hosted and local-sovereignty tools gained real momentum")
    elif "self-hosted workspaces" in local_arc:
        parts.append("self-hosted AI workspaces became more credible")

    if month_arcs.get("security-gap"):
        parts.append("the security gap stayed more visible than the fixes")

    platform_arc = month_arcs.get("platform-gaming", [])
    if "fork-inflation" in platform_arc:
        parts.append("fork inflation replaced the earlier star-farming playbook")
    elif "star-farming" in platform_arc:
        parts.append("coordinated star-farming made discovery harder to trust")

    if parts:
        return "; ".join(parts[:-1]) + ("" if len(parts) < 2 else "; ") + parts[-1] if len(parts) > 1 else parts[0]

    return trim_words(strip_markdown(month.summaries[-1] if month.summaries else month.text_blob), 32)


def month_yearly_excerpt(month: MonthSnapshot, limit: int = 48) -> str:
    if month.synthesis_narrative:
        return trim_words(strip_markdown(month.synthesis_narrative), limit).rstrip(".")
    fallback = month.summaries[-1] if month.summaries else month.text_blob
    return trim_words(strip_markdown(fallback), limit).rstrip(".")


def build_month_story(months: list[MonthSnapshot]) -> str:
    if not months:
        return ""
    if len(months) == 1:
        return f"The monthly progression is already visible in {months[0].month_name}: {month_yearly_excerpt(months[0])}."

    clauses: list[str] = []
    for index, month in enumerate(months):
        excerpt = month_yearly_excerpt(month)
        if index == 0:
            lead = "set the initial tone"
        elif index == len(months) - 1:
            lead = "pushed the story further"
        else:
            lead = "carried the story forward"
        clauses.append(f"{month.month_name} {lead} when {excerpt}")
    return (
        "The monthly progression is clear: "
        + "; ".join(clauses)
        + ". Taken together, those shifts show a market moving from experimentation toward packaging, distribution, and operating discipline. "
        + "Even when the surface story changes from one month to the next, the deeper motion is cumulative rather than episodic."
    )


def build_arc_commentary(arcs: dict[str, list[str]]) -> list[str]:
    commentary: list[str] = []
    agent_arc = arcs.get("agent-skills", [])
    if agent_arc:
        commentary.append(f"Agent skills moved through {' → '.join(agent_arc)}.")
    platform_arc = arcs.get("platform-gaming", [])
    if platform_arc:
        commentary.append(f"Platform gaming adapted through {' → '.join(platform_arc)} instead of disappearing.")
    local_arc = arcs.get("self-hosted-ai", [])
    if local_arc:
        commentary.append(f"Self-hosted AI evolved through {' → '.join(local_arc)} as builders chased more control over execution and cost.")
    security_arc = arcs.get("security-gap", [])
    if security_arc:
        commentary.append("The security gap stayed ahead of the fixes: each month made the need for agent isolation, supply-chain auditing, and prompt-injection defenses easier to see.")
    return commentary


def build_prediction_review(arcs: dict[str, list[str]]) -> str:
    confirmations: list[str] = []
    if "globalization" in arcs.get("agent-skills", []):
        confirmations.append("skills globalized")
    if "verticalization" in arcs.get("agent-skills", []):
        confirmations.append("skills also verticalized quickly")
    if len(arcs.get("platform-gaming", [])) >= 2:
        confirmations.append("discovery-layer abuse mutated instead of self-correcting")
    if arcs.get("self-hosted-ai"):
        confirmations.append("local and self-hosted AI kept becoming a category rather than a workaround")
    if arcs.get("security-gap"):
        confirmations.append("the trust and security gap remained open")
    if not confirmations:
        return "What was confirmed: the biggest structural questions still look unresolved."
    joined = "; ".join(confirmations[:-1]) + ("" if len(confirmations) < 2 else "; ") + confirmations[-1] if len(confirmations) > 1 else confirmations[0]
    return f"What was confirmed: {joined}."


def build_weakened_review(arcs: dict[str, list[str]]) -> str:
    weakened: list[str] = []
    if arcs.get("security-gap"):
        weakened.append("the idea that trust tooling would catch up on its own")
    if len(arcs.get("agent-skills", [])) >= 2:
        weakened.append("the simpler thesis that one general-purpose agent workflow would dominate everything")
    if not weakened:
        weakened.append("the hope that one short-term spike would settle the year's story")
    joined = ", ".join(weakened[:-1]) + ("" if len(weakened) < 2 else ", and ") + weakened[-1] if len(weakened) > 1 else weakened[0]
    return f"What weakened: {joined}."


def compress_narrative(paragraphs: list[str], max_words: int = 500) -> str:
    text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
    if word_count(text) <= max_words:
        return text
    compressed = text
    for limit in (460, 430, 400, 360):
        words = compressed.split()
        if len(words) <= max_words:
            break
        compressed = " ".join(words[:limit]).rstrip(",;:.") + "…"
    return compressed


def build_arc_lines(months: list[MonthSnapshot]) -> tuple[str, ...]:
    arcs: list[str] = []
    for family in TREND_FAMILIES:
        stages = detect_family_arc(months, family)
        if stages:
            arcs.append(f"{family.label}: {' > '.join(stages)}")
    return tuple(arcs)


def synthesize_year(months: list[MonthSnapshot]) -> tuple[str, tuple[str, ...]]:
    arcs = {family.key: detect_family_arc(months, family) for family in TREND_FAMILIES}
    paragraphs = [
        build_theme_sentence(months[0].year, arcs),
        build_month_story(months),
        " ".join(build_arc_commentary(arcs)),
        " ".join(
            [
                build_prediction_review(arcs),
                build_weakened_review(arcs),
                "That leaves the main story of the year intact: builders are getting more serious about packaging and operating agents, while the trust, filtering, and governance layers remain conspicuously behind.",
            ]
        ),
    ]
    return compress_narrative(paragraphs), build_arc_lines(months)


def build_yearly_narrative_pages(content_root: Path, years: Iterable[int] | None = None) -> list[YearlyNarrativePage]:
    grouped: dict[int, list[MonthSnapshot]] = {}
    for snapshot in load_month_snapshots(content_root, years):
        grouped.setdefault(snapshot.year, []).append(snapshot)

    pages: list[YearlyNarrativePage] = []
    for year, months in sorted(grouped.items()):
        ordered = sorted(months, key=lambda item: item.month)
        narrative, arc_lines = synthesize_year(ordered)
        pages.append(
            YearlyNarrativePage(
                year=year,
                path=content_root / "yearly" / f"{year}.md",
                frontmatter={
                    "title": f"{year} Yearly Narrative",
                    "date": ordered[-1].date,
                    "year": year,
                    "categories": ["yearly"],
                    "months_covered": [month.month_slug for month in ordered],
                    "format": "narrative",
                },
                narrative=narrative,
                arc_lines=arc_lines,
            )
        )
    return pages


def render_yearly_page(page: YearlyNarrativePage) -> str:
    body = f"## Year in Review\n\n{page.narrative}\n"
    return render_frontmatter(page.frontmatter) + body


def generate_yearly_narratives(content_root: Path, years: Iterable[int] | None = None) -> list[Path]:
    written: list[Path] = []
    for page in build_yearly_narrative_pages(content_root, years):
        page.path.parent.mkdir(parents=True, exist_ok=True)
        page.path.write_text(render_yearly_page(page), encoding="utf-8")
        written.append(page.path)
    return written


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    written = generate_yearly_narratives(args.content_root, args.years)
    if not written:
        print(f"No monthly rollups found under {args.content_root / 'monthly'}")
        return 0
    for path in written:
        print(f"Generated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

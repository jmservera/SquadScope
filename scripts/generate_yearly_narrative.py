#!/usr/bin/env python3
"""Generate yearly narrative pages from monthly rollup content.

Reads monthly pages (content/monthly/YYYY/MM.md), detects trend-family arcs
across months, and synthesizes a cohesive year-in-review narrative. Output
includes:
- SEO-friendly editorial titles (max 70 chars) driven by detected arcs
- Meta description summaries (≤155 chars) extracted from narrative opening
- Cross-links to each contributing monthly report
- Structured frontmatter: months_covered, format, summary, categories
"""

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
HEADING_LINE_PATTERN = re.compile(r"(?m)^#+\s+")

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
    synthesis_paragraphs: tuple[str, ...] = ()

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
                *self.synthesis_paragraphs,
                *self.summaries,
                *self.themes,
                *self.signals,
                *self.noise,
                *self.gaps,
                *self.closing_reads,
            ]
        )

    @property
    def yearly_source_paragraphs(self) -> tuple[str, ...]:
        if self.synthesis_paragraphs:
            return self.synthesis_paragraphs
        paragraphs = [
            sentence
            for sentence in (
                self.summaries[-1] if self.summaries else "",
                self.signals[-1] if self.signals else "",
                self.gaps[-1] if self.gaps else "",
                self.closing_reads[-1] if self.closing_reads else "",
            )
            if sentence
        ]
        if paragraphs:
            return tuple(paragraphs)
        fallback = strip_markdown(self.text_blob)
        return (fallback,) if fallback else ()


@dataclass(frozen=True)
class YearlyNarrativePage:
    year: int
    path: Path
    frontmatter: dict[str, Any]
    narrative: str


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
            (
                "economy",
                ("economy", "distribution format", "marketplace", "skills layer", "skills packs"),
            ),
            (
                "globalization",
                (
                    "east asian",
                    "chinese",
                    "global",
                    "globalization",
                    "xiaohongshu",
                    "wechat",
                    "cultural",
                    "linguistic",
                ),
            ),
            (
                "verticalization",
                (
                    "verticalization",
                    "vertical",
                    "domain-specific",
                    "role-specific",
                    "legal",
                    "medical",
                    "finance",
                    "education",
                ),
            ),
        ),
    ),
    TrendFamily(
        key="platform-gaming",
        label="platform-gaming",
        keywords=(
            "star-farming",
            "fork inflation",
            "spam",
            "activator",
            "cheat",
            "prediction-market bot",
            "seo-farming",
        ),
        stages=(
            ("star-farming", ("star-farming", "star farming", "seo-farming")),
            (
                "fork-inflation",
                ("fork inflation", "fork-inflation", "inflated fork", "implausibly inflated"),
            ),
            (
                "activator-spam",
                (
                    "activator",
                    "activated",
                    "kms",
                    "copy-trading",
                    "keyword-repetition",
                    "bot cluster",
                ),
            ),
            (
                "fraud-cheat noise",
                (
                    "fraud",
                    "wallet-spoofer",
                    "game cheat",
                    "crypto fraud",
                    "software unlock",
                    "prediction-market bot",
                ),
            ),
        ),
    ),
    TrendFamily(
        key="security-gap",
        label="security-gap",
        keywords=(
            "security gap",
            "prompt injection",
            "supply-chain",
            "supply chain",
            "agent execution security",
            "agent isolation",
            "permission-scoping",
        ),
        stages=(
            (
                "identified",
                (
                    "security signal",
                    "security gap",
                    "agent execution security",
                    "permission-scoping",
                    "agent isolation",
                ),
            ),
            (
                "widening",
                (
                    "still holds",
                    "remains",
                    "widening",
                    "become exploitable",
                    "not attracting commensurate attention",
                ),
            ),
            (
                "unresolved",
                (
                    "no tooling exists",
                    "gap that will become exploitable",
                    "does not exist",
                    "stayed missing",
                ),
            ),
        ),
    ),
    TrendFamily(
        key="self-hosted-ai",
        label="self-hosted-ai",
        keywords=(
            "self-hosted",
            "local-sovereignty",
            "local sovereignty",
            "local-sovereignty",
            "billing friction",
            "workspace",
            "local-first",
        ),
        stages=(
            ("friction", ("billing friction", "cost", "copilot billing")),
            ("self-hosted workspaces", ("self-hosted", "workspace launch", "workspace")),
            (
                "local sovereignty",
                (
                    "local-sovereignty",
                    "local sovereignty",
                    "local-first",
                    "sandboxd",
                    "memory",
                    "control",
                ),
            ),
        ),
    ),
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate yearly narrative pages from monthly rollups."
    )
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


def extract_prose_paragraphs(body: str) -> tuple[str, ...]:
    paragraphs: list[str] = []
    for block in re.split(r"\n\s*\n", body.strip()):
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if all(line.lstrip().startswith("#") for line in lines):
            continue
        cleaned_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                stripped = HEADING_LINE_PATTERN.sub("", stripped)
            stripped = re.sub(r"^[-*]\s+", "", stripped)
            stripped = re.sub(r"^\d+\.\s+", "", stripped)
            if stripped:
                cleaned_lines.append(stripped)
        paragraph = strip_markdown(" ".join(cleaned_lines))
        if paragraph and paragraph != "_No updates yet._":
            paragraphs.append(paragraph)
    return tuple(paragraphs)


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


def frontmatter_list(frontmatter: dict[str, Any], key: str) -> list[str]:
    raw = frontmatter.get(key, [])
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()]
    return []


def load_month_snapshot(path: Path) -> MonthSnapshot:
    frontmatter, body = analysis_gate.extract_frontmatter(path.read_text(encoding="utf-8"))
    sections = split_sections(body)
    month_synthesis = strip_markdown(sections.get("Month Synthesis", ""))
    if month_synthesis:
        summaries = dedupe_preserving_order(
            [str(frontmatter.get("summary", "")).strip(), month_synthesis]
        )
        themes = dedupe_preserving_order(
            frontmatter_list(frontmatter, "themes")
            + frontmatter_list(frontmatter, "persistent_themes")
            + frontmatter_list(frontmatter, "accelerating_themes")
            + frontmatter_list(frontmatter, "weakening_themes")
        )
        signals = dedupe_preserving_order(
            [strip_markdown(sections.get("Trend Arc", ""))]
            + [
                theme.replace("-", " ")
                for theme in frontmatter_list(frontmatter, "accelerating_themes")
            ]
            + [
                theme.replace("-", " ")
                for theme in frontmatter_list(frontmatter, "persistent_themes")
            ]
        )
        noise = tuple(
            theme.replace("-", " ") for theme in frontmatter_list(frontmatter, "weakening_themes")
        )
        gaps = tuple(frontmatter_list(frontmatter, "key_gaps"))
        closing_reads = tuple(
            value
            for value in [
                strip_markdown(sections.get("Prediction Review", "")),
                str(frontmatter.get("summary", "")).strip(),
            ]
            if value
        )
        return MonthSnapshot(
            path=path,
            year=int(frontmatter["year"]),
            month=int(frontmatter["month"]),
            title=str(frontmatter.get("title", path.stem)),
            date=str(frontmatter["date"]),
            summaries=tuple(summaries),
            themes=tuple(themes),
            signals=tuple(signals),
            noise=noise,
            gaps=gaps,
            closing_reads=closing_reads,
        )

    themes: list[str] = []
    for raw in extract_labeled_values(
        sections.get("Month Overview", ""), "Recurring themes so far"
    ):
        themes.extend(part.strip() for part in raw.rstrip(".").split(",") if part.strip())
    return MonthSnapshot(
        path=path,
        year=int(frontmatter["year"]),
        month=int(frontmatter["month"]),
        title=str(frontmatter.get("title", path.stem)),
        date=str(frontmatter["date"]),
        summaries=tuple(extract_labeled_values(sections.get("Month Overview", ""), "Summary")),
        themes=tuple(dedupe_preserving_order(themes)),
        signals=tuple(extract_labeled_values(sections.get("Trends Observed", ""), "Signal")),
        noise=tuple(extract_labeled_values(sections.get("Trends Observed", ""), "Noise")),
        gaps=tuple(extract_labeled_values(sections.get("Key Takeaways", ""), "Gap to watch")),
        closing_reads=tuple(
            extract_labeled_values(sections.get("Key Takeaways", ""), "Closing read")
        ),
    )


def analyzed_dir_for(content_root: Path) -> Path:
    return content_root.parent / "data" / "analyzed"


def load_month_synthesis_paragraphs(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    try:
        _, body = analysis_gate.extract_frontmatter(text)
    except ValueError:
        body = text
    return extract_prose_paragraphs(body)


def load_month_snapshot_with_preference(path: Path, content_root: Path) -> MonthSnapshot:
    snapshot = load_month_snapshot(path)
    synthesis_path = (
        analyzed_dir_for(content_root) / f"{snapshot.year}-{snapshot.month:02d}-month-synthesis.md"
    )
    if not synthesis_path.is_file():
        return snapshot
    synthesis_paragraphs = load_month_synthesis_paragraphs(synthesis_path)
    if not synthesis_paragraphs:
        return snapshot
    return MonthSnapshot(
        path=snapshot.path,
        year=snapshot.year,
        month=snapshot.month,
        title=snapshot.title,
        date=snapshot.date,
        summaries=snapshot.summaries,
        themes=snapshot.themes,
        signals=snapshot.signals,
        noise=snapshot.noise,
        gaps=snapshot.gaps,
        closing_reads=snapshot.closing_reads,
        synthesis_paragraphs=synthesis_paragraphs,
    )


def load_month_snapshots(
    content_root: Path, years: Iterable[int] | None = None
) -> list[MonthSnapshot]:
    if years:
        paths = []
        for year in sorted(set(years)):
            paths.extend(sorted((content_root / "monthly" / str(year)).glob("*.md")))
    else:
        paths = sorted((content_root / "monthly").glob("*/*.md"))
    snapshots = [
        load_month_snapshot_with_preference(path, content_root) for path in paths if path.is_file()
    ]
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
    cleaned = re.sub(
        r"^(The durable signal this week |This week |Week \d+ |W\d+ )",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(".")
    return trim_words(cleaned, limit)


def join_phrases(parts: Iterable[str], *, conjunction: str = "and") -> str:
    items = [part.strip() for part in parts if part and part.strip()]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"


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
    if month.synthesis_paragraphs:
        return trim_words(strip_markdown(month.synthesis_paragraphs[0]), 40)
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
        return (
            "; ".join(parts[:-1]) + ("" if len(parts) < 2 else "; ") + parts[-1]
            if len(parts) > 1
            else parts[0]
        )

    source = (
        month.yearly_source_paragraphs[0] if month.yearly_source_paragraphs else month.text_blob
    )
    return trim_words(strip_markdown(source), 32)


def build_month_bridge(month: MonthSnapshot, position: int, total: int) -> str:
    if total == 1:
        return f"{month.month_name} supplied the year's opening evidence"
    if position == 0:
        return f"{month.month_name} set the initial tone"
    if position == total - 1:
        return f"{month.month_name} pushed the story further"
    return f"in {month.month_name}"


def build_opening_paragraph(months: list[MonthSnapshot], arcs: dict[str, list[str]]) -> str:
    opening = build_theme_sentence(months[0].year, arcs)
    span = (
        months[0].month_name
        if len(months) == 1
        else f"From {months[0].month_name} through {months[-1].month_name}"
    )
    durable_categories: list[str] = []
    if arcs.get("agent-skills"):
        durable_categories.append("agent skills as a real distribution layer")
    if arcs.get("self-hosted-ai"):
        durable_categories.append("local and self-hosted execution as a durable buyer priority")
    if arcs.get("security-gap"):
        durable_categories.append("agent security as the main unresolved infrastructure gap")
    if not durable_categories:
        durable_categories.append("workflow-level shifts rather than one-off launches")
    return (
        f"{opening} {span}, the important change was not a parade of isolated repositories but the way a few categories kept hardening: "
        f"{join_phrases(durable_categories)}. The year so far reads less like a sequence of weekly surprises and more like an ecosystem choosing its operating model."
    )


def build_evolution_paragraph(months: list[MonthSnapshot]) -> str:
    if not months:
        return ""
    fragments = [
        f"{build_month_bridge(month, index, len(months))} when {summarize_month(month).rstrip('.')}"
        for index, month in enumerate(months)
    ]
    if len(fragments) == 1:
        body = fragments[0]
    else:
        body = "; ".join(fragments[:-1]) + f"; {fragments[-1]}"
    return (
        f"The monthly progression is clear: {body}. Taken together, those shifts show a market moving from experimentation toward packaging, distribution, and operating discipline. "
        "Even when the surface story changes from one month to the next, the deeper motion is cumulative rather than episodic."
    )


def build_pattern_paragraph(arcs: dict[str, list[str]]) -> str:
    sentences: list[str] = []
    agent_arc = arcs.get("agent-skills", [])
    if agent_arc:
        if "verticalization" in agent_arc or "globalization" in agent_arc:
            sentences.append(
                "The category that hardened fastest was agent skills: what began as infrastructure and workflow plumbing started behaving like a market, then spread into more specific geographies, languages, and job-shaped use cases."
            )
        else:
            sentences.append(
                "The clearest durable category was agent skills, which stopped looking like a novelty and started looking like shared infrastructure."
            )
    local_arc = arcs.get("self-hosted-ai", [])
    if local_arc:
        sentences.append(
            "Self-hosted and local-first tooling also matured from a cost or billing workaround into a control story about sovereignty, reliability, and execution on hardware teams already own."
        )
    platform_arc = arcs.get("platform-gaming", [])
    if platform_arc:
        sentences.append(
            "The pattern that mutated instead of fading was platform gaming: the noise never really disappeared, it simply changed tactics from star-farming to fork inflation and then into more industrialized spam, fraud, and activator-style clutter."
        )
    security_arc = arcs.get("security-gap", [])
    if security_arc:
        sentences.append(
            "The prediction that capability would outrun trust was confirmed every month, because nothing in the visible tooling stack closed the gaps around agent isolation, prompt injection defense, or skills supply-chain auditing."
        )
    return " ".join(sentences)


def build_prediction_review(arcs: dict[str, list[str]]) -> str:
    confirmations: list[str] = []
    if "globalization" in arcs.get("agent-skills", []):
        confirmations.append("skills did globalize")
    if "verticalization" in arcs.get("agent-skills", []):
        confirmations.append("skills also verticalized quickly")
    if len(arcs.get("platform-gaming", [])) >= 2:
        confirmations.append("discovery-layer abuse mutated instead of self-correcting")
    if arcs.get("self-hosted-ai"):
        confirmations.append(
            "local and self-hosted AI kept becoming a category rather than a workaround"
        )
    if arcs.get("security-gap"):
        confirmations.append("the trust and security gap remained open")
    weakened: list[str] = []
    if arcs.get("platform-gaming"):
        weakened.append("the hope that GitHub discovery noise would self-correct")
    if arcs.get("security-gap"):
        weakened.append("the idea that trust tooling would catch up on its own")
    if "verticalization" in arcs.get("agent-skills", []):
        weakened.append(
            "the simpler thesis that one general-purpose agent workflow would dominate everything"
        )
    if not confirmations and not weakened:
        return "The running predictions stayed directionally useful: the biggest structural questions still look unresolved."
    sentences: list[str] = []
    if confirmations:
        sentences.append(f"What was confirmed: {join_phrases(confirmations)}.")
    if weakened:
        sentences.append(f"What weakened: {join_phrases(weakened)}.")
    sentences.append(
        "That leaves the main story of the year intact: builders are getting more serious about packaging and operating agents, while the trust, filtering, and governance layers remain conspicuously behind."
    )
    return " ".join(sentences)


def compress_narrative(paragraphs: list[str], max_words: int = 500) -> str:
    text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
    if word_count(text) <= max_words:
        return text
    compressed = text
    for limit in (480, 460, 430, 400, 360):
        words = compressed.split()
        if len(words) <= max_words:
            break
        compressed = " ".join(words[:limit]).rstrip(",;:.") + "…"
    return compressed


def synthesize_year(months: list[MonthSnapshot]) -> str:
    arcs = {family.key: detect_family_arc(months, family) for family in TREND_FAMILIES}
    paragraphs = [
        build_opening_paragraph(months, arcs),
        build_evolution_paragraph(months),
        build_pattern_paragraph(arcs),
        build_prediction_review(arcs),
    ]
    return compress_narrative(paragraphs)


def generate_yearly_title(year: int, arcs: dict[str, list[str]]) -> str:
    """Generate an SEO-friendly editorial title (max 70 chars) for yearly narrative."""
    has_skills = bool(arcs.get("agent-skills"))
    has_security = bool(arcs.get("security-gap"))
    has_noise = bool(arcs.get("platform-gaming"))
    has_local = bool(arcs.get("self-hosted-ai"))

    if has_skills and has_security:
        title = f"When Agents Became Infrastructure — {year} So Far"
    elif has_skills and has_noise:
        title = f"Agents Rise While Discovery Noise Mutates — {year}"
    elif has_skills:
        title = f"Agent Tooling Grows Up — {year} So Far"
    elif has_security:
        title = f"Capability Outpaces Trust — {year} So Far"
    elif has_local:
        title = f"Local AI Takes Hold — {year} So Far"
    else:
        title = f"The Ecosystem Reorganizes — {year} So Far"

    return title[:70]


def _extract_summary(narrative: str, max_length: int = 155) -> str:
    """Extract a ≤155-character summary from the narrative's first sentence."""
    narrative = narrative.strip()
    # Take first sentence (up to first . ! or ? followed by whitespace or end)
    first_sentence_match = re.match(r"(.+?[.!?])(?:\s|$)", narrative)
    if first_sentence_match:
        sentence = first_sentence_match.group(1).strip()
        if len(sentence) <= max_length:
            return sentence
        # Truncate at last word boundary within limit
        truncated = sentence[: max_length - 1].rsplit(" ", 1)[0]
        return truncated.rstrip(".,;:") + "…"
    # Fallback: truncate narrative at word boundary
    if len(narrative) <= max_length:
        return narrative.strip()
    truncated = narrative[: max_length - 1].rsplit(" ", 1)[0]
    return truncated.rstrip(".,;:") + "…"


def build_yearly_narrative_pages(
    content_root: Path, years: Iterable[int] | None = None
) -> list[YearlyNarrativePage]:
    grouped: dict[int, list[MonthSnapshot]] = {}
    for snapshot in load_month_snapshots(content_root, years):
        grouped.setdefault(snapshot.year, []).append(snapshot)

    pages: list[YearlyNarrativePage] = []
    for year, months in sorted(grouped.items()):
        ordered = sorted(months, key=lambda item: item.month)
        narrative = synthesize_year(ordered)
        arcs = {family.key: detect_family_arc(ordered, family) for family in TREND_FAMILIES}
        title = generate_yearly_title(year, arcs)
        summary = _extract_summary(narrative)
        month_slugs = [month.month_slug for month in ordered]
        nav_links = []
        for slug in month_slugs:
            parts = slug.split("-")
            if len(parts) == 2:
                year_str, month_str = parts
                month_num = int(month_str)
                month_name = MONTH_NAMES.get(month_num, month_str)
                nav_links.append(f"[{month_name}](/monthly/{year_str}/{month_str}/)")
        nav_prefix = ""
        if nav_links:
            nav_prefix = f"**Monthly reports:** {' · '.join(nav_links)}\n\n"
        pages.append(
            YearlyNarrativePage(
                year=year,
                path=content_root / "yearly" / f"{year}.md",
                frontmatter={
                    "title": title,
                    "date": ordered[-1].date,
                    "year": year,
                    "categories": ["yearly"],
                    "months_covered": month_slugs,
                    "format": "narrative",
                    "summary": summary,
                },
                narrative=nav_prefix + narrative,
            )
        )
    return pages


def render_yearly_page(page: YearlyNarrativePage) -> str:
    body = f"## Year in Review\n\n{page.narrative}\n"
    return render_frontmatter(page.frontmatter) + body


def generate_yearly_narratives(
    content_root: Path, years: Iterable[int] | None = None
) -> list[Path]:
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

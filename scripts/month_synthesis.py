"""Month synthesis: deterministic monthly narrative generator.

Consumes weekly analysis summaries for a given month and produces a synthesis
artifact with:
- Structured frontmatter: title, summary, themes, persistent/accelerating/weakening
  themes, key_gaps, top_repos, source_checksum, weeks_covered
- Body sections: Month Synthesis (narrative), Weekly Reports (cross-linked list),
  Trend Arc (persistent/accelerating/weakening theme bullets), Prediction Review
- Summary field (≤28 words) suitable for SEO meta descriptions
- Source checksum for idempotent regeneration (skips if input unchanged)
"""

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import scripts.analysis_gate as analysis_gate

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

SECTION_PATTERN = re.compile(r"(?m)^##\s+(.+?)\s*$")
WORD_PATTERN = re.compile(r"\S+")
SYNTHESIS_VERSION = 2


@dataclass(frozen=True)
class MonthSynthesis:
    path: Path
    year: int
    month: int
    date: str
    weeks_covered: tuple[str, ...]
    summary: str
    narrative: str
    trend_arc: str
    prediction_review: str
    weekly_reports: tuple[str, ...]
    themes: tuple[str, ...]
    persistent_themes: tuple[str, ...]
    accelerating_themes: tuple[str, ...]
    weakening_themes: tuple[str, ...]
    key_gaps: tuple[str, ...]
    top_repos: tuple[str, ...]
    source_checksum: str
    status: str = "generated"

    @property
    def month_slug(self) -> str:
        return f"{self.year}-{self.month:02d}"

    @property
    def title(self) -> str:
        return f"{MONTH_NAMES[self.month]} {self.year} Month Synthesis"


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def yaml_value(value: Any) -> str:
    if isinstance(value, str):
        return yaml_quote(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, (list, tuple)):
        return f"[{', '.join(yaml_value(item) for item in value)}]"
    return str(value)


def render_frontmatter(frontmatter: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {yaml_value(value)}")
    lines.extend(["---", "", ""])
    return "\n".join(lines)


def split_sections(body: str) -> dict[str, str]:
    matches = list(SECTION_PATTERN.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group(1).strip()] = body[start:end].strip("\n")
    return sections


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def strip_markdown(value: str) -> str:
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    cleaned = cleaned.replace("**", "").replace("*", "").replace("`", "")
    return normalize_text(cleaned)


def trim_words(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text.strip()
    return " ".join(words[:limit]).rstrip(",;:.") + "…"


def dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def tag_label(tag: str) -> str:
    return tag.replace("-", " ")


def join_terms(values: list[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"


def top_sentences(values: list[str], *, limit: int = 2, words: int = 18) -> list[str]:
    sentences: list[str] = []
    for value in dedupe([normalize_text(value) for value in values]):
        if not value:
            continue
        sentences.append(trim_words(strip_markdown(value), words).rstrip("."))
        if len(sentences) >= limit:
            break
    return sentences


def build_weekly_reports(items: list[Any]) -> tuple[str, ...]:
    return tuple(
        f"- [{item.week_title}]({item.week_link}) — {trim_words(strip_markdown(item.summary), 18)}"
        for item in items
    )


def compress_week(item: Any) -> dict[str, Any]:
    return {
        "week": item.week,
        "title": item.title,
        "summary": item.summary,
        "top_repo": item.top_repo,
        "tags": list(item.tags),
        "signal": item.signal,
        "noise": item.noise,
        "gaps": item.gaps,
        "conclusion": item.conclusion,
        "featured_repos": list(item.featured_repos[:5]),
    }


def build_month_synthesis_pack(items: list[Any]) -> str:
    payload = {
        "synthesis_version": SYNTHESIS_VERSION,
        "month": f"{items[0].year}-{items[0].month:02d}",
        "weeks_covered": [item.week for item in items],
        "weeks": [compress_week(item) for item in items],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def source_checksum(pack: str) -> str:
    return "sha256:" + hashlib.sha256(pack.encode("utf-8")).hexdigest()


def synthesis_path(analyzed_dir: Path, year: int, month: int) -> Path:
    return analyzed_dir / f"{year}-{month:02d}-month-synthesis.md"


def _theme_trajectory(
    items: list[Any],
) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    tag_counts = Counter(tag for item in items for tag in set(item.tags))
    weeks_per_tag: dict[str, list[int]] = {}
    if len(items) == 1:
        ordered_themes = [tag for tag, _ in tag_counts.most_common(5)]
        return ordered_themes, [], [], [], []
    midpoint = max(1, len(items) // 2)
    for index, item in enumerate(items):
        for tag in set(item.tags):
            weeks_per_tag.setdefault(tag, []).append(index)

    persistent: list[str] = []
    accelerating: list[str] = []
    weakening: list[str] = []
    emerging: list[str] = []
    for tag, positions in weeks_per_tag.items():
        in_first_half = any(position < midpoint for position in positions)
        in_second_half = any(position >= midpoint for position in positions)
        if len(positions) >= 2:
            persistent.append(tag)
        if in_second_half and not in_first_half:
            emerging.append(tag)
        elif in_first_half and not in_second_half:
            weakening.append(tag)
        elif (
            positions
            and positions[-1] >= midpoint
            and positions[0] < midpoint
            and len(positions) >= 2
        ):
            accelerating.append(tag)

    ordered_themes = [tag for tag, _ in tag_counts.most_common(5)]
    persistent.sort(key=lambda tag: (-tag_counts[tag], tag))
    accelerating.sort(key=lambda tag: (-tag_counts[tag], tag))
    weakening.sort(key=lambda tag: (-tag_counts[tag], tag))
    emerging.sort(key=lambda tag: (-tag_counts[tag], tag))
    return ordered_themes, persistent, accelerating, weakening, emerging


def _word_count(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def _trim_to_range(text: str, *, minimum: int = 200, maximum: int = 350) -> str:
    cleaned = "\n\n".join(part.strip() for part in text.split("\n\n") if part.strip())
    count = _word_count(cleaned)
    if count <= maximum:
        return cleaned
    words = cleaned.split()
    trimmed = " ".join(words[:maximum]).rstrip(",;:.") + "…"
    if _word_count(trimmed) >= minimum:
        return trimmed
    return cleaned


def synthesize_month(
    items: list[Any], analyzed_dir: Path, checksum: str | None = None
) -> MonthSynthesis:
    if not items:
        raise ValueError("Cannot synthesize an empty month")

    year = items[0].year
    month = items[0].month
    pack = build_month_synthesis_pack(items)
    digest = checksum or source_checksum(pack)
    path = synthesis_path(analyzed_dir, year, month)

    themes, persistent, accelerating, weakening, emerging = _theme_trajectory(items)
    theme_labels = [tag_label(tag) for tag in themes[:3]]
    persistent_labels = [tag_label(tag) for tag in persistent[:3]]
    accelerating_labels = [tag_label(tag) for tag in (emerging + accelerating)[:3]]
    weakening_labels = [tag_label(tag) for tag in weakening[:3]]

    summaries = [trim_words(strip_markdown(item.summary), 24) for item in items if item.summary]
    signals = top_sentences([item.signal for item in items if item.signal], limit=2, words=22)
    noise = top_sentences([item.noise for item in items if item.noise], limit=2, words=18)
    gaps = top_sentences([item.gaps for item in items if item.gaps], limit=3, words=18)
    conclusions = top_sentences(
        [item.conclusion for item in items if item.conclusion], limit=2, words=20
    )
    top_repos = dedupe([item.top_repo for item in items if item.top_repo])[:4]

    summary = f"{MONTH_NAMES[month]} {year} was defined by {join_terms(theme_labels) if theme_labels else 'cross-week trend consolidation'}."
    if accelerating_labels:
        summary += f" Later in the month, {join_terms(accelerating_labels)} gathered pace."
    elif noise:
        summary += " The noise floor kept mutating instead of clearing."
    summary = trim_words(summary, 28)

    opening = (
        f"{MONTH_NAMES[month]} {year} reads less like three isolated weekly spikes and more like one continuous adjustment in priorities. "
        f"The month opened with {summaries[0] if summaries else 'a broad platform reset'} and ended with "
        f"{summaries[-1] if summaries else 'a clearer hierarchy of durable themes'}, which means the center of gravity shifted without abandoning the strongest earlier signals."
    )

    theme_sentence_parts: list[str] = []
    if persistent_labels:
        theme_sentence_parts.append(
            f"Persistent themes such as {join_terms(persistent_labels)} stayed present across multiple weeks"
        )
    if accelerating_labels:
        theme_sentence_parts.append(
            f"Later reports pushed {join_terms(accelerating_labels)} from interesting side threads into defining narratives"
        )
    if weakening_labels:
        theme_sentence_parts.append(
            f"Early-month concerns around {join_terms(weakening_labels)} faded relative to the stronger follow-on trends"
        )
    if len(top_repos) > 1:
        theme_sentence_parts.append(
            f"The month's anchor repos moved from {join_terms(top_repos[:2])} toward "
            f"{top_repos[-1]}, reinforcing that the winning projects were the ones narrowing scope while deepening practical utility"
        )
    elif top_repos:
        theme_sentence_parts.append(
            f"{top_repos[0]} served as the clearest anchor repo, which fits a month where practical utility mattered more than novelty alone"
        )
    theme_paragraph = ". ".join(part.rstrip(".") for part in theme_sentence_parts if part) + "."

    signal_paragraph = (
        f"The cross-week signal strengthened around {'; '.join(signals) if signals else 'operationally useful work rather than one-off hype'}. "
        f"At the same time, the month never solved its trust problem: "
        f"{'; '.join(gaps) if gaps else 'the same defensive gaps kept resurfacing'}."
    )

    prediction_sentence = "Most weekly predictions held up"
    if weakening_labels:
        prediction_sentence += f": the month kept validating {join_terms(accelerating_labels or persistent_labels or theme_labels)} while {join_terms(weakening_labels)} lost urgency"
    elif accelerating_labels or persistent_labels:
        prediction_sentence += f": later weeks reinforced {join_terms(accelerating_labels or persistent_labels)} instead of reversing them"
    else:
        prediction_sentence += (
            ": the later reports mostly confirmed the earlier direction of travel"
        )
    if conclusions:
        prediction_sentence += f". In retrospect, the clearest forward-looking reads were that {'; '.join(conclusions)}."
    else:
        prediction_sentence += "."

    if noise:
        prediction_sentence += f" The main counter-signal was noise that evolved from {' to '.join(noise[:2]) if len(noise) > 1 else noise[0]}."

    narrative = _trim_to_range(
        "\n\n".join([opening, theme_paragraph, signal_paragraph, prediction_sentence])
    )

    trend_arc_lines = [
        f"- Persistent themes: {join_terms(persistent_labels) if persistent_labels else 'none yet'}.",
        f"- Accelerating themes: {join_terms(accelerating_labels) if accelerating_labels else 'none yet'}.",
        f"- Weakened or receding themes: {join_terms(weakening_labels) if weakening_labels else 'none clearly receding yet'}.",
    ]
    if top_repos:
        trend_arc_lines.append(f"- Top repos that anchored the month: {join_terms(top_repos)}.")

    prediction_lines = [prediction_sentence]
    if gaps:
        prediction_lines.append(
            "The biggest unresolved gaps remained "
            + f"{join_terms(gaps[:3])}, so the monthly story still points to missing trust, filtering, or operational scaffolding."
        )

    return MonthSynthesis(
        path=path,
        year=year,
        month=month,
        date=items[-1].date.isoformat(),
        weeks_covered=tuple(item.week for item in items),
        summary=summary,
        narrative=narrative,
        trend_arc="\n".join(trend_arc_lines),
        prediction_review="\n\n".join(prediction_lines),
        weekly_reports=build_weekly_reports(items),
        themes=tuple(themes),
        persistent_themes=tuple(persistent),
        accelerating_themes=tuple(dedupe(emerging + accelerating)),
        weakening_themes=tuple(weakening),
        key_gaps=tuple(gaps),
        top_repos=tuple(top_repos),
        source_checksum=digest,
    )


def render_month_synthesis(synthesis: MonthSynthesis) -> str:
    frontmatter = {
        "title": synthesis.title,
        "date": synthesis.date,
        "month": synthesis.month_slug,
        "weeks_covered": list(synthesis.weeks_covered),
        "categories": ["monthly-synthesis"],
        "summary": synthesis.summary,
        "status": synthesis.status,
        "source_checksum": synthesis.source_checksum,
        "themes": list(synthesis.themes),
        "persistent_themes": list(synthesis.persistent_themes),
        "accelerating_themes": list(synthesis.accelerating_themes),
        "weakening_themes": list(synthesis.weakening_themes),
        "key_gaps": list(synthesis.key_gaps),
        "top_repos": list(synthesis.top_repos),
    }
    body = (
        f"## Month Synthesis\n\n{synthesis.narrative}\n\n"
        f"## Weekly Reports\n\n" + "\n".join(synthesis.weekly_reports) + "\n\n"
        f"## Trend Arc\n\n{synthesis.trend_arc}\n\n"
        f"## Prediction Review\n\n{synthesis.prediction_review}\n"
    )
    return render_frontmatter(frontmatter) + body


def write_month_synthesis(synthesis: MonthSynthesis) -> None:
    synthesis.path.parent.mkdir(parents=True, exist_ok=True)
    synthesis.path.write_text(render_month_synthesis(synthesis), encoding="utf-8")


def _frontmatter_list(frontmatter: dict[str, Any], key: str) -> tuple[str, ...]:
    raw = frontmatter.get(key, [])
    if isinstance(raw, list):
        return tuple(str(item) for item in raw)
    return ()


def load_month_synthesis(path: Path) -> MonthSynthesis:
    frontmatter, body = analysis_gate.extract_frontmatter(path.read_text(encoding="utf-8"))
    month_slug = str(frontmatter["month"])
    year_text, month_text = month_slug.split("-", 1)
    sections = split_sections(body)
    weekly_reports = tuple(
        line
        for line in sections.get("Weekly Reports", "").splitlines()
        if line.strip().startswith("- ")
    )
    return MonthSynthesis(
        path=path,
        year=int(year_text),
        month=int(month_text),
        date=str(frontmatter["date"]),
        weeks_covered=_frontmatter_list(frontmatter, "weeks_covered"),
        summary=str(frontmatter.get("summary", "")),
        narrative=sections.get("Month Synthesis", "").strip(),
        trend_arc=sections.get("Trend Arc", "").strip(),
        prediction_review=sections.get("Prediction Review", "").strip(),
        weekly_reports=weekly_reports,
        themes=_frontmatter_list(frontmatter, "themes"),
        persistent_themes=_frontmatter_list(frontmatter, "persistent_themes"),
        accelerating_themes=_frontmatter_list(frontmatter, "accelerating_themes"),
        weakening_themes=_frontmatter_list(frontmatter, "weakening_themes"),
        key_gaps=_frontmatter_list(frontmatter, "key_gaps"),
        top_repos=_frontmatter_list(frontmatter, "top_repos"),
        source_checksum=str(frontmatter.get("source_checksum", "")),
        status=str(frontmatter.get("status", "generated")),
    )


def ensure_month_synthesis(items: list[Any], analyzed_dir: Path) -> MonthSynthesis:
    if not items:
        raise ValueError("Cannot synthesize an empty month")
    pack = build_month_synthesis_pack(items)
    checksum = source_checksum(pack)
    path = synthesis_path(analyzed_dir, items[0].year, items[0].month)
    if path.exists():
        cached = load_month_synthesis(path)
        if (
            cached.weeks_covered == tuple(item.week for item in items)
            and cached.source_checksum == checksum
        ):
            return replace(cached, weekly_reports=build_weekly_reports(items))
    synthesis = synthesize_month(items, analyzed_dir, checksum)
    write_month_synthesis(synthesis)
    return synthesis

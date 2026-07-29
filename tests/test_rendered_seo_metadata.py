from __future__ import annotations

import os
import shutil
import subprocess
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

import pytest


class HeadMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.description: str | None = None
        self.google_site_verification: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.description = attrs_dict.get("content", "")
        if (
            tag.lower() == "meta"
            and attrs_dict.get("name", "").lower() == "google-site-verification"
        ):
            self.google_site_verification = attrs_dict.get("content", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def test_rendered_pages_have_unique_titles_and_meta_descriptions(tmp_path: Path) -> None:
    if shutil.which("hugo") is None:
        pytest.skip("Hugo binary is required to render SEO metadata fixtures")

    repo_root = Path(__file__).resolve().parents[1]
    rendered_site = tmp_path / "public"
    subprocess.run(
        ["hugo", "--minify", "--quiet", "--destination", str(rendered_site)],
        cwd=repo_root,
        check=True,
    )

    values: dict[tuple[str, str], list[Path]] = defaultdict(list)
    missing: list[str] = []
    for html_file in sorted(rendered_site.rglob("*.html")):
        parser = HeadMetadataParser()
        parser.feed(html_file.read_text(encoding="utf-8", errors="ignore"))
        title = parser.title
        description = (parser.description or "").strip()
        rel_path = html_file.relative_to(rendered_site)
        if not title:
            missing.append(f"{rel_path}: empty <title>")
        if not description:
            missing.append(f"{rel_path}: empty meta description")
        values[("title", title)].append(rel_path)
        values[("meta description", description)].append(rel_path)

    duplicates = []
    for (kind, value), paths in values.items():
        if value and len(paths) > 1:
            rendered_paths = ", ".join(str(path) for path in paths)
            duplicates.append(f"Duplicate {kind} {value!r}: {rendered_paths}")

    assert not missing
    assert not duplicates


def test_gsc_site_verification_meta_requires_hugo_env_override(tmp_path: Path) -> None:
    if shutil.which("hugo") is None:
        pytest.skip("Hugo binary is required to render GSC verification metadata")

    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.pop("HUGO_PARAMS_GSC_SITE_VERIFICATION", None)
    env.pop("HUGO_PARAMS_ANALYTICS_GOOGLE_SITEVERIFICATIONTAG", None)

    default_site = tmp_path / "default"
    subprocess.run(
        ["hugo", "--minify", "--quiet", "--destination", str(default_site)],
        cwd=repo_root,
        env=env,
        check=True,
    )
    default_parser = HeadMetadataParser()
    default_parser.feed((default_site / "index.html").read_text(encoding="utf-8"))
    assert default_parser.google_site_verification is None

    verified_site = tmp_path / "verified"
    env["HUGO_PARAMS_GSC_SITE_VERIFICATION"] = "testtoken123"
    subprocess.run(
        ["hugo", "--minify", "--quiet", "--destination", str(verified_site)],
        cwd=repo_root,
        env=env,
        check=True,
    )
    verified_html = (verified_site / "index.html").read_text(encoding="utf-8")
    verified_parser = HeadMetadataParser()
    verified_parser.feed(verified_html)
    assert verified_parser.google_site_verification == "testtoken123"


def test_gsc_site_verification_prefers_new_config_over_legacy(
    tmp_path: Path,
) -> None:
    if shutil.which("hugo") is None:
        pytest.skip("Hugo binary is required to render GSC verification metadata")

    repo_root = Path(__file__).resolve().parents[1]
    override_config = tmp_path / "gsc-precedence.toml"
    override_config.write_text(
        """
[params]
  gsc_site_verification = "newtoken123"

[params.analytics.google]
  SiteVerificationTag = "legacytoken456"
""".strip(),
        encoding="utf-8",
    )

    rendered_site = tmp_path / "new-precedence"
    subprocess.run(
        [
            "hugo",
            "--minify",
            "--quiet",
            "--config",
            f"hugo.toml,{override_config}",
            "--destination",
            str(rendered_site),
        ],
        cwd=repo_root,
        check=True,
    )
    parser = HeadMetadataParser()
    parser.feed((rendered_site / "index.html").read_text(encoding="utf-8"))
    assert parser.google_site_verification == "newtoken123"


def test_gsc_site_verification_legacy_config_remains_fallback(tmp_path: Path) -> None:
    if shutil.which("hugo") is None:
        pytest.skip("Hugo binary is required to render GSC verification metadata")

    repo_root = Path(__file__).resolve().parents[1]
    legacy_config = tmp_path / "gsc-legacy.toml"
    legacy_config.write_text(
        """
[params.analytics.google]
  SiteVerificationTag = "legacytoken456"
""".strip(),
        encoding="utf-8",
    )

    rendered_site = tmp_path / "legacy"
    subprocess.run(
        [
            "hugo",
            "--minify",
            "--quiet",
            "--config",
            f"hugo.toml,{legacy_config}",
            "--destination",
            str(rendered_site),
        ],
        cwd=repo_root,
        check=True,
    )
    parser = HeadMetadataParser()
    parser.feed((rendered_site / "index.html").read_text(encoding="utf-8"))
    assert parser.google_site_verification == "legacytoken456"

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

import pytest


class HeadMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.description: str | None = None
        self.google_site_verification: str | None = None
        self.meta: dict[tuple[str, str], list[str]] = defaultdict(list)
        self.links: dict[str, list[str]] = defaultdict(list)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.description = attrs_dict.get("content", "")
        if tag.lower() == "meta":
            for attribute in ("name", "property"):
                key = attrs_dict.get(attribute, "").lower()
                if key:
                    self.meta[(attribute, key)].append(attrs_dict.get("content", ""))
        if tag.lower() == "link" and attrs_dict.get("rel"):
            for relation in attrs_dict["rel"].lower().split():
                self.links[relation].append(attrs_dict.get("href", ""))
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


class JsonLdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_json_ld = False
        self.json_ld: list[dict[str, object]] = []
        self.json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        self.in_json_ld = (
            tag.lower() == "script" and attrs_dict.get("type", "").lower() == "application/ld+json"
        )
        if self.in_json_ld:
            self.json_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.in_json_ld:
            parsed = json.loads("".join(self.json_parts))
            assert isinstance(parsed, dict)
            self.json_ld.append(parsed)
            self.in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self.in_json_ld:
            self.json_parts.append(data)


@pytest.fixture(scope="module")
def rendered_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    if shutil.which("hugo") is None:
        pytest.skip("Hugo binary is required to render SEO metadata fixtures")

    repo_root = Path(__file__).resolve().parents[1]
    destination = tmp_path_factory.mktemp("rendered-seo") / "public"
    subprocess.run(
        ["hugo", "--minify", "--quiet", "--destination", str(destination)],
        cwd=repo_root,
        check=True,
    )
    return destination


def _parse_html(path: Path) -> tuple[HeadMetadataParser, JsonLdParser]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    metadata = HeadMetadataParser()
    metadata.feed(content)
    schemas = JsonLdParser()
    schemas.feed(content)
    return metadata, schemas


def _assert_absolute_schema_urls(value: object, path: Path, key: str = "") -> None:
    url_keys = {"@id", "codeRepository", "isBasedOn", "item", "url"}
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            _assert_absolute_schema_urls(child_value, path, child_key)
    elif isinstance(value, list):
        for child_value in value:
            _assert_absolute_schema_urls(child_value, path, key)
    elif key in url_keys and isinstance(value, str):
        assert urlparse(value).scheme in {"http", "https"}, f"{path}: {key}={value!r}"


def test_rendered_page_classes_emit_appropriate_schema(rendered_site: Path) -> None:
    expected_types = {
        "weekly/2026/w31/index.html": {"Article", "BreadcrumbList"},
        "topics/ai-coding-agents/index.html": {
            "CollectionPage",
            "ItemList",
            "BreadcrumbList",
        },
        "data/most-starred-mcp-projects/index.html": {
            "Dataset",
            "ItemList",
            "BreadcrumbList",
        },
        "repo/anthropics-claude-code/index.html": {
            "WebPage",
            "SoftwareSourceCode",
            "BreadcrumbList",
        },
    }
    for relative_path, expected in expected_types.items():
        _, parser = _parse_html(rendered_site / relative_path)
        actual = {str(document["@type"]) for document in parser.json_ld}
        assert expected <= actual, f"{relative_path}: expected {expected}, got {actual}"

    for relative_path in (
        "data/most-starred-mcp-projects/index.html",
        "repo/anthropics-claude-code/index.html",
    ):
        _, parser = _parse_html(rendered_site / relative_path)
        assert "Article" not in {document["@type"] for document in parser.json_ld}


def test_site_wide_metadata_json_ld_and_breadcrumb_contracts(rendered_site: Path) -> None:
    failures: list[str] = []
    for html_file in sorted(rendered_site.rglob("*.html")):
        relative_path = html_file.relative_to(rendered_site)
        metadata, schemas = _parse_html(html_file)
        canonical = metadata.links["canonical"]
        if len(canonical) != 1 or not canonical[0].startswith("https://claracle.com/"):
            failures.append(f"{relative_path}: invalid canonical {canonical}")
            continue

        required_social = {
            ("property", "og:url"),
            ("property", "og:title"),
            ("property", "og:description"),
            ("property", "og:image"),
            ("property", "og:image:alt"),
            ("property", "og:image:width"),
            ("property", "og:image:height"),
            ("name", "twitter:card"),
            ("name", "twitter:title"),
            ("name", "twitter:description"),
            ("name", "twitter:image"),
            ("name", "twitter:image:alt"),
        }
        missing = sorted(
            key
            for key in required_social
            if not metadata.meta[key] or not metadata.meta[key][0].strip()
        )
        if missing:
            failures.append(f"{relative_path}: missing social fields {missing}")
            continue
        if metadata.meta[("property", "og:url")] != canonical:
            failures.append(f"{relative_path}: og:url differs from canonical")
        if metadata.meta[("name", "twitter:image")] != metadata.meta[("property", "og:image")]:
            failures.append(f"{relative_path}: twitter:image differs from og:image")
        if (
            metadata.meta[("name", "twitter:image:alt")]
            != metadata.meta[("property", "og:image:alt")]
        ):
            failures.append(f"{relative_path}: twitter:image:alt differs from og:image:alt")
        for dimension in ("og:image:width", "og:image:height"):
            value = metadata.meta[("property", dimension)][0]
            if not value.isdigit() or int(value) <= 0:
                failures.append(f"{relative_path}: invalid {dimension} {value!r}")

        for document in schemas.json_ld:
            _assert_absolute_schema_urls(document, relative_path)
        if relative_path != Path("index.html"):
            breadcrumbs = [
                document
                for document in schemas.json_ld
                if document.get("@type") == "BreadcrumbList"
            ]
            if not breadcrumbs:
                failures.append(f"{relative_path}: expected a BreadcrumbList")
                continue
            for breadcrumb in breadcrumbs:
                items = breadcrumb.get("itemListElement", [])
                positions = [item.get("position") for item in items]
                if positions != list(range(1, len(items) + 1)):
                    failures.append(f"{relative_path}: invalid breadcrumb positions {positions}")

    assert not failures, "\n".join(failures)


def test_rendered_xml_is_valid_absolute_and_has_no_news_sitemap(
    rendered_site: Path,
) -> None:
    xml_files = sorted(rendered_site.rglob("*.xml"))
    assert xml_files
    assert not (rendered_site / "news-sitemap.xml").exists()
    for xml_file in xml_files:
        root = ElementTree.parse(xml_file).getroot()
        assert "http://www.google.com/schemas/sitemap-news" not in xml_file.read_text(
            encoding="utf-8"
        )
        for element in root.iter():
            local_name = element.tag.rsplit("}", 1)[-1]
            if local_name in {"link", "loc"} and (element.text or "").strip():
                assert (element.text or "").strip().startswith("https://claracle.com/")
            href = element.attrib.get("href")
            if href:
                assert urlparse(href).scheme in {"http", "https"}


def _render_social_fixtures(
    tmp_path: Path,
    fixtures: dict[str, tuple[str, bool]],
) -> tuple[subprocess.CompletedProcess[str], dict[str, Path]]:
    repo_root = Path(__file__).resolve().parents[1]
    fixture_root = repo_root / "content/seo-contract-fixtures"
    output_paths: dict[str, Path] = {}
    try:
        fixture_root.mkdir(parents=True)
        (fixture_root / "_index.md").write_text(
            "---\ntitle: SEO contract fixtures\ndate: 2020-01-01\n---\n",
            encoding="utf-8",
        )
        for slug, (front_matter, local_image) in fixtures.items():
            page_dir = fixture_root / slug
            page_dir.mkdir()
            (page_dir / "index.md").write_text(
                f"---\ntitle: Social fixture\ndate: 2020-01-01\n{front_matter}---\nFixture body.\n",
                encoding="utf-8",
            )
            if local_image:
                shutil.copyfile(
                    repo_root / "static/images/squadscope-social-card.png",
                    page_dir / "social.png",
                )
            output_paths[slug] = tmp_path / f"public/seo-contract-fixtures/{slug}/index.html"
        result = subprocess.run(
            ["hugo", "--minify", "--destination", str(tmp_path / "public")],
            cwd=repo_root,
            check=False,
            text=True,
            capture_output=True,
        )
    finally:
        shutil.rmtree(fixture_root, ignore_errors=True)
    return result, output_paths


@pytest.mark.skipif(shutil.which("hugo") is None, reason="hugo is not installed")
def test_social_images_have_positive_dimensions_and_alt(tmp_path: Path) -> None:
    result, output_paths = _render_social_fixtures(
        tmp_path,
        {
            "default": ("", False),
            "local": (
                'cover:\n  image: "social.png"\n  relative: true\n  alt: "Local fixture image"\n',
                True,
            ),
            "remote": (
                'og_image: "https://cdn.example.com/social.png"\n'
                'og_image_alt: "Remote fixture image"\n'
                "og_image_width: 1600\nog_image_height: 900\n",
                False,
            ),
        },
    )
    assert result.returncode == 0, result.stderr
    for slug, expected_dimensions in {
        "default": (1200, 630),
        "local": (1200, 630),
        "remote": (1600, 900),
    }.items():
        metadata, _ = _parse_html(output_paths[slug])
        assert metadata.meta[("property", "og:image:alt")][0]
        dimensions = tuple(
            int(metadata.meta[("property", name)][0])
            for name in ("og:image:width", "og:image:height")
        )
        assert dimensions == expected_dimensions


@pytest.mark.skipif(shutil.which("hugo") is None, reason="hugo is not installed")
def test_remote_social_image_without_dimensions_fails_render(tmp_path: Path) -> None:
    result, _ = _render_social_fixtures(
        tmp_path,
        {
            "remote-missing-dimensions": (
                'og_image: "https://cdn.example.com/social.png"\n'
                'og_image_alt: "Remote fixture image"\n',
                False,
            )
        },
    )
    assert result.returncode != 0
    assert "requires positive og_image_width and og_image_height" in result.stderr


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

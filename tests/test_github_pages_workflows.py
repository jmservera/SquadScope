from __future__ import annotations

from pathlib import Path

import yaml


def _workflow(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def test_production_workflows_use_pinned_github_pages_boundary() -> None:
    for relative in (
        ".github/workflows/deploy-site.yml",
        ".github/workflows/crawl-and-publish.yml",
    ):
        text = Path(relative).read_text(encoding="utf-8")
        workflow = _workflow(relative)
        deploy = workflow["jobs"]["deploy"]
        rendered_steps = "\n".join(
            f"{step.get('uses', '')}\n{step.get('run', '')}\n{step.get('with', '')}"
            for step in deploy["steps"]
        )
        assert "cloudflare/wrangler-action@" not in text
        assert "CLOUDFLARE_" not in text
        assert "actions/configure-pages@983d7736d9b0ae728b81ab479565c72886d7745b" in text
        assert "actions/upload-pages-artifact@56afc609e74202658d3ffba0e8f6dda462b719fa" in text
        assert "actions/deploy-pages@d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e" in rendered_steps
        assert "scripts/verify_repository_migration_http.py" in rendered_steps
        assert deploy["environment"]["name"] == "github-pages"


def test_repository_source_is_not_hydrated_from_publish() -> None:
    for relative in (
        ".github/workflows/deploy-site.yml",
        ".github/workflows/crawl-and-publish.yml",
        ".github/workflows/generate-data-pages.yml",
    ):
        assert "content/repo/" not in Path(relative).read_text(encoding="utf-8")


def test_cloudflare_redirect_file_is_absent() -> None:
    assert not Path("static/_redirects").exists()

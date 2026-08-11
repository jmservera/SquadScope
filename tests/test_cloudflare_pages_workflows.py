from __future__ import annotations

from pathlib import Path

import yaml


def _workflow(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def test_production_workflows_use_one_pinned_cloudflare_boundary() -> None:
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
        assert "actions/configure-pages@" not in text
        assert "actions/deploy-pages@" not in text
        assert "actions/upload-pages-artifact@" not in text
        assert (
            "cloudflare/wrangler-action@9acf94ace14e7dc412b076f2c5c20b8ce93c79cd" in rendered_steps
        )
        assert "wranglerVersion': '4.120.1" in rendered_steps
        assert "pages deploy public --project-name=claracle --branch=main" in rendered_steps
        assert "secrets.CLOUDFLARE_API_TOKEN" in rendered_steps
        assert "secrets.CLOUDFLARE_ACCOUNT_ID" in rendered_steps
        assert "scripts/verify_repository_migration_http.py" in rendered_steps
        assert deploy["environment"]["name"] == "cloudflare-pages"


def test_repository_source_is_not_hydrated_from_publish() -> None:
    for relative in (
        ".github/workflows/deploy-site.yml",
        ".github/workflows/crawl-and-publish.yml",
        ".github/workflows/generate-data-pages.yml",
    ):
        assert "content/repo/" not in Path(relative).read_text(encoding="utf-8")


def test_approved_redirect_rule_is_one_hop_and_permanent() -> None:
    assert Path("static/_redirects").read_text(encoding="utf-8") == (
        "/repo/pewdiepie-archdaemon-odysseus/ /repo/odysseus-dev-odysseus/ 301\n"
    )

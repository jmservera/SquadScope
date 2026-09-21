from __future__ import annotations

import json
from pathlib import Path

from scripts import ai_output_guard
from scripts.analyze_fallback import estimate_tokens
from scripts.canary_token import generate_canary, inject_canary


def test_rotate_and_validate_clean_output(tmp_path: Path) -> None:
    prompt_path = tmp_path / "prompt.md"
    token_path = tmp_path / "canary.txt"
    preflight_path = tmp_path / "preflight.json"
    output_path = tmp_path / "output.md"
    original_canary = generate_canary()
    prompt_path.write_text(
        inject_canary("# Analysis\n\nUse the supplied evidence.\n", original_canary),
        encoding="utf-8",
    )
    token_path.write_text(original_canary + "\n", encoding="utf-8")
    preflight_path.write_text(
        json.dumps(
            {
                "prompt_token_budget": 1000,
                "components": [{"name": "rendered_prompt"}],
            }
        ),
        encoding="utf-8",
    )
    output_path.write_text("## Trends\n\nEvidence-backed result.\n", encoding="utf-8")

    assert (
        ai_output_guard.main(
            [
                "rotate",
                "--prompt",
                str(prompt_path),
                "--token-file",
                str(token_path),
                "--preflight-report",
                str(preflight_path),
            ]
        )
        == 0
    )
    rotated_canary = token_path.read_text(encoding="utf-8").strip()
    assert rotated_canary != original_canary
    assert original_canary not in prompt_path.read_text(encoding="utf-8")
    report = json.loads(preflight_path.read_text(encoding="utf-8"))
    assert report["prompt_checksum_sha256"]
    assert report["components"][0]["checksum_sha256"] == report["prompt_checksum_sha256"]
    assert (
        ai_output_guard.main(
            ["validate", "--output", str(output_path), "--token-file", str(token_path)]
        )
        == 0
    )


def test_rotate_uses_utf8_byte_token_estimate(tmp_path: Path) -> None:
    prompt_path = tmp_path / "prompt.md"
    token_path = tmp_path / "canary.txt"
    preflight_path = tmp_path / "preflight.json"
    original_canary = generate_canary()
    prompt_path.write_text(
        inject_canary("# Analysis\n\nEvidence: 日本語 🚀\n", original_canary),
        encoding="utf-8",
    )
    token_path.write_text(original_canary + "\n", encoding="utf-8")
    preflight_path.write_text(
        json.dumps(
            {
                "prompt_token_budget": 1000,
                "components": [{"name": "rendered_prompt"}],
            }
        ),
        encoding="utf-8",
    )

    ai_output_guard.rotate_canary(prompt_path, token_path, preflight_path)

    prompt = prompt_path.read_text(encoding="utf-8")
    report = json.loads(preflight_path.read_text(encoding="utf-8"))
    expected_tokens = estimate_tokens(prompt)
    assert report["prompt_tokens"] == expected_tokens
    assert report["rendered_prompt_estimate"]["tokens"] == expected_tokens
    assert report["components"][0]["token_estimate"] == expected_tokens


def test_rotate_refreshes_all_preflight_artifacts(tmp_path: Path) -> None:
    prompt_path = tmp_path / "prompt.md"
    token_path = tmp_path / "canary.txt"
    preflight_path = tmp_path / "analysis-input-manifest.json"
    legacy_preflight_path = tmp_path / "analysis-preflight.json"
    preflight_md_path = tmp_path / "analysis-preflight.md"
    original_canary = generate_canary()
    prompt_path.write_text(
        inject_canary("# Analysis\n\nUse the supplied evidence.\n", original_canary),
        encoding="utf-8",
    )
    token_path.write_text(original_canary + "\n", encoding="utf-8")
    report = {
        "prompt_token_budget": 1000,
        "prompt_tokens": 1,
        "prompt_bytes": 1,
        "prompt_checksum_sha256": "stale",
        "degraded": False,
        "degradation_reason": None,
        "publish_eligible": True,
        "promotion_policy": "eligible-only",
        "fallback_policy": "none",
        "deterministic_slices": ["raw"],
        "components": [
            {
                "name": "rendered_prompt",
                "included": True,
                "bytes": 1,
                "token_estimate": 1,
                "checksum_sha256": "stale",
                "path": None,
                "inclusion_reason": "required",
                "compaction_decision": "none",
            }
        ],
    }
    preflight_path.write_text(json.dumps(report), encoding="utf-8")
    legacy_preflight_path.write_text(json.dumps(report), encoding="utf-8")
    preflight_md_path.write_text("stale\n", encoding="utf-8")

    ai_output_guard.rotate_canary(
        prompt_path,
        token_path,
        preflight_path,
        legacy_preflight_path,
        preflight_md_path,
    )

    canonical = preflight_path.read_text(encoding="utf-8")
    assert legacy_preflight_path.read_text(encoding="utf-8") == canonical
    refreshed = json.loads(canonical)
    markdown = preflight_md_path.read_text(encoding="utf-8")
    assert refreshed["prompt_checksum_sha256"] != "stale"
    assert refreshed["prompt_checksum_sha256"] in markdown
    assert f"`{refreshed['prompt_tokens']}` tokens" in markdown


def test_validate_rejects_canary_leak(tmp_path: Path) -> None:
    token_path = tmp_path / "canary.txt"
    output_path = tmp_path / "output.md"
    canary = generate_canary()
    token_path.write_text(canary + "\n", encoding="utf-8")
    output_path.write_text(f"Leaked internal marker: {canary}\n", encoding="utf-8")

    assert (
        ai_output_guard.main(
            ["validate", "--output", str(output_path), "--token-file", str(token_path)]
        )
        == 1
    )


def test_validate_rejects_prompt_boundary_leak(tmp_path: Path) -> None:
    token_path = tmp_path / "canary.txt"
    output_path = tmp_path / "output.md"
    token_path.write_text(generate_canary() + "\n", encoding="utf-8")
    output_path.write_text(
        "## Analysis\n\n<untrusted-content>replayed prompt</untrusted-content>\n",
        encoding="utf-8",
    )

    assert (
        ai_output_guard.main(
            ["validate", "--output", str(output_path), "--token-file", str(token_path)]
        )
        == 1
    )

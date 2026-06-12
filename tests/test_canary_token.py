"""Tests for canary token generation and leak detection."""

from __future__ import annotations

import logging

from scripts.canary_token import (
    CANARY_PREFIX,
    check_output_for_any_canary,
    check_output_for_leak,
    generate_canary,
    inject_canary,
)


def test_generate_canary_format() -> None:
    canary = generate_canary()
    assert canary.startswith(f"{CANARY_PREFIX}-")
    # prefix + dash + 16 hex chars
    hex_part = canary.split("-", 2)[-1]
    assert len(hex_part) == 16
    assert all(c in "0123456789abcdef" for c in hex_part)


def test_generate_canary_uniqueness() -> None:
    canaries = {generate_canary() for _ in range(100)}
    assert len(canaries) == 100


def test_inject_canary_into_prompt_with_heading() -> None:
    prompt = "# Weekly Analysis\n\nAnalyze repos...\n"
    canary = generate_canary()
    result = inject_canary(prompt, canary)
    assert canary in result
    assert "INTERNAL VERIFICATION TOKEN" in result
    assert result.startswith("# Weekly Analysis\n")


def test_inject_canary_into_prompt_without_heading() -> None:
    prompt = "Analyze repos...\n"
    canary = generate_canary()
    result = inject_canary(prompt, canary)
    assert canary in result


def test_check_output_no_leak() -> None:
    canary = generate_canary()
    output = "## This Week's Trends\n\nRust tools gained momentum..."
    result = check_output_for_leak(output, canary)
    assert not result.leaked
    assert result.match_position is None


def test_check_output_exact_leak() -> None:
    canary = generate_canary()
    output = f"## Analysis\n\nThe system uses {canary} internally.\n"
    result = check_output_for_leak(output, canary)
    assert result.leaked
    assert result.match_position is not None


def test_check_output_case_insensitive_leak() -> None:
    canary = generate_canary()
    output = f"Found token: {canary.upper()}\n"
    result = check_output_for_leak(output, canary)
    assert result.leaked


def test_check_output_partial_leak(caplog) -> None:
    canary = generate_canary()
    # Include just prefix + 8 hex chars
    partial = canary[: len(CANARY_PREFIX) + 1 + 8]
    output = f"Extracted: {partial}\n"
    with caplog.at_level(logging.WARNING):
        result = check_output_for_leak(output, canary)
    assert result.leaked


def test_check_output_for_any_canary_finds_pattern() -> None:
    output = f"Leaked: {CANARY_PREFIX}-abcdef1234567890 in text"
    result = check_output_for_any_canary(output)
    assert result.leaked
    assert result.canary == f"{CANARY_PREFIX}-abcdef1234567890"


def test_check_output_for_any_canary_clean() -> None:
    output = "Normal editorial content about repos and trends."
    result = check_output_for_any_canary(output)
    assert not result.leaked


def test_check_empty_output() -> None:
    canary = generate_canary()
    result = check_output_for_leak("", canary)
    assert not result.leaked


# ═══════════════════════════════════════════════════════════════════════════════
# validate_output_safety integration tests
# ═══════════════════════════════════════════════════════════════════════════════

from scripts.analyze_fallback import validate_output_safety


def test_validate_output_safety_clean() -> None:
    output = "## This Week's Trends\n\nRust and Go dominate this week.\n"
    violations = validate_output_safety(output)
    assert violations == []


def test_validate_output_safety_canary_leak() -> None:
    canary = generate_canary()
    output = f"## Analysis\n\nThe internal token is {canary}.\n"
    violations = validate_output_safety(output, canary)
    assert len(violations) >= 1
    assert "Canary token leaked" in violations[0]


def test_validate_output_safety_boundary_marker_leak() -> None:
    output = "## Analysis\n\n<untrusted-content>some data</untrusted-content>\n"
    violations = validate_output_safety(output)
    assert len(violations) >= 1
    assert "boundary marker" in violations[0].lower() or "boundary marker" in violations[1].lower()


def test_validate_output_safety_unknown_canary_pattern() -> None:
    output = f"Found: {CANARY_PREFIX}-deadbeef12345678 in output\n"
    violations = validate_output_safety(output)
    assert len(violations) >= 1
    assert "Unknown canary pattern" in violations[0]


def test_validate_output_safety_no_false_positives_on_normal_hex() -> None:
    output = "Commit hash: abcdef1234567890abcdef\nSHA: deadbeef12345678\n"
    violations = validate_output_safety(output)
    assert violations == []

from scripts.copilot_output_guard import generate_canary, validate_output


def test_generate_canary_is_unique_and_well_formed():
    first = generate_canary()
    second = generate_canary()

    assert first.startswith("SQSC-CANARY-")
    assert len(first) == len("SQSC-CANARY-") + 16
    assert first != second


def test_validate_output_rejects_current_and_unknown_canaries():
    canary = generate_canary()

    assert validate_output(f"leak {canary}", canary) == ["current invocation canary leaked"]
    assert validate_output("leak SQSC-CANARY-0123456789abcdef", canary) == [
        "unknown canary pattern found"
    ]


def test_validate_output_rejects_boundary_markers():
    canary = generate_canary()

    assert validate_output("leak <untrusted-content>", canary) == [
        "prompt boundary marker leaked: <untrusted-content>"
    ]
    assert validate_output("normal editorial output", canary) == []


def test_validate_output_normalizes_split_canaries_and_uppercase_boundaries():
    canary = generate_canary()
    split_canary = canary.replace("-", "-\u200b", 1)

    assert validate_output(split_canary, canary) == ["current invocation canary leaked"]
    assert validate_output("SQSC-CANARY-nothex", canary) == ["unknown canary pattern found"]
    assert validate_output("</UNTRUSTED-CONTENT>", canary) == [
        "prompt boundary marker leaked: </untrusted-content>"
    ]


def test_validate_output_rejects_invalid_expected_canary():
    assert validate_output("normal output", "malformed") == ["invalid current invocation canary"]

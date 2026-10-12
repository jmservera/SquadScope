import pytest

from scripts.check_dependency_lock import check_report, read_pins


def report(**versions):
    return {
        "install": [
            {"metadata": {"name": name, "version": version}} for name, version in versions.items()
        ]
    }


def test_lock_allows_existing_versions_when_index_has_newer_releases(tmp_path):
    lock = tmp_path / "requirements.lock"
    lock.write_text("pydantic==2.13.5\npydantic_core==2.46.5\n")
    check_report(read_pins(lock), report(pydantic="2.13.5", **{"pydantic-core": "2.46.5"}))


@pytest.mark.parametrize(
    "resolved",
    [
        report(pydantic="2.14.1"),
        report(pydantic="2.13.5", **{"pydantic-core": "2.46.5"}),
        report(),
    ],
)
def test_lock_rejects_changed_missing_or_unpinned_dependencies(resolved):
    with pytest.raises(ValueError, match="Incomplete or incompatible"):
        check_report({"pydantic": "2.13.5"}, resolved)


@pytest.mark.parametrize("entry", ["pydantic>=2", "", "pydantic==2\nPydantic==2"])
def test_lock_rejects_unpinned_empty_and_duplicate_entries(tmp_path, entry):
    lock = tmp_path / "requirements.lock"
    lock.write_text(entry)
    with pytest.raises(ValueError):
        read_pins(lock)

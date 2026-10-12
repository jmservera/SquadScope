import subprocess
from pathlib import Path
from zipfile import ZipFile

import pytest
import yaml

from scripts.check_dependency_lock import check_report, read_pins, validate_lock


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


@pytest.mark.parametrize(
    "entry",
    [
        "pydantic>=2",
        "",
        "pydantic==2\nPydantic==2",
        "pydantic-core==2\npydantic_core==2",
        "pydantic==",
        "not a requirement",
        "-r other.lock",
        "pydantic==2.*",
    ],
)
def test_lock_rejects_unpinned_empty_and_duplicate_entries(tmp_path, entry):
    lock = tmp_path / "requirements.lock"
    lock.write_text(entry)
    with pytest.raises(ValueError):
        read_pins(lock)


@pytest.fixture
def offline_index(tmp_path, monkeypatch):
    """Give the real pip resolver a small, network-free wheel index."""
    for name, version, dependencies in [
        ("defusedxml", "0.7.1", []),
        ("defusedxml", "0.8.0", []),
        ("six", "1.17.0", []),
        ("parent", "1.0", ["six>=1.17"]),
    ]:
        dist_info = f"{name}-{version}.dist-info"
        with ZipFile(tmp_path / f"{name}-{version}-py3-none-any.whl", "w") as wheel:
            metadata = f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n"
            metadata += "".join(f"Requires-Dist: {dependency}\n" for dependency in dependencies)
            wheel.writestr(f"{dist_info}/METADATA", metadata + "\n")
            wheel.writestr(
                f"{dist_info}/WHEEL",
                "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
            )
            wheel.writestr(f"{dist_info}/RECORD", "")
    monkeypatch.setenv("PIP_NO_INDEX", "1")
    monkeypatch.setenv("PIP_FIND_LINKS", str(tmp_path))
    monkeypatch.setenv("PIP_CONFIG_FILE", "/dev/null")
    return tmp_path


def test_real_resolver_rejects_orphan_six_pin(offline_index):
    requirements = offline_index / "requirements.txt"
    lock = offline_index / "requirements.lock"
    requirements.write_text("defusedxml>=0.7,<1\n")
    lock.write_text("defusedxml==0.7.1\nsix==1.17.0\n")
    with pytest.raises(ValueError, match="Incomplete or incompatible lock: six"):
        validate_lock(requirements, lock)


@pytest.mark.parametrize(
    ("roots", "pins", "expected_count"),
    [
        ("defusedxml>=0.7,<1\n", "defusedxml==0.7.1\n", 1),
        ("parent>=1\n", "parent==1.0\nsix==1.17.0\n", 2),
    ],
)
def test_real_resolver_accepts_exact_closure_despite_newer_index_release(
    offline_index, roots, pins, expected_count
):
    requirements = offline_index / "requirements.txt"
    lock = offline_index / "requirements.lock"
    requirements.write_text(roots)
    lock.write_text(pins)
    assert validate_lock(requirements, lock) == expected_count


@pytest.mark.parametrize(
    ("roots", "pins", "error"),
    [
        ("parent>=1\n", "parent==1.0\n", ValueError),
        ("defusedxml>=0.8\n", "defusedxml==0.7.1\n", subprocess.CalledProcessError),
        ("defusedxml>=0.7\n", "defusedxml==0.9.0\n", subprocess.CalledProcessError),
    ],
)
def test_real_resolver_rejects_missing_incompatible_or_unavailable_pins(
    offline_index, roots, pins, error
):
    requirements = offline_index / "requirements.txt"
    lock = offline_index / "requirements.lock"
    requirements.write_text(roots)
    lock.write_text(pins)
    with pytest.raises(error):
        validate_lock(requirements, lock)


def test_ci_audits_deployed_pins_strictly_without_resolving_ranges():
    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/ci.yml").read_text())
    steps = workflow["jobs"]["python"]["steps"]
    install = next(step["run"] for step in steps if step["name"] == "Install Python dependencies")
    audit = next(step["run"] for step in steps if step["name"] == "Audit Python dependencies")
    assert "pip install -r requirements.lock" in install
    assert audit == "python -m pip_audit --strict --disable-pip --no-deps -r requirements.lock"

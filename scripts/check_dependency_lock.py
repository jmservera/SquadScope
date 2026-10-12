"""Validate a complete pinned dependency graph without upgrading it from PyPI."""

import json
import re
import subprocess  # nosec B404 - invoke the current Python's pip with fixed argv, no shell
import sys
from pathlib import Path


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def read_pins(path: Path) -> dict[str, str]:
    pins = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)", line)
        if not match:
            raise ValueError(f"Lock entry must be an exact pin: {line}")
        name, version = match.groups()
        name = normalize(name)
        if name in pins:
            raise ValueError(f"Duplicate lock entry: {name}")
        pins[name] = version
    if not pins:
        raise ValueError("Dependency lock is empty")
    return pins


def check_report(pins: dict[str, str], report: dict) -> None:
    resolved = {
        normalize(item["metadata"]["name"]): item["metadata"]["version"]
        for item in report["install"]
    }
    if resolved != pins:
        differences = sorted(
            name for name in pins.keys() | resolved.keys() if pins.get(name) != resolved.get(name)
        )
        raise ValueError("Incomplete or incompatible lock: " + ", ".join(differences))


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    lock = root / "requirements.lock"
    pins = read_pins(lock)
    # stdout is JSON only; pip progress stays on stderr, and no report file or
    # download URL is exposed. Both inputs force pip to verify compatibility.
    result = subprocess.run(  # nosec B603 - fixed argv and repository-owned paths, no shell
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--dry-run",
            "--ignore-installed",
            "--disable-pip-version-check",
            "--quiet",
            "--report",
            "-",
            "-r",
            str(root / "requirements.txt"),
            "-r",
            str(lock),
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    check_report(pins, json.loads(result.stdout))
    print(f"Verified {len(pins)} compatible exact dependency pins.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as exc:
        if isinstance(exc, subprocess.CalledProcessError):
            print("Dependency resolution failed: review requirements.txt and requirements.lock.")
        else:
            print(str(exc))
        raise SystemExit(1) from exc

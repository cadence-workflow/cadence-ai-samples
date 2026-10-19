"""Copy only this recipe and rerun its offline checks."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
RECIPE_ROOT = HERE.parents[1]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="incident-triage-clean-copy-") as temp:
        destination = Path(temp) / "incident-triage"
        shutil.copytree(
            RECIPE_ROOT,
            destination,
            ignore=shutil.ignore_patterns(
                ".venv",
                ".evidence",
                ".run-state",
                ".state",
                "__pycache__",
                "*.egg-info",
            ),
        )
        implementation = destination / "python" / "bare"
        environment = {
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        commands = (
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-v",
            ],
            [sys.executable, "durability_manifest.py", "--json"],
        )
        for command in commands:
            result = subprocess.run(
                command,
                cwd=implementation,
                env=environment,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
        print("CLEAN COPY PASSED: offline tests and manifest are independent")


if __name__ == "__main__":
    main()

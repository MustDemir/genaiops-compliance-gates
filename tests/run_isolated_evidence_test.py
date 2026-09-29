#!/usr/bin/env python3
"""Run the recorder fault-injection test without changing this checkout."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run():
    with tempfile.TemporaryDirectory(prefix="verify-evidence-") as directory:
        replica = Path(directory) / "repo"
        # This legacy test replaces record_evidence.py temporarily. Never run
        # it against the caller's working copy, even if cleanup is interrupted.
        shutil.copytree(
            ROOT, replica,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.db",
                                         "*.db-journal", "pipeline_report_*.json"),
        )
        result = subprocess.run(
            [sys.executable, str(replica / "pipeline/test_evidence_fail_closed.py")],
            cwd=replica, timeout=300,
        )
        return result.returncode


if __name__ == "__main__":
    sys.exit(run())

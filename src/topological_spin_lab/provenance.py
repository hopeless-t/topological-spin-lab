from __future__ import annotations

import platform as platform_module
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True, slots=True)
class Provenance:
    git_commit: str | None
    python_version: str
    numpy_version: str
    platform: str


def _git_commit(cwd: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = completed.stdout.strip()
    return value or None


def collect_provenance(cwd: Path | None = None) -> Provenance:
    root = cwd if cwd is not None else Path.cwd()
    return Provenance(
        git_commit=_git_commit(root),
        python_version=sys.version.split()[0],
        numpy_version=np.__version__,
        platform=platform_module.platform(),
    )

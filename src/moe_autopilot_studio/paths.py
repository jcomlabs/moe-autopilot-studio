from __future__ import annotations

import os
import sys
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent


def repository_root() -> Path:
    candidate = PACKAGE_DIR.parents[1]
    if (candidate / "pyproject.toml").exists():
        return candidate
    return Path(getattr(sys, "_MEIPASS", PACKAGE_DIR))


def fixtures_dir() -> Path:
    override = os.getenv("STUDIO_FIXTURES_DIR")
    if override:
        return Path(override).resolve()
    for candidate in (repository_root() / "fixtures", Path.cwd() / "fixtures"):
        if candidate.exists():
            return candidate
    return PACKAGE_DIR / "fixtures"


def static_dir() -> Path:
    override = os.getenv("STUDIO_STATIC_DIR")
    if override:
        return Path(override).resolve()
    packaged = PACKAGE_DIR / "static"
    if packaged.exists():
        return packaged
    return repository_root() / "frontend" / "dist"


def data_dir() -> Path:
    if os.name == "nt":
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    target = base / "MoEAutopilotStudio"
    target.mkdir(parents=True, exist_ok=True)
    return target

"""Path helpers for conda's Windows entry point launchers."""

from __future__ import annotations

from .paths import (
    LAUNCHER_KINDS,
    WINDOWS_SUBDIRS,
    get_launcher_name,
    get_launcher_path,
    get_launcher_script_name,
    get_launcher_script_path,
    get_launcher_script_short_path,
    get_launcher_short_path,
    get_launcher_short_paths,
    get_supported_subdirs,
)

__all__ = (
    "LAUNCHER_KINDS",
    "WINDOWS_SUBDIRS",
    "get_launcher_name",
    "get_launcher_path",
    "get_launcher_script_name",
    "get_launcher_script_path",
    "get_launcher_script_short_path",
    "get_launcher_short_path",
    "get_launcher_short_paths",
    "get_supported_subdirs",
)

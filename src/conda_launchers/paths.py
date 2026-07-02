"""Resolve paths for launchers shipped by the conda-launchers package."""

from __future__ import annotations

from os import PathLike
from pathlib import Path
import sys
from typing import Literal

LauncherKind = Literal["cli", "gui"]

LAUNCHER_KINDS: tuple[LauncherKind, ...] = ("cli", "gui")
WINDOWS_SUBDIRS: tuple[str, ...] = ("win-32", "win-64", "win-arm64")

ARCH_BY_SUBDIR = {
    "win-32": "32",
    "win-64": "64",
    "win-arm64": "arm64",
}
SCRIPT_SUFFIX_BY_KIND = {
    "cli": "-script.py",
    "gui": "-script.pyw",
}


def get_supported_subdirs() -> tuple[str, ...]:
    """Return Windows subdirs with launchers shipped by this package."""
    return WINDOWS_SUBDIRS


def get_launcher_name(subdir: str, kind: LauncherKind = "cli") -> str:
    """Return the launcher executable filename for a Windows subdir."""
    if kind not in LAUNCHER_KINDS:
        supported = ", ".join(LAUNCHER_KINDS)
        raise ValueError(
            f"unsupported launcher kind {kind!r}; expected one of {supported}"
        )
    try:
        arch = ARCH_BY_SUBDIR[subdir]
    except KeyError as exc:
        supported = ", ".join(WINDOWS_SUBDIRS)
        raise ValueError(
            f"unsupported Windows subdir {subdir!r}; expected one of {supported}"
        ) from exc
    return f"{kind}-{arch}.exe"


def get_launcher_script_name(subdir: str, kind: LauncherKind = "cli") -> str:
    """Return the script filename used to test the launcher executable."""
    return (
        get_launcher_name(subdir, kind).removesuffix(".exe")
        + SCRIPT_SUFFIX_BY_KIND[kind]
    )


def get_launcher_short_path(subdir: str, kind: LauncherKind = "cli") -> str:
    """Return the conda package path to a launcher executable.

    The returned path always uses POSIX separators because conda package records
    store paths that way.
    """
    return f"Scripts/{get_launcher_name(subdir, kind)}"


def get_launcher_script_short_path(subdir: str, kind: LauncherKind = "cli") -> str:
    """Return the conda package path to the launcher test script."""
    return f"Scripts/{get_launcher_script_name(subdir, kind)}"


def get_launcher_short_paths(kind: LauncherKind = "cli") -> dict[str, str]:
    """Return package paths to launcher executables keyed by Windows subdir."""
    return {subdir: get_launcher_short_path(subdir, kind) for subdir in WINDOWS_SUBDIRS}


def get_launcher_path(
    subdir: str,
    kind: LauncherKind = "cli",
    *,
    prefix: str | PathLike[str] | None = None,
) -> Path:
    """Return the full path to a launcher executable under a prefix."""
    root = Path(sys.prefix if prefix is None else prefix)
    return root.joinpath(*get_launcher_short_path(subdir, kind).split("/"))


def get_launcher_script_path(
    subdir: str,
    kind: LauncherKind = "cli",
    *,
    prefix: str | PathLike[str] | None = None,
) -> Path:
    """Return the full path to a launcher test script under a prefix."""
    root = Path(sys.prefix if prefix is None else prefix)
    return root.joinpath(*get_launcher_script_short_path(subdir, kind).split("/"))

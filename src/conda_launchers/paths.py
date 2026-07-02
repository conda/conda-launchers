"""Resolve paths for launchers shipped by the conda-launchers package."""

from __future__ import annotations

from os import PathLike
from pathlib import Path
import sys
from typing import Literal

LauncherKind = Literal["cli", "gui"]

LAUNCHER_KINDS: tuple[LauncherKind, ...] = ("cli", "gui")
WINDOWS_SUBDIRS: tuple[str, ...] = ("win-32", "win-64", "win-arm64")

_ARCH_BY_SUBDIR = {
    "win-32": "32",
    "win-64": "64",
    "win-arm64": "arm64",
}
_SCRIPT_SUFFIX_BY_KIND = {
    "cli": "-script.py",
    "gui": "-script.pyw",
}


def get_supported_subdirs() -> tuple[str, ...]:
    """Return Windows subdirs with launchers shipped by this package."""
    return WINDOWS_SUBDIRS


def get_launcher_name(subdir: str, kind: LauncherKind = "cli") -> str:
    """Return the launcher executable filename for a Windows subdir."""
    return f"{_validate_kind(kind)}-{_arch_for_subdir(subdir)}.exe"


def get_launcher_script_name(subdir: str, kind: LauncherKind = "cli") -> str:
    """Return the script filename used to test the launcher executable."""
    kind = _validate_kind(kind)
    return f"{kind}-{_arch_for_subdir(subdir)}{_SCRIPT_SUFFIX_BY_KIND[kind]}"


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
    return _prefix_path(prefix, get_launcher_short_path(subdir, kind))


def get_launcher_script_path(
    subdir: str,
    kind: LauncherKind = "cli",
    *,
    prefix: str | PathLike[str] | None = None,
) -> Path:
    """Return the full path to a launcher test script under a prefix."""
    return _prefix_path(prefix, get_launcher_script_short_path(subdir, kind))


def _arch_for_subdir(subdir: str) -> str:
    try:
        return _ARCH_BY_SUBDIR[subdir]
    except KeyError as exc:
        supported = ", ".join(WINDOWS_SUBDIRS)
        raise ValueError(
            f"unsupported Windows subdir {subdir!r}; expected one of {supported}"
        ) from exc


def _validate_kind(kind: str) -> LauncherKind:
    if kind in LAUNCHER_KINDS:
        return kind  # type: ignore[return-value]
    supported = ", ".join(LAUNCHER_KINDS)
    raise ValueError(f"unsupported launcher kind {kind!r}; expected one of {supported}")


def _prefix_path(prefix: str | PathLike[str] | None, short_path: str) -> Path:
    root = Path(sys.prefix if prefix is None else prefix)
    return root.joinpath(*short_path.split("/"))

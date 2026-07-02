from __future__ import annotations

from pathlib import Path
import sys
from typing import TYPE_CHECKING

import pytest

from conda_launchers import (
    get_launcher_name,
    get_launcher_path,
    get_launcher_script_name,
    get_launcher_script_path,
    get_launcher_script_short_path,
    get_launcher_short_path,
    get_launcher_short_paths,
    get_supported_subdirs,
)

if TYPE_CHECKING:
    from pytest import MonkeyPatch


def test_get_supported_subdirs():
    assert get_supported_subdirs() == ("win-32", "win-64", "win-arm64")


@pytest.mark.parametrize(
    ("subdir", "kind", "expected"),
    (
        ("win-64", "cli", "cli-64.exe"),
        ("win-arm64", "gui", "gui-arm64.exe"),
    ),
)
def test_get_launcher_name(subdir: str, kind: str, expected: str):
    assert get_launcher_name(subdir, kind) == expected  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("subdir", "kind", "expected"),
    (
        ("win-32", "cli", "cli-32-script.py"),
        ("win-64", "gui", "gui-64-script.pyw"),
    ),
)
def test_get_launcher_script_name(subdir: str, kind: str, expected: str):
    assert get_launcher_script_name(subdir, kind) == expected  # type: ignore[arg-type]


def test_get_short_paths():
    assert get_launcher_short_path("win-64") == "Scripts/cli-64.exe"
    assert (
        get_launcher_script_short_path("win-arm64", "gui")
        == "Scripts/gui-arm64-script.pyw"
    )


def test_get_launcher_short_paths():
    assert get_launcher_short_paths() == {
        "win-32": "Scripts/cli-32.exe",
        "win-64": "Scripts/cli-64.exe",
        "win-arm64": "Scripts/cli-arm64.exe",
    }


def test_get_launcher_path_uses_provided_prefix():
    prefix = Path("prefix")

    assert get_launcher_path("win-64", prefix=prefix) == (
        prefix / "Scripts" / "cli-64.exe"
    )
    assert get_launcher_script_path("win-64", "gui", prefix=prefix) == (
        prefix / "Scripts" / "gui-64-script.pyw"
    )


def test_get_launcher_path_defaults_to_sys_prefix(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(sys, "prefix", "prefix")

    assert get_launcher_path("win-32") == Path("prefix") / "Scripts" / "cli-32.exe"


def test_rejects_unsupported_subdir():
    with pytest.raises(ValueError, match="unsupported Windows subdir"):
        get_launcher_short_path("linux-64")


def test_rejects_unsupported_kind():
    with pytest.raises(ValueError, match="unsupported launcher kind"):
        get_launcher_short_path("win-64", "tui")  # type: ignore[arg-type]

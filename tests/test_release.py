"""Run the workflow's release scripts without GitHub or signing credentials."""

import hashlib
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/test.yml"


def script(name):
    step = WORKFLOW.read_text().split(f"      - name: {name}\n", 1)[1]
    block = step.split("        run: |\n", 1)[1]
    return textwrap.dedent(re.match(r"(?: {10}.*\n|\n)*", block)[0])


class ReleaseTests(unittest.TestCase):
    def test_tag_matches_recipe(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "recipe").mkdir()
            (root / "recipe/recipe.yaml").write_text(
                'context:\n  version: "24.7.1"\n  build_number: 5\n'
            )
            for tag in ("24.7.1-5", "v24.7.1-5", "24.7.2-5", "24.7.1-6"):
                with self.subTest(tag=tag):
                    result = subprocess.run(
                        [sys.executable, "-"],
                        input=script("Check release tag against recipe"),
                        cwd=root,
                        env={**os.environ, "RELEASE_TAG": tag},
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=10,
                    )
                    self.assertEqual(
                        result.returncode == 0, tag == "24.7.1-5", result.stderr
                    )

    @unittest.skipIf(os.name == "nt", "Draft release jobs run in Bash on Linux")
    def test_draft_upload_and_failures(self):
        failures = (
            None,
            "missing",
            "version",
            "checksum",
            "existing",
            "api",
            "create",
            "ambiguous-create",
            "upload",
            "cleanup",
            "published",
        )
        for failure in failures:
            with (
                self.subTest(failure=failure),
                tempfile.TemporaryDirectory() as temporary,
            ):
                root = Path(temporary)
                assets = root / "isolated"
                assets.mkdir()
                for variant in (
                    "32-zig",
                    "64-gcc",
                    "64-vs2022",
                    "arm64-vs2022",
                    "64-zig",
                    "arm64-zig",
                ):
                    arch, compiler = variant.split("-")
                    for kind in ("cli", "gui"):
                        executable = (
                            assets / f"{kind}-{arch}-24.7.1-123abcd_{compiler}_5.exe"
                        )
                        executable.write_bytes(executable.name.encode())
                        digest = (
                            hashlib.sha256(executable.read_bytes()).hexdigest().upper()
                        )
                        executable.with_suffix(".exe.sha256").write_bytes(
                            f"{digest}\r\n".encode()
                        )
                if failure == "missing":
                    next(assets.glob("*.exe")).unlink()
                if failure == "checksum":
                    next(assets.glob("*.sha256")).write_text("0" * 64)
                original = {path.name: path.read_bytes() for path in assets.iterdir()}

                state = root / "state"
                if failure == "existing":
                    state.write_text("published")
                fake_gh = root / "gh"
                fake_gh.write_text(
                    f"#!{sys.executable}\n"
                    + textwrap.dedent("""\
                    import os
                    from pathlib import Path
                    import sys

                    command = sys.argv[1] if sys.argv[1] == "api" else sys.argv[2]
                    failure = os.environ["FAILURE"]
                    state = Path("state")
                    with Path("commands").open("a") as log:
                        print(command, file=log)
                    if command == "api":
                        if failure == "api":
                            sys.exit(1)
                        if state.exists():
                            print(os.environ["RELEASE_TAG"])
                    elif command == "create":
                        assert "--draft" in sys.argv and "--verify-tag" in sys.argv
                        if failure == "create":
                            sys.exit(1)
                        state.write_text("draft")
                        if failure == "ambiguous-create":
                            sys.exit(1)
                    elif command == "upload":
                        assert "--clobber" not in sys.argv
                        assert len([arg for arg in sys.argv if arg.startswith("isolated/")]) == 24
                        if failure == "published":
                            state.write_text("published")
                        if failure in ("upload", "cleanup", "published"):
                            sys.exit(1)
                    elif command == "view":
                        print("true" if state.read_text() == "draft" else "false")
                    elif command == "delete":
                        assert state.read_text() == "draft"
                        if failure == "cleanup":
                            sys.exit(1)
                        state.unlink()
                    else:
                        sys.exit(99)
                    """)
                )
                fake_gh.chmod(0o755)
                result = subprocess.run(
                    ["bash", "--noprofile", "--norc"],
                    input=script("Check assets and create draft release"),
                    cwd=root,
                    env={
                        **os.environ,
                        "PATH": str(root) + os.pathsep + os.environ["PATH"],
                        "RELEASE_TAG": "24.7.2-5"
                        if failure == "version"
                        else "24.7.1-5",
                        "GH_REPO": "example/release-test",
                        "FAILURE": failure or "",
                    },
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=10,
                )
                self.assertEqual(result.returncode == 0, failure is None, result.stderr)
                log = root / "commands"
                commands = log.read_text().splitlines() if log.exists() else []
                expected = {
                    None: ["api", "create", "upload"],
                    "missing": [],
                    "version": [],
                    "checksum": [],
                    "existing": ["api"],
                    "api": ["api"],
                    "create": ["api", "create"],
                    "ambiguous-create": ["api", "create"],
                    "upload": ["api", "create", "upload", "view", "delete"],
                    "cleanup": ["api", "create", "upload", "view", "delete"],
                    "published": ["api", "create", "upload", "view"],
                }
                self.assertEqual(commands, expected[failure])
                if failure in (None, "cleanup", "ambiguous-create"):
                    self.assertEqual(state.read_text(), "draft")
                elif failure in ("existing", "published"):
                    self.assertEqual(state.read_text(), "published")
                else:
                    self.assertFalse(state.exists())
                self.assertEqual(
                    original,
                    {path.name: path.read_bytes() for path in assets.iterdir()},
                )


if __name__ == "__main__":
    unittest.main()

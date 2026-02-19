# conda-launchers

This repository provides the patches and build instructions necessary to compile and package the Windows Python entry-point launchers used in the conda ecosystem.

## What is this

These are the binaries that you can find next to all those `*-script.py` files in your `%PREFIX%\Scripts` directory. Their sole purpose is to:

1. Find the necessary Python executable in the directory above:
    - `cli-*.exe` will look for `python.exe`.
    - `gui-*.exe` will look for `pythonw.exe`.
2. Locate the adjacent Python script. This is based on the name of launcher itself. The target Python script must be `[name of the launcher without extension]-script.py`. So if you have a copy of the launcher named `my-application.exe`, it will look for `my-application-script.py`.
3. Execute `..\python[w].exe [adjacent-script].py`.

`conda` and `conda-build` will place an adequately renamed copy next to each [Python `console_scripts` entry point](https://packaging.python.org/en/latest/specifications/entry-points/#use-for-scripts) created.

## History

These launchers are based on the [CPython 3.7 launcher](https://github.com/python/cpython/blob/3.7/PC/launcher.c). These launchers were then [patched](https://github.com/conda/conda-build/blob/24.7.1/conda_build/launcher_sources/cpython-launcher-c-mods-for-setuptools.3.7.patch) for the conda ecosystem and historically provided in the `conda/conda-build` repository:
- The binaries were committed directly in the git history:
    - [`cli-64.exe`](https://github.com/conda/conda-build/blob/24.7.1/conda_build/cli-64.exe) + [`cli-32.exe`](https://github.com/conda/conda-build/blob/24.7.1/conda_build/cli-32.exe)
    - [`gui-64.exe`](https://github.com/conda/conda-build/blob/24.7.1/conda_build/gui-64.exe) + [`gui-32.exe`](https://github.com/conda/conda-build/blob/24.7.1/conda_build/gui-32.exe)
- The build instructions were in [`launcher_sources`](https://github.com/conda/conda-build/tree/24.7.1/conda_build/launcher_sources)

`conda/conda` also shipped its own copies of [`cli-64.exe`](https://github.com/conda/conda/blob/24.7.1/conda/shell/cli-64.exe) and [`cli-32.exe` ](https://github.com/conda/conda/blob/24.7.1/conda/shell/cli-32.exe) to create its own entry point upon reinitialization, plus the entry points for `noarch` packages.

In April 2024, the files were committed again after being `codesign`ed by Anaconda (see [`conda/conda#13685`](https://github.com/conda/conda/issues/13685) for details).

This repository now collects all those sources and suggests a way to package them as a conda package for easy reutilization.

## Automated builds & releases

All launcher binaries are built automatically in GitHub Actions using Zig as a
cross-compiler. Every push to `main` and every pull request triggers the
**Build Launchers** workflow which produces:

| Binary | Architecture | Type |
|--------|-------------|------|
| `cli-32.exe` | x86 (32-bit) | Console |
| `cli-64.exe` | x86_64 (64-bit) | Console |
| `cli-arm64.exe` | aarch64 (ARM64) | Console |
| `gui-32.exe` | x86 (32-bit) | GUI |
| `gui-64.exe` | x86_64 (64-bit) | GUI |
| `gui-arm64.exe` | aarch64 (ARM64) | GUI |

### Creating a release

Push a semver tag to trigger the **Release** workflow:

```bash
git tag v24.7.2
git push origin v24.7.2
```

The release workflow will:

1. Build all six launcher binaries.
2. Generate `SHA256SUMS.txt` checksums.
3. Create [sigstore build-provenance attestations](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds) for every artifact.
4. Publish an **immutable GitHub Release** with all assets attached.

### Verifying attestations

```bash
gh attestation verify cli-arm64.exe --repo conda/conda-launchers
```

## Debugging

The launchers will provide some debugging information if the environment variable `PYLAUNCH_DEBUG=1` is set.

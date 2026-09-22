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

## How to build

Different compiler stacks will generate different binaries. Since these launcher executables
will be copied many times over, we want the smallest self-contained executables. No external
linkage allowed.

We have three different build variants:

- GCC: the smallest binaries, but only for `win-64` so far.
- MSVC: `win-64` and `win-arm64`, but they are heavier.
- Zig: small executables, all platforms, but maintainers are not very familiar with the stack. Consider them experimental.

You can build either by calling `rattler-build` via `pixi` in this cloned repository:

```batch
pixi run rattler-build build ^
    --recipe recipe/ ^
    --variant-config recipe/variants/{gcc,vs,zig}.yaml ^
    --target-platform {win-32,win-64,win-arm64}
```

> `{a,b,c}` above denotes "Pick one of these"

## Releases

`conda-launchers` follows a `YY.MM.MICRO-BUILD` CalVer scheme. The `YY.MM.MICRO` was initially seeded from `conda-build`, where the patches and scripts used to live. Subsequent releases will stick to the release month. The `BUILD` component is taken from the build number in `recipe/recipe.yaml`.

To release, update `context.version` and `context.build_number` in `recipe/recipe.yaml`, then tag the reviewed commit with `<version>-<build_number>` and push that tag. Do not create or publish the release in the GitHub UI first. The workflow checks that the tag matches the recipe and then:

1. Builds all six compiler/architecture variants as conda packages.
2. Extracts the 12 executables, signs them with Azure Code Signing, verifies their Authenticode signatures, and generates SHA-256 files from the signed bytes.
3. Saves the signed files in the `conda-launchers-signed` workflow artifact.
4. Checks that all 12 executables and their matching checksum files are present, then attaches them to a new draft release.
5. Publishes the draft only after every asset has been uploaded.

Canary repackaging and upload run independently on pushes to `main` and release tags. A canary upload failure does not block the signed GitHub release.

### Immutable releases

This draft-first process addresses the [immutable-release request in #25](https://github.com/conda/conda-launchers/issues/25#issuecomment-4865131894), following the release workflows in [conda-sigstore](https://github.com/jezdez/conda-sigstore/blob/main/.github/workflows/release.yml) and [conda-sboms](https://github.com/conda-incubator/conda-sboms/blob/main/.github/workflows/release.yml).

After this workflow is merged, a repository administrator must enable **Settings > General > Releases > Enable release immutability** before the next release. The setting locks assets and tags for future releases only. Existing releases are not changed. See [GitHub's immutable-release documentation](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).

If asset upload or publication fails, use **Re-run failed jobs** on the original workflow run. The upload job downloads the existing signed artifact rather than rebuilding or signing again. After a failed upload, it attempts to remove the draft it just created, leaving the tag and workflow artifact intact. If draft creation or cleanup fails, GitHub may still have a draft for the tag. Inspect it and remove only the incomplete, unpublished draft before retrying. If publication alone fails, retry that job with the populated draft in place. Existing releases are never automatically replaced.

Do not rerun all jobs, replace published assets, or move a published tag. Corrections to published executables require a new version or build number and a new tag. Keep the existing asset naming scheme so downstream recipes can continue pinning filenames and checksums.

The `conda-canary` channel does NOT ship signed binaries. They are only meant to support development workflows in this repository. Unless (re-)signing is an option, distributors would probably want to binary-repackage the Releases Assets directly.

## Packaging

The per-compiler build matrix is for releasing new signed versions of the launchers. For packaging, the CI extracts the executables from three of them (zig for `win-32`, gcc for `win-64`, vs2022 for `win-arm64`) and repackages them into a single `noarch` package. This is driven by `recipe/variants/repackage.yaml` which installs all six launchers under `share/conda-launchers/`. Here we mirror the layout produced by the [conda-forge feedstock](https://github.com/conda-forge/conda-launchers-feedstock) and is what `conda` expects at runtime.

Note that the conda-forge feedstock pins the Release Asset names and their sha256 checksums. Any change to the matrix build strings (`<hash>_<compiler>_<build_number>`), the per-architecture compiler assignments, or the release tag format (`<version>-<build_number>`) requires a coordinated feedstock PR.

## History

These launchers are based on the [CPython 3.7 launcher](https://github.com/python/cpython/blob/3.7/PC/launcher.c). These launchers were then [patched](https://github.com/conda/conda-build/blob/24.7.1/conda_build/launcher_sources/cpython-launcher-c-mods-for-setuptools.3.7.patch) for the conda ecosystem and historically provided in the `conda/conda-build` repository:
- The binaries were committed directly in the git history:
    - [`cli-64.exe`](https://github.com/conda/conda-build/blob/24.7.1/conda_build/cli-64.exe) + [`cli-32.exe`](https://github.com/conda/conda-build/blob/24.7.1/conda_build/cli-32.exe)
    - [`gui-64.exe`](https://github.com/conda/conda-build/blob/24.7.1/conda_build/gui-64.exe) + [`gui-32.exe`](https://github.com/conda/conda-build/blob/24.7.1/conda_build/gui-32.exe)
- The build instructions were in [`launcher_sources`](https://github.com/conda/conda-build/tree/24.7.1/conda_build/launcher_sources)

`conda/conda` also shipped its own copies of [`cli-64.exe`](https://github.com/conda/conda/blob/24.7.1/conda/shell/cli-64.exe) and [`cli-32.exe` ](https://github.com/conda/conda/blob/24.7.1/conda/shell/cli-32.exe) to create its own entry point upon reinitialization, plus the entry points for `noarch` packages.

In April 2024, the files were committed again after being `codesign`ed by Anaconda (see [`conda/conda#13685`](https://github.com/conda/conda/issues/13685) for details).

This repository now collects all those sources and suggests a way to package them as a conda package for easy reutilization.

## Debugging

The launchers will provide some debugging information if the environment variable `PYLAUNCH_DEBUG=1` is set.

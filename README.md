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

You only need to create a new Release via the Github UI. This will trigger a new build in Github Actions that will:

* Build all launchers from source as conda packages
* Upload them to the `conda-canary` channel and CI artifacts
* Extract the `*.exe` files within, and sign them with Azure Code Signing.
* Upload the signed executables to the Release Assets.

The `conda-canary` channel does NOT ship signed binaries. They are only meant to support development workflows in this repository. Unless (re-)signing is an option, distributors would probably want to binary-repackage the Releases Assets directly.

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

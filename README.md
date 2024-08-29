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

## Debugging

The launchers will provide some debugging information if the environment variable `PYLAUNCH_DEBUG=1` is set.

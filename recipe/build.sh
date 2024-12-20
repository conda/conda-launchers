#!/usr/bin/env bash
# Adapted from https://github.com/conda/conda-build/blob/24.7.1/conda_build/launcher_sources/build.sh
# Set PYLAUNCH_DEBUG=1 to debug in CMD.exe

set -euxo pipefail

_ARCH=${target_platform#*-} # keep chunk after dash (e.g. '64' in 'win-64')

if [[ "${_ARCH}" == "64" ]]; then
  _CL_MACHINE=x64
elif [[ "${_ARCH}" == "arm64" ]]; then
  _CL_MACHINE=ARM64
fi

# Build resources file
test -f resources.rc && rm -f resources.rc
echo "#include \"winuser.h\""      > resources.rc
echo "1 RT_MANIFEST launcher.manifest" >> resources.rc
test -f resources-${_ARCH}.res && rm -f resources-${_ARCH}.res

if [[ "${c_compiler}" == "gcc" ]]; then
  ${WINDRES:-windres} --input resources.rc --output resources-${_ARCH}.res --output-format=coff -v
else
  which rc.exe
  rc.exe resources.rc
  mv resources.res resources-${_ARCH}.res
fi

ls -alh .

# Compile launchers
for _TYPE in cli gui; do
  if [[ ${_TYPE} == cli ]]; then
    if [[ "${c_compiler}" == "gcc" ]]; then
      CPPFLAGS=
      LDFLAGS=
    else
      CPPFLAGS=
      LDFLAGS="-SUBSYSTEM:CONSOLE"
    fi
  else
    if [[ "${c_compiler}" == "gcc" ]]; then
      CPPFLAGS="-D_WINDOWS -mwindows"
      LDFLAGS="-mwindows"
    else
      CPPFLAGS="-D_WINDOWS"
      LDFLAGS="-SUBSYSTEM:WINDOWS"
    fi
  fi

  # An executable with mingw and `static-libgcc` is 42K
  # An executable with vcruntime statically linked (-MT) in is 920K
  # An executable with vcruntime dynamically linked (-MD) in is 84K
  # For arm64, since we don't have mingw, we are going to use -MT
  #  since -MD needs vcruntime140.dll installed and the binaries need
  #  to be run from Scripts which does not have vcruntime140.dll.
  #  Also we cannot assume that vcruntime140.dll is found in the system.
  if [[ "${c_compiler}" == "vs" ]]; then
    cl.exe -D NDEBUG -D "WIN32_LEAN_AND_MEAN" ${CPPFLAGS} -ZI -Gy -MT launcher.c -Os -link -MACHINE:${_CL_MACHINE} ${LDFLAGS} resources-${_ARCH}.res user32.lib version.lib advapi32.lib shell32.lib -out:${_TYPE}-${_ARCH}.exe
  else
    ${CC} -O2 -DSCRIPT_WRAPPER -DUNICODE -D_UNICODE -DMINGW_HAS_SECURE_API -DMAXINT=INT_MAX ${CPPFLAGS} \
      ${SRC_DIR}/launcher.c -c -o ${_TYPE}-${_ARCH}.o

    ${CC} -Wl,-s --static -static-libgcc -municode ${LDFLAGS} \
      ${_TYPE}-${_ARCH}.o resources-${_ARCH}.res -o ${_TYPE}-${_ARCH}.exe
  fi

done

echo "Built these executables:"
ls -alh *.exe

# Install in PREFIX
mkdir -p "${PREFIX}/Scripts"
for f in *.exe; do
  echo "Installing $f..."
  cp "$f" "${PREFIX}/Scripts"
  echo "print(\"$f successfully launched the accompanying Python script\")" > "${PREFIX}/Scripts/${f%.*}-script.py"
done

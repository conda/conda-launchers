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
echo "1 RT_MANIFEST manifest.xml" >> resources.rc
test -f resources-${_ARCH}.res && rm -f resources-${_ARCH}.res

if [[ "${c_compiler}" == "gcc" ]]; then
  ${WINDRES:-windres} --input resources.rc --output resources-${_ARCH}.res --output-format=coff -v
else
  rc.exe -fo:resources-${_ARCH}.res resources.rc
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

  # You *could* use MSVC 2008 here, but you'd end up with much larger (~230k) executables.
  if [[ "${c_compiler}" == "vs" ]]; then
    cl.exe -opt:nowin98 -D NDEBUG -D "WIN32_LEAN_AND_MEAN" ${CPPFLAGS} -ZI -Gy -MT launcher.c -Os -link -MACHINE:${_CL_MACHINE} ${LDFLAGS} resources-${_ARCH}.res version.lib advapi32.lib shell32.lib -out:${_TYPE}-${_ARCH}.exe
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

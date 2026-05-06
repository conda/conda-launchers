setlocal EnableDelayedExpansion

@rem Patch manually
patch.exe -Np0 -i cpython-launcher-c-mods-for-setuptools.3.7.patch --binary
IF !ERRORLEVEL! NEQ 0 exit 1

@rem rename patched source file to be used for building
move /Y launcher.c.orig launcher.c
IF !ERRORLEVEL! NEQ 0 exit 1

@rem Delegate to the Unixy script. We need to translate the key path variables
@rem to be Unix-y rather than Windows-y, though.
set PREFIX_BAK=!PREFIX!
FOR /F "delims=" %%i IN ('cygpath.exe -u -p "!PATH!"') DO set "PATH_OVERRIDE=%%i"
FOR /F "delims=" %%i IN ('cygpath.exe -a -u "!PREFIX!"') DO set "PREFIX=%%i"
FOR /F "delims=" %%i in ('cygpath.exe -a -u "!BUILD_PREFIX!"') DO set "BUILD_PREFIX=%%i"

copy !RECIPE_DIR!\build.sh .
bash build.sh
IF !ERRORLEVEL! NEQ 0 exit 1

xcopy cli-*.exe "!PREFIX_BAK!\Scripts\" /Y
xcopy cli-*.py "!PREFIX_BAK!\Scripts\" /Y
xcopy gui-*.exe "!PREFIX_BAK!\Scripts\" /Y
xcopy gui-*.py "!PREFIX_BAK!\Scripts\" /Y
xcopy gui-*.pyw "!PREFIX_BAK!\Scripts\" /Y

@rem no-op for conda-launchers metapackage
if %PKG_NAME% == conda-launchers (exit 0)

@rem Patch manually
patch.exe -Np0 -i cpython-launcher-c-mods-for-setuptools.3.7.patch --binary
IF %ERRORLEVEL% NEQ 0 exit 1

@rem rename patched source file to be used for building
move /Y launcher.c.orig launcher.c
IF %ERRORLEVEL% NEQ 0 exit 1

:: Delegate to the Unixy script. We need to translate the key path variables
:: to be Unix-y rather than Windows-y, though.
set "OG_PREGIX=%PREFIX%"
FOR /F "delims=" %%i IN ('cygpath.exe -u -p "%PATH%"') DO set "PATH_OVERRIDE=%%i"
FOR /F "delims=" %%i IN ('cygpath.exe -u "%PREFIX%"') DO set "PREFIX=%%i"
FOR /F "delims=" %%i in ('cygpath.exe -u "%BUILD_PREFIX%"') DO set "BUILD_PREFIX=%%i"

copy %RECIPE_DIR%\build.sh .
bash build.sh
IF %ERRORLEVEL% NEQ 0 exit 1


echo "OG_PREFIX:"
echo %OG_PREFIX%
echo "PREFIX:"
echo %PREFIX%
echo dir OG_PREFIX
dir %OG_PREFIX%
echo dir PREFIX
dir %PREFIX%

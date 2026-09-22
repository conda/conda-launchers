setlocal EnableDelayedExpansion

mkdir "%PREFIX%\share\conda-launchers"
IF %ERRORLEVEL% NEQ 0 exit 1

for %%a in (32 64 arm64) do (
    copy /Y "cli-%%a.exe" "%PREFIX%\share\conda-launchers\cli-%%a.exe"
    IF !ERRORLEVEL! NEQ 0 exit 1
    copy /Y "gui-%%a.exe" "%PREFIX%\share\conda-launchers\gui-%%a.exe"
    IF !ERRORLEVEL! NEQ 0 exit 1
)

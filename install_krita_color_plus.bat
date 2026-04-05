@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

where py >nul 2>nul
if %errorlevel%==0 (
    py install_gui.py
    goto :end
)

where python >nul 2>nul
if %errorlevel%==0 (
    python install_gui.py
    goto :end
)

echo Python launcher not found. Install Python or run install_gui.py manually.
pause
exit /b 1

:end
if not %errorlevel%==0 (
    echo Installer exited with errors.
    pause
    exit /b %errorlevel%
)

echo Installation completed.
pause
exit /b 0

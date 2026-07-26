@echo off
rem One-click launcher for python-zero-to-hero (Windows).
rem
rem   run              your progress across all 21 days
rem   run day04        grade Day 4
rem   run day04 -v     grade Day 4 with full failure detail
rem   run next         grade the first day you haven't finished
rem   run doctor       check your setup
rem
rem Works out which Python to use, installs pytest if it is missing, then hands
rem over to check.py. Everything you type after `run` is passed through.
rem
rem Override the interpreter:  set PZH_PYTHON=C:\Python312\python.exe

setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PY="

rem An explicit choice wins, then a project virtualenv, then newest-first.
if defined PZH_PYTHON call :try "%PZH_PYTHON%"
if not defined PY call :try "%~dp0.venv\Scripts\python.exe"
if not defined PY call :try "py -3.14"
if not defined PY call :try "py -3.13"
if not defined PY call :try "py -3.12"
if not defined PY call :try "py -3.11"
if not defined PY call :try "py -3.10"
if not defined PY call :try "py -3"
if not defined PY call :try "python"
if not defined PY call :try "python3"

if not defined PY (
    echo.
    echo   Could not find a working Python 3.10 or newer.
    echo.
    echo   This course needs Python 3.10+. To fix it:
    echo     * install it         -^> see SETUP.md in this folder
    echo     * or point me at one -^> set PZH_PYTHON=C:\path\to\python.exe
    echo.
    echo   On Windows the installer's "Add python.exe to PATH" checkbox is the
    echo   usual culprit. SETUP.md section 2 covers it.
    echo.
    exit /b 1
)

rem pytest is the only hard dependency. Install it once if absent.
%PY% -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo   pytest is missing - installing it once with %PY% ...
    %PY% -m pip install --quiet pytest >nul 2>&1
    if errorlevel 1 (
        %PY% -m pip install --quiet --user pytest >nul 2>&1
        if errorlevel 1 (
            echo.
            echo   Could not install pytest automatically. Try:
            echo     %PY% -m pip install --user pytest
            echo.
            exit /b 1
        )
    )
)

rem Tell check.py how you invoked it, so its hints say "run day05" rather than
rem "python check.py day05".
set "PZH_LAUNCHER=run"

%PY% check.py %*
exit /b %errorlevel%

:try
rem Run the candidate for real - a launcher can exist and still fail to start.
%~1 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 set "PY=%~1"
goto :eof

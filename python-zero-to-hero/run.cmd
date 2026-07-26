@echo off
rem One-click launcher for python-zero-to-hero (Windows).
rem
rem   run              your progress across all 21 days
rem   run day04        grade Day 4
rem   run day04 -v     grade Day 4 with full failure detail
rem   run next         grade the first day you haven't finished
rem   run doctor       check your setup
rem   run notebook     read the lessons as runnable notebooks in JupyterLab
rem   run notebook day05   open Day 5's notebook straight away
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

rem `run notebook` is the only argument that does not go to the grader: it is a
rem different front end onto the same course.
if /i "%~1"=="notebook" goto notebook

rem Tell check.py how you invoked it, so its hints say "run day05" rather than
rem "python check.py day05".
set "PZH_LAUNCHER=run"

%PY% check.py %*
exit /b %errorlevel%

:notebook
rem Nothing in a notebook is graded, so JupyterLab and friends stay optional and
rem are installed on first use rather than up front.
%PY% -c "import jupyterlab" >nul 2>&1
if errorlevel 1 (
    echo   JupyterLab is missing - installing the notebook extras once with %PY% ...
    %PY% -m pip install --quiet -r requirements-notebooks.txt >nul 2>&1
    if errorlevel 1 (
        %PY% -m pip install --quiet --user -r requirements-notebooks.txt >nul 2>&1
        if errorlevel 1 (
            echo.
            echo   Could not install the notebook extras automatically. Try:
            echo     %PY% -m pip install --user -r requirements-notebooks.txt
            echo.
            echo   You do not need any of this to take the course - the graded work
            echo   is exercises.py plus `run dayNN`, which only needs pytest.
            echo.
            exit /b 1
        )
    )
)

rem Flags a container needs: listen on all interfaces so a forwarded port works,
rem do not try to open a browser that isn't there, and root the file browser at
rem the course folder rather than wherever you happened to be.
set "JFLAGS=--ip=0.0.0.0 --port=8888 --no-browser"
set "JROOT=--ServerApp.root_dir=%CD%"

rem No day given: just open the file browser at the course root.
if "%~2"=="" (
    %PY% -m jupyterlab %JFLAGS% "%JROOT%"
    exit /b %errorlevel%
)

rem An optional day, spelled however check.py accepts it: day05, 05, 5.
set "SEL=%~2"
if /i "!SEL:~0,3!"=="day" set "SEL=!SEL:~3!"
echo !SEL!| findstr /r /c:"^[0-9][0-9]*$" >nul
if errorlevel 1 (
    echo.
    echo   Don't know which notebook '%~2' means.
    echo.
    echo   Try:  run notebook day05   or   run notebook   ^(opens the file browser^)
    echo.
    exit /b 1
)
set "NUM=0!SEL!"
set "NUM=!NUM:~-2!"

rem The build script names them notebooks\dayNN_slug.ipynb, and we do not want
rem to hardcode 21 slugs, so match on the day number.
set "NB="
set "NBFILE="
for %%F in ("notebooks\day!NUM!_*.ipynb") do if exist "%%~fF" set "NBFILE=%%~nxF"
if defined NBFILE set "NB=notebooks\!NBFILE!"

if not defined NB (
    echo.
    echo   No notebook for day !NUM! yet ^(looked for notebooks\day!NUM!_*.ipynb^).
    echo.
    echo   The notebooks are generated from each day's LESSON.md. Build them with:
    echo.
    echo     %PY% tools\build_notebooks.py
    echo.
    echo   Then re-run:  run notebook day!NUM!
    echo.
    echo   Or read the lesson as plain text - it is the same content:
    echo     course\week*\day!NUM!_*\LESSON.md
    echo.
    exit /b 1
)

rem The positional path opens the notebook when there is a browser to open it
rem in; default_url is what makes it work in a container, where you arrive at
rem "/" from a forwarded port and want to land in the lesson.
set "JOPEN=--LabApp.default_url=/lab/tree/notebooks/!NBFILE!"
%PY% -m jupyterlab %JFLAGS% "!JROOT!" "!JOPEN!" "!NB!"
exit /b %errorlevel%

:try
rem Run the candidate for real - a launcher can exist and still fail to start.
%~1 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 set "PY=%~1"
goto :eof

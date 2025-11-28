@echo off
echo ================================================
echo     EnergyInsight BUSINESS - Lancement Rapide
echo ================================================
echo.

REM Recherche Python dans les emplacements courants
set PYTHON_CMD=

REM Test 1: Python dans PATH
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    echo Python detecte: py
    goto :launch
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo Python detecte: python
    goto :launch
)

REM Test 2: Python dans AppData Local
if exist "C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe
    echo Python detecte: Python312
    goto :launch
)

if exist "C:\Users\PC\AppData\Local\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=C:\Users\PC\AppData\Local\Programs\Python\Python311\python.exe
    echo Python detecte: Python311
    goto :launch
)

REM Test 3: Python dans Program Files
if exist "C:\Program Files\Python312\python.exe" (
    set PYTHON_CMD=C:\Program Files\Python312\python.exe
    echo Python detecte: Program Files Python312
    goto :launch
)

if exist "C:\Program Files\Python311\python.exe" (
    set PYTHON_CMD=C:\Program Files\Python311\python.exe
    echo Python detecte: Program Files Python311
    goto :launch
)

echo.
echo ERREUR: Python non trouve !
echo.
echo Solutions:
echo 1. Executez diagnostic_simple.bat pour diagnostiquer
echo 2. Executez install_python_auto.bat pour installer
echo 3. Redemarrez votre ordinateur
echo.
pause
exit /b 1

:launch
echo.
echo Verification des modules requis...
"%PYTHON_CMD%" -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo Installation des modules...
    "%PYTHON_CMD%" -m pip install flask pandas numpy plotly reportlab
)

echo.
echo Verification si l'application est deja en cours...
netstat -an | findstr "127.0.0.1:5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo L'application est deja en cours !
    echo Ouverture du navigateur...
    start http://127.0.0.1:5000
    pause
    exit /b 0
)

echo.
echo Lancement d'EnergyInsight...
echo Application disponible sur: http://127.0.0.1:5000
echo.
echo Ouverture automatique du navigateur dans 3 secondes...
timeout /t 3 /nobreak >nul
start http://127.0.0.1:5000
echo.
echo Appuyez sur Ctrl+C pour arreter l'application
echo.

"%PYTHON_CMD%" app.py

echo.
echo Application arretee.
pause

@echo off
echo ================================================
echo     EnergyInsight BUSINESS - Demarrage
echo ================================================
echo.

REM Verifier si Python est installe
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    echo Python detecte: py
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
        echo Python detecte: python
    ) else (
        echo.
        echo ERREUR: Python n'est pas installe ou pas dans le PATH.
        echo.
        echo Solutions possibles:
        echo 1. Installer Python depuis https://www.python.org/downloads/
        echo 2. Cocher "Add Python to PATH" lors de l'installation
        echo 3. Redemarrer l'ordinateur apres installation
        echo.
        pause
        exit /b 1
    )
)
echo.

REM Verifier si les modules requis sont installes
echo Verification des modules requis...
%PYTHON_CMD% -c "import flask, pandas, numpy, plotly, reportlab" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Installation des modules requis...
    %PYTHON_CMD% -m pip install flask pandas numpy plotly reportlab
    if %errorlevel% neq 0 (
        echo.
        echo ERREUR: Impossible d'installer les modules requis.
        echo Veuillez verifier votre installation Python.
        pause
        exit /b 1
    )
)

echo.
echo Verification si l'application est deja en cours d'execution...
netstat -an | findstr "127.0.0.1:5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo L'application est deja en cours d'execution !
    echo Ouverture du navigateur...
    start http://127.0.0.1:5000
    echo.
    echo Application disponible sur: http://127.0.0.1:5000
    echo.
    pause
    exit /b 0
)

echo.
echo Demarrage d'EnergyInsight BUSINESS...
echo.
echo Fonctionnalites disponibles:
echo   - Analyse automatisee des pics anormaux
echo   - Projections economiques detaillees
echo   - Vue par periode (HP/HC, zones, saisons)
echo   - Rapport PDF avec potentiel d'economies
echo   - Objectifs de reduction et plan d'action
echo   - Import CSV/Excel de factures entreprise
echo.
echo Application disponible sur: http://127.0.0.1:5000
echo.
echo Ouverture automatique du navigateur dans 3 secondes...
timeout /t 3 /nobreak >nul
start http://127.0.0.1:5000
echo.
echo Appuyez sur Ctrl+C pour arreter l'application
echo.

%PYTHON_CMD% app.py

echo.
echo Application arretee.
pause

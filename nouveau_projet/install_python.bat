@echo off
echo ================================================
echo     Installation Python pour EnergyInsight
echo ================================================
echo.

echo Verification des installations Python disponibles...
echo.

REM Verifier Microsoft Store Python
echo 1. Verification Python Microsoft Store...
where python >nul 2>&1
if %errorlevel% equ 0 (
    python --version 2>nul
    if %errorlevel% equ 0 (
        echo    ✅ Python Microsoft Store trouve
        goto FOUND_PYTHON
    )
)
echo    ❌ Python Microsoft Store non trouve

REM Verifier py launcher
echo.
echo 2. Verification py launcher...
where py >nul 2>&1
if %errorlevel% equ 0 (
    py --version 2>nul
    if %errorlevel% equ 0 (
        echo    ✅ Python py launcher trouve
        goto FOUND_PYTHON
    )
)
echo    ❌ py launcher non trouve

REM Verifier python3
echo.
echo 3. Verification python3...
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    python3 --version 2>nul
    if %errorlevel% equ 0 (
        echo    ✅ python3 trouve
        goto FOUND_PYTHON
    )
)
echo    ❌ python3 non trouve

REM Aucun Python trouve
echo.
echo ❌ AUCUNE INSTALLATION PYTHON TROUVEE
echo.
echo 🚀 SOLUTIONS D'INSTALLATION RAPIDE:
echo.
echo Option 1 - Microsoft Store (RECOMMANDEE):
echo   - Ouvrir Microsoft Store
echo   - Chercher "Python 3.12"
echo   - Cliquer "Obtenir"
echo   - Installation automatique
echo.
echo Option 2 - Site officiel:
echo   - Aller sur https://python.org/downloads/
echo   - Telecharger Python 3.8+
echo   - IMPORTANT: Cocher "Add Python to PATH"
echo   - Redemarrer apres installation
echo.
echo Option 3 - Commande PowerShell (Admin):
echo   winget install Python.Python.3.12
echo.
echo Appuyez sur une touche pour ouvrir Microsoft Store...
pause >nul
start ms-windows-store://pdp/?productid=9NCVDN91XZQP
exit /b 1

:FOUND_PYTHON
echo.
echo ✅ Python trouve ! Installation des modules...
echo.

REM Determiner la commande Python a utiliser
where python >nul 2>&1 && set PYTHON_CMD=python || (
    where py >nul 2>&1 && set PYTHON_CMD=py || set PYTHON_CMD=python3
)

echo Commande Python: %PYTHON_CMD%
echo.

REM Installer les modules requis
echo Installation des modules Flask, pandas, numpy, plotly...
%PYTHON_CMD% -m pip install --user flask pandas numpy plotly reportlab
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Erreur d'installation des modules
    echo Tentative avec --break-system-packages...
    %PYTHON_CMD% -m pip install --break-system-packages flask pandas numpy plotly reportlab
)

echo.
echo ✅ Installation terminee !
echo.
echo Pour lancer EnergyInsight:
echo   %PYTHON_CMD% app.py
echo.
echo Ou utiliser: start_app_simple.bat
echo.

REM Creer un script de lancement simple
echo @echo off > start_app_simple.bat
echo echo Lancement EnergyInsight... >> start_app_simple.bat
echo %PYTHON_CMD% app.py >> start_app_simple.bat
echo pause >> start_app_simple.bat

echo ✅ Script de lancement cree: start_app_simple.bat
echo.
pause

@echo off
echo ================================================
echo     Diagnostic Python - EnergyInsight
echo ================================================
echo.

echo 1. Verification de Python...
echo.

where py >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python (py) detecte
    py --version
    set PYTHON_CMD=py
) else (
    echo [ERREUR] Python (py) non trouve
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Python (python) detecte
        python --version
        set PYTHON_CMD=python
    ) else (
        echo [ERREUR] Python (python) non trouve
        echo.
        echo SOLUTION: Executez install_python_auto.bat
        echo.
        pause
        exit /b 1
    )
)

echo.
echo 2. Verification de pip...
%PYTHON_CMD% -m pip --version
if %errorlevel% neq 0 (
    echo [ERREUR] pip non fonctionnel
) else (
    echo [OK] pip fonctionne
)

echo.
echo 3. Verification des modules requis...
echo.

set MODULES=flask pandas numpy plotly reportlab openpyxl

for %%m in (%MODULES%) do (
    %PYTHON_CMD% -c "import %%m; print('[OK] %%m')" 2>nul
    if %errorlevel% neq 0 (
        echo [MANQUANT] %%m
        set MISSING=1
    )
)

if defined MISSING (
    echo.
    echo Certains modules sont manquants.
    echo Voulez-vous les installer maintenant ? (o/n)
    set /p choice=
    if /i "%choice%"=="o" (
        echo.
        echo Installation des modules manquants...
        %PYTHON_CMD% -m pip install %MODULES%
    )
)

echo.
echo 4. Test de l'application EnergyInsight...
echo.

if exist app.py (
    echo [OK] app.py trouve
    %PYTHON_CMD% -c "import app; print('[OK] app.py peut etre importe')" 2>nul
    if %errorlevel% neq 0 (
        echo [ERREUR] Probleme dans app.py
        %PYTHON_CMD% -c "import app" 2>&1
    )
) else (
    echo [ERREUR] app.py non trouve
)

echo.
echo 5. Test du fichier d'exemple...
echo.

if exist exemple_donnees_conso_entreprise.csv (
    echo [OK] Fichier d'exemple trouve
    %PYTHON_CMD% -c "import pandas as pd; df = pd.read_csv('exemple_donnees_conso_entreprise.csv'); print(f'[OK] {len(df)} lignes lues')" 2>nul
    if %errorlevel% neq 0 (
        echo [ERREUR] Probleme de lecture du fichier d'exemple
    )
) else (
    echo [ERREUR] Fichier d'exemple non trouve
)

echo.
echo ================================================
echo     Diagnostic termine
echo ================================================
echo.

if not defined MISSING (
    echo Tout semble fonctionner ! Vous pouvez lancer start_business.bat
) else (
    echo Des problemes ont ete detectes. Suivez les instructions ci-dessus.
)

echo.
pause

@echo off
echo ================================================
echo     Diagnostic Python - EnergyInsight
echo ================================================
echo.

echo 1. Verification de Python...
echo.

where py >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python py detecte
    py --version
    set PYTHON_CMD=py
) else (
    echo [ERREUR] Python py non trouve
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Python python detecte
        python --version
        set PYTHON_CMD=python
    ) else (
        echo [ERREUR] Python python non trouve
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
echo 3. Test simple d'importation...
%PYTHON_CMD% -c "print('Python fonctionne correctement')"

echo.
echo 4. Verification des modules de base...
%PYTHON_CMD% -c "import sys; print('Modules de base OK')"

echo.
echo 5. Test du fichier app.py...
if exist app.py (
    echo [OK] app.py trouve
) else (
    echo [ERREUR] app.py non trouve
)

echo.
echo ================================================
echo     Diagnostic termine
echo ================================================
echo.
pause

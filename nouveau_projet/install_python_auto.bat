@echo off
echo ================================================
echo     Installation automatique de Python
echo ================================================
echo.

REM Verifier si Python est deja installe
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo Python (py) est deja installe !
    py --version
    echo.
    echo Verification des modules...
    goto :check_modules
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Python est deja installe !
    python --version
    echo.
    echo Verification des modules...
    goto :check_modules
)

echo Python n'est pas installe. Installation en cours...
echo.

REM Creer un dossier temporaire
mkdir %TEMP%\python_install 2>nul
cd /d %TEMP%\python_install

echo Telechargement de Python...
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python_installer.exe'}"

if not exist python_installer.exe (
    echo.
    echo ERREUR: Impossible de telecharger Python.
    echo Veuillez telecharger manuellement depuis https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo Installation de Python en cours...
echo IMPORTANT: Python sera installe avec les options suivantes:
echo   - Ajouter Python au PATH
echo   - Installer pip
echo   - Installer pour tous les utilisateurs
echo.

python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

echo.
echo Attente de la fin de l'installation...
timeout /t 10 /nobreak >nul

echo.
echo Nettoyage...
cd /d %~dp0
rmdir /s /q %TEMP%\python_install

echo.
echo Verification de l'installation...
where py >nul 2>&1
if %errorlevel% neq 0 (
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo ERREUR: L'installation a echoue.
        echo Veuillez redemarrer votre ordinateur et reessayer.
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python
    )
) else (
    set PYTHON_CMD=py
)

echo Python installe avec succes !
%PYTHON_CMD% --version
echo.

:check_modules
echo Installation des modules requis pour EnergyInsight...
echo.

REM Determiner la commande Python a utiliser
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

echo Mise a jour de pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo.
echo Installation des modules EnergyInsight...
%PYTHON_CMD% -m pip install flask pandas numpy plotly reportlab weasyprint openpyxl

if %errorlevel% neq 0 (
    echo.
    echo ERREUR: Impossible d'installer certains modules.
    echo Tentative d'installation individuelle...
    echo.
    
    %PYTHON_CMD% -m pip install flask
    %PYTHON_CMD% -m pip install pandas
    %PYTHON_CMD% -m pip install numpy
    %PYTHON_CMD% -m pip install plotly
    %PYTHON_CMD% -m pip install reportlab
    %PYTHON_CMD% -m pip install openpyxl
    
    echo.
    echo Installation terminee avec quelques avertissements possibles.
) else (
    echo.
    echo Tous les modules installes avec succes !
)

echo.
echo ================================================
echo     Installation terminee !
echo ================================================
echo.
echo Python est maintenant pret pour EnergyInsight.
echo Vous pouvez maintenant lancer start_business.bat
echo.
echo Si vous rencontrez encore des problemes:
echo 1. Redemarrez votre ordinateur
echo 2. Relancez start_business.bat
echo.
pause

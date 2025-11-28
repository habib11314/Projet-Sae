@echo off
title EnergyInsight BUSINESS - Menu Principal
color 0A

:MENU
cls
echo ================================================
echo     EnergyInsight BUSINESS - Menu Principal
echo ================================================
echo.
echo Votre solution de pilotage energetique strategique
echo.
echo Options disponibles:
echo.
echo   1. 🚀 Demarrer l'application
echo   2. 🌐 Ouvrir l'application (si deja demarree)
echo   3. 🔍 Verifier l'etat de l'application
echo   4. 🛑 Arreter l'application
echo   5. 📋 Tester l'installation
echo   6. 📚 Afficher la documentation
echo   7. ❌ Quitter
echo.
echo ================================================

set /p choice=Choisissez une option (1-7): 

if "%choice%"=="1" goto START_APP
if "%choice%"=="2" goto OPEN_APP
if "%choice%"=="3" goto CHECK_APP
if "%choice%"=="4" goto STOP_APP
if "%choice%"=="5" goto TEST_APP
if "%choice%"=="6" goto SHOW_DOCS
if "%choice%"=="7" goto EXIT
goto INVALID

:START_APP
echo.
echo Demarrage de l'application...
call start_business.bat
goto MENU

:OPEN_APP
echo.
echo Ouverture de l'application...
call open_business.bat
goto MENU

:CHECK_APP
echo.
echo Verification de l'etat de l'application...
netstat -an | findstr "127.0.0.1:5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Application EN COURS D'EXECUTION sur http://127.0.0.1:5000
) else (
    echo ❌ Application NON ACTIVE
)
echo.
pause
goto MENU

:STOP_APP
echo.
echo Arret de l'application...
call stop_business.bat
goto MENU

:TEST_APP
echo.
echo Test de l'installation...
if exist test_business.py (
    python test_business.py
) else (
    echo ❌ Fichier de test non trouve
)
echo.
pause
goto MENU

:SHOW_DOCS
echo.
echo Documentation disponible:
echo.
echo   📄 README_BUSINESS.md     - Documentation complete
echo   📋 GUIDE_BUSINESS.md      - Guide d'utilisation
echo   🔧 requirements_business.txt - Dependances
echo.
echo Souhaitez-vous ouvrir la documentation ? (O/N)
set /p doc_choice=Votre choix: 
if /i "%doc_choice%"=="O" (
    if exist README_BUSINESS.md (
        start notepad README_BUSINESS.md
    ) else (
        echo ❌ Fichier de documentation non trouve
    )
)
echo.
pause
goto MENU

:INVALID
echo.
echo ❌ Option invalide. Veuillez choisir un numero entre 1 et 7.
timeout /t 2 /nobreak >nul
goto MENU

:EXIT
echo.
echo Merci d'avoir utilise EnergyInsight BUSINESS !
echo.
echo 🌱 Votre partenaire pour l'excellence energetique
echo.
timeout /t 2 /nobreak >nul
exit /b 0

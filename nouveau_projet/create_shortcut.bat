@echo off
echo ================================================
echo     EnergyInsight BUSINESS - Creation Raccourci
echo ================================================
echo.

REM Obtenir le chemin du bureau
set "DESKTOP=%USERPROFILE%\Desktop"
set "CURRENT_DIR=%~dp0"

echo Creation du raccourci sur le bureau...
echo.

REM Créer le fichier de raccourci
echo @echo off > "%DESKTOP%\EnergyInsight Business.bat"
echo title EnergyInsight BUSINESS >> "%DESKTOP%\EnergyInsight Business.bat"
echo cd /d "%CURRENT_DIR%" >> "%DESKTOP%\EnergyInsight Business.bat"
echo call menu_business.bat >> "%DESKTOP%\EnergyInsight Business.bat"

if exist "%DESKTOP%\EnergyInsight Business.bat" (
    echo ✅ Raccourci cree avec succes !
    echo.
    echo Localisation: %DESKTOP%\EnergyInsight Business.bat
    echo.
    echo Vous pouvez maintenant :
    echo   1. Double-cliquer sur le raccourci depuis le bureau
    echo   2. Acceder directement au menu principal
    echo   3. Gerer l'application facilement
    echo.
    echo Souhaitez-vous tester le raccourci maintenant ? (O/N)
    set /p test_choice=Votre choix: 
    
    if /i "%test_choice%"=="O" (
        echo.
        echo Lancement du raccourci...
        call "%DESKTOP%\EnergyInsight Business.bat"
    )
) else (
    echo ❌ Erreur lors de la creation du raccourci
    echo.
    echo Verifiez les permissions d'ecriture sur le bureau
)

echo.
echo Appuyez sur une touche pour continuer...
pause >nul

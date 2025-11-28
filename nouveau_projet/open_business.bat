@echo off
echo ================================================
echo     EnergyInsight BUSINESS - Acces Rapide
echo ================================================
echo.

REM Verifier si l'application est en cours d'execution
echo Verification de l'application...
netstat -an | findstr "127.0.0.1:5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ✅ Application detectee en cours d'execution
    echo 🌐 Ouverture du navigateur...
    start http://127.0.0.1:5000
    echo.
    echo Application disponible sur: http://127.0.0.1:5000
    echo.
    echo Appuyez sur une touche pour fermer cette fenetre...
    pause >nul
    exit /b 0
) else (
    echo.
    echo ❌ Application non detectee
    echo.
    echo L'application EnergyInsight Business n'est pas en cours d'execution.
    echo.
    echo Options disponibles:
    echo   1. Lancer start_business.bat pour demarrer l'application
    echo   2. Verifier si l'application fonctionne sur un autre port
    echo   3. Redemarrer l'application si necessaire
    echo.
    echo Souhaitez-vous demarrer l'application maintenant ? (O/N)
    set /p choice=Votre choix: 
    
    if /i "%choice%"=="O" (
        echo.
        echo Demarrage de l'application...
        call start_business.bat
    ) else (
        echo.
        echo Operation annulee.
        pause
        exit /b 0
    )
)

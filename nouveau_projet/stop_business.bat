@echo off
echo ================================================
echo     EnergyInsight BUSINESS - Arret Application
echo ================================================
echo.

REM Verifier si l'application est en cours d'execution
echo Recherche de l'application en cours d'execution...
netstat -an | findstr "127.0.0.1:5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ✅ Application detectee sur le port 5000
    echo.
    echo Recherche du processus Python...
    
    REM Trouver et tuer le processus Python qui utilise le port 5000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr "127.0.0.1:5000"') do (
        echo Arret du processus ID: %%a
        taskkill /pid %%a /f >nul 2>&1
        if %errorlevel% equ 0 (
            echo ✅ Application arretee avec succes
        ) else (
            echo ❌ Erreur lors de l'arret du processus
        )
    )
    
    echo.
    echo Verification de l'arret...
    timeout /t 2 /nobreak >nul
    netstat -an | findstr "127.0.0.1:5000" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ✅ Application completement arretee
    ) else (
        echo ⚠️  L'application semble toujours active
        echo Vous pouvez fermer manuellement la fenetre de commande
    )
    
) else (
    echo.
    echo ❌ Aucune application detectee sur le port 5000
    echo.
    echo L'application EnergyInsight Business ne semble pas en cours d'execution.
)

echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul

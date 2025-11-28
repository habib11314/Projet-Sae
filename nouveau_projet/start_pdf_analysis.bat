@echo off
echo 🚀 Démarrage d'EnergyInsight - Version PDF
echo.
echo Lancement de l'application avec accès direct à l'analyse PDF...

start "" http://localhost:5000/pdf-analysis
echo Ouverture du navigateur sur la page d'analyse PDF...

C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe app.py

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ ERREUR: L'application n'a pas pu démarrer correctement.
    echo Pour diagnostiquer le problème, exécutez diagnostic_app.bat
    echo.
    pause
)

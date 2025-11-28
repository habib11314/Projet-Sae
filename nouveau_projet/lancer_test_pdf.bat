@echo off
echo ====================================
echo LANCEMENT SIMPLE DE L'ANALYSEUR PDF
echo ====================================
echo.

echo Démarrage de l'application de test simplifiée...
echo Cette version lance uniquement l'analyseur de factures PDF sans la version complète.
echo.

C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe test_bouton_pdf.py

echo.
if %errorlevel% neq 0 (
    echo [ERREUR] L'application de test n'a pas pu démarrer correctement.
    echo Vérifiez que toutes les dépendances sont installées:
    echo pip install flask pandas plotly pdfplumber PyPDF2
) else (
    echo [OK] L'application de test est en cours d'exécution.
    echo Ouvrez votre navigateur à l'adresse: http://localhost:5001
    echo Pour analyser une facture PDF, cliquez sur "Analyser vos données".
)

pause

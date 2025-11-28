@echo off
echo ====================================
echo DIAGNOSTIC DE ENERGYINSIGHT
echo ====================================
echo.
echo Date et heure: %DATE% %TIME%
echo.

echo Vérification de Python...
if exist "C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe" (
    echo [OK] Python trouvé à: C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe
    C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe --version
) else (
    echo [ERREUR] Python NON TROUVÉ à: C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe
    echo Recherche d'autres installations Python...
    
    if exist "C:\Python312\python.exe" (
        echo [TROUVÉ] Python à: C:\Python312\python.exe
        C:\Python312\python.exe --version
    ) else (
        echo [NON TROUVÉ] Python non trouvé à: C:\Python312\python.exe
    )
    
    if exist "C:\Program Files\Python312\python.exe" (
        echo [TROUVÉ] Python à: C:\Program Files\Python312\python.exe
        "C:\Program Files\Python312\python.exe" --version
    ) else (
        echo [NON TROUVÉ] Python non trouvé à: C:\Program Files\Python312\python.exe
    )
)

echo.
echo Vérification du fichier app.py...
if exist "app.py" (
    echo [OK] app.py trouvé
) else (
    echo [ERREUR] app.py NON TROUVÉ dans le répertoire courant
)

echo.
echo Vérification des dépendances...
echo.
echo Essai de lancer Python pour vérifier Flask...
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe -c "try: import flask; print('[OK] Flask installé:', flask.__version__); except ImportError: print('[ERREUR] Flask non installé')"
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe -c "try: import pandas; print('[OK] Pandas installé:', pandas.__version__); except ImportError: print('[ERREUR] Pandas non installé')"
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe -c "try: import plotly; print('[OK] Plotly installé:', plotly.__version__); except ImportError: print('[ERREUR] Plotly non installé')"
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe -c "try: import pdfplumber; print('[OK] pdfplumber installé:', pdfplumber.__version__); except ImportError: print('[ERREUR] pdfplumber non installé')"

echo.
echo Tentative de démarrage avec diagnostics...
echo.
echo Début des logs d'erreur:
echo ------------------------
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe -c "try: import sys; sys.path.insert(0, '.'); import app; print('[OK] Import app réussi'); except Exception as e: print('[ERREUR] Import app échoué:', e)"
echo ------------------------
echo.

echo Appuyez sur une touche pour continuer et essayer de démarrer l'application...
pause

echo.
echo Tentative de démarrage de l'application avec capture des erreurs...
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe app.py 2> error_log.txt
if %errorlevel% neq 0 (
    echo [ERREUR] L'application n'a pas démarré correctement. Consultez error_log.txt pour plus de détails.
    echo Contenu de error_log.txt:
    type error_log.txt
) else (
    echo [OK] L'application semble avoir démarré sans erreur.
)

echo.
echo Diagnostic terminé.
echo Pour plus d'aide, envoyez le contenu de cette fenêtre à l'équipe de support.
pause

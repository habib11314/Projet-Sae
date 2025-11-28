@echo off
echo ======================================================================
echo DIAGNOSTIC AVANCE ENERGYINSIGHT
echo ======================================================================
echo.
echo [INFO] Verification de l'environnement Python...
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Python n'est pas correctement installe
    pause
    exit /b 1
)

echo.
echo [INFO] Verification des dependances Flask...
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe -c "import flask; print(f'Flask version: {flask.__version__}')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Flask n'est pas correctement installe
    echo [INFO] Installation de Flask...
    C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe -m pip install flask
)

echo.
echo [INFO] Verification de WeasyPrint...
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe -c "import weasyprint; print(f'WeasyPrint version: {weasyprint.__version__}')"
if %ERRORLEVEL% NEQ 0 (
    echo [AVERTISSEMENT] WeasyPrint n'est pas installe (necessaire pour les PDF)
)

echo.
echo [INFO] Test de lancement de l'application avec debug avance...
echo.
echo [INFO] Lancement de l'application principale avec trace...
set FLASK_ENV=development
set FLASK_DEBUG=1
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe -u app.py
pause

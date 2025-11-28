@echo off
echo ================================================
echo     EnergyInsight - Lancement Direct
echo ================================================
echo.

REM Essayer differentes commandes Python
echo Tentative de lancement avec python...
python app.py 2>nul
if %errorlevel% equ 0 goto END

echo.
echo Tentative de lancement avec py...
py app.py 2>nul
if %errorlevel% equ 0 goto END

echo.
echo Tentative de lancement avec python3...
python3 app.py 2>nul
if %errorlevel% equ 0 goto END

echo.
echo ERREUR: Python non trouve ou non installe
echo.
echo Solutions:
echo 1. Installer Python depuis Microsoft Store
echo 2. Installer Python depuis python.org
echo 3. Utiliser Anaconda ou Miniconda
echo.
echo Installation Microsoft Store (Recommandee):
echo - Ouvrir Microsoft Store
echo - Chercher "Python 3.11" ou "Python 3.12"
echo - Cliquer "Obtenir" pour installer
echo.
pause
exit /b 1

:END
echo.
echo Application fermee.
pause

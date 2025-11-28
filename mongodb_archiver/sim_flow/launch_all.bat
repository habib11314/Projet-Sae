@echo off
REM Script batch pour lancer les 4 simulateurs dans des terminaux separés
REM Usage: launch_all.bat

echo.
echo ================================
echo   LANCEUR DE SIMULATEURS
echo ================================
echo.

REM Detecter Python (priorite a py.exe pour Windows)
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
    ) else (
        echo [ERREUR] Python non trouve dans PATH
        pause
        exit /b 1
    )
)

echo [OK] Python commande: %PYTHON_CMD%

REM Verifier si venv existe
if exist "%~dp0..\venv\Scripts\activate.bat" (
    echo [OK] Virtual environment trouve
    set VENV_ACTIVATE=call "%~dp0..\venv\Scripts\activate.bat" ^&^& 
) else (
    echo [WARN] Pas de venv, utilisation Python systeme
    set VENV_ACTIVATE=
)

echo.
echo Ouverture des terminaux...
echo.

REM Terminal 1 - Client
echo [1/4] Client Simulator
start "CLIENT SIMULATOR" cmd /k "cd /d "%~dp0.." && %VENV_ACTIVATE%echo. && echo ===== CLIENT SIMULATOR ===== && echo Cree des commandes aleatoires && echo. && %PYTHON_CMD% clients\client_sim.py"
timeout /t 1 /nobreak >nul

REM Terminal 2 - Platform
echo [2/4] Platform Simulator
start "PLATFORM SIMULATOR" cmd /k "cd /d "%~dp0.." && %VENV_ACTIVATE%echo. && echo ===== PLATFORM SIMULATOR ===== && echo Orchestre les demandes && echo. && %PYTHON_CMD% plateforme\platform_sim.py"
timeout /t 1 /nobreak >nul

REM Terminal 3 - Restaurant
echo [3/4] Restaurant Simulator
start "RESTAURANT SIMULATOR" cmd /k "cd /d "%~dp0.." && %VENV_ACTIVATE%echo. && echo ===== RESTAURANT SIMULATOR ===== && echo Accepte/Refuse les commandes && echo. && %PYTHON_CMD% restaurants\restaurant_sim.py"
timeout /t 1 /nobreak >nul

REM Terminal 4 - Livreur
echo [4/4] Livreur Simulator
start "LIVREUR SIMULATOR" cmd /k "cd /d "%~dp0.." && %VENV_ACTIVATE%echo. && echo ===== LIVREUR SIMULATOR ===== && echo Accepte/Refuse les livraisons && echo. && %PYTHON_CMD% livreurs\livreur_sim.py"

echo.
echo ================================
echo   4 TERMINAUX LANCES !
echo ================================
echo.
echo Conseils:
echo   - Disposez les fenetres cote a cote
echo   - Appuyez Ctrl+C pour arreter
echo   - Consultez sim_flow\README.md
echo.
pause

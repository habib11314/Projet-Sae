# Script PowerShell pour lancer les 4 simulateurs dans des terminaux séparés
# Usage: .\sim_flow\launch_all.ps1

Write-Host "🚀 Lancement des 4 simulateurs..." -ForegroundColor Cyan
Write-Host ""

# Chemin vers le répertoire du projet
$projectPath = Split-Path -Parent $PSScriptRoot

# Vérifier si on est dans le bon répertoire
if (-not (Test-Path "$projectPath\clients\client_sim.py")) {
    Write-Host "❌ Erreur: Scripts de simulation non trouvés dans clients/" -ForegroundColor Red
    Write-Host "   Assurez-vous d'exécuter depuis le dossier mongodb_archiver" -ForegroundColor Yellow
    exit 1
}

# Chemin vers Python (essayer plusieurs options)
$pythonCmd = "python"
if (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command "python3" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
}

Write-Host "✓ Python command: $pythonCmd" -ForegroundColor Green

# Vérifier si venv existe
$venvActivate = "$projectPath\venv\Scripts\Activate.ps1"
$activateCmd = ""
if (Test-Path $venvActivate) {
    Write-Host "✓ Virtual environment trouvé" -ForegroundColor Green
    $activateCmd = ". '$venvActivate'; "
} else {
    Write-Host "⚠️  Pas de venv trouvé, utilisation du Python système" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📦 Ouverture des terminaux..." -ForegroundColor Cyan
Write-Host ""

# Terminal 1 - Client Simulator
Write-Host "🧑 Terminal 1: Client Simulator" -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$projectPath'; $activateCmd Write-Host '🧑 CLIENT SIMULATOR' -ForegroundColor Blue; Write-Host 'Crée des commandes aléatoires' -ForegroundColor Gray; Write-Host ''; $pythonCmd clients\client_sim.py"

Start-Sleep -Seconds 1

# Terminal 2 - Platform Simulator
Write-Host "🏢 Terminal 2: Platform Simulator" -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$projectPath'; $activateCmd Write-Host '🏢 PLATFORM SIMULATOR' -ForegroundColor Magenta; Write-Host 'Orchestre les demandes' -ForegroundColor Gray; Write-Host ''; $pythonCmd plateforme\platform_sim.py"

Start-Sleep -Seconds 1

# Terminal 3 - Restaurant Simulator
Write-Host "🍽️  Terminal 3: Restaurant Simulator" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$projectPath'; $activateCmd Write-Host '🍽️  RESTAURANT SIMULATOR' -ForegroundColor Green; Write-Host 'Accepte/Refuse les commandes' -ForegroundColor Gray; Write-Host ''; $pythonCmd restaurants\restaurant_sim.py"

Start-Sleep -Seconds 1

# Terminal 4 - Livreur Simulator
Write-Host "🚗 Terminal 4: Livreur Simulator" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$projectPath'; $activateCmd Write-Host '🚗 LIVREUR SIMULATOR' -ForegroundColor Yellow; Write-Host 'Accepte/Refuse les livraisons' -ForegroundColor Gray; Write-Host ''; $pythonCmd livreurs\livreur_sim.py"

Write-Host ""
Write-Host "✅ 4 terminaux lancés!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Conseils:" -ForegroundColor Cyan
Write-Host "   - Disposez les terminaux côte à côte pour voir le flux" -ForegroundColor Gray
Write-Host "   - Appuyez sur Ctrl+C dans chaque terminal pour arrêter" -ForegroundColor Gray
Write-Host "   - Consultez sim_flow\README.md pour plus d'infos" -ForegroundColor Gray
Write-Host ""
Write-Host "🎬 Les simulateurs sont maintenant actifs!" -ForegroundColor Cyan

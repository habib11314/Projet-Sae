"""
Launcher Python pour la simulation multi-terminaux
Lance les 4 simulateurs dans des fenêtres CMD séparées
"""
import os
import sys
import subprocess
import time
import platform
from pathlib import Path

# Force UTF-8 encoding for prints on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_python_command():
    """Détecte la commande Python disponible"""
    commands = ['py', 'python', 'python3']
    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, '--version'], 
                capture_output=True, 
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                print(f"✅ Python trouvé: {cmd} ({result.stdout.strip()})")
                return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print("❌ Python non trouvé dans PATH")
    sys.exit(1)

def get_script_dir():
    """Retourne le dossier contenant ce script"""
    return Path(__file__).parent.absolute()

def launch_windows_terminal(script_name, title, python_cmd, script_dir):
    """Lance un script dans un nouveau terminal Windows"""
    script_path = script_dir.parent / script_name
    
    # Build relative path for Windows (script_name may contain '/').
    script_rel = str(script_name).replace('/', '\\')
    # Commande pour CMD avec /k (keep window open)
    # Important: start "titre" doit avoir le titre entre guillemets
    cmd = f'start "{title}" cmd /k "cd /d {script_dir.parent} && echo ===== {title} ===== && echo. && {python_cmd} {script_rel}' + '"'
    
    # Utilise shell=True pour que 'start' fonctionne
    subprocess.Popen(cmd, shell=True)
    print(f"  🚀 {title}")
    time.sleep(1)  # Pause entre chaque lancement

def launch_unix_terminal(script_name, title, python_cmd, script_dir):
    """Lance un script dans un nouveau terminal Unix/Linux/Mac"""
    script_path = script_dir / script_name
    
    # Pour Linux/Mac, essayer différents émulateurs de terminal
    terminals = [
        ['gnome-terminal', '--', 'bash', '-c'],
        ['xterm', '-hold', '-e'],
        ['konsole', '-e'],
        ['xfce4-terminal', '-x'],
        ['osascript', '-e']  # macOS
    ]
    
    for term in terminals:
        try:
            if term[0] == 'osascript':  # macOS
                cmd = [
                    'osascript', '-e',
                    f'tell app "Terminal" to do script "cd {script_dir.parent} && {python_cmd} sim_flow/{script_name}"'
                ]
            else:
                cmd = term + [f'{python_cmd} {script_path}; exec bash']
            
            subprocess.Popen(cmd)
            print(f"  🚀 {title}")
            time.sleep(1)
            return
        except FileNotFoundError:
            continue
    
    print(f"  ⚠️  Aucun émulateur de terminal trouvé")
    print(f"     Lancez manuellement: {python_cmd} {script_path}")

def main():
    print()
    print("=" * 60)
    print("  🎬 LANCEUR DE SIMULATION MULTI-TERMINAUX")
    print("=" * 60)
    print()
    
    # Détection Python
    python_cmd = get_python_command()
    
    # Détection du système
    system = platform.system()
    print(f"✅ Système détecté: {system}")
    print()
    
    # Obtenir le dossier des scripts
    script_dir = get_script_dir()
    print(f"📁 Dossier: {script_dir}")
    print()
    
    # Vérifier que les scripts existent
    # Prefer the reorganized paths under repo root; keep simple names for titles
    scripts = [
        ('clients/client_sim.py', 'CLIENT SIMULATOR'),
        ('plateforme/platform_sim.py', 'PLATFORM SIMULATOR'),
        ('restaurants/restaurant_sim.py', 'RESTAURANT SIMULATOR'),
        ('livreurs/livreur_sim.py', 'LIVREUR SIMULATOR'),
    ]
    
    print("🔍 Vérification des scripts (recherche dans clients/, restaurants/, livreurs/, plateforme/)...")
    for script_name, _ in scripts:
        # check in repo root relative to sim_flow parent
        candidate = script_dir.parent / script_name
        if not candidate.exists():
            print(f"  ❌ {script_name} non trouvé à {candidate}!")
            sys.exit(1)
        print(f"  ✅ {script_name}")
    
    print()
    print("🚀 Lancement des terminaux...")
    print()
    
    # Lancer les 4 simulateurs
    for i, (script_name, title) in enumerate(scripts, 1):
        if system == 'Windows':
            launch_windows_terminal(script_name, title, python_cmd, script_dir)
        else:
            launch_unix_terminal(script_name, title, python_cmd, script_dir)
    
    print()
    print("=" * 60)
    print("  ✅ 4 TERMINAUX LANCÉS !")
    print("=" * 60)
    print()
    print("💡 Conseils:")
    print("  • Disposez les fenêtres côte à côte")
    print("  • Appuyez Ctrl+C dans chaque terminal pour arrêter")
    print("  • Consultez README.md pour plus d'infos")
    print()
    print("⚠️  Si les terminaux se ferment immédiatement:")
    print("  1. Vérifiez .env dans le dossier parent")
    print("  2. Vérifiez la connexion MongoDB: py ../test_config.py")
    print("  3. Peuplez la base: py ../simulate.py --count 500")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Launcher interrompu")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

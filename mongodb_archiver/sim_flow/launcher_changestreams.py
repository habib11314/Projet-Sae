# -*- coding: utf-8 -*-
"""
Launcher pour les simulateurs avec Change Streams
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

# Force UTF-8 encoding for prints on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_python_command():
    """Détecte la commande Python disponible"""
    for cmd in ['py', 'python3', 'python']:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return 'python'

def get_script_dir():
    """Retourne le dossier contenant ce script"""
    return Path(__file__).parent

def launch_windows_terminal(script_name, title, python_cmd, script_dir):
    """Lance un script dans un nouveau terminal Windows"""
    parent_dir = script_dir.parent
    script_path = script_dir / script_name
    # Build a single command string for Windows 'start' to ensure correct quoting
    parent = str(parent_dir)
    # script_name may include a subfolder like 'clients/client_sim_changestreams.py'
    script_rel = script_name.replace('/', '\\')

    # The inner command (after /k) must be wrapped in quotes; escape inner quotes correctly
    inner = f'cd /d "{parent}" && {python_cmd} {script_rel}'
    cmd_str = f'cmd.exe /c start "{title}" cmd.exe /k "{inner}"'

    try:
        # Debug output to help diagnosing issues when windows don't appear
        print(f"  -> executing: {cmd_str}")
        subprocess.Popen(cmd_str, shell=True)
        print(f"  OK {title}")
    except Exception as e:
        print(f"  ERREUR {title}: {e}")

def main():
    print()
    print("=" * 60)
    print("  LAUNCHER CHANGE STREAMS - 4 SIMULATEURS")
    print("=" * 60)
    print()
    
    python_cmd = get_python_command()
    system = platform.system()
    script_dir = get_script_dir()
    
    print(f"Python: {python_cmd}")
    print(f"Systeme: {system}")
    print()
    
    if system != 'Windows':
        print("ERREUR: Ce launcher est concu pour Windows")
        print("Lancez manuellement les scripts *_changestreams.py")
        return 1
    
    # Updated to new domain folders under the repository root
    simulators = [
        ('clients/client_sim_changestreams.py', 'CLIENT'),
        ('plateforme/platform_sim_changestreams.py', 'PLATFORM'),
        ('restaurants/restaurant_sim_changestreams.py', 'RESTAURANT'),
        ('livreurs/livreur_sim_changestreams.py', 'LIVREUR'),
    ]
    
    print("Lancement des terminaux...")
    print()
    
    for script, title in simulators:
        launch_windows_terminal(script, title, python_cmd, script_dir)
    
    print()
    print("=" * 60)
    print("  4 TERMINAUX LANCES (Change Streams)!")
    print("=" * 60)
    print()
    print("Les simulateurs utilisent Change Streams pour:")
    print("  - Detection en temps reel des nouvelles commandes")
    print("  - Reception instantanee des reponses")
    print("  - Surveillance des changements de statut")
    print("  - Notifications push aux clients")
    print()
    print("Appuyez Ctrl+C dans chaque terminal pour arreter")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nLauncher interrompu")
        sys.exit(0)
    except Exception as e:
        print(f"\nERREUR: {e}")
        sys.exit(1)

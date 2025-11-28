"""
Launcher Python avancé avec options CLI
"""
import argparse
import os
import sys
import subprocess
import time
from pathlib import Path

# Force UTF-8 encoding for prints on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Importer les fonctions du launcher principal
from launcher import get_python_command, get_script_dir, launch_windows_terminal, launch_unix_terminal
import platform

SIMULATORS = {
    'client': ('client_sim.py', 'CLIENT SIMULATOR'),
    'platform': ('platform_sim.py', 'PLATFORM SIMULATOR'),
    'restaurant': ('restaurant_sim.py', 'RESTAURANT SIMULATOR'),
    'livreur': ('livreur_sim.py', 'LIVREUR SIMULATOR'),
}

def run_inline(script_name, python_cmd):
    """Lance un script dans le terminal actuel (sans ouvrir de nouvelle fenêtre)"""
    script_path = get_script_dir() / script_name
    parent_dir = get_script_dir().parent
    
    print()
    print("=" * 60)
    print(f"  🚀 Lancement de {script_name}")
    print("=" * 60)
    print()
    print("Appuyez Ctrl+C pour arrêter")
    print()
    
    try:
        # Change le répertoire courant
        os.chdir(parent_dir)
        
        # Lance le script
        subprocess.run([python_cmd, f'sim_flow/{script_name}'])
    except KeyboardInterrupt:
        print("\n\n⚠️  Script arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return 1
    
    return 0

def main():
    parser = argparse.ArgumentParser(
        description='Launcher pour la simulation multi-terminaux',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  py launcher_advanced.py                    # Lance les 4 terminaux
  py launcher_advanced.py --only client      # Lance seulement le client
  py launcher_advanced.py --inline platform  # Lance platform dans ce terminal
  py launcher_advanced.py --list             # Liste les simulateurs disponibles
        """
    )
    
    parser.add_argument(
        '--only',
        choices=['client', 'platform', 'restaurant', 'livreur'],
        help='Lance seulement un simulateur (dans une nouvelle fenêtre)'
    )
    
    parser.add_argument(
        '--inline',
        choices=['client', 'platform', 'restaurant', 'livreur'],
        help='Lance un simulateur dans le terminal actuel (sans nouvelle fenêtre)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='Liste les simulateurs disponibles'
    )
    
    args = parser.parse_args()
    
    # Liste les simulateurs
    if args.list:
        print()
        print("Simulateurs disponibles:")
        print()
        for key, (script, title) in SIMULATORS.items():
            print(f"  • {key:12s} → {script:20s} ({title})")
        print()
        return 0
    
    # Détection Python
    python_cmd = get_python_command()
    system = platform.system()
    script_dir = get_script_dir()
    
    # Mode inline (lance dans le terminal actuel)
    if args.inline:
        script_name, _ = SIMULATORS[args.inline]
        return run_inline(script_name, python_cmd)
    
    # Mode --only (lance un seul terminal)
    if args.only:
        print()
        print("=" * 60)
        print(f"  🎬 LANCEMENT: {args.only.upper()}")
        print("=" * 60)
        print()
        
        script_name, title = SIMULATORS[args.only]
        
        if system == 'Windows':
            launch_windows_terminal(script_name, title, python_cmd, script_dir)
        else:
            launch_unix_terminal(script_name, title, python_cmd, script_dir)
        
        print()
        print(f"✅ Terminal lancé: {title}")
        print()
        return 0
    
    # Mode par défaut: lance les 4 terminaux
    print()
    print("=" * 60)
    print("  🎬 LANCEUR DE SIMULATION MULTI-TERMINAUX")
    print("=" * 60)
    print()
    print(f"✅ Système: {system}")
    print()
    print("🚀 Lancement des 4 terminaux...")
    print()
    
    for key, (script_name, title) in SIMULATORS.items():
        if system == 'Windows':
            launch_windows_terminal(script_name, title, python_cmd, script_dir)
        else:
            launch_unix_terminal(script_name, title, python_cmd, script_dir)
    
    print()
    print("=" * 60)
    print("  ✅ 4 TERMINAUX LANCÉS !")
    print("=" * 60)
    print()
    print("💡 Pour tester individuellement:")
    print("  py launcher_advanced.py --only client")
    print("  py launcher_advanced.py --inline platform")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Launcher interrompu")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

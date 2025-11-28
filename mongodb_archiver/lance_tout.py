# -*- coding: utf-8 -*-
"""Script de lancement rapide - Lance les 4 simulateurs
Utilise launcher_advanced.py pour ouvrir Client, Platform, Restaurant, Livreur
"""
import subprocess
import sys
from pathlib import Path

print()
print("=" * 70)
print("  LANCEMENT DES 4 SIMULATEURS")
print("=" * 70)
print()

# Chemin vers launcher_advanced.py
sim_flow_dir = Path(__file__).parent / 'sim_flow'
launcher_path = sim_flow_dir / 'launcher_advanced.py'

if not launcher_path.exists():
    print(f"ERREUR: {launcher_path} introuvable")
    sys.exit(1)

print("Ouverture des terminaux...")
print()

try:
    # Lancer le launcher_advanced sans arguments = lance les 4 terminaux
    result = subprocess.run(
        ['py', str(launcher_path)],
        cwd=str(sim_flow_dir),
        capture_output=False,
        text=True
    )
    
    if result.returncode == 0:
        print()
        print("=" * 70)
        print("  TERMINAUX LANCES AVEC SUCCES!")
        print("=" * 70)
        print()
        print("Observez les 4 fenetres ouvertes:")
        print("  1. CLIENT     - Cree des commandes")
        print("  2. PLATFORM   - Orchestre le flux")
        print("  3. RESTAURANT - Accepte/refuse les commandes")
        print("  4. LIVREUR    - Accepte/refuse les livraisons")
        print()
        print("Le flux complet:")
        print("  Client cree commande -> Platform envoie au Restaurant")
        print("  -> Restaurant accepte -> Platform cherche Livreur")
        print("  -> Livreur accepte -> Platform ATTRIBUE et notifie Client")
        print()
        print("Appuyez Ctrl+C dans chaque terminal pour arreter")
        print()
    else:
        print(f"Le launcher a termine avec le code: {result.returncode}")
        
except KeyboardInterrupt:
    print("\nInterrompu par l'utilisateur")
except Exception as e:
    print(f"ERREUR: {e}")
    sys.exit(1)

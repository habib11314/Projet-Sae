"""Script de test automatique pour le flux complet
Lance les 4 simulateurs dans des terminaux séparés et crée une commande de test
"""
import os
import sys
import time
import subprocess
from pathlib import Path

print()
print("=" * 70)
print("  🚀 TEST AUTOMATIQUE - FLUX COMPLET UBEREATS")
print("=" * 70)
print()

# Déterminer le chemin du projet
project_root = Path(__file__).parent
sim_flow_dir = project_root / 'sim_flow'
launcher_path = sim_flow_dir / 'launcher.py'

# Vérifier que launcher.py existe
if not launcher_path.exists():
    print(f"❌ Erreur: {launcher_path} introuvable")
    sys.exit(1)

print("📋 ÉTAPE 1/3 - Lancement des 4 simulateurs")
print("   Ouverture des terminaux Client, Platform, Restaurant, Livreur...")
print()

# Lancer le launcher
try:
    # Utiliser py pour lancer le launcher
    result = subprocess.run(
        ['py', str(launcher_path)],
        cwd=str(sim_flow_dir),
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("✅ Les 4 terminaux ont été lancés avec succès!")
        print(result.stdout)
    else:
        print("⚠️  Le launcher a terminé avec des avertissements:")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
except subprocess.TimeoutExpired:
    print("✅ Les terminaux sont en cours d'exécution (timeout normal)")
except Exception as e:
    print(f"❌ Erreur lors du lancement: {e}")
    sys.exit(1)

print()
print("⏳ Attente de 5 secondes pour que les simulateurs démarrent...")
time.sleep(5)

print()
print("📋 ÉTAPE 2/3 - Création d'une commande de test")
print("   Insertion d'une commande avec status='pending_request'...")
print()

# Créer une commande de test
make_order_script = sim_flow_dir / 'make_test_order.py'
if make_order_script.exists():
    try:
        result = subprocess.run(
            ['py', str(make_order_script)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Commande de test créée:")
            print(result.stdout)
            
            # Extraire le numéro de commande
            for line in result.stdout.split('\n'):
                if 'INSERTED_TEST_ORDER' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        numero_commande = parts[1]
                        print(f"   📦 Numéro: {numero_commande}")
        else:
            print("⚠️  Erreur lors de la création de la commande:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Erreur: {e}")
else:
    print(f"⚠️  Script {make_order_script} introuvable, création manuelle...")

print()
print("📋 ÉTAPE 3/3 - Observation du flux")
print()
print("🔍 Que se passe-t-il maintenant ?")
print()
print("1️⃣  TERMINAL CLIENT")
print("   → Crée la commande et surveille les changements de statut")
print("   → Affichera la NOTIFICATION quand le livreur sera assigné")
print()
print("2️⃣  TERMINAL PLATFORM")
print("   → Détecte la commande en attente")
print("   → Envoie requête au restaurant")
print("   → Cherche un livreur disponible")
print("   → ATTRIBUE la commande et envoie notification au client")
print()
print("3️⃣  TERMINAL RESTAURANT")
print("   → Reçoit la requête de la plateforme")
print("   → Accepte ou refuse aléatoirement (70% acceptation)")
print("   → Affiche un bloc formaté avec la décision")
print()
print("4️⃣  TERMINAL LIVREUR")
print("   → Reçoit la requête de livraison")
print("   → Accepte ou refuse aléatoirement (70% acceptation)")
print("   → Affiche une BANNIÈRE D'ATTRIBUTION si accepté")
print()
print("=" * 70)
print("  ✅ TEST EN COURS - Observez les 4 terminaux!")
print("=" * 70)
print()
print("💡 Conseils:")
print("   • Les simulateurs tournent en boucle")
print("   • Le client crée une nouvelle commande toutes les 3 secondes")
print("   • Appuyez sur Ctrl+C dans chaque terminal pour arrêter")
print()
print("📊 Pour vérifier l'état d'une commande dans MongoDB:")
print(f"   py {sim_flow_dir / 'show_order_status.py'} <numero_commande>")
print()

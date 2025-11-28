"""
Lanceur de Simulation - 4 Terminaux Automatiques
- Terminal 1: Manager (écoute et attribue)
- Terminal 2: Restaurant (accepte/refuse préparation)
- Terminal 3: Livreur (accepte/refuse livraison)
- Terminal 4: Client (génère commandes)
"""

import subprocess
import time
import sys

def lancer_terminal(titre, script, args=""):
    """Lance un script Python dans un nouveau terminal PowerShell"""
    commande = f'py "{script}" {args}'
    
    # Créer un nouveau terminal PowerShell avec titre
    subprocess.Popen([
        "powershell.exe",
        "-NoExit",
        "-Command",
        f"$Host.UI.RawUI.WindowTitle = '{titre}'; {commande}"
    ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    print(f"✅ Lancé: {titre}")
    time.sleep(2)  # Délai entre chaque lancement

def main():
    print("\n" + "="*60)
    print("🚀 LANCEMENT DE LA SIMULATION - Plusieurs Livreurs")
    print("="*60 + "\n")
    
    import os
    chemin_base = os.path.dirname(os.path.abspath(__file__))
    
    # Vérifier que Redis tourne
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis actif\n")
    except:
        print("❌ ERREUR: Redis non accessible !")
        print("   → Démarrez Redis d'abord:\n")
        print("   cd C:\\Users\\PC\\Downloads\\redis\\Redis-x64-5.0.14.1")
        print("   Start-Process .\\redis-server.exe\n")
        return
    
    print("📂 Dossier:", chemin_base)
    print("\n🎬 Lancement des acteurs...\n")
    
    # 1. Lancer le Manager (moved into managers/)
    manager_script = os.path.join(chemin_base, "managers", "manager_auto_ameliore.py")
    lancer_terminal("MANAGER - Attribution Automatique", manager_script)
    
    # 2. Lancer le Restaurant (moved into restaurants/)
    restaurant_script = os.path.join(chemin_base, "restaurants", "restaurant_auto.py")
    lancer_terminal("RESTAURANT - Confirmation Commandes", restaurant_script)
    
    # 3. Lancer plusieurs Livreurs (5 livreurs par défaut) (moved into livreurs/)
    livreur_script = os.path.join(chemin_base, "livreurs", "livreur_auto_ameliore.py")
    nb_livreurs = 5  # Vous pouvez changer ce nombre
    for i in range(1, nb_livreurs + 1):
        livreur_id = f"livreur-{i:03d}"
        lancer_terminal(f"LIVREUR-{i:03d} - Taux aléatoire", livreur_script, livreur_id)
    
    # 4. Lancer le Client
    client_script = os.path.join(chemin_base, "clients", "client_auto_ameliore.py")
    lancer_terminal("CLIENT - Commandes Aléatoires", client_script)
    
    print("\n" + "="*60)
    print(f"✅ SIMULATION LANCÉE - {3 + nb_livreurs} Terminaux actifs")
    print("="*60)
    print("\n📊 État:")
    print("   🟢 Terminal 1: MANAGER (coordonne tout)")
    print("   🟢 Terminal 2: RESTAURANT (accepte/refuse préparation)")
    print(f"   🟢 Terminaux 3-{2+nb_livreurs}: LIVREURS x{nb_livreurs} (acceptent/refusent livraisons)")
    print(f"   🟢 Terminal {3+nb_livreurs}: CLIENT (génère commandes)")
    print(f"\n💡 Observez les {3+nb_livreurs} terminaux pour voir le flux complet !")
    print("💡 Chaque terminal peut être fermé avec Ctrl+C")
    print("\n🔹 Pour lancer plus de livreurs, exécutez:")
    print("   py livreur_auto_ameliore.py livreur-002")
    print("   py livreur_auto_ameliore.py livreur-003")
    print("   etc.\n")

if __name__ == "__main__":
    main()

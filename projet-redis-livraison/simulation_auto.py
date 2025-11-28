"""
Script de simulation automatique du système de livraison Redis
Lance automatiquement : Manager + Livreurs + Clients
"""

import subprocess
import time
import sys
import os

def lancer_processus(script, args=None, nom="Processus"):
    """Lance un script Python dans un nouveau processus"""
    cmd = [sys.executable, script]
    if args:
        cmd.extend(args)
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        print(f"✅ {nom} lancé (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Erreur lors du lancement de {nom}: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("🚀 SIMULATION AUTOMATIQUE - Système de Livraison Redis")
    print("="*60)
    
    processus = []
    
    # 1. Lancer le Manager
    print("\n📋 Étape 1/3 : Lancement du Manager...")
    manager = lancer_processus("manager.py", nom="Manager")
    if manager:
        processus.append(manager)
        time.sleep(2)  # Attendre que le manager soit prêt
    
    # 2. Lancer plusieurs livreurs automatiques
    print("\n📋 Étape 2/3 : Lancement des Livreurs automatiques...")
    nb_livreurs = 5
    for i in range(1, nb_livreurs + 1):
        livreur = lancer_processus(
            "livreur_auto.py", 
            args=[f"livreur-{i:03d}"],
            nom=f"Livreur {i:03d}"
        )
        if livreur:
            processus.append(livreur)
        time.sleep(0.5)
    
    # 3. Lancer des clients automatiques
    print("\n📋 Étape 3/3 : Lancement des Clients automatiques...")
    nb_clients = 3
    for i in range(1, nb_clients + 1):
        client = lancer_processus(
            "client_auto.py",
            nom=f"Client {i}"
        )
        if client:
            processus.append(client)
        time.sleep(2)  # Espacer les commandes
    
    print("\n" + "="*60)
    print("✅ Simulation lancée avec succès !")
    print("="*60)
    print(f"\n📊 Processus actifs :")
    print(f"   - 1 Manager")
    print(f"   - {nb_livreurs} Livreurs automatiques")
    print(f"   - {nb_clients} Clients automatiques")
    print(f"\n💡 Les fenêtres s'ouvrent automatiquement.")
    print(f"⚠️  Appuyez sur Ctrl+C pour arrêter la simulation.")
    
    try:
        # Garder le script actif
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de la simulation...")
        for p in processus:
            try:
                p.terminate()
            except:
                pass
        print("👋 Simulation terminée")

if __name__ == "__main__":
    main()

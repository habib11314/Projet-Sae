"""
Script d'exemple - Démo complète du système d'archivage
Ce script montre comment utiliser tous les composants
"""
import time
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from logger import setup_logger
from archiver import OrderArchiver
from watcher import OrderWatcher
from generator import DataGenerator


def demo_batch_archiving():
    """Démonstration du mode batch"""
    print("\n" + "="*70)
    print("📦 DEMO: Archivage par lots (Batch Mode)")
    print("="*70 + "\n")
    
    # Configuration pour simulation
    config = Config.for_simulation()
    logger = setup_logger('demo_batch')
    
    # Créer l'archiver
    archiver = OrderArchiver(config, logger)
    
    # Connexion
    if not archiver.connect():
        print("❌ Erreur de connexion")
        return
    
    # Créer les index
    archiver.ensure_indexes()
    
    # Archiver en mode dry-run
    print("🔍 Mode DRY-RUN (simulation)...")
    stats = archiver.archive_all(dry_run=True)
    
    print(archiver.get_stats_summary())
    
    # Archivage réel (commenté par sécurité)
    # print("\n✅ Mode PRODUCTION...")
    # stats = archiver.archive_all(dry_run=False)
    # print(archiver.get_stats_summary())
    
    archiver.close()


def demo_watch_mode():
    """Démonstration du mode watch avec Change Streams"""
    print("\n" + "="*70)
    print("👀 DEMO: Mode Watch (Change Streams)")
    print("="*70 + "\n")
    
    print("""
Ce mode utilise MongoDB Change Streams pour détecter en temps réel
quand une commande passe au statut 'livrée' et l'archive immédiatement.

Avantages:
✅ Archivage automatique en temps réel
✅ Pas besoin de cron jobs
✅ Resume après interruption
✅ Filtrage côté serveur (performant)

Prérequis:
⚠️  Nécessite un MongoDB Replica Set (pas standalone)
⚠️  Disponible dans MongoDB Atlas par défaut
    """)
    
    response = input("Démarrer le watcher ? (y/N): ")
    if response.lower() != 'y':
        print("Demo annulée")
        return
    
    config = Config.for_simulation()
    logger = setup_logger('demo_watch')
    
    watcher = OrderWatcher(config, logger)
    
    try:
        print("\n🚀 Démarrage du watcher...")
        print("💡 Ouvrez un autre terminal et modifiez une commande:")
        print("   db.Commande.updateOne({numero_commande: 'CMD-2025-000001'}, {$set: {status: 'livrée'}})")
        print("\n⏹️  Appuyez sur Ctrl+C pour arrêter\n")
        
        watcher.watch_simple()
        
    except KeyboardInterrupt:
        print("\n✅ Watcher arrêté")


def demo_data_generation():
    """Démonstration de la génération de données"""
    print("\n" + "="*70)
    print("🎲 DEMO: Génération de données de test")
    print("="*70 + "\n")
    
    config = Config.for_simulation()
    logger = setup_logger('demo_generator')
    
    generator = DataGenerator(config, seed=42, logger=logger)
    
    print("""
Génération de données réalistes:
- Clients avec noms/emails français
- Livreurs avec véhicules
- Restaurants avec cuisines variées
- Menus avec prix
- Commandes avec statuts variés
    """)
    
    response = input("Générer 100 commandes de test ? (y/N): ")
    if response.lower() != 'y':
        print("Demo annulée")
        return
    
    generator.populate_database(
        n_clients=20,
        n_livreurs=10,
        n_restaurants=10,
        n_menus=30,
        n_commandes=100,
        p_delivered=0.3,
        p_null_ids=0.05,
        clear_existing=True
    )
    
    generator.close()
    print("\n✅ Données générées avec succès!")


def demo_completeness_check():
    """Démonstration de la vérification de complétude"""
    print("\n" + "="*70)
    print("🔍 DEMO: Vérification de complétude des données")
    print("="*70 + "\n")
    
    config = Config.for_simulation()
    logger = setup_logger('demo_completeness')
    archiver = OrderArchiver(config, logger)
    
    # Exemples de commandes
    complete_order = {
        'nom_client': 'Jean Dupont',
        'nom_livreur': 'Alice Martin',
        'nom_restaurant': 'Le Bistrot',
        'nom_menu': 'Menu du jour',
        'coût_commande': 15.5
    }
    
    incomplete_order = {
        'nom_client': 'Client inconnu',
        'nom_livreur': None,
        'nom_restaurant': 'Le Bistrot',
        'nom_menu': 'Menu non spécifié',
        'coût_commande': 15.5
    }
    
    print("Commande complète:")
    is_complete, missing = archiver.check_completeness(complete_order)
    print(f"  Complete: {is_complete}")
    print(f"  Champs manquants: {missing if missing else 'Aucun'}")
    
    print("\nCommande incomplète:")
    is_complete, missing = archiver.check_completeness(incomplete_order)
    print(f"  Complete: {is_complete}")
    print(f"  Champs manquants: {missing}")


def demo_enrichment_pipeline():
    """Affichage du pipeline d'enrichissement"""
    print("\n" + "="*70)
    print("🔗 DEMO: Pipeline d'enrichissement MongoDB")
    print("="*70 + "\n")
    
    config = Config.for_simulation()
    archiver = OrderArchiver(config)
    
    pipeline = archiver.get_enrichment_pipeline("CMD-EXAMPLE")
    
    print("Le pipeline effectue les opérations suivantes:")
    print("1. $match   : Filtre la commande par numero_commande")
    print("2. $lookup  : Join avec Client (id_client)")
    print("3. $lookup  : Join avec Livreur (id_livreur)")
    print("4. $lookup  : Join avec Restaurants (id_restaurant)")
    print("5. $lookup  : Join avec Menu (id_menu)")
    print("6. $addFields : Transformation des tableaux en objets")
    print("7. $project : Sélection et normalisation des champs")
    
    print("\n📊 Nombre d'étapes:", len(pipeline))
    print("🔗 Nombre de joins:", sum(1 for stage in pipeline if '$lookup' in stage))


def main():
    """Menu principal"""
    while True:
        print("\n" + "="*70)
        print("🎯 MONGODB ORDER ARCHIVER - DEMOS")
        print("="*70)
        print("\n1. 📦 Archivage par lots (Batch)")
        print("2. 👀 Mode Watch avec Change Streams")
        print("3. 🎲 Génération de données de test")
        print("4. 🔍 Vérification de complétude")
        print("5. 🔗 Pipeline d'enrichissement")
        print("0. ❌ Quitter")
        
        choice = input("\nChoisissez une option: ")
        
        if choice == '1':
            demo_batch_archiving()
        elif choice == '2':
            demo_watch_mode()
        elif choice == '3':
            demo_data_generation()
        elif choice == '4':
            demo_completeness_check()
        elif choice == '5':
            demo_enrichment_pipeline()
        elif choice == '0':
            print("\n👋 Au revoir!")
            break
        else:
            print("❌ Option invalide")
        
        if choice != '0':
            input("\n▶️  Appuyez sur Entrée pour continuer...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir!")
        sys.exit(0)

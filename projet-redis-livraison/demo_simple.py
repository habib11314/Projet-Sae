"""
Démonstration Simplifiée - Tout dans un seul processus
Simule le système complet sans ouvrir plusieurs fenêtres
"""

import redis
import json
import random
import time
from datetime import datetime
from threading import Thread

# Configuration
NB_LIVREURS = 5
NB_CLIENTS = 3
DELAI_ENTRE_COMMANDES = 3  # secondes

class SystemeComplet:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        print("✅ Connexion à Redis établie\n")
    
    def simulation_complete(self):
        """Lance une simulation complète"""
        print("="*70)
        print("🚀 DÉMONSTRATION AUTOMATIQUE - Système de Livraison Redis")
        print("="*70)
        print()
        
        # Générer des commandes aléatoires
        for i in range(NB_CLIENTS):
            print(f"\n{'='*70}")
            print(f"📦 COMMANDE {i+1}/{NB_CLIENTS}")
            print(f"{'='*70}\n")
            
            # Simuler un client qui passe commande
            self.simuler_commande()
            
            # Attendre entre les commandes
            if i < NB_CLIENTS - 1:
                print(f"\n⏳ Attente de {DELAI_ENTRE_COMMANDES} secondes avant la prochaine commande...\n")
                time.sleep(DELAI_ENTRE_COMMANDES)
        
        print("\n" + "="*70)
        print("✅ SIMULATION TERMINÉE")
        print("="*70)
        print(f"\n📊 Résumé :")
        print(f"   - {NB_CLIENTS} commandes passées")
        print(f"   - Système de notifications temps réel démontré")
        print(f"   - Attribution automatique des livreurs")
        print("\n💡 Le système Redis Pub/Sub fonctionne parfaitement !")
        print()
    
    def simuler_commande(self):
        """Simule une commande complète"""
        # 1. Créer une commande aléatoire
        commande = self.generer_commande_aleatoire()
        
        print(f"👤 Client: {commande['nom_client']}")
        print(f"🏪 Restaurant: {commande['restaurant_nom']}")
        print(f"💰 Montant: {commande['montant_total']}€")
        print(f"📍 Livraison: {commande['adresse_livraison']}")
        print(f"🚴 Rémunération livreur: {commande['remuneration_livreur']}€")
        
        # 2. Publier la commande
        print(f"\n📤 Publication de la commande sur Redis...")
        message_json = json.dumps(commande, ensure_ascii=False)
        nb_manager = self.redis_client.publish('nouvelles-commandes', message_json)
        print(f"   ✅ {nb_manager} manager(s) ont reçu la commande")
        
        time.sleep(0.5)
        
        # 3. Créer et publier l'offre (simulation du manager)
        offre = {
            "id_commande": commande['id_commande'],
            "restaurant_nom": commande['restaurant_nom'],
            "restaurant_adresse": commande['restaurant_adresse'],
            "adresse_livraison": commande['adresse_livraison'],
            "remuneration_livreur": commande['remuneration_livreur']
        }
        
        print(f"\n📢 Publication de l'offre aux livreurs...")
        message_offre = json.dumps(offre, ensure_ascii=False)
        nb_livreurs = self.redis_client.publish('offres-courses', message_offre)
        print(f"   ✅ {nb_livreurs} livreur(s) ont reçu l'offre")
        
        time.sleep(0.5)
        
        # 4. Simuler la réponse d'un livreur aléatoire
        id_livreur = f"livreur-{random.randint(1, NB_LIVREURS):03d}"
        candidature = {
            "id_livreur": id_livreur,
            "id_commande": commande['id_commande']
        }
        
        print(f"\n🚴 Le {id_livreur} manifeste son intérêt...")
        message_candidature = json.dumps(candidature, ensure_ascii=False)
        nb_manager_reponse = self.redis_client.publish('reponses-livreurs', message_candidature)
        print(f"   ✅ Candidature envoyée au manager")
        
        time.sleep(0.5)
        
        # 5. Attribution (simulation du manager)
        notification_livreur = {
            "type": "attribution",
            "id_commande": commande['id_commande'],
            "message": f"🎉 Course {commande['id_commande']} attribuée !"
        }
        
        print(f"\n✅ Attribution de la course au {id_livreur}...")
        canal_livreur = f"notifications-livreur:{id_livreur}"
        message_notif = json.dumps(notification_livreur, ensure_ascii=False)
        self.redis_client.publish(canal_livreur, message_notif)
        
        # 6. Confirmation au client
        confirmation = {
            "id_commande": commande['id_commande'],
            "id_livreur": id_livreur,
            "statut": "Livreur attribué",
            "message": f"Commande prise en charge par {id_livreur}"
        }
        
        canal_client = f"confirmation-client:{commande['id_client']}"
        message_confirm = json.dumps(confirmation, ensure_ascii=False)
        self.redis_client.publish(canal_client, message_confirm)
        print(f"   ✅ Confirmation envoyée au client")
        
        print(f"\n🎉 Commande {commande['id_commande']} traitée avec succès !")
    
    def generer_commande_aleatoire(self):
        """Génère une commande aléatoire"""
        noms = ["Alice", "Bob", "Charlie", "Diana", "Emma", "Frank", "Grace"]
        restaurants = [
            ("Burger King", "12 Rue de la Paix, Paris"),
            ("Pizza Hut", "25 Avenue Montaigne, Paris"),
            ("Sushi Shop", "8 Boulevard Saint-Germain, Paris"),
            ("KFC", "33 Rue du Faubourg Saint-Antoine, Paris"),
            ("McDonald's", "119 Avenue des Champs-Élysées, Paris")
        ]
        adresses = [
            "45 Avenue des Champs-Élysées, Paris",
            "12 Rue de Rivoli, Paris",
            "33 Boulevard Saint-Michel, Paris",
            "Aulnay-sous-Bois",
            "32 bis Avenue de Gargan"
        ]
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        id_commande = f"CMD-{timestamp}-{random.randint(1000, 9999)}"
        nom_client = random.choice(noms)
        id_client = f"client-{random.randint(1000, 9999)}"
        restaurant_nom, restaurant_adresse = random.choice(restaurants)
        montant = round(random.uniform(10, 50), 2)
        remuneration = round(montant * 0.15, 2)
        
        return {
            "id_commande": id_commande,
            "id_client": id_client,
            "nom_client": nom_client,
            "restaurant_nom": restaurant_nom,
            "restaurant_adresse": restaurant_adresse,
            "plats": [{"nom": "Plat", "prix": montant}],
            "montant_total": montant,
            "adresse_livraison": random.choice(adresses),
            "remuneration_livreur": remuneration,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    try:
        systeme = SystemeComplet()
        systeme.simulation_complete()
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation interrompue")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

"""
Client Automatique - Passe des commandes aléatoires
"""

import redis
import json
import random
import time
import os
from datetime import datetime

class ClientAutomatique:
    def __init__(self, id_client, nom_client, host='localhost', port=6379):
        """Initialise la connexion Redis pour un client automatique"""
        self.id_client = id_client
        self.nom_client = nom_client
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        
        # S'abonner au canal de confirmation de commande
        self.pubsub.subscribe(f'confirmation-client:{id_client}')
        
        print(f"👤 Client automatique {nom_client} ({id_client}) connecté")
        
    def charger_restaurants(self):
        """Charge les restaurants depuis le fichier JSON"""
        try:
            chemin_json = os.path.join(os.path.dirname(__file__), 'restaurants.json')
            with open(chemin_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict) and 'restaurants' in data:
                restaurants_data = data['restaurants']
            else:
                restaurants_data = data
            
            # Limiter à 50 restaurants
            restaurants_data = restaurants_data[:50]
            
            # Transformer les données
            restaurants = []
            for idx, resto in enumerate(restaurants_data, 1):
                if 'menu' not in resto or not resto.get('menu'):
                    resto['menu'] = [
                        {"name": "Plat principal", "price": round(random.uniform(8.0, 15.0), 2)},
                        {"name": "Entrée", "price": round(random.uniform(4.0, 8.0), 2)},
                        {"name": "Dessert", "price": round(random.uniform(3.0, 6.0), 2)},
                        {"name": "Boisson", "price": round(random.uniform(2.0, 4.0), 2)}
                    ]
                
                restaurant = {
                    "id": idx,
                    "name": resto.get('name', resto.get('restaurant_name', f'Restaurant {idx}')),
                    "address": resto.get('address', resto.get('address_line_1', 'Adresse non disponible')),
                    "lat": resto.get('lat', '0'),
                    "lng": resto.get('lng', '0'),
                    "menu": resto.get('menu', [])
                }
                restaurants.append(restaurant)
            
            return restaurants
        except:
            # Restaurants par défaut
            return [
                {
                    "id": 1,
                    "name": "Burger King",
                    "address": "12 Rue de la Paix, Paris",
                    "menu": [
                        {"name": "Whopper", "price": 6.50},
                        {"name": "Frites", "price": 2.50},
                    ]
                }
            ]
    
    def passer_commande_aleatoire(self):
        """Passe automatiquement une commande aléatoire"""
        restaurants = self.charger_restaurants()
        
        # Choisir un restaurant aléatoire
        restaurant = random.choice(restaurants)
        
        # Choisir entre 1 et 4 plats aléatoires
        nb_plats = random.randint(1, 4)
        plats_choisis = random.sample(restaurant['menu'], min(nb_plats, len(restaurant['menu'])))
        
        # Adresses de livraison possibles
        adresses = [
            "45 Avenue des Champs-Élysées, Paris",
            "12 Rue de Rivoli, Paris",
            "33 Boulevard Saint-Michel, Paris",
            "8 Place de la Concorde, Paris",
            "156 Boulevard Haussmann, Paris",
            "25 Rue du Faubourg Saint-Honoré, Paris",
            "88 Avenue de la République, Paris",
            "Aulnay-sous-Bois",
            "32 bis Avenue de Gargan",
            "15 Rue Victor Hugo, Bobigny"
        ]
        adresse_livraison = random.choice(adresses)
        
        # Afficher la commande
        print("\n" + "🛒"*30)
        print("📦 NOUVELLE COMMANDE AUTOMATIQUE")
        print("🛒"*30)
        print(f"👤 Client      : {self.nom_client}")
        print(f"🏪 Restaurant  : {restaurant['name']}")
        print(f"📍 Adresse     : {restaurant['address']}")
        print(f"🍽️  Plats      :")
        for plat in plats_choisis:
            print(f"   - {plat['name']} ({plat['price']}€)")
        print(f"📍 Livraison   : {adresse_livraison}")
        print("🛒"*30 + "\n")
        
        # Générer un ID unique pour la commande
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        id_commande = f"CMD-{timestamp}-{random.randint(1000, 9999)}"
        
        # Calculer le montant total
        montant_total = sum(plat['price'] for plat in plats_choisis)
        
        # Calculer la rémunération du livreur (15% du montant)
        remuneration_livreur = round(montant_total * 0.15, 2)
        
        # Créer la commande
        commande = {
            "id_commande": id_commande,
            "id_client": self.id_client,
            "nom_client": self.nom_client,
            "restaurant_nom": restaurant['name'],
            "restaurant_adresse": restaurant['address'],
            "plats": [{"nom": p['name'], "prix": p['price']} for p in plats_choisis],
            "montant_total": round(montant_total, 2),
            "adresse_livraison": adresse_livraison,
            "remuneration_livreur": remuneration_livreur,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publier la commande sur le canal 'nouvelles-commandes'
        message_json = json.dumps(commande, ensure_ascii=False)
        self.redis_client.publish('nouvelles-commandes', message_json)
        
        print(f"✅ Commande envoyée avec succès !")
        print(f"   ID Commande : {id_commande}")
        print(f"   Montant     : {montant_total:.2f}€")
        print(f"\n⏳ En attente de confirmation...\n")
        
        return id_commande
    
    def ecouter_confirmations(self, duree=30):
        """Écoute les confirmations pendant une durée limitée"""
        print(f"📡 Écoute des confirmations pendant {duree} secondes...\n")
        debut = time.time()
        
        for message in self.pubsub.listen():
            if time.time() - debut > duree:
                print(f"⏱️  Temps d'écoute écoulé ({duree}s)")
                break
                
            if message['type'] == 'message':
                confirmation = json.loads(message['data'])
                self._afficher_confirmation(confirmation)
                # Arrêter après avoir reçu la confirmation
                break
    
    def _afficher_confirmation(self, confirmation):
        """Affiche une confirmation de commande"""
        print("\n" + "🎉"*30)
        print("✅ COMMANDE CONFIRMÉE")
        print("🎉"*30)
        print(f"ID Commande : {confirmation['id_commande']}")
        print(f"Livreur     : {confirmation.get('id_livreur', 'En attente')}")
        print(f"Statut      : {confirmation['statut']}")
        print(f"Message     : {confirmation['message']}")
        print("🎉"*30 + "\n")

def generer_nom_client():
    """Génère un nom de client aléatoire"""
    prenoms = ["Alice", "Bob", "Charlie", "Diana", "Emma", "Frank", "Grace", "Henri", 
               "Isabelle", "Jacques", "Karim", "Léa", "Marc", "Nina", "Oscar", 
               "Pierre", "Quincy", "Rose", "Sophie", "Thomas"]
    return random.choice(prenoms)

if __name__ == "__main__":
    # Génération d'un client aléatoire
    nom_client = generer_nom_client()
    id_client = f"client-{random.randint(1000, 9999)}"
    
    client = ClientAutomatique(id_client, nom_client)
    
    try:
        # Passer une commande automatiquement
        client.passer_commande_aleatoire()
        
        # Écouter la confirmation (30 secondes max)
        client.ecouter_confirmations(duree=30)
        
        print(f"👋 Client {nom_client} terminé")
        
    except KeyboardInterrupt:
        print(f"\n👋 Client {nom_client} interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

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
        self.pubsub.subscribe(f'confirmation-client:{id_client}')
        print(f"👤 Client automatique {nom_client} ({id_client}) connecté")

    def charger_restaurants(self):
        """Charge les restaurants depuis data/restaurants.json"""
        try:
            chemin_json = os.path.join(os.path.dirname(__file__), '..', 'data', 'restaurants.json')
            with open(chemin_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'restaurants' in data:
                restaurants_data = data['restaurants']
            else:
                restaurants_data = data
            restaurants_data = restaurants_data[:50]
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
            return [{
                "id": 1,
                "name": "Burger King",
                "address": "12 Rue de la Paix, Paris",
                "menu": [{"name": "Whopper", "price": 6.50}, {"name": "Frites", "price": 2.50}]
            }]

    def passer_commande_aleatoire(self):
        restaurants = self.charger_restaurants()
        restaurant = random.choice(restaurants)
        nb_plats = random.randint(1, 4)
        plats_choisis = random.sample(restaurant['menu'], min(nb_plats, len(restaurant['menu'])))
        adresses = [
            "45 Avenue des Champs-Élysées, Paris",
            "12 Rue de Rivoli, Paris",
            "33 Boulevard Saint-Michel, Paris",
            "8 Place de la Concorde, Paris",
            "156 Boulevard Haussmann, Paris",
            "25 Rue du Faubourg Saint-Honoré, Paris",
            "88 Avenue de la République, 93100 Montreuil",
            "32 bis Avenue de Gargan",
            "15 Rue Victor Hugo, Bobigny"
        ]
        adresse_livraison = random.choice(adresses)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        id_commande = f"CMD-{timestamp}-{random.randint(1000, 9999)}"
        montant_total = sum(plat['price'] for plat in plats_choisis)
        remuneration_livreur = round(montant_total * 0.15, 2)
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
        message_json = json.dumps(commande, ensure_ascii=False)
        self.redis_client.publish('nouvelles-commandes', message_json)
        return id_commande

    def ecouter_confirmations(self, duree=30):
        debut = time.time()
        for message in self.pubsub.listen():
            if time.time() - debut > duree:
                break
            if message['type'] == 'message':
                confirmation = json.loads(message['data'])
                # display
                print("\n✅ COMMANDE CONFIRMÉE", confirmation)
                break

def generer_nom_client():
    prenoms = ["Alice", "Bob", "Charlie", "Diana", "Emma", "Frank", "Grace", "Henri", "Isabelle", "Jacques"]
    return random.choice(prenoms)

if __name__ == "__main__":
    nom_client = generer_nom_client()
    id_client = f"client-{random.randint(1000, 9999)}"
    client = ClientAutomatique(id_client, nom_client)
    try:
        client.passer_commande_aleatoire()
        client.ecouter_confirmations(duree=30)
    except KeyboardInterrupt:
        pass

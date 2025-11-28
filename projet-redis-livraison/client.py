import redis
import json
import random
import os
from datetime import datetime

class Client:
    def __init__(self, id_client, nom_client, host='localhost', port=6379):
        """
        Initialise la connexion Redis pour un client
        
        Args:
            id_client (str): Identifiant unique du client
            nom_client (str): Nom du client
        """
        self.id_client = id_client
        self.nom_client = nom_client
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        
        # S'abonner au canal de confirmation de commande
        self.pubsub.subscribe(f'confirmation-client:{id_client}')
        
        print(f"👤 Client {nom_client} ({id_client}) connecté")
        
    def afficher_menu(self, restaurant):
        """Affiche le menu d'un restaurant"""
        print("\n" + "="*60)
        print(f"📋 MENU - {restaurant['name']}")
        print("="*60)
        print(f"📍 Adresse: {restaurant['address']}")
        print("\n🍽️  Plats disponibles :")
        
        for idx, plat in enumerate(restaurant['menu'], 1):
            print(f"  {idx}. {plat['name']} - {plat['price']}€")
        
        print("="*60)
        
    def passer_commande(self, restaurant, plats_choisis, adresse_livraison):
        """
        Envoie une commande au manager via Redis
        
        Args:
            restaurant (dict): Informations du restaurant
            plats_choisis (list): Liste des plats commandés
            adresse_livraison (str): Adresse de livraison du client
        """
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
            "montant_total": montant_total,
            "adresse_livraison": adresse_livraison,
            "remuneration_livreur": remuneration_livreur,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publier la commande sur le canal 'nouvelles-commandes'
        message_json = json.dumps(commande, ensure_ascii=False)
        self.redis_client.publish('nouvelles-commandes', message_json)
        
        print("\n✅ Commande envoyée avec succès !")
        print(f"   ID Commande : {id_commande}")
        print(f"   Montant     : {montant_total}€")
        print(f"   Livraison à : {adresse_livraison}")
        print(f"\n⏳ En attente de confirmation...\n")
        
        return id_commande
        
    def ecouter_confirmations(self):
        """Écoute les confirmations de commande du manager"""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                confirmation = json.loads(message['data'])
                self._afficher_confirmation(confirmation)
                
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

def charger_restaurants_json():
    """Charge les restaurants depuis le fichier JSON"""
    import os
    try:
        chemin_json = os.path.join(os.path.dirname(__file__), 'restaurants.json')
        with open(chemin_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Si le JSON a une clé "restaurants"
        if isinstance(data, dict) and 'restaurants' in data:
            restaurants_data = data['restaurants']
        else:
            restaurants_data = data
        
        # Limiter à 20 restaurants pour l'affichage
        restaurants_data = restaurants_data[:20]
        
        # Transformer les données pour avoir un menu par défaut si absent
        restaurants = []
        for idx, resto in enumerate(restaurants_data, 1):
            # Créer un menu par défaut basé sur des prix aléatoires
            if 'menu' not in resto or not resto.get('menu'):
                resto['menu'] = [
                    {"name": "Plat principal", "price": round(random.uniform(8.0, 15.0), 2)},
                    {"name": "Entrée", "price": round(random.uniform(4.0, 8.0), 2)},
                    {"name": "Dessert", "price": round(random.uniform(3.0, 6.0), 2)},
                    {"name": "Boisson", "price": round(random.uniform(2.0, 4.0), 2)}
                ]
            
            # Normaliser les clés (name, address, etc.)
            restaurant = {
                "id": idx,
                "name": resto.get('name', resto.get('restaurant_name', f'Restaurant {idx}')),
                "address": resto.get('address', resto.get('address_line_1', 'Adresse non disponible')),
                "lat": resto.get('lat', '0'),
                "lng": resto.get('lng', '0'),
                "menu": resto.get('menu', [])
            }
            restaurants.append(restaurant)
        
        print(f"✅ {len(restaurants)} restaurants chargés depuis restaurants.json")
        return restaurants
        
    except FileNotFoundError:
        print("⚠️ Fichier restaurants.json introuvable, utilisation de restaurants par défaut")
        return obtenir_restaurants_par_defaut()
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return obtenir_restaurants_par_defaut()

def obtenir_restaurants_par_defaut():
    """Retourne des restaurants par défaut en cas d'erreur"""
    return [
        {
            "id": 1,
            "name": "Burger King",
            "address": "12 Rue de la Paix, Paris",
            "lat": "48.8698",
            "lng": "2.3318",
            "menu": [
                {"name": "Whopper", "price": 6.50},
                {"name": "Chicken Royal", "price": 5.90},
                {"name": "Frites", "price": 2.50},
                {"name": "Coca-Cola", "price": 2.00}
            ]
        },
        {
            "id": 2,
            "name": "Pizza Hut",
            "address": "25 Avenue Montaigne, Paris",
            "lat": "48.8656",
            "lng": "2.3054",
            "menu": [
                {"name": "Pizza Margherita", "price": 9.90},
                {"name": "Pizza 4 Fromages", "price": 11.50},
                {"name": "Pizza Pepperoni", "price": 10.90},
                {"name": "Salade César", "price": 5.50}
            ]
        },
        {
            "id": 3,
            "name": "Sushi Shop",
            "address": "8 Boulevard Saint-Germain, Paris",
            "lat": "48.8530",
            "lng": "2.3499",
            "menu": [
                {"name": "California Roll (8 pièces)", "price": 7.50},
                {"name": "Sashimi Saumon (6 pièces)", "price": 9.90},
                {"name": "Maki Avocat (6 pièces)", "price": 4.50},
                {"name": "Soupe Miso", "price": 3.00}
            ]
        }
    ]

def mode_interactif():
    """Mode interactif pour passer une commande"""
    
    # Charger les restaurants depuis le fichier JSON
    restaurants = charger_restaurants_json()
    
    # Création du client
    print("\n👤 Bienvenue sur la plateforme de livraison de repas !")
    nom_client = input("Entrez votre nom : ").strip()
    id_client = f"client-{random.randint(1000, 9999)}"
    
    client = Client(id_client, nom_client)
    
    # Affichage des restaurants disponibles
    print("\n" + "="*60)
    print("🍽️  RESTAURANTS DISPONIBLES")
    print("="*60)
    for idx, resto in enumerate(restaurants, 1):
        print(f"{idx}. {resto['name']} - {resto['address']}")
    print("="*60)
    
    # Choix du restaurant
    choix_resto = int(input("\nChoisissez un restaurant (numéro) : ")) - 1
    restaurant_choisi = restaurants[choix_resto]
    
    # Affichage du menu
    client.afficher_menu(restaurant_choisi)
    
    # Choix des plats
    plats_choisis = []
    while True:
        choix = input("\nChoisissez un plat (numéro) ou 'f' pour finaliser : ").strip().lower()
        
        if choix == 'f':
            if plats_choisis:
                break
            else:
                print("⚠️ Vous devez choisir au moins un plat !")
                continue
        
        try:
            idx_plat = int(choix) - 1
            plat = restaurant_choisi['menu'][idx_plat]
            plats_choisis.append(plat)
            print(f"✅ {plat['name']} ajouté au panier ({plat['price']}€)")
        except (ValueError, IndexError):
            print("❌ Choix invalide !")
    
    # Adresse de livraison
    adresse_livraison = input("\n📍 Entrez votre adresse de livraison : ").strip()
    
    # Passer la commande
    client.passer_commande(restaurant_choisi, plats_choisis, adresse_livraison)
    
    # Écouter les confirmations (bloquant)
    try:
        print("📡 En attente de confirmation du manager...")
        client.ecouter_confirmations()
    except KeyboardInterrupt:
        print(f"\n👋 {nom_client} déconnecté")

if __name__ == "__main__":
    mode_interactif()

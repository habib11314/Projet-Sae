import json
import os

def charger_restaurants(fichier_json="restaurants.json"):
    """
    Charge la liste des restaurants depuis un fichier JSON
    
    Args:
        fichier_json (str): Chemin vers le fichier JSON des restaurants
        
    Returns:
        list: Liste des restaurants avec leurs menus
    """
    # Chercher le fichier dans plusieurs emplacements possibles
    chemins_possibles = [
        fichier_json,
        f"C:/Users/PC/Downloads/{fichier_json}",
        f"C:/Users/PC/projet-redis-livraison/{fichier_json}",
        os.path.join(os.path.dirname(__file__), fichier_json)
    ]
    
    for chemin in chemins_possibles:
        if os.path.exists(chemin):
            try:
                with open(chemin, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Si le JSON a une clé "restaurants"
                if isinstance(data, dict) and 'restaurants' in data:
                    restaurants = data['restaurants']
                else:
                    restaurants = data
                
                print(f"✅ {len(restaurants)} restaurants chargés depuis {chemin}")
                return restaurants
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {chemin}: {e}")
    
    # Si aucun fichier trouvé, retourner des restaurants par défaut
    print("⚠️ Fichier restaurants.json introuvable, utilisation de restaurants par défaut")
    return obtenir_restaurants_par_defaut()

def obtenir_restaurants_par_defaut():
    """Retourne une liste de restaurants par défaut pour les tests"""
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
        },
        {
            "id": 4,
            "name": "KFC",
            "address": "33 Rue du Faubourg Saint-Antoine, Paris",
            "lat": "48.8520",
            "lng": "2.3716",
            "menu": [
                {"name": "Bucket 10 pièces", "price": 15.90},
                {"name": "Twister", "price": 6.50},
                {"name": "Wings (6 pièces)", "price": 5.90},
                {"name": "Coleslaw", "price": 2.90}
            ]
        },
        {
            "id": 5,
            "name": "McDonald's",
            "address": "119 Avenue des Champs-Élysées, Paris",
            "lat": "48.8719",
            "lng": "2.3019",
            "menu": [
                {"name": "Big Mac", "price": 5.50},
                {"name": "McChicken", "price": 4.90},
                {"name": "Frites Moyennes", "price": 2.50},
                {"name": "McFlurry", "price": 3.50}
            ]
        }
    ]

def generer_menu_aleatoire():
    """Génère un menu aléatoire pour les restaurants qui n'en ont pas"""
    plats_possibles = [
        {"name": "Plat du jour", "price": 12.50},
        {"name": "Salade composée", "price": 8.90},
        {"name": "Sandwich", "price": 5.50},
        {"name": "Dessert", "price": 4.00},
        {"name": "Boisson", "price": 2.50}
    ]
    return plats_possibles

if __name__ == "__main__":
    # Test du chargement
    restaurants = charger_restaurants()
    print(f"\nPremier restaurant: {restaurants[0]['name']}")
    print(f"Adresse: {restaurants[0]['address']}")
    if 'menu' in restaurants[0]:
        print(f"Nombre de plats au menu: {len(restaurants[0]['menu'])}")

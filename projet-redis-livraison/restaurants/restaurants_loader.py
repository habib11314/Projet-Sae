import json
import os

def charger_restaurants(fichier_json="restaurants.json"):
    """
    Charge la liste des restaurants depuis un fichier JSON
    Recherche prioritaire dans ../data/ pour la nouvelle structure
    """
    # Chercher le fichier dans plusieurs emplacements possibles
    chemins_possibles = [
        # explicit data folder relative to this module
        os.path.join(os.path.dirname(__file__), '..', 'data', fichier_json),
        # same directory as this module (fallback)
        os.path.join(os.path.dirname(__file__), fichier_json),
        # legacy absolute locations
        f"C:/Users/PC/Downloads/{fichier_json}",
        f"C:/Users/PC/projet-redis-livraison/{fichier_json}",
        fichier_json
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

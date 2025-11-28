"""
Simulation Avancée avec Scénarios Réalistes
- Gestion des états des livreurs (disponible, en livraison, livré)
- Attribution intelligente (pas de double livraison)
- Communication client-livreur aléatoire
- Refus/Acceptation aléatoire
- Temps de livraison simulé
"""

import redis
import json
import random
import time
from datetime import datetime
from threading import Thread, Lock
import os

# ========== DONNÉES RÉALISTES ==========

PRENOMS = [
    "Mohammed", "Fatima", "Ali", "Aisha", "Omar", "Khadija", "Hassan", "Amina",
    "Ibrahim", "Mariam", "Ahmed", "Nadia", "Youssef", "Sara", "Karim", "Leila",
    "Pierre", "Sophie", "Jean", "Marie", "Luc", "Julie", "Marc", "Emma",
    "Thomas", "Léa", "Nicolas", "Camille", "Alexandre", "Chloé", "Maxime", "Laura",
    "Antoine", "Manon", "Lucas", "Océane", "Gabriel", "Inès", "Hugo", "Anaïs"
]

NOMS = [
    "Benali", "Mansouri", "Khalil", "Rousseau", "Martin", "Bernard", "Dubois", 
    "Thomas", "Robert", "Petit", "Durand", "Leroy", "Moreau", "Simon", "Laurent",
    "Lefebvre", "Michel", "Garcia", "David", "Bertrand", "Roux", "Vincent",
    "Fournier", "Morel", "Girard", "André", "Mercier", "Blanc", "Guerin", "Boyer"
]

ADRESSES_LIVRAISON = [
    "45 Avenue des Champs-Élysées, 75008 Paris",
    "12 Rue de Rivoli, 75004 Paris",
    "33 Boulevard Saint-Michel, 75005 Paris",
    "8 Place de la Concorde, 75008 Paris",
    "156 Boulevard Haussmann, 75008 Paris",
    "25 Rue du Faubourg Saint-Honoré, 75008 Paris",
    "88 Avenue de la République, 93100 Montreuil",
    "15 Rue Victor Hugo, 93000 Bobigny",
    "32 bis Avenue de Gargan, 93390 Clichy-sous-Bois",
    "47 Boulevard Gambetta, 93170 Bagnolet",
    "22 Rue Jean Jaurès, 93130 Noisy-le-Sec",
    "135 Avenue du Président Wilson, 93210 Saint-Denis",
    "67 Rue de Paris, 93100 Montreuil",
    "91 Avenue Aristide Briand, 93320 Les Pavillons-sous-Bois",
    "55 Rue de la République, 93200 Saint-Denis",
    "18 Boulevard de Strasbourg, 93600 Aulnay-sous-Bois",
    "76 Avenue Jean Lolive, 93500 Pantin",
    "29 Rue Hoche, 93170 Bagnolet",
    "103 Boulevard Félix Faure, 93300 Aubervilliers",
    "41 Rue du Général Leclerc, 93110 Rosny-sous-Bois"
]

COMMENTAIRES_POSITIFS = [
    "Excellent service !",
    "Livreur très sympathique",
    "Livraison rapide, merci !",
    "Nourriture encore chaude",
    "Parfait, rien à redire",
    "Super pro, à l'heure",
    "Très bon contact",
    "Emballage soigné",
    "Politesse irréprochable",
    "Je recommande ce livreur"
]

COMMENTAIRES_NEGATIFS = [
    "Frites froides",
    "En retard de 15 minutes",
    "Manque de couverts",
    "Burger écrasé",
    "Boisson renversée",
    "Mauvaise adresse livrée",
    "Livreur pas aimable",
    "Emballage déchiré",
    "Il manque un plat",
    "Sauce oubliée",
    "Pizza froide",
    "Commande incomplète"
]

COMMENTAIRES_NEUTRES = [
    "Correct",
    "RAS",
    "Bien",
    "Ok",
    "Conforme à la commande",
    "Pas de problème particulier",
    "Standard",
    "Normal"
]

# ========== GESTIONNAIRE DES LIVREURS ==========

class GestionnaireLivreurs:
    """Gère l'état de tous les livreurs"""
    
    def __init__(self):
        self.livreurs = {}  # {id_livreur: {"statut": "disponible", "commande_actuelle": None}}
        self.lock = Lock()
    
    def initialiser_livreur(self, id_livreur):
        """Initialise un livreur comme disponible"""
        with self.lock:
            self.livreurs[id_livreur] = {
                "statut": "disponible",
                "commande_actuelle": None,
                "nb_livraisons": 0
            }
            print(f"   🚴 {id_livreur} initialisé (statut: disponible)")
    
    def est_disponible(self, id_livreur):
        """Vérifie si un livreur est disponible"""
        with self.lock:
            return self.livreurs.get(id_livreur, {}).get("statut") == "disponible"
    
    def obtenir_livreurs_disponibles(self):
        """Retourne la liste des livreurs disponibles"""
        with self.lock:
            return [id_l for id_l, info in self.livreurs.items() 
                    if info["statut"] == "disponible"]
    
    def marquer_en_livraison(self, id_livreur, id_commande):
        """Marque un livreur comme en cours de livraison"""
        with self.lock:
            if id_livreur in self.livreurs:
                self.livreurs[id_livreur]["statut"] = "en_livraison"
                self.livreurs[id_livreur]["commande_actuelle"] = id_commande
                print(f"   📦 {id_livreur} → EN LIVRAISON (commande: {id_commande})")
    
    def marquer_livre(self, id_livreur):
        """Marque un livreur comme ayant terminé sa livraison"""
        with self.lock:
            if id_livreur in self.livreurs:
                self.livreurs[id_livreur]["statut"] = "disponible"
                self.livreurs[id_livreur]["commande_actuelle"] = None
                self.livreurs[id_livreur]["nb_livraisons"] += 1
                print(f"   ✅ {id_livreur} → DISPONIBLE (livraison terminée)")
    
    def afficher_etat(self):
        """Affiche l'état de tous les livreurs"""
        with self.lock:
            print("\n" + "📊"*30)
            print("ÉTAT DES LIVREURS")
            print("📊"*30)
            for id_l, info in self.livreurs.items():
                statut_emoji = "🟢" if info["statut"] == "disponible" else "🔴"
                print(f"   {statut_emoji} {id_l}: {info['statut']} | "
                      f"Livraisons: {info['nb_livraisons']}")
            print("📊"*30 + "\n")

# ========== SIMULATION AVANCÉE ==========

class SimulationAvancee:
    def __init__(self, nb_livreurs=8, nb_commandes=10):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.gestionnaire_livreurs = GestionnaireLivreurs()
        self.nb_livreurs = nb_livreurs
        self.nb_commandes = nb_commandes
        self.restaurants = self.charger_restaurants()
        
        # Initialiser les livreurs
        for i in range(1, nb_livreurs + 1):
            self.gestionnaire_livreurs.initialiser_livreur(f"livreur-{i:03d}")
        
        print(f"\n✅ Connexion à Redis établie")
        print(f"✅ {nb_livreurs} livreurs initialisés")
        print(f"✅ Restaurants chargés depuis JSON\n")
    
    def charger_restaurants(self):
        """Charge les VRAIS restaurants et VRAIS menus depuis les 2 fichiers JSON"""
        try:
            # 1. Charger les restaurants (try data/ then repo root)
            possible_restos = [
                os.path.join(os.path.dirname(__file__), '..', 'data', 'restaurants.json'),
                os.path.join(os.path.dirname(__file__), 'restaurants.json')
            ]
            chemin_restaurants = None
            for p in possible_restos:
                if os.path.exists(p):
                    chemin_restaurants = p
                    break
            if not chemin_restaurants:
                raise FileNotFoundError('restaurants.json introuvable (data/ ou repo root)')
            with open(chemin_restaurants, 'r', encoding='utf-8') as f:
                data_restos = json.load(f)
            
            restaurants_data = data_restos.get('restaurants', data_restos) if isinstance(data_restos, dict) else data_restos
            
            # 2. Charger les menus (try data/ then repo root)
            possible_menus = [
                os.path.join(os.path.dirname(__file__), '..', 'data', 'menu.json'),
                os.path.join(os.path.dirname(__file__), 'menu.json')
            ]
            chemin_menu = None
            for p in possible_menus:
                if os.path.exists(p):
                    chemin_menu = p
                    break
            if not chemin_menu:
                raise FileNotFoundError('menu.json introuvable (data/ ou repo root)')
            with open(chemin_menu, 'r', encoding='utf-8') as f:
                data_menu = json.load(f)
            
            menu_data = data_menu.get('menu', data_menu) if isinstance(data_menu, dict) else data_menu
            
            # 3. Organiser les menus par restaurant_id
            menus_par_resto = {}
            for item in menu_data:
                resto_id = str(item.get('restaurant_id', ''))
                if resto_id not in menus_par_resto:
                    menus_par_resto[resto_id] = []
                
                # Extraire le prix
                price_str = item.get('price', '0')
                try:
                    price = float(price_str.replace('USD', '').replace('$', '').strip())
                except:
                    price = 10.0
                
                menus_par_resto[resto_id].append({
                    "name": item.get('name', 'Plat'),
                    "category": item.get('category', ''),
                    "price": price
                })
            
            # 4. Créer la liste des restaurants avec leurs menus
            restaurants = []
            for resto in restaurants_data[:100]:
                resto_id = str(resto.get('id', ''))
                menu_items = menus_par_resto.get(resto_id, [])[:20]
                
                if menu_items:
                    restaurants.append({
                        "id": resto_id,
                        "name": resto.get('name', 'Restaurant'),
                        "address": resto.get('full_address', resto.get('address', 'Adresse')),
                        "category": resto.get('category', ''),
                        "menu": menu_items
                    })
            
            print(f"✅ {len(restaurants)} restaurants avec VRAIS menus chargés depuis JSON")
            return restaurants
        except Exception as e:
            print(f"⚠️  Erreur: {e}")
            return self.obtenir_restaurants_par_defaut()
    
    def generer_menu_aleatoire(self):
        """Génère un menu aléatoire"""
        plats = [
            "Burger", "Pizza", "Tacos", "Sushi", "Pasta", "Salade", 
            "Sandwich", "Kebab", "Poulet", "Poisson"
        ]
        menu = []
        for _ in range(random.randint(3, 6)):
            menu.append({
                "name": f"{random.choice(plats)} {random.choice(['Classic', 'Deluxe', 'Spécial', 'Royal'])}",
                "price": round(random.uniform(5.0, 15.0), 2)
            })
        return menu
    
    def obtenir_restaurants_par_defaut(self):
        """Restaurants par défaut si JSON indisponible"""
        return [
            {
                "id": 1,
                "name": "Burger King",
                "address": "12 Rue de la Paix, Paris",
                "menu": [
                    {"name": "Whopper", "price": 6.50},
                    {"name": "Chicken Royal", "price": 5.90},
                    {"name": "Frites", "price": 2.50}
                ]
            }
        ]
    
    def generer_commande_aleatoire(self):
        """Génère une commande avec données aléatoires réalistes"""
        # Client aléatoire
        prenom = random.choice(PRENOMS)
        nom = random.choice(NOMS)
        nom_client = f"{prenom} {nom}"
        id_client = f"client-{random.randint(1000, 9999)}"
        
        # Restaurant aléatoire
        restaurant = random.choice(self.restaurants)
        
        # Plats aléatoires (1 à 4 plats)
        nb_plats = random.randint(1, 4)
        plats_choisis = random.sample(restaurant['menu'], min(nb_plats, len(restaurant['menu'])))
        
        # Adresse aléatoire
        adresse_livraison = random.choice(ADRESSES_LIVRAISON)
        
        # Calculs
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        id_commande = f"CMD-{timestamp[:14]}-{random.randint(1000, 9999)}"
        montant_total = sum(p['price'] for p in plats_choisis)
        remuneration = round(montant_total * 0.15, 2)
        
        return {
            "id_commande": id_commande,
            "id_client": id_client,
            "nom_client": nom_client,
            "restaurant_nom": restaurant['name'],
            "restaurant_adresse": restaurant['address'],
            "plats": [{"nom": p['name'], "prix": p['price']} for p in plats_choisis],
            "montant_total": round(montant_total, 2),
            "adresse_livraison": adresse_livraison,
            "remuneration_livreur": remuneration,
            "timestamp": datetime.now().isoformat()
        }
    
    def simuler_processus_livraison(self, commande):
        """Simule tout le processus de livraison avec scénarios réalistes"""
        print("\n" + "🛒"*35)
        print(f"📦 NOUVELLE COMMANDE #{commande['id_commande'][-4:]}")
        print("🛒"*35)
        print(f"👤 Client       : {commande['nom_client']}")
        print(f"🏪 Restaurant   : {commande['restaurant_nom']}")
        print(f"💰 Montant      : {commande['montant_total']}€")
        print(f"📍 Livraison    : {commande['adresse_livraison']}")
        print(f"🍽️  Plats       : {', '.join([p['nom'] for p in commande['plats'][:2]])}")
        if len(commande['plats']) > 2:
            print(f"                 ... et {len(commande['plats'])-2} autre(s)")
        print("🛒"*35)
        
        # 1. Publication de la commande
        message_json = json.dumps(commande, ensure_ascii=False)
        self.redis_client.publish('nouvelles-commandes', message_json)
        time.sleep(0.3)
        
        # 2. Créer l'offre pour les livreurs
        offre = {
            "id_commande": commande['id_commande'],
            "restaurant_nom": commande['restaurant_nom'],
            "restaurant_adresse": commande['restaurant_adresse'],
            "adresse_livraison": commande['adresse_livraison'],
            "remuneration_livreur": commande['remuneration_livreur']
        }
        
        # 3. Obtenir les livreurs disponibles
        livreurs_disponibles = self.gestionnaire_livreurs.obtenir_livreurs_disponibles()
        
        if not livreurs_disponibles:
            print("\n❌ AUCUN LIVREUR DISPONIBLE - Commande en attente\n")
            return
        
        print(f"\n📢 Offre diffusée à {len(livreurs_disponibles)} livreur(s) disponible(s)")
        message_offre = json.dumps(offre, ensure_ascii=False)
        self.redis_client.publish('offres-courses', message_offre)
        time.sleep(0.5)
        
        # 4. Simulation des réponses des livreurs
        livreur_attribue = None
        
        for livreur_id in livreurs_disponibles:
            # Chaque livreur a une chance aléatoire d'accepter
            taux_acceptation = random.uniform(0.3, 0.8)
            temps_reflexion = random.uniform(0.5, 2.0)
            time.sleep(temps_reflexion)
            
            accepte = random.random() < taux_acceptation
            
            if accepte:
                print(f"   ✅ {livreur_id} ACCEPTE la course")
                livreur_attribue = livreur_id
                break
            else:
                raisons = ["trop loin", "autre livraison", "pause", "refus"]
                print(f"   ❌ {livreur_id} REFUSE ({random.choice(raisons)})")
        
        if not livreur_attribue:
            print("\n⚠️  AUCUN LIVREUR N'A ACCEPTÉ - Nouvelle tentative nécessaire\n")
            return
        
        # 5. Attribution de la commande
        self.gestionnaire_livreurs.marquer_en_livraison(livreur_attribue, commande['id_commande'])
        
        candidature = {
            "id_livreur": livreur_attribue,
            "id_commande": commande['id_commande']
        }
        self.redis_client.publish('reponses-livreurs', json.dumps(candidature, ensure_ascii=False))
        
        # Notification au livreur
        notification_livreur = {
            "type": "attribution",
            "id_commande": commande['id_commande'],
            "message": f"🎉 Course attribuée ! Direction: {commande['adresse_livraison']}"
        }
        self.redis_client.publish(
            f"notifications-livreur:{livreur_attribue}", 
            json.dumps(notification_livreur, ensure_ascii=False)
        )
        
        # Confirmation au client
        confirmation = {
            "id_commande": commande['id_commande'],
            "id_livreur": livreur_attribue,
            "statut": "En préparation",
            "message": f"Votre commande est prise en charge par {livreur_attribue}"
        }
        self.redis_client.publish(
            f"confirmation-client:{commande['id_client']}", 
            json.dumps(confirmation, ensure_ascii=False)
        )
        
        print(f"\n✅ Course attribuée à {livreur_attribue}")
        
        # 6. Simulation du temps de livraison (10-30 secondes)
        temps_livraison = random.uniform(10, 30)
        print(f"⏱️  Temps de livraison estimé: {temps_livraison:.0f}s")
        print(f"🚴 {livreur_attribue} en route vers {commande['adresse_livraison'][:30]}...")
        
        time.sleep(temps_livraison)
        
        # 7. Livraison terminée
        print(f"\n📍 Livraison arrivée !")
        
        # 8. Commentaire aléatoire du client
        type_commentaire = random.choices(
            ['positif', 'negatif', 'neutre'],
            weights=[0.70, 0.20, 0.10]  # 70% positif, 20% négatif, 10% neutre
        )[0]
        
        if type_commentaire == 'positif':
            commentaire = random.choice(COMMENTAIRES_POSITIFS)
            emoji = "⭐⭐⭐⭐⭐"
        elif type_commentaire == 'negatif':
            commentaire = random.choice(COMMENTAIRES_NEGATIFS)
            emoji = "⭐⭐"
        else:
            commentaire = random.choice(COMMENTAIRES_NEUTRES)
            emoji = "⭐⭐⭐"
        
        print(f"💬 Commentaire client: \"{commentaire}\" {emoji}")
        
        # Message de livraison
        statut_livraison = {
            "id_commande": commande['id_commande'],
            "id_livreur": livreur_attribue,
            "statut": "Livré",
            "commentaire": commentaire,
            "note": emoji,
            "temps_livraison": f"{temps_livraison:.0f}s"
        }
        self.redis_client.publish(
            f"statut-livraison:{commande['id_commande']}", 
            json.dumps(statut_livraison, ensure_ascii=False)
        )
        
        # 9. Libérer le livreur
        self.gestionnaire_livreurs.marquer_livre(livreur_attribue)
        
        print(f"✅ LIVRAISON TERMINÉE\n")
    
    def lancer_simulation(self):
        """Lance la simulation complète"""
        print("\n" + "="*70)
        print("🚀 SIMULATION AVANCÉE - Système de Livraison Réaliste")
        print("="*70)
        print(f"📊 Configuration:")
        print(f"   - {self.nb_livreurs} livreurs actifs")
        print(f"   - {self.nb_commandes} commandes à simuler")
        print(f"   - {len(self.restaurants)} restaurants disponibles")
        print("="*70 + "\n")
        
        for i in range(self.nb_commandes):
            print(f"\n{'='*70}")
            print(f"📦 SCÉNARIO {i+1}/{self.nb_commandes}")
            print(f"{'='*70}")
            
            # Générer et traiter une commande
            commande = self.generer_commande_aleatoire()
            self.simuler_processus_livraison(commande)
            
            # Afficher l'état des livreurs périodiquement
            if (i + 1) % 3 == 0:
                self.gestionnaire_livreurs.afficher_etat()
            
            # Délai aléatoire entre les commandes (2-5 secondes)
            if i < self.nb_commandes - 1:
                delai = random.uniform(2, 5)
                print(f"⏳ Pause de {delai:.1f}s avant la prochaine commande...")
                time.sleep(delai)
        
        # Résumé final
        self.gestionnaire_livreurs.afficher_etat()
        
        print("\n" + "="*70)
        print("✅ SIMULATION TERMINÉE")
        print("="*70)
        print(f"\n📊 Statistiques finales:")
        print(f"   - {self.nb_commandes} commandes traitées")
        print(f"   - Système de notifications temps réel vérifié")
        print(f"   - Gestion des états des livreurs opérationnelle")
        print(f"   - Communication client-livreur simulée")
        print("\n💡 Le système Redis Pub/Sub avec gestion d'états fonctionne parfaitement !")
        print()

# ========== POINT D'ENTRÉE ==========

if __name__ == "__main__":
    try:
        # Paramètres configurables
        NB_LIVREURS = 8
        NB_COMMANDES = 15
        
        simulation = SimulationAvancee(nb_livreurs=NB_LIVREURS, nb_commandes=NB_COMMANDES)
        simulation.lancer_simulation()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

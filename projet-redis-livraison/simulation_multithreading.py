"""
Simulation Multi-threading Avancée
- Plusieurs clients passent commande simultanément
- Gestion concurrente des livraisons
- Scénarios ultra-réalistes en parallèle
"""

import redis
import json
import random
import time
from datetime import datetime
from threading import Thread, Lock
import os

# ========== DONNÉES RÉALISTES (importées de simulation_realiste) ==========

PRENOMS = [
    "Mohammed", "Fatima", "Ali", "Aisha", "Omar", "Khadija", "Hassan", "Amina",
    "Ibrahim", "Mariam", "Ahmed", "Nadia", "Youssef", "Sara", "Karim", "Leila",
    "Pierre", "Sophie", "Jean", "Marie", "Luc", "Julie", "Marc", "Emma",
    "Thomas", "Léa", "Nicolas", "Camille", "Alexandre", "Chloé", "Maxime", "Laura"
]

NOMS = [
    "Benali", "Mansouri", "Khalil", "Rousseau", "Martin", "Bernard", "Dubois", 
    "Thomas", "Robert", "Petit", "Durand", "Leroy", "Moreau", "Simon"
]

ADRESSES_LIVRAISON = [
    "45 Avenue des Champs-Élysées, 75008 Paris",
    "12 Rue de Rivoli, 75004 Paris",
    "33 Boulevard Saint-Michel, 75005 Paris",
    "88 Avenue de la République, 93100 Montreuil",
    "15 Rue Victor Hugo, 93000 Bobigny",
    "47 Boulevard Gambetta, 93170 Bagnolet",
    "22 Rue Jean Jaurès, 93130 Noisy-le-Sec",
    "135 Avenue du Président Wilson, 93210 Saint-Denis",
    "67 Rue de Paris, 93100 Montreuil",
    "55 Rue de la République, 93200 Saint-Denis"
]

COMMENTAIRES_POSITIFS = [
    "Excellent service !", "Livreur très sympathique", "Livraison rapide, merci !",
    "Nourriture encore chaude", "Parfait, rien à redire", "Super pro, à l'heure"
]

COMMENTAIRES_NEGATIFS = [
    "Frites froides", "En retard de 15 minutes", "Manque de couverts",
    "Burger écrasé", "Boisson renversée", "Il manque un plat", "Pizza froide"
]

COMMENTAIRES_NEUTRES = ["Correct", "RAS", "Bien", "Ok"]

# ========== GESTIONNAIRE THREAD-SAFE ==========

class GestionnaireLivreursThreadSafe:
    def __init__(self):
        self.livreurs = {}
        self.lock = Lock()
        self.stats = {
            "commandes_traitees": 0,
            "commandes_en_cours": 0,
            "commandes_echouees": 0
        }
    
    def initialiser_livreur(self, id_livreur):
        with self.lock:
            self.livreurs[id_livreur] = {
                "statut": "disponible",
                "commande_actuelle": None,
                "nb_livraisons": 0
            }
    
    def obtenir_livreur_disponible(self):
        """Retourne un livreur disponible (thread-safe)"""
        with self.lock:
            for id_l, info in self.livreurs.items():
                if info["statut"] == "disponible":
                    return id_l
            return None
    
    def marquer_en_livraison(self, id_livreur, id_commande):
        with self.lock:
            if id_livreur in self.livreurs:
                self.livreurs[id_livreur]["statut"] = "en_livraison"
                self.livreurs[id_livreur]["commande_actuelle"] = id_commande
                self.stats["commandes_en_cours"] += 1
    
    def marquer_livre(self, id_livreur):
        with self.lock:
            if id_livreur in self.livreurs:
                self.livreurs[id_livreur]["statut"] = "disponible"
                self.livreurs[id_livreur]["commande_actuelle"] = None
                self.livreurs[id_livreur]["nb_livraisons"] += 1
                self.stats["commandes_traitees"] += 1
                self.stats["commandes_en_cours"] -= 1
    
    def marquer_echec(self):
        with self.lock:
            self.stats["commandes_echouees"] += 1
    
    def obtenir_stats(self):
        with self.lock:
            nb_disponibles = sum(1 for info in self.livreurs.values() 
                                if info["statut"] == "disponible")
            nb_en_livraison = len(self.livreurs) - nb_disponibles
            return {
                **self.stats,
                "livreurs_disponibles": nb_disponibles,
                "livreurs_en_livraison": nb_en_livraison
            }

# ========== SIMULATION MULTI-THREADING ==========

class SimulationMultithreading:
    def __init__(self, nb_livreurs=10, nb_commandes=20):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.gestionnaire = GestionnaireLivreursThreadSafe()
        self.nb_livreurs = nb_livreurs
        self.nb_commandes = nb_commandes
        self.restaurants = self.charger_restaurants()
        self.lock_affichage = Lock()
        
        for i in range(1, nb_livreurs + 1):
            self.gestionnaire.initialiser_livreur(f"livreur-{i:03d}")
    
    def charger_restaurants(self):
        """Charge les VRAIS restaurants et VRAIS menus depuis les 2 fichiers JSON"""
        try:
            # 1. Charger restaurants.json (try data/ then fallback to repo root)
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
            
            # 2. Charger menu.json (try data/ then fallback to repo root)
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
            
            # 3. Organiser par restaurant_id
            menus_par_resto = {}
            for item in menu_data:
                resto_id = str(item.get('restaurant_id', ''))
                if resto_id not in menus_par_resto:
                    menus_par_resto[resto_id] = []
                try:
                    price = float(item.get('price', '0').replace('USD', '').replace('$', '').strip())
                except:
                    price = 10.0
                menus_par_resto[resto_id].append({
                    "name": item.get('name', 'Plat'),
                    "price": price
                })
            
            # 4. Construire la liste
            restaurants = []
            for resto in restaurants_data[:80]:
                resto_id = str(resto.get('id', ''))
                menu_items = menus_par_resto.get(resto_id, [])[:15]
                if menu_items:
                    restaurants.append({
                        "id": resto_id,
                        "name": resto.get('name', 'Restaurant'),
                        "address": resto.get('full_address', 'Adresse'),
                        "menu": menu_items
                    })
            
            print(f"✅ {len(restaurants)} restaurants avec menus réels chargés")
            return restaurants
        except Exception as e:
            print(f"⚠️  Erreur: {e}")
            return [{"id": 1, "name": "Restaurant Test", "address": "Paris", 
                    "menu": [{"name": "Plat", "price": 10.0}]}]
    
    def generer_commande(self):
        prenom = random.choice(PRENOMS)
        nom = random.choice(NOMS)
        restaurant = random.choice(self.restaurants)
        plats = random.sample(restaurant['menu'], min(random.randint(1, 3), len(restaurant['menu'])))
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return {
            "id_commande": f"CMD-{timestamp[:14]}-{random.randint(1000, 9999)}",
            "id_client": f"client-{random.randint(1000, 9999)}",
            "nom_client": f"{prenom} {nom}",
            "restaurant_nom": restaurant['name'],
            "restaurant_adresse": restaurant['address'],
            "plats": [{"nom": p['name'], "prix": p['price']} for p in plats],
            "montant_total": round(sum(p['price'] for p in plats), 2),
            "adresse_livraison": random.choice(ADRESSES_LIVRAISON),
            "timestamp": datetime.now().isoformat()
        }
    
    def print_safe(self, message):
        """Affichage thread-safe"""
        with self.lock_affichage:
            print(message)
    
    def traiter_commande_thread(self, numero_commande):
        """Traite une commande dans un thread séparé"""
        commande = self.generer_commande()
        
        self.print_safe(f"\n{'='*60}")
        self.print_safe(f"📦 COMMANDE #{numero_commande} - {commande['id_commande'][-8:]}")
        self.print_safe(f"👤 {commande['nom_client']} | 🏪 {commande['restaurant_nom']}")
        self.print_safe(f"💰 {commande['montant_total']}€ | 📍 {commande['adresse_livraison'][:40]}")
        self.print_safe(f"{'='*60}")
        
        # Tentative d'attribution avec timeout
        max_tentatives = 5
        tentative = 0
        livreur_attribue = None
        
        while tentative < max_tentatives and not livreur_attribue:
            livreur_attribue = self.gestionnaire.obtenir_livreur_disponible()
            
            if livreur_attribue:
                # Simulation acceptation aléatoire
                if random.random() > 0.25:  # 75% d'acceptation
                    self.print_safe(f"   ✅ {livreur_attribue} ACCEPTE")
                    self.gestionnaire.marquer_en_livraison(livreur_attribue, commande['id_commande'])
                    break
                else:
                    self.print_safe(f"   ❌ {livreur_attribue} REFUSE")
                    livreur_attribue = None
            
            tentative += 1
            time.sleep(random.uniform(0.5, 1.5))
        
        if not livreur_attribue:
            self.print_safe(f"   ⚠️  ÉCHEC: Aucun livreur disponible après {max_tentatives} tentatives")
            self.gestionnaire.marquer_echec()
            return
        
        # Simulation livraison
        temps_livraison = random.uniform(8, 20)
        self.print_safe(f"   🚴 {livreur_attribue} en route (⏱️ {temps_livraison:.0f}s)")
        time.sleep(temps_livraison)
        
        # Commentaire aléatoire
        type_com = random.choices(['positif', 'negatif', 'neutre'], weights=[0.7, 0.2, 0.1])[0]
        if type_com == 'positif':
            commentaire = random.choice(COMMENTAIRES_POSITIFS)
            emoji = "⭐⭐⭐⭐⭐"
        elif type_com == 'negatif':
            commentaire = random.choice(COMMENTAIRES_NEGATIFS)
            emoji = "⭐⭐"
        else:
            commentaire = random.choice(COMMENTAIRES_NEUTRES)
            emoji = "⭐⭐⭐"
        
        self.print_safe(f"   📍 LIVRÉ ! 💬 \"{commentaire}\" {emoji}")
        
        self.gestionnaire.marquer_livre(livreur_attribue)
    
    def afficher_stats_periodiques(self):
        """Affiche les stats toutes les 5 secondes"""
        while True:
            time.sleep(5)
            stats = self.gestionnaire.obtenir_stats()
            
            self.print_safe("\n" + "📊"*30)
            self.print_safe("STATISTIQUES EN TEMPS RÉEL")
            self.print_safe("📊"*30)
            self.print_safe(f"✅ Commandes livrées    : {stats['commandes_traitees']}")
            self.print_safe(f"🚴 En cours de livraison: {stats['commandes_en_cours']}")
            self.print_safe(f"❌ Échecs               : {stats['commandes_echouees']}")
            self.print_safe(f"🟢 Livreurs disponibles : {stats['livreurs_disponibles']}/{self.nb_livreurs}")
            self.print_safe(f"🔴 Livreurs occupés     : {stats['livreurs_en_livraison']}/{self.nb_livreurs}")
            self.print_safe("📊"*30 + "\n")
    
    def lancer_simulation(self):
        print("\n" + "="*70)
        print("🚀 SIMULATION MULTI-THREADING - Commandes Simultanées")
        print("="*70)
        print(f"📊 {self.nb_livreurs} livreurs | {self.nb_commandes} commandes")
        print("="*70 + "\n")
        
        # Thread pour les stats
        thread_stats = Thread(target=self.afficher_stats_periodiques, daemon=True)
        thread_stats.start()
        
        # Lancer les commandes en parallèle
        threads = []
        for i in range(1, self.nb_commandes + 1):
            thread = Thread(target=self.traiter_commande_thread, args=(i,))
            thread.start()
            threads.append(thread)
            
            # Démarrage progressif
            time.sleep(random.uniform(1, 3))
        
        # Attendre que toutes les commandes soient terminées
        for thread in threads:
            thread.join()
        
        # Stats finales
        stats = self.gestionnaire.obtenir_stats()
        print("\n" + "="*70)
        print("✅ SIMULATION TERMINÉE")
        print("="*70)
        print(f"\n📊 RÉSULTATS FINAUX:")
        print(f"   ✅ Commandes livrées: {stats['commandes_traitees']}")
        print(f"   ❌ Commandes échouées: {stats['commandes_echouees']}")
        print(f"   📈 Taux de succès: {stats['commandes_traitees']/self.nb_commandes*100:.1f}%")
        print(f"\n💡 Système multi-threading opérationnel !\n")

if __name__ == "__main__":
    try:
        simulation = SimulationMultithreading(nb_livreurs=10, nb_commandes=25)
        simulation.lancer_simulation()
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation interrompue")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

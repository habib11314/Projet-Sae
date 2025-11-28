"""
Client Automatique Amélioré
- Charge les VRAIS restaurants et menus depuis JSON
- Génère des commandes aléatoires réalistes
- Fonctionne en continu
"""

import redis
import json
import random
import time
from datetime import datetime
import os

# Données réalistes
PRENOMS = ["Mohammed", "Fatima", "Ali", "Aisha", "Omar", "Khadija", "Hassan", 
           "Pierre", "Sophie", "Jean", "Marie", "Emma", "Léa", "Nicolas"]

NOMS = ["Benali", "Mansouri", "Khalil", "Martin", "Bernard", "Dubois", 
        "Robert", "Petit", "Durand", "Leroy"]

ADRESSES = [
    "45 Avenue des Champs-Élysées, 75008 Paris",
    "12 Rue de Rivoli, 75004 Paris",
    "33 Boulevard Saint-Michel, 75005 Paris",
    "88 Avenue de la République, 93100 Montreuil",
    "15 Rue Victor Hugo, 93000 Bobigny",
    "47 Boulevard Gambetta, 93170 Bagnolet",
    "22 Rue Jean Jaurès, 93130 Noisy-le-Sec",
    "135 Avenue du Président Wilson, 93210 Saint-Denis"
]

def charger_restaurants_json():
    """Charge les VRAIS restaurants et VRAIS menus depuis les 2 fichiers JSON"""
    try:
        # 1. Charger les restaurants
        chemin_restaurants = os.path.join(os.path.dirname(__file__), 'restaurants.json')
        with open(chemin_restaurants, 'r', encoding='utf-8') as f:
            data_restos = json.load(f)
        
        restaurants_data = data_restos.get('restaurants', data_restos) if isinstance(data_restos, dict) else data_restos
        
        # 2. Charger les menus
        # ATTENTION: `menu.json` peut être très volumineux (ex: >100MB). Pour
        # éviter un MemoryError sur `json.load`, on parcourt le fichier en
        # streaming et on collecte uniquement les entrées correspondant aux
        # restaurants que l'on charge (au maximum 100 restaurants).
        chemin_menu = os.path.join(os.path.dirname(__file__), 'menu.json')

        menus_par_resto = {}
        # IDs des restaurants que l'on retiendra (max 100)
        target_ids = set(str(r.get('id', '')) for r in restaurants_data[:100])

        try:
            file_size = os.path.getsize(chemin_menu)
        except Exception:
            file_size = 0

        # If file is small, fallback to simple load
        if file_size and file_size < 10 * 1024 * 1024:
            with open(chemin_menu, 'r', encoding='utf-8') as f:
                data_menu = json.load(f)
            menu_data = data_menu.get('menu', data_menu) if isinstance(data_menu, dict) else data_menu
            iterable = menu_data
        else:
            # Streaming: read chunks and extract JSON objects inside the top-level
            # array `menu`. This avoids allocating the whole file in memory.
            iterable = []
            with open(chemin_menu, 'r', encoding='utf-8') as f:
                buf = ''
                in_array = False
                depth = 0
                obj_buf = ''
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    buf += chunk
                    i = 0
                    while i < len(buf):
                        ch = buf[i]
                        if not in_array:
                            if ch == '[':
                                in_array = True
                            i += 1
                            continue

                        # inside array: find JSON objects by brace depth
                        if depth == 0:
                            if ch == '{':
                                depth = 1
                                obj_buf = ch
                        else:
                            obj_buf += ch
                            if ch == '{':
                                depth += 1
                            elif ch == '}':
                                depth -= 1
                                if depth == 0:
                                    # Complete JSON object collected
                                    try:
                                        obj = json.loads(obj_buf)
                                        iterable.append(obj)
                                    except Exception:
                                        # skip malformed objects
                                        pass
                                    obj_buf = ''
                        i += 1

                    # keep the leftover (unprocessed tail) in buf
                    buf = buf[i:]

        # 3. Organiser les menus par restaurant_id (ne garder que ceux qui nous intéressent)
        for item in iterable:
            try:
                resto_id = str(item.get('restaurant_id', ''))
            except Exception:
                continue
            # si on collecte en streaming, filtrer sur target_ids
            if target_ids and resto_id not in target_ids:
                continue

            if resto_id not in menus_par_resto:
                menus_par_resto[resto_id] = []

            # Extraire le prix (format: "15.99 USD")
            price_str = item.get('price', '0')
            try:
                price = float(str(price_str).replace('USD', '').replace('$', '').strip())
            except Exception:
                price = 10.0

            menus_par_resto[resto_id].append({
                "name": item.get('name', 'Plat'),
                "category": item.get('category', ''),
                "description": item.get('description', ''),
                "price": price
            })
        
        # 4. Créer la liste des restaurants avec leurs menus
        restaurants = []
        for resto in restaurants_data[:100]:  # 100 restaurants max
            resto_id = str(resto.get('id', ''))
            
            # Récupérer le VRAI menu depuis menu.json
            menu_items = menus_par_resto.get(resto_id, [])[:20]  # Max 20 plats
            
            if menu_items:  # Seulement si le restaurant a un menu
                restaurants.append({
                    "id": resto_id,
                    "name": resto.get('name', 'Restaurant'),
                    "address": resto.get('full_address', resto.get('address', 'Adresse inconnue')),
                    "category": resto.get('category', ''),
                    "menu": menu_items
                })
        
        print(f"✅ {len(restaurants)} restaurants avec VRAIS menus chargés depuis JSON")
        return restaurants
    except Exception as e:
        print(f"❌ Erreur chargement JSON: {e}")
        import traceback
        traceback.print_exc()
        return []

def generer_commande_aleatoire(restaurants):
    """Génère une commande avec VRAIS plats du JSON"""
    if not restaurants:
        print("❌ Aucun restaurant disponible")
        return None
    
    # Client aléatoire
    prenom = random.choice(PRENOMS)
    nom = random.choice(NOMS)
    nom_client = f"{prenom} {nom}"
    id_client = f"client-{random.randint(1000, 9999)}"
    # Statut premium aléatoire (20% des clients)
    premium = random.random() < 0.2
    
    # Restaurant aléatoire (avec VRAI menu)
    restaurant = random.choice(restaurants)
    
    # Plats aléatoires (1 à 3 plats du VRAI menu)
    nb_plats = random.randint(1, 3)
    plats_choisis = random.sample(restaurant['menu'], min(nb_plats, len(restaurant['menu'])))
    
    # Adresse aléatoire
    adresse_livraison = random.choice(ADRESSES)
    
    # Calculs
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    id_commande = f"CMD-{timestamp[:14]}-{random.randint(1000, 9999)}"
    montant_total = sum(p['price'] for p in plats_choisis)
    remuneration = round(montant_total * 0.15, 2)
    
    frais_livraison = 0.0 if premium else 2.99
    return {
        "id_commande": id_commande,
        "id_client": id_client,
        "nom_client": nom_client,
        "premium": premium,
        "restaurant_nom": restaurant['name'],
        "restaurant_adresse": restaurant['address'],
        "plats": [{"nom": p['name'], "prix": p['price']} for p in plats_choisis],
        "montant_total": round(montant_total, 2),
        "adresse_livraison": adresse_livraison,
        "remuneration_livreur": remuneration,
        "frais_livraison": frais_livraison,
        "timestamp": datetime.now().isoformat()
    }

def main():
    print("\n" + "="*60)
    print("🛒 CLIENT AUTOMATIQUE - Commandes Aléatoires")
    print("="*60 + "\n")
    
    # Connexion Redis
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        redis_client.ping()
        print("✅ Connecté à Redis\n")
    except:
        print("❌ Redis non accessible. Démarrez redis-server.exe")
        return
    
    # Charger les restaurants
    restaurants = charger_restaurants_json()
    if not restaurants:
        print("❌ Impossible de charger les restaurants")
        return
    
    # Thread pour écouter les notifications clients
    def ecouter_notifications():
        pubsub = redis_client.pubsub()
        pubsub.subscribe('notifications-clients')
        print("👂 En écoute des notifications livreurs...\n")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    notif = json.loads(message['data'])
                    
                    if notif.get('type') == 'attribution_confirmee':
                        print("\n" + "📱"*30)
                        print(f"📲 LIVREUR ASSIGNÉ!")
                        print(f"   📦 Commande: {notif['id_commande'][-8:]}")
                        print(f"   🚴 Livreur: {notif['livreur_nom']}")
                        print(f"   📞 Téléphone: {notif['livreur_telephone']}")
                        print(f"   💬 {notif['message']}")
                        print("📱"*30 + "\n")
                    
                    elif notif.get('type') == 'commande_annulee':
                        print("\n" + "❌"*30)
                        print(f"🚫 COMMANDE ANNULÉE")
                        print(f"   📦 Commande: {notif['id_commande'][-8:]}")
                        print(f"   ⚠️  Raison: {notif['raison']}")
                        print(f"   💬 {notif['message']}")
                        # Show refunded amount if provided
                        montant = notif.get('montant_rembourse') or notif.get('montant')
                        if montant:
                            try:
                                # montant may be string or number
                                print(f"   💶 Remboursement: {float(montant):.2f}€")
                            except Exception:
                                print(f"   💶 Remboursement: {montant}€")
                        print("❌"*30 + "\n")
                except:
                    pass
    
    # Lancer le thread d'écoute
    from threading import Thread
    thread_notifs = Thread(target=ecouter_notifications, daemon=True)
    thread_notifs.start()
    
    print(f"🚀 Démarrage de la génération de commandes...\n")
    print("   (Ctrl+C pour arrêter)\n")
    
    commande_num = 1
    
    try:
        while True:
            # Générer une commande
            commande = generer_commande_aleatoire(restaurants)
            
            if commande:
                print(f"📦 COMMANDE #{commande_num}")
                print(f"   👤 Client: {commande['nom_client']} {'(PREMIUM)' if commande['premium'] else ''}")
                print(f"   🏪 Restaurant: {commande['restaurant_nom']}")
                print(f"   🍽️  Plats: {', '.join([p['nom'][:30] for p in commande['plats']])}")
                print(f"   💰 Total: {commande['montant_total']}€")
                print(f"   🚚 Frais livraison: {commande['frais_livraison']}€{' (offert)' if commande['premium'] else ''}")
                print(f"   📍 Livraison: {commande['adresse_livraison'][:50]}")
                
                # Publier sur Redis
                message_json = json.dumps(commande, ensure_ascii=False)
                nb_receivers = redis_client.publish('nouvelles-commandes', message_json)
                print(f"   ✅ Publiée → {nb_receivers} manager(s) notifié(s)\n")
                # Optionnel : envoi d'une demande d'annulation aléatoire (5% de chance)
                def maybe_cancel(cmd):
                    if random.random() < 0.05:
                        delay = random.uniform(1, 10)  # small delay before cancel
                        def do_cancel():
                            time.sleep(delay)
                            ann = {"id_commande": cmd["id_commande"], "id_client": cmd["id_client"], "raison": "client_change_mind"}
                            try:
                                redis_client.publish('annulations-clients', json.dumps(ann, ensure_ascii=False))
                                print(f"   ❗ Demande d'annulation envoyée pour {cmd['id_commande']} après {delay:.1f}s")
                            except Exception:
                                pass
                        Thread(target=do_cancel, daemon=True).start()
                maybe_cancel(commande)
                commande_num += 1
            
            # Pause aléatoire entre 5 et 15 secondes
            delai = random.uniform(5, 15)
            print(f"⏳ Prochaine commande dans {delai:.1f}s...\n")
            time.sleep(delai)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Client automatique arrêté")
        print(f"📊 Total: {commande_num - 1} commandes générées\n")

if __name__ == "__main__":
    main()

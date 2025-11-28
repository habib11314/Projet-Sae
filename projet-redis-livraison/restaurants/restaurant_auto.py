"""
Restaurant Automatique (moved to restaurants/)
"""

import redis
import json
import random
import time
from threading import Thread

RAISONS_REFUS = [
    "Rupture de stock",
    "Cuisine débordée",
    "Fermeture imminente",
    "Ingrédients manquants",
    "Temps de préparation trop long"
]

class RestaurantAutomatique:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.taux_acceptation = random.uniform(0.80, 0.95)  # 80-95% d'acceptation
        self.commandes_acceptees = 0
        self.commandes_refusees = 0
        
    def ecouter_demandes(self):
        """Écoute les demandes de préparation du manager"""
        self.pubsub.subscribe('demandes-restaurants')
        print("👂 En écoute des demandes de préparation...\n")
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    demande = json.loads(message['data'])
                    id_commande = demande['id_commande']
                    restaurant_nom = demande['restaurant_nom']
                    plats = demande['plats']
                    montant = demande['montant_total']
                    
                    print(f"\n📋 DEMANDE DE PRÉPARATION")
                    print(f"   📦 Commande: {id_commande[-8:]}")
                    print(f"   🏪 Restaurant: {restaurant_nom[:40]}")
                    print(f"   🍽️  Plats: {len(plats)} article(s)")
                    print(f"   💰 Montant: {montant}€")
                    
                    # Temps de vérification (1-3 secondes)
                    temps_verif = random.uniform(1, 3)
                    print(f"   ⏱️  Vérification en cours... ({temps_verif:.1f}s)")
                    time.sleep(temps_verif)
                    
                    # Décision aléatoire
                    accepte = random.random() < self.taux_acceptation
                    
                    if accepte:
                        print(f"   ✅ COMMANDE ACCEPTÉE - Préparation démarrée")
                        self.commandes_acceptees += 1
                        
                        reponse = {
                            "id_commande": id_commande,
                            "restaurant_nom": restaurant_nom,
                            "statut": "accepte",
                            "temps_preparation": random.randint(10, 25),
                            "message": "Commande en préparation"
                        }
                    else:
                        raison = random.choice(RAISONS_REFUS)
                        print(f"   ❌ COMMANDE REFUSÉE - {raison}")
                        self.commandes_refusees += 1
                        
                        reponse = {
                            "id_commande": id_commande,
                            "restaurant_nom": restaurant_nom,
                            "statut": "refuse",
                            "raison": raison,
                            "message": f"Impossible de préparer : {raison}"
                        }
                    
                    # Envoyer la réponse au manager
                    self.redis_client.publish(
                        'reponses-restaurants',
                        json.dumps(reponse, ensure_ascii=False)
                    )
                    
                    print(f"   📤 Réponse envoyée au manager\n")
                    
                except Exception as e:
                    print(f"❌ Erreur traitement demande: {e}")
    
    def demarrer(self):
        print("\n" + "="*60)
        print("🏪 RESTAURANTS AUTOMATIQUES")
        print("="*60 + "\n")
        print(f"   Taux d'acceptation: {self.taux_acceptation*100:.0f}%\n")
        
        try:
            self.redis_client.ping()
            print("✅ Connecté à Redis\n")
        except:
            print("❌ Redis non accessible")
            return
        
        # Lancer le thread d'écoute
        thread_demandes = Thread(target=self.ecouter_demandes, daemon=True)
        thread_demandes.start()
        # Lancer le thread d'écoute des notifications destinées aux restaurants
        thread_notifications = Thread(target=self.ecouter_notifications_resto, daemon=True)
        thread_notifications.start()
        
        print("🚀 En attente de demandes (Ctrl+C pour arrêter)\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n\n🛑 Restaurants déconnectés")
            print(f"📊 Statistiques:")
            print(f"   ✅ Acceptées: {self.commandes_acceptees}")
            print(f"   ❌ Refusées: {self.commandes_refusees}")
            print(f"   📈 Taux: {self.commandes_acceptees/(self.commandes_acceptees+self.commandes_refusees)*100:.1f}%\n" if (self.commandes_acceptees + self.commandes_refusees) > 0 else "")

    def ecouter_notifications_resto(self):
        """Écoute les notifications ciblées aux restaurants (pattern: notifications-restaurant:*)"""
        try:
            pubsub_notif = self.redis_client.pubsub(ignore_subscribe_messages=True)
            pubsub_notif.psubscribe('notifications-restaurant:*')
            print("👂 En écoute des notifications restaurants (pattern: notifications-restaurant:*)\n")

            for message in pubsub_notif.listen():
                try:
                    if message['type'] in ('pmessage', 'message'):
                        data = message.get('data')
                        channel = message.get('channel')
                        # channel may be bytes depending on redis client config
                        if isinstance(channel, bytes):
                            channel = channel.decode()
                        print(f"\n🔔 Notification reçue sur {channel}: {data}\n")
                except Exception as e:
                    print(f"❌ Erreur traitement notification resto: {e}")

        except Exception as e:
            print(f"❌ Impossible d'écouter notifications restaurants: {e}")

if __name__ == "__main__":
    restaurant = RestaurantAutomatique()
    restaurant.demarrer()

"""
Livreur Automatique Amélioré (moved to livreurs/)
"""

import redis
import json
import random
import time
from threading import Thread

COMMENTAIRES_POSITIFS = [
    "Excellent service !",
    "Livreur très sympathique",
    "Livraison rapide, merci !",
    "Nourriture encore chaude",
    "Parfait, rien à redire"
]

COMMENTAIRES_NEGATIFS = [
    "Frites froides",
    "En retard de 15 minutes",
    "Manque de couverts",
    "Burger écrasé",
    "Il manque un plat"
]

COMMENTAIRES_NEUTRES = ["Correct", "RAS", "Bien", "Ok"]

class LivreurAutomatique:
    def __init__(self, id_livreur):
        self.id_livreur = id_livreur
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.pubsub_offres = self.redis_client.pubsub()
        self.pubsub_notifs = self.redis_client.pubsub()
        self.statut = "disponible"
        self.nb_livraisons = 0
        self.taux_acceptation = random.uniform(0.5, 0.8)  # 50-80% d'acceptation
        
    def ecouter_offres(self):
        """Écoute les offres et répond aléatoirement"""
        self.pubsub_offres.subscribe('offres-courses')
        
        for message in self.pubsub_offres.listen():
            if message['type'] == 'message' and self.statut == "disponible":
                try:
                    offre = json.loads(message['data'])
                    id_commande = offre['id_commande']
                    restaurant = offre['restaurant_nom']
                    remuneration = offre['remuneration_livreur']
                    
                    print(f"\n📢 OFFRE REÇUE: {id_commande[-8:]}")
                    print(f"   🏪 {restaurant}")
                    print(f"   💰 Rémunération: {remuneration}€")
                    
                    # Temps de réflexion (1-3s)
                    time.sleep(random.uniform(1, 3))
                    
                    # Décision aléatoire
                    if random.random() < self.taux_acceptation:
                        print(f"   ✅ J'ACCEPTE la course !")
                        self.statut = "en_livraison"
                        
                        # Envoyer candidature
                        candidature = {
                            "id_livreur": self.id_livreur,
                            "id_commande": id_commande
                        }
                        self.redis_client.publish(
                            'reponses-livreurs',
                            json.dumps(candidature, ensure_ascii=False)
                        )
                        
                        # Simuler la livraison dans un thread
                        Thread(target=self.simuler_livraison, args=(id_commande,), daemon=True).start()
                    else:
                        raisons = ["trop loin", "en pause", "autre course", "pas intéressé"]
                        raison = random.choice(raisons)
                        print(f"   ❌ Je REFUSE ({raison})\n")
                        
                except Exception as e:
                    print(f"❌ Erreur traitement offre: {e}")
    
    def ecouter_notifications(self):
        """Écoute les notifications privées"""
        self.pubsub_notifs.subscribe(f'notifications-livreur:{self.id_livreur}')
        
        for message in self.pubsub_notifs.listen():
            if message['type'] == 'message':
                try:
                    notification = json.loads(message['data'])
                    if notification.get('type') == 'attribution':
                        print(f"\n🎉 {notification['message']}")
                        print(f"   📦 Commande: {notification['id_commande'][-8:]}")
                        print(f"   🚴 Je pars livrer...\n")
                except:
                    pass
    
    def simuler_livraison(self, id_commande):
        """Simule le processus de livraison"""
        # Temps de livraison (10-25 secondes)
        temps_livraison = random.uniform(10, 25)
        print(f"⏱️  Temps de livraison: {temps_livraison:.0f}s")
        time.sleep(temps_livraison)
        
        # Livraison terminée
        print(f"\n📍 LIVRAISON TERMINÉE: {id_commande[-8:]}")
        
        # Commentaire client aléatoire
        type_com = random.choices(['positif', 'negatif', 'neutre'], weights=[0.7, 0.2, 0.1])[0]
        
        if type_com == 'positif':
            commentaire = random.choice(COMMENTAIRES_POSITIFS)
            note = "⭐⭐⭐⭐⭐"
        elif type_com == 'negatif':
            commentaire = random.choice(COMMENTAIRES_NEGATIFS)
            note = "⭐⭐"
        else:
            commentaire = random.choice(COMMENTAIRES_NEUTRES)
            note = "⭐⭐⭐"
        
        print(f"   💬 Client: \"{commentaire}\" {note}")
        
        # Publier le statut
        statut = {
            "id_commande": id_commande,
            "id_livreur": self.id_livreur,
            "statut": "Livré",
            "commentaire": commentaire,
            "note": note
        }
        self.redis_client.publish(
            f"statut-livraison:{id_commande}",
            json.dumps(statut, ensure_ascii=False)
        )
        
        # Redevenir disponible
        self.statut = "disponible"
        self.nb_livraisons += 1
        print(f"   ✅ Disponible pour nouvelle course (Total: {self.nb_livraisons})\n")
    
    def demarrer(self):
        print("\n" + "="*60)
        print(f"🚴 LIVREUR: {self.id_livreur}")
        print("="*60)
        print(f"   Taux d'acceptation: {self.taux_acceptation*100:.0f}%\n")
        
        try:
            self.redis_client.ping()
            print("✅ Connecté à Redis\n")
        except:
            print("❌ Redis non accessible")
            return
        
        # Lancer les threads d'écoute
        thread_offres = Thread(target=self.ecouter_offres, daemon=True)
        thread_notifs = Thread(target=self.ecouter_notifications, daemon=True)
        
        thread_offres.start()
        thread_notifs.start()
        
        print("🚀 En attente d'offres (Ctrl+C pour arrêter)\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n\n🛑 Livreur {self.id_livreur} déconnecté")
            print(f"📊 {self.nb_livraisons} livraisons effectuées\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        id_livreur = sys.argv[1]
    else:
        id_livreur = f"livreur-{random.randint(1, 999):03d}"
    
    livreur = LivreurAutomatique(id_livreur)
    livreur.demarrer()

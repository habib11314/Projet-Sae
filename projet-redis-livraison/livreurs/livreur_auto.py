"""
Livreur Automatique (moved to livreurs/)
"""

import redis
import json
import sys
import random
import time

class LivreurAutomatique:
    def __init__(self, id_livreur, host='localhost', port=6379):
        """
        Initialise la connexion Redis pour un livreur automatique
        """
        self.id_livreur = id_livreur
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        
        # Probabilité d'accepter une offre (70% de chance)
        self.taux_acceptation = 0.7
        
        # Abonnement simultané aux deux canaux
        self.pubsub.subscribe('offres-courses')  # Canal public
        self.pubsub.subscribe(f'notifications-livreur:{id_livreur}')  # Canal privé
        
        print(f"🚴 Livreur automatique {id_livreur} connecté et en attente d'offres...")
        
    def ecouter_messages(self):
        """Boucle principale d'écoute des messages Redis"""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                canal = message['channel']
                data = json.loads(message['data'])
                
                # Traitement selon le type de canal
                if canal == 'offres-courses':
                    self._traiter_offre_auto(data)
                elif canal == f'notifications-livreur:{self.id_livreur}':
                    self._traiter_notification(data)
                    
    def _traiter_offre_auto(self, offre):
        """Traite automatiquement une nouvelle offre"""
        print("\n" + "="*60)
        print("🆕 NOUVELLE OFFRE DE COURSE")
        print("="*60)
        print(f"ID Commande      : {offre['id_commande']}")
        print(f"Restaurant       : {offre['restaurant_nom']}")
        print(f"Adresse retrait  : {offre['restaurant_adresse']}")
        print(f"Adresse livraison: {offre['adresse_livraison']}")
        print(f"Rémunération     : {offre['remuneration_livreur']}€")
        print("="*60)
        
        # Simuler un temps de réflexion (1-3 secondes)
        temps_reflexion = random.uniform(1, 3)
        print(f"⏳ Analyse de l'offre... ({temps_reflexion:.1f}s)")
        time.sleep(temps_reflexion)
        
        # Décision aléatoire basée sur le taux d'acceptation
        accepte = random.random() < self.taux_acceptation
        
        if accepte:
            print(f"✅ {self.id_livreur} ACCEPTE la course !")
            self.manifester_interet(offre['id_commande'])
        else:
            print(f"❌ {self.id_livreur} REFUSE la course (pas disponible)")
            
    def _traiter_notification(self, notification):
        """Affiche les notifications privées (attribution de course)"""
        print("\n" + "🎉"*30)
        print(notification['message'])
        print("🎉"*30 + "\n")
        
    def manifester_interet(self, id_commande):
        """
        Publie une candidature sur le canal 'reponses-livreurs'
        """
        candidature = {
            "id_livreur": self.id_livreur,
            "id_commande": id_commande
        }
        
        message_json = json.dumps(candidature, ensure_ascii=False)
        self.redis_client.publish('reponses-livreurs', message_json)
        
        print(f"📤 Candidature envoyée pour la commande {id_commande}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python livreur_auto.py <id_livreur>")
        print("   Exemple: python livreur_auto.py livreur-001")
        sys.exit(1)
    id_livreur = sys.argv[1]
    livreur = LivreurAutomatique(id_livreur)
    try:
        livreur.ecouter_messages()
    except KeyboardInterrupt:
        print(f"\n👋 Livreur {id_livreur} déconnecté")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

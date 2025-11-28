import redis
import json
import sys
from threading import Thread

class Livreur:
    def __init__(self, id_livreur, host='localhost', port=6379):
        """
        Initialise la connexion Redis pour un livreur
        
        Args:
            id_livreur (str): Identifiant unique du livreur
        """
        self.id_livreur = id_livreur
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        
        # Abonnement simultané aux deux canaux
        self.pubsub.subscribe('offres-courses')  # Canal public
        self.pubsub.subscribe(f'notifications-livreur:{id_livreur}')  # Canal privé
        
        print(f"🚴 Livreur {id_livreur} connecté et en attente d'offres...")
        
    def ecouter_messages(self):
        """
        Boucle principale d'écoute des messages Redis
        Traite à la fois les offres publiques et les notifications privées
        """
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                canal = message['channel']
                data = json.loads(message['data'])
                
                # Traitement selon le type de canal
                if canal == 'offres-courses':
                    self._traiter_offre(data)
                elif canal == f'notifications-livreur:{self.id_livreur}':
                    self._traiter_notification(data)
                    
    def _traiter_offre(self, offre):
        """Affiche les détails d'une nouvelle offre"""
        print("\n" + "="*60)
        print("🆕 NOUVELLE OFFRE DE COURSE")
        print("="*60)
        print(f"ID Commande      : {offre['id_commande']}")
        print(f"Restaurant       : {offre['restaurant_nom']}")
        print(f"Adresse retrait  : {offre['restaurant_adresse']}")
        print(f"Adresse livraison: {offre['adresse_livraison']}")
        print(f"Rémunération     : {offre['remuneration_livreur']}€")
        print("="*60)
        
        # Demande à l'utilisateur s'il est intéressé
        reponse = input("Êtes-vous intéressé ? (o/n) : ").strip().lower()
        
        if reponse == 'o':
            self.manifester_interet(offre['id_commande'])
        else:
            print("❌ Offre refusée\n")
            
    def _traiter_notification(self, notification):
        """Affiche les notifications privées (attribution de course)"""
        print("\n" + "🎉"*30)
        print(notification['message'])
        print("🎉"*30 + "\n")
        
    def manifester_interet(self, id_commande):
        """
        Publie une candidature sur le canal 'reponses-livreurs'
        
        Args:
            id_commande (str): Identifiant de la commande visée
        """
        candidature = {
            "id_livreur": self.id_livreur,
            "id_commande": id_commande
        }
        
        message_json = json.dumps(candidature, ensure_ascii=False)
        self.redis_client.publish('reponses-livreurs', message_json)
        
        print(f"✅ Candidature envoyée pour la commande {id_commande}\n")

# Exemple d'utilisation
if __name__ == "__main__":
    # Récupération de l'ID du livreur (argument ligne de commande ou par défaut)
    id_livreur = sys.argv[1] if len(sys.argv) > 1 else "livreur-001"
    
    livreur = Livreur(id_livreur)
    
    try:
        # Démarrage de l'écoute (bloquant)
        livreur.ecouter_messages()
    except KeyboardInterrupt:
        print(f"\n👋 Livreur {id_livreur} déconnecté")

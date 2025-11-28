"""
Manager (moved to managers/)
"""

import redis
import json
import time
from threading import Thread

class Manager:
    def __init__(self, host='localhost', port=6379):
        """Initialise la connexion Redis pour le manager"""
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.pubsub_commandes = self.redis_client.pubsub()
        self.candidatures = []  # Stocke les candidatures reçues
        self.commandes_en_attente = {}  # Stocke les commandes en attente d'attribution
        
    def publier_offre_course(self, offre):
        """
        Publie une nouvelle offre de course sur le canal 'offres-courses'
        
        Args:
            offre (dict): Dictionnaire contenant les détails de la commande
        """
        # Sérialisation de l'offre en JSON
        message_json = json.dumps(offre, ensure_ascii=False)
        
        # Publication sur le canal public
        nb_destinataires = self.redis_client.publish('offres-courses', message_json)
        
        print(f"\n✅ Offre publiée (reçue par {nb_destinataires} livreur(s)) :")
        print(f"   ID Commande      : {offre['id_commande']}")
        print(f"   Restaurant       : {offre['restaurant_nom']} ({offre['restaurant_adresse']})")
        print(f"   Livraison        : {offre['adresse_livraison']}")
        print(f"   Rémunération     : {offre['remuneration_livreur']}€")
        
    def ecouter_nouvelles_commandes(self):
        """
        Écoute les nouvelles commandes des clients et crée automatiquement des offres
        Cette méthode doit être exécutée dans un thread séparé
        """
        self.pubsub_commandes.subscribe('nouvelles-commandes')
        print("\n📡 En attente de nouvelles commandes des clients...")
        
        for message in self.pubsub_commandes.listen():
            if message['type'] == 'message':
                # Désérialisation de la commande
                commande = json.loads(message['data'])
                self._traiter_nouvelle_commande(commande)
    
    def _traiter_nouvelle_commande(self, commande):
        """Traite une nouvelle commande reçue d'un client"""
        print("\n" + "💼"*30)
        print("📥 NOUVELLE COMMANDE REÇUE")
        print("💼"*30)
        print(f"   ID Commande      : {commande['id_commande']}")
        print(f"   Client           : {commande['nom_client']}")
        print(f"   Restaurant       : {commande['restaurant_nom']}")
        print(f"   Montant total    : {commande['montant_total']}€")
        print(f"   Adresse livraison: {commande['adresse_livraison']}")
        print("💼"*30 + "\n")
        
        # Stocker la commande
        self.commandes_en_attente[commande['id_commande']] = commande
        
        # Créer une offre pour les livreurs
        offre = {
            "id_commande": commande['id_commande'],
            "restaurant_nom": commande['restaurant_nom'],
            "restaurant_adresse": commande['restaurant_adresse'],
            "adresse_livraison": commande['adresse_livraison'],
            "remuneration_livreur": commande['remuneration_livreur']
        }
        
        self.publier_offre_course(offre)
    
    def ecouter_reponses_livreurs(self):
        """
        Écoute en continu les candidatures des livreurs sur 'reponses-livreurs'
        Cette méthode doit être exécutée dans un thread séparé
        """
        self.pubsub.subscribe('reponses-livreurs')
        print("\n📡 Écoute des candidatures des livreurs...")
        
        commandes_attribuees = set()  # Pour éviter les attributions multiples
         
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                # Désérialisation de la candidature
                candidature = json.loads(message['data'])
                self.candidatures.append(candidature)
                
                print(f"\n📬 Nouvelle candidature reçue :")
                print(f"   Livreur ID       : {candidature['id_livreur']}")
                print(f"   Pour la commande : {candidature['id_commande']}")
                
                # Attribution automatique au premier livreur qui répond
                id_commande = candidature['id_commande']
                if id_commande not in commandes_attribuees:
                    commandes_attribuees.add(id_commande)
                    self.attribuer_course(candidature['id_livreur'], id_commande)
                
    def attribuer_course(self, id_livreur, id_commande):
        """
        Envoie une notification d'attribution au livreur sélectionné
        
        Args:
            id_livreur (str): Identifiant du livreur choisi
            id_commande (str): Identifiant de la commande
        """
        canal_prive = f"notifications-livreur:{id_livreur}"
        
        notification = {
            "type": "attribution",
            "id_commande": id_commande,
            "message": f"🎉 Félicitations ! La commande {id_commande} vous a été attribuée."
        }
        
        message_json = json.dumps(notification, ensure_ascii=False)
        self.redis_client.publish(canal_prive, message_json)
        
        print(f"\n✅ Course {id_commande} attribuée au livreur {id_livreur}")
        
        # Envoyer confirmation au client
        if id_commande in self.commandes_en_attente:
            commande = self.commandes_en_attente[id_commande]
            self.confirmer_commande_client(commande['id_client'], id_commande, id_livreur)
    
    def confirmer_commande_client(self, id_client, id_commande, id_livreur):
        """Envoie une confirmation au client"""
        canal_client = f"confirmation-client:{id_client}"
        
        confirmation = {
            "id_commande": id_commande,
            "id_livreur": id_livreur,
            "statut": "Livreur attribué",
            "message": f"Votre commande {id_commande} a été prise en charge par le livreur {id_livreur}"
        }
        
        message_json = json.dumps(confirmation, ensure_ascii=False)
        self.redis_client.publish(canal_client, message_json)
        
        print(f"✅ Confirmation envoyée au client {id_client}")


# Exemple d'utilisation
if __name__ == "__main__":
    manager = Manager()
    
    # Démarrage de l'écoute des nouvelles commandes dans un thread séparé
    thread_commandes = Thread(target=manager.ecouter_nouvelles_commandes, daemon=True)
    thread_commandes.start()
    
    # Démarrage de l'écoute des réponses dans un thread séparé
    thread_ecoute = Thread(target=manager.ecouter_reponses_livreurs, daemon=True)
    thread_ecoute.start()
    
    print("\n🏢 Manager démarré et prêt à recevoir des commandes...")
    print("   📥 Écoute les commandes des clients sur 'nouvelles-commandes'")
    print("   📬 Écoute les candidatures des livreurs sur 'reponses-livreurs'")
    
    # Maintenir le programme actif
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Manager arrêté")

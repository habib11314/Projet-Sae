"""
Manager Automatique Amélioré (moved to managers/)
"""

import redis
import json
import time
import random
from threading import Thread

class ManagerAutomatique:
    def __init__(self):
        # backward-compatible: default keeps global broadcast behavior
        # set use_private_offers=True to select and send offers to specific livreurs
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.pubsub_commandes = self.redis_client.pubsub()
        self.pubsub_reponses = self.redis_client.pubsub()
        self.pubsub_restaurants = self.redis_client.pubsub()
        self.pubsub_annulations = self.redis_client.pubsub()
        # channel names
        self.CHANNEL_ANNULATIONS = 'annulations-clients'
        self.CHANNEL_CONFIRMATION_CLIENT = 'confirmation-client'  # use confirmation-client:{id_client}
        self.commandes_attribuees = set()
        self.commandes_en_attente_resto = {}  # {id_commande: data_commande}
        # Configuration for targeted offers
        self.use_private_offers = False
        self.targets_per_offer = 5
        self.geo_search_radius_m = 5000

    def ecouter_nouvelles_commandes(self):
        """Écoute les commandes clients et demande confirmation au restaurant"""
        self.pubsub_commandes.subscribe('nouvelles-commandes')
        print("👂 En écoute des nouvelles commandes...\n")
        
        for message in self.pubsub_commandes.listen():
            if message['type'] == 'message':
                try:
                    commande = json.loads(message['data'])
                    
                    print("\n" + "🆕"*30)
                    print(f"📦 NOUVELLE COMMANDE: {commande['id_commande'][-8:]}")
                    print(f"   👤 Client: {commande['nom_client']}")
                    print(f"   🏪 Restaurant: {commande['restaurant_nom']}")
                    print(f"   💰 Montant: {commande['montant_total']}€")
                    print(f"   🚚 Frais livraison: {commande.get('frais_livraison', 2.99)}€{' (offert PREMIUM)' if commande.get('premium') else ''}")
                    print("🆕"*30)
                    
                    # NOUVELLE ÉTAPE : Demander confirmation au restaurant
                    print(f"📤 Envoi demande de préparation au restaurant...")
                    
                    demande_restaurant = {
                        "id_commande": commande['id_commande'],
                        "restaurant_nom": commande['restaurant_nom'],
                        "plats": commande['plats'],
                        "montant_total": commande['montant_total']
                    }
                    
                    # Stocker la commande en attente de réponse restaurant
                    self.commandes_en_attente_resto[commande['id_commande']] = commande

                    # Persist order state in Redis (minimal fields)
                    order_key = f"order:{commande['id_commande']}"
                    try:
                        self.redis_client.hset(order_key, mapping={
                            'status': 'pending',
                            'id_client': commande.get('id_client', ''),
                            'restaurant_nom': commande.get('restaurant_nom', ''),
                            'montant_total': str(commande.get('montant_total', '0'))
                        })
                    except Exception:
                        pass
                    
                    # Publier la demande au restaurant
                    self.redis_client.publish(
                        'demandes-restaurants',
                        json.dumps(demande_restaurant, ensure_ascii=False)
                    )
                    
                    print(f"⏳ En attente de confirmation du restaurant...\n")
                    
                except Exception as e:
                    print(f"❌ Erreur traitement commande: {e}")

    def ecouter_reponses_restaurants(self):
        """Écoute les réponses des restaurants (accepté/refusé)"""
        self.pubsub_restaurants.subscribe('reponses-restaurants')
        print("👂 En écoute des réponses restaurants...\n")
        
        for message in self.pubsub_restaurants.listen():
            if message['type'] == 'message':
                try:
                    reponse = json.loads(message['data'])
                    id_commande = reponse['id_commande']
                    statut = reponse['statut']
                    
                    # Récupérer la commande en attente
                    if id_commande not in self.commandes_en_attente_resto:
                        continue
                    
                    commande = self.commandes_en_attente_resto[id_commande]
                    
                    if statut == "accepte":
                        print(f"\n✅ RESTAURANT ACCEPTE: {id_commande[-8:]}")
                        print(f"   🏪 {reponse['restaurant_nom'][:40]}")
                        print(f"   ⏱️  Temps préparation: {reponse.get('temps_preparation', 15)}min")
                        
                        # Retirer de la liste d'attente
                        del self.commandes_en_attente_resto[id_commande]
                        
                        # MAINTENANT diffuser l'offre aux livreurs
                        offre = {
                            "id_commande": commande['id_commande'],
                            "restaurant_nom": commande['restaurant_nom'],
                            "restaurant_adresse": commande['restaurant_adresse'],
                            "adresse_livraison": commande['adresse_livraison'],
                            "remuneration_livreur": commande['remuneration_livreur'],
                            "frais_livraison": commande.get('frais_livraison', 2.99),
                            "premium": commande.get('premium', False)
                        }
                        
                        message_offre = json.dumps(offre, ensure_ascii=False)
                        # mark prepared/ready in order state
                        try:
                            self.redis_client.hset(f"order:{id_commande}", mapping={
                                'status': 'ready',
                                'temps_preparation': str(reponse.get('temps_preparation', ''))
                            })
                        except Exception:
                            pass

                        # record offers sent timestamp and publish offers
                        try:
                            self.redis_client.hset(f"order:{id_commande}", mapping={'offers_sent_ts': str(time.time())})
                        except Exception:
                            pass

                        # If configured, select a subset of livreurs and publish privately.
                        nb_livreurs = 0
                        try:
                            if self.use_private_offers:
                                # Prefer GEO selection if coordinates are available
                                ids = []
                                # check for coordinates in commande or in restaurant response
                                resto_lon = None
                                resto_lat = None
                                if isinstance(commande, dict):
                                    resto_lon = commande.get('restaurant_lon') or commande.get('restaurant_longitude')
                                    resto_lat = commande.get('restaurant_lat') or commande.get('restaurant_latitude')
                                # fallback to response fields if present
                                resto_lon = resto_lon or reponse.get('restaurant_lon') if isinstance(reponse, dict) else resto_lon
                                resto_lat = resto_lat or reponse.get('restaurant_lat') if isinstance(reponse, dict) else resto_lat

                                if resto_lon and resto_lat:
                                    try:
                                        ids = self.select_livreurs_by_geo(float(resto_lon), float(resto_lat), rayon_m=self.geo_search_radius_m, k=self.targets_per_offer)
                                    except Exception:
                                        ids = []

                                if not ids:
                                    ids = self.select_livreurs_from_set(k=self.targets_per_offer)

                                if ids:
                                    for lid in ids:
                                        try:
                                            self.redis_client.publish(f"offres-livreur:{lid}", message_offre)
                                            nb_livreurs += 1
                                        except Exception:
                                            pass

                        except Exception:
                            # on error, fallback to global publish
                            nb_livreurs = 0

                        # If not using private offers, or selection failed, fallback to broadcast
                        if not self.use_private_offers or nb_livreurs == 0:
                            try:
                                nb_livreurs = self.redis_client.publish('offres-courses', message_offre)
                            except Exception:
                                nb_livreurs = 0

                        print(f"📢 Offre diffusée à {nb_livreurs} livreur(s)\n")

                        # schedule an auto-cancel if no livreur accepts in timeout (seconds)
                        try:
                            self.schedule_no_driver_timeout(id_commande, timeout_seconds=5)
                        except Exception:
                            pass
                        
                    else:  # refusé
                        print(f"\n❌ RESTAURANT REFUSE: {id_commande[-8:]}")
                        print(f"   🏪 {reponse['restaurant_nom'][:40]}")
                        print(f"   ⚠️  Raison: {reponse.get('raison', 'Non disponible')}")
                        
                        # Retirer de la liste d'attente
                        del self.commandes_en_attente_resto[id_commande]
                        
                        # Mark cancelled and refund client
                        try:
                            self.redis_client.hset(f"order:{id_commande}", mapping={
                                'status': 'cancelled',
                                'cancel_reason': reponse.get('raison', 'Restaurant indisponible'),
                                'refunded_client': 'true'
                            })
                        except Exception:
                            pass

                        # Notifier le client de l'annulation + remboursement
                        # include the refunded amount when available
                        montant = commande.get('montant_total') if isinstance(commande, dict) else None
                        notification_client = {
                            "type": "commande_annulee",
                            "id_commande": id_commande,
                            "raison": reponse.get('raison', 'Restaurant indisponible'),
                            "message": f"❌ Commande annulée : {reponse.get('raison')}",
                            "remboursement": "client",
                            "montant_rembourse": montant
                        }
                        self.redis_client.publish('notifications-clients', json.dumps(notification_client, ensure_ascii=False))
                        print(f"📱 Client notifié de l'annulation et remboursement\n")
                        
                except Exception as e:
                    print(f"❌ Erreur traitement réponse restaurant: {e}")
    
    def ecouter_reponses_livreurs(self):
        """Écoute les réponses des livreurs et attribue la course"""
        self.pubsub_reponses.subscribe('reponses-livreurs')
        print("👂 En écoute des réponses livreurs...\n")
        
        for message in self.pubsub_reponses.listen():
            if message['type'] == 'message':
                try:
                    candidature = json.loads(message['data'])
                    id_commande = candidature['id_commande']
                    id_livreur = candidature['id_livreur']
                    
                    # Vérifier si déjà attribuée
                    if id_commande in self.commandes_attribuees:
                        print(f"   ⚠️  {id_livreur} trop tard (déjà attribuée)")
                        continue
                    
                    # Attribution
                    self.commandes_attribuees.add(id_commande)
                    
                    print(f"\n✅ ATTRIBUTION")
                    print(f"   🚴 Livreur: {id_livreur}")
                    print(f"   📦 Commande: {id_commande[-8:]}")
                    
                    # Générer un numéro de téléphone pour le livreur
                    numero_livreur = f"06 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
                    
                    # Notifier le livreur
                    notification_livreur = {
                        "type": "attribution",
                        "id_commande": id_commande,
                        "message": "🎉 Course attribuée !"
                    }
                    self.redis_client.publish(
                        f"notifications-livreur:{id_livreur}",
                        json.dumps(notification_livreur, ensure_ascii=False)
                    )
                    
                    # Notifier le CLIENT avec les infos du livreur
                    notification_client = {
                        "type": "attribution_confirmee",
                        "id_commande": id_commande,
                        "livreur_nom": id_livreur,
                        "livreur_telephone": numero_livreur,
                        "message": f"🚴 Votre livreur {id_livreur} arrive bientôt !"
                    }
                    # Publier sur le canal général (tous les clients peuvent voir)
                    nb_clients = self.redis_client.publish(
                        'notifications-clients',
                        json.dumps(notification_client, ensure_ascii=False)
                    )
                    # persist assignment
                    try:
                        self.redis_client.hset(f"order:{id_commande}", mapping={
                            'status': 'assigned',
                            'assigned_livreur': id_livreur
                        })
                    except Exception:
                        pass
                    
                    print(f"   ✅ Notification envoyée à {id_livreur}")
                    print(f"   📱 Info livreur envoyée à {nb_clients} client(s): {numero_livreur}\n")
                    
                except Exception as e:
                    print(f"❌ Erreur traitement réponse: {e}")

    def select_livreurs_from_set(self, k=5):
        """Select up to k livreur IDs from Redis set 'livreurs:disponibles'.
        Returns list of IDs (possibly empty). Non-destructive and random.
        """
        try:
            membres = list(self.redis_client.smembers('livreurs:disponibles') or [])
            if not membres:
                return []
            random.shuffle(membres)
            return membres[:k]
        except Exception:
            return []

    def select_livreurs_by_geo(self, lon, lat, rayon_m=5000, k=5):
        """Select up to k nearest livreur IDs using Redis GEO index 'livreurs:geo'.
        Requires livreurs to maintain GEOADD entries.
        Returns list of IDs (possibly empty).
        """
        try:
            # georadius returns list of ids sorted by distance when sort='ASC'
            ids = self.redis_client.georadius('livreurs:geo', lon, lat, rayon_m, unit='m', sort='ASC', count=k)
            return ids or []
        except Exception:
            return []

    def ecouter_annulations_clients(self):
        """Écoute et traite les demandes d'annulation des clients."""
        self.pubsub_annulations.subscribe(self.CHANNEL_ANNULATIONS)
        print("👂 En écoute des annulations clients...\n")

        for message in self.pubsub_annulations.listen():
            if message['type'] != 'message':
                continue
            try:
                data = json.loads(message['data'])
                id_commande = data.get('id_commande')
                id_client = data.get('id_client')
                raison = data.get('raison', 'annulation client')
                if not id_commande:
                    continue
                self.traiter_annulation(id_commande, id_client, raison)
            except Exception as e:
                print(f"❌ Erreur traitement annulation: {e}")

    def traiter_annulation(self, id_commande, id_client=None, raison='annulation client'):
        """Traitement minimal et sûr des annulations :
        - annulation immédiate si status pending/waiting
        - si status ready/prepared et aucun livreur assigné -> annulation après préparation (flags refunds)
        - sinon, on ignore (déjà assignée ou en livraison)
        """
        order_key = f"order:{id_commande}"
        try:
            order = self.redis_client.hgetall(order_key) or {}
        except Exception:
            order = {}

        status = (order.get('status') or '').lower()

        if status in ('', 'pending', 'waiting_for_resto'):
            # immediate cancellation, refund client
            try:
                self.redis_client.hset(order_key, mapping={
                    'status': 'cancelled',
                    'cancel_reason': raison,
                    'refunded_client': 'true'
                })
            except Exception:
                pass

            payload = {"type": "annulation_confirmee", "id_commande": id_commande, "raison": raison, "remboursement": "client"}
            # Publish both to the private client channel (if known) and to the general notifications channel
            try:
                self.redis_client.publish('notifications-clients', json.dumps(payload, ensure_ascii=False))
            except Exception:
                pass
            if id_client:
                try:
                    canal_client = f"{self.CHANNEL_CONFIRMATION_CLIENT}:{id_client}"
                    self.redis_client.publish(canal_client, json.dumps(payload, ensure_ascii=False))
                except Exception:
                    pass
            print(f"✅ Annulation immédiate traitée pour {id_commande}")
            return

        if status in ('prepared', 'ready', 'waiting_for_livreur'):
            assigned = order.get('assigned_livreur')
            if not assigned:
                try:
                    self.redis_client.hset(order_key, mapping={
                        'status': 'cancelled',
                        'cancel_reason': 'no_livreur_after_preparation',
                        'refunded_restaurant': 'true',
                        'refunded_client': 'true'
                    })
                except Exception:
                    pass
                # notify restaurant (if known) and client
                resto_nom = order.get('restaurant_nom')
                if resto_nom:
                    # best effort publish to restaurant-specific channel
                    try:
                        self.redis_client.publish(f"notifications-restaurant:{resto_nom}", json.dumps({"type": "annulation_apres_preparation", "id_commande": id_commande}, ensure_ascii=False))
                    except Exception:
                        pass
                payload = {"type": "annulation_apres_preparation", "id_commande": id_commande, "remboursement": "client+restaurant"}
                # publish to general client notifications and to private client channel if present
                try:
                    self.redis_client.publish('notifications-clients', json.dumps(payload, ensure_ascii=False))
                except Exception:
                    pass
                if id_client:
                    try:
                        canal_client = f"{self.CHANNEL_CONFIRMATION_CLIENT}:{id_client}"
                        self.redis_client.publish(canal_client, json.dumps(payload, ensure_ascii=False))
                    except Exception:
                        pass
                print(f"✅ Annulation après préparation traitée pour {id_commande} (remboursements appliqués)")
                return

        # Else, assigned or in delivery — do not auto-cancel
        print(f"ℹ️ Annulation ignorée pour {id_commande} — status={status}")

    def schedule_no_driver_timeout(self, id_commande, timeout_seconds=20):
        """Schedule a background check: if no driver accepts within timeout, cancel and refund.

        This starts a daemon thread that sleeps `timeout_seconds` and then checks order state.
        If no 'assigned_livreur' is present, it will mark the order cancelled and publish
        refund notifications to restaurant and client.
        """
        def _worker():
            try:
                time.sleep(timeout_seconds)
                order = self.redis_client.hgetall(f"order:{id_commande}") or {}
                status = (order.get('status') or '').lower()
                assigned = order.get('assigned_livreur')
                if assigned or status == 'assigned':
                    # already assigned, nothing to do
                    return

                # no driver accepted in time -> cancel and refund both
                try:
                    self.redis_client.hset(f"order:{id_commande}", mapping={
                        'status': 'cancelled',
                        'cancel_reason': 'no_livreur_after_offers',
                        'refunded_restaurant': 'true',
                        'refunded_client': 'true'
                    })
                except Exception:
                    pass

                # notify restaurant (if known) and client
                resto_nom = order.get('restaurant_nom')
                if resto_nom:
                    try:
                        self.redis_client.publish(f"notifications-restaurant:{resto_nom}", json.dumps({"type": "annulation_no_livreur", "id_commande": id_commande, "message": "Aucun livreur n'a accepté la course, remboursement effectué au restaurant."}, ensure_ascii=False))
                    except Exception:
                        pass

                client_id = order.get('id_client')
                payload = {"type": "annulation_no_livreur", "id_commande": id_commande, "remboursement": "client+restaurant", "message": "Aucun livreur n'a accepté la course, remboursement effectué"}
                if client_id:
                    try:
                        self.redis_client.publish(f"{self.CHANNEL_CONFIRMATION_CLIENT}:{client_id}", json.dumps(payload, ensure_ascii=False))
                    except Exception:
                        pass
                else:
                    try:
                        self.redis_client.publish('notifications-clients', json.dumps(payload, ensure_ascii=False))
                    except Exception:
                        pass

                print(f"⚠️ Auto-cancel (no driver) performed for {id_commande}")
            except Exception as e:
                print(f"❌ Error in schedule_no_driver_timeout worker for {id_commande}: {e}")

        t = Thread(target=_worker, daemon=True)
        t.start()
    
    def demarrer(self):
        print("\n" + "="*60)
        print("👔 MANAGER AUTOMATIQUE")
        print("="*60 + "\n")
        
        try:
            self.redis_client.ping()
            print("✅ Connecté à Redis\n")
        except:
            print("❌ Redis non accessible")
            return
        
        # Lancer les threads d'écoute
        thread_commandes = Thread(target=self.ecouter_nouvelles_commandes, daemon=True)
        thread_restaurants = Thread(target=self.ecouter_reponses_restaurants, daemon=True)
        thread_reponses = Thread(target=self.ecouter_reponses_livreurs, daemon=True)
        thread_annulations = Thread(target=self.ecouter_annulations_clients, daemon=True)
        
        thread_commandes.start()
        thread_restaurants.start()
        thread_reponses.start()
        thread_annulations.start()
        
        print("🚀 Manager actif (Ctrl+C pour arrêter)\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Manager arrêté")
            print(f"📊 {len(self.commandes_attribuees)} commandes attribuées\n")

if __name__ == "__main__":
    manager = ManagerAutomatique()
    manager.demarrer()

"""Platform simulator with Change Streams
Monitors new orders using Change Streams and orchestrates the complete flow.
"""
import os
import time
from datetime import datetime, timezone
from pymongo import MongoClient
from pathlib import Path
import threading

# Charger les variables d'environnement depuis .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("⚠️  python-dotenv non installé")

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'Ubereats')

print()
print("=" * 70)
print("  🏢 PLATFORM SIMULATOR - Orchestrateur (Change Streams)")
print("=" * 70)
print()
print(f"🔗 Connexion à MongoDB...")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
def _mask_mongo_uri(uri: str) -> str:
    # Mask userinfo (user:pass@) if present for safe printing
    try:
        if '://' in uri and '@' in uri:
            prefix, rest = uri.split('://', 1)
            userinfo, host = rest.split('@', 1)
            return f"{prefix}://***:***@{host}"
    except Exception:
        pass
    return uri

print(f"✅ Connecté à la base: {DB_NAME} (URI: {_mask_mongo_uri(MONGODB_URI)})")
print()
print("🎯 Démarrage de l'orchestrateur avec Change Streams...")
print("   • Écoute en temps réel les nouvelles commandes")
print("   • Envoie requêtes aux restaurants")
print("   • Cherche des livreurs disponibles")
print("   • Assigne les commandes")
print()
print("💡 Appuyez sur Ctrl+C pour arrêter")
print("=" * 70)
print()

def _extract_order_price(doc):
    """Return a float price for an order-like document.
    Tries several common field names and falls back to 0.0.
    """
    if not doc:
        return 0.0
    # Known possible price fields in this codebase
    keys = ['prix_total', 'coût_commande', 'coût_total', 'coût', 'price', 'coût_commande']
    for k in keys:
        if k in doc and doc.get(k) is not None:
            try:
                return float(doc.get(k))
            except Exception:
                try:
                    # Some documents may store nested structures
                    return float(doc.get(k, 0.0))
                except Exception:
                    continue
    # try some common ASCII variants
    if 'cout_total' in doc and doc.get('cout_total') is not None:
        try:
            return float(doc.get('cout_total'))
        except Exception:
            pass
    return 0.0

def wait_for_restaurant_response(numero, rest_id, timeout=60):
    """Wait for restaurant response using Change Streams"""
    pipeline = [
        {
            '$match': {
                'operationType': 'update',
                'fullDocument.numero_commande': numero,
                'fullDocument.id_restaurant': rest_id,
                'fullDocument.status': {'$in': ['accepted', 'rejected']}
            }
        }
    ]
    
    start_time = time.time()
    try:
        # Use full_document='updateLookup' to get the full document after update
        with db.RestaurantRequests.watch(pipeline, full_document='updateLookup', max_await_time_ms=1000) as stream:
            while time.time() - start_time < timeout:
                try:
                    change = stream.try_next()
                    if change is not None:
                        return change['fullDocument']
                    time.sleep(0.1)
                except Exception:
                    time.sleep(0.1)
    except Exception as e:
        print(f"   ⚠️ Erreur Change Stream restaurant: {e}")
    
    return None

def wait_for_livreur_response(numero, livreur_id, timeout=30):
    """Wait for livreur response using Change Streams"""
    pipeline = [
        {
            '$match': {
                'operationType': 'update',
                'fullDocument.numero_commande': numero,
                'fullDocument.id_livreur': livreur_id,
                'fullDocument.status': {'$in': ['accepted', 'rejected']}
            }
        }
    ]
    
    start_time = time.time()
    try:
        # Use full_document='updateLookup' to get the full document after update
        with db.DeliveryRequests.watch(pipeline, full_document='updateLookup', max_await_time_ms=1000) as stream:
            while time.time() - start_time < timeout:
                try:
                    change = stream.try_next()
                    if change is not None:
                        return change['fullDocument']
                    time.sleep(0.1)
                except Exception:
                    time.sleep(0.1)
    except Exception as e:
        print(f"   ⚠️ Erreur Change Stream livreur: {e}")
    
    return None

def notify_client_cancel(numero, id_client, reason):
    """Insert a cancellation notification for the client (simulation)."""
    notification = {
        'numero_commande': numero,
        'id_client': id_client,
        'message': f"Votre commande {numero} a été annulée : {reason}",
        'sent_at': datetime.now(timezone.utc)
    }
    try:
        db.Notifications.insert_one(notification)
    except Exception:
        pass


def record_refund(numero, beneficiary, amount, kind):
    """Record a refund event in the Refunds collection (simulation).
    beneficiary: id_client or id_restaurant
    kind: short code describing refund (eg: 'full_refund_client', 'refund_restaurant_preparation')
    """
    refund = {
        'numero_commande': numero,
        'beneficiary': beneficiary,
        'amount': amount,
        'kind': kind,
        'ts': datetime.now(timezone.utc)
    }
    try:
        db.Refunds.insert_one(refund)
    except Exception:
        pass


def cancel_order_immediate(numero):
    """Cancel the order immediately and refund the client (simulation)."""
    updated = db.Commande.find_one_and_update(
        {'numero_commande': numero, 'status': {'$ne': 'cancelled'}},
        {'$set': {'status': 'cancelled', 'cancel_reason': 'immediate', 'cancelled_at': datetime.now(timezone.utc)}}
    )
    if updated:
        client_id = updated.get('id_client')
        prix = _extract_order_price(updated)
        try:
            # full refund to client
            record_refund(numero, client_id, prix, 'full_refund_client')
            notify_client_cancel(numero, client_id, 'Annulation immédiate, remboursement effectué.')
        except Exception:
            pass


def watch_cancellations(stop_event):
    """Watch Commande updates for client cancel requests and process them immediately."""
    pipeline = [{'$match': {'operationType': 'update', 'updateDescription.updatedFields.status': 'cancel_requested'}}]
    try:
        with db.Commande.watch(pipeline, full_document='updateLookup') as stream:
            for change in stream:
                if stop_event.is_set():
                    break
                doc = change.get('fullDocument')
                if doc:
                    numero = doc.get('numero_commande')
                    print(f"   🔔 Annulation demandée pour {numero} (watcher).")
                    try:
                        cancel_order_immediate(numero)
                    except Exception as e:
                        print(f"   ⚠️ Erreur lors de l'annulation immédiate: {e}")
    except Exception as e:
        print(f"   ⚠️ Watcher annulations échoué: {e}")


def select_candidates_for_order(order, k=5, max_distance_m=2000):
    """Return up to k available livreurs prioritized by same city then proximity.
    Expects optional client snapshot with 'coords' == [lng, lat] or 'city'.
    """
    client_snapshot = order.get('client_snapshot', {}) if isinstance(order, dict) else {}
    order_city = client_snapshot.get('city') or order.get('adresse_livraison_city')
    coords = client_snapshot.get('coords') or order.get('coords')
    candidates = []
    try:
        if order_city:
            candidates = list(db.Livreur.find({'statut': 'disponible', 'city': order_city}).limit(k))
            if len(candidates) >= k:
                return candidates[:k]
        if coords and isinstance(coords, (list, tuple)) and len(coords) == 2:
            geo_query = {
                'statut': 'disponible',
                'location': {'$near': {'$geometry': {'type': 'Point', 'coordinates': coords}, '$maxDistance': max_distance_m}}
            }
            candidates = list(db.Livreur.find(geo_query).limit(k))
            if candidates:
                return candidates[:k]
        candidates = list(db.Livreur.find({'statut': 'disponible'}).limit(k))
    except Exception:
        # fallback: simple query
        candidates = list(db.Livreur.find({'statut': 'disponible'}).limit(k))
    return candidates[:k]


def wait_for_any_livreur_response(numero, candidate_ids, timeout=30):
    """Wait for any candidate to accept/reject using a single Change Stream.
    Returns the fullDocument of the first matching update, or None on timeout/error.
    """
    if not candidate_ids:
        return None
    pipeline = [
        {'$match': {
            'operationType': 'update',
            'fullDocument.numero_commande': numero,
            'fullDocument.id_livreur': {'$in': candidate_ids},
            'fullDocument.status': {'$in': ['accepted', 'rejected']}
        }}
    ]
    start_time = time.time()
    try:
        with db.DeliveryRequests.watch(pipeline, full_document='updateLookup', max_await_time_ms=1000) as stream:
            while time.time() - start_time < timeout:
                try:
                    change = stream.try_next()
                    if change is not None:
                        return change.get('fullDocument')
                    time.sleep(0.1)
                except Exception:
                    time.sleep(0.1)
    except Exception as e:
        print(f"   ⚠️ Erreur Change Stream (candidats): {e}")
    return None

def process_order(order):
    """Process a single order through the complete flow"""
    numero = order['numero_commande']
    rest_id = order.get('id_restaurant')
    
    print()
    print("─" * 70)
    print(f"🔍 NOUVELLE COMMANDE DÉTECTÉE (Change Stream)")
    print("─" * 70)
    print(f"   📦 N° Commande  : {numero}")
    print(f"   🍽️  Restaurant  : {rest_id}")
    print(f"   📤 Action      : Envoi requête au restaurant...")
    print("─" * 70)

    # Check for immediate cancellation (client may have requested before processing)
    current = db.Commande.find_one({'numero_commande': numero})
    if current and current.get('status') == 'cancel_requested':
        print(f"   ⚠️ Commande {numero} annulée immédiatement (request).")
        cancel_order_immediate(numero)
        return

    # Create restaurant request
    req = {
        'numero_commande': numero,
        'id_restaurant': rest_id,
        'status': 'requested',
        'requested_at': datetime.now(timezone.utc)
    }
    db.RestaurantRequests.insert_one(req)
    print(f"   ✅ Requête envoyée")

    # Wait for restaurant response using Change Streams
    print(f"   ⏳ Attente réponse restaurant (max 60s via Change Streams)...")
    response = wait_for_restaurant_response(numero, rest_id, timeout=60)

    if not response or response.get('status') != 'accepted':
        # Formatted rejection block
        print()
        print("─" * 70)
        print("🍽️  RÉPONSE RESTAURANT - REFUS / TIMEOUT")
        print("─" * 70)
        print(f"   📦 Commande : {numero}")
        print(f"   🍽️  Restaurant: {rest_id}")
        print(f"   ⏱️  Réponse   : Aucun / rejet")
        print("   📝 Action    : Mise à jour -> rejected_by_restaurant")
        print("─" * 70)
        db.Commande.update_one({'numero_commande': numero}, {'$set': {'status': 'rejected_by_restaurant'}})
        return

    # Formatted acceptance block
    print()
    print("─" * 70)
    print("🍽️  RÉPONSE RESTAURANT - ACCEPTÉE")
    print("─" * 70)
    print(f"   📦 Commande : {numero}")
    print(f"   🍽️  Restaurant: {rest_id}")
    print(f"   ✅ Statut    : accepted")
    print("   📝 Action    : Recherche de livreurs disponibles...")
    print("─" * 70)

    # Find available livreur
    # Before searching livreur, check again if client cancelled during preparation
    current = db.Commande.find_one({'numero_commande': numero})
    if current and current.get('status') == 'cancel_requested':
        print(f"   ⚠️ Commande {numero} annulée après préparation (request).")
        # Refund restaurant for preparation and full refund to client (simulated rules)
        prix_total = _extract_order_price(current)
        prix_prep = prix_total * 0.6 if prix_total else 0.0
        client_id = current.get('id_client')
        try:
            record_refund(numero, rest_id, prix_prep, 'refund_restaurant_preparation')
            record_refund(numero, client_id, prix_total, 'full_refund_client')
        except Exception:
            pass
        db.Commande.update_one({'numero_commande': numero}, {'$set': {'status': 'cancelled', 'cancel_reason': 'cancel_after_preparation', 'cancelled_at': datetime.now(timezone.utc)}})
        notify_client_cancel(numero, client_id, 'Annulation après préparation, remboursements effectués.')
        return

    # --- Select multiple candidates (top-K) and send DeliveryRequests to each ---
    candidates = select_candidates_for_order(current or order, k=5, max_distance_m=2000)
    # Debug: print number of candidates found
    try:
        print(f"   🔎 Candidates found: {len(candidates)}")
    except Exception:
        print("   🔎 Candidates found: (unable to determine length)")

    if not candidates:
        # Fallback to legacy behavior: pick any available livreur (maintains previous behavior)
        print(f"   ⚠️ Aucun candidat top-K trouvé pour {numero}, fallback sur recherche simple (find_one)")
        livreur = db.Livreur.find_one({'statut': 'disponible'})
        if not livreur:
            print(f"   ⚠️ Aucun livreur disponible pour {numero}")
            db.Commande.update_one({'numero_commande': numero}, {'$set': {'status': 'waiting_for_livreur'}})
            return

        # Create single delivery request and wait for the single livreur response (legacy path)
        # record the time we sent the delivery request(s) for metrics
        delivery_request_ts = datetime.now(timezone.utc)
        try:
            db.Commande.update_one({'numero_commande': numero}, {'$set': {'delivery_request_ts': delivery_request_ts}})
        except Exception:
            pass

        fb_prix = _extract_order_price(current) if current else _extract_order_price(order)
        delivery_req = {
            'numero_commande': numero,
            'id_livreur': livreur['id_livreur'],
            'status': 'requested',
            'requested_at': delivery_request_ts,
            'offered_price': max(1.0, round(fb_prix * 0.15, 2))
        }
        db.DeliveryRequests.insert_one(delivery_req)
        print(f"   📤 Requête envoyée au livreur {livreur['id_livreur']} (fallback)")
        print(f"   ⏳ Attente réponse livreur (max 30s via Change Streams)...")
        dr = wait_for_livreur_response(numero, livreur['id_livreur'], timeout=30)

        if not dr or dr.get('status') != 'accepted':
            print(f"   ❌ Livreur n'a pas accepté pour {numero} (fallback)")
            db.Commande.update_one({'numero_commande': numero}, {'$set': {'status': 'waiting_for_livreur'}})
            return

        livreur_doc = db.Livreur.find_one({'id_livreur': livreur['id_livreur']}) or livreur
        assigned_livreur = livreur_doc['id_livreur']
    else:
        # compute offered price for this delivery (example: 15% of order, min 1.0)
        prix_total = _extract_order_price(current) if current else _extract_order_price(order)
        offered_fee = max(1.0, round(prix_total * 0.15, 2))

        # record a single delivery_request_ts for the whole candidate batch
        delivery_request_ts = datetime.now(timezone.utc)
        try:
            db.Commande.update_one({'numero_commande': numero}, {'$set': {'delivery_request_ts': delivery_request_ts}})
        except Exception:
            pass

        candidate_ids = []
        for livreur in candidates:
            try:
                candidate_ids.append(livreur['id_livreur'])
                delivery_req = {
                    'numero_commande': numero,
                    'id_livreur': livreur['id_livreur'],
                    'status': 'requested',
                    'requested_at': delivery_request_ts,
                    'offered_price': offered_fee,
                    'city': (order.get('client_snapshot') or {}).get('city')
                }
                db.DeliveryRequests.insert_one(delivery_req)
            except Exception:
                continue
        print(f"   📤 Requêtes envoyées à {len(candidate_ids)} livreurs (fee={offered_fee})")

        # Wait for any candidate to respond using a single Change Stream
        print(f"   ⏳ Attente réponse(s) livreurs (max 30s via Change Streams)...")
        dr = wait_for_any_livreur_response(numero, candidate_ids, timeout=30)

        if not dr or dr.get('status') != 'accepted':
            print(f"   ❌ Aucun livreur n'a accepté pour {numero} (top-{len(candidate_ids)} tentatives)")
            db.Commande.update_one({'numero_commande': numero}, {'$set': {'status': 'waiting_for_livreur'}})
            return

        # If accepted, get the accepted livreur id and continue assignment
        accepted_livreur_id = dr.get('id_livreur')
        livreur_doc = db.Livreur.find_one({'id_livreur': accepted_livreur_id}) or {}
        assigned_livreur = accepted_livreur_id

    # Update commande and livreur records
    db.Commande.update_one(
        {'numero_commande': numero},
        {'$set': {'status': 'en_cours', 'id_livreur': assigned_livreur}}
    )
    db.Livreur.update_one(
        {'id_livreur': assigned_livreur},
        {'$set': {'statut': 'en_course', 'numero_commande': numero}}
    )

    # Record assignment metrics (assignment delay) if we have a delivery_request_ts
    try:
        assigned_at = datetime.now(timezone.utc)
        cmd = db.Commande.find_one({'numero_commande': numero})
        dr_ts = cmd.get('delivery_request_ts') if cmd else None
        if dr_ts:
            try:
                assignment_delay_ms = int((assigned_at - dr_ts).total_seconds() * 1000)
            except Exception:
                assignment_delay_ms = None
        else:
            assignment_delay_ms = None

        metric = {
            'numero_commande': numero,
            'delivery_request_ts': dr_ts,
            'assigned_at': assigned_at,
            'assignment_delay_ms': assignment_delay_ms,
            'ts': datetime.now(timezone.utc)
        }
        try:
            db.Metrics.insert_one(metric)
        except Exception:
            pass
    except Exception:
        pass

    # Pretty assignment block
    prenom = livreur_doc.get('Prénom') or livreur_doc.get('prenom')
    nom = livreur_doc.get('Nom') or livreur_doc.get('nom')
    if prenom and nom:
        livreur_name = f"{prenom} {nom}"
    elif prenom:
        livreur_name = f"{prenom} ({assigned_livreur})"
    elif nom:
        livreur_name = f"{nom} ({assigned_livreur})"
    else:
        livreur_name = str(assigned_livreur)

    print()
    print("─" * 70)
    print("🚀 ATTRIBUTION DE COMMANDE AU LIVREUR")
    print("─" * 70)
    print(f"   📦 Commande : {numero}")
    print(f"   🧑‍🚚 Livreur  : {assigned_livreur} ({livreur_name})")
    if livreur_doc.get('Téléphone') or livreur_doc.get('telephone'):
        phone = livreur_doc.get('Téléphone') or livreur_doc.get('telephone')
        print(f"   📞 Téléphone: {phone}")
    print(f"   ✅ Statut    : en_cours")
    print("   📝 Action    : Commande assignée et livreur notifié")
    print("─" * 70)

    # Send enriched notification to client
    prenom = livreur_doc.get('Prénom') or livreur_doc.get('prenom')
    nom = livreur_doc.get('Nom') or livreur_doc.get('nom')
    if prenom and nom:
        livreur_name = f"{prenom} {nom}"
    elif prenom:
        livreur_name = f"{prenom} ({assigned_livreur})"
    elif nom:
        livreur_name = f"{nom} ({assigned_livreur})"
    else:
        livreur_name = str(assigned_livreur)

    livreur_phone = livreur_doc.get('Téléphone') or livreur_doc.get('telephone')
    message = f"Votre commande {numero} a été prise en charge par le livreur {livreur_name} (id: {assigned_livreur})"
    if livreur_phone:
        message += f" - Tel: {livreur_phone}"

    notification = {
        'numero_commande': numero,
        'id_client': order.get('id_client'),
        'message': message,
        'sent_at': datetime.now(timezone.utc)
    }
    db.Notifications.insert_one(notification)
    print(f"   ✉️ Notification envoyée au client {order.get('id_client')}")

try:
    # Use Change Streams to watch for new orders
    print("🔄 Écoute des nouvelles commandes via Change Streams...")
    print()
    
    # Watch for inserts with status='pending_request'
    pipeline = [
        {
            '$match': {
                'operationType': 'insert',
                'fullDocument.status': 'pending_request'
            }
        }
    ]
    
    # Start a background watcher to process cancel requests in real time
    stop_event = threading.Event()
    threading.Thread(target=watch_cancellations, args=(stop_event,), daemon=True).start()

    with db.Commande.watch(pipeline) as stream:
        for change in stream:
            order = change.get('fullDocument')
            if order:
                # Process each order in a separate thread to handle multiple orders concurrently
                threading.Thread(target=process_order, args=(order,), daemon=True).start()

except KeyboardInterrupt:
    print('\n[PLATFORM] Stopped by user')
finally:
    client.close()

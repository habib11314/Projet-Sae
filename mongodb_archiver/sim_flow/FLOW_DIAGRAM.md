# 🎬 Flux de simulation - Diagramme détaillé

## Vue d'ensemble du système

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SIMULATION MULTI-TERMINAUX                           │
│                    4 processus indépendants                             │
└─────────────────────────────────────────────────────────────────────────┘

     [MongoDB Atlas/Local]
              │
    ┌─────────┴─────────┐
    │    Collections    │
    │  - Commande       │
    │  - Client         │
    │  - Restaurant     │
    │  - Menu           │
    │  - Livreur        │
    │  - Requests       │
    │  - Notifications  │
    └───────┬───────────┘
            │
    ┌───────┴───────────────────────────────────────────┐
    │                                                    │
┌───▼────┐  ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
│Terminal│  │Terminal │  │Terminal │  │Terminal │
│   1    │  │   2     │  │   3     │  │   4     │
│ CLIENT │  │PLATFORM │  │RESTAU   │  │LIVREUR  │
└────────┘  └─────────┘  └─────────┘  └─────────┘
```

## Flux détaillé étape par étape

### Étape 1: Création de commande

```
┌──────────────────────────────────────────────────────┐
│ Terminal 1: CLIENT                                   │
└──────────────────────────────────────────────────────┘

1. Sélectionne aléatoirement:
   ├─ Un client (collection Client)
   ├─ Un restaurant (collection Restaurants)
   └─ Un menu (collection Menu)

2. Crée document Commande:
   {
     numero_commande: "SIM-1729089234-5678",
     id_client: "CLI-00023",
     id_restaurant: "RES-00001",
     id_menu: "MEN-00045",
     status: "pending_request",  ◀── État initial
     date_commande: 2025-10-16T14:30:00Z,
     ...
   }

3. Insère dans MongoDB.Commande

4. Boucle d'écoute (polling):
   while (status != final):
     ├─ Lit document toutes les 1s
     ├─ Détecte changements de status
     └─ Affiche: "status changed: X -> Y"

   États finaux:
   - 'livrée'
   - 'annulée'
   - 'rejected_by_restaurant'
```

### Étape 2: Platform détecte et envoie au restaurant

```
┌──────────────────────────────────────────────────────┐
│ Terminal 2: PLATFORM                                 │
└──────────────────────────────────────────────────────┘

1. Polling sur collection Commande:
   while True:
     order = find_one({ status: "pending_request" })
     if order:
       break

2. Crée RestaurantRequest:
   {
     numero_commande: "SIM-1729089234-5678",
     id_restaurant: "RES-00001",
     status: "requested",  ◀── Attend réponse
     requested_at: now()
   }

3. Insère dans MongoDB.RestaurantRequests

4. Attend réponse (polling 60s max):
   for i in range(60):
     response = find_one({
       numero_commande: "SIM-...",
       status: {"$in": ["accepted", "rejected"]}
     })
     if response:
       break
     sleep(1)

5. Si rejected ou timeout:
   └─ Update Commande.status = "rejected_by_restaurant"
   └─ FIN

6. Si accepted:
   └─ Continue à étape suivante ➜
```

### Étape 3: Restaurant accepte/refuse

```
┌──────────────────────────────────────────────────────┐
│ Terminal 3: RESTAURANT                               │
└──────────────────────────────────────────────────────┘

1. Polling sur RestaurantRequests:
   while True:
     req = find_one({ status: "requested" })
     if req:
       break

2. Décision aléatoire:
   accepted = random() < RESTAURANT_ACCEPT_RATE
   └─ Par défaut: 80% d'acceptation

3. Update RestaurantRequest:
   {
     status: "accepted" ou "rejected",
     responded_at: now()
   }

4. Retour à Platform (étape 2) ➜
```

### Étape 4: Platform cherche un livreur

```
┌──────────────────────────────────────────────────────┐
│ Terminal 2: PLATFORM (suite)                         │
└──────────────────────────────────────────────────────┘

1. Cherche livreur disponible:
   livreur = find_one({ statut: "disponible" })

2. Si aucun disponible:
   └─ Update Commande.status = "waiting_for_livreur"
   └─ FIN (ou retry)

3. Si disponible, crée DeliveryRequest:
   {
     numero_commande: "SIM-1729089234-5678",
     id_livreur: "LIV-00012",
     status: "requested",  ◀── Attend réponse
     requested_at: now()
   }

4. Insère dans MongoDB.DeliveryRequests

5. Attend réponse livreur (30s max):
   for i in range(30):
     dr = find_one({
       numero_commande: "SIM-...",
       status: {"$in": ["accepted", "rejected"]}
     })
     if dr:
       break
     sleep(1)

6. Si rejected ou timeout:
   └─ Update Commande.status = "waiting_for_livreur"
   └─ FIN

7. Si accepted:
   └─ Continue à étape suivante ➜
```

### Étape 5: Livreur accepte/refuse

```
┌──────────────────────────────────────────────────────┐
│ Terminal 4: LIVREUR                                  │
└──────────────────────────────────────────────────────┘

1. Polling sur DeliveryRequests:
   while True:
     req = find_one({ status: "requested" })
     if req:
       break

2. Décision aléatoire:
   accepted = random() < LIVREUR_ACCEPT_RATE
   └─ Par défaut: 70% d'acceptation

3. Update DeliveryRequest:
   {
     status: "accepted" ou "rejected",
     responded_at: now()
   }

4. Si accepted:
   └─ Update Livreur.statut = "en_course"

5. Retour à Platform (étape 4) ➜
```

### Étape 6: Platform finalise et notifie

```
┌──────────────────────────────────────────────────────┐
│ Terminal 2: PLATFORM (finalisation)                  │
└──────────────────────────────────────────────────────┘

1. Update Commande:
   {
     status: "en_cours",
     id_livreur: "LIV-00012"
   }

2. Crée Notification:
   {
     numero_commande: "SIM-1729089234-5678",
     id_client: "CLI-00023",
     message: "Votre commande a été assignée au livreur LIV-00012",
     sent_at: now()
   }

3. Insère dans MongoDB.Notifications

4. Client (Terminal 1) détecte changement ✓
```

### Étape 7: Client reçoit notification

```
┌──────────────────────────────────────────────────────┐
│ Terminal 1: CLIENT (fin)                             │
└──────────────────────────────────────────────────────┘

1. Polling détecte changement:
   old_status: "pending_request"
   new_status: "en_cours"

2. Affiche:
   "[CLIENT] Order SIM-... status changed: pending_request -> en_cours"

3. Affiche:
   "[CLIENT] Final status for SIM-...: en_cours"

4. FIN du cycle
   └─ Client crée une nouvelle commande après 3s
```

## Collections MongoDB créées

```
┌─────────────────────────────────────────────────────┐
│ Collections lues (doivent exister)                  │
├─────────────────────────────────────────────────────┤
│ Client        │ Données clients (Nom, Email, etc.)  │
│ Restaurants   │ Restaurants (name, address, etc.)   │
│ Menu          │ Plats disponibles (name, price)     │
│ Livreur       │ Livreurs (statut: disponible/...)   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Collections créées/modifiées                        │
├─────────────────────────────────────────────────────┤
│ Commande            │ Commandes créées               │
│ RestaurantRequests  │ Demandes aux restaurants       │
│ DeliveryRequests    │ Demandes aux livreurs          │
│ Notifications       │ Notifications clients          │
└─────────────────────────────────────────────────────┘
```

## États de la commande

```
pending_request ──┐
                  ├──▶ [Restaurant]
                  │       │
                  │       ├─▶ rejected ──▶ rejected_by_restaurant (FIN)
                  │       │
                  │       └─▶ accepted ──┐
                  │                      ├──▶ [Livreur Search]
                  │                      │       │
                  │                      │       ├─▶ no livreur ──▶ waiting_for_livreur (FIN)
                  │                      │       │
                  │                      │       └─▶ livreur found ──┐
                  │                      │                            ├──▶ [Livreur]
                  │                      │                            │       │
                  │                      │                            │       ├─▶ rejected ──▶ waiting_for_livreur (FIN)
                  │                      │                            │       │
                  │                      │                            │       └─▶ accepted ──▶ en_cours (FIN)
                  │                      │                            │
                  └──────────────────────┴────────────────────────────┘
```

## Timing et performances

```
Temps moyens (estimés):

┌────────────────────────────────────────┬──────────┐
│ Étape                                  │ Durée    │
├────────────────────────────────────────┼──────────┤
│ Client crée commande                   │ < 1s     │
│ Platform détecte (polling)             │ 0-1s     │
│ Platform → Restaurant request          │ < 0.5s   │
│ Restaurant décide                      │ 0-1s     │
│ Platform → Cherche livreur             │ < 0.5s   │
│ Platform → Livreur request             │ < 0.5s   │
│ Livreur décide                         │ 0-1s     │
│ Platform finalise + notifie            │ < 1s     │
│ Client détecte notification (polling)  │ 0-1s     │
├────────────────────────────────────────┼──────────┤
│ TOTAL (commande acceptée)              │ 3-7s     │
└────────────────────────────────────────┴──────────┘
```

## Amélioration possible: Change Streams

Remplacer polling par Change Streams MongoDB:
- Latence < 100ms au lieu de 1s
- Moins de charge sur MongoDB
- Réactivité instantanée

```python
# Exemple pour Client
with db.Commande.watch([{'$match': {'fullDocument.numero_commande': numero}}]) as stream:
    for change in stream:
        print(f"Status changed: {change['fullDocument']['status']}")
```

---

**💡 Cette architecture est scalable et peut gérer des centaines de commandes/minute**

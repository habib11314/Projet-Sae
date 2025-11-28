# 🎯 SIMULATIONS AVANCÉES - Guide Complet

## 📋 Vue d'ensemble

Ce projet contient maintenant **3 niveaux de simulation** du système de livraison Redis :

### 1️⃣ **demo_simple.py** - Démo Basique
✅ Simulation séquentielle simple  
✅ 3 commandes prédéfinies  
✅ Idéal pour comprendre le concept  

### 2️⃣ **simulation_realiste.py** - Simulation Réaliste ⭐ RECOMMANDÉ
✅ **Gestion des états des livreurs** (disponible/en_livraison)  
✅ **Scénarios aléatoires ultra-réalistes**  
✅ **Commentaires clients aléatoires** ("Frites froides", "Excellent service", etc.)  
✅ **Refus/Acceptation aléatoire** par les livreurs  
✅ **Temps de livraison simulé** (10-30 secondes)  
✅ **Attribution intelligente** (pas de double livraison)  

### 3️⃣ **simulation_multithreading.py** - Simulation Avancée
✅ **Multi-threading** - Plusieurs commandes simultanées  
✅ **Statistiques en temps réel** toutes les 5 secondes  
✅ **Gestion concurrente** thread-safe  
✅ **Scénarios parallèles** réalistes  

---

## 🚀 LANCEMENT DES SIMULATIONS

### Prérequis
```powershell
# 1. Démarrer Redis (dans un terminal séparé)
cd C:\Users\PC\Downloads\redis\Redis-x64-5.0.14.1
Start-Process -FilePath ".\redis-server.exe"

# 2. Vérifier que Redis fonctionne
.\redis-cli.exe ping
# Doit afficher: PONG
```

---

### 🎬 OPTION 1 : Simulation Réaliste (RECOMMANDÉ)

```powershell
cd C:\Users\PC\projet-redis-livraison
py simulation_realiste.py
```

**Ce que vous verrez :**

```
📦 NOUVELLE COMMANDE #1234
👤 Client       : Fatima Benali
🏪 Restaurant   : McDonald's
💰 Montant      : 28.50€
📍 Livraison    : 45 Avenue des Champs-Élysées, 75008 Paris
🍽️  Plats       : BigMac, Frites

📢 Offre diffusée à 5 livreur(s) disponible(s)
   ❌ livreur-001 REFUSE (trop loin)
   ❌ livreur-002 REFUSE (pause)
   ✅ livreur-003 ACCEPTE la course

✅ Course attribuée à livreur-003
   📦 livreur-003 → EN LIVRAISON (commande: CMD-...)
⏱️  Temps de livraison estimé: 18s
🚴 livreur-003 en route vers 45 Avenue des Champs-Élysées...

📍 Livraison arrivée !
💬 Commentaire client: "Excellent service !" ⭐⭐⭐⭐⭐
   ✅ livreur-003 → DISPONIBLE (livraison terminée)
✅ LIVRAISON TERMINÉE
```

**Paramètres configurables :**
```python
# Dans le fichier simulation_realiste.py (ligne 468)
NB_LIVREURS = 8   # Nombre de livreurs disponibles
NB_COMMANDES = 15 # Nombre de commandes à simuler
```

---

### 🔥 OPTION 2 : Simulation Multi-threading (Avancé)

```powershell
cd C:\Users\PC\projet-redis-livraison
py simulation_multithreading.py
```

**Différences :**
- ⚡ **Plusieurs commandes traitées en parallèle**
- 📊 **Statistiques en temps réel** toutes les 5 secondes
- 🔄 **Gestion concurrente** des livreurs
- 🎯 **Plus réaliste** (comme une vraie plateforme)

**Statistiques affichées :**
```
📊📊📊📊📊📊📊📊📊📊📊📊📊
STATISTIQUES EN TEMPS RÉEL
📊📊📊📊📊📊📊📊📊📊📊📊📊
✅ Commandes livrées    : 8
🚴 En cours de livraison: 3
❌ Échecs               : 1
🟢 Livreurs disponibles : 6/10
🔴 Livreurs occupés     : 4/10
📊📊📊📊📊📊📊📊📊📊📊📊📊
```

---

## 🎲 SCÉNARIOS ALÉATOIRES IMPLÉMENTÉS

### 1. **Génération de clients aléatoires**
- ✅ Prénoms variés (40 prénoms : Mohammed, Fatima, Pierre, Sophie, etc.)
- ✅ Noms de famille variés (30 noms)
- ✅ **20 adresses réelles** à Paris et Seine-Saint-Denis

### 2. **Restaurants et menus**
- ✅ Chargés depuis `restaurants.json` (50 restaurants)
- ✅ Menus générés automatiquement si absents
- ✅ Attribution aléatoire du restaurant

### 3. **Plats de la commande**
- ✅ Entre 1 et 4 plats par commande
- ✅ Sélection aléatoire dans le menu du restaurant
- ✅ Calcul automatique du montant total

### 4. **Gestion des livreurs**
- ✅ **États : disponible → en_livraison → disponible**
- ✅ **Pas de double attribution** (vérification de disponibilité)
- ✅ **Acceptation aléatoire** (30-80% selon le livreur)
- ✅ **Raisons de refus** : "trop loin", "autre livraison", "pause"

### 5. **Temps de livraison**
- ✅ **Aléatoire entre 10 et 30 secondes**
- ✅ Affiché en temps réel
- ✅ Simulation réaliste du trajet

### 6. **Commentaires clients**
- ✅ **70% de commentaires positifs** :
  - "Excellent service !"
  - "Livreur très sympathique"
  - "Livraison rapide, merci !"
  - "Nourriture encore chaude"
  - etc.

- ✅ **20% de commentaires négatifs** :
  - "Frites froides"
  - "En retard de 15 minutes"
  - "Manque de couverts"
  - "Burger écrasé"
  - "Il manque un plat"
  - etc.

- ✅ **10% de commentaires neutres** :
  - "Correct"
  - "RAS"
  - "Bien"

### 7. **Notes des clients**
- ⭐⭐⭐⭐⭐ (5 étoiles) pour les commentaires positifs
- ⭐⭐ (2 étoiles) pour les commentaires négatifs
- ⭐⭐⭐ (3 étoiles) pour les commentaires neutres

---

## 📊 CANAUX REDIS UTILISÉS

| Canal | Description | Émetteur | Récepteur |
|-------|-------------|----------|-----------|
| `nouvelles-commandes` | Publication de nouvelles commandes | Client | Manager |
| `offres-courses` | Diffusion des offres aux livreurs | Manager | Tous les livreurs |
| `reponses-livreurs` | Candidatures des livreurs | Livreurs | Manager |
| `notifications-livreur:<ID>` | Notifications privées | Manager | Livreur spécifique |
| `confirmation-client:<ID>` | Confirmations de commande | Manager | Client spécifique |
| `statut-livraison:<CMD>` | Statut final de livraison | Système | Tous |

---

## 🎯 ARCHITECTURE DU SYSTÈME

```
┌─────────────┐
│   CLIENTS   │ (Générés aléatoirement)
└──────┬──────┘
       │ nouvelles-commandes
       ▼
┌──────────────────────┐
│   GESTIONNAIRE       │
│   (GestionnaireLivreurs)
│   - États des livreurs
│   - Statistiques
└──────┬───────────────┘
       │ offres-courses
       ▼
┌────────────────────────────┐
│   LIVREURS (8-10)          │
│   États:                   │
│   • disponible             │
│   • en_livraison           │
│   Décisions aléatoires:    │
│   • Accepter (30-80%)      │
│   • Refuser (20-70%)       │
└────────┬───────────────────┘
         │ reponses-livreurs
         ▼
┌──────────────────────┐
│   ATTRIBUTION        │
│   + Livraison        │
│   + Commentaire      │
└──────────────────────┘
```

---

## ⚙️ PERSONNALISATION

### Modifier le nombre de livreurs et commandes

**Dans `simulation_realiste.py` :**
```python
# Ligne 468
NB_LIVREURS = 8    # ← Changez ici (ex: 15)
NB_COMMANDES = 15  # ← Changez ici (ex: 30)
```

**Dans `simulation_multithreading.py` :**
```python
# Ligne 251
simulation = SimulationMultithreading(
    nb_livreurs=10,  # ← Changez ici
    nb_commandes=25  # ← Changez ici
)
```

### Modifier les taux d'acceptation

**Dans `simulation_realiste.py`, ligne 310 :**
```python
# Actuellement : entre 30% et 80%
taux_acceptation = random.uniform(0.3, 0.8)

# Pour augmenter les acceptations :
taux_acceptation = random.uniform(0.6, 0.9)  # 60-90%

# Pour plus de refus :
taux_acceptation = random.uniform(0.2, 0.5)  # 20-50%
```

### Modifier les temps de livraison

**Dans `simulation_realiste.py`, ligne 356 :**
```python
# Actuellement : entre 10 et 30 secondes
temps_livraison = random.uniform(10, 30)

# Pour livraisons plus rapides :
temps_livraison = random.uniform(5, 15)

# Pour livraisons plus longues :
temps_livraison = random.uniform(20, 60)
```

### Modifier les proportions de commentaires

**Dans `simulation_realiste.py`, ligne 368 :**
```python
# Actuellement : 70% positif, 20% négatif, 10% neutre
type_commentaire = random.choices(
    ['positif', 'negatif', 'neutre'],
    weights=[0.70, 0.20, 0.10]
)[0]

# Pour plus de commentaires positifs :
weights=[0.85, 0.10, 0.05]  # 85% positif

# Pour plus de négatifs (simulation problématique) :
weights=[0.40, 0.50, 0.10]  # 50% négatif
```

---

## 🐛 RÉSOLUTION DE PROBLÈMES

### Redis ne répond pas
```powershell
# Vérifier si Redis fonctionne
cd C:\Users\PC\Downloads\redis\Redis-x64-5.0.14.1
.\redis-cli.exe ping

# Si pas de réponse, redémarrer Redis
Start-Process -FilePath ".\redis-server.exe"
```

### Erreur "No module named 'redis'"
```powershell
# Installer le module Redis
pip install redis
# ou
py -m pip install redis
```

### Aucun livreur ne répond
- ✅ Augmentez le nombre de livreurs (`NB_LIVREURS = 15`)
- ✅ Augmentez le taux d'acceptation (voir section Personnalisation)
- ✅ Diminuez le nombre de commandes simultanées

---

## 📈 UTILISATION POUR VOTRE PROJET

### Pour une présentation
**Utilisez `simulation_realiste.py`** :
- Facile à comprendre
- Sortie visuelle claire
- Scénarios bien détaillés

### Pour démontrer la scalabilité
**Utilisez `simulation_multithreading.py`** :
- Montre la gestion concurrente
- Statistiques impressionnantes
- Plus proche d'un système réel

### Pour des tests manuels
**Utilisez les scripts originaux** :
```powershell
# Terminal 1
py manager.py

# Terminal 2
py livreur.py livreur-001

# Terminal 3
py client.py
```

---

## 🎓 POINTS CLÉS POUR VOTRE RAPPORT

✅ **Redis Pub/Sub** : Communication asynchrone temps réel  
✅ **Gestion d'états** : Tracking des livreurs (disponible/occupé)  
✅ **Thread-safety** : Lock pour éviter les conflits concurrents  
✅ **Scalabilité** : Gestion de multiples commandes simultanées  
✅ **Réalisme** : Scénarios aléatoires proches de la réalité  
✅ **Canaux privés** : `notifications-livreur:<ID>` pour communications ciblées  
✅ **Statistiques** : Monitoring en temps réel du système  

---

## 📝 STRUCTURE DES MESSAGES REDIS

### Nouvelle commande (client → manager)
```json
{
  "id_commande": "CMD-20251015-1234",
  "id_client": "client-5678",
  "nom_client": "Fatima Benali",
  "restaurant_nom": "McDonald's",
  "restaurant_adresse": "12 Rue de Paris",
  "plats": [
    {"nom": "BigMac", "prix": 6.50},
    {"nom": "Frites", "prix": 2.50}
  ],
  "montant_total": 9.00,
  "adresse_livraison": "45 Avenue des Champs-Élysées",
  "timestamp": "2025-10-15T14:32:10"
}
```

### Statut de livraison
```json
{
  "id_commande": "CMD-20251015-1234",
  "id_livreur": "livreur-003",
  "statut": "Livré",
  "commentaire": "Excellent service !",
  "note": "⭐⭐⭐⭐⭐",
  "temps_livraison": "18s"
}
```

---

## 🚀 COMMANDES RAPIDES

```powershell
# Simulation réaliste (15 commandes, 8 livreurs)
cd C:\Users\PC\projet-redis-livraison
py simulation_realiste.py

# Simulation multi-threading (25 commandes parallèles)
py simulation_multithreading.py

# Simulation simple (3 commandes de démo)
py demo_simple.py
```

---

## 💡 CONSEILS

1. **Commencez par `demo_simple.py`** pour comprendre le concept
2. **Testez `simulation_realiste.py`** avec des paramètres réduits (5 commandes)
3. **Augmentez progressivement** le nombre de commandes et livreurs
4. **Observez les états** des livreurs pour voir la gestion intelligente
5. **Lisez les commentaires** pour voir la variété des scénarios

---

**Bon courage pour votre projet ! 🎓✨**

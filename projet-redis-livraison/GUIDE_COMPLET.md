# 🚀 Guide d'Utilisation Complet - Système de Livraison Redis

## 📋 Vue d'ensemble du système

Votre système simule maintenant une plateforme de livraison complète avec 3 acteurs :

1. **👤 CLIENT** : Passe des commandes de repas
2. **🏢 MANAGER** : Reçoit les commandes et coordonne les livreurs  
3. **🚴 LIVREUR** : Accepte les courses et effectue les livraisons

---

## 🎬 Guide de Démarrage Rapide

### 📍 Étape 1 : Démarrer Redis Server

Dans un terminal PowerShell :
```powershell
cd C:\Users\PC\Downloads\redis\Redis-x64-5.0.14.1
.\redis-server.exe
```
✅ Laissez cette fenêtre ouverte

---

### 🏢 Étape 2 : Lancer le Manager (Terminal 1)

```powershell
cd C:\Users\PC\projet-redis-livraison
py manager.py
```

**Ce que fait le manager :**
- ✅ Écoute les commandes des clients sur `nouvelles-commandes`
- ✅ Crée automatiquement des offres pour les livreurs
- ✅ Gère l'attribution des courses
- ✅ Envoie les confirmations aux clients

**Vous devriez voir :**
```
🏢 Manager démarré et prêt à recevoir des commandes...
   📥 Écoute les commandes des clients sur 'nouvelles-commandes'
   📬 Écoute les candidatures des livreurs sur 'reponses-livreurs'
```

---

### 🚴 Étape 3 : Lancer les Livreurs (Terminaux 2, 3, 4...)

**Terminal 2 :**
```powershell
cd C:\Users\PC\projet-redis-livraison
py livreur.py livreur-001
```

**Terminal 3 :**
```powershell
cd C:\Users\PC\projet-redis-livraison
py livreur.py livreur-002
```

**Terminal 4 :**
```powershell
cd C:\Users\PC\projet-redis-livraison
py livreur.py livreur-003
```

**Ce que font les livreurs :**
- ✅ S'abonnent au canal public `offres-courses`
- ✅ S'abonnent à leur canal privé `notifications-livreur:<ID>`
- ✅ Reçoivent les offres en temps réel
- ✅ Peuvent accepter ou refuser les courses

**Vous devriez voir :**
```
🚴 Livreur livreur-001 connecté et en attente d'offres...
```

---

### 👤 Étape 4 : Lancer un Client (Terminal 5)

```powershell
cd C:\Users\PC\projet-redis-livraison
py client.py
```

**Ce que fait le client :**
1. Entre son nom
2. Choisit un restaurant dans la liste
3. Consulte le menu
4. Sélectionne des plats
5. Indique son adresse de livraison
6. Envoie la commande au manager
7. Reçoit une confirmation quand un livreur est assigné

---

## 🎯 Scénario de Test Complet

### 1️⃣ Dans le terminal CLIENT :

```
👤 Bienvenue sur la plateforme de livraison de repas !
Entrez votre nom : Jean Dupont

============================================================
🍽️  RESTAURANTS DISPONIBLES
============================================================
1. Burger King - 12 Rue de la Paix, Paris
2. Pizza Hut - 25 Avenue Montaigne, Paris
3. Sushi Shop - 8 Boulevard Saint-Germain, Paris
============================================================

Choisissez un restaurant (numéro) : 1

============================================================
📋 MENU - Burger King
============================================================
📍 Adresse: 12 Rue de la Paix, Paris

🍽️  Plats disponibles :
  1. Whopper - 6.5€
  2. Chicken Royal - 5.9€
  3. Frites - 2.5€
  4. Coca-Cola - 2.0€
============================================================

Choisissez un plat (numéro) ou 'f' pour finaliser : 1
✅ Whopper ajouté au panier (6.5€)

Choisissez un plat (numéro) ou 'f' pour finaliser : 3
✅ Frites ajouté au panier (2.5€)

Choisissez un plat (numéro) ou 'f' pour finaliser : f

📍 Entrez votre adresse de livraison : 45 Avenue des Champs-Élysées, Paris

✅ Commande envoyée avec succès !
   ID Commande : CMD-20251015093045-1234
   Montant     : 9.0€
   Livraison à : 45 Avenue des Champs-Élysées, Paris

⏳ En attente de confirmation...
```

---

### 2️⃣ Dans le terminal MANAGER :

```
💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼
📥 NOUVELLE COMMANDE REÇUE
💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼
   ID Commande      : CMD-20251015093045-1234
   Client           : Jean Dupont
   Restaurant       : Burger King
   Montant total    : 9.0€
   Adresse livraison: 45 Avenue des Champs-Élysées, Paris
💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼💼

✅ Offre publiée (reçue par 3 livreur(s)) :
   ID Commande      : CMD-20251015093045-1234
   Restaurant       : Burger King (12 Rue de la Paix, Paris)
   Livraison        : 45 Avenue des Champs-Élysées, Paris
   Rémunération     : 1.35€
```

---

### 3️⃣ Dans TOUS les terminaux LIVREURS :

```
============================================================
🆕 NOUVELLE OFFRE DE COURSE
============================================================
ID Commande      : CMD-20251015093045-1234
Restaurant       : Burger King
Adresse retrait  : 12 Rue de la Paix, Paris
Adresse livraison: 45 Avenue des Champs-Élysées, Paris
Rémunération     : 1.35€
============================================================
Êtes-vous intéressé ? (o/n) : 
```

**Le livreur-002 tape `o` en premier !**

---

### 4️⃣ Dans le terminal MANAGER :

```
📬 Nouvelle candidature reçue :
   Livreur ID       : livreur-002
   Pour la commande : CMD-20251015093045-1234

✅ Course CMD-20251015093045-1234 attribuée au livreur livreur-002
✅ Confirmation envoyée au client client-XXXX
```

---

### 5️⃣ Dans le terminal du LIVREUR-002 (qui a accepté) :

```
✅ Candidature envoyée pour la commande CMD-20251015093045-1234

🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
🎉 Félicitations ! La commande CMD-20251015093045-1234 vous a été attribuée.
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
```

---

### 6️⃣ Dans le terminal CLIENT :

```
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
✅ COMMANDE CONFIRMÉE
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
ID Commande : CMD-20251015093045-1234
Livreur     : livreur-002
Statut      : Livreur attribué
Message     : Votre commande CMD-20251015093045-1234 a été prise en charge par le livreur livreur-002
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
```

---

## 📊 Architecture Redis Pub/Sub

```
┌─────────────┐
│   CLIENT    │ Passe commande
└──────┬──────┘
       │
       ▼ publish
┌──────────────────────┐
│ nouvelles-commandes  │ Canal Redis
└──────┬───────────────┘
       │
       ▼ subscribe
┌─────────────┐
│   MANAGER   │ Crée offre
└──────┬──────┘
       │
       ▼ publish
┌──────────────────────┐
│  offres-courses      │ Canal Redis (public)
└──────┬───────────────┘
       │
       ▼ subscribe (tous les livreurs)
┌─────────────────────┐
│  LIVREURS (1,2,3)   │ Acceptent/refusent
└──────┬──────────────┘
       │
       ▼ publish
┌──────────────────────┐
│ reponses-livreurs    │ Canal Redis
└──────┬───────────────┘
       │
       ▼ subscribe
┌─────────────┐
│   MANAGER   │ Attribue course
└──────┬──────┘
       │
       ├──────────────────┐
       ▼ publish          ▼ publish
┌─────────────────┐  ┌────────────────────┐
│ notifications-  │  │ confirmation-      │
│ livreur:002     │  │ client:XXXX        │
└─────────────────┘  └────────────────────┘
       │                      │
       ▼ subscribe            ▼ subscribe
┌─────────────────┐  ┌────────────────────┐
│  Livreur-002    │  │   Client           │
│  (notifié)      │  │   (confirmé)       │
└─────────────────┘  └────────────────────┘
```

---

## 🔑 Canaux Redis Utilisés

| Canal | Type | Émetteur | Récepteur | Contenu |
|-------|------|----------|-----------|---------|
| `nouvelles-commandes` | Public | Client | Manager | Commande complète du client |
| `offres-courses` | Public | Manager | Tous les livreurs | Offre de livraison |
| `reponses-livreurs` | Public | Livreurs | Manager | Candidatures |
| `notifications-livreur:<ID>` | Privé | Manager | Livreur spécifique | Attribution |
| `confirmation-client:<ID>` | Privé | Manager | Client spécifique | Confirmation |

---

## 💡 Points Clés pour Votre Présentation

✅ **Architecture événementielle** : Communication asynchrone via Redis Pub/Sub  
✅ **Temps réel** : Latence < 1ms entre publication et réception  
✅ **Découplage** : Clients, manager et livreurs ne se connaissent pas directement  
✅ **Scalabilité** : Peut supporter des milliers de livreurs simultanés  
✅ **Multi-canal** : Chaque acteur écoute plusieurs canaux en parallèle  
✅ **Notifications ciblées** : Canaux privés pour chaque utilisateur  

---

## 🛠️ Commandes Utiles

### Tester Redis en direct
```powershell
cd C:\Users\PC\Downloads\redis\Redis-x64-5.0.14.1
.\redis-cli.exe

# Dans redis-cli :
PING                              # Test de connexion
PUBSUB CHANNELS                   # Liste des canaux actifs
PUBSUB NUMSUB offres-courses      # Nombre d'abonnés sur un canal
```

### Arrêter proprement
- **Client / Livreur / Manager** : `Ctrl + C`
- **Redis Server** : Fermez la fenêtre ou `Ctrl + C`

---

## 📁 Fichiers du Projet

| Fichier | Rôle | Acteur |
|---------|------|--------|
| `client.py` | Interface client pour commander | 👤 Client |
| `manager.py` | Coordination générale | 🏢 Manager |
| `livreur.py` | Interface livreur | 🚴 Livreur |
| `attribution.py` | Attribution manuelle (optionnel) | 🏢 Manager |
| `restaurants_loader.py` | Chargement du JSON restaurants | 🛠️ Utilitaire |

---

**Bon test ! 🚀**

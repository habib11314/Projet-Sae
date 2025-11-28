# 🤖 Guide des Simulations Automatiques

## 📋 Trois modes de simulation disponibles

### 🎯 Mode 1 : Simulation Complète (Recommandé)
**Fichier :** `simulation_auto.py`

Lance automatiquement tous les composants dans des fenêtres séparées :
- 1 Manager
- 5 Livreurs automatiques (acceptent aléatoirement)
- 3 Clients automatiques (passent des commandes)

```bash
cd C:\Users\PC\projet-redis-livraison
py simulation_auto.py
```

**Avantages :**
- ✅ Simulation réaliste avec plusieurs fenêtres
- ✅ Livreurs qui décident aléatoirement
- ✅ Clients qui passent des commandes espacées
- ✅ Facile à observer

---

### 🎬 Mode 2 : Démonstration Simple
**Fichier :** `demo_simple.py`

Simule tout le système dans un seul terminal (sans fenêtres multiples) :
- Génère 3 commandes successives
- Affiche chaque étape du processus
- Parfait pour les présentations

```bash
cd C:\Users\PC\projet-redis-livraison
py demo_simple.py
```

**Avantages :**
- ✅ Une seule fenêtre
- ✅ Affichage détaillé de chaque étape
- ✅ Idéal pour comprendre le flux
- ✅ Pas de gestion de multiples terminaux

**Exemple de sortie :**
```
======================================================================
🚀 DÉMONSTRATION AUTOMATIQUE - Système de Livraison Redis
======================================================================

======================================================================
📦 COMMANDE 1/3
======================================================================

👤 Client: Alice
🏪 Restaurant: Burger King
💰 Montant: 24.50€
📍 Livraison: 45 Avenue des Champs-Élysées, Paris
🚴 Rémunération livreur: 3.68€

📤 Publication de la commande sur Redis...
   ✅ 1 manager(s) ont reçu la commande

📢 Publication de l'offre aux livreurs...
   ✅ 5 livreur(s) ont reçu l'offre

🚴 Le livreur-003 manifeste son intérêt...
   ✅ Candidature envoyée au manager

✅ Attribution de la course au livreur-003...
   ✅ Confirmation envoyée au client

🎉 Commande CMD-20251015140131-7220 traitée avec succès !
```

---

### 🧪 Mode 3 : Test Manuel avec Automation
**Fichiers :** `livreur_auto.py` + `client_auto.py`

Lance manuellement les composants automatiques :

**Terminal 1 - Manager :**
```bash
py manager.py
```

**Terminal 2, 3, 4... - Livreurs automatiques :**
```bash
py livreur_auto.py livreur-001
py livreur_auto.py livreur-002
py livreur_auto.py livreur-003
```

**Terminal final - Client automatique :**
```bash
py client_auto.py
```

**Avantages :**
- ✅ Contrôle total sur chaque composant
- ✅ Peut lancer autant de livreurs que souhaité
- ✅ Peut lancer des clients en continu

---

## 📊 Comparaison des Modes

| Mode | Fenêtres | Automatisation | Complexité | Usage |
|------|----------|----------------|------------|-------|
| `simulation_auto.py` | Multiple | 100% | Moyenne | **Démo réaliste** |
| `demo_simple.py` | 1 seule | 100% | Faible | **Présentation** |
| Manuel avec `*_auto.py` | Multiple | 90% | Élevée | **Tests avancés** |

---

## 🎯 Quel mode choisir ?

### Pour une présentation/démonstration rapide :
➡️ **Utilisez `demo_simple.py`**
- Une seule commande à exécuter
- Tout se passe dans un terminal
- Facile à suivre

### Pour une simulation réaliste :
➡️ **Utilisez `simulation_auto.py`**
- Ouvre automatiquement toutes les fenêtres
- Simule un vrai système avec plusieurs acteurs
- Impressionnant visuellement

### Pour des tests personnalisés :
➡️ **Utilisez les scripts `*_auto.py` manuellement**
- Lancez autant de livreurs que vous voulez
- Contrôlez le timing des commandes
- Debuggage plus facile

---

## ⚙️ Configuration

### Modifier le nombre de livreurs/clients
Éditez `simulation_auto.py` :
```python
nb_livreurs = 10  # Au lieu de 5
nb_clients = 5    # Au lieu de 3
```

### Modifier le taux d'acceptation des livreurs
Éditez `livreur_auto.py` :
```python
self.taux_acceptation = 0.9  # 90% au lieu de 70%
```

### Modifier le délai entre commandes
Éditez `demo_simple.py` :
```python
DELAI_ENTRE_COMMANDES = 5  # 5 secondes au lieu de 3
```

---

## 🐛 Dépannage

### Redis ne répond pas
```bash
# Vérifier que Redis tourne
cd C:\Users\PC\Downloads\redis\Redis-x64-5.0.14.1
.\redis-cli.exe ping
# Doit afficher : PONG
```

### Les fenêtres ne s'ouvrent pas
- Sur Windows, vérifiez que Python est dans le PATH
- Essayez de lancer `demo_simple.py` à la place

### Erreur "Module redis not found"
```bash
pip install redis
```

---

## 📈 Exemple de Scénario Complet

### Scénario : Démo pour un projet étudiant

1. **Préparer Redis**
   ```bash
   cd C:\Users\PC\Downloads\redis\Redis-x64-5.0.14.1
   .\redis-server.exe
   ```

2. **Lancer la démo simple** (dans un autre terminal)
   ```bash
   cd C:\Users\PC\projet-redis-livraison
   py demo_simple.py
   ```

3. **Expliquer pendant l'exécution :**
   - "Voici un client qui passe commande"
   - "Le manager reçoit la commande via Redis Pub/Sub"
   - "L'offre est diffusée instantanément aux livreurs"
   - "Un livreur accepte et reçoit l'attribution"
   - "Le client est notifié automatiquement"

4. **Montrer le code Redis Pub/Sub**
   - Ouvrir `manager.py` et montrer `publish()` et `subscribe()`
   - Expliquer l'architecture événementielle

---

## 🎓 Pour votre présentation

### Points clés à mentionner :
1. ✅ **Architecture Pub/Sub** : Communication asynchrone temps réel
2. ✅ **Scalabilité** : Peut gérer des milliers de livreurs
3. ✅ **Découplage** : Les composants ne se connaissent pas directement
4. ✅ **Latence < 1ms** : Diffusion instantanée des messages
5. ✅ **Canaux multiples** : Public (offres) + Privés (notifications)

### Démonstration en live :
1. Lancer `demo_simple.py`
2. Montrer les 3 commandes qui s'exécutent
3. Expliquer chaque étape affichée
4. Ouvrir Redis CLI et montrer les canaux actifs :
   ```bash
   redis-cli
   PUBSUB CHANNELS
   ```

---

**Bon courage pour votre projet ! 🚀**

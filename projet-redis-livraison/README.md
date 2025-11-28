# 🚴 Projet Redis - Système de Notification Livraison en Temps Réel

## 📋 Description du Projet

Ce POC (Proof of Concept) simule un système de notification en temps réel pour une plateforme de livraison de repas utilisant **Redis Pub/Sub**.

## 🏗️ Architecture

### Canaux Redis utilisés :
- **`nouvelles-commandes`** : Canal où les clients envoient leurs commandes
- **`offres-courses`** : Canal public où le manager publie les nouvelles offres
- **`reponses-livreurs`** : Canal où les livreurs manifestent leur intérêt
- **`notifications-livreur:<ID>`** : Canaux privés pour notifier chaque livreur individuellement
- **`confirmation-client:<ID>`** : Canaux privés pour confirmer les commandes aux clients

## 📂 Structure du Projet

```
projet-redis-livraison/
├── client.py           # Script pour les clients (passer commande)
├── manager.py          # Script du gestionnaire de plateforme
├── livreur.py          # Script pour les livreurs
├── attribution.py      # Script d'attribution directe
├── restaurants_loader.py # Utilitaire pour charger les restaurants
└── README.md           # Ce fichier
```

## 🚀 Installation

### Prérequis
- Python 3.12+
- Redis Server

### Installation des dépendances
```bash
pip install redis
```

## 📖 Guide d'Utilisation

### Étape 1 : Démarrer Redis Server

Ouvrez un terminal dans le dossier d'installation de Redis :
```bash
cd C:\Users\PC\Downloads\redis\Redis-x64-5.0.14.1
.\redis-server.exe
```

### Étape 2 : Lancer plusieurs livreurs (dans des terminaux séparés)

**Terminal 1 - Livreur 1 :**
```bash
cd C:\Users\PC\projet-redis-livraison
python livreur.py livreur-001
```

**Terminal 2 - Livreur 2 :**
```bash
cd C:\Users\PC\projet-redis-livraison
python livreur.py livreur-002
```

**Terminal 3 - Livreur 3 :**
```bash
cd C:\Users\PC\projet-redis-livraison
python livreur.py livreur-003
```

### Étape 3 : Lancer le Manager

**Terminal 4 - Manager :**
```bash
cd C:\Users\PC\projet-redis-livraison
python manager.py
```

Le manager va :
1. Publier une offre de course
2. Attendre 10 secondes les candidatures
3. Attribuer automatiquement la course au premier candidat

### Étape 4 (Optionnelle) : Attribution manuelle

Si vous voulez attribuer manuellement une course à un livreur spécifique :
```bash
python attribution.py livreur-002 CMD-001
```

## 🔄 Flux de Travail

```
┌─────────────┐
│   CLIENT    │
└──────┬──────┘
       │ 1. Passe commande
       ▼
┌─────────────────────────┐
│  nouvelles-commandes    │ ◄── Canal Redis
└──────┬──────────────────┘
       │ 2. Manager reçoit
       ▼
┌─────────────┐
│   MANAGER   │
└──────┬──────┘
       │ 3. Publie offre
       ▼
┌─────────────────────┐
│  offres-courses     │ ◄── Canal public Redis
└─────────┬───────────┘
          │ 4. Reçoivent l'offre
    ┌─────┼─────┬─────┐
    ▼     ▼     ▼     ▼
┌────────────────────────┐
│ Livreur 1, 2, 3, ...   │
└───────┬────────────────┘
        │ 5. Manifestent intérêt
        ▼
┌─────────────────────┐
│ reponses-livreurs   │ ◄── Canal de réponse
└──────┬──────────────┘
       │ 6. Manager sélectionne
       ├──────────────┬─────────────────┐
       ▼              ▼                 ▼
┌────────────────────────────┐  ┌──────────────────┐
│ notifications-livreur:001  │  │ confirmation-    │
│                            │  │ client:xxx       │
└────────────────────────────┘  └──────────────────┘
       Livreur notifié              Client notifié
```

## 🎯 Fonctionnalités Démontrées

✅ **Broadcast en temps réel** : Une offre est diffusée instantanément à tous les livreurs  
✅ **Communication bidirectionnelle** : Les livreurs peuvent répondre aux offres  
✅ **Notifications privées** : Attribution sécurisée à un livreur spécifique  
✅ **Multi-canal** : Chaque livreur écoute simultanément le canal public et son canal privé  

## 📊 Modèle de Données

### Message d'Offre
```json
{
  "id_commande": "CMD-001",
  "restaurant_nom": "Burger King",
  "restaurant_adresse": "12 Rue de la Paix, Paris",
  "adresse_livraison": "45 Avenue des Champs-Élysées, Paris",
  "remuneration_livreur": 8.50
}
```

### Candidature de Livreur
```json
{
  "id_livreur": "livreur-001",
  "id_commande": "CMD-001"
}
```

### Notification d'Attribution
```json
{
  "type": "attribution",
  "id_commande": "CMD-001",
  "message": "🎉 Félicitations ! La commande CMD-001 vous a été attribuée."
}
```

## ⚠️ Limitations du POC

- **Pas de persistance** : Les messages Redis Pub/Sub ne sont pas stockés
- **Pas de sécurité** : Aucune authentification implémentée
- **Scalabilité limitée** : Pour une production réelle, considérer Redis Streams ou Kafka

## 🔧 Configuration

Par défaut, les scripts se connectent à :
- **Host** : `localhost`
- **Port** : `6379`

Pour modifier, éditez les paramètres dans les constructeurs de classe.

## 📚 Documentation Redis

- [Redis Pub/Sub Documentation](https://redis.io/docs/latest/develop/pubsub/)
- [Redis-py Library](https://redis-py.readthedocs.io/)

## 👨‍💻 Auteur

Projet réalisé dans le cadre du cours **"Bases de Données Avancées"**

---

**Bon test ! 🚀**

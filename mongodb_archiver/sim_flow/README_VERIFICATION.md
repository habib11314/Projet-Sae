# Système de Simulation avec Change Streams

## ✅ Comment vérifier que le système fonctionne

### Méthode 1 : Lancer le système et observer les terminaux

1. **Lancer tous les simulateurs** :
   ```powershell
   cd C:\Users\PC\mongodb_archiver\sim_flow
   py launcher_changestreams.py
   ```

2. **4 terminaux devraient s'ouvrir** :
   - **CLIENT** : Crée des commandes toutes les 10 secondes
   - **PLATFORM** : Détecte les commandes et orchestre le flux
   - **RESTAURANT** : Accepte/refuse les requêtes (80% d'acceptation)
   - **LIVREUR** : Accepte/refuse les livraisons (70% d'acceptation)

3. **Observer les terminaux** :
   - Terminal **CLIENT** : Devrait afficher "NOUVELLE COMMANDE CRÉÉE" toutes les 10s
   - Terminal **PLATFORM** : Devrait afficher "NOUVELLE COMMANDE DÉTECTÉE" dès qu'une commande est créée
   - Terminal **RESTAURANT** : Devrait afficher "NOUVELLE REQUÊTE RESTAURANT" et répondre
   - Terminal **LIVREUR** : Devrait afficher "NOUVELLE REQUÊTE LIVREUR" quand le restaurant accepte

### Méthode 2 : Test automatique

Avec les simulateurs **en cours d'exécution**, lancez ce script dans un **nouveau** terminal :

```powershell
cd C:\Users\PC\mongodb_archiver\sim_flow
py verify_system.py
```

Ce script va :
1. Créer une commande de test
2. Vérifier que la platform la détecte (10s)
3. Vérifier que le restaurant répond (10s)
4. Vérifier que le livreur accepte (10s)
5. Afficher le résultat final

**Résultat attendu** :
```
✅ PLATFORM FONCTIONNE!
✅ RESTAURANT FONCTIONNE!
✅ LIVREUR FONCTIONNE!
🎉 SUCCÈS COMPLET! Tous les simulateurs fonctionnent!
```

### Méthode 3 : Vérification manuelle dans MongoDB

```powershell
# Compter les documents avant
py -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv('.env'); client = MongoClient(os.getenv('MONGODB_URI')); db = client['Ubereats']; print(f'Commandes: {db.Commande.count_documents({})}'); print(f'RestReq: {db.RestaurantRequests.count_documents({})}'); print(f'DelivReq: {db.DeliveryRequests.count_documents({})}')"

# Attendre 20 secondes (le client crée une commande toutes les 10s)

# Recompter - les nombres devraient avoir augmenté
py -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv('.env'); client = MongoClient(os.getenv('MONGODB_URI')); db = client['Ubereats']; print(f'Commandes: {db.Commande.count_documents({})}'); print(f'RestReq: {db.RestaurantRequests.count_documents({})}'); print(f'DelivReq: {db.DeliveryRequests.count_documents({})}')"
```

Si les nombres augmentent → Le système fonctionne !

## 🐛 Dépannage

### Problème : "La platform ne détecte pas les commandes"

**Solutions** :
1. Vérifiez que **tous les 4 terminaux** sont ouverts et actifs
2. Regardez le terminal PLATFORM - y a-t-il des erreurs ?
3. Vérifiez MongoDB Atlas Change Streams :
   ```powershell
   py test_support_changestreams.py
   ```
   Doit afficher : `✅ Votre MongoDB supporte les Change Streams!`

### Problème : "Les terminaux se ferment immédiatement"

**Cause** : Erreur dans le script (connexion MongoDB, dépendances manquantes)

**Solutions** :
1. Lancez manuellement chaque simulateur pour voir l'erreur :
   ```powershell
   cd C:\Users\PC\mongodb_archiver
   py sim_flow\platform_sim_changestreams.py
   ```
2. Vérifiez `.env` contient bien `MONGODB_URI`
3. Vérifiez les dépendances : `py -m pip install pymongo python-dotenv`

### Problème : "Le système était OK avant, maintenant ça ne marche plus"

**Solutions** :
1. Fermez TOUS les terminaux ouverts (Client, Platform, Restaurant, Livreur)
2. Relancez : `py launcher_changestreams.py`
3. Attendez 5 secondes que tous les simulateurs se connectent
4. Testez avec `py verify_system.py`

## 📊 Indicateurs de bon fonctionnement

### Terminal CLIENT
```
🆕 NOUVELLE COMMANDE CRÉÉE
   📝 Numéro      : SIM-1760612345-1234
   🔄 Statut      : pending_request
👀 Écoute via Change Streams pour SIM-...
⏳ Attente de 10 secondes avant nouvelle commande...
```

### Terminal PLATFORM
```
🔍 NOUVELLE COMMANDE DÉTECTÉE (Change Stream)
   📦 N° Commande  : SIM-1760612345-1234
   ✅ Requête envoyée
   ⏳ Attente réponse restaurant (max 60s via Change Streams)...

🍽️  RÉPONSE RESTAURANT - ACCEPTÉE
   ✅ Statut    : accepted

🚀 ATTRIBUTION DE COMMANDE AU LIVREUR
   🧑‍🚚 Livreur  : LIV-00012 (Dupont)
   ✅ Statut    : en_cours
```

### Terminal RESTAURANT
```
📥 NOUVELLE REQUÊTE RESTAURANT (Change Stream)
   📦 Commande : SIM-1760612345-1234

✅ ACCEPTÉE
   Commande : SIM-1760612345-1234
```

### Terminal LIVREUR
```
📥 NOUVELLE REQUÊTE LIVREUR (Change Stream)
   📦 Commande : SIM-1760612345-1234

✅ ACCEPTÉE
   Commande : SIM-1760612345-1234
```

## 🎯 Flux complet attendu

1. **CLIENT** crée une commande (toutes les 10s)
2. **PLATFORM** détecte instantanément via Change Stream
3. **PLATFORM** envoie requête au restaurant
4. **RESTAURANT** reçoit via Change Stream et répond (80% accepte)
5. **PLATFORM** reçoit réponse via Change Stream
6. **PLATFORM** cherche un livreur et envoie requête
7. **LIVREUR** reçoit via Change Stream et répond (70% accepte)
8. **PLATFORM** assigne la commande et notifie le client
9. **CLIENT** reçoit notification via Change Stream

**Temps total** : 2-5 secondes (vs 30+ secondes avec polling)

# 🎯 SIMULATION COMPLÈTE - Système de Livraison Redis

## ✅ DONNÉES RÉELLES UTILISÉES

Le système utilise maintenant **2 fichiers JSON** avec les **VRAIES données** :

### 📁 `restaurants.json`
- **100 restaurants réels**
- Informations : nom, adresse, catégorie, note, prix
- Exemple : "Starbucks", "Golden Temple Vegetarian Cafe", "Red Sea Ethiopian"

### 📁 `menu.json`  
- **Milliers de plats réels** 
- Chaque plat lié à un `restaurant_id`
- Informations : nom, prix, catégorie, description
- Exemple : "Iced Caramel Macchiato" (4.25 USD), "Bourbon Street Cheesecake" (23.00 USD)

---

## 🚀 LANCEMENT RAPIDE

### Étape 1 : Démarrer Redis
```powershell
cd C:\Users\PC\Downloads\redis\Redis-x64-5.0.14.1
Start-Process .\redis-server.exe
```

### Étape 2 : Lancer la simulation (3 terminaux automatiques)
```powershell
cd C:\Users\PC\projet-redis-livraison
py lancer_simulation_3_terminaux.py
```

**Résultat** : 3 nouveaux terminaux s'ouvrent :
- 🟢 **MANAGER** : Écoute et attribue les commandes
- 🟢 **LIVREUR-001** : Accepte/refuse aléatoirement (50-80%)
- 🟢 **CLIENT** : Génère des commandes avec VRAIS restaurants/menus

---

## 📊 CE QUE VOUS VERREZ

### Terminal CLIENT :
```
📦 COMMANDE #1
   👤 Client: Fatima Benali
   🏪 Restaurant: Starbucks (Hwy 11 and Avenue W)
   🍽️  Plats: Iced Caramel Macchiato, Pike Place® Roast
   💰 Total: 8.50€
   📍 Livraison: 45 Avenue des Champs-Élysées
   ✅ Publiée → 1 manager(s) notifié(s)
```

### Terminal MANAGER :
```
📦 NOUVELLE COMMANDE: CMD-5678
   👤 Client: Fatima Benali
   🏪 Restaurant: Starbucks
   💰 Montant: 8.50€
📢 Offre diffusée à 1 livreur(s)

✅ ATTRIBUTION
   🚴 Livreur: livreur-001
   📦 Commande: CMD-5678
```

### Terminal LIVREUR :
```
📢 OFFRE REÇUE: CMD-5678
   🏪 Starbucks
   💰 Rémunération: 1.28€
   ✅ J'ACCEPTE la course !

🎉 Course attribuée !
🚴 Je pars livrer...
⏱️  Temps de livraison: 15s

📍 LIVRAISON TERMINÉE
   💬 Client: "Excellent service !" ⭐⭐⭐⭐⭐
   ✅ Disponible pour nouvelle course (Total: 1)
```

---

## 🎲 FONCTIONNALITÉS AUTOMATIQUES

### ✅ Données 100% réelles
- **Restaurants** : Noms, adresses, catégories du JSON
- **Menus** : Plats authentiques avec vrais prix
- **Prix** : Convertis de USD en EUR

### ✅ Scénarios aléatoires
- **Clients** : 14 prénoms × 10 noms = 140 combinaisons
- **Adresses** : 8 adresses réelles (Paris, Montreuil, Bobigny, etc.)
- **Commandes** : 1 à 3 plats par commande
- **Intervalle** : 5 à 15 secondes entre commandes

### ✅ Comportements réalistes
- **Livreurs** : Taux d'acceptation 50-80% (aléatoire)
- **Refus** : "trop loin", "en pause", "autre course"
- **Livraison** : 10-25 secondes
- **Commentaires** : 70% positifs, 20% négatifs, 10% neutres

---

## 📂 FICHIERS PRINCIPAUX

| Fichier | Description | Usage |
|---------|-------------|-------|
| `client_auto_ameliore.py` | Client automatique | Génère commandes avec VRAIS menus |
| `manager_auto_ameliore.py` | Manager automatique | Écoute et attribue |
| `livreur_auto_ameliore.py` | Livreur automatique | Accepte/refuse/livre |
| `lancer_simulation_3_terminaux.py` | Lanceur | Ouvre les 3 terminaux |
| `restaurants.json` | Base de données | 100 restaurants réels |
| `menu.json` | Base de données | Milliers de plats réels |

---

## 🔧 AJOUTER PLUS DE LIVREURS

Ouvrez un nouveau terminal :
```powershell
cd C:\Users\PC\projet-redis-livraison
py livreur_auto_ameliore.py livreur-002
py livreur_auto_ameliore.py livreur-003
# ... etc
```

Chaque livreur a son propre **taux d'acceptation aléatoire** !

---

## 🛑 ARRÊTER LA SIMULATION

- Dans chaque terminal : `Ctrl+C`
- Les statistiques s'affichent automatiquement

---

## 📈 EXEMPLES DE RESTAURANTS RÉELS

- **Starbucks** : Iced Caramel Macchiato, Pike Place Roast
- **Red Sea Ethiopian** : Dolmas, Fish Dulet, Lamb Tibbs
- **SOCU Southern Kitchen** : Bourbon Street Cheesecake, Shrimp & Grits
- **Golden Temple Vegetarian Cafe** : Slice of Bread, Hummus Plate
- **Chez Lulu** : Lulu's House Salad, Upstream Salad
- **Moon Star Chinese** : Egg Roll, General Tso's Chicken
- **Potatoe Potatohz Perfic Pizza** : Three Topping Veggie

---

## ✅ AVANTAGES

✅ **100% réaliste** : Vrais restaurants, vrais plats, vrais prix  
✅ **Léger** : N'alourdit pas votre PC  
✅ **Visuel** : 3 terminaux séparés pour tout voir  
✅ **Flexible** : Ajoutez autant de livreurs que vous voulez  
✅ **Pédagogique** : Parfait pour démontrer Redis Pub/Sub  

---

## 🎓 POUR VOTRE PROJET ACADÉMIQUE

### Points clés à présenter :
1. **Redis Pub/Sub** : Communication asynchrone temps réel
2. **5 canaux** : nouvelles-commandes, offres-courses, reponses-livreurs, notifications-livreur:<ID>, confirmation-client:<ID>
3. **Données réelles** : 100 restaurants × milliers de plats
4. **Scénarios réalistes** : Refus, acceptation, livraison, commentaires
5. **Scalabilité** : Ajout dynamique de livreurs

---

**Bon courage pour votre projet ! 🚀✨**

# 🚀 GUIDE RAPIDE - Simulation 3 Terminaux

## ✅ Prérequis

1. **Démarrer Redis** (OBLIGATOIRE) :
```powershell
cd C:\Users\PC\Downloads\redis\Redis-x64-5.0.14.1
Start-Process .\redis-server.exe
```

2. **Vérifier Redis** :
```powershell
.\redis-cli.exe ping
# Doit afficher: PONG
```

---

## 🎯 LANCEMENT AUTOMATIQUE (1 seule commande)

### Option 1 : Lancement des 3 terminaux d'un coup

```powershell
cd C:\Users\PC\projet-redis-livraison
py lancer_simulation_3_terminaux.py
```

**Résultat** : 3 nouveaux terminaux s'ouvrent automatiquement :
- ✅ **Terminal 1 (MANAGER)** : Écoute les commandes, diffuse aux livreurs, attribue
- ✅ **Terminal 2 (LIVREUR)** : Écoute les offres, accepte/refuse aléatoirement
- ✅ **Terminal 3 (CLIENT)** : Génère des commandes aléatoires toutes les 5-15s

---

## 🎮 LANCEMENT MANUEL (contrôle total)

### 1. Terminal Manager (à lancer en premier)
```powershell
cd C:\Users\PC\projet-redis-livraison
py manager_auto_ameliore.py
```

### 2. Terminal Livreur (autant que vous voulez)
```powershell
# Terminal 2
py livreur_auto_ameliore.py livreur-001

# Terminal 3 (optionnel - plus de livreurs)
py livreur_auto_ameliore.py livreur-002

# Terminal 4 (optionnel)
py livreur_auto_ameliore.py livreur-003
```

### 3. Terminal Client (en dernier)
```powershell
py client_auto_ameliore.py
```

---

## 🎲 FONCTIONNALITÉS AUTOMATIQUES

### Client Automatique
✅ Charge les **VRAIS restaurants depuis JSON** (50 restaurants)  
✅ Utilise les **VRAIS menus** avec vrais prix  
✅ Génère des **clients aléatoires** (prénoms, noms, adresses)  
✅ Commandes toutes les **5-15 secondes**  
✅ 1 à 3 plats par commande  

### Manager Automatique
✅ Écoute les nouvelles commandes en **temps réel**  
✅ Diffuse les offres à **tous les livreurs connectés**  
✅ Attribue au **premier qui accepte**  
✅ Évite les **doubles attributions**  

### Livreur Automatique
✅ **Taux d'acceptation aléatoire** : 50-80%  
✅ **Raisons de refus** : "trop loin", "en pause", etc.  
✅ **Temps de livraison** : 10-25 secondes  
✅ **Commentaires clients** :
   - 70% positifs : "Excellent service !", "Nourriture chaude"
   - 20% négatifs : "Frites froides", "En retard"
   - 10% neutres : "Correct", "RAS"
✅ **Notes** : ⭐⭐⭐⭐⭐ (positif) / ⭐⭐ (négatif) / ⭐⭐⭐ (neutre)

---

## 📺 CE QUE VOUS VERREZ

### Terminal MANAGER :
```
📦 NOUVELLE COMMANDE: CMD-5678
   👤 Client: Fatima Benali
   🏪 Restaurant: McDonald's
   💰 Montant: 18.50€
📢 Offre diffusée à 3 livreur(s)

✅ ATTRIBUTION
   🚴 Livreur: livreur-001
   📦 Commande: CMD-5678
   ✅ Notification envoyée à livreur-001
```

### Terminal LIVREUR :
```
📢 OFFRE REÇUE: CMD-5678
   🏪 McDonald's
   💰 Rémunération: 2.78€
   ✅ J'ACCEPTE la course !

🎉 Course attribuée !
   📦 Commande: CMD-5678
   🚴 Je pars livrer...

⏱️  Temps de livraison: 15s

📍 LIVRAISON TERMINÉE: CMD-5678
   💬 Client: "Excellent service !" ⭐⭐⭐⭐⭐
   ✅ Disponible pour nouvelle course (Total: 1)
```

### Terminal CLIENT :
```
📦 COMMANDE #1
   👤 Client: Omar Khalil
   🏪 Restaurant: Burger King
   🍽️  Plats: Whopper, Frites
   💰 Total: 9.00€
   📍 Livraison: 45 Avenue des Champs-Élysées
   ✅ Publiée → 1 manager(s) notifié(s)

⏳ Prochaine commande dans 8.3s...
```

---

## 🛑 ARRÊTER LA SIMULATION

- **Dans chaque terminal** : Appuyez sur `Ctrl+C`
- Les statistiques s'affichent avant fermeture :
  - Manager : Nombre de commandes attribuées
  - Livreur : Nombre de livraisons effectuées
  - Client : Nombre de commandes générées

---

## 🔧 PERSONNALISATION

### Augmenter le nombre de livreurs
Lancez plus de terminaux livreurs :
```powershell
py livreur_auto_ameliore.py livreur-002
py livreur_auto_ameliore.py livreur-003
py livreur_auto_ameliore.py livreur-004
# ... etc
```

### Modifier le délai entre commandes
**Dans `client_auto_ameliore.py` (ligne 115)** :
```python
# Actuellement : 5-15 secondes
delai = random.uniform(5, 15)

# Pour plus rapide :
delai = random.uniform(2, 5)

# Pour plus lent :
delai = random.uniform(10, 30)
```

### Modifier le taux d'acceptation
**Dans `livreur_auto_ameliore.py` (ligne 32)** :
```python
# Actuellement : 50-80%
self.taux_acceptation = random.uniform(0.5, 0.8)

# Pour plus d'acceptations :
self.taux_acceptation = random.uniform(0.7, 0.9)

# Pour plus de refus :
self.taux_acceptation = random.uniform(0.3, 0.6)
```

---

## ✅ AVANTAGES DE CETTE VERSION

✅ **Léger** : Pas de simulation lourde qui bug le PC  
✅ **Réaliste** : Utilise les VRAIS restaurants et menus du JSON  
✅ **Interactif** : 3 terminaux séparés pour visualiser chaque acteur  
✅ **Flexible** : Lancez autant de livreurs que vous voulez  
✅ **Contrôlable** : Arrêtez/relancez quand vous voulez  
✅ **Scalable** : Ajoutez des livreurs en temps réel  

---

## 📋 CHECKLIST RAPIDE

1. ✅ Redis démarré
2. ✅ `py lancer_simulation_3_terminaux.py`
3. ✅ Observer les 3 terminaux
4. ✅ Ajouter des livreurs si besoin
5. ✅ Ctrl+C pour arrêter

---

**C'est tout ! Profitez de votre simulation réaliste ! 🎉**

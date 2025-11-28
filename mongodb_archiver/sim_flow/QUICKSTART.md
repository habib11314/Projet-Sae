# 🎬 Guide Rapide - Simulation Multi-Terminaux

## 🚀 Lancement rapide (2 secondes !)

```powershell
# Dans PowerShell ou CMD, depuis le dossier mongodb_archiver:
.\sim_flow\launch_all.bat
```

**Résultat**: 4 terminaux s'ouvrent automatiquement ! 🎉

---

## 📺 Que se passe-t-il ?

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Terminal 1    │     │   Terminal 2    │     │   Terminal 3    │     │   Terminal 4    │
│   🧑 CLIENT     │────▶│  🏢 PLATFORM   │────▶│  🍽️  RESTAURANT │     │   🚗 LIVREUR   │
│                 │     │                 │     │                 │     │                 │
│ Crée commande   │     │ Reçoit commande │     │ Reçoit demande  │     │ Reçoit demande  │
│ aléatoire       │     │ └─▶ Envoie au   │     │ Accepte/Refuse  │     │ Accepte/Refuse  │
│                 │     │     restaurant  │     │ (80% accept)    │     │ (70% accept)    │
│ Attend notif... │◀────│                 │◀────│                 │     │                 │
│                 │     │ Si accepté:     │     │                 │     │                 │
│ ✅ Livreur      │     │ └─▶ Cherche     │────────────────────────────▶│ Si accepté:     │
│    assigné!     │     │     livreur     │     │                 │     │ Marque en_course│
│                 │     │ └─▶ Notifie     │     │                 │     │                 │
└─────────────────┘     │     client      │     └─────────────────┘     └─────────────────┘
                        └─────────────────┘
```

---

## 🎯 Flux complet (exemple)

### 1️⃣ Terminal CLIENT (bleu)
```
[CLIENT] Created order SIM-1729089234-5678 for restaurant Le Bistrot (id: RES-00001)
[CLIENT] Listening for updates on SIM-1729089234-5678...
[CLIENT] Order SIM-1729089234-5678 status changed: pending_request -> en_cours
[CLIENT] Final status for SIM-1729089234-5678: en_cours
```

### 2️⃣ Terminal PLATFORM (magenta)
```
[PLATFORM] New pending request SIM-1729089234-5678 -> restaurant RES-00001
[PLATFORM] Waiting for restaurant response for SIM-1729089234-5678...
[PLATFORM] Restaurant accepted order SIM-1729089234-5678. Searching for livreurs...
[PLATFORM] Delivery request sent to livreur LIV-00012 for SIM-1729089234-5678
[PLATFORM] Order SIM-1729089234-5678 assigned to livreur LIV-00012 and marked 'en_cours'
[PLATFORM] Notification sent to client CLI-00023 for SIM-1729089234-5678
```

### 3️⃣ Terminal RESTAURANT (vert)
```
[RESTAURANT] Received request for order SIM-1729089234-5678 (restaurant RES-00001)
[RESTAURANT] Request for SIM-1729089234-5678 -> accepted
```

### 4️⃣ Terminal LIVREUR (jaune)
```
[LIVREUR] Delivery request for SIM-1729089234-5678 to livreur LIV-00012
[LIVREUR] Livreur LIV-00012 accepted and is now 'en_course' for SIM-1729089234-5678
```

---

## ⚙️ Configuration

Créer un fichier `.env` (optionnel):
```env
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGODB_DATABASE=Ubereats
RESTAURANT_ACCEPT_RATE=0.8
LIVREUR_ACCEPT_RATE=0.7
```

---

## 📊 Collections créées/utilisées

### Lecture (doit exister):
- `Client` - Clients existants
- `Restaurants` - Restaurants existants
- `Menu` - Menus/plats disponibles
- `Livreur` - Livreurs disponibles

### Écriture (créées automatiquement):
- `Commande` - Nouvelles commandes
- `RestaurantRequests` - Demandes aux restaurants
- `DeliveryRequests` - Demandes aux livreurs
- `Notifications` - Notifications clients

---

## 🎨 Organisation des fenêtres

Disposition recommandée (écran large):
```
┌───────────────┬───────────────┐
│   CLIENT      │   PLATFORM    │
│   (Terminal 1)│   (Terminal 2)│
├───────────────┼───────────────┤
│  RESTAURANT   │   LIVREUR     │
│   (Terminal 3)│   (Terminal 4)│
└───────────────┴───────────────┘
```

---

## ⏹️ Arrêter la simulation

Dans chaque terminal, appuyez sur:
```
Ctrl + C
```

Ou fermez simplement les fenêtres.

---

## 🔧 Dépannage

### "Python non trouvé"
```powershell
# Installer Python ou vérifier PATH
python --version
```

### "Aucune commande créée"
```powershell
# Générer des données de test d'abord
python simulate.py --count 100
```

### "No clients in DB"
```powershell
# Populer la base de données
python simulate.py --simulation --count 500
```

### Les scripts ne communiquent pas
- Vérifier que tous les 4 scripts tournent simultanément
- Vérifier la connexion MongoDB (URI correct dans .env)
- Vérifier que les collections Client/Restaurant/Menu/Livreur existent

---

## 💡 Astuces

### Modifier les taux d'acceptation
```powershell
# Restaurant accepte 100% des commandes
$env:RESTAURANT_ACCEPT_RATE=1.0
.\sim_flow\launch_all.bat

# Livreur refuse 50% des demandes
$env:LIVREUR_ACCEPT_RATE=0.5
.\sim_flow\launch_all.bat
```

### Mode verbeux (bientôt)
Ajoutez `--verbose` dans les scripts pour plus de logs

### Ralentir la simulation
Éditez `client_sim.py` et augmentez `time.sleep(3)` à la fin

---

## 📚 Ressources

- `sim_flow/README.md` - Documentation complète
- `README.md` - Documentation système complet
- `ARCHITECTURE.md` - Schémas visuels du flux

---

**🎉 Profitez de la simulation en temps réel !**

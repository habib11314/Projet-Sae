Simulation flow - 4 terminals

This folder contains four simulators to run concurrently (each in its own terminal):

1) client_sim.py    -> simulates clients creating orders
2) platform_sim.py  -> platform orchestrator: sends RestaurantRequests and DeliveryRequests
3) restaurant_sim.py-> restaurants accept/reject orders
4) livreur_sim.py   -> livreurs accept/reject delivery requests

How to run:

🚀 OPTION 1 - Launcher Python (RECOMMANDÉ):

```powershell
# Lance les 4 terminaux automatiquement
py launcher.py
```

Avantages:
✅ Portable (Windows/Linux/Mac)
✅ Détection automatique de Python
✅ Meilleurs messages d'erreur

Options avancées:
```powershell
# Tester un seul simulateur (dans ce terminal)
py launcher_advanced.py --inline client

# Lancer un seul simulateur (nouvelle fenêtre)
py launcher_advanced.py --only platform

# Voir toutes les options
py launcher_advanced.py --help
```

➡️ Guide complet: LAUNCHER_GUIDE.md

🔧 OPTION 2 - Scripts batch (Windows uniquement):

# PowerShell:
.\launch_all.ps1

# OU CMD/Batch:
.\launch_all.bat

→ Les 4 terminaux s'ouvrent automatiquement !

📝 OPTION 3 - Manuel (4 terminaux séparés):

# 1. Activate your venv
.\venv\Scripts\Activate.ps1

# 2. In Terminal 1 (Client):
python sim_flow/client_sim.py

# 3. In Terminal 2 (Platform):
python sim_flow/platform_sim.py

# 4. In Terminal 3 (Restaurant):
python sim_flow/restaurant_sim.py

# 5. In Terminal 4 (Livreur):
python sim_flow/livreur_sim.py

Configuration via environment variables (.env or environment):
- MONGODB_URI (optional, default mongodb://localhost:27017/)
- MONGODB_DATABASE (optional, default Ubereats)
- RESTAURANT_ACCEPT_RATE (optional, default 0.8)
- LIVREUR_ACCEPT_RATE (optional, default 0.7)

Notes:
- The scripts use simple polling for portability; if you want, we can rewrite them using Change Streams.
- Make sure collections `Client`, `Restaurants`, `Menu`, and `Livreur` are populated (use simulate.py or your own data).
- The scripts create `RestaurantRequests`, `DeliveryRequests`, and `Notifications` collections as needed.

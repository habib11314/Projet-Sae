# EnergyInsight Business - Aide Rapide

## 🚀 Démarrage Ultra-Rapide

### Première utilisation
1. **Double-clic** sur `menu_business.bat`
2. **Choisir option 1** : Démarrer l'application
3. **Attendre** l'ouverture automatique du navigateur
4. **Utiliser** l'application sur http://127.0.0.1:5000

### Utilisation suivante
1. **Double-clic** sur `open_business.bat`
2. **Accès direct** si l'application est déjà lancée
3. **Ou redémarrage** automatique si nécessaire

## 📁 Fichiers Importants

### Scripts de Contrôle
- `menu_business.bat` ➜ **Menu principal avec toutes les options**
- `start_business.bat` ➜ **Démarrer l'application**
- `open_business.bat` ➜ **Ouvrir sans relancer**
- `stop_business.bat` ➜ **Arrêter l'application**

### Données et Tests
- `exemple_donnees_conso_entreprise.csv` ➜ **Données d'exemple**
- `test_business.py` ➜ **Test de l'installation**

### Documentation
- `README_BUSINESS.md` ➜ **Documentation complète**
- `GUIDE_BUSINESS.md` ➜ **Guide d'utilisation**

## 🔧 Problèmes Fréquents

### Python introuvable
```
Solution: Installer Python depuis python.org
Cocher "Add Python to PATH" lors de l'installation
```

### Modules manquants
```
Solution: Le script installe automatiquement les modules
Ou manuellement: pip install -r requirements_business.txt
```

### Port 5000 occupé
```
Solution: Modifier le port dans app_business.py
Ou arrêter l'autre application utilisant le port
```

### L'application ne s'ouvre pas
```
Solutions:
1. Vérifier que Python est installé
2. Lancer test_business.py pour diagnostiquer
3. Vérifier les logs d'erreur
```

## 📊 Formats de Données

### Format Recommandé (Entreprise)
```csv
Date de relevé,Consommation HP (kWh),Consommation HC (kWh),Consommation totale (kWh),Zone,Facture estimée (€)
2024-01-01,1250,890,2140,Production,428.50
```

### Format Minimal
```csv
Date,Consumption (kWh)
2024-01-01,2140
```

## 🎯 Fonctionnalités Principales

### 1. Upload de Données
- Glisser-déposer le fichier CSV/Excel
- Validation automatique du format
- Prévisualisation des données

### 2. Analyse Automatique
- Détection des pics anormaux
- Calcul des économies potentielles
- Score d'efficacité énergétique
- Recommandations personnalisées

### 3. Visualisations
- Graphiques interactifs
- Répartition par zones
- Évolution temporelle
- Comparaisons HP/HC

### 4. Rapport PDF
- Résumé exécutif
- Recommandations chiffrées
- Plan d'action prioritaire
- Métriques détaillées

## 💡 Conseils d'Utilisation

### Préparation des Données
- Utiliser des dates au format DD/MM/YYYY ou YYYY-MM-DD
- Vérifier la cohérence des valeurs numériques
- Inclure les colonnes HP/HC si disponibles
- Spécifier les zones/secteurs pour une analyse fine

### Interprétation des Résultats
- **Score A (85-100)** : Excellente performance
- **Score B (70-84)** : Bonne performance, optimisations mineures
- **Score C (55-69)** : Performance moyenne, améliorations nécessaires
- **Score D (0-54)** : Performance faible, audit urgent

### Actions Prioritaires
1. **Immédiat** : Sensibilisation, éco-gestes
2. **Court terme** : Optimisation HP/HC, programmation
3. **Moyen terme** : Monitoring, audit zones
4. **Long terme** : Renouvellement équipements

## 📞 Support

### Auto-Diagnostic
1. Lancer `test_business.py`
2. Vérifier tous les modules
3. Tester l'analyse sur données d'exemple

### Messages d'Erreur Courants
- **"Python est introuvable"** ➜ Installer Python
- **"Modules manquants"** ➜ Installation automatique
- **"Port occupé"** ➜ Arrêter l'autre application
- **"Fichier non trouvé"** ➜ Vérifier le chemin

### Performances
- **Fichiers lourds** : Utiliser des extraits pour les tests
- **Lenteur** : Vérifier la RAM disponible
- **Graphiques** : Utiliser un navigateur récent

---

**EnergyInsight Business** - Votre solution de pilotage énergétique 🌱⚡

*Pour une aide détaillée, consultez `README_BUSINESS.md`*

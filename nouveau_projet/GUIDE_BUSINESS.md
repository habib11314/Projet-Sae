# EnergyInsight Business - Guide de Démarrage

## 🚀 Démarrage Rapide

### Méthode 1 : Double-clic
1. Double-cliquez sur `start_business.bat`
2. L'application s'ouvre automatiquement sur http://127.0.0.1:5000

### Méthode 2 : Ligne de commande
```bash
python app_business.py
```

## 📊 Fonctionnalités Stratégiques

### 🔍 Analyse Automatisée
- **Détection de pics anormaux** : Identification automatique des surconsommations
- **Analyse HP/HC** : Optimisation tarifaire heures pleines/creuses
- **Analyse par zones** : Consommation détaillée par secteur d'activité
- **Saisonnalité** : Patterns de consommation selon les périodes

### 💰 Projections Économiques
- **Coût annuel projeté** : Estimation basée sur les données historiques
- **Potentiel d'économies** : Calcul précis des gains possibles
- **ROI optimisation** : Retour sur investissement des améliorations
- **Scénarios d'économies** : Conservateur, modéré, agressif

### 🎯 Recommandations Stratégiques
- **Optimisation tarifaire** : Déplacement des usages vers les heures creuses
- **Gestion des pics** : Monitoring temps réel et délestage
- **Audit par zones** : Identification des secteurs problématiques
- **Sensibilisation** : Formation du personnel aux éco-gestes

### 📋 Plan d'Action Chronologique
1. **Actions immédiates** (0-1 mois) : Audit rapide, sensibilisation
2. **Actions court terme** (1-6 mois) : Optimisation HP/HC, programmation
3. **Actions moyen terme** (6-18 mois) : Monitoring, audit zones
4. **Actions long terme** (18+ mois) : Renouvellement équipements

## 📄 Format des Données Supportées

### Format Entreprise (Recommandé)
```csv
Date de relevé,Consommation HP (kWh),Consommation HC (kWh),Consommation totale (kWh),Zone,Facture estimée (€)
2024-01-01,1250,890,2140,Production,428.50
2024-01-02,1180,910,2090,Bureaux,418.75
```

### Format Standard
```csv
Date,Consumption (kWh)
2024-01-01,2140
2024-01-02,2090
```

## 🏢 Exemples d'Usage Professionnel

### PME (25 000€/an d'électricité)
- **Diagnostic** : 20% de consommation nocturne non utilisée
- **Problème** : Hausse de 30% en février (chauffage mal régulé)
- **Solution** : Coupure chauffage WE + détecteurs de présence
- **Résultat** : **2 500€/an d'économies** (10% du budget)

### Industrie (150 000€/an d'électricité)
- **Diagnostic** : Pics de consommation fréquents en production
- **Problème** : Ratio HP/HC non optimisé (75% en HP)
- **Solution** : Délestage automatique + reprogrammation
- **Résultat** : **18 000€/an d'économies** (12% du budget)

## 🔧 Installation et Dépannage

### Prérequis
- Python 3.7+
- Modules : Flask, Pandas, Numpy, Plotly, ReportLab

### Installation automatique
Le script `start_business.bat` installe automatiquement les dépendances manquantes.

### Dépannage
- **Python introuvable** : Vérifiez l'installation et le PATH
- **Modules manquants** : Utilisez `pip install -r requirements.txt`
- **Port occupé** : Changez le port dans `app_business.py`

## 📊 Métriques Clés

### Score d'Efficacité (0-100)
- **A (85-100)** : Excellent - Optimisation avancée
- **B (70-84)** : Bon - Améliorations mineures
- **C (55-69)** : Moyen - Optimisations nécessaires
- **D (0-54)** : Faible - Audit urgent requis

### Indicateurs Économiques
- **Coût/kWh** : Prix moyen payé
- **Variabilité** : Stabilité de la consommation
- **Pics** : Fréquence des surconsommations
- **HP/HC** : Ratio d'utilisation tarifaire

## 🎯 Objectifs d'Économies Types

### Optimisation de Base (8-15%)
- Programmation horaire
- Sensibilisation personnel
- Éco-gestes simples

### Optimisation Avancée (15-25%)
- Monitoring temps réel
- Gestion automatique des pics
- Optimisation HP/HC

### Rénovation Complète (25-40%)
- Équipements haute performance
- Isolation renforcée
- Systèmes intelligents

## 📱 Interface Web

### Dashboard Principal
- Vue d'ensemble des consommations
- Graphiques interactifs
- Alertes et recommandations

### Analyse Détaillée
- Répartition par zones
- Évolution temporelle
- Détection d'anomalies

### Rapport PDF
- Résumé exécutif
- Recommandations chiffrées
- Plan d'action détaillé

---

**EnergyInsight Business** - Votre partenaire pour l'optimisation énergétique stratégique 🌱⚡💼

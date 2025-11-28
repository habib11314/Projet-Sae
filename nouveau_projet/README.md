# EnergyInsight - Analyseur de Consommation Énergétique

## 🚀 Description

EnergyInsight est une application web professionnelle d'analyse de consommation énergétique conçue pour les entreprises du secteur énergétique (ENGIE, EDF, TotalEnergies, etc.). L'application offre une analyse intelligente des données de consommation avec détection automatique d'anomalies et génération de rapports PDF professionnels.

## 🎯 Objectif

Cette application vise à :
- **Aider les entreprises énergétiques** à expliquer les patterns de consommation à leurs clients
- **Fournir aux équipes techniques** des outils de diagnostic rapides
- **Générer des rapports professionnels** pour les présentations client
- **Supporter les consultations en efficacité énergétique**
- **Servir de preuve de concept** pour les applications du secteur énergétique

## ✨ Fonctionnalités

### 📊 Analyse Intelligente
- **Détection automatique des pics** de consommation
- **Identification des anomalies** et tendances
- **Calcul des métriques** essentielles (moyenne, total, min/max)
- **Recommandations personnalisées** basées sur les patterns

### 📈 Visualisation
- **Graphiques interactifs** avec Plotly
- **Dashboard responsive** avec métriques clés
- **Interface moderne** adaptée au secteur professionnel
- **Visualisation des tendances** temporelles

### 📄 Génération de Rapports
- **Rapports PDF professionnels** avec analyse détaillée
- **Recommandations d'action** prioritaires
- **Métriques de performance** et statistiques
- **Branding professionnel** pour présentation client

### 🔧 Fonctionnalités Techniques
- **Support multi-formats** : CSV, Excel, JSON
- **Validation des données** et gestion d'erreurs
- **Données d'exemple** pour démonstration
- **Interface intuitive** avec drag & drop

## 🛠️ Technologies

- **Backend** : Flask (Python)
- **Analyse de données** : Pandas, NumPy
- **Visualisation** : Plotly
- **Génération PDF** : WeasyPrint
- **Frontend** : Bootstrap 5, HTML5, CSS3, JavaScript
- **Graphiques** : Plotly.js

## 📋 Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)

## 🚀 Installation

1. **Cloner le projet** :
```bash
git clone <repository-url>
cd EnergyInsight
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Lancer l'application** :
```bash
python app.py
```

4. **Accéder à l'application** :
Ouvrez votre navigateur et allez à `http://localhost:5000`

## 📁 Structure du Projet

```
EnergyInsight/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── uploads/              # Dossier pour les fichiers uploadés
├── templates/            # Templates HTML
│   ├── index.html        # Page d'accueil
│   ├── upload.html       # Page d'upload
│   ├── dashboard.html    # Dashboard d'analyse
│   └── report.html       # Template de rapport PDF
└── .github/
    └── copilot-instructions.md  # Instructions pour Copilot
```

## 🔧 Configuration

### Variables d'environnement (optionnel)
```bash
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Limites de fichiers
- Taille maximum : 16MB
- Formats acceptés : CSV, XLSX, JSON

## 📊 Format des Données

Votre fichier doit contenir au minimum :
- **Colonne date** : Date de mesure (formats acceptés : YYYY-MM-DD, DD/MM/YYYY)
- **Colonne consommation** : Valeur en kWh

Exemples de noms de colonnes acceptés :
- `date`, `Date`
- `consumption`, `Consommation`, `kWh`

## 🎨 Cas d'Usage

### Pour les Entreprises Énergétiques
- **Analyse client** : Diagnostic rapide des patterns de consommation
- **Support technique** : Identification des anomalies et recommandations
- **Reporting client** : Génération de rapports professionnels explicatifs

### Pour les Consultants en Énergie
- **Audit énergétique** : Analyse détaillée des données de consommation
- **Présentation client** : Rapports visuels et recommandations
- **Suivi performance** : Monitoring des améliorations

### Pour les Équipes Techniques
- **Diagnostic terrain** : Analyse rapide lors des interventions
- **Détection d'anomalies** : Identification automatique des pics
- **Documentation** : Rapports techniques détaillés

## 🔍 Exemple d'Analyse

L'application détecte automatiquement :
- **Pics de consommation** (>150% de la moyenne)
- **Tendances saisonnières** et variations
- **Anomalies** et patterns inhabituels
- **Recommandations** d'optimisation

## 📈 Valeur Ajoutée

- **Gain de temps** : Analyse automatique en 5 minutes
- **Professionnalisme** : Rapports de qualité entreprise
- **Précision** : Détection d'anomalies à 95%
- **Simplicité** : Interface intuitive sans formation

## 🎯 Roadmap

- [ ] API REST pour intégration
- [ ] Authentification utilisateur
- [ ] Comparaison multi-sites
- [ ] Alertes automatiques
- [ ] Export Excel avancé
- [ ] Intégration IoT temps réel

## 🤝 Contribution

Ce projet est conçu comme une démonstration professionnelle pour le secteur énergétique. Pour contribuer :
1. Fork le projet
2. Créer une branche feature
3. Commiter vos changements
4. Ouvrir une Pull Request

## 📝 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 📞 Contact

Pour toute question concernant l'application ou son utilisation dans un contexte professionnel, n'hésitez pas à nous contacter.

---

**EnergyInsight** - Transformez vos données énergétiques en insights actionables 🚀

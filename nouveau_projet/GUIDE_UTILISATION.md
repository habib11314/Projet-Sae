# EnergyInsight - Guide d'Utilisation Complet

## 🚀 Version Complète avec Génération PDF

### Fonctionnalités Disponibles

✅ **Analyse Avancée avec Pandas**
- Détection automatique des pics de consommation
- Calcul de statistiques avancées (écart-type, coefficient de variation)
- Analyse des tendances temporelles
- Score d'efficacité énergétique (0-100)

✅ **Visualisations Interactives Plotly**
- Graphiques interactifs avec zoom et pan
- Moyennes mobiles et lignes de tendance
- Marquage automatique des pics
- Seuils d'alerte visuels

✅ **Génération PDF Professionnelle**
- Rapports complets avec ReportLab
- Tableaux de statistiques détaillées
- Recommandations personnalisées
- Design professionnel pour entreprises

✅ **Recommandations Intelligentes**
- Analyse contextuelle de la consommation
- Calcul du potentiel d'économie
- Priorisation des actions
- Conseils spécifiques par secteur

### URLs d'Accès

🌐 **Application principale :** `http://127.0.0.1:5000`

### Pages Disponibles

1. **Accueil** : `http://127.0.0.1:5000/`
   - Présentation de l'application
   - Accès aux fonctionnalités

2. **Upload** : `http://127.0.0.1:5000/upload`
   - Upload de fichiers CSV, Excel, JSON
   - Validation automatique des formats

3. **Dashboard** : `http://127.0.0.1:5000/dashboard/<nom_fichier>`
   - Visualisation interactive des données
   - Statistiques en temps réel
   - Graphiques Plotly avancés

4. **Génération PDF** : `http://127.0.0.1:5000/generate_report/<nom_fichier>`
   - Rapport PDF professionnel
   - Téléchargement automatique

5. **Données d'exemple** : `http://127.0.0.1:5000/sample_data`
   - API pour générer des données de test
   - Format JSON

### Formats de Fichiers Supportés

#### CSV
```csv
date,consumption
2024-01-01,145.2
2024-01-02,162.8
```

#### Excel (.xlsx)
Colonnes requises : `date`, `consumption`

#### JSON
```json
[
  {"date": "2024-01-01", "consumption": 145.2},
  {"date": "2024-01-02", "consumption": 162.8}
]
```

### Colonnes Reconnues Automatiquement

- **Date** : `date`, `Date`, `DATE`
- **Consommation** : `consumption`, `Consommation`, `kWh`, `kwh`

### Fonctionnalités Avancées

#### 1. Détection d'Anomalies
- Seuil dynamique basé sur l'écart-type
- Classification par sévérité (high/medium/low)
- Calcul du pourcentage de dépassement

#### 2. Score d'Efficacité
- Algorithme propriétaire 0-100
- Basé sur la variabilité et les pics
- Recommandations ciblées

#### 3. Analyse des Tendances
- Régression linéaire pour les tendances
- Moyennes mensuelles
- Détection des patterns saisonniers

#### 4. Recommandations IA
- Analyse contextuelle multi-critères
- Estimation des économies potentielles
- Priorisation intelligente

### Exemples d'Utilisation

#### Test Rapide
1. Démarrer l'application : `python app_complete.py`
2. Ouvrir : `http://127.0.0.1:5000`
3. Utiliser le fichier `exemple_test.csv` fourni
4. Analyser les résultats
5. Générer le rapport PDF

#### Intégration Professionnelle
1. Préparer vos données au format requis
2. Uploader via l'interface web
3. Analyser le dashboard interactif
4. Générer le rapport pour vos clients
5. Utiliser les recommandations pour l'optimisation

### Dépendances Requises

```txt
Flask==2.3.3
pandas==2.1.4
numpy==1.26.2
plotly==5.15.0
reportlab==4.0.4
```

### Commandes de Lancement

#### Windows
```powershell
C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe app_complete.py
```

#### Linux/Mac
```bash
python3 app_complete.py
```

### Résolution des Problèmes

#### Erreur "Python not found"
- Utilisez le chemin complet vers Python
- Vérifiez votre variable PATH

#### Erreur de packages
- Installez les dépendances : `pip install -r requirements.txt`
- Vérifiez les versions avec `pip list`

#### Erreur de génération PDF
- Vérifiez que ReportLab est installé
- Redémarrez l'application

### Performance et Limites

- **Taille maximale de fichier** : 16MB
- **Formats supportés** : CSV, Excel, JSON
- **Données recommandées** : 30+ points pour une analyse optimale
- **Pics détectés** : Jusqu'à 1000 pics affichés

### Support et Contact

Pour toute question ou problème :
1. Vérifiez ce guide d'utilisation
2. Consultez les logs de l'application
3. Testez avec les fichiers d'exemple fournis

---

**EnergyInsight** - Solution professionnelle d'analyse énergétique
Version complète avec génération PDF avancée

# 🚀 Comment Lancer EnergyInsight Business

## ⚡ Démarrage Rapide (3 étapes)

### 1️⃣ Installation Python (Si pas encore fait)
- Aller sur https://www.python.org/downloads/
- Télécharger Python 3.8+ pour Windows
- ⚠️ **IMPORTANT** : Cocher "Add Python to PATH" lors de l'installation
- Redémarrer l'ordinateur après installation

### 2️⃣ Lancer l'Application
**Double-clic sur l'un de ces fichiers :**
- `start_business.bat` ➜ **Démarrage complet**
- `menu_business.bat` ➜ **Menu avec options**

### 3️⃣ Utiliser l'Application
- **Navigateur s'ouvre automatiquement** sur http://127.0.0.1:5000
- **Uploader un fichier CSV/Excel** ou utiliser les données d'exemple
- **Voir l'analyse automatique** avec recommandations

---

## 🔧 Méthodes de Lancement Détaillées

### 🎯 **Méthode 1 : Fichier BAT (Recommandée)**
```
Double-clic sur : start_business.bat
```
**✅ Avantages :**
- Installation automatique des modules
- Ouverture automatique du navigateur
- Vérification de l'état de l'application

### 🎯 **Méthode 2 : Menu Principal**
```
Double-clic sur : menu_business.bat
Choisir option 1 : Démarrer l'application
```
**✅ Avantages :**
- Interface complète avec toutes les options
- Gestion avancée (start/stop/test)
- Accès à la documentation

### 🎯 **Méthode 3 : Raccourci Bureau**
```
1. Double-clic sur : create_shortcut.bat
2. Utiliser le raccourci créé sur le bureau
```
**✅ Avantages :**
- Accès rapide depuis le bureau
- Plus besoin de naviguer dans les dossiers

### 🎯 **Méthode 4 : Ligne de Commande**
```bash
# Ouvrir PowerShell/CMD dans le dossier
python app_business.py
```
**✅ Avantages :**
- Pour les utilisateurs avancés
- Voir les messages de debug

---

## 🌐 Accès à l'Application

### Une fois lancée :
- **URL** : http://127.0.0.1:5000
- **Port** : 5000 (local uniquement)
- **Interface** : Navigateur web moderne

### Pages disponibles :
- **/** ➜ Page d'accueil
- **/upload** ➜ Upload de fichiers
- **/dashboard/nomfichier** ➜ Analyse complète

---

## 📁 Fichiers de Test

### Données d'exemple fournies :
- `exemple_donnees_conso_entreprise.csv` ➜ **Format entreprise complet**
- Colonnes : Date, HP/HC, Zones, Factures
- **100 relevés** sur 6 mois
- **Différentes zones** : Production, Bureaux, etc.

### Test de l'installation :
```
Double-clic sur : test_business.py
```

---

## ❌ Problèmes Fréquents

### **"Python est introuvable"**
**Solution :**
1. Installer Python depuis python.org
2. ⚠️ Cocher "Add Python to PATH"
3. Redémarrer l'ordinateur

### **"Modules manquants"**
**Solution automatique :**
- Le script `start_business.bat` installe tout automatiquement

**Solution manuelle :**
```bash
pip install flask pandas numpy plotly reportlab
```

### **"Port 5000 occupé"**
**Solution :**
1. Arrêter l'autre application qui utilise le port
2. Ou modifier le port dans `app_business.py`

### **L'application ne s'ouvre pas**
**Solutions :**
1. Vérifier que Python est installé et dans le PATH
2. Lancer `test_business.py` pour diagnostiquer
3. Regarder les messages d'erreur dans la console

---

## 🎯 Workflow d'Utilisation

### **Première fois :**
1. **Installation Python** (si nécessaire)
2. **Double-clic** `start_business.bat`
3. **Attendre** l'installation des modules
4. **Navigateur s'ouvre** automatiquement
5. **Test** avec `exemple_donnees_conso_entreprise.csv`

### **Utilisations suivantes :**
1. **Double-clic** `start_business.bat`
2. **Application se lance** (plus rapide)
3. **Upload** vos propres données
4. **Analyser** et générer des rapports

### **Arrêt :**
- **Ctrl+C** dans la console
- **Ou** double-clic `stop_business.bat`
- **Ou** fermer la fenêtre de commande

---

## 📊 Après le Lancement

### Interface Web :
1. **Page d'accueil** : Présentation des fonctionnalités
2. **Upload** : Glisser-déposer votre fichier CSV/Excel
3. **Dashboard** : Analyse complète avec graphiques
4. **Rapport PDF** : Génération automatique

### Analyses disponibles :
- 🔍 **Pics anormaux** : Détection automatique
- 📊 **Projections économiques** : Estimations chiffrées
- 📅 **Analyse HP/HC** : Optimisation tarifaire
- 🏢 **Répartition par zones** : Consommation sectorielle
- 🎯 **Recommandations** : Plan d'action prioritaire

---

## 🆘 Aide Rapide

### Fichiers d'aide :
- `AIDE_RAPIDE.md` ➜ **Ce fichier**
- `README_BUSINESS.md` ➜ **Documentation complète**
- `GUIDE_BUSINESS.md` ➜ **Guide d'utilisation détaillé**

### Support :
1. **Tester d'abord** : `test_business.py`
2. **Vérifier** : Installation Python et modules
3. **Consulter** : Messages d'erreur dans la console

---

**🌱 EnergyInsight Business - Votre partenaire pour l'optimisation énergétique ⚡💼**

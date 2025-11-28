# 🚨 PROBLÈME DÉTECTÉ: Python non configuré

## Le problème

Quand vous lancez `launch_all.bat`, les 4 terminaux s'ouvrent mais se ferment immédiatement car:

**❌ Python n'est pas accessible dans votre PATH Windows**

## Solutions possibles

### Option 1: Installer Python (RECOMMANDÉ)

1. **Téléchargez Python 3.11+**: https://www.python.org/downloads/
2. **IMPORTANT**: Cochez "Add Python to PATH" lors de l'installation
3. Redémarrez PowerShell/CMD
4. Testez: `python --version`

### Option 2: Utiliser Python depuis le Microsoft Store

```powershell
# Installer depuis le Store
python

# Cela ouvrira le Microsoft Store, installez Python 3.11
```

### Option 3: Ajouter Python au PATH manuellement

Si Python est déjà installé mais pas dans le PATH:

1. Trouvez où Python est installé:
   ```powershell
   Get-ChildItem -Path C:\ -Filter python.exe -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
   ```

2. Ajoutez au PATH:
   - Ouvrez "Variables d'environnement Windows"
   - Modifiez la variable `Path`
   - Ajoutez: `C:\Users\VotreNom\AppData\Local\Programs\Python\Python311`
   - Ajoutez: `C:\Users\VotreNom\AppData\Local\Programs\Python\Python311\Scripts`

3. Redémarrez PowerShell

### Option 4: Utiliser `py` au lieu de `python`

Si vous avez le Python Launcher:

```powershell
# Testez
py --version

# Si ça marche, modifiez launch_all.bat:
# Remplacez "python" par "py"
```

## Une fois Python configuré

```powershell
# 1. Installer les dépendances
pip install pymongo python-dotenv faker

# 2. Modifier le fichier .env avec votre URI MongoDB
notepad .env

# 3. Peupler la base de données
python simulate.py --count 500

# 4. Lancer la simulation
cd sim_flow
.\launch_all.bat
```

## Test rapide

```powershell
# Test 1: Python accessible?
python --version

# Test 2: pip accessible?
pip --version

# Test 3: Packages installés?
pip list

# Test 4: Configuration OK?
python test_config.py
```

## Alternative: Utiliser l'ancien script d'archivage

Si vous voulez juste tester l'archivage sans simulation multi-terminaux:

```powershell
# Lancez l'archiveur simple
python archiver_commandes.py
```

---

**🎯 Une fois Python correctement installé, relancez `.\sim_flow\launch_all.bat`**

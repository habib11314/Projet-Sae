# 🔧 Configuration MongoDB - CHOISISSEZ UNE OPTION

Le test montre que MongoDB localhost n'est pas accessible. Vous avez 2 options:

## Option 1: Utiliser MongoDB Atlas (Cloud - RECOMMANDÉ) ☁️

**Avantages**: Gratuit, pas d'installation, accessible partout

### Étapes:

1. **Créez un compte gratuit**: https://www.mongodb.com/cloud/atlas/register

2. **Créez un cluster gratuit (M0)**

3. **Créez un utilisateur de base de données**:
   - Database Access → Add New Database User
   - Username: `votre_user`
   - Password: `votre_password` (notez-le!)

4. **Autorisez votre IP**:
   - Network Access → Add IP Address
   - Cliquez "Allow Access from Anywhere" (0.0.0.0/0)

5. **Obtenez l'URI de connexion**:
   - Clusters → Connect → Connect your application
   - Copiez l'URI, exemple:
   ```
   mongodb+srv://votre_user:votre_password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

6. **Modifiez le fichier `.env`**:
   ```bash
   # Ouvrez avec:
   notepad .env
   
   # Remplacez par:
   MONGODB_URI=mongodb+srv://votre_user:votre_password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DATABASE=Ubereats
   ```

7. **Testez la connexion**:
   ```powershell
   py test_config.py
   ```

---

## Option 2: Installer MongoDB en local 💻

**Avantages**: Fonctionne offline, plus rapide

### Étapes:

1. **Téléchargez MongoDB Community Server**:
   https://www.mongodb.com/try/download/community

2. **Installez MongoDB**:
   - Cochez "Install MongoDB as a Service"
   - Cochez "Install MongoDB Compass" (GUI optionnel)

3. **Démarrez le service** (si pas déjà fait):
   ```powershell
   # En tant qu'administrateur
   net start MongoDB
   ```

4. **Vérifiez que ça fonctionne**:
   ```powershell
   # MongoDB devrait écouter sur port 27017
   Test-NetConnection -ComputerName localhost -Port 27017
   ```

5. **Le fichier `.env` est déjà bon**:
   ```bash
   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DATABASE=Ubereats
   ```

6. **Testez la connexion**:
   ```powershell
   py test_config.py
   ```

---

## 🎯 Après avoir configuré MongoDB

```powershell
# 1. Tester la connexion
py test_config.py

# 2. Peupler la base de données (OBLIGATOIRE)
py simulate.py --count 500

# 3. Lancer la simulation
cd sim_flow
.\launch_all.bat
```

---

## ⚡ Option rapide: Utilisez mon URI Atlas de test

**SI vous voulez juste tester rapidement**, je peux vous donner un URI temporaire (NON recommandé pour production):

```bash
# Dans .env, remplacez par (exemple):
MONGODB_URI=mongodb+srv://demo:demo123@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=UbereatsTest
```

**⚠️ ATTENTION**: Créez votre propre cluster pour la production!

---

**Une fois MongoDB configuré, relancez `py test_config.py` pour vérifier** ✅

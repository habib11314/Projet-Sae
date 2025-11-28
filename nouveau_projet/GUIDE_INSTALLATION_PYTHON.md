# Guide d'installation Python pour EnergyInsight

## Problème rencontré
L'application EnergyInsight ne peut pas démarrer car Python n'est pas correctement installé ou configuré.

## Solutions (par ordre de préférence)

### 1. Installation automatique (RECOMMANDÉ)
```
1. Double-cliquez sur install_python_auto.bat
2. Attendez la fin de l'installation
3. Redémarrez votre ordinateur
4. Lancez start_business.bat
```

### 2. Diagnostic des problèmes
```
1. Double-cliquez sur diagnostic_python.bat
2. Suivez les instructions affichées
3. Corrigez les problèmes détectés
```

### 3. Installation manuelle
```
1. Allez sur https://www.python.org/downloads/
2. Téléchargez Python 3.11 ou plus récent
3. Lancez l'installateur
4. IMPORTANT: Cochez "Add Python to PATH"
5. Cliquez sur "Install Now"
6. Redémarrez votre ordinateur
7. Relancez start_business.bat
```

## Messages d'erreur courants

### "Python est introuvable"
- Solution: Suivez l'installation automatique ou manuelle ci-dessus

### "Impossible d'installer les modules requis"
- Solution: Exécutez diagnostic_python.bat et suivez les instructions

### "L'application est déjà en cours d'exécution"
- Solution: Ouvrez http://127.0.0.1:5000 dans votre navigateur

## Vérification du succès

Une fois Python installé, vous devriez voir :
```
Python détecté: py
Vérification des modules requis...
Démarrage d'EnergyInsight BUSINESS...
Application disponible sur: http://127.0.0.1:5000
```

## Support

Si les problèmes persistent :
1. Redémarrez votre ordinateur
2. Exécutez diagnostic_python.bat
3. Vérifiez que vous avez les droits administrateur
4. Désactivez temporairement l'antivirus pendant l'installation

## Fichiers d'aide créés

- `install_python_auto.bat` : Installation automatique de Python
- `diagnostic_python.bat` : Diagnostic des problèmes Python
- `start_business.bat` : Lancement de l'application
- `GUIDE_INSTALLATION_PYTHON.md` : Ce guide

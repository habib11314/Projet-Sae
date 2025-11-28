#!/usr/bin/env python3
"""
StatEnergie - Script de diagnostic des dépendances PDF
"""

import sys
import os
import importlib.util

def check_dependency(module_name):
    """Vérifie si un module est installé et retourne sa version si disponible"""
    is_installed = importlib.util.find_spec(module_name) is not None
    version = None
    
    if is_installed:
        try:
            module = __import__(module_name)
            if hasattr(module, '__version__'):
                version = module.__version__
            elif hasattr(module, 'version'):
                version = module.version
        except ImportError:
            is_installed = False
    
    return is_installed, version

def main():
    """Affiche l'état des dépendances PDF"""
    print("=== Diagnostic des dépendances PDF pour StatEnergie ===")
    print(f"Python version: {sys.version}")
    print(f"Exécution depuis: {os.getcwd()}")
    print("\nVérification des bibliothèques PDF:")
    
    dependencies = [
        "PyPDF2",
        "pdfplumber",
        "reportlab"
    ]
    
    all_installed = True
    
    for dep in dependencies:
        is_installed, version = check_dependency(dep)
        status = f"INSTALLÉ (version {version})" if is_installed else "NON INSTALLÉ"
        print(f"- {dep}: {status}")
        
        if not is_installed:
            all_installed = False
    
    print("\n=== Résultat ===")
    if all_installed:
        print("✅ Toutes les dépendances PDF sont installées.")
        print("Si vous rencontrez encore des erreurs, vérifiez les permissions et les chemins d'accès.")
    else:
        print("❌ Certaines dépendances PDF ne sont pas installées.")
        print("Solution: Exécutez la commande suivante pour installer toutes les dépendances:")
        print("pip install -r requirements.txt")
        print("ou installez individuellement les bibliothèques manquantes avec:")
        print("pip install PyPDF2 pdfplumber reportlab")

if __name__ == "__main__":
    main()

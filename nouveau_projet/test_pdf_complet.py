#!/usr/bin/env python3
"""
Test complet de la génération PDF avec analyse réelle
"""

import pandas as pd
import sys
import os

# Ajouter le répertoire courant au PATH pour importer les fonctions
sys.path.append('.')

# Importer les fonctions depuis app.py
from app import analyze_consumption_data, generate_professional_pdf

def test_complete_pdf_generation():
    """Test complet de génération PDF avec des données réelles"""
    print("🧪 Test complet de génération PDF avec données réelles...")
    
    # Charger le fichier d'exemple
    try:
        df = pd.read_csv('exemple_donnees_conso_entreprise.csv')
        print(f"✅ Fichier chargé: {len(df)} lignes")
        print(f"📊 Colonnes: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du fichier: {e}")
        return False
    
    # Analyser les données
    try:
        print("\n🔍 Analyse des données...")
        analysis = analyze_consumption_data(df)
        print("✅ Analyse terminée")
        
        # Afficher quelques statistiques
        if 'basic_stats' in analysis:
            stats = analysis['basic_stats']
            print(f"📈 Consommation moyenne: {stats.get('avg_consumption', 'N/A'):.1f} kWh")
            print(f"📊 Pics détectés: {len(analysis.get('peaks', []))}")
            print(f"💡 Recommandations: {len(analysis.get('recommendations', []))}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Générer le PDF
    try:
        print("\n📄 Génération du PDF...")
        pdf_buffer = generate_professional_pdf(analysis, 'exemple_donnees_conso_entreprise.csv', df)
        
        # Sauvegarder le PDF
        with open('rapport_test_complet.pdf', 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print("✅ PDF généré avec succès: rapport_test_complet.pdf")
        
        # Vérifier la taille du fichier
        file_size = os.path.getsize('rapport_test_complet.pdf')
        print(f"📦 Taille du fichier: {file_size} bytes")
        
        if file_size > 1000:  # Au moins 1KB
            print("✅ Le PDF semble valide (taille correcte)")
            return True
        else:
            print("⚠️  Le PDF semble trop petit")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la génération PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_generation():
    """Test de l'URL de génération PDF"""
    print("\n🌐 Test de l'URL de génération PDF...")
    
    import requests
    try:
        response = requests.get('http://127.0.0.1:5000/generate_report/exemple_donnees_conso_entreprise.csv', 
                              timeout=30)
        
        if response.status_code == 200:
            print("✅ URL de génération PDF fonctionne")
            print(f"📦 Taille de la réponse: {len(response.content)} bytes")
            
            # Sauvegarder le PDF depuis l'URL
            with open('rapport_url_test.pdf', 'wb') as f:
                f.write(response.content)
            print("✅ PDF téléchargé depuis l'URL: rapport_url_test.pdf")
            return True
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"📝 Contenu: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test URL: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test complet de la génération PDF EnergyInsight")
    print("=" * 60)
    
    # Test 1: Génération directe
    success1 = test_complete_pdf_generation()
    
    # Test 2: Génération via URL (nécessite que l'app soit lancée)
    success2 = test_url_generation()
    
    print("\n" + "=" * 60)
    print("📋 RÉSULTATS:")
    print(f"  ✅ Génération directe: {'SUCCÈS' if success1 else 'ÉCHEC'}")
    print(f"  ✅ Génération via URL: {'SUCCÈS' if success2 else 'ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS - La génération PDF fonctionne parfaitement!")
    elif success1:
        print("\n⚠️  La génération directe fonctionne, mais vérifiez que l'application Flask est lancée")
    else:
        print("\n❌ Problèmes détectés - vérifiez les erreurs ci-dessus")

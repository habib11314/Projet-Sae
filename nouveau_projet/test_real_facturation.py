#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test avec le vrai fichier facturation.csv
"""

import pandas as pd
import traceback
from app import analyze_consumption_data, detect_data_format

def test_real_facturation():
    """Test avec le vrai fichier facturation"""
    print("🧪 Test avec le vrai fichier facturation.csv")
    
    try:
        # Charger le fichier
        df = pd.read_csv('facturation.csv')
        print(f"📊 DataFrame chargé: {df.shape}")
        print(f"📋 Colonnes: {list(df.columns)}")
        print(f"🔍 Aperçu:\n{df.head()}")
        
        # Test de détection de format
        print(f"\n🔍 Test détection format...")
        data_format = detect_data_format(df)
        print(f"🎯 Format détecté: {data_format}")
        
        # Test de l'analyse complète
        print("\n🔍 Lancement de l'analyse complète...")
        result = analyze_consumption_data(df)
        
        if 'error' in result:
            print(f"❌ Erreur dans l'analyse: {result['error']}")
            return False
        
        print("✅ Analyse réussie!")
        print(f"📊 Type de résultat: {type(result)}")
        print(f"🔑 Clés disponibles: {list(result.keys()) if isinstance(result, dict) else 'Non dict'}")
        
        if 'basic_stats' in result:
            print(f"📈 Basic stats: {result['basic_stats']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        print("📋 Stack trace:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_real_facturation()

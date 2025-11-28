#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test pour identifier l'erreur 'dict object' has no attribute 'total_consumption'
"""

import pandas as pd
import traceback
from app import analyze_consumption_data

def test_facturation():
    """Test avec un fichier facturation"""
    print("🧪 Test analyse facturation")
    
    # Créer des données de test facturation
    data = {
        'Mois': ['2024-01', '2024-02', '2024-03', '2024-04'],
        'Site': ['Site A', 'Site B', 'Site A', 'Site B'], 
        'Consommation (kWh)': [1500, 1200, 1800, 1100],
        'Montant facturé (€)': [300, 240, 360, 220]
    }
    
    df = pd.DataFrame(data)
    print(f"📊 DataFrame créé: {df.shape}")
    print(f"📋 Colonnes: {list(df.columns)}")
    print(f"🔍 Aperçu:\n{df}")
    
    try:
        # Test de l'analyse
        print("\n🔍 Lancement de l'analyse...")
        result = analyze_consumption_data(df)
        
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
    test_facturation()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test diagnostic pour le fichier facturation.csv
"""

import pandas as pd
import sys
import os

def test_facturation_diagnostic():
    """Diagnostic complet du fichier facturation.csv"""
    print("🔍 DIAGNOSTIC FICHIER FACTURATION.CSV")
    print("=" * 60)
    
    try:
        # 1. Charger le fichier
        df = pd.read_csv('facturation.csv')
        print(f"✅ Fichier chargé: {df.shape}")
        print(f"📋 Colonnes originales: {list(df.columns)}")
        
        # 2. Afficher les premières lignes
        print(f"\n📄 Aperçu des données:")
        print(df.head())
        
        # 3. Tester la détection de format
        sys.path.append('.')
        from app import detect_data_format
        
        format_detected = detect_data_format(df)
        print(f"\n🎯 Format détecté: {format_detected}")
        
        # 4. Tester la standardisation
        from app import standardize_columns
        
        df_std = standardize_columns(df, format_detected)
        print(f"\n📋 Colonnes après standardisation: {list(df_std.columns)}")
        print(f"📄 Aperçu standardisé:")
        print(df_std.head())
        
        # 5. Vérifier les colonnes clés
        if 'consumption' in df_std.columns:
            print(f"\n✅ Colonne 'consumption' trouvée")
            print(f"📊 Valeurs consumption: {df_std['consumption'].head()}")
            print(f"📊 Type consumption: {df_std['consumption'].dtype}")
        else:
            print(f"\n❌ Colonne 'consumption' manquante !")
        
        if 'fournisseur' in df_std.columns:
            print(f"✅ Colonne 'fournisseur' trouvée")
            print(f"📊 Fournisseurs: {df_std['fournisseur'].unique()}")
        else:
            print(f"❌ Colonne 'fournisseur' manquante")
        
        # 6. Tester l'analyseur
        from analyzers_specialized import analyze_factures_normalisees
        
        print(f"\n🧪 Test de l'analyseur...")
        results = analyze_factures_normalisees(df_std)
        
        print(f"✅ Analyse réussie!")
        print(f"📊 Format: {results['data_format']}")
        print(f"📊 Stats de base: {results['basic_stats']}")
        print(f"💡 Nb recommandations: {len(results['recommendations'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_facturation_diagnostic()

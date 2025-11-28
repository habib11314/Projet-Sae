#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de diagnostic pour les factures normalisées
"""

import pandas as pd
from app import detect_data_format, standardize_columns

def test_factures_diagnostic():
    """Diagnostic des factures normalisées"""
    print("🔬 DIAGNOSTIC FACTURES NORMALISÉES")
    print("=" * 50)
    
    try:
        # Charger le fichier RÉEL utilisé dans les tests
        df = pd.read_csv('facturation.csv')
        print(f"📊 Données chargées: {df.shape}")
        print(f"📋 Colonnes originales: {list(df.columns)}")
        print(f"📄 Aperçu:")
        print(df.head(2))
        
        # Test détection format
        format_detecte = detect_data_format(df)
        print(f"🎯 Format détecté: {format_detecte}")
        
        # Test standardisation
        df_std = standardize_columns(df, format_detecte)
        print(f"📋 Colonnes après standardisation: {list(df_std.columns)}")
        
        # Vérifier les colonnes essentielles
        if 'consumption' in df_std.columns:
            print(f"✅ Colonne consumption présente: {df_std['consumption'].sum():.1f}")
        else:
            print("❌ Colonne consumption manquante")
            if 'hp_consumption' in df_std.columns and 'hc_consumption' in df_std.columns:
                total = df_std['hp_consumption'].sum() + df_std['hc_consumption'].sum()
                print(f"⚠️  HP+HC disponibles: {total:.1f}")
        
        if 'fournisseur' in df_std.columns:
            print(f"✅ Colonne fournisseur présente: {df_std['fournisseur'].unique()}")
        else:
            print("❌ Colonne fournisseur manquante")
        
        # Test de l'analyseur
        print("\n🔍 Test de l'analyseur...")
        from analyzers_specialized import analyze_factures_normalisees
        
        results = analyze_factures_normalisees(df_std)
        print(f"✅ Analyse réussie!")
        print(f"📊 Basic stats: {list(results['basic_stats'].keys())}")
        print(f"💡 Recommandations: {len(results['recommendations'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_factures_diagnostic()

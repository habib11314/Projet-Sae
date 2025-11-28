#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des 3 nouveaux formats spécialisés
"""

import pandas as pd
from app import analyze_consumption_data

def test_format(filename, description):
    """Test un format spécifique"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {description}")
    print(f"📁 Fichier: {filename}")
    print(f"{'='*80}")
    
    try:
        df = pd.read_csv(filename)
        print(f"📊 Données chargées: {df.shape}")
        print(f"📋 Colonnes: {list(df.columns)}")
        print(f"🔍 Aperçu:")
        print(df.head(3))
        
        print(f"\n🔍 Analyse en cours...")
        results = analyze_consumption_data(df)
        
        if 'error' in results:
            print(f"❌ Erreur: {results['error']}")
            return False
        
        print(f"✅ Format détecté: {results['data_format']}")
        print(f"📊 Nom du format: {results['file_info'].get('format_name', 'N/A')}")
        
        if 'basic_stats' in results:
            stats = results['basic_stats']
            print(f"📈 Consommation totale: {stats.get('total_consumption', 0):.1f} kWh")
            print(f"📈 Consommation moyenne: {stats.get('avg_consumption', 0):.1f} kWh")
        
        if results.get('recommendations'):
            print(f"💡 Recommandations: {len(results['recommendations'])}")
            for i, reco in enumerate(results['recommendations'][:2], 1):
                print(f"  {i}. {reco.get('action', 'N/A')}")
        
        print(f"🎉 Test réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test des 3 formats"""
    print("🚀 TEST DES 3 FORMATS STANDARDS DU SECTEUR ÉNERGÉTIQUE")
    
    tests = [
        ("exemple_grdf_courbe_charge.csv", "Format GRD-F / Courbes de charge"),
        ("exemple_factures_normalisees.csv", "Format Factures Normalisées"),
        ("exemple_ademe_iso50001.csv", "Format ADEME / ISO 50001")
    ]
    
    results = []
    for filename, description in tests:
        success = test_format(filename, description)
        results.append((filename, success))
    
    print(f"\n{'='*80}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*80}")
    
    for filename, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"  {filename}: {status}")
    
    total_success = sum(1 for _, success in results if success)
    print(f"\n🎯 RÉSULTAT: {total_success}/{len(results)} formats fonctionnels")

if __name__ == "__main__":
    main()

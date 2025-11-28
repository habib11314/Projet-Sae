#!/usr/bin/env python3
"""
Test comparatif entre sample_data.csv et exemple_donnees_conso_entreprise.csv
"""

import pandas as pd
import sys
sys.path.append('.')

from app import detect_data_format, standardize_columns, analyze_consumption_data, create_advanced_chart

def compare_files():
    print("🔍 COMPARAISON DES DEUX FICHIERS")
    print("=" * 80)
    
    # Charger les deux fichiers
    print("\n📁 Chargement des fichiers...")
    
    # Sample data
    print("\n🔹 SAMPLE_DATA.CSV:")
    try:
        df_sample = pd.read_csv('sample_data.csv')
        print(f"  📊 Colonnes: {list(df_sample.columns)}")
        print(f"  📏 Dimensions: {df_sample.shape}")
        print(f"  🔍 Aperçu:")
        print(f"    {df_sample.head(3).to_string()}")
        
        # Détection format
        format_sample = detect_data_format(df_sample)
        print(f"  🎯 Format détecté: {format_sample}")
        
        # Standardisation
        df_sample_std = standardize_columns(df_sample, format_sample)
        print(f"  🔄 Colonnes après standardisation: {list(df_sample_std.columns)}")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return
    
    # Exemple entreprise
    print("\n🔹 EXEMPLE_DONNEES_CONSO_ENTREPRISE.CSV:")
    try:
        df_entreprise = pd.read_csv('exemple_donnees_conso_entreprise.csv')
        print(f"  📊 Colonnes: {list(df_entreprise.columns)}")
        print(f"  📏 Dimensions: {df_entreprise.shape}")
        print(f"  🔍 Aperçu:")
        print(f"    {df_entreprise.head(2).to_string()}")
        
        # Détection format
        format_entreprise = detect_data_format(df_entreprise)
        print(f"  🎯 Format détecté: {format_entreprise}")
        
        # Standardisation
        df_entreprise_std = standardize_columns(df_entreprise, format_entreprise)
        print(f"  🔄 Colonnes après standardisation: {list(df_entreprise_std.columns)}")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return
    
    # Analyse comparative
    print("\n" + "=" * 80)
    print("🧪 ANALYSE COMPARATIVE")
    print("=" * 80)
    
    # Analyse sample_data
    print("\n🔹 ANALYSE SAMPLE_DATA:")
    try:
        analysis_sample = analyze_consumption_data(df_sample)
        print(f"  📈 Consommation moyenne: {analysis_sample.get('avg_consumption', 'N/A'):.1f} kWh")
        print(f"  📊 Pics détectés: {len(analysis_sample.get('peaks', []))}")
        print(f"  🎯 Format final: {analysis_sample.get('data_format', 'N/A')}")
        print(f"  📋 Colonnes dans DF final: {analysis_sample.get('file_info', {}).get('columns_detected', [])}")
        
        # Test graphique
        try:
            chart_sample = create_advanced_chart(df_sample_std, analysis_sample)
            print(f"  📈 Graphique: {'✅ GÉNÉRÉ' if chart_sample else '❌ ÉCHEC'}")
        except Exception as e:
            print(f"  📈 Graphique: ❌ ERREUR - {e}")
            
    except Exception as e:
        print(f"  ❌ Erreur analyse: {e}")
    
    # Analyse exemple entreprise
    print("\n🔹 ANALYSE EXEMPLE ENTREPRISE:")
    try:
        analysis_entreprise = analyze_consumption_data(df_entreprise)
        print(f"  📈 Consommation moyenne: {analysis_entreprise.get('avg_consumption', 'N/A'):.1f} kWh")
        print(f"  📊 Pics détectés: {len(analysis_entreprise.get('peaks', []))}")
        print(f"  🎯 Format final: {analysis_entreprise.get('data_format', 'N/A')}")
        print(f"  📋 Colonnes dans DF final: {analysis_entreprise.get('file_info', {}).get('columns_detected', [])}")
        
        # Test graphique
        try:
            chart_entreprise = create_advanced_chart(df_entreprise_std, analysis_entreprise)
            print(f"  📈 Graphique: {'✅ GÉNÉRÉ' if chart_entreprise else '❌ ÉCHEC'}")
        except Exception as e:
            print(f"  📈 Graphique: ❌ ERREUR - {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"  ❌ Erreur analyse: {e}")
        import traceback
        traceback.print_exc()
    
    # Conclusion
    print("\n" + "=" * 80)
    print("🎯 DIAGNOSTIC")
    print("=" * 80)
    
    if format_sample != format_entreprise:
        print(f"🔍 DIFFÉRENCE DE FORMAT DÉTECTÉE:")
        print(f"   📁 sample_data.csv → {format_sample}")
        print(f"   📁 exemple_entreprise.csv → {format_entreprise}")
        print(f"💡 C'est pourquoi vous avez des analyses différentes !")
    else:
        print(f"🔍 Même format détecté: {format_sample}")
        print(f"💡 Le problème vient probablement de la génération du graphique ou des données")

if __name__ == "__main__":
    compare_files()

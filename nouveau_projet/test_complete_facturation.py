#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet avec génération de graphique pour facturation
"""

import pandas as pd
import traceback
from app import analyze_consumption_data, create_advanced_chart

def test_complete_facturation():
    """Test complet avec génération de graphique"""
    print("🧪 Test complet avec graphique - facturation.csv")
    
    try:
        # Charger le fichier
        df = pd.read_csv('facturation.csv')
        print(f"📊 DataFrame chargé: {df.shape}")
        print(f"📋 Colonnes: {list(df.columns)}")
        
        # Test de l'analyse complète
        print("\n🔍 Lancement de l'analyse complète...")
        analysis = analyze_consumption_data(df)
        
        if 'error' in analysis:
            print(f"❌ Erreur dans l'analyse: {analysis['error']}")
            return False
        
        print("✅ Analyse réussie!")
        
        # Test de génération de graphique
        print("\n📈 Test génération de graphique...")
        
        # Préparer le DataFrame pour le graphique
        # Il faut ajouter une colonne date et consumption pour le graphique
        df_graph = df.copy()
        df_graph['date'] = pd.to_datetime(df_graph['Mois'] + '-01')  # Convertir mois en date
        df_graph['consumption'] = df_graph['Consommation totale (kWh)']
        
        chart_data = create_advanced_chart(df_graph, analysis)
        
        if chart_data:
            print("✅ Graphique généré avec succès!")
        else:
            print("❌ Échec génération graphique")
            return False
        
        # Afficher les recommandations
        if 'recommendations' in analysis and analysis['recommendations']:
            print(f"\n💡 Recommandations ({len(analysis['recommendations'])}):")
            for i, reco in enumerate(analysis['recommendations'][:3], 1):
                print(f"  {i}. {reco.get('action', 'N/A')}")
        
        # Afficher les économies potentielles
        if 'cost_analysis' in analysis and 'potential_savings' in analysis['cost_analysis']:
            savings = analysis['cost_analysis']['potential_savings']
            total_savings = savings.get('total_annuel', 0)
            print(f"\n💰 Économies potentielles: {total_savings:.2f}€/an")
        
        print("\n🎉 Test complet réussi!")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        print("📋 Stack trace:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_complete_facturation()

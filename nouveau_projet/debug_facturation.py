#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de debugging approfondi pour identifier l'erreur exacte
"""

import pandas as pd
import traceback
import sys
import os

def debug_facturation_error():
    """Debug approfondi pour identifier où se produit l'erreur"""
    print("🐛 DEBUG APPROFONDI - FACTURATION")
    print("=" * 60)
    
    try:
        # Importer les fonctions une par une pour identifier laquelle plante
        print("📦 1. Import des modules...")
        
        from app import analyze_consumption_data
        print("✅ analyze_consumption_data importé")
        
        from app import create_advanced_chart  
        print("✅ create_advanced_chart importé")
        
        from app import generate_professional_pdf
        print("✅ generate_professional_pdf importé")
        
        # Charger le fichier
        print("\n📂 2. Chargement du fichier...")
        df = pd.read_csv('facturation.csv')
        print(f"✅ Fichier chargé: {df.shape}")
        print(f"📋 Colonnes: {list(df.columns)}")
        
        # Test de l'analyse
        print("\n🔍 3. Test analyze_consumption_data...")
        analysis = analyze_consumption_data(df)
        print("✅ analyze_consumption_data réussi")
        
        print(f"📊 Type d'analysis: {type(analysis)}")
        print(f"🔑 Clés dans analysis: {list(analysis.keys()) if isinstance(analysis, dict) else 'PAS UN DICT'}")
        
        if 'error' in analysis:
            print(f"❌ Erreur dans analysis: {analysis['error']}")
            return False
        
        # Test du graphique avec debug
        print("\n📈 4. Test create_advanced_chart...")
        
        # Préparer le DataFrame pour le graphique
        df_chart = df.copy()
        df_chart['date'] = pd.to_datetime(df['Mois'] + '-01')
        df_chart['consumption'] = df['Consommation totale (kWh)']
        
        print(f"📊 DataFrame pour graphique: {df_chart.shape}")
        print(f"📋 Colonnes pour graphique: {list(df_chart.columns)}")
        
        # Tester la génération du graphique
        try:
            chart_json = create_advanced_chart(df_chart, analysis)
            if chart_json:
                print("✅ create_advanced_chart réussi")
            else:
                print("⚠️  create_advanced_chart retourne None")
        except Exception as chart_error:
            print(f"❌ Erreur dans create_advanced_chart: {str(chart_error)}")
            print("📋 Traceback create_advanced_chart:")
            traceback.print_exc()
            
        # Test de la génération PDF
        print("\n📄 5. Test generate_professional_pdf...")
        try:
            pdf_buffer = generate_professional_pdf(analysis, 'facturation.csv', df)
            if pdf_buffer:
                print("✅ generate_professional_pdf réussi")
            else:
                print("⚠️  generate_professional_pdf retourne None")
        except Exception as pdf_error:
            print(f"❌ Erreur dans generate_professional_pdf: {str(pdf_error)}")
            print("📋 Traceback generate_professional_pdf:")
            traceback.print_exc()
        
        # Inspection détaillée de la structure analysis
        print("\n🔍 6. Inspection détaillée de 'analysis'...")
        
        if isinstance(analysis, dict):
            for key, value in analysis.items():
                print(f"🔑 {key}: {type(value)} - {str(value)[:100]}...")
                
                # Si c'est basic_stats, l'inspecter
                if key == 'basic_stats' and isinstance(value, dict):
                    print("   📊 Contenu basic_stats:")
                    for subkey, subvalue in value.items():
                        print(f"      - {subkey}: {subvalue}")
        
        print("\n🎉 Debug terminé sans erreur fatale")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR DANS LE DEBUG: {str(e)}")
        print(f"📋 Type d'erreur: {type(e).__name__}")
        print("📝 Traceback complet:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_facturation_error()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet simulant l'upload web pour facturation
"""

import pandas as pd
import traceback
import os
from app import analyze_consumption_data, create_advanced_chart

def simulate_web_upload():
    """Simule exactement ce qui se passe lors d'un upload web"""
    print("🧪 SIMULATION COMPLÈTE D'UPLOAD WEB")
    print("=" * 60)
    
    file_path = 'facturation.csv'
    
    try:
        # 1. Lire le fichier comme le fait l'interface web
        print("📂 1. Lecture du fichier (comme l'interface web)...")
        
        # Essayer différents encodages comme dans l'interface web
        df = None
        for encoding in ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"✅ Fichier lu avec l'encodage: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
            print("⚠️  Fichier lu avec gestion d'erreurs d'encodage")
        
        print(f"📊 Colonnes détectées: {list(df.columns)}")
        print(f"📏 Dimensions: {df.shape}")
        print(f"🔍 Aperçu des premières lignes:")
        print(df.head())
        
        # 2. Analyse comme dans l'interface web
        print("\n🔄 2. Démarrage de l'analyse (comme l'interface web)...")
        try:
            analysis = analyze_consumption_data(df)
            print("✅ Analyse terminée avec succès")
            
            if 'error' in analysis:
                print(f"❌ Erreur dans l'analyse: {analysis['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur pendant l'analyse: {str(e)}")
            print(f"📋 Type d'erreur: {type(e).__name__}")
            traceback.print_exc()
            return False
        
        # 3. Génération du graphique comme dans l'interface web
        print("\n📈 3. Génération du graphique (comme l'interface web)...")
        try:
            # Créer une copie du DataFrame avec les colonnes nécessaires
            df_for_chart = df.copy()
            
            # Pour les fichiers facturation, on doit ajouter les colonnes attendues
            if 'Mois' in df.columns:
                df_for_chart['date'] = pd.to_datetime(df['Mois'] + '-01')
            
            if 'Consommation totale (kWh)' in df.columns:
                df_for_chart['consumption'] = df['Consommation totale (kWh)']
            elif 'Consommation (kWh)' in df.columns:
                df_for_chart['consumption'] = df['Consommation (kWh)']
            
            chart_data = create_advanced_chart(df_for_chart, analysis)
            
            if chart_data:
                print("✅ Graphique généré avec succès")
            else:
                print("❌ Échec génération graphique")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la génération du graphique: {str(e)}")
            traceback.print_exc()
            return False
        
        # 4. Vérification des données retournées
        print("\n📊 4. Vérification des données retournées...")
        
        print(f"🔑 Clés disponibles: {list(analysis.keys())}")
        
        if 'basic_stats' in analysis:
            print(f"📈 Basic stats: {analysis['basic_stats']}")
        
        if 'recommendations' in analysis and analysis['recommendations']:
            print(f"💡 Recommandations: {len(analysis['recommendations'])}")
            for i, reco in enumerate(analysis['recommendations'][:2], 1):
                print(f"  {i}. {reco.get('action', 'N/A')}")
        
        if 'cost_analysis' in analysis:
            cost = analysis['cost_analysis']
            print(f"💰 Analyse coût - Total: {cost.get('total_cost', 0):.2f}€")
            if 'potential_savings' in cost:
                savings = cost['potential_savings'].get('total_annuel', 0)
                print(f"💰 Économies potentielles: {savings:.2f}€/an")
        
        print("\n🎉 SIMULATION COMPLÈTE RÉUSSIE !")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR GÉNÉRALE: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simulate_web_upload()
    if success:
        print("\n✅ Le problème facturation semble résolu !")
    else:
        print("\n❌ Le problème persiste...")

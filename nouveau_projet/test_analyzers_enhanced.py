#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des analyseurs enrichis
"""

import pandas as pd
import json

def test_enhanced_analyzers():
    """Test les 3 analyseurs enrichis"""
    print("🧪 TEST DES ANALYSEURS ENRICHIS")
    print("=" * 60)
    
    # Test 1: GRD-F
    print("\n📊 1. Test GRD-F enrichi...")
    try:
        from analyzers_specialized import analyze_grdf_courbe_charge
        
        df_grdf = pd.read_csv('exemple_grdf_courbe_charge.csv')
        results = analyze_grdf_courbe_charge(df_grdf)
        
        print(f"✅ Format: {results['data_format']}")
        print(f"📈 Consommation totale: {results['basic_stats']['total_consumption']:.1f} kWh")
        print(f"⚡ Pics détectés: {len(results['peaks'])}")
        print(f"💡 Recommandations: {len(results['recommendations'])}")
        
        if results['recommendations']:
            print(f"🎯 Première recommandation: {results['recommendations'][0]['category']}")
            if 'roi_estime' in results['recommendations'][0]:
                print(f"💰 ROI estimé: {results['recommendations'][0]['roi_estime']}")
        
        if 'energy_efficiency' in results:
            print(f"📊 Score efficacité: {results['energy_efficiency']['performance_globale']['note_efficacite']}/10")
        
    except Exception as e:
        print(f"❌ Erreur GRD-F: {e}")
    
    # Test 2: Factures
    print("\n💰 2. Test Factures enrichi...")
    try:
        from analyzers_specialized import analyze_factures_normalisees
        
        df_factures = pd.read_csv('exemple_factures_normalisees.csv')
        results = analyze_factures_normalisees(df_factures)
        
        print(f"✅ Format: {results['data_format']}")
        print(f"💳 Montant total: {results['cost_analysis']['montant_total_factures']:.2f}€")
        print(f"🏢 Fournisseurs: {results['basic_stats']['nb_fournisseurs']}")
        print(f"💡 Recommandations: {len(results['recommendations'])}")
        
        if 'supplier_analysis' in results:
            supplier_analysis = results['supplier_analysis']
            print(f"💸 Moins cher: {supplier_analysis['fournisseur_le_moins_cher']}")
            print(f"💸 Plus cher: {supplier_analysis['fournisseur_le_plus_cher']}")
        
        if 'contract_optimization' in results:
            print(f"💰 Économie potentielle: {results['contract_optimization']['potentiel_economie_total']:.0f}€/an")
        
    except Exception as e:
        print(f"❌ Erreur Factures: {e}")
    
    # Test 3: ADEME/ISO
    print("\n🌱 3. Test ADEME/ISO enrichi...")
    try:
        from analyzers_specialized import analyze_ademe_iso50001
        
        df_ademe = pd.read_csv('exemple_ademe_iso50001.csv')
        results = analyze_ademe_iso50001(df_ademe)
        
        print(f"✅ Format: {results['data_format']}")
        print(f"📊 Indicateurs: {results['basic_stats']['nb_indicateurs']}")
        print(f"💡 Recommandations: {len(results['recommendations'])}")
        
        if 'iso_compliance' in results:
            iso = results['iso_compliance']
            print(f"📋 Score conformité ISO: {iso['score_conformite']:.1f}%")
            print(f"🎯 Niveau: {iso['niveau_certification']}")
        
        if 'performance_tracking' in results:
            perf = results['performance_tracking']
            print(f"✅ Objectifs atteints: {perf['objectifs_atteints']}")
            print(f"❌ Objectifs dépassés: {perf['objectifs_depasses']}")
        
        if 'improvement_plan' in results:
            plan = results['improvement_plan']
            print(f"🎯 Actions prioritaires: {len(plan['actions_prioritaires'])}")
            print(f"💰 Budget estimé: {plan['budget_estime']:.0f}€")
        
    except Exception as e:
        print(f"❌ Erreur ADEME: {e}")
    
    print("\n🎉 Tests terminés!")

if __name__ == "__main__":
    test_enhanced_analyzers()

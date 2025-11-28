#!/usr/bin/env python3
"""
Test des améliorations économiques d'EnergyInsight
"""

import pandas as pd
import sys
sys.path.append('.')

from app import analyze_consumption_data, generate_professional_pdf

def test_economic_improvements():
    print("💰 TEST DES AMÉLIORATIONS ÉCONOMIQUES")
    print("=" * 60)
    
    # Test avec le fichier entreprise (plus de données économiques)
    print("\n📊 Test avec exemple_donnees_conso_entreprise.csv...")
    
    try:
        # Charger le fichier
        df = pd.read_csv('exemple_donnees_conso_entreprise.csv')
        print(f"✅ Fichier chargé: {len(df)} lignes")
        
        # Analyser avec les nouvelles fonctions économiques
        print("\n🔍 Analyse économique avancée...")
        analysis = analyze_consumption_data(df)
        
        # Vérifier les nouvelles données économiques
        cost_analysis = analysis.get('cost_analysis', {})
        
        if cost_analysis:
            print("\n💳 ANALYSE FINANCIÈRE:")
            print(f"  📈 Coût annuel projeté: {cost_analysis.get('annual_projection', 0):.0f}€")
            print(f"  💰 Économies potentielles: {cost_analysis.get('potential_savings', {}).get('total_annuel', 0):.0f}€/an")
            
            # Répartition des économies
            savings = cost_analysis.get('potential_savings', {})
            print(f"  🎯 Réduction pics: {savings.get('reduction_pics', 0):.0f}€")
            print(f"  ⚡ Optimisation générale: {savings.get('optimisation_generale', 0):.0f}€")
            print(f"  📋 Changement tarification: {savings.get('changement_tarification', 0):.0f}€")
            print(f"  🔧 Solutions technologiques: {savings.get('solutions_technologiques', 0):.0f}€")
            
            # Opportunités d'investissement
            investments = cost_analysis.get('investment_opportunities', [])
            print(f"\n🏗️  OPPORTUNITÉS D'INVESTISSEMENT ({len(investments)} solutions):")
            for i, inv in enumerate(investments[:3], 1):
                print(f"  {i}. {inv.get('solution', 'N/A')}")
                print(f"     💰 Investissement: {inv.get('investissement', 0):,}€")
                print(f"     📈 Économies/an: {inv.get('economies_annuelles', 0):.0f}€")
                print(f"     ⏰ ROI: {inv.get('roi_annees', 0):.1f} ans")
            
            # Recommandations économiques
            eco_recs = cost_analysis.get('economic_recommendations', [])
            print(f"\n📋 RECOMMANDATIONS ÉCONOMIQUES ({len(eco_recs)} actions):")
            for i, rec in enumerate(eco_recs[:2], 1):
                print(f"  {i}. {rec.get('titre', 'N/A')}")
                print(f"     🎯 Catégorie: {rec.get('categorie', 'N/A')}")
                print(f"     💰 Impact: {rec.get('impact_financier', 0):.0f}€/an")
                print(f"     ⏱️  ROI: {rec.get('roi_estime', 'N/A')}")
            
            # Analyse de tarification
            tarification = cost_analysis.get('tarification_analysis', {})
            if tarification:
                print(f"\n🏷️  ANALYSE TARIFAIRE:")
                print(f"  📊 Profil détecté: {tarification.get('profile_detected', 'N/A')}")
                print(f"  📋 Tarif recommandé: {tarification.get('tarif_recommande', 'N/A')}")
        
        else:
            print("❌ Aucune analyse économique trouvée")
            return False
        
        # Test génération PDF avec nouvelles sections
        print("\n📄 Test génération PDF enrichi...")
        pdf_buffer = generate_professional_pdf(analysis, 'exemple_entreprise.csv', df)
        
        # Sauvegarder
        with open('rapport_economique_ameliore.pdf', 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        # Vérifier la taille
        import os
        size = os.path.getsize('rapport_economique_ameliore.pdf')
        print(f"✅ PDF généré: {size:,} bytes")
        
        if size > 8000:  # Doit être plus gros avec les nouvelles sections
            print("✅ PDF enrichi généré avec succès!")
            return True
        else:
            print("⚠️  PDF semble trop petit pour contenir toutes les sections")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_roi_calculations():
    """Test spécifique des calculs de ROI"""
    print("\n🧮 TEST DES CALCULS DE ROI")
    print("-" * 40)
    
    try:
        from app import (analyze_investment_opportunities, 
                        calculate_optimization_potential,
                        calculate_tariff_savings,
                        calculate_technology_savings)
        
        # Données de test
        annual_savings = 5000  # 5000€ d'économies potentielles
        basic_stats = {
            'avg_consumption': 1500,  # Profil professionnel
            'total_consumption': 180000,
            'std_consumption': 300
        }
        peaks = [{'impact_cost': 200} for _ in range(10)]  # 10 pics coûteux
        file_info = {'date_range': {'duration_days': 120}}
        
        # Test des calculs
        investments = analyze_investment_opportunities(annual_savings, basic_stats, peaks)
        optimization_rate = calculate_optimization_potential(basic_stats, peaks)
        tariff_savings = calculate_tariff_savings(basic_stats, file_info)
        tech_savings = calculate_technology_savings(basic_stats, peaks, file_info)
        
        print(f"✅ Investissements analysés: {len(investments)} solutions")
        print(f"✅ Taux d'optimisation: {optimization_rate*100:.1f}%")
        print(f"✅ Économies tarifaires: {tariff_savings:.0f}€")
        print(f"✅ Économies technologiques: {tech_savings:.0f}€")
        
        # Vérifier la logique des ROI
        for inv in investments[:2]:
            roi = inv['roi_annees']
            if 0.5 <= roi <= 10:  # ROI raisonnable
                print(f"✅ ROI cohérent pour {inv['solution']}: {roi:.1f} ans")
            else:
                print(f"⚠️  ROI suspect pour {inv['solution']}: {roi:.1f} ans")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur calculs ROI: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TEST COMPLET DES AMÉLIORATIONS ÉCONOMIQUES")
    print("=" * 80)
    
    # Test 1: Analyse économique complète
    success1 = test_economic_improvements()
    
    # Test 2: Calculs de ROI
    success2 = test_roi_calculations()
    
    print("\n" + "=" * 80)
    print("📊 RÉSULTATS FINAUX:")
    print(f"  💰 Analyse économique: {'✅ SUCCÈS' if success1 else '❌ ÉCHEC'}")
    print(f"  🧮 Calculs ROI: {'✅ SUCCÈS' if success2 else '❌ ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 TOUTES LES AMÉLIORATIONS ÉCONOMIQUES FONCTIONNENT!")
        print("📄 Rapport PDF enrichi disponible: rapport_economique_ameliore.pdf")
        print("💡 L'application propose maintenant des solutions concrètes d'économies")
    else:
        print("\n⚠️  Certaines fonctionnalités nécessitent des corrections")
    
    print("=" * 80)

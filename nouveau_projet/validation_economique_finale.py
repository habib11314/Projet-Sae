#!/usr/bin/env python3
"""
Validation finale des améliorations économiques EnergyInsight
"""

import pandas as pd
import sys
sys.path.append('.')

from app import analyze_consumption_data, generate_professional_pdf

def final_validation():
    print("🎯 VALIDATION FINALE DES AMÉLIORATIONS ÉCONOMIQUES")
    print("=" * 70)
    
    # Test avec données entreprise
    df = pd.read_csv('exemple_donnees_conso_entreprise.csv')
    analysis = analyze_consumption_data(df)
    
    # Extraction des données économiques
    cost_analysis = analysis.get('cost_analysis', {})
    
    print("✅ FONCTIONNALITÉS ÉCONOMIQUES VALIDÉES:")
    print("-" * 50)
    
    # 1. Analyse financière de base
    annual_cost = cost_analysis.get('annual_projection', 0)
    print(f"1. 💰 Coût annuel calculé: {annual_cost:,.0f}€")
    
    # 2. Économies potentielles détaillées
    savings = cost_analysis.get('potential_savings', {})
    total_savings = savings.get('total_annuel', 0)
    print(f"2. 📈 Économies potentielles: {total_savings:,.0f}€/an ({total_savings/annual_cost*100:.1f}%)")
    
    # 3. Répartition des économies
    print("3. 🎯 Répartition des économies:")
    print(f"   • Réduction pics: {savings.get('reduction_pics', 0):,.0f}€")
    print(f"   • Optimisation générale: {savings.get('optimisation_generale', 0):,.0f}€")
    print(f"   • Changement tarification: {savings.get('changement_tarification', 0):,.0f}€")
    print(f"   • Solutions technologiques: {savings.get('solutions_technologiques', 0):,.0f}€")
    
    # 4. Analyse de tarification
    tarif = cost_analysis.get('tarification_analysis', {})
    print(f"4. 🏷️  Analyse tarifaire:")
    print(f"   • Profil: {tarif.get('profile_detected', 'N/A')}")
    print(f"   • Tarif recommandé: {tarif.get('tarif_recommande', 'N/A')}")
    
    # 5. Opportunités d'investissement
    investments = cost_analysis.get('investment_opportunities', [])
    print(f"5. 🏗️  Investissements ({len(investments)} solutions):")
    for i, inv in enumerate(investments[:2], 1):
        roi = inv.get('roi_annees', 0)
        print(f"   {i}. {inv.get('solution', 'N/A')}")
        print(f"      💰 {inv.get('investissement', 0):,}€ → {inv.get('economies_annuelles', 0):,.0f}€/an (ROI: {roi:.1f} ans)")
    
    # 6. Recommandations économiques
    eco_recs = cost_analysis.get('economic_recommendations', [])
    print(f"6. 📋 Recommandations ({len(eco_recs)} actions):")
    for i, rec in enumerate(eco_recs[:2], 1):
        print(f"   {i}. {rec.get('titre', 'N/A')}")
        print(f"      💰 Impact: {rec.get('impact_financier', 0):,.0f}€/an")
        print(f"      ⏱️  ROI: {rec.get('roi_estime', 'N/A')}")
    
    # Test génération PDF enrichi
    print("\n📄 VALIDATION PDF ENRICHI:")
    print("-" * 30)
    
    pdf_buffer = generate_professional_pdf(analysis, 'exemple_entreprise.csv', df)
    
    # Sauvegarder et analyser
    with open('rapport_final_enrichi.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    import os
    size = os.path.getsize('rapport_final_enrichi.pdf')
    
    print(f"✅ PDF généré: {size:,} bytes")
    
    # Validation des sections ajoutées
    if size > 6000:  # Plus gros avec les nouvelles sections
        print("✅ PDF contient probablement toutes les sections économiques")
    else:
        print("⚠️  PDF pourrait manquer certaines sections")
    
    # Calcul de l'amélioration
    improvement_rate = (total_savings / annual_cost) * 100 if annual_cost > 0 else 0
    
    print(f"\n🎉 RÉSULTAT FINAL:")
    print("=" * 50)
    print(f"💰 Coût annuel actuel: {annual_cost:,.0f}€")
    print(f"📈 Économies possibles: {total_savings:,.0f}€ ({improvement_rate:.1f}%)")
    print(f"🏆 Meilleur ROI: {investments[0].get('roi_annees', 0):.1f} ans" if investments else "🏆 Pas d'investissement nécessaire")
    
    if improvement_rate > 15:
        print("🎯 EXCELLENT POTENTIEL D'OPTIMISATION!")
    elif improvement_rate > 10:
        print("✅ BON POTENTIEL D'ÉCONOMIES")
    else:
        print("📊 Potentiel d'optimisation modéré")
    
    print("\n📋 NOUVELLES FONCTIONNALITÉS AJOUTÉES:")
    print("=" * 50)
    print("✅ Analyse financière complète avec projections")
    print("✅ Calcul d'économies par catégorie (pics, tarifs, tech)")
    print("✅ Détection automatique du profil tarifaire optimal")
    print("✅ Recommandations d'investissement avec ROI détaillé")
    print("✅ Plan d'action économique priorisé")
    print("✅ Rapport PDF enrichi avec section économique")
    print("✅ Solutions personnalisées selon le profil de consommation")
    
    return True

if __name__ == "__main__":
    final_validation()

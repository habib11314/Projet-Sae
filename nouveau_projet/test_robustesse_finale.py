#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de robustesse finale pour EnergyInsight
Vérifie que l'analyse économique fonctionne correctement pour tous les fichiers
"""

import sys
import os
import traceback
from app import analyze_consumption_data, generate_professional_pdf

def test_file_analysis(filename, description):
    """Test l'analyse d'un fichier spécifique"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {description}")
    print(f"📁 Fichier: {filename}")
    print(f"{'='*80}")
    
    try:
        if not os.path.exists(filename):
            print(f"❌ Fichier non trouvé: {filename}")
            return False
            
        # Test de l'analyse complète
        print("🔍 Lancement de l'analyse...")
        analysis = analyze_consumption_data(filename)
        
        if not analysis:
            print("❌ Échec de l'analyse")
            return False
            
        print("✅ Analyse réussie!")
        
        # Vérification des composants clés
        required_keys = ['basic_stats', 'peaks', 'cost_analysis', 'graph_json']
        missing_keys = [key for key in required_keys if key not in analysis]
        
        if missing_keys:
            print(f"⚠️  Clés manquantes: {missing_keys}")
            return False
            
        print("✅ Toutes les clés requises présentes")
        
        # Test de l'analyse économique
        cost_analysis = analysis['cost_analysis']
        print(f"💰 Coût total: {cost_analysis.get('total_cost', 0):.2f}€")
        print(f"📊 Pics détectés: {len(analysis['peaks'])}")
        
        # Test de génération PDF
        print("📄 Test de génération PDF...")
        try:
            pdf_buffer = generate_professional_pdf(analysis, filename)
            if pdf_buffer:
                print("✅ PDF généré avec succès")
            else:
                print("❌ Échec génération PDF")
                return False
        except Exception as pdf_error:
            print(f"❌ Erreur PDF: {str(pdf_error)}")
            return False
            
        # Vérification des recommandations économiques
        if 'economic_recommendations' in cost_analysis:
            print(f"💡 Recommandations économiques: {len(cost_analysis['economic_recommendations'])}")
        
        # Vérification des économies potentielles
        if 'potential_savings' in cost_analysis:
            savings = cost_analysis['potential_savings']
            total_savings = savings.get('total_annuel', 0)
            print(f"💰 Économies potentielles: {total_savings:.2f}€/an")
            
        print("✅ Test réussi pour ce fichier!")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors du test: {str(e)}")
        print("📋 Stack trace:")
        traceback.print_exc()
        return False

def main():
    """Test principal"""
    print("🧪 TEST DE ROBUSTESSE FINALE - EnergyInsight")
    print("=" * 80)
    
    # Liste des fichiers à tester
    test_files = [
        ("sample_data.csv", "Fichier standard simple"),
        ("exemple_donnees_conso_entreprise.csv", "Fichier entreprise avancé")
    ]
    
    results = []
    
    for filename, description in test_files:
        success = test_file_analysis(filename, description)
        results.append((filename, success))
    
    # Résumé final
    print(f"\n{'='*80}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*80}")
    
    total_tests = len(results)
    successful_tests = sum(1 for _, success in results if success)
    
    for filename, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"  {filename}: {status}")
    
    print(f"\n🎯 RÉSULTAT GLOBAL: {successful_tests}/{total_tests} tests réussis")
    
    if successful_tests == total_tests:
        print("🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print("✅ L'application est robuste et prête à l'emploi")
    else:
        print("⚠️  Certains tests ont échoué - vérification requise")
        
    return successful_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

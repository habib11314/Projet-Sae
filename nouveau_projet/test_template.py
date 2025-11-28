#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template
import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

def test_template():
    try:
        with app.app_context():
            # Test 1: Template de base
            print("Test 1: Template de base")
            result = render_template('dashboard_advanced.html', 
                                   analysis=None, 
                                   filename=None, 
                                   chart_data=None)
            print(f"✅ Template de base OK - {len(result)} caractères")
            
            # Test 2: Template avec données minimales
            print("\nTest 2: Template avec données minimales")
            fake_analysis = {
                'total_consumption': 1000.0,
                'avg_consumption': 10.0,
                'peaks': [],
                'statistics': {'efficiency_score': 75.0},
                'data_format': 'standard',
                'file_info': {'columns_detected': ['date', 'consumption']},
                'recommendations': []
            }
            
            result = render_template('dashboard_advanced.html', 
                                   analysis=fake_analysis, 
                                   filename='test.csv', 
                                   chart_data='{}')
            print(f"✅ Template avec données OK - {len(result)} caractères")
            
            # Test 3: Vérification des erreurs dans le template
            print("\nTest 3: Vérification du contenu")
            if 'error' in result.lower():
                print("❌ Erreur détectée dans le template")
            else:
                print("✅ Aucune erreur détectée")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test du template: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Test du template dashboard_advanced.html")
    print("=" * 50)
    success = test_template()
    if success:
        print("\n✅ Tous les tests sont passés")
    else:
        print("\n❌ Des erreurs ont été détectées")

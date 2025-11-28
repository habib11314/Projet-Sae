#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test upload du fichier exemple_factures_normalisees.csv
"""

import requests
import os
import time

def test_upload_exemple_factures():
    """Test avec le fichier exemple_factures_normalisees.csv"""
    print("🧪 TEST UPLOAD EXEMPLE_FACTURES_NORMALISEES.CSV")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    
    # Vérifier que l'app répond
    try:
        print("🔍 1. Vérification de l'application...")
        response = requests.get(base_url, timeout=5)
        print(f"✅ Application accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Application non accessible: {e}")
        return False
    
    # Tester l'upload avec exemple_factures_normalisees.csv
    try:
        print("\n📤 2. Test upload exemple_factures_normalisees.csv...")
        
        if not os.path.exists('exemple_factures_normalisees.csv'):
            print("❌ Fichier exemple_factures_normalisees.csv non trouvé")
            return False
        
        upload_url = f"{base_url}/upload"
        
        with open('exemple_factures_normalisees.csv', 'rb') as f:
            files = {'file': ('exemple_factures_normalisees.csv', f, 'text/csv')}
            
            print("📡 Envoi du fichier exemple...")
            response = requests.post(upload_url, files=files, timeout=60, allow_redirects=False)
            
            print(f"📊 Code de réponse: {response.status_code}")
            
            if response.status_code in [302, 303]:
                redirect_url = response.headers.get('Location')
                print(f"🔄 Redirection vers: {redirect_url}")
                
                # Suivre la redirection
                if redirect_url.startswith('/'):
                    full_redirect_url = base_url + redirect_url
                else:
                    full_redirect_url = redirect_url
                
                print(f"🌐 URL complète: {full_redirect_url}")
                
                dashboard_response = requests.get(full_redirect_url, timeout=60)
                print(f"📊 Code dashboard: {dashboard_response.status_code}")
                
                if dashboard_response.status_code == 200:
                    content = dashboard_response.text
                    
                    # Vérifier s'il y a des erreurs
                    if "Erreur lors de l'analyse" in content:
                        print("❌ ERREUR DÉTECTÉE dans le dashboard!")
                        
                        # Extraire le message d'erreur
                        import re
                        error_match = re.search(r"Erreur lors de l'analyse: ([^<]+)", content)
                        if error_match:
                            error_msg = error_match.group(1).strip()
                            print(f"📋 Message d'erreur: {error_msg}")
                        
                        return False
                    
                    elif "Dashboard" in content or "Analyse" in content:
                        print("✅ Dashboard chargé avec succès!")
                        
                        # Vérifier la présence de données
                        if "kWh" in content:
                            print("✅ Données de consommation présentes")
                        if "€" in content:
                            print("✅ Données financières présentes")
                        if "Recommandations" in content:
                            print("✅ Recommandations présentes")
                        if "Graphique" in content or "chart" in content:
                            print("✅ Graphique présent")
                        
                        return True
                    
                    else:
                        print("⚠️  Contenu du dashboard inhabituel")
                        print(f"📄 Début du contenu: {content[:500]}...")
                        return False
                
                else:
                    print(f"❌ Erreur dashboard: {dashboard_response.status_code}")
                    print(f"📄 Contenu erreur: {dashboard_response.text[:500]}...")
                    return False
            
            else:
                print(f"❌ Erreur upload: {response.status_code}")
                print(f"📄 Contenu: {response.text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ Exception durant le test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_upload_exemple_factures()
    
    if success:
        print("\n🎉 SUCCÈS ! L'upload exemple factures fonctionne !")
    else:
        print("\n❌ ÉCHEC ! Problème avec l'upload exemple factures...")

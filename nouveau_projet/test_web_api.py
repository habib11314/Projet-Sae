#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test automatisé via l'API web pour vérifier le bon fonctionnement
"""

import requests
import os
import time

def test_web_upload():
    """Test automatisé via l'API web"""
    print("🌐 TEST AUTOMATISÉ VIA L'API WEB")
    print("=" * 50)
    
    # URL de l'application
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Vérifier que l'application répond
        print("🔍 1. Vérification que l'application répond...")
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Application accessible")
        else:
            print(f"❌ Application non accessible: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible de contacter l'application: {e}")
        print("💡 Assurez-vous que l'application est lancée sur http://127.0.0.1:5000")
        return False
    
    try:
        # Upload du fichier facturation
        print("\n📤 2. Upload du fichier facturation...")
        
        if not os.path.exists('facturation.csv'):
            print("❌ Fichier facturation.csv non trouvé")
            return False
        
        upload_url = f"{base_url}/upload"
        
        with open('facturation.csv', 'rb') as f:
            files = {'file': ('facturation.csv', f, 'text/csv')}
            
            # Faire l'upload
            response = requests.post(upload_url, files=files, timeout=30, allow_redirects=False)
            
            print(f"📊 Statut upload: {response.status_code}")
            
            if response.status_code in [302, 303]:  # Redirection après upload réussi
                print("✅ Upload réussi - redirection détectée")
                
                # Extraire l'URL de redirection
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    print(f"🔄 URL de redirection: {redirect_url}")
                    
                    # Suivre la redirection pour vérifier que le dashboard fonctionne
                    if redirect_url.startswith('/'):
                        redirect_url = base_url + redirect_url
                    
                    print("\n📊 3. Test du dashboard...")
                    dashboard_response = requests.get(redirect_url, timeout=30)
                    
                    if dashboard_response.status_code == 200:
                        print("✅ Dashboard accessible et fonctionnel")
                        
                        # Vérifier que le contenu semble correct
                        content = dashboard_response.text
                        if "Analyse de la Consommation" in content or "Dashboard" in content:
                            print("✅ Contenu du dashboard semble correct")
                        else:
                            print("⚠️  Contenu du dashboard inhabituel")
                        
                        return True
                    else:
                        print(f"❌ Erreur dashboard: {dashboard_response.status_code}")
                        return False
                        
            elif response.status_code == 200:
                print("⚠️  Upload sans redirection - vérification du contenu...")
                if "Fichier uploadé avec succès" in response.text:
                    print("✅ Message de succès détecté")
                    return True
                else:
                    print("❌ Pas de message de succès")
                    return False
            else:
                print(f"❌ Erreur upload: {response.status_code}")
                print(f"📄 Réponse: {response.text[:500]}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Ce test va vérifier si l'upload facturation fonctionne vraiment via l'interface web")
    print("⚠️  Assurez-vous que l'application est lancée !")
    
    # Attendre un peu pour laisser le temps à l'application de démarrer
    time.sleep(2)
    
    success = test_web_upload()
    
    if success:
        print("\n🎉 SUCCÈS ! L'upload facturation fonctionne via l'interface web !")
    else:
        print("\n❌ ÉCHEC ! Il y a encore un problème avec l'upload facturation...")

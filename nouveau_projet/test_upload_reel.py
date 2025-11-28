#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test automatisé complet qui simule EXACTEMENT l'upload web
"""

import requests
import os
import time
import json

def test_upload_facturation_complet():
    """Test automatisé qui reproduit exactement l'upload web"""
    print("🔬 TEST COMPLET UPLOAD FACTURATION VIA WEB")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    
    # 1. Vérifier que l'app répond
    try:
        print("🔍 1. Vérification de l'application...")
        response = requests.get(base_url, timeout=5)
        print(f"✅ Application accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Application non accessible: {e}")
        return False
    
    # 2. Tester l'upload
    try:
        print("\n📤 2. Test upload facturation.csv...")
        
        if not os.path.exists('facturation.csv'):
            print("❌ Fichier facturation.csv non trouvé")
            return False
        
        upload_url = f"{base_url}/upload"
        
        with open('facturation.csv', 'rb') as f:
            files = {'file': ('facturation.csv', f, 'text/csv')}
            
            print("📡 Envoi du fichier...")
            response = requests.post(upload_url, files=files, timeout=60, allow_redirects=False)
            
            print(f"📊 Code de réponse: {response.status_code}")
            print(f"📄 Headers: {dict(response.headers)}")
            
            if response.status_code in [302, 303]:
                redirect_url = response.headers.get('Location')
                print(f"🔄 Redirection vers: {redirect_url}")
                
                # 3. Suivre la redirection (là où l'erreur peut se produire)
                print("\n📊 3. Test du dashboard (où l'erreur peut apparaître)...")
                
                if redirect_url.startswith('/'):
                    full_redirect_url = base_url + redirect_url
                else:
                    full_redirect_url = redirect_url
                
                print(f"🌐 URL complète: {full_redirect_url}")
                
                # C'est ici que l'erreur peut se produire
                dashboard_response = requests.get(full_redirect_url, timeout=60)
                
                print(f"📊 Code dashboard: {dashboard_response.status_code}")
                
                if dashboard_response.status_code == 200:
                    content = dashboard_response.text
                    
                    # Vérifier s'il y a des erreurs dans le contenu
                    if "Erreur lors de l'analyse" in content:
                        print("❌ ERREUR DÉTECTÉE dans le dashboard!")
                        
                        # Extraire le message d'erreur
                        import re
                        error_match = re.search(r"Erreur lors de l'analyse: ([^<]+)", content)
                        if error_match:
                            error_msg = error_match.group(1).strip()
                            print(f"📋 Message d'erreur: {error_msg}")
                            
                            if "total_consumption" in error_msg:
                                print("🎯 C'est bien l'erreur 'total_consumption' !")
                                return False
                        
                        return False
                    
                    elif "Dashboard" in content or "Analyse" in content:
                        print("✅ Dashboard chargé avec succès!")
                        
                        # Vérifier la présence de données
                        if "kWh" in content and "€" in content:
                            print("✅ Données d'analyse présentes")
                        
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
            
            elif response.status_code == 200:
                content = response.text
                if "Erreur lors de l'analyse" in content:
                    print("❌ ERREUR DÉTECTÉE lors de l'upload!")
                    
                    # Extraire le message d'erreur
                    import re
                    error_match = re.search(r"Erreur lors de l'analyse: ([^<]+)", content)
                    if error_match:
                        error_msg = error_match.group(1).strip()
                        print(f"📋 Message d'erreur: {error_msg}")
                        
                        if "total_consumption" in error_msg:
                            print("🎯 C'est bien l'erreur 'total_consumption' !")
                    
                    return False
                else:
                    print("⚠️  Upload sans redirection")
                    return True
            
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
    print("🎯 CE TEST VA REPRODUIRE EXACTEMENT VOTRE UPLOAD")
    print("💡 S'il y a encore l'erreur, on la verra ici !")
    
    # Test diagnostic rapide avant le test web
    print("\n🔍 DIAGNOSTIC RAPIDE DU FICHIER...")
    try:
        import pandas as pd
        from app import detect_data_format, standardize_columns
        from analyzers_specialized import analyze_factures_normalisees
        
        df = pd.read_csv('facturation.csv')
        print(f"📋 Colonnes: {list(df.columns)}")
        
        format_detected = detect_data_format(df)
        print(f"🎯 Format: {format_detected}")
        
        df_std = standardize_columns(df, format_detected)
        
        # DIAGNOSTIC DÉTAILLÉ POUR IDENTIFIER LE PROBLÈME
        print(f"🔍 Type de df_std: {type(df_std)}")
        print(f"📋 Colonnes standardisées: {list(df_std.columns) if hasattr(df_std, 'columns') else 'PAS UN DATAFRAME!'}")
        
        if not hasattr(df_std, 'columns'):
            print(f"❌ ERREUR CRITIQUE: df_std n'est pas un DataFrame!")
            print(f"📄 Contenu de df_std: {df_std}")
            print(f"📄 Type exact: {type(df_std).__name__}")
            raise Exception("df_std n'est pas un DataFrame après standardize_columns")
        
        if 'consumption' in df_std.columns:
            print(f"✅ Consumption trouvée: {df_std['consumption'].dtype}")
            print(f"📊 Premières valeurs consumption: {df_std['consumption'].head().tolist()}")
        else:
            print(f"❌ Consumption manquante!")
            print(f"📋 Colonnes disponibles: {list(df_std.columns)}")
            
        # Vérifier que df_std est bien un DataFrame avant l'analyseur
        if not isinstance(df_std, pd.DataFrame):
            print(f"❌ ERREUR: df_std n'est pas un DataFrame avant l'analyseur!")
            print(f"📄 Type: {type(df_std)}, Contenu: {df_std}")
            raise Exception("df_std n'est pas un DataFrame avant l'analyseur")
            
        print(f"🧪 Test de l'analyseur avec DataFrame valide...")
        # Test analyseur direct
        results = analyze_factures_normalisees(df_std)
        print(f"✅ Analyseur OK")
        
    except Exception as e:
        print(f"❌ Diagnostic échoué: {e}")
        import traceback
        traceback.print_exc()
    
    time.sleep(2)  # Laisser le temps à l'app de démarrer
    
    success = test_upload_facturation_complet()
    
    if success:
        print("\n🎉 SUCCÈS ! L'upload facturation fonctionne parfaitement !")
    else:
        print("\n❌ ÉCHEC ! L'erreur persiste effectivement...")

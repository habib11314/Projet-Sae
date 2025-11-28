#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug approfondi pour identifier l'erreur 'str' object has no attribute 'consumption'
"""

import pandas as pd
import traceback
import sys

def debug_erreur_str():
    """Diagnostic ultra-détaillé pour traquer l'erreur str/consumption"""
    print("🔍 DIAGNOSTIC ULTRA-DÉTAILLÉ - ERREUR STR/CONSUMPTION")
    print("=" * 70)
    
    try:
        # Importer les modules
        from app import detect_data_format, standardize_columns, analyze_consumption_data
        from analyzers_specialized import analyze_factures_normalisees
        
        # Test avec le fichier qui pose problème
        print("\n📁 Test avec facturation.csv...")
        df_orig = pd.read_csv('facturation.csv')
        print(f"✅ Fichier chargé: {df_orig.shape}")
        print(f"📋 Colonnes: {list(df_orig.columns)}")
        print(f"🔍 Type df_orig: {type(df_orig)}")
        
        # Étape 1: Détection du format
        print(f"\n🎯 ÉTAPE 1: Détection du format...")
        format_detected = detect_data_format(df_orig)
        print(f"✅ Format détecté: {format_detected}")
        print(f"🔍 Type format_detected: {type(format_detected)}")
        
        # Étape 2: Standardisation des colonnes
        print(f"\n🔄 ÉTAPE 2: Standardisation des colonnes...")
        df_std = standardize_columns(df_orig, format_detected)
        print(f"✅ Standardisation terminée")
        print(f"🔍 Type df_std: {type(df_std)}")
        print(f"📋 Colonnes standardisées: {list(df_std.columns) if hasattr(df_std, 'columns') else 'PAS DE COLONNES!'}")
        
        if not isinstance(df_std, pd.DataFrame):
            print(f"❌ ERREUR CRITIQUE: df_std n'est pas un DataFrame!")
            print(f"📄 Contenu de df_std: {repr(df_std)}")
            print(f"📄 Type exact: {type(df_std)}")
            return False
        
        # Vérifier la colonne consumption
        if 'consumption' in df_std.columns:
            print(f"✅ Colonne 'consumption' trouvée")
            print(f"📊 Type consumption: {df_std['consumption'].dtype}")
            print(f"📊 Valeurs consumption: {df_std['consumption'].tolist()}")
        else:
            print(f"❌ Colonne 'consumption' manquante!")
            return False
        
        # Étape 3: Test de l'analyseur spécialisé directement
        print(f"\n🧪 ÉTAPE 3: Test analyseur spécialisé direct...")
        try:
            results = analyze_factures_normalisees(df_std)
            print(f"✅ Analyseur spécialisé OK")
        except Exception as e:
            print(f"❌ Erreur analyseur spécialisé: {e}")
            traceback.print_exc()
            return False
        
        # Étape 4: Test de la fonction principale analyze_consumption_data
        print(f"\n🏭 ÉTAPE 4: Test fonction principale analyze_consumption_data...")
        try:
            # La fonction analyze_consumption_data prend seulement le DataFrame en entrée
            results_main = analyze_consumption_data(df_orig)  # Utiliser df_orig, pas df_std
            print(f"✅ Fonction principale OK")
        except Exception as e:
            print(f"❌ ERREUR DANS LA FONCTION PRINCIPALE: {e}")
            print(f"🔍 Type de df_std au moment de l'erreur: {type(df_std)}")
            print(f"🔍 Hasattr df_std consumption: {hasattr(df_std, 'consumption') if hasattr(df_std, '__getattribute__') else 'N/A'}")
            
            # Diagnostic détaillé du DataFrame au moment de l'erreur
            if isinstance(df_std, pd.DataFrame):
                print(f"📋 Colonnes disponibles: {list(df_std.columns)}")
                print(f"📊 Shape: {df_std.shape}")
                print(f"📄 Head:\n{df_std.head()}")
            else:
                print(f"❌ df_std n'est plus un DataFrame: {type(df_std)}")
                print(f"📄 Contenu: {repr(df_std)}")
            
            traceback.print_exc()
            return False
        
        # Étape 5: Test avec différents fichiers d'exemple
        print(f"\n📁 ÉTAPE 5: Test avec exemple_factures_normalisees.csv...")
        try:
            df_exemple = pd.read_csv('exemple_factures_normalisees.csv')
            print(f"✅ Exemple chargé: {df_exemple.shape}")
            
            format_exemple = detect_data_format(df_exemple)
            print(f"✅ Format exemple: {format_exemple}")
            
            df_exemple_std = standardize_columns(df_exemple, format_exemple)
            print(f"✅ Standardisation exemple OK")
            print(f"🔍 Type df_exemple_std: {type(df_exemple_std)}")
            
            results_exemple = analyze_consumption_data(df_exemple)  # Seulement le DataFrame
            print(f"✅ Analyse exemple OK")
            
        except Exception as e:
            print(f"❌ Erreur avec exemple: {e}")
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_erreur_str()

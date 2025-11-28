#!/usr/bin/env python3
"""
StatEnergie - Application professionnelle d'analyse énergétique
Solution complète pour entreprises du secteur énergétique
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json
import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import tempfile
import io
import traceback
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from pdf_bill_analyzer import PDFBillAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'statenergie-secret-key-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extensions autorisées
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json', 'pdf'}

def allowed_file(filename):
    """Vérifier si le fichier est autorisé"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_data_format(df):
    """Détecter automatiquement le format des données énergétiques professionnelles"""
    columns = df.columns.str.lower()
    
    # 1. FORMAT GRD-F (Courbes de charge - Enedis/EDF/ENGIE)
    has_pdl_prm = any('pdl' in col or 'prm' in col for col in columns)
    has_index = any('index' in col for col in columns)
    has_datetime = any('date' in col and 'heure' in col for col in columns) or any('datetime' in col for col in columns)
    has_hp_hc = any('hp' in col for col in columns) and any('hc' in col for col in columns)
    has_conso_interval = any('conso' in col for col in columns) and (has_datetime or has_index)
    
    if (has_pdl_prm and has_index) or (has_conso_interval and has_hp_hc):
        return 'grdf_courbe_charge'
    
    # 2. FORMAT FACTURES NORMALISÉES (Comptabilité entreprise)
    has_client = any('client' in col or 'numéro' in col for col in columns)
    has_periode = any('période' in col or 'facturé' in col for col in columns)
    has_montant = any('montant' in col or 'prix' in col or 'tarif' in col for col in columns)
    has_taxes = any('taxe' in col or 'tva' in col or 'cspe' in col or 'cta' in col for col in columns)
    has_fournisseur = any('fournisseur' in col or 'engie' in col or 'edf' in col for col in columns)
    
    if (has_client and has_montant) or (has_periode and has_fournisseur) or has_taxes:
        return 'factures_normalisees'
    
    # 3. FORMAT ADEME / ISO 50001 (Management énergétique)
    has_iso_indicators = any('indicateur' in col or 'performance' in col for col in columns)
    has_energy_type = any('type' in col and 'energie' in col for col in columns)
    has_kpi = any('kpi' in col or 'objectif' in col or 'cible' in col for col in columns)
    has_ademe = any('ademe' in col or 'iso' in col or '50001' in col for col in columns)
    has_management = any('management' in col or 'pilotage' in col for col in columns)
    
    if has_iso_indicators or has_kpi or has_ademe or has_management:
        return 'ademe_iso50001'
    
    # Fallback: détecter un format générique si aucun format spécialisé n'est reconnu
    has_basic_conso = any('consommation' in col or 'consumption' in col for col in columns)
    has_basic_date = any('date' in col for col in columns)
    
    if has_basic_conso and has_basic_date:
        return 'format_generique'
    
    return 'format_non_reconnu'

def standardize_columns(df, data_format):
    """Standardiser les noms de colonnes selon le format détecté"""
    df_std = df.copy()
    
    print(f"🔍 Colonnes originales: {list(df_std.columns)}")
    print(f"🎯 Format détecté: {data_format}")
    
    if data_format == 'grdf_courbe_charge':
        # Format GRD-F / Courbes de charge
        column_mapping = {}
        
        for col in df_std.columns:
            col_lower = col.lower()
            
            # Date/heure
            if 'date' in col_lower and ('heure' in col_lower or 'time' in col_lower):
                column_mapping[col] = 'datetime'
                print(f"📅 Colonne datetime détectée: '{col}' -> 'datetime'")
            elif 'date' in col_lower:
                column_mapping[col] = 'date'
                print(f"📅 Colonne date détectée: '{col}' -> 'date'")
            
            # Index cumulé
            elif 'index' in col_lower:
                column_mapping[col] = 'index_cumul'
                print(f"📊 Index cumulé: '{col}' -> 'index_cumul'")
            
            # Consommation par intervalle
            elif 'conso' in col_lower and ('kwh' in col_lower or 'mwh' in col_lower):
                column_mapping[col] = 'consumption'
                print(f"⚡ Consommation: '{col}' -> 'consumption'")
            
            # HP/HC
            elif 'hp' in col_lower and 'conso' in col_lower:
                column_mapping[col] = 'hp_consumption'
                print(f"🌞 HP: '{col}' -> 'hp_consumption'")
            elif 'hc' in col_lower and 'conso' in col_lower:
                column_mapping[col] = 'hc_consumption'
                print(f"🌙 HC: '{col}' -> 'hc_consumption'")
            
            # Point de livraison
            elif 'pdl' in col_lower or 'prm' in col_lower:
                column_mapping[col] = 'point_livraison'
                print(f"🏢 Point livraison: '{col}' -> 'point_livraison'")
        
        df_std = df_std.rename(columns=column_mapping)
        
        # Calculer la consommation si on a HP+HC
        if 'hp_consumption' in df_std.columns and 'hc_consumption' in df_std.columns and 'consumption' not in df_std.columns:
            df_std['consumption'] = df_std['hp_consumption'] + df_std['hc_consumption']
            print("� Consommation totale calculée: HP + HC")
    
    elif data_format == 'factures_normalisees':
        # Format factures normalisées
        column_mapping = {}
        consumption_mapped = False  # Flag pour éviter les doublons sur 'consumption'
        
        for col in df_std.columns:
            col_lower = col.lower()
            
            # Numéro client/Site
            if ('client' in col_lower or 'numéro' in col_lower or 'site' in col_lower) and 'numero_client' not in column_mapping.values():
                column_mapping[col] = 'numero_client'
                print(f"👤 Numéro client/Site: '{col}' -> 'numero_client'")
            
            # Période/Mois
            elif ('période' in col_lower or 'mois' in col_lower or 'date' in col_lower) and 'periode' not in column_mapping.values():
                column_mapping[col] = 'periode'
                print(f"📅 Période: '{col}' -> 'periode'")
            
            # Consommations (ordre de priorité pour éviter les conflits)
            elif not consumption_mapped and ('consommation' in col_lower and ('totale' in col_lower or 'total' in col_lower)):
                column_mapping[col] = 'consumption'
                consumption_mapped = True
                print(f"⚡ Consommation totale: '{col}' -> 'consumption'")
            elif not consumption_mapped and ('conso' in col_lower and 'hp' in col_lower):
                column_mapping[col] = 'hp_consumption'
                print(f"� Conso HP: '{col}' -> 'hp_consumption'")
            elif not consumption_mapped and ('conso' in col_lower and 'hc' in col_lower):
                column_mapping[col] = 'hc_consumption'
                print(f"🌙 Conso HC: '{col}' -> 'hc_consumption'")
            elif not consumption_mapped and ('conso' in col_lower or 'consommation' in col_lower) and 'kwh' in col_lower:
                column_mapping[col] = 'consumption'
                consumption_mapped = True
                print(f"⚡ Consommation: '{col}' -> 'consumption'")
            
            # Montants (ordre de priorité)
            elif ('montant' in col_lower and ('ht' in col_lower or 'hors' in col_lower)) and 'montant_ht' not in column_mapping.values():
                column_mapping[col] = 'montant_ht'
                print(f"💰 Montant HT: '{col}' -> 'montant_ht'")
            elif ('montant' in col_lower and ('ttc' in col_lower or 'toutes' in col_lower)) and 'montant_ttc' not in column_mapping.values():
                column_mapping[col] = 'montant_ttc'
                print(f"💰 Montant TTC: '{col}' -> 'montant_ttc'")
            elif ('montant' in col_lower and 'factur' in col_lower) and 'montant_ttc' not in column_mapping.values():
                column_mapping[col] = 'montant_ttc'  # Assumer TTC pour "montant facturé"
                print(f"💰 Montant facturé: '{col}' -> 'montant_ttc'")
            elif ('montant' in col_lower or ('€' in col and 'montant' in col_lower)) and 'montant' not in column_mapping.values():
                column_mapping[col] = 'montant'
                print(f"💰 Montant: '{col}' -> 'montant'")
            
            # Fournisseur
            elif 'fournisseur' in col_lower and 'fournisseur' not in column_mapping.values():
                column_mapping[col] = 'fournisseur'
                print(f"🏢 Fournisseur: '{col}' -> 'fournisseur'")
            
            # Taxes
            elif any(tax in col_lower for tax in ['tva', 'cspe', 'cta', 'taxe']) and 'taxes' not in column_mapping.values():
                column_mapping[col] = 'taxes'
                print(f"🏛️ Taxes: '{col}' -> 'taxes'")
        
        # Appliquer le mapping
        df_std = df_std.rename(columns=column_mapping)
        
        # Calculer la consommation totale si HP+HC mais pas de consommation totale
        if 'hp_consumption' in df_std.columns and 'hc_consumption' in df_std.columns and 'consumption' not in df_std.columns:
            df_std['consumption'] = df_std['hp_consumption'] + df_std['hc_consumption']
            print("⚡ Consommation totale calculée: HP + HC")
    
    elif data_format == 'ademe_iso50001':
        # Format ADEME / ISO 50001
        column_mapping = {}
        
        for col in df_std.columns:
            col_lower = col.lower()
            
            # Indicateurs de performance
            if 'indicateur' in col_lower or 'kpi' in col_lower:
                column_mapping[col] = 'kpi_energetique'
                print(f"📊 KPI énergétique: '{col}' -> 'kpi_energetique'")
            
            # Objectifs/Cibles
            elif 'objectif' in col_lower or 'cible' in col_lower:
                column_mapping[col] = 'objectif'
                print(f"🎯 Objectif: '{col}' -> 'objectif'")
            
            # Type d'énergie
            elif 'type' in col_lower and 'energie' in col_lower:
                column_mapping[col] = 'type_energie'
                print(f"⚡ Type énergie: '{col}' -> 'type_energie'")
            
            # Performance
            elif 'performance' in col_lower:
                column_mapping[col] = 'performance'
                print(f"📈 Performance: '{col}' -> 'performance'")
            
            # Consommation
            elif 'consommation' in col_lower or 'consumption' in col_lower:
                column_mapping[col] = 'consumption'
                print(f"⚡ Consommation: '{col}' -> 'consumption'")
        
        df_std = df_std.rename(columns=column_mapping)
    
    elif data_format == 'format_generique':
        # Format générique de base
        for col in df_std.columns:
            col_lower = col.lower()
            if 'consommation' in col_lower or 'consumption' in col_lower:
                df_std['consumption'] = df_std[col]
            elif 'date' in col_lower:
                df_std['date'] = df_std[col]
    
    print(f"🔄 Colonnes après standardisation: {list(df_std.columns)}")
    return df_std

def analyze_consumption_data(df):
    """Analyse ultra-avancée des données de consommation selon le format professionnel détecté"""
    
    # Détecter le format et standardiser les colonnes
    data_format = detect_data_format(df)
    df_standardized = standardize_columns(df, data_format)
    
    # Vérification critique : s'assurer que df_standardized est bien un DataFrame
    if not isinstance(df_standardized, pd.DataFrame):
        print(f"❌ ERREUR CRITIQUE: standardize_columns a retourné {type(df_standardized)} au lieu d'un DataFrame")
        print(f"📄 Contenu retourné: {repr(df_standardized)}")
        raise TypeError(f"standardize_columns a retourné {type(df_standardized)} au lieu d'un DataFrame")
    
    df = df_standardized
    print(f"🔍 Colonnes après standardisation: {list(df.columns)}")
    
    # Utiliser l'analyseur spécialisé selon le format
    if data_format == 'grdf_courbe_charge':
        try:
            from analyzers_specialized import analyze_grdf_courbe_charge
            results = analyze_grdf_courbe_charge(df)
            results['columns'] = list(df.columns)
            return results
        except Exception as e:
            print(f"❌ Erreur analyse GRD-F: {e}")
            import traceback; traceback.print_exc()
    
    elif data_format == 'factures_normalisees':
        try:
            from analyzers_specialized import analyze_factures_normalisees
            results = analyze_factures_normalisees(df)
            results['columns'] = list(df.columns)
            return results
        except Exception as e:
            print(f"❌ Erreur analyse factures: {e}")
            import traceback; traceback.print_exc()
    
    elif data_format == 'ademe_iso50001':
        try:
            from analyzers_specialized import analyze_ademe_iso50001
            results = analyze_ademe_iso50001(df)
            results['columns'] = list(df.columns)
            return results
        except Exception as e:
            print(f"❌ Erreur analyse ADEME: {e}")
            import traceback; traceback.print_exc()
    
    elif data_format == 'format_non_reconnu':
        return {
            'error': f'Format de fichier non reconnu. Formats supportés: GRD-F (courbes de charge), Factures normalisées, ADEME/ISO 50001',
            'data_format': data_format,
            'file_info': {'columns_detected': list(df.columns)},
            'supported_formats': [
                'GRD-F / Courbes de charge (Enedis, EDF, ENGIE)',
                'Factures normalisées (comptabilité entreprise)', 
                'ADEME / ISO 50001 (management énergétique)'
            ]
        }
    
    # Fallback pour format générique
    print("⚠️  Utilisation de l'analyse générique (format non spécialisé)")
    
    # Convertir les dates
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        print(f"📅 Dates converties - plage: {df['date'].min()} à {df['date'].max()}")
    else:
        print("⚠️  Aucune colonne 'date' trouvée - ajout de dates par défaut")
        df['date'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
    
    # Nettoyer les données numériques
    numeric_columns = ['consumption', 'total_consumption', 'hp_consumption', 'hc_consumption', 'estimated_bill']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"🔢 Colonne {col} convertie en numérique")
    
    # Déterminer la colonne de consommation
    consumption_col = None
    if 'consumption' in df.columns:
        consumption_col = 'consumption'
    elif 'total_consumption' in df.columns:
        consumption_col = 'total_consumption'
    elif 'hp_consumption' in df.columns:
        consumption_col = 'hp_consumption'
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            consumption_col = numeric_cols[0]
            df['consumption'] = df[consumption_col]
            print(f"🔢 Utilisation de la colonne numérique: {consumption_col}")
    
    if consumption_col is None:
        return {
            'error': 'Aucune donnée de consommation valide trouvée',
            'data_format': data_format,
            'file_info': {'columns_detected': list(df.columns)},
            'basic_stats': {},
            'advanced_stats': {},
            'peaks': [],
            'trends': {},
            'recommendations': [],
            'cost_analysis': {},
            'environmental_impact': {},
            'benchmarking': {},
            'solutions': []
        }
    
    df = df.dropna(subset=[consumption_col])
    print(f"📊 Lignes valides après nettoyage: {len(df)} (colonne utilisée: {consumption_col})")
    
    if len(df) == 0:
        return {
            'error': 'Aucune donnée de consommation valide trouvée',
            'data_format': data_format,
            'file_info': {},
            'basic_stats': {},
            'advanced_stats': {},
            'peaks': [],
            'trends': {},
            'recommendations': [],
            'cost_analysis': {},
            'environmental_impact': {},
            'benchmarking': {},
            'solutions': []
        }
    
    # === INFORMATIONS DU FICHIER ===
    file_info = {
        'total_records': len(df),
        'data_format': data_format,
        'columns_detected': list(df.columns),
        'date_range': {
            'start': 'Non spécifié',
            'end': 'Non spécifié', 
            'duration_days': 0
        },
        'data_quality': {
            'missing_values': df[consumption_col].isna().sum(),
            'zero_values': (df[consumption_col] == 0).sum(),
            'negative_values': (df[consumption_col] < 0).sum(),
            'quality_score': calculate_data_quality_score(df)
        }
    }
    
    # Ajouter les informations de date si disponibles
    if 'date' in df.columns and not df['date'].isna().all():
        try:
            file_info['date_range'] = {
                'start': str(df['date'].min()),
                'end': str(df['date'].max()),
                'duration_days': (pd.to_datetime(df['date'].max()) - pd.to_datetime(df['date'].min())).days + 1
            }
        except Exception as e:
            print(f"⚠️  Erreur lors du calcul de la plage de dates: {e}")
            # Garder les valeurs par défaut
    
    # === STATISTIQUES DE BASE ===
    consumption = df[consumption_col]
    basic_stats = {
        'total_consumption': float(consumption.sum()),
        'avg_consumption': float(consumption.mean()),
        'max_consumption': float(consumption.max()),
        'min_consumption': float(consumption.min()),
        'std_consumption': float(consumption.std()),
        'median_consumption': float(consumption.median())
    }
    
    # === ANALYSES SPÉCIFIQUES SELON LE FORMAT ===
    hp_hc_analysis = None
    zone_analysis = None
    billing_analysis = None
    
    if data_format == 'enterprise_advanced':
        # Analyse HP/HC
        if 'hp_consumption' in df.columns and 'hc_consumption' in df.columns:
            hp_hc_analysis = analyze_hp_hc_consumption(df)
        
        # Analyse par zones
        if 'zone' in df.columns:
            zone_analysis = analyze_zone_consumption(df)
        
        # Analyse de facturation
        if 'estimated_bill' in df.columns:
            billing_analysis = analyze_billing_patterns(df)
    
    # === STATISTIQUES AVANCÉES ===
    advanced_stats = {
        'quartiles': {
            'q1': float(consumption.quantile(0.25)),
            'q3': float(consumption.quantile(0.75)),
            'iqr': float(consumption.quantile(0.75) - consumption.quantile(0.25))
        },
        'distribution': {
            'skewness': float(consumption.skew()),
            'kurtosis': float(consumption.kurtosis()),
            'coefficient_variation': float(consumption.std() / consumption.mean()) if consumption.mean() > 0 else 0
        },
        'patterns': analyze_consumption_patterns(df),
        'seasonal_analysis': analyze_seasonal_patterns(df),
        'efficiency_metrics': calculate_efficiency_metrics(consumption)
    }
    
    # === DÉTECTION DES PICS ===
    threshold = basic_stats['avg_consumption'] + 1.5 * basic_stats['std_consumption']
    peaks_df = df[df[consumption_col] > threshold]
    
    peaks = []
    for _, peak in peaks_df.iterrows():
        peaks.append({
            'date': str(peak['date']) if 'date' in peak else 'N/A',
            'value': float(peak[consumption_col]),
            'percentage_above_avg': float(((peak[consumption_col] - basic_stats['avg_consumption']) / basic_stats['avg_consumption']) * 100),
            'severity': classify_peak_severity(peak[consumption_col], basic_stats['avg_consumption'], basic_stats['std_consumption']),
            'impact_cost': estimate_peak_cost_impact(peak[consumption_col], basic_stats['avg_consumption'])
        })
    
    # === ANALYSE DES TENDANCES ===
    trends = analyze_detailed_trends(df)
    
    # === ANALYSE DES COÛTS ===
    cost_analysis = calculate_cost_analysis(basic_stats, peaks, file_info)
    
    # === IMPACT ENVIRONNEMENTAL ===
    environmental_impact = calculate_environmental_impact(basic_stats, file_info)
    
    # === BENCHMARKING ===
    benchmarking = perform_benchmarking(basic_stats, file_info)
    
    # === RECOMMANDATIONS AVANCÉES ===
    recommendations = generate_advanced_recommendations({
        'basic_stats': basic_stats,
        'advanced_stats': advanced_stats,
        'peaks': peaks,
        'trends': trends,
        'cost_analysis': cost_analysis,
        'environmental_impact': environmental_impact,
        'benchmarking': benchmarking,
        'file_info': file_info
    })
    
    # === SOLUTIONS CONCRÈTES ===
    solutions = generate_concrete_solutions(recommendations, cost_analysis)
    
    return {
        'file_info': file_info,
        'basic_stats': basic_stats,
        'advanced_stats': advanced_stats,
        'peaks': peaks,
        'trends': trends,
        'cost_analysis': cost_analysis,
        'environmental_impact': environmental_impact,
        'benchmarking': benchmarking,
        'recommendations': recommendations,
        'solutions': solutions,
        # Nouvelles analyses pour format entreprise
        'hp_hc_analysis': hp_hc_analysis,
        'zone_analysis': zone_analysis,
        'billing_analysis': billing_analysis,
        'data_format': data_format,
        # Compatibilité avec l'ancien format
        'total_consumption': basic_stats['total_consumption'],
        'avg_consumption': basic_stats['avg_consumption'],
        'max_consumption': basic_stats['max_consumption'],
        'min_consumption': basic_stats['min_consumption'],
        'std_consumption': basic_stats['std_consumption'],
        'statistics': {
            'median': basic_stats['median_consumption'],
            'quartile_25': advanced_stats['quartiles']['q1'],
            'quartile_75': advanced_stats['quartiles']['q3'],
            'coefficient_variation': advanced_stats['distribution']['coefficient_variation'],
            'efficiency_score': advanced_stats['efficiency_metrics']['overall_score']
        }
    }

def create_advanced_chart(df, analysis):
    """Crée un graphique avancé avec Plotly - harmonisé pour tous les formats"""
    try:
        print(f"🔍 Debug graphique - colonnes disponibles: {list(df.columns)}")
        
        if 'date' not in df.columns:
            print("❌ Colonne 'date' manquante dans le DataFrame")
            return None
            
        fig = go.Figure()
        
        # Préparer les données
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Détecter le format de données
        data_format = analysis.get('data_format', 'standard')
        
        # Déterminer la colonne de consommation principale
        consumption_col = None
        if 'consumption' in df.columns:
            consumption_col = 'consumption'
        elif 'total_consumption' in df.columns:
            consumption_col = 'total_consumption'
        
        if not consumption_col:
            print("❌ Aucune colonne de consommation trouvée")
            return None
            
        # Graphique unifié pour tous les formats
        print(f"📊 Génération graphique unifié - Format: {data_format}")
        df[consumption_col] = pd.to_numeric(df[consumption_col], errors='coerce')
        
        # Nom unifié pour tous les formats
        graph_name = 'Consommation (kWh)'
        tooltip_label = 'Consommation'
        
        # Ligne principale unique pour tous les formats
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df[consumption_col],
            mode='lines+markers',
            name=graph_name,
            line=dict(color='#2E86AB', width=4),
            marker=dict(size=8),
            hovertemplate=f'<b>Date:</b> %{{x}}<br><b>{tooltip_label}:</b> %{{y:.1f}} kWh<extra></extra>'
        ))
        
        # Ligne de moyenne (adaptée aux différentes structures)
        if 'basic_stats' in analysis and 'avg_consumption' in analysis['basic_stats']:
            avg_consumption = analysis['basic_stats']['avg_consumption']
            std_consumption = analysis['basic_stats'].get('std_consumption', 0)
        else:
            avg_consumption = analysis.get('avg_consumption', df[consumption_col].mean())
            std_consumption = analysis.get('std_consumption', df[consumption_col].std())
        
        fig.add_hline(
            y=avg_consumption,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Moyenne: {avg_consumption:.1f} kWh",
            annotation_position="top right"
        )
        
        # Seuil d'alerte
        alert_threshold = avg_consumption + 1.5 * std_consumption
        fig.add_hline(
            y=alert_threshold,
            line_dash="dot",
            line_color="red",
            annotation_text=f"Seuil d'alerte: {alert_threshold:.1f} kWh",
            annotation_position="top right"
        )
        
        # Marquer les pics (toujours sur la consommation principale)
        if analysis['peaks']:
            peak_dates = [pd.to_datetime(peak['date']) for peak in analysis['peaks']]
            peak_values = [peak['value'] for peak in analysis['peaks']]
            
            fig.add_trace(go.Scatter(
                x=peak_dates,
                y=peak_values,
                mode='markers',
                name='Pics de consommation',
                marker=dict(color='red', size=12, symbol='triangle-up'),
                hovertemplate='<b>Pic détecté</b><br><b>Date:</b> %{x}<br><b>Consommation:</b> %{y:.1f} kWh<extra></extra>'
            ))
        
        # Moyennes mobiles (toujours sur la consommation principale)
        if len(df) >= 7:
            df['ma_7'] = df[consumption_col].rolling(window=7, center=True).mean()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['ma_7'],
                mode='lines',
                name='Moyenne mobile (7j)',
                line=dict(color='green', width=2, dash='dash'),
                opacity=0.7,
                hovertemplate='<b>Date:</b> %{x}<br><b>Moyenne 7j:</b> %{y:.1f} kWh<extra></extra>'
            ))
        
        # Configuration du graphique harmonisée
        title_text = 'Analyse de la Consommation Énergétique'
        
        fig.update_layout(
            title={
                'text': title_text,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2E86AB'}
            },
            xaxis_title='Date',
            yaxis_title='Consommation (kWh)',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        print(f"📊 Graphique généré avec succès - Format: {data_format}")
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print(f"❌ Erreur dans create_advanced_chart: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_professional_pdf(analysis, filename, df=None):
    """Génère un rapport PDF professionnel complet"""
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2E86AB'),
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#2E86AB'),
        alignment=TA_LEFT
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Contenu du PDF
    story = []
    
    # Titre
    story.append(Paragraph("StatEnergie", title_style))
    story.append(Paragraph("Rapport d'Analyse Énergétique Professionnel", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    # Informations du rapport
    info_data = [
        ['Fichier analysé:', filename],
        ['Date de génération:', datetime.now().strftime('%d/%m/%Y à %H:%M')],
        ['Période d\'analyse:', 'Données complètes du fichier'],
        ['Type d\'analyse:', 'Analyse avancée avec détection d\'anomalies']
    ]
    
    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4FD')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2E86AB'))
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Gestion de la compatibilité avec l'ancienne et nouvelle structure
    efficiency_score = 0
    if 'statistics' in analysis and 'efficiency_score' in analysis['statistics']:
        efficiency_score = analysis['statistics']['efficiency_score']
    elif 'advanced_stats' in analysis and 'efficiency_metrics' in analysis['advanced_stats']:
        efficiency_score = analysis['advanced_stats']['efficiency_metrics']['overall_score']
    else:
        efficiency_score = 50  # Valeur par défaut
    
    # Résumé exécutif
    story.append(Paragraph("Résumé Exécutif", heading_style))
    
    if efficiency_score >= 75:
        summary = f"Votre installation présente une efficacité énergétique <b>excellente</b> ({efficiency_score:.1f}/100)."
    elif efficiency_score >= 50:
        summary = f"Votre installation présente une efficacité énergétique <b>modérée</b> ({efficiency_score:.1f}/100)."
    else:
        summary = f"Votre installation présente une efficacité énergétique <b>faible</b> ({efficiency_score:.1f}/100)."
    
    num_peaks = len(analysis.get('peaks', []))
    avg_consumption = analysis.get('avg_consumption', analysis.get('basic_stats', {}).get('avg_consumption', 0))
    
    summary += f" L'analyse révèle {num_peaks} pics de consommation et "
    summary += f"une consommation moyenne de {avg_consumption:.1f} kWh."
    
    story.append(Paragraph(summary, normal_style))
    story.append(Spacer(1, 15))
    
    # Statistiques détaillées
    story.append(Paragraph("Statistiques Détaillées", heading_style))
    
    # Utiliser la nouvelle structure si disponible
    if 'basic_stats' in analysis:
        stats = analysis['basic_stats']
        adv_stats = analysis.get('advanced_stats', {})
        total_consumption = stats.get('total_consumption', 0)
        avg_consumption = stats.get('avg_consumption', 0)
        max_consumption = stats.get('max_consumption', 0)
        min_consumption = stats.get('min_consumption', 0)
        std_consumption = stats.get('std_consumption', 0)
        median = stats.get('median_consumption', 0)
        coefficient_variation = adv_stats.get('distribution', {}).get('coefficient_variation', 0)
    else:
        # Compatibilité avec l'ancienne structure
        total_consumption = analysis.get('total_consumption', 0)
        avg_consumption = analysis.get('avg_consumption', 0)
        max_consumption = analysis.get('max_consumption', 0)
        min_consumption = analysis.get('min_consumption', 0)
        std_consumption = analysis.get('std_consumption', 0)
        median = analysis.get('statistics', {}).get('median', 0)
        coefficient_variation = analysis.get('statistics', {}).get('coefficient_variation', 0)
    
    stats_data = [
        ['Métrique', 'Valeur', 'Unité'],
        ['Consommation totale', f"{total_consumption:.1f}", 'kWh'],
        ['Consommation moyenne', f"{avg_consumption:.1f}", 'kWh'],
        ['Consommation maximale', f"{max_consumption:.1f}", 'kWh'],
        ['Consommation minimale', f"{min_consumption:.1f}", 'kWh'],
        ['Écart-type', f"{std_consumption:.1f}", 'kWh'],
        ['Médiane', f"{median:.1f}", 'kWh'],
        ['Coefficient de variation', f"{coefficient_variation:.2f}", '-'],
        ['Score d\'efficacité', f"{efficiency_score:.1f}", '/100']
    ]
    
    stats_table = Table(stats_data, colWidths=[200, 100, 50])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2E86AB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Analyse des pics
    story.append(Paragraph("Analyse des Pics de Consommation", heading_style))
    
    peaks = analysis.get('peaks', [])
    if peaks:
        story.append(Paragraph(f"<b>{len(peaks)} pics de consommation</b> ont été détectés:", normal_style))
        
        peaks_data = [['Date', 'Consommation (kWh)', 'Dépassement (%)', 'Sévérité']]
        for peak in peaks[:10]:  # Limiter à 10 pics
            date_str = peak.get('date', 'N/A')
            if date_str != 'N/A':
                try:
                    # Formatage de la date
                    date_obj = pd.to_datetime(date_str)
                    date_str = date_obj.strftime('%d/%m/%Y')
                except:
                    pass
            
            peaks_data.append([
                date_str,
                f"{peak.get('value', 0):.1f}",
                f"{peak.get('percentage_above_avg', 0):.1f}%",
                get_severity_display(peak.get('severity', 'medium'))
            ])
        
        peaks_table = Table(peaks_data, colWidths=[120, 100, 100, 80])
        peaks_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B6B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FF6B6B')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF5F5')])
        ]))
        
        story.append(peaks_table)
    else:
        story.append(Paragraph("✅ Aucun pic de consommation significatif détecté.", normal_style))
    
    story.append(Spacer(1, 20))
    
    # Recommandations
    story.append(Paragraph("Recommandations Personnalisées", heading_style))
    
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations[:5], 1):  # Limiter à 5 recommandations
            priority_color = {
                'high': colors.HexColor('#FF6B6B'),
                'élevée': colors.HexColor('#FF6B6B'),
                'medium': colors.HexColor('#FFA500'),
                'moyenne': colors.HexColor('#FFA500'),
                'low': colors.HexColor('#4CAF50'),
                'faible': colors.HexColor('#4CAF50')
            }.get(rec.get('priority', 'medium').lower(), colors.black)
            
            story.append(Paragraph(f"<b>{i}. {rec.get('title', 'Recommandation')}</b>", 
                                 ParagraphStyle('RecTitle', parent=normal_style, textColor=priority_color)))
            story.append(Paragraph(f"<b>Diagnostic:</b> {rec.get('message', 'Non spécifié')}", normal_style))
            story.append(Paragraph(f"<b>Action recommandée:</b> {rec.get('action', 'Non spécifiée')}", normal_style))
            story.append(Paragraph(f"<b>Potentiel d'économie:</b> {rec.get('savings_potential', 'Non estimé')}", normal_style))
            story.append(Spacer(1, 10))
    else:
        story.append(Paragraph("✅ Votre profil de consommation est optimal.", normal_style))
    
    # === NOUVELLE SECTION : ANALYSE ÉCONOMIQUE APPROFONDIE ===
    story.append(Spacer(1, 20))
    story.append(Paragraph("Analyse Économique et Opportunités d'Investissement", heading_style))
    
    # Récupérer l'analyse des coûts
    cost_analysis = analysis.get('cost_analysis', {})
    
    if cost_analysis:
        # Résumé financier
        annual_projection = cost_analysis.get('annual_projection', 0)
        total_savings = cost_analysis.get('potential_savings', {}).get('total_annuel', 0)
        
        story.append(Paragraph(f"<b>Projection annuelle :</b> {annual_projection:.0f}€", normal_style))
        story.append(Paragraph(f"<b>Économies potentielles :</b> {total_savings:.0f}€/an ({total_savings/annual_projection*100:.1f}%)", normal_style))
        story.append(Spacer(1, 10))
        
        # Répartition des coûts
        cost_breakdown = cost_analysis.get('cost_breakdown', {})
        if cost_breakdown:
            story.append(Paragraph("Répartition des Coûts", 
                                 ParagraphStyle('SubHeading', parent=normal_style, fontSize=12, textColor=colors.HexColor('#2E86AB'))))
            
            breakdown_data = [
                ['Poste de Coût', 'Montant (€)', 'Pourcentage'],
                ['Consommation de base', f"{cost_breakdown.get('consommation_base', 0):.0f}", 
                 f"{100-cost_breakdown.get('pourcentage_pics', 0):.1f}%"],
                ['Pics de consommation', f"{cost_breakdown.get('pics_consommation', 0):.0f}", 
                 f"{cost_breakdown.get('pourcentage_pics', 0):.1f}%"]
            ]
            
            breakdown_table = Table(breakdown_data, colWidths=[180, 80, 80])
            breakdown_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFA500')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FFA500')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF8DC')])
            ]))
            
            story.append(breakdown_table)
            story.append(Spacer(1, 15))
        
        # Opportunités d'investissement
        investments = cost_analysis.get('investment_opportunities', [])
        if investments:
            story.append(Paragraph("Top 3 des Investissements Recommandés", 
                                 ParagraphStyle('SubHeading', parent=normal_style, fontSize=12, textColor=colors.HexColor('#2E86AB'))))
            
            invest_data = [['Solution', 'Investissement (€)', 'Économies/an (€)', 'ROI (années)']]
            for inv in investments[:3]:
                invest_data.append([
                    inv.get('solution', 'N/A'),
                    f"{inv.get('investissement', 0):,.0f}".replace(',', ' '),
                    f"{inv.get('economies_annuelles', 0):.0f}",
                    f"{inv.get('roi_annees', 0):.1f}"
                ])
            
            invest_table = Table(invest_data, colWidths=[140, 80, 80, 60])
            invest_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4CAF50')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8F0')])
            ]))
            
            story.append(invest_table)
            story.append(Spacer(1, 15))
        
        # Recommandations économiques prioritaires
        economic_recs = cost_analysis.get('economic_recommendations', [])
        if economic_recs:
            story.append(Paragraph("Plan d'Action Économique Prioritaire", 
                                 ParagraphStyle('SubHeading', parent=normal_style, fontSize=12, textColor=colors.HexColor('#2E86AB'))))
            
            for i, rec in enumerate(economic_recs[:3], 1):
                # Couleur selon la catégorie
                if 'Urgente' in rec.get('categorie', ''):
                    cat_color = colors.HexColor('#FF6B6B')
                elif 'Court terme' in rec.get('categorie', ''):
                    cat_color = colors.HexColor('#FFA500')
                else:
                    cat_color = colors.HexColor('#4CAF50')
                
                story.append(Paragraph(f"<b>{i}. {rec.get('titre', 'Action recommandée')}</b>", 
                                     ParagraphStyle('EconRecTitle', parent=normal_style, textColor=cat_color, fontSize=11)))
                story.append(Paragraph(f"<b>Catégorie:</b> {rec.get('categorie', 'N/A')}", normal_style))
                story.append(Paragraph(f"<b>Impact financier:</b> {rec.get('impact_financier', 0):.0f}€/an", normal_style))
                story.append(Paragraph(f"<b>ROI estimé:</b> {rec.get('roi_estime', 'N/A')}", normal_style))
                story.append(Paragraph(f"<b>Investissement:</b> {rec.get('investissement_requis', 'N/A')}", normal_style))
                
                # Actions principales
                actions = rec.get('actions', [])
                if actions:
                    actions_text = "<br/>".join([f"• {action}" for action in actions[:3]])
                    story.append(Paragraph(f"<b>Actions clés:</b><br/>{actions_text}", normal_style))
                
                story.append(Spacer(1, 8))
    
    # Conclusion enrichie
    story.append(Spacer(1, 20))
    story.append(Paragraph("Conclusion et Prochaines Étapes", heading_style))
    
    # Calcul du potentiel total d'économies
    total_potential = cost_analysis.get('potential_savings', {}).get('total_annuel', 0) if cost_analysis else 0
    
    conclusion_text = f"""
    Cette analyse économique révèle un potentiel d'optimisation significatif de {total_potential:.0f}€ par an.
    Votre score d'efficacité de {efficiency_score:.1f}/100 indique des opportunités d'amélioration concrètes.
    
    <b>Prochaines étapes recommandées :</b>
    1. Mettre en place les actions immédiates (0-3 mois)
    2. Évaluer les investissements à court terme (3-12 mois) 
    3. Planifier les optimisations structurelles (1-3 ans)
    4. Suivre mensuellement les performances énergétiques
    
    <b>Support StatEnergie :</b>
    Nos experts peuvent vous accompagner dans la mise en œuvre de ces recommandations
    et le suivi de vos économies d'énergie. Contactez-nous pour un audit personnalisé.
    """
    
    story.append(Paragraph(conclusion_text, normal_style))
    
    # Générer le PDF
    doc.build(story)
    
    # Réinitialiser le buffer
    buffer.seek(0)
    return buffer

# === FONCTIONS D'ANALYSE SPÉCIFIQUES ENTREPRISE ===

def analyze_hp_hc_consumption(df):
    """Analyse la consommation HP/HC"""
    analysis = {
        'total_hp': 0,
        'total_hc': 0,
        'ratio_hp_hc': 0,
        'avg_hp': 0,
        'avg_hc': 0,
        'peak_hp': 0,
        'peak_hc': 0,
        'efficiency_score': 0,
        'recommendations': []
    }
    
    if 'hp_consumption' not in df.columns or 'hc_consumption' not in df.columns:
        return analysis
    
    # Calculs de base
    total_hp = df['hp_consumption'].sum()
    total_hc = df['hc_consumption'].sum()
    
    analysis.update({
        'total_hp': float(total_hp),
        'total_hc': float(total_hc),
        'ratio_hp_hc': float(total_hp / total_hc) if total_hc > 0 else 0,
        'avg_hp': float(df['hp_consumption'].mean()),
        'avg_hc': float(df['hc_consumption'].mean()),
        'peak_hp': float(df['hp_consumption'].max()),
        'peak_hc': float(df['hc_consumption'].max())
    })
    
    # Score d'efficacité basé sur la répartition HP/HC
    # Idéalement, HC devrait être plus élevé (tarif plus avantageux)
    if total_hc > total_hp:
        analysis['efficiency_score'] = 85  # Bon usage
    elif total_hc > total_hp * 0.8:
        analysis['efficiency_score'] = 70  # Acceptable
    else:
        analysis['efficiency_score'] = 45  # À améliorer
    
    # Recommandations
    if analysis['ratio_hp_hc'] > 1.5:
        analysis['recommendations'].append("Optimiser l'utilisation en heures creuses pour réduire les coûts")
    if analysis['ratio_hp_hc'] < 0.5:
        analysis['recommendations'].append("Excellente utilisation des heures creuses - maintenir cette répartition")
    
    return analysis

def analyze_zone_consumption(df):
    """Analyse la consommation par zone"""
    analysis = {
        'zones_summary': {},
        'total_zones': 0,
        'most_consuming_zone': '',
        'least_consuming_zone': '',
        'zone_efficiency': {},
        'recommendations': []
    }
    
    if 'zone' not in df.columns:
        return analysis
    
    # Analyse par zone
    zone_stats = df.groupby('zone').agg({
        'consumption': ['sum', 'mean', 'count'],
        'estimated_bill': 'sum' if 'estimated_bill' in df.columns else 'size'
    }).round(2)
    
    zone_stats.columns = ['total_consumption', 'avg_consumption', 'count_readings', 'total_cost']
    
    # Convertir en dictionnaire
    analysis['zones_summary'] = zone_stats.to_dict('index')
    analysis['total_zones'] = len(zone_stats)
    
    # Zone la plus/moins consommatrice
    if not zone_stats.empty:
        analysis['most_consuming_zone'] = zone_stats['total_consumption'].idxmax()
        analysis['least_consuming_zone'] = zone_stats['total_consumption'].idxmin()
    
    # Efficacité par zone (consommation par lecture)
    for zone in zone_stats.index:
        efficiency = zone_stats.loc[zone, 'avg_consumption']
        if efficiency > 2000:
            analysis['zone_efficiency'][zone] = 'Élevée'
        elif efficiency > 1000:
            analysis['zone_efficiency'][zone] = 'Modérée'
        else:
            analysis['zone_efficiency'][zone] = 'Optimale'
    
    # Recommandations
    if analysis['total_zones'] > 1:
        max_zone = analysis['most_consuming_zone']
        analysis['recommendations'].append(f"Focus sur l'optimisation de la zone {max_zone}")
    
    return analysis

def analyze_billing_patterns(df):
    """Analyse les patterns de facturation"""
    analysis = {
        'total_cost': 0,
        'avg_daily_cost': 0,
        'cost_trend': 'stable',
        'cost_variability': 'faible',
        'projected_monthly': 0,
        'projected_yearly': 0,
        'cost_efficiency': 'good',
        'recommendations': []
    }
    
    if 'estimated_bill' not in df.columns:
        return analysis
    
    # Calculs de base
    total_cost = df['estimated_bill'].sum()
    avg_cost = df['estimated_bill'].mean()
    
    analysis.update({
        'total_cost': float(total_cost),
        'avg_daily_cost': float(avg_cost)
    })
    
    # Projections
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        days_covered = (df['date'].max() - df['date'].min()).days + 1
        if days_covered > 0:
            daily_avg = total_cost / days_covered
            analysis['projected_monthly'] = float(daily_avg * 30)
            analysis['projected_yearly'] = float(daily_avg * 365)
    
    # Variabilité des coûts
    cost_std = df['estimated_bill'].std()
    if cost_std / avg_cost > 0.3:
        analysis['cost_variability'] = 'élevée'
    elif cost_std / avg_cost > 0.15:
        analysis['cost_variability'] = 'modérée'
    else:
        analysis['cost_variability'] = 'faible'
    
    # Efficacité des coûts (€/kWh)
    if 'consumption' in df.columns:
        cost_per_kwh = avg_cost / df['consumption'].mean()
        if cost_per_kwh < 0.15:
            analysis['cost_efficiency'] = 'excellent'
        elif cost_per_kwh < 0.20:
            analysis['cost_efficiency'] = 'good'
        else:
            analysis['cost_efficiency'] = 'to_improve'
    
    # Recommandations
    if analysis['cost_variability'] == 'élevée':
        analysis['recommendations'].append("Analyser les pics de consommation pour stabiliser les coûts")
    if analysis['projected_yearly'] > 50000:
        analysis['recommendations'].append("Considérer un audit énergétique approfondi")
    
    return analysis

def calculate_data_quality_score(df):
    """Calcule un score de qualité des données basé sur plusieurs critères"""
    score = 100  # Score de départ parfait
    
    # Si le DataFrame est vide ou None
    if df is None or df.empty:
        return 0
    
    # Vérifier les colonnes essentielles
    essential_columns = ['consumption', 'date']
    for col in essential_columns:
        if col not in df.columns:
            score -= 30  # Pénalité importante pour l'absence de colonnes essentielles
    
    # Si consommation existe, vérifier la qualité
    if 'consumption' in df.columns:
        # Pourcentage de valeurs manquantes
        missing_pct = df['consumption'].isna().mean() * 100
        score -= min(30, missing_pct * 3)  # Jusqu'à -30 points pour les valeurs manquantes
        
        # Pourcentage de valeurs nulles
        zero_pct = (df['consumption'] == 0).mean() * 100
        score -= min(15, zero_pct * 1.5)  # Jusqu'à -15 points pour trop de zéros
        
        # Valeurs négatives (généralement des erreurs)
        negative_pct = (df['consumption'] < 0).mean() * 100
        score -= min(20, negative_pct * 10)  # Jusqu'à -20 points pour les valeurs négatives
        
        # Vérifier les valeurs aberrantes (outliers)
        if len(df) > 5:
            q1 = df['consumption'].quantile(0.25)
            q3 = df['consumption'].quantile(0.75)
            iqr = q3 - q1
            outlier_pct = ((df['consumption'] < (q1 - 3 * iqr)) | (df['consumption'] > (q3 + 3 * iqr))).mean() * 100
            score -= min(15, outlier_pct * 3)  # Jusqu'à -15 points pour les valeurs aberrantes
    
    # Vérifier la régularité des dates si elles existent
    if 'date' in df.columns and not df['date'].isna().all():
        try:
            df_with_date = df.copy()
            df_with_date['date'] = pd.to_datetime(df_with_date['date'])
            df_with_date = df_with_date.sort_values('date')
            
            # Vérifier la période couverte (préférer au moins 30 jours pour une analyse pertinente)
            date_range = (df_with_date['date'].max() - df_with_date['date'].min()).days
            if date_range < 30:
                score -= min(10, (30 - date_range) / 3)  # Jusqu'à -10 points pour une période trop courte
            
            # Vérifier les écarts entre les dates
            if len(df_with_date) > 1:
                df_with_date['date_diff'] = df_with_date['date'].diff().dt.days
                irregular_pct = (df_with_date['date_diff'].dropna() != df_with_date['date_diff'].dropna().mode()[0]).mean() * 100
                score -= min(10, irregular_pct / 10)  # Jusqu'à -10 points pour des données irrégulières
        except:
            score -= 10  # Erreur dans le traitement des dates
    
    # Bonus pour la richesse des données
    extra_useful_columns = ['hp_consumption', 'hc_consumption', 'estimated_bill', 'zone', 'temperature']
    for col in extra_useful_columns:
        if col in df.columns and not df[col].isna().all():
            score += 3  # +3 points par colonne utile supplémentaire
    
    # Normalisation finale du score entre 0 et 100
    return max(0, min(100, score))

def create_dataframe_from_manual_entry(bill_data):
    """Crée un DataFrame optimisé à partir des données de facturation saisies manuellement"""
    try:
        print(f"⚙️ Création d'un DataFrame à partir des données manuelles: {bill_data}")
        
        # S'assurer que les valeurs numériques sont correctement converties
        consumption = 0
        try:
            consumption = float(bill_data.get("consumption_kwh", 0))
        except:
            consumption = 100  # Valeur par défaut si la conversion échoue
            
        amount = 0
        try:
            amount = float(bill_data.get("amount", 0))
        except:
            amount = 50  # Valeur par défaut si la conversion échoue
        
        # Gestion améliorée des dates
        bill_date = datetime.now()
        try:
            if bill_data.get("bill_date"):
                bill_date = pd.to_datetime(bill_data.get("bill_date"))
            else:
                bill_date = datetime.now()
        except:
            bill_date = datetime.now()
            
        # Période de facturation
        period_start = bill_date - timedelta(days=30)  # Par défaut: 30 jours avant
        period_end = bill_date  # Par défaut: date de facture
        
        try:
            if bill_data.get("period_start"):
                period_start = pd.to_datetime(bill_data.get("period_start"))
        except:
            pass
            
        try:
            if bill_data.get("period_end"):
                period_end = pd.to_datetime(bill_data.get("period_end"))
        except:
            pass
        
        # Données de base pour le DataFrame
        data = {
            "provider": [bill_data.get("provider", "Non spécifié")],
            "date": [bill_date],
            "consumption": [consumption],
            "estimated_bill": [amount],
            "consumption_kwh": [consumption],  # Pour la compatibilité
            "period_start": [period_start],
            "period_end": [period_end],
            "client_ref": [bill_data.get("client_ref", "")],
            "meter_number": [bill_data.get("meter_number", "")]
        }
            
        # Créer le DataFrame de base
        df_base = pd.DataFrame(data)
        
        # Générer une série temporelle basée sur les données saisies
        # Cette étape est cruciale pour permettre une analyse significative
        days_in_period = (period_end - period_start).days
        if days_in_period <= 0:
            days_in_period = 30  # Période minimale par défaut
        
        # Calculer la consommation journalière moyenne
        daily_consumption = consumption / days_in_period
        daily_cost = amount / days_in_period
        
        # Générer des points répartis sur la période
        num_points = min(30, days_in_period)  # Maximum 30 points
        date_range = pd.date_range(start=period_start, end=period_end, periods=num_points)
        
        # Créer des variations réalistes
        variation_factor = 0.3  # 30% de variation
        consumption_values = [daily_consumption * (1 + variation_factor * (np.random.random() - 0.5)) for _ in range(num_points)]
        bill_values = [daily_cost * (1 + variation_factor * (np.random.random() - 0.5)) for _ in range(num_points)]
        
        # Construire le DataFrame final
        df = pd.DataFrame({
            "date": date_range,
            "consumption": consumption_values,
            "estimated_bill": bill_values,
            "provider": [bill_data.get("provider", "Non spécifié")] * num_points,
            "client_ref": [bill_data.get("client_ref", "")] * num_points,
            "meter_number": [bill_data.get("meter_number", "")] * num_points,
            "consumption_kwh": consumption_values,  # Pour la compatibilité
            "source_type": ["manuel"] * num_points  # Marquer les données comme manuelles
        })
        
        print(f"✅ DataFrame créé avec succès: {df.shape} lignes et {len(df.columns)} colonnes")
        print(f"📊 Aperçu des données générées:\n{df.head(3)}")
        
        return df
    
    except Exception as e:
        print(f"❌ Erreur lors de la création du DataFrame manuel: {str(e)}")
        traceback.print_exc()
        
        # Retourner un DataFrame minimal mais fonctionnel pour éviter les erreurs
        default_dates = [datetime.now() - timedelta(days=i*5) for i in range(10)]
        default_consumption = [100 - i*5 for i in range(10)]
        default_bill = [50 - i*2.5 for i in range(10)]
        
        return pd.DataFrame({
            "date": default_dates,
            "consumption": default_consumption,
            "estimated_bill": default_bill,
            "provider": ["Saisie manuelle"] * 10,
            "consumption_kwh": default_consumption,  # Pour la compatibilité
            "source_type": ["manuel"] * 10
        })

# Routes Flask
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/formats')
def formats():
    """Page des formats de fichiers supportés"""
    return render_template('formats.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Gestion de l'upload de fichiers"""
    if request.method == 'POST':
        # Vérifier si un fichier a été sélectionné
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné.')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Aucun fichier sélectionné.')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Si c'est un fichier PDF, traiter d'abord avec l'analyseur PDF
            if filename.lower().endswith('.pdf'):
                try:
                    # Traiter le fichier PDF pour en extraire les données
                    pdf_analyzer = PDFBillAnalyzer()
                    bill_data = pdf_analyzer.process_pdf_bill(filepath)
                    
                    if "error" in bill_data:
                        flash(f"Impossible d'analyser le PDF: {bill_data['error']}")
                        return redirect(request.url)
                    
                    # Créer un DataFrame à partir des données de facturation
                    df = pdf_analyzer.create_dataframe_from_bill(bill_data)
                    
                    if df is None or df.empty:
                        flash("Impossible d'extraire des données valides du PDF.")
                        return redirect(request.url)
                    
                    # Sauvegarder les données extraites dans un CSV temporaire
                    csv_filename = filename.replace('.pdf', '.csv')
                    csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
                    df.to_csv(csv_filepath, index=False)
                    
                    flash('PDF analysé et données extraites avec succès!')
                    return redirect(url_for('dashboard', filename=csv_filename))
                except Exception as e:
                    flash(f"Erreur lors du traitement du PDF: {str(e)}")
                    return redirect(request.url)
            else:
                # Traitement normal pour les autres types de fichiers
                flash('Fichier uploadé avec succès!')
                return redirect(url_for('dashboard', filename=filename))
        else:
            flash('Type de fichier non autorisé. Utilisez CSV, Excel, JSON ou PDF.')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/dashboard/<filename>')
def dashboard(filename):
    """Dashboard principal - redirige vers l'analyse avancée"""
    return redirect(url_for('dashboard_advanced', filename=filename))

@app.route('/dashboard_advanced/<filename>')
def dashboard_advanced(filename):
    """Dashboard avancé avec analyse enrichie"""
    print(f"🔍 DEBUG: Entrée dans dashboard_advanced avec filename: {filename}")
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"🔍 DEBUG: Chemin fichier: {file_path}")
        
        # Vérifier si c'est une analyse de données manuelles
        is_manual = "manual" in filename
        if is_manual:
            print(f"📝 MANUEL: Traitement des données saisies manuellement: {filename}")
        
        if not os.path.exists(file_path):
            print(f"❌ DEBUG: Fichier non trouvé: {file_path}")
            flash('Fichier non trouvé.')
            return redirect(url_for('index'))
        
        print(f"✅ DEBUG: Fichier existe, début de lecture...")
        
        # Lire le fichier selon son extension avec gestion d'encodage
        try:
            if filename.endswith('.csv'):
                # Essayer différents encodages
                for encoding in ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        print(f"✅ Fichier lu avec l'encodage: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # Si aucun encodage ne fonctionne
                    df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
                    print("⚠️  Fichier lu avec gestion d'erreurs d'encodage")
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            elif filename.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                flash('Format de fichier non supporté.')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erreur lors de la lecture du fichier: {str(e)}')
            return redirect(url_for('index'))
        
        print(f"📊 Colonnes détectées: {list(df.columns)}")
        print(f"📏 Dimensions: {df.shape}")
        print(f"🔍 Aperçu des premières lignes:")
        print(df.head())
        
        # Effectuer l'analyse avancée (qui inclut la détection de format et standardisation)
        try:
            print("🔄 Démarrage de l'analyse...")
            analysis = analyze_consumption_data(df)
            print("✅ Analyse terminée avec succès")
        except Exception as e:
            print(f"❌ Erreur pendant l'analyse: {str(e)}")
            print(f"📋 Type d'erreur: {type(e).__name__}")
            import traceback
            print("📝 Traceback complet:")
            traceback.print_exc()
            flash(f'Erreur lors de l\'analyse: {str(e)}')
            return redirect(url_for('index'))
        
        # Générer le graphique
        try:
            print("📈 Génération du graphique...")
            
            # Préparer le DataFrame pour le graphique
            df_for_chart = df.copy()
            
            # Pour le format facturation, ajouter les colonnes nécessaires
            data_format = analysis.get('data_format', 'standard')
            
            if data_format == 'enterprise_facturation':
                # Ajouter une colonne date si elle n'existe pas
                if 'date' not in df_for_chart.columns:
                    if 'Mois' in df_for_chart.columns:
                        df_for_chart['date'] = pd.to_datetime(df_for_chart['Mois'] + '-01')
                    else:
                        # Date par défaut
                        df_for_chart['date'] = pd.date_range(start='2024-01-01', periods=len(df_for_chart), freq='M')
                
                # Ajouter une colonne consumption si elle n'existe pas
                if 'consumption' not in df_for_chart.columns:
                    if 'Consommation totale (kWh)' in df_for_chart.columns:
                        df_for_chart['consumption'] = df_for_chart['Consommation totale (kWh)']
                    elif 'Consommation (kWh)' in df_for_chart.columns:
                        df_for_chart['consumption'] = df_for_chart['Consommation (kWh)']
                    else:
                        # Utiliser la première colonne numérique
                        numeric_cols = df_for_chart.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            df_for_chart['consumption'] = df_for_chart[numeric_cols[0]]
            
            chart_data = create_advanced_chart(df_for_chart, analysis)
            print("✅ Graphique généré avec succès")
        except Exception as e:
            print(f"❌ Erreur lors de la génération du graphique: {str(e)}")
            import traceback
            print("📝 Traceback génération graphique:")
            traceback.print_exc()
            chart_data = None
        
        # Date d'analyse
        analysis_date = datetime.now().strftime('%d/%m/%Y à %H:%M')
        
        print(f"🎯 DEBUG: Avant render_template dashboard_advanced.html")
        print(f"🎯 DEBUG: analysis keys: {list(analysis.keys()) if analysis else 'None'}")
        print(f"🎯 DEBUG: chart_data exists: {chart_data is not None}")
        
        result = render_template('dashboard_advanced.html', 
                             analysis=analysis,
                             chart_data=chart_data,
                             filename=filename,
                             analysis_date=analysis_date)
        
        print(f"✅ DEBUG: Template rendu avec succès, retour de la réponse")
        return result
        
    except Exception as e:
        print(f"❌ DEBUG: Exception dans dashboard_advanced: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Erreur lors de l\'analyse: {str(e)}')
        return redirect(url_for('index'))

@app.route('/generate_report/<filename>')
def generate_report(filename):
    """Génération du rapport PDF professionnel"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            flash('Fichier non trouvé.')
            return redirect(url_for('upload_file'))
        
        # Charger et analyser les données
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filename.endswith('.json'):
            df = pd.read_json(filepath)
        
        # Standardiser les colonnes
        if 'Date' in df.columns and 'date' not in df.columns:
            df['date'] = df['Date']
        if 'Consommation' in df.columns and 'consumption' not in df.columns:
            df['consumption'] = df['Consommation']
        if 'kWh' in df.columns and 'consumption' not in df.columns:
            df['consumption'] = df['kWh']
        
        analysis = analyze_consumption_data(df)
        
        # Générer le PDF professionnel
        pdf_buffer = generate_professional_pdf(analysis, filename, df)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'rapport_energetique_{filename.split(".")[0]}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Erreur lors de la génération du rapport: {str(e)}')
       
        return redirect(url_for('dashboard', filename=filename))

@app.route('/sample_data')
def sample_data():
    """Génère des données d'exemple pour test"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    
    # Simuler une consommation réaliste
    base_consumption = 180
    seasonal_variation = 60 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
    weekly_pattern = 30 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)
    random_noise = np.random.normal(0, 25, len(dates))
    
    consumption = base_consumption + seasonal_variation + weekly_pattern + random_noise
    consumption = np.maximum(consumption, 50)  # Minimum 50 kWh
    
    # Ajouter des pics réalistes
    peak_days = np.random.choice(len(dates), 20, replace=False)
    consumption[peak_days] *= np.random.uniform(1.8, 2.5, len(peak_days))
    
    sample_data = {
        'dates': dates.strftime('%Y-%m-%d').tolist(),
        'consumption': consumption.tolist()
    }
    
    return jsonify(sample_data)

# Stockage temporaire des résultats d'analyse PDF
pdf_analysis_results = {}

@app.route('/pdf-analysis')
def pdf_analysis():
    """Page d'analyse des factures PDF"""
    return render_template('pdf_analysis.html')

@app.route('/analyze-sample-pdf')
def analyze_sample_pdf():
    """Analyse la facture exemple"""
    # Utiliser la facture exemple fournie
    file_path = 'facture_test.pdf'
    
    if not os.path.exists(file_path):
        flash('Facture exemple non trouvée')
        return redirect(url_for('pdf_analysis'))
    
    # Analyser le PDF
    analyzer = PDFBillAnalyzer()
    result = analyzer.process_pdf_bill(file_path)
    
    # Générer un ID unique pour cette analyse
    pdf_id = str(uuid.uuid4())
    pdf_analysis_results[pdf_id] = {
        'result': result,
        'file_path': file_path
    }
    
    # Récupérer le texte de debug
    debug_text = analyzer.get_debug_text()
    
    return render_template('pdf_analysis.html', result=result, pdf_id=pdf_id, debug_text=debug_text)

@app.route('/export-pdf-data/<pdf_id>')
def export_pdf_data(pdf_id):
    """Exporte les données extraites de la facture au format CSV"""
    if pdf_id not in pdf_analysis_results:
        flash('Analyse non trouvée')
        return redirect(url_for('pdf_analysis'))
    
    result = pdf_analysis_results[pdf_id]['result']
    
    # Créer un DataFrame à partir des résultats
    analyzer = PDFBillAnalyzer()
    df = analyzer.create_dataframe_from_bill(result)
    
    if df is None:
        flash("Impossible de créer un fichier d'export - données insuffisantes")
        return redirect(url_for('pdf_analysis'))
    
    # Sauvegarder en CSV temporaire
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    df.to_csv(temp_file.name, index=False, sep=';')
    
    # Envoyer le fichier CSV
    return send_file(
        temp_file.name,
        mimetype='text/csv',
        as_attachment=True,
        download_name='donnees_facture.csv'
    )

@app.route('/analyze-pdf', methods=['GET', 'POST'])
def analyze_pdf():
    """Analyse une facture PDF uploadée avec options avancées"""
    if request.method == 'POST':
        # Vérifier si un fichier a été téléchargé
        if 'pdf_file' not in request.files:
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.pdf'):
            # Récupérer les options d'extraction
            extraction_mode = request.form.get('extraction_mode', 'standard')
            extract_tables = 'extract_tables' in request.form
            debug_mode = 'debug_mode' in request.form
            specific_provider = request.form.get('specific_provider', '')
            
            # Options d'analyse
            options = {
                "extraction_mode": extraction_mode,
                "extract_tables": extract_tables,
                "debug_mode": debug_mode
            }
            
            if specific_provider:
                options["specific_provider"] = specific_provider
            
            # Sauvegarder le fichier
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Analyser le PDF
            analyzer = PDFBillAnalyzer()
            result = analyzer.process_pdf_bill(file_path, options)
            
            # Récupérer le texte de debug si disponible
            debug_text = None
            if debug_mode:
                debug_text = analyzer.get_debug_text()
            
            # Générer un ID unique pour cette analyse
            import uuid
            pdf_id = str(uuid.uuid4())
            pdf_analysis_results[pdf_id] = {
                'result': result,
                'file_path': file_path,
                'options': options
            }
            
            return render_template('pdf_analysis.html', result=result, pdf_id=pdf_id, debug_text=debug_text)
    
    return render_template('pdf_analysis.html')

@app.route('/analyze-pdf-advanced/<pdf_id>/<mode>')
def analyze_pdf_advanced(pdf_id, mode):
    """Réanalyse un PDF déjà téléchargé avec un mode différent"""
    if pdf_id not in pdf_analysis_results:
        flash('Analyse non trouvée')
        return redirect(url_for('pdf_analysis'))
    
    # Récupérer le chemin du fichier de l'analyse précédente
    file_path = pdf_analysis_results[pdf_id]['file_path']
    
    if not os.path.exists(file_path):
        flash('Fichier PDF non trouvé')
        return redirect(url_for('pdf_analysis'))
    
    # Définir les nouvelles options d'extraction
    options = {
        "extraction_mode": mode,
        "extract_tables": True,
        "debug_mode": True
    }
    
    # Réanalyser le PDF avec les nouvelles options
    analyzer = PDFBillAnalyzer()
    result = analyzer.process_pdf_bill(file_path, options)
    
    # Récupérer le texte de debug
    debug_text = analyzer.get_debug_text()
    
    # Générer un nouvel ID pour cette analyse
    import uuid
    new_pdf_id = str(uuid.uuid4())
    pdf_analysis_results[new_pdf_id] = {
        'result': result,
        'file_path': file_path,
        'options': options
    }
    
    return render_template('pdf_analysis.html', result=result, pdf_id=new_pdf_id, debug_text=debug_text)

@app.route('/pdf-extraction-help')
def pdf_extraction_help():
    """Page d'aide pour les problèmes d'extraction PDF"""
    return render_template('pdf_extraction_help.html')

@app.route('/analyze-with-data/<pdf_id>')
def analyze_with_data(pdf_id):
    """Redirige vers l'analyse de données de la facture PDF ou saisie manuelle"""
    try:
        print(f"🔍 Traitement de l'analyse pour PDF ID: {pdf_id}")
        
        if pdf_id not in pdf_analysis_results:
            flash('Analyse non trouvée - veuillez réessayer')
            return redirect(url_for('pdf_analysis'))
        
        result = pdf_analysis_results[pdf_id]['result']
        is_manual = pdf_analysis_results[pdf_id].get('manual_entry', False)
        source_text = "saisies manuellement" if is_manual else "extraites du PDF"
        print(f"📋 Données {source_text} récupérées: {result}")
        
        # Créer un DataFrame à partir des résultats
        df = None
        if is_manual:
            # Pour les données saisies manuellement
            print("🖋️ Création du DataFrame à partir des données saisies manuellement")
            df = create_dataframe_from_manual_entry(result)
        else:
            # Pour les données extraites d'un PDF
            print("📄 Création du DataFrame à partir des données PDF")
            analyzer = PDFBillAnalyzer()
            df = analyzer.create_dataframe_from_bill(result)
        
        if df is None:
            print("❌ Échec de création du DataFrame - données insuffisantes")
            flash("Impossible de créer des données pour analyse - informations insuffisantes")
            return redirect(url_for('pdf_analysis'))
        
        print(f"✓ DataFrame initial créé: {df.shape}")
        
        # Vérification et ajout des colonnes obligatoires
        essential_columns = ['consumption', 'date', 'estimated_bill']
        
        # Assurer la présence de la colonne 'consumption'
        if 'consumption' not in df.columns:
            if 'consumption_kwh' in df.columns:
                print("➕ Ajout de colonne: consumption à partir de consumption_kwh")
                df['consumption'] = df['consumption_kwh']
            else:
                # Créer une colonne de consommation par défaut
                print("⚠️ Création d'une colonne de consommation par défaut")
                if is_manual and 'amount' in result:
                    # Estimer la consommation à partir du montant (approximation)
                    df['consumption'] = float(result.get('amount', 100)) * 5  # ~5 kWh par €
                else:
                    df['consumption'] = 100  # Valeur par défaut
        
        # Assurer la présence de la colonne 'date'
        if 'date' not in df.columns:
            if 'bill_date' in df.columns:
                print("➕ Ajout de colonne: date à partir de bill_date")
                df['date'] = pd.to_datetime(df['bill_date'], errors='coerce')
            elif 'period_start' in df.columns:
                print("➕ Ajout de colonne: date à partir de period_start")
                df['date'] = pd.to_datetime(df['period_start'], errors='coerce')
            else:
                # Créer une colonne de date par défaut
                print("⚠️ Création d'une colonne de date par défaut")
                df['date'] = datetime.now()
        
        # Assurer que la date est au format datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Assurer la présence de la colonne 'estimated_bill'
        if 'estimated_bill' not in df.columns:
            if 'amount' in df.columns:
                print("➕ Ajout de colonne: estimated_bill à partir de amount")
                df['estimated_bill'] = df['amount']
            else:
                # Créer une colonne de coût par défaut
                print("⚠️ Création d'une colonne de coût par défaut")
                if is_manual and 'consumption_kwh' in result:
                    # Estimer le coût à partir de la consommation (approximation)
                    df['estimated_bill'] = float(result.get('consumption_kwh', 100)) * 0.20  # ~0.20 € par kWh
                else:
                    df['estimated_bill'] = 50  # Valeur par défaut
        
        # Sauvegarder temporairement en CSV pour l'analyse
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        source_type = "manual" if is_manual else "pdf"
        csv_filename = f"facture_{source_type}_{timestamp}.csv"
        csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
        
        print(f"💾 Sauvegarde du DataFrame enrichi ({df.shape[0]} lignes, {df.shape[1]} colonnes)")
        print(f"📊 Aperçu avant sauvegarde:\n{df.head(3)}")
        
        # Vérifier qu'il n'y a pas de valeurs NaN dans les colonnes essentielles
        for col in essential_columns:
            if col in df.columns and df[col].isna().any():
                print(f"⚠️ Remplacement des valeurs NaN dans la colonne {col}")
                if col == 'date':
                    df[col] = df[col].fillna(datetime.now())
                elif col == 'consumption':
                    df[col] = df[col].fillna(100)
                elif col == 'estimated_bill':
                    df[col] = df[col].fillna(50)
        
        df.to_csv(csv_filepath, index=False)
        
        # Message de confirmation et redirection
        flash(f'Données {source_text} prêtes pour analyse avancée')
        print(f"✅ Redirection vers le dashboard avec le fichier: {csv_filename}")
        
        return redirect(url_for('dashboard_advanced', filename=csv_filename))
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse des données: {str(e)}")
        traceback.print_exc()
        flash(f'Erreur lors de l\'analyse des données: {str(e)}')
        return redirect(url_for('pdf_analysis'))

@app.route('/compare-pdf-data/<pdf_id>')
def compare_pdf_data(pdf_id):
    """Redirige vers la page de comparaison avec les données de la facture"""
    if pdf_id not in pdf_analysis_results:
        flash('Analyse non trouvée')
        return redirect(url_for('pdf_analysis'))
    
    # Dans une application complète, cette fonction permettrait de comparer
    # les données de cette facture avec d'autres données historiques
    flash('Fonctionnalité de comparaison à venir dans une prochaine mise à jour')
    return redirect(url_for('pdf_analysis'))

@app.route('/manual_bill_entry', methods=['GET', 'POST'])
def manual_bill_entry():
    """Page pour saisir manuellement les données d'une facture"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        bill_data = {
            "provider": request.form.get('provider', 'Non spécifié'),
            "bill_date": request.form.get('bill_date'),
            "consumption_kwh": float(request.form.get('consumption_kwh', 0)) if request.form.get('consumption_kwh') else 0,
            "amount": float(request.form.get('amount', 0)) if request.form.get('amount') else 0,
            "period_start": request.form.get('period_start'),
            "period_end": request.form.get('period_end'),
            "client_ref": request.form.get('client_ref', ''),
            "meter_number": request.form.get('meter_number', '')
        }
        
        # Générer un ID unique pour cette analyse manuelle
        pdf_id = str(uuid.uuid4())
        pdf_analysis_results[pdf_id] = {
            'result': bill_data,
            'manual_entry': True,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        flash('Données de facture enregistrées avec succès')
        # Rediriger directement vers l'analyse des données
        return redirect(url_for('analyze_with_data', pdf_id=pdf_id))
    
    # Afficher le formulaire
    return render_template('manual_bill_entry.html')

def analyze_consumption_patterns(df):
    """Analyser les patterns de consommation pour l'analyse avancée des données manuelles"""
    # Déterminer la colonne de consommation à utiliser
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    consumption = df[consumption_col]
    
    # Initialiser les résultats d'analyse
    analysis = {
        'total': float(consumption.sum()),
        'average': float(consumption.mean()),
        'median': float(consumption.median()),
        'std': float(consumption.std()),
        'max': float(consumption.max()),
        'min': float(consumption.min()),
        'quartiles': {
            'q25': float(consumption.quantile(0.25)),
            'q75': float(consumption.quantile(0.75))
        },
        'coefficient_variation': float(consumption.std() / consumption.mean()) if consumption.mean() > 0 else 0,
        'trend': 'stable',
        'volatility': 'low'
    }
    
    # Analyser la tendance si des dates sont disponibles
    if 'date' in df.columns:
        df_sorted = df.sort_values('date').copy()
        x = np.arange(len(df_sorted))
        y = df_sorted[consumption_col].values
        
        if len(x) > 1:
            try:
                # Calculer la tendance linéaire
                from scipy import stats
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                # Interpréter la pente
                if slope > 0.05 * analysis['average']:
                    analysis['trend'] = 'increasing'
                elif slope < -0.05 * analysis['average']:
                    analysis['trend'] = 'decreasing'
                else:
                    analysis['trend'] = 'stable'
                
                # Stocker les données de régression
                analysis['regression'] = {
                    'slope': float(slope),
                    'intercept': float(intercept),
                    'r_squared': float(r_value**2),
                    'p_value': float(p_value)
                }
            except:
                pass
    
    # Déterminer la volatilité
    if analysis['coefficient_variation'] < 0.1:
        analysis['volatility'] = 'very_low'
    elif analysis['coefficient_variation'] < 0.2:
        analysis['volatility'] = 'low'
    elif analysis['coefficient_variation'] < 0.4:
        analysis['volatility'] = 'medium'
    else:
        analysis['volatility'] = 'high'
    
    # Détecter les pics de consommation
    threshold = analysis['average'] + 1.5 * analysis['std']
    peaks = df[df[consumption_col] > threshold]
    
    analysis['peaks'] = {
        'count': len(peaks),
        'percentage': len(peaks) / len(df) * 100,
        'average_magnitude': float(peaks[consumption_col].mean()) if len(peaks) > 0 else 0,
        'max_peak': float(peaks[consumption_col].max()) if len(peaks) > 0 else 0
    }
    
    # Calculer le surcoût potentiel dû aux pics
    if 'estimated_bill' in df.columns:
        avg_cost_per_kwh = df['estimated_bill'].sum() / consumption.sum() if consumption.sum() > 0 else 0.20
        peak_excess = peaks[consumption_col].sum() - (analysis['average'] * len(peaks))
        analysis['peaks']['estimated_cost_impact'] = float(peak_excess * avg_cost_per_kwh * 1.5)  # Majoration de 50% pour l'impact des pics
    
    # Ajouter des recommandations basiques
    analysis['recommendations'] = []
    
    if analysis['volatility'] in ['high', 'medium']:
        analysis['recommendations'].append({
            'type': 'volatility',
            'message': 'Réduisez la variabilité de votre consommation pour optimiser vos coûts',
            'priority': 'high' if analysis['volatility'] == 'high' else 'medium',
            'potential_impact': 'significant'
        })
    
    if analysis['peaks']['percentage'] > 10:
        analysis['recommendations'].append({
            'type': 'peaks',
            'message': 'Attention aux pics de consommation fréquents qui peuvent impacter votre facture',
            'priority': 'high',
            'potential_impact': 'high'
        })
    
    if analysis['trend'] == 'increasing':
        analysis['recommendations'].append({
            'type': 'trend',
            'message': 'Votre consommation est en augmentation, analysez les causes de cette hausse',
            'priority': 'medium',
            'potential_impact': 'growing'
        })
    
    return analysis

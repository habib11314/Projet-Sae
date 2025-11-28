#!/usr/bin/env python3
"""
EnergyInsight BUSINESS - Outil de pilotage énergétique stratégique
Version avancée pour analyses économiques détaillées
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import tempfile
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

app = Flask(__name__)
app.config['SECRET_KEY'] = 'energyinsight-business-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extensions autorisées
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}

def allowed_file(filename):
    """Vérifier si le fichier est autorisé"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_data_format(df):
    """Détecter automatiquement le format des données"""
    columns = df.columns.str.lower()
    
    # Format entreprise avancé (HP/HC, zones, factures)
    if any('hp' in col for col in columns) and any('hc' in col for col in columns):
        return 'enterprise_advanced'
    
    # Format standard (date, consumption)
    elif any('consumption' in col or 'consommation' in col for col in columns):
        return 'standard'
    
    # Format minimal avec colonnes numériques
    elif len(df.select_dtypes(include=[np.number]).columns) >= 1:
        return 'basic_numeric'
    
    return 'unknown'

def standardize_columns(df, data_format):
    """Standardiser les noms de colonnes selon le format détecté"""
    df_std = df.copy()
    
    if data_format == 'enterprise_advanced':
        # Mapping pour format entreprise
        column_mapping = {
            'date de relevé': 'date',
            'date_releve': 'date',
            'consommation hp (kwh)': 'hp_consumption',
            'consommation hc (kwh)': 'hc_consumption', 
            'consommation totale (kwh)': 'total_consumption',
            'zone': 'zone',
            'facture estimée (€)': 'estimated_bill',
            'facture_estimee': 'estimated_bill'
        }
        
        # Renommer les colonnes
        for old_name, new_name in column_mapping.items():
            for col in df_std.columns:
                if old_name.lower() in col.lower():
                    df_std = df_std.rename(columns={col: new_name})
        
        # Si pas de consommation totale, la calculer
        if 'total_consumption' not in df_std.columns:
            if 'hp_consumption' in df_std.columns and 'hc_consumption' in df_std.columns:
                df_std['total_consumption'] = df_std['hp_consumption'] + df_std['hc_consumption']
        
        # Ajouter consumption pour compatibilité
        if 'total_consumption' in df_std.columns:
            df_std['consumption'] = df_std['total_consumption']
    
    elif data_format == 'standard':
        # Format standard
        for col in df_std.columns:
            if 'consommation' in col.lower() or 'consumption' in col.lower():
                df_std['consumption'] = df_std[col]
            elif 'date' in col.lower():
                df_std['date'] = df_std[col]
    
    return df_std

def analyze_business_data(df):
    """Analyse stratégique complète pour entreprises"""
    
    # Détecter le format et standardiser
    data_format = detect_data_format(df)
    df = standardize_columns(df, data_format)
    
    # Convertir les dates
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Nettoyer les données numériques
    numeric_columns = ['consumption', 'total_consumption', 'hp_consumption', 'hc_consumption', 'estimated_bill']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Supprimer les lignes avec des données manquantes critiques
    df = df.dropna(subset=['consumption'] if 'consumption' in df.columns else ['total_consumption'])
    
    if len(df) == 0:
        return {'error': 'Aucune donnée valide trouvée'}
    
    # Initialiser l'analyse
    analysis = {
        'data_format': data_format,
        'file_info': analyze_file_info(df),
        'consumption_analysis': analyze_consumption_patterns(df),
        'economic_analysis': analyze_economic_impact(df),
        'zone_analysis': analyze_zones(df) if 'zone' in df.columns else None,
        'hp_hc_analysis': analyze_hp_hc_patterns(df) if data_format == 'enterprise_advanced' else None,
        'peak_analysis': analyze_peak_consumption(df),
        'seasonal_analysis': analyze_seasonal_patterns(df),
        'efficiency_score': calculate_business_efficiency_score(df),
        'strategic_recommendations': generate_strategic_recommendations(df),
        'economic_projections': calculate_economic_projections(df),
        'action_plan': generate_action_plan(df)
    }
    
    return analysis

def analyze_file_info(df):
    """Analyser les informations du fichier"""
    info = {
        'total_records': len(df),
        'date_range': None,
        'data_quality': 'excellent',
        'completeness': 100.0,
        'columns_detected': list(df.columns),
        'period_covered': None,
        'frequency': 'unknown'
    }
    
    if 'date' in df.columns:
        date_series = pd.to_datetime(df['date'], errors='coerce')
        valid_dates = date_series.dropna()
        
        if len(valid_dates) > 0:
            info['date_range'] = {
                'start': valid_dates.min().strftime('%d/%m/%Y'),
                'end': valid_dates.max().strftime('%d/%m/%Y'),
                'days_covered': (valid_dates.max() - valid_dates.min()).days
            }
            
            # Déterminer la fréquence
            if len(valid_dates) > 1:
                diff_days = np.diff(valid_dates.dt.dayofyear).mean()
                if diff_days <= 1:
                    info['frequency'] = 'daily'
                elif diff_days <= 7:
                    info['frequency'] = 'weekly'
                elif diff_days <= 31:
                    info['frequency'] = 'monthly'
    
    # Calculer la qualité des données
    missing_data = df.isnull().sum().sum()
    total_cells = df.shape[0] * df.shape[1]
    info['completeness'] = ((total_cells - missing_data) / total_cells) * 100
    
    if info['completeness'] >= 95:
        info['data_quality'] = 'excellent'
    elif info['completeness'] >= 80:
        info['data_quality'] = 'good'
    elif info['completeness'] >= 60:
        info['data_quality'] = 'fair'
    else:
        info['data_quality'] = 'poor'
    
    # Calculer la période couverte
    if info['date_range']:
        info['period_covered'] = f"{info['date_range']['days_covered']} jours"
    
    return info

def analyze_consumption_patterns(df):
    """Analyser les patterns de consommation"""
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    consumption = df[consumption_col]
    
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
    
    # Analyser la tendance
    if 'date' in df.columns:
        df_sorted = df.sort_values('date').copy()
        x = np.arange(len(df_sorted))
        y = df_sorted[consumption_col].values
        
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            if slope > consumption.mean() * 0.01:  # Augmentation > 1% par période
                analysis['trend'] = 'increasing'
            elif slope < -consumption.mean() * 0.01:  # Diminution > 1% par période
                analysis['trend'] = 'decreasing'
    
    # Analyser la volatilité
    cv = analysis['coefficient_variation']
    if cv > 0.3:
        analysis['volatility'] = 'high'
    elif cv > 0.15:
        analysis['volatility'] = 'medium'
    
    return analysis

def analyze_economic_impact(df):
    """Analyser l'impact économique"""
    economic = {
        'total_cost': 0,
        'annual_cost_estimate': 0,
        'average_cost_per_kwh': 0.18,  # Prix moyen électricité entreprise
        'daily_average_cost': 0,
        'monthly_average': 0,
        'cost_breakdown': {},
        'savings_potential': {}
    }
    
    # Calculer les coûts
    if 'estimated_bill' in df.columns:
        bills = pd.to_numeric(df['estimated_bill'], errors='coerce').dropna()
        if len(bills) > 0:
            economic['total_cost'] = float(bills.sum())
            economic['annual_cost_estimate'] = float(bills.sum() * (365 / len(df)))
            economic['monthly_average'] = float(bills.mean() * 4.33)  # 4.33 semaines par mois
            economic['daily_average_cost'] = float(bills.mean())
            
            consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
            total_kwh = df[consumption_col].sum()
            if total_kwh > 0:
                economic['average_cost_per_kwh'] = float(bills.sum() / total_kwh)
    else:
        # Estimation basée sur la consommation
        consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
        total_kwh = df[consumption_col].sum()
        economic['total_cost'] = float(total_kwh * economic['average_cost_per_kwh'])
        economic['annual_cost_estimate'] = float(total_kwh * economic['average_cost_per_kwh'] * (365 / len(df)))
        economic['monthly_average'] = economic['annual_cost_estimate'] / 12
        economic['daily_average_cost'] = economic['annual_cost_estimate'] / 365
    
    # Calculer le potentiel d'économies
    economic['savings_potential'] = {
        'optimisation_horaires': {
            'description': 'Optimisation des horaires HP/HC',
            'savings_percent': 15,
            'annual_savings': economic['annual_cost_estimate'] * 0.15
        },
        'gestion_zones': {
            'description': 'Meilleure gestion par zones',
            'savings_percent': 10,
            'annual_savings': economic['annual_cost_estimate'] * 0.10
        },
        'detection_gaspillages': {
            'description': 'Détection et élimination des gaspillages',
            'savings_percent': 20,
            'annual_savings': economic['annual_cost_estimate'] * 0.20
        },
        'total_potential': economic['annual_cost_estimate'] * 0.35
    }
    
    return economic

def analyze_zones(df):
    """Analyser la consommation par zones"""
    if 'zone' not in df.columns:
        return None
    
    zone_analysis = {
        'zones': {},
        'recommendations': []
    }
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    
    for zone in df['zone'].unique():
        zone_data = df[df['zone'] == zone]
        zone_consumption = zone_data[consumption_col]
        
        zone_analysis['zones'][zone] = {
            'total_consumption': float(zone_consumption.sum()),
            'average_consumption': float(zone_consumption.mean()),
            'percentage': float((zone_consumption.sum() / df[consumption_col].sum()) * 100),
            'records_count': len(zone_data),
            'total_cost': float(zone_consumption.sum() * 0.18),  # Prix moyen
            'efficiency_rating': 'normal'
        }
        
        # Évaluer l'efficacité de la zone
        avg_all = df[consumption_col].mean()
        zone_avg = zone_consumption.mean()
        
        if zone_avg > avg_all * 1.2:
            zone_analysis['zones'][zone]['efficiency_rating'] = 'inefficient'
        elif zone_avg < avg_all * 0.8:
            zone_analysis['zones'][zone]['efficiency_rating'] = 'efficient'
    
    # Identifier les zones problématiques
    for zone, data in zone_analysis['zones'].items():
        if data['efficiency_rating'] == 'inefficient':
            zone_analysis['recommendations'].append({
                'zone': zone,
                'issue': 'Consommation élevée détectée',
                'action': f'Audit énergétique recommandé pour la zone {zone}',
                'potential_savings': data['total_cost'] * 0.25
            })
    
    return zone_analysis

def analyze_hp_hc_patterns(df):
    """Analyser les patterns HP (Heures Pleines) / HC (Heures Creuses)"""
    if 'hp_consumption' not in df.columns or 'hc_consumption' not in df.columns:
        return None
    
    hp_total = df['hp_consumption'].sum()
    hc_total = df['hc_consumption'].sum()
    total_consumption = hp_total + hc_total
    
    analysis = {
        'total_hp': float(hp_total),
        'total_hc': float(hc_total),
        'hp_percentage': float((hp_total / total_consumption) * 100),
        'hc_percentage': float((hc_total / total_consumption) * 100),
        'hp_average': float(df['hp_consumption'].mean()),
        'hc_average': float(df['hc_consumption'].mean()),
        'ratio_hp_hc': float(hp_total / hc_total) if hc_total > 0 else float('inf'),
        'optimization_potential': 0,
        'optimization_recommendation': '',
        'recommendations': []
    }
    
    # Analyser le potentiel d'optimisation
    optimal_hp_percentage = 60  # Idéalement 60% HP, 40% HC pour une entreprise
    actual_hp_percentage = analysis['hp_percentage']
    
    if actual_hp_percentage > 70:
        potential_savings = (hp_total * 0.22 - hc_total * 0.12) * 0.12  # Différence tarifaire
        analysis['optimization_potential'] = float(potential_savings)
        analysis['optimization_recommendation'] = 'Trop de consommation en heures pleines - Déplacer des usages vers les heures creuses'
        analysis['recommendations'].append({
            'priority': 'high',
            'action': 'Déplacer des usages vers les heures creuses',
            'details': 'Programmation des équipements non critiques (chauffage, eau chaude) pendant les HC',
            'expected_savings': potential_savings
        })
    
    elif actual_hp_percentage < 50:
        potential_savings = total_consumption * 0.18 * 0.03
        analysis['optimization_potential'] = float(potential_savings)
        analysis['optimization_recommendation'] = 'Bonne utilisation des heures creuses - Optimisations mineures possibles'
    
    return analysis

def analyze_peak_consumption(df):
    """Analyser les pics de consommation avec détection d'anomalies"""
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    consumption = df[consumption_col]
    
    # Détecter les pics (consommation > moyenne + 1.5 * écart-type)
    mean_consumption = consumption.mean()
    std_consumption = consumption.std()
    threshold = mean_consumption + 1.5 * std_consumption
    
    peaks = df[consumption > threshold].copy()
    
    peak_analysis = {
        'peaks_count': len(peaks),
        'peak_threshold': float(threshold),
        'average_peak_value': float(peaks[consumption_col].mean()) if len(peaks) > 0 else 0,
        'peak_percentage': float((len(peaks) / len(df)) * 100),
        'max_peak': {
            'date': 'N/A',
            'value': 0,
            'context': 'Aucun pic détecté'
        },
        'anomalies': [],
        'economic_impact': 0,
        'recommendations': []
    }
    
    # Analyser chaque pic
    if len(peaks) > 0:
        max_peak_idx = peaks[consumption_col].idxmax()
        max_peak_row = peaks.loc[max_peak_idx]
        peak_analysis['max_peak'] = {
            'date': max_peak_row['date'].strftime('%d/%m/%Y') if 'date' in max_peak_row and pd.notna(max_peak_row['date']) else 'N/A',
            'value': float(max_peak_row[consumption_col]),
            'context': f'Pic maximum: {float(max_peak_row[consumption_col]):.0f} kWh'
        }
    
    for idx, peak in peaks.iterrows():
        anomaly = {
            'date': peak['date'].strftime('%d/%m/%Y') if 'date' in peak and pd.notna(peak['date']) else 'Unknown',
            'consumption': float(peak[consumption_col]),
            'excess_consumption': float(peak[consumption_col] - mean_consumption),
            'excess_cost': float((peak[consumption_col] - mean_consumption) * 0.18),
            'severity': 'medium'
        }
        
        # Classer la sévérité
        if peak[consumption_col] > mean_consumption * 2:
            anomaly['severity'] = 'critical'
        elif peak[consumption_col] > mean_consumption * 1.5:
            anomaly['severity'] = 'high'
        
        # Ajouter informations de zone si disponible
        if 'zone' in peak:
            anomaly['zone'] = peak['zone']
        
        peak_analysis['anomalies'].append(anomaly)
    
    # Calculer l'impact financier
    peak_analysis['economic_impact'] = sum(anomaly['excess_cost'] for anomaly in peak_analysis['anomalies'])
    
    # Générer des recommandations
    if peak_analysis['peaks_count'] > len(df) * 0.1:  # Plus de 10% de pics
        peak_analysis['recommendations'].append({
            'priority': 'high',
            'title': 'Pics de consommation fréquents',
            'action': 'Installation de systèmes de monitoring en temps réel',
            'expected_savings': peak_analysis['economic_impact'] * 0.7
        })
    
    return peak_analysis

def analyze_seasonal_patterns(df):
    """Analyser les patterns saisonniers"""
    if 'date' not in df.columns:
        return None
    
    df_with_date = df.copy()
    df_with_date['date'] = pd.to_datetime(df_with_date['date'], errors='coerce')
    df_with_date = df_with_date.dropna(subset=['date'])
    
    if len(df_with_date) == 0:
        return None
    
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    
    # Ajouter des colonnes temporelles
    df_with_date['month'] = df_with_date['date'].dt.month
    df_with_date['season'] = df_with_date['month'].map({
        12: 'Hiver', 1: 'Hiver', 2: 'Hiver',
        3: 'Printemps', 4: 'Printemps', 5: 'Printemps',
        6: 'Été', 7: 'Été', 8: 'Été',
        9: 'Automne', 10: 'Automne', 11: 'Automne'
    })
    df_with_date['weekday'] = df_with_date['date'].dt.dayofweek
    df_with_date['is_weekend'] = df_with_date['weekday'].isin([5, 6])
    
    seasonal_analysis = {
        'monthly_averages': {},
        'seasonal_averages': {},
        'weekend_vs_weekday': {},
        'patterns': [],
        'recommendations': []
    }
    
    # Analyse mensuelle
    monthly_avg = df_with_date.groupby('month')[consumption_col].mean()
    for month, avg in monthly_avg.items():
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                      'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        seasonal_analysis['monthly_averages'][month_names[month-1]] = float(avg)
    
    # Analyse saisonnière
    seasonal_avg = df_with_date.groupby('season')[consumption_col].mean()
    for season, avg in seasonal_avg.items():
        seasonal_analysis['seasonal_averages'][season] = float(avg)
    
    # Analyse weekend vs semaine
    weekend_avg = df_with_date[df_with_date['is_weekend']][consumption_col].mean()
    weekday_avg = df_with_date[~df_with_date['is_weekend']][consumption_col].mean()
    
    seasonal_analysis['weekend_vs_weekday'] = {
        'weekend_average': float(weekend_avg) if not pd.isna(weekend_avg) else 0,
        'weekday_average': float(weekday_avg) if not pd.isna(weekday_avg) else 0,
        'weekend_savings_potential': max(0, float(weekend_avg - weekday_avg * 0.3)) if not pd.isna(weekend_avg) and not pd.isna(weekday_avg) else 0
    }
    
    # Identifier les patterns
    if seasonal_analysis['weekend_vs_weekday']['weekend_average'] > seasonal_analysis['weekend_vs_weekday']['weekday_average'] * 0.8:
        seasonal_analysis['patterns'].append({
            'pattern': 'high_weekend_consumption',
            'message': 'Consommation élevée le weekend (équipements non arrêtés)',
            'savings_potential': seasonal_analysis['weekend_vs_weekday']['weekend_savings_potential'] * 52  # 52 weekends
        })
    
    return seasonal_analysis

def calculate_business_efficiency_score(df):
    """Calculer un score d'efficacité business (0-100)"""
    score = 100
    penalties = []
    
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    consumption = df[consumption_col]
    
    # Pénalité pour variabilité élevée
    cv = consumption.std() / consumption.mean() if consumption.mean() > 0 else 0
    if cv > 0.4:
        penalty = min(25, cv * 50)
        score -= penalty
        penalties.append(f"Variabilité élevée (-{penalty:.1f})")
    
    # Pénalité pour pics fréquents
    threshold = consumption.mean() + 1.5 * consumption.std()
    peak_ratio = len(consumption[consumption > threshold]) / len(consumption)
    if peak_ratio > 0.1:
        penalty = min(20, peak_ratio * 100)
        score -= penalty
        penalties.append(f"Pics fréquents (-{penalty:.1f})")
    
    # Bonus pour optimisation HP/HC
    if 'hp_consumption' in df.columns and 'hc_consumption' in df.columns:
        hp_total = df['hp_consumption'].sum()
        hc_total = df['hc_consumption'].sum()
        hp_percentage = hp_total / (hp_total + hc_total) * 100
        
        if 55 <= hp_percentage <= 65:  # Ratio optimal
            score += 5
            penalties.append("Bon ratio HP/HC (+5)")
        elif hp_percentage > 75:
            penalty = min(15, (hp_percentage - 75) / 2)
            score -= penalty
            penalties.append(f"Trop de HP (-{penalty:.1f})")
    
    # Bonus pour régularité saisonnière
    if 'date' in df.columns:
        df_temp = df.copy()
        df_temp['date'] = pd.to_datetime(df_temp['date'], errors='coerce')
        if len(df_temp.dropna(subset=['date'])) > 0:
            df_temp['month'] = df_temp['date'].dt.month
            monthly_std = df_temp.groupby('month')[consumption_col].mean().std()
            overall_mean = consumption.mean()
            if monthly_std / overall_mean < 0.2:  # Variation saisonnière < 20%
                score += 5
                penalties.append("Consommation régulière (+5)")
    
    return {
        'score': int(max(0, min(100, score))),
        'category': 'Excellent' if score >= 85 else 'Bon' if score >= 70 else 'Moyen' if score >= 55 else 'Faible',
        'grade': 'A' if score >= 85 else 'B' if score >= 70 else 'C' if score >= 55 else 'D',
        'penalties': penalties
    }

def generate_strategic_recommendations(df):
    """Générer des recommandations stratégiques business"""
    recommendations = {
        'optimisation_tarifaire': [],
        'gestion_des_pics': [],
        'optimisation_zones': [],
        'sensibilisation': []
    }
    
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    consumption = df[consumption_col]
    
    # Analyser les coûts totaux
    if 'estimated_bill' in df.columns:
        annual_cost = df['estimated_bill'].sum() * (365 / len(df))
    else:
        annual_cost = consumption.sum() * 0.18 * (365 / len(df))
    
    # Recommandation 1: Optimisation HP/HC
    if 'hp_consumption' in df.columns and 'hc_consumption' in df.columns:
        hp_total = df['hp_consumption'].sum()
        total = consumption.sum()
        hp_percentage = (hp_total / total) * 100
        
        if hp_percentage > 70:
            recommendations['optimisation_tarifaire'].append(
                f'Déplacer {hp_percentage-60:.1f}% de la consommation vers les heures creuses'
            )
            recommendations['optimisation_tarifaire'].append(
                'Installer des programmateurs sur les équipements non critiques'
            )
    
    # Recommandation 2: Gestion des pics
    threshold = consumption.mean() + 1.5 * consumption.std()
    peaks = df[consumption > threshold]
    
    if len(peaks) > len(df) * 0.1:
        recommendations['gestion_des_pics'].append(
            f'Installer un système de monitoring - {len(peaks)} pics détectés'
        )
        recommendations['gestion_des_pics'].append(
            'Mettre en place un délestage automatique'
        )
    
    # Recommandation 3: Analyse par zones
    if 'zone' in df.columns:
        zone_consumption = df.groupby('zone')[consumption_col].sum()
        highest_zone = zone_consumption.idxmax()
        zone_percentage = (zone_consumption.max() / consumption.sum()) * 100
        
        if zone_percentage > 40:
            recommendations['optimisation_zones'].append(
                f'Audit énergétique prioritaire - Zone {highest_zone} ({zone_percentage:.1f}%)'
            )
            recommendations['optimisation_zones'].append(
                'Vérifier l\'isolation et les équipements de cette zone'
            )
    
    # Recommandation 4: Sensibilisation
    recommendations['sensibilisation'].append(
        'Former le personnel aux éco-gestes'
    )
    recommendations['sensibilisation'].append(
        'Afficher les consommations en temps réel'
    )
    
    return recommendations

def calculate_economic_projections(df):
    """Calculer les projections économiques"""
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    
    # Coût actuel
    if 'estimated_bill' in df.columns:
        current_annual_cost = df['estimated_bill'].sum() * (365 / len(df))
        cost_per_kwh = df['estimated_bill'].sum() / df[consumption_col].sum()
    else:
        current_annual_cost = df[consumption_col].sum() * 0.18 * (365 / len(df))
        cost_per_kwh = 0.18
    
    # Projections
    projections = {
        'annual_projection': current_annual_cost,
        'annual_savings_potential': current_annual_cost * 0.25,
        'roi_months': 12.0,
        'potential_reduction_percentage': 25.0,
        'projections_5_years': [],
        'savings_scenarios': {}
    }
    
    return projections

def generate_action_plan(df):
    """Générer un plan d'action chronologique"""
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    
    # Analyser les coûts pour calculer les économies
    if 'estimated_bill' in df.columns:
        annual_cost = df['estimated_bill'].sum() * (365 / len(df))
    else:
        annual_cost = df[consumption_col].sum() * 0.18 * (365 / len(df))
    
    action_plan = [
        {
            'priority': 1,
            'title': 'Audit énergétique rapide',
            'description': 'Identifier les gaspillages évidents et les équipements défaillants',
            'estimated_savings': annual_cost * 0.05,
            'implementation_time': '1 mois',
            'difficulty': 'Facile'
        },
        {
            'priority': 2,
            'title': 'Optimisation HP/HC',
            'description': 'Reprogrammation des équipements pour maximiser l\'usage des heures creuses',
            'estimated_savings': annual_cost * 0.12,
            'implementation_time': '2-3 mois',
            'difficulty': 'Moyen'
        },
        {
            'priority': 3,
            'title': 'Monitoring temps réel',
            'description': 'Installation d\'un système de surveillance et d\'alertes',
            'estimated_savings': annual_cost * 0.15,
            'implementation_time': '6 mois',
            'difficulty': 'Moyen'
        },
        {
            'priority': 4,
            'title': 'Sensibilisation du personnel',
            'description': 'Formation aux éco-gestes et affichage des consommations',
            'estimated_savings': annual_cost * 0.08,
            'implementation_time': '1 mois',
            'difficulty': 'Facile'
        }
    ]
    
    # Ajouter des actions spécifiques selon les données
    if 'zone' in df.columns:
        zone_consumption = df.groupby('zone')[consumption_col].sum()
        highest_zone = zone_consumption.idxmax()
        action_plan.append({
            'priority': 5,
            'title': f'Audit approfondi - Zone {highest_zone}',
            'description': f'Analyse détaillée de la zone la plus consommatrice',
            'estimated_savings': annual_cost * 0.18,
            'implementation_time': '12 mois',
            'difficulty': 'Difficile'
        })
    
    return action_plan

def create_business_charts(df, analysis):
    """Créer des graphiques avancés pour l'analyse business"""
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    
    charts = {
        'consumption_chart': create_consumption_chart(df, analysis),
        'hp_hc_chart': create_hp_hc_chart(df, analysis) if 'hp_consumption' in df.columns else None,
        'monthly_chart': create_monthly_chart(df, analysis),
        'peaks_chart': create_peaks_chart(df, analysis),
        'economic_chart': create_economic_chart(df, analysis)
    }
    
    return charts

def create_consumption_chart(df, analysis):
    """Créer le graphique principal de consommation"""
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    
    fig = go.Figure()
    
    if 'date' in df.columns:
        df_sorted = df.sort_values('date')
        
        # Ligne de consommation principale
        fig.add_trace(go.Scatter(
            x=df_sorted['date'],
            y=df_sorted[consumption_col],
            mode='lines+markers',
            name='Consommation totale',
            line=dict(color='#2E7D32', width=3),
            hovertemplate='<b>%{x}</b><br>Consommation: %{y:.1f} kWh<extra></extra>'
        ))
        
        # Ligne de moyenne
        mean_consumption = df_sorted[consumption_col].mean()
        fig.add_hline(
            y=mean_consumption,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Moyenne: {mean_consumption:.1f} kWh"
        )
        
        # Seuil d'alerte pour les pics
        if 'peak_analysis' in analysis:
            threshold = analysis['peak_analysis']['peak_threshold']
            fig.add_hline(
                y=threshold,
                line_dash="dot",
                line_color="red",
                annotation_text=f"Seuil d'alerte: {threshold:.1f} kWh"
            )
    
    fig.update_layout(
        title='Évolution de la Consommation',
        xaxis_title='Date',
        yaxis_title='Consommation (kWh)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_hp_hc_chart(df, analysis):
    """Créer le graphique HP/HC"""
    if 'hp_consumption' not in df.columns:
        return None
    
    hp_total = df['hp_consumption'].sum()
    hc_total = df['hc_consumption'].sum()
    
    fig = go.Figure(data=[
        go.Pie(labels=['Heures Pleines', 'Heures Creuses'], 
               values=[hp_total, hc_total],
               hole=0.3,
               marker_colors=['#FF6B6B', '#4ECDC4'])
    ])
    
    fig.update_layout(
        title='Répartition HP/HC',
        template='plotly_white',
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_monthly_chart(df, analysis):
    """Créer le graphique mensuel"""
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    
    if 'date' in df.columns:
        df_temp = df.copy()
        df_temp['date'] = pd.to_datetime(df_temp['date'])
        df_temp['month'] = df_temp['date'].dt.strftime('%Y-%m')
        monthly_data = df_temp.groupby('month')[consumption_col].sum()
        
        fig = go.Figure(data=[
            go.Bar(x=monthly_data.index, y=monthly_data.values, 
                   marker_color='#1976D2')
        ])
        
        fig.update_layout(
            title='Consommation Mensuelle',
            xaxis_title='Mois',
            yaxis_title='Consommation (kWh)',
            template='plotly_white',
            height=400
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return None

def create_peaks_chart(df, analysis):
    """Créer le graphique des pics"""
    consumption_col = 'consumption' if 'consumption' in df.columns else 'total_consumption'
    
    fig = go.Figure()
    
    if 'date' in df.columns:
        df_sorted = df.sort_values('date')
        
        # Ligne de consommation
        fig.add_trace(go.Scatter(
            x=df_sorted['date'],
            y=df_sorted[consumption_col],
            mode='lines',
            name='Consommation',
            line=dict(color='#2E7D32', width=2)
        ))
        
        # Marquer les pics
        if 'peak_analysis' in analysis and analysis['peak_analysis']['anomalies']:
            peak_dates = []
            peak_values = []
            for anomaly in analysis['peak_analysis']['anomalies']:
                if anomaly['date'] != 'Unknown':
                    try:
                        peak_date = pd.to_datetime(anomaly['date'], format='%d/%m/%Y')
                        peak_dates.append(peak_date)
                        peak_values.append(anomaly['consumption'])
                    except:
                        continue
            
            if peak_dates:
                fig.add_trace(go.Scatter(
                    x=peak_dates,
                    y=peak_values,
                    mode='markers',
                    name='Pics détectés',
                    marker=dict(color='red', size=10, symbol='triangle-up')
                ))
    
    fig.update_layout(
        title='Détection des Pics',
        xaxis_title='Date',
        yaxis_title='Consommation (kWh)',
        template='plotly_white',
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_economic_chart(df, analysis):
    """Créer le graphique économique"""
    projections = analysis.get('economic_projections', {})
    
    months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
              'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    
    # Estimation mensuelle basée sur la projection annuelle
    monthly_cost = [projections.get('annual_projection', 0) / 12] * 12
    monthly_savings = [projections.get('annual_savings_potential', 0) / 12] * 12
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=months,
        y=monthly_cost,
        name='Coût actuel',
        marker_color='#FF6B6B'
    ))
    
    fig.add_trace(go.Bar(
        x=months,
        y=monthly_savings,
        name='Économies potentielles',
        marker_color='#4ECDC4'
    ))
    
    fig.update_layout(
        title='Projection Économique Mensuelle',
        xaxis_title='Mois',
        yaxis_title='Coût (€)',
        template='plotly_white',
        height=400,
        barmode='group'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def generate_business_pdf(analysis, filename):
    """Générer un rapport PDF business complet"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'BusinessTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2E86AB'),
        alignment=TA_CENTER
    )
    
    story = []
    
    # Titre
    story.append(Paragraph("EnergyInsight BUSINESS", title_style))
    story.append(Paragraph("Rapport d'Analyse Stratégique Énergétique", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    # Résumé exécutif
    story.append(Paragraph("RÉSUMÉ EXÉCUTIF", styles['Heading2']))
    
    economic = analysis.get('economic_analysis', {})
    efficiency = analysis.get('efficiency_score', {})
    
    executive_summary = f"""
    <b>Coût énergétique annuel estimé:</b> {economic.get('annual_cost_estimate', 0):.0f} €<br/>
    <b>Score d'efficacité énergétique:</b> {efficiency.get('score', 0):.1f}/100 (Grade {efficiency.get('grade', 'N/A')})<br/>
    <b>Potentiel d'économies identifié:</b> {economic.get('savings_potential', {}).get('total_potential', 0):.0f} € par an<br/>
    <b>Nombre de recommandations:</b> {len(analysis.get('strategic_recommendations', []))}
    """
    
    story.append(Paragraph(executive_summary, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Analyse économique détaillée
    story.append(Paragraph("ANALYSE ÉCONOMIQUE DÉTAILLÉE", styles['Heading2']))
    
    if economic:
        economic_data = [
            ['Métrique', 'Valeur'],
            ['Coût annuel estimé', f"{economic.get('annual_cost_estimate', 0):.0f} €"],
            ['Coût mensuel moyen', f"{economic.get('monthly_average', 0):.0f} €"],
            ['Prix moyen kWh', f"{economic.get('cost_per_kwh', 0):.3f} €"],
        ]
        
        economic_table = Table(economic_data, colWidths=[200, 150])
        economic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2E86AB'))
        ]))
        
        story.append(economic_table)
        story.append(Spacer(1, 20))
    
    # Recommandations stratégiques
    story.append(Paragraph("RECOMMANDATIONS STRATÉGIQUES", styles['Heading2']))
    
    recommendations = analysis.get('strategic_recommendations', [])
    for i, rec in enumerate(recommendations[:3], 1):  # Top 3 recommandations
        story.append(Paragraph(f"{i}. {rec['title']}", styles['Heading3']))
        story.append(Paragraph(f"<b>Description:</b> {rec['description']}", styles['Normal']))
        story.append(Paragraph(f"<b>Investissement:</b> {rec['investment_required']}", styles['Normal']))
        story.append(Paragraph(f"<b>Retour sur investissement:</b> {rec['payback_period']}", styles['Normal']))
        story.append(Paragraph(f"<b>Économies annuelles:</b> {rec['annual_savings']:.0f} €", styles['Normal']))
        story.append(Paragraph(f"<b>ROI:</b> {rec['roi']:.1f}%", styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Plan d'action
    story.append(Paragraph("PLAN D'ACTION RECOMMANDÉ", styles['Heading2']))
    
    action_plan = analysis.get('action_plan', {})
    for period, actions in action_plan.items():
        if actions:
            period_name = {
                'immediate_actions': 'Actions immédiates (0-1 mois)',
                'short_term_actions': 'Actions court terme (1-6 mois)',
                'medium_term_actions': 'Actions moyen terme (6-18 mois)',
                'long_term_actions': 'Actions long terme (18+ mois)'
            }.get(period, period)
            
            story.append(Paragraph(period_name, styles['Heading3']))
            
            for action in actions:
                story.append(Paragraph(f"• <b>{action['action']}</b>: {action['description']}", styles['Normal']))
                story.append(Paragraph(f"  Coût: {action['cost']}€, Économies: {action['savings_potential']}", styles['Normal']))
            
            story.append(Spacer(1, 10))
    
    # Générer le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# Routes Flask
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Gestion de l'upload de fichiers"""
    if request.method == 'POST':
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
            
            flash('Fichier uploadé avec succès!')
            return redirect(url_for('business_dashboard', filename=filename))
        else:
            flash('Type de fichier non autorisé. Utilisez CSV, Excel ou JSON.')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/dashboard/<filename>')
def business_dashboard(filename):
    """Dashboard business avancé"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            flash('Fichier non trouvé.')
            return redirect(url_for('upload_file'))
        
        # Charger les données
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filename.endswith('.json'):
            df = pd.read_json(filepath)
        else:
            flash('Format de fichier non supporté.')
            return redirect(url_for('upload_file'))
        
        # Analyser les données avec la nouvelle fonction business
        analysis = analyze_business_data(df)
        
        if 'error' in analysis:
            flash(f'Erreur d\'analyse: {analysis["error"]}')
            return redirect(url_for('upload_file'))
        
        # Créer les graphiques
        charts = create_business_charts(df, analysis)
        
        # Date actuelle
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        return render_template('dashboard_business.html', 
                             filename=filename, 
                             analysis=analysis, 
                             consumption_chart_data=charts['consumption_chart'],
                             hp_hc_chart_data=charts['hp_hc_chart'],
                             monthly_chart_data=charts['monthly_chart'],
                             peaks_chart_data=charts['peaks_chart'],
                             economic_chart_data=charts['economic_chart'],
                             current_time=current_time)
        
    except Exception as e:
        flash(f'Erreur lors de l\'analyse: {str(e)}')
        return redirect(url_for('upload_file'))

@app.route('/generate_report/<filename>')
def generate_business_report(filename):
    """Génération du rapport PDF business"""
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
        
        analysis = analyze_business_data(df)
        
        # Générer le PDF business
        pdf_buffer = generate_business_pdf(analysis, filename)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'rapport_business_{filename.split(".")[0]}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Erreur lors de la génération du rapport: {str(e)}')
        return redirect(url_for('business_dashboard', filename=filename))

@app.route('/sample_data')
def sample_business_data():
    """Génère des données d'exemple business"""
    # Créer des données d'exemple avec format entreprise
    dates = pd.date_range(start='2024-01-01', end='2024-06-30', freq='W')
    np.random.seed(42)
    
    zones = ['Bureaux', 'Réfectoire', 'Salle Serveurs', 'Atelier', 'Extérieurs']
    
    data = []
    for date in dates:
        zone = np.random.choice(zones)
        
        # Consommation HP (plus élevée en journée)
        hp_base = 1200 if zone == 'Salle Serveurs' else 800
        hp_consumption = hp_base + np.random.normal(0, 200)
        
        # Consommation HC (plus faible la nuit)
        hc_base = 600 if zone == 'Salle Serveurs' else 400
        hc_consumption = hc_base + np.random.normal(0, 150)
        
        total_consumption = hp_consumption + hc_consumption
        estimated_bill = hp_consumption * 0.22 + hc_consumption * 0.12  # Tarifs HP/HC
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'hp_consumption': max(0, hp_consumption),
            'hc_consumption': max(0, hc_consumption),
            'total_consumption': total_consumption,
            'zone': zone,
            'estimated_bill': estimated_bill
        })
    
    return jsonify(data)

if __name__ == '__main__':
    print("🚀 Démarrage d'EnergyInsight BUSINESS")
    print("📊 Fonctionnalités stratégiques:")
    print("   ✅ Analyse automatisée des pics anormaux")
    print("   ✅ Projections économiques détaillées")
    print("   ✅ Vue par période (HP/HC, zones, saisons)")
    print("   ✅ Rapport PDF avec potentiel d'économies")
    print("   ✅ Objectifs de réduction & plan d'action")
    print("   ✅ Import CSV/Excel de factures entreprise")
    print("🌐 Application disponible sur: http://127.0.0.1:5000")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

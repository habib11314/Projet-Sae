#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseurs spécialisés pour les 3 formats standards du secteur énergétique
"""

import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json

def analyze_grdf_courbe_charge(df):
    """Analyse spécialisée ultra-avancée pour les courbes de charge GRD-F"""
    print("🔍 Analyse spécialisée: Format GRD-F / Courbes de charge")
    
    results = {
        'data_format': 'grdf_courbe_charge',
        'file_info': {'format_name': 'Courbes de charge GRD-F (Enedis/EDF/ENGIE)'},
        'basic_stats': {},
        'advanced_stats': {},
        'peaks': [],
        'recommendations': [],
        'cost_analysis': {},
        'energy_efficiency': {},
        'consumption_patterns': {},
        'seasonal_analysis': {},
        'graph_json': None
    }
    
    # Préparer les données avec horodatage intelligent
    if 'datetime' in df.columns:
        df['date'] = pd.to_datetime(df['datetime'])
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    # Extraire les informations temporelles pour l'analyse avancée
    df['hour'] = df['date'].dt.hour
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6])
    
    # Consommation principale avec calcul intelligent
    if 'consumption' not in df.columns and 'hp_consumption' in df.columns and 'hc_consumption' in df.columns:
        df['consumption'] = df['hp_consumption'] + df['hc_consumption']
    
    consumption = df['consumption'].dropna()
    
    # Statistiques de base enrichies
    results['basic_stats'] = {
        'total_consumption': float(consumption.sum()),
        'avg_consumption': float(consumption.mean()),
        'max_consumption': float(consumption.max()),
        'min_consumption': float(consumption.min()),
        'std_consumption': float(consumption.std()),
        'nb_points_mesure': len(consumption),
        'periode_analyse': f"{df['date'].min().strftime('%d/%m/%Y')} au {df['date'].max().strftime('%d/%m/%Y')}",
        'duree_jours': (df['date'].max() - df['date'].min()).days,
        'moyenne_quotidienne': float(consumption.sum() / max(1, (df['date'].max() - df['date'].min()).days))
    }
    
    # ANALYSE AVANCÉE DES PATTERNS DE CONSOMMATION
    consumption_by_hour = df.groupby('hour')['consumption'].agg(['mean', 'std', 'max']).round(2)
    consumption_by_day = df.groupby('day_of_week')['consumption'].mean().round(2)
    consumption_weekend_vs_week = df.groupby('is_weekend')['consumption'].mean().round(2)
    
    results['consumption_patterns'] = {
        'pic_matinal': {
            'heure': int(consumption_by_hour.loc[consumption_by_hour.index.intersection(range(6, 10))]['mean'].idxmax()) if len(consumption_by_hour.index.intersection(range(6, 10))) > 0 else 8,
            'valeur': float(consumption_by_hour.loc[consumption_by_hour.index.intersection(range(6, 10))]['mean'].max()) if len(consumption_by_hour.index.intersection(range(6, 10))) > 0 else 0,
            'interpretation': 'Pic de démarrage d\'activité'
        },
        'pic_vespertine': {
            'heure': int(consumption_by_hour.loc[consumption_by_hour.index.intersection(range(17, 21))]['mean'].idxmax()) if len(consumption_by_hour.index.intersection(range(17, 21))) > 0 else 18,
            'valeur': float(consumption_by_hour.loc[consumption_by_hour.index.intersection(range(17, 21))]['mean'].max()) if len(consumption_by_hour.index.intersection(range(17, 21))) > 0 else 0,
            'interpretation': 'Pic de fin d\'activité'
        },
        'consommation_nuit': {
            'moyenne': float(consumption_by_hour.loc[consumption_by_hour.index.intersection([22, 23, 0, 1, 2, 3, 4, 5])]['mean'].mean()) if len(consumption_by_hour.index.intersection([22, 23, 0, 1, 2, 3, 4, 5])) > 0 else float(consumption.quantile(0.1)),
            'interpretation': 'Consommation de base (veille, éclairage de sécurité)'
        },
        'ratio_weekend_semaine': float(consumption_weekend_vs_week.get(True, 0) / consumption_weekend_vs_week.get(False, 1)) if consumption_weekend_vs_week.get(False, 0) > 0 else 1,
        'charge_base_estimee': float(consumption.quantile(0.1)),
        'facteur_charge': float(consumption.mean() / consumption.max()) if consumption.max() > 0 else 0
    }
    
    # Analyse HP/HC ultra-détaillée
    if 'hp_consumption' in df.columns and 'hc_consumption' in df.columns:
        hp_total = df['hp_consumption'].sum()
        hc_total = df['hc_consumption'].sum()
        
        # Calcul des économies potentielles
        prix_hp = 0.1593  # Prix HP moyen professionnel 2024
        prix_hc = 0.1249  # Prix HC moyen professionnel 2024
        cout_actuel = hp_total * prix_hp + hc_total * prix_hc
        
        # Simulation optimisation HP/HC
        total_conso = hp_total + hc_total
        ratio_optimal_hc = 0.65  # 65% en HC serait optimal
        hc_optimal = total_conso * ratio_optimal_hc
        hp_optimal = total_conso * (1 - ratio_optimal_hc)
        cout_optimal = hp_optimal * prix_hp + hc_optimal * prix_hc
        economie_potentielle = cout_actuel - cout_optimal
        
        results['advanced_stats']['hp_hc_analysis'] = {
            'total_hp': float(hp_total),
            'total_hc': float(hc_total),
            'ratio_hp_hc': float(hp_total / hc_total) if hc_total > 0 else 0,
            'pourcentage_hp': float(hp_total / (hp_total + hc_total) * 100),
            'pourcentage_hc': float(hc_total / (hp_total + hc_total) * 100),
            'cout_actuel': round(cout_actuel, 2),
            'cout_optimal': round(cout_optimal, 2),
            'economie_potentielle': round(economie_potentielle, 2),
            'pourcentage_economie': round((economie_potentielle / cout_actuel * 100), 1) if cout_actuel > 0 else 0,
            'recommandation_transfert_kwh': round(max(0, hp_total - hp_optimal), 0)
        }
    
    # DÉTECTION INTELLIGENTE DES PICS ET ANOMALIES
    mean_conso = consumption.mean()
    std_conso = consumption.std()
    
    # Seuils adaptatifs selon le type d'installation
    if mean_conso > 100:  # Grande installation
        seuil_pic_majeur = mean_conso + 3 * std_conso
        seuil_pic_mineur = mean_conso + 2 * std_conso
    else:  # Petite installation
        seuil_pic_majeur = mean_conso + 2.5 * std_conso
        seuil_pic_mineur = mean_conso + 1.5 * std_conso
    
    pics_majeurs = consumption[consumption > seuil_pic_majeur]
    pics_mineurs = consumption[(consumption > seuil_pic_mineur) & (consumption <= seuil_pic_majeur)]
    
    for idx in pics_majeurs.index:
        results['peaks'].append({
            'date': df.loc[idx, 'date'].strftime('%d/%m/%Y %H:%M'),
            'value': float(consumption.loc[idx]),
            'severity': 'critical',
            'percentage_above_avg': float((consumption.loc[idx] - mean_conso) / mean_conso * 100),
            'cout_depassement': round((consumption.loc[idx] - mean_conso) * 0.15, 2),
            'heure': df.loc[idx, 'hour'],
            'type_jour': 'Weekend' if df.loc[idx, 'is_weekend'] else 'Semaine'
        })
    
    for idx in pics_mineurs.index[:5]:  # Limiter à 5 pics mineurs
        results['peaks'].append({
            'date': df.loc[idx, 'date'].strftime('%d/%m/%Y %H:%M'),
            'value': float(consumption.loc[idx]),
            'severity': 'medium',
            'percentage_above_avg': float((consumption.loc[idx] - mean_conso) / mean_conso * 100),
            'cout_depassement': round((consumption.loc[idx] - mean_conso) * 0.15, 2),
            'heure': df.loc[idx, 'hour'],
            'type_jour': 'Weekend' if df.loc[idx, 'is_weekend'] else 'Semaine'
        })
    
    # RECOMMANDATIONS ULTRA-PRÉCISES ET ACTIONNABLES
    recommandations = []
    
    # 1. Gestion des pics
    if len(results['peaks']) > 0:
        pics_critiques = [p for p in results['peaks'] if p['severity'] == 'critical']
        pics_moyens = [p for p in results['peaks'] if p['severity'] == 'medium']
        
        if pics_critiques:
            recommandations.append({
                'category': '🚨 PICS CRITIQUES',
                'action': f"{len(pics_critiques)} pics critiques détectés ! Économie potentielle : {sum([p['cout_depassement'] for p in pics_critiques]):.0f}€/mois",
                'priority': 'critical',
                'solutions': [
                    f"Installer un délesteur automatique (ROI: 6-12 mois)",
                    f"Décaler les gros équipements hors des heures {', '.join(set([str(p['heure']) for p in pics_critiques]))}h",
                    f"Programmer un effacement de {max([p['value'] for p in pics_critiques]):.0f}kW pendant les pics",
                    f"Négocier un contrat d'effacement tarifaire avec votre fournisseur"
                ],
                'roi_estime': f"{sum([p['cout_depassement'] for p in pics_critiques]) * 12:.0f}€/an"
            })
        
        if pics_moyens:
            recommandations.append({
                'category': '⚠️ Optimisation des pointes',
                'action': f"{len(pics_moyens)} pics modérés détectés. Optimisation recommandée.",
                'priority': 'high',
                'solutions': [
                    f"Lisser la consommation sur les créneaux {', '.join(set([str(p['heure']) for p in pics_moyens]))}h",
                    f"Installer des variateurs de vitesse sur les moteurs",
                    f"Programmer le démarrage échelonné des équipements"
                ],
                'roi_estime': f"{sum([p['cout_depassement'] for p in pics_moyens]) * 12:.0f}€/an"
            })
    
    # 2. Optimisation HP/HC ultra-détaillée
    if 'hp_hc_analysis' in results['advanced_stats']:
        hp_hc = results['advanced_stats']['hp_hc_analysis']
        
        if hp_hc['economie_potentielle'] > 100:
            recommandations.append({
                'category': '💰 OPTIMISATION HP/HC PRIORITAIRE',
                'action': f"Économie immédiate possible : {hp_hc['economie_potentielle']:.0f}€/mois ({hp_hc['pourcentage_economie']:.1f}%)",
                'priority': 'high',
                'solutions': [
                    f"Transférer {hp_hc['recommandation_transfert_kwh']:.0f} kWh/mois vers les heures creuses",
                    f"Programmer les gros équipements entre 22h30 et 6h30",
                    f"Installer des ballons d'eau chaude à accumulation HC",
                    f"Décaler la production/maintenance en HC quand possible",
                    f"Timer intelligent sur les systèmes de chauffage/climatisation"
                ],
                'roi_estime': f"{hp_hc['economie_potentielle'] * 12:.0f}€/an - ROI immédiat"
            })
    
    # 3. Analyse du facteur de charge
    facteur_charge = results['consumption_patterns']['facteur_charge']
    if facteur_charge < 0.3:
        recommandations.append({
            'category': '📊 Amélioration du facteur de charge',
            'action': f"Facteur de charge faible ({facteur_charge:.2f}). Optimisation énergétique possible.",
            'priority': 'medium',
            'solutions': [
                f"Lisser la consommation sur 24h pour améliorer l'efficacité",
                f"Négocier un tarif adapté aux installations à facteur de charge variable",
                f"Installer un système de stockage d'énergie",
                f"Optimiser la planification des process énergétivores"
            ],
            'roi_estime': f"5-15% d'économie sur la facture énergétique"
        })
    
    # 4. Consommation de base / veille
    conso_base = results['consumption_patterns']['charge_base_estimee']
    if conso_base > results['basic_stats']['avg_consumption'] * 0.4:
        recommandations.append({
            'category': '🔋 Réduction de la consommation de base',
            'action': f"Consommation de base élevée ({conso_base:.1f} kW). Chasse aux consommations fantômes.",
            'priority': 'medium',
            'solutions': [
                f"Audit des équipements en veille permanente",
                f"Installer des prises programmables/coupures automatiques",
                f"Optimiser l'éclairage de sécurité (LED, détecteurs)",
                f"Vérifier l'isolation thermique (chauffage/climatisation de base)"
            ],
            'roi_estime': f"Économie potentielle : {conso_base * 0.15 * 24 * 30:.0f}€/mois"
        })
    
    # 5. Pattern weekend vs semaine
    ratio_weekend = results['consumption_patterns']['ratio_weekend_semaine']
    if ratio_weekend > 0.8:
        recommandations.append({
            'category': '📅 Optimisation week-end',
            'action': f"Consommation week-end élevée ({ratio_weekend:.2f} vs semaine). Economies possibles.",
            'priority': 'low',
            'solutions': [
                f"Programmer l'arrêt automatique des équipements non-essentiels",
                f"Optimiser le chauffage/climatisation en absence",
                f"Maintenance préventive le week-end plutôt qu'en continu",
                f"Installer des sondes de présence"
            ],
            'roi_estime': f"5-10% d'économie sur les consommations week-end"
        })
    
    # 6. Recommandations saisonnières
    if 'month' in df.columns and df['month'].nunique() >= 3:
        conso_by_month = df.groupby('month')['consumption'].mean()
        ecart_saisonnier = (conso_by_month.max() - conso_by_month.min()) / conso_by_month.mean()
        
        if ecart_saisonnier > 0.5:
            recommandations.append({
                'category': '🌡️ Optimisation saisonnière',
                'action': f"Forte variation saisonnière ({ecart_saisonnier:.1%}). Optimisation chauffage/climatisation.",
                'priority': 'medium',
                'solutions': [
                    f"Installer une pompe à chaleur haute efficacité",
                    f"Améliorer l'isolation thermique du bâtiment",
                    f"Programmer les températures selon l'occupation",
                    f"Installer des récupérateurs de chaleur"
                ],
                'roi_estime': f"15-30% d'économie sur le chauffage/climatisation"
            })
    
    results['recommendations'] = recommandations
    
    # ANALYSE ÉCONOMIQUE ULTRA-DÉTAILLÉE
    prix_base_kwh = 0.15  # Prix moyen professionnel
    prix_hp = 0.1593
    prix_hc = 0.1249
    
    # Coûts actuels
    if 'hp_hc_analysis' in results['advanced_stats']:
        cout_total = results['advanced_stats']['hp_hc_analysis']['cout_actuel']
    else:
        cout_total = results['basic_stats']['total_consumption'] * prix_base_kwh
    
    cout_mensuel = cout_total / max(1, results['basic_stats']['duree_jours'] / 30)
    cout_annuel = cout_mensuel * 12
    
    # Calcul des économies par axe d'amélioration
    economie_pics = sum([p.get('cout_depassement', 0) for p in results['peaks']]) * 12 if results['peaks'] else 0
    economie_hp_hc = results['advanced_stats'].get('hp_hc_analysis', {}).get('economie_potentielle', 0) * 12
    economie_base = (results['consumption_patterns']['charge_base_estimee'] * 0.1 * 24 * 365 * prix_base_kwh) if results['consumption_patterns']['charge_base_estimee'] > 0 else 0
    
    total_economies_possibles = economie_pics + economie_hp_hc + economie_base
    
    results['cost_analysis'] = {
        'cout_total_periode': round(cout_total, 2),
        'cout_mensuel_estime': round(cout_mensuel, 2),
        'cout_annuel_estime': round(cout_annuel, 2),
        'cout_kwh_moyen': round(cout_total / results['basic_stats']['total_consumption'], 3) if results['basic_stats']['total_consumption'] > 0 else prix_base_kwh,
        'economies_possibles': {
            'pics_et_pointes': round(economie_pics, 2),
            'optimisation_hp_hc': round(economie_hp_hc, 2),
            'reduction_base': round(economie_base, 2),
            'total_annuel': round(total_economies_possibles, 2),
            'pourcentage_total': round((total_economies_possibles / cout_annuel * 100), 1) if cout_annuel > 0 else 0
        },
        'benchmark_sectoriel': {
            'votre_ratio_kwh_euro': round(results['basic_stats']['total_consumption'] / cout_total, 1) if cout_total > 0 else 0,
            'ratio_optimal_cible': 8.5,  # kWh/€ cible pour une installation optimisée
            'position': 'Bon' if (results['basic_stats']['total_consumption'] / cout_total) > 7 else 'À améliorer'
        },
        'projections_investissement': {
            'delesteur_automatique': {'cout': 3500, 'economie_annuelle': economie_pics, 'roi_annees': round(3500 / max(1, economie_pics), 1)},
            'programmation_hp_hc': {'cout': 1200, 'economie_annuelle': economie_hp_hc, 'roi_annees': round(1200 / max(1, economie_hp_hc), 1)},
            'audit_energetique': {'cout': 2000, 'economie_annuelle': total_economies_possibles * 0.8, 'roi_annees': round(2000 / max(1, total_economies_possibles * 0.8), 1)}
        }
    }
    
    # EFFICACITÉ ÉNERGÉTIQUE GLOBALE
    nb_jours = max(1, results['basic_stats']['duree_jours'])
    
    results['energy_efficiency'] = {
        'performance_globale': {
            'note_efficacite': min(10, max(1, 10 - (len(results['peaks']) * 0.5) - (max(0, facteur_charge - 0.7) * 5))),
            'niveau': 'Excellent' if facteur_charge > 0.7 and len(results['peaks']) < 2 else 'Bon' if facteur_charge > 0.5 else 'À améliorer'
        },
        'indicateurs_cles': {
            'stabilite_consommation': round(1 - (results['basic_stats']['std_consumption'] / results['basic_stats']['avg_consumption']), 2),
            'efficacite_temporelle': round(facteur_charge, 2),
            'optimisation_tarifaire': round((results['advanced_stats'].get('hp_hc_analysis', {}).get('pourcentage_hc', 50)) / 65, 2),
            'gestion_pics': round(max(0, 1 - len(results['peaks']) / 10), 2)
        },
        'potentiel_amelioration': {
            'score_actuel': round(facteur_charge * 10, 1),
            'score_potentiel': round(min(10, facteur_charge * 10 + 2), 1),
            'actions_prioritaires': [r['category'] for r in recommandations[:3]]
        }
    }
    
    return results

def analyze_factures_normalisees(df):
    """Analyse spécialisée ultra-avancée pour les factures normalisées"""
    print("🔍 Analyse spécialisée: Format Factures Normalisées")
    
    results = {
        'data_format': 'factures_normalisees',
        'file_info': {'format_name': 'Factures Normalisées (Comptabilité Entreprise)'},
        'basic_stats': {},
        'advanced_stats': {},
        'peaks': [],
        'recommendations': [],
        'cost_analysis': {},
        'supplier_analysis': {},
        'contract_optimization': {},
        'graph_json': None
    }
    
    # Consommation totale avec gestion HP/HC
    if 'consumption' not in df.columns and 'hp_consumption' in df.columns and 'hc_consumption' in df.columns:
        df['consumption'] = df['hp_consumption'] + df['hc_consumption']
    
    consumption = df['consumption'].dropna()
    
    # Statistiques de base enrichies
    results['basic_stats'] = {
        'total_consumption': float(consumption.sum()),
        'avg_consumption': float(consumption.mean()),
        'max_consumption': float(consumption.max()),
        'min_consumption': float(consumption.min()),
        'std_consumption': float(consumption.std()),
        'nb_factures': len(df),
        'nb_fournisseurs': df['fournisseur'].nunique() if 'fournisseur' in df.columns else 1,
        'nb_sites': df['pdl'].nunique() if 'pdl' in df.columns else 1,
        'periode_analyse': f"{len(df)} factures analysées"
    }
    
    # ANALYSE FINANCIÈRE ULTRA-DÉTAILLÉE avec fallback intelligent
    montant_total = 0
    montant_ht = 0
    taxes_total = 0
    
    # Chercher les colonnes de montant dans l'ordre de priorité
    montant_col = None
    if 'montant_ttc' in df.columns:
        montant_col = 'montant_ttc'
        montant_total = df[montant_col].sum()
        montant_ht = df['montant_ht'].sum() if 'montant_ht' in df.columns else montant_total / 1.20
    elif 'montant_ht' in df.columns:
        montant_col = 'montant_ht'
        montant_ht = df[montant_col].sum()
        montant_total = montant_ht * 1.20
    elif 'montant' in df.columns:
        montant_col = 'montant'
        montant_total = df[montant_col].sum()
        montant_ht = montant_total / 1.20
    else:
        # Fallback: chercher toute colonne avec € et montant/facturé
        for col in df.columns:
            if '€' in col and ('montant' in col.lower() or 'facturé' in col.lower()):
                montant_col = col
                montant_total = df[col].sum()
                montant_ht = montant_total / 1.20
                break
    
    # Calcul des taxes détaillées
    if 'tva' in df.columns:
        taxes_total += df['tva'].sum()
    if 'cspe' in df.columns:
        taxes_total += df['cspe'].sum()
    if 'cta' in df.columns:
        taxes_total += df['cta'].sum()
    
    cout_kwh_moyen = montant_total / consumption.sum() if consumption.sum() > 0 else 0
    
    results['cost_analysis'] = {
        'montant_total_factures': float(montant_total),
        'montant_ht_total': float(montant_ht),
        'taxes_et_contributions': float(taxes_total),
        'cout_moyen_kwh': float(cout_kwh_moyen),
        'facture_moyenne': float(montant_total / len(df)) if len(df) > 0 else 0,
        'facture_mediane': float(df[montant_col].median()) if montant_col and montant_col in df.columns else 0,
        'ecart_type_factures': float(df[montant_col].std()) if montant_col and montant_col in df.columns else 0,
        'benchmark_prix': {
            'votre_prix_kwh': round(cout_kwh_moyen, 4),
            'prix_marche_reference': 0.1489,  # Prix de référence professionnel
            'ecart_marche_pourcent': round((cout_kwh_moyen - 0.1489) / 0.1489 * 100, 1) if cout_kwh_moyen > 0 else 0,
            'position_concurrentielle': 'Favorable' if cout_kwh_moyen < 0.1489 else 'À négocier'
        }
    }
    
    # ANALYSE COMPARATIVE PAR FOURNISSEUR
    prix_par_fournisseur = {}  # Initialiser par défaut
    
    if 'fournisseur' in df.columns:
        # Construire la fonction d'agrégation dynamiquement
        agg_dict = {
            'consumption': ['sum', 'mean']
        }
        
        # Ajouter les colonnes de montant si elles existent
        if 'montant_ttc' in df.columns:
            agg_dict['montant_ttc'] = ['sum', 'mean']
        elif 'montant_ht' in df.columns:
            agg_dict['montant_ht'] = ['sum', 'mean']
        elif 'montant' in df.columns:
            agg_dict['montant'] = ['sum', 'mean']
        
        # Ajouter une colonne de comptage si elle existe
        if 'numero_client' in df.columns:
            agg_dict['numero_client'] = 'count'
        elif 'site' in df.columns:
            agg_dict['site'] = 'count'
        else:
            # Utiliser l'index pour compter
            agg_dict['consumption'] = ['sum', 'mean', 'count']
        
        fournisseur_stats = df.groupby('fournisseur').agg(agg_dict).round(2)
        
        # Calcul des prix moyens par fournisseur avec fallback robuste
        for fournisseur in df['fournisseur'].unique():
            df_fournisseur = df[df['fournisseur'] == fournisseur]
            conso_fournisseur = df_fournisseur['consumption'].sum()
            montant_fournisseur = 0
            
            # Chercher la colonne de montant dans l'ordre de priorité
            if montant_col and montant_col in df_fournisseur.columns:
                montant_fournisseur = df_fournisseur[montant_col].sum()
            elif 'montant_ttc' in df_fournisseur.columns:
                montant_fournisseur = df_fournisseur['montant_ttc'].sum()
            elif 'montant_ht' in df_fournisseur.columns:
                montant_fournisseur = df_fournisseur['montant_ht'].sum()
            elif 'montant' in df_fournisseur.columns:
                montant_fournisseur = df_fournisseur['montant'].sum()
            else:
                # Fallback - chercher une colonne avec € dans le nom
                for col in df_fournisseur.columns:
                    if '€' in col and ('montant' in col.lower() or 'facturé' in col.lower()):
                        montant_fournisseur = df_fournisseur[col].sum()
                        break
            
            prix_par_fournisseur[fournisseur] = {
                'prix_kwh': round(montant_fournisseur / conso_fournisseur, 4) if conso_fournisseur > 0 else 0,
                'part_volume': round(conso_fournisseur / consumption.sum() * 100, 1) if consumption.sum() > 0 else 0,
                'part_cout': round(montant_fournisseur / montant_total * 100, 1) if montant_total > 0 else 0,
                'nb_factures': len(df_fournisseur),
                'consommation_totale': round(conso_fournisseur, 0),
                'montant_total': round(montant_fournisseur, 2)
            }
        
        results['supplier_analysis'] = {
            'comparaison_fournisseurs': prix_par_fournisseur,
            'fournisseur_le_moins_cher': min(prix_par_fournisseur.keys(), key=lambda x: prix_par_fournisseur[x]['prix_kwh']) if prix_par_fournisseur else 'N/A',
            'fournisseur_le_plus_cher': max(prix_par_fournisseur.keys(), key=lambda x: prix_par_fournisseur[x]['prix_kwh']) if prix_par_fournisseur else 'N/A',
            'ecart_prix_max': round(max([f['prix_kwh'] for f in prix_par_fournisseur.values()]) - min([f['prix_kwh'] for f in prix_par_fournisseur.values()]), 4) if prix_par_fournisseur else 0,
            'diversification_score': len(prix_par_fournisseur),
            'recommandation_consolidation': len(prix_par_fournisseur) > 2
        }
        
        # Créer une version simplifiée pour le template
        analyse_fournisseurs_simple = {}
        for fournisseur in df['fournisseur'].unique():
            df_fournisseur = df[df['fournisseur'] == fournisseur]
            analyse_fournisseurs_simple[fournisseur] = {
                'consumption_total': round(df_fournisseur['consumption'].sum(), 0),
                'consumption_moyenne': round(df_fournisseur['consumption'].mean(), 2),
                'nb_factures': len(df_fournisseur)
            }
        
        results['advanced_stats']['analyse_fournisseurs'] = analyse_fournisseurs_simple
    
    # OPTIMISATION CONTRACTUELLE
    # Simulation groupement d'achat
    meilleur_prix = min([f['prix_kwh'] for f in prix_par_fournisseur.values()]) if prix_par_fournisseur else cout_kwh_moyen
    economie_groupement = (cout_kwh_moyen - meilleur_prix) * consumption.sum() if meilleur_prix < cout_kwh_moyen else 0
    
    # Simulation contrat optimisé
    prix_negocie_estime = cout_kwh_moyen * 0.92  # 8% de réduction possible
    economie_negociation = (cout_kwh_moyen - prix_negocie_estime) * consumption.sum()
    
    results['contract_optimization'] = {
        'prix_actuel_moyen': round(cout_kwh_moyen, 4),
        'prix_optimise_possible': round(prix_negocie_estime, 4),
        'economie_groupement_annuelle': round(economie_groupement * 12, 2) if economie_groupement > 0 else 0,
        'economie_negociation_annuelle': round(economie_negociation * 12, 2),
        'potentiel_economie_total': round((economie_groupement + economie_negociation) * 12, 2),
        'recommandations_contractuelles': {
            'volume_annuel_total': round(consumption.sum() * 12, 0),
            'poids_negociation': 'Fort' if consumption.sum() * 12 > 500000 else 'Moyen' if consumption.sum() * 12 > 100000 else 'Faible',
            'type_contrat_optimal': 'Fixe' if results['basic_stats']['std_consumption'] < results['basic_stats']['avg_consumption'] * 0.3 else 'Variable indexé',
            'duree_recommandee': '3 ans' if consumption.sum() * 12 > 200000 else '2 ans'
        }
    }
    
    # RECOMMANDATIONS ULTRA-DÉTAILLÉES POUR FACTURES
    recommandations = []
    
    # 1. Optimisation multi-fournisseurs
    if results['basic_stats']['nb_fournisseurs'] > 1 and 'supplier_analysis' in results:
        supplier_analysis = results['supplier_analysis']
        economie_possible = supplier_analysis['ecart_prix_max'] * consumption.sum() * 12
        
        recommandations.append({
            'category': '🏢 OPTIMISATION MULTI-FOURNISSEURS',
            'action': f"Écart de {supplier_analysis['ecart_prix_max']:.4f}€/kWh entre fournisseurs. Économie : {economie_possible:.0f}€/an",
            'priority': 'critical',
            'solutions': [
                f"Centraliser {results['basic_stats']['nb_fournisseurs']} contrats vers {supplier_analysis['fournisseur_le_moins_cher']}",
                f"Négocier un contrat groupé pour {consumption.sum():.0f} kWh/période",
                f"Renégocier avec vos fournisseurs actuels en utilisant l'offre de {supplier_analysis['fournisseur_le_moins_cher']}",
                f"Lancer un appel d'offres pour optimiser votre portefeuille"
            ],
            'roi_estime': f"{economie_possible:.0f}€/an - Économie immédiate"
        })
    
    # 2. Négociation tarifaire
    benchmark = results['cost_analysis']['benchmark_prix']
    if benchmark['ecart_marche_pourcent'] > 5:
        recommandations.append({
            'category': '💰 NÉGOCIATION TARIFAIRE URGENTE',
            'action': f"Prix {benchmark['ecart_marche_pourcent']:+.1f}% vs marché. Renégociation immédiate recommandée.",
            'priority': 'high',
            'solutions': [
                f"Négocier une baisse vers {benchmark['prix_marche_reference']:.4f}€/kWh (prix marché)",
                f"Faire jouer la concurrence avec 3-4 fournisseurs",
                f"Proposer un contrat pluriannuel pour obtenir de meilleurs tarifs",
                f"Grouper vos sites pour augmenter le volume négocié"
            ],
            'roi_estime': f"{results['contract_optimization']['economie_negociation_annuelle']:.0f}€/an"
        })
    
    # 3. Optimisation HP/HC sur factures
    if 'hp_consumption' in df.columns and 'hc_consumption' in df.columns:
        hp_total = df['hp_consumption'].sum()
        hc_total = df['hc_consumption'].sum()
        ratio_hc = hc_total / (hp_total + hc_total) * 100
        
        if ratio_hc < 60:
            manque_hc = (hp_total + hc_total) * 0.6 - hc_total
            economie_hc = manque_hc * (0.1593 - 0.1249) * 12  # Différence HP/HC
            
            recommandations.append({
                'category': '⚡ OPTIMISATION HP/HC',
                'action': f"Seulement {ratio_hc:.1f}% en heures creuses. Objectif : 60%+",
                'priority': 'high',
                'solutions': [
                    f"Transférer {manque_hc:.0f} kWh/mois vers les heures creuses",
                    f"Programmer les équipements entre 22h30-6h30 et week-ends",
                    f"Installer des systèmes de stockage/accumulation",
                    f"Décaler la production non urgente en heures creuses"
                ],
                'roi_estime': f"{economie_hc:.0f}€/an d'économie directe"
            })
    
    # 4. Régularité des factures
    if results['cost_analysis']['ecart_type_factures'] > results['cost_analysis']['facture_moyenne'] * 0.3:
        recommandations.append({
            'category': '📊 LISSAGE DE CONSOMMATION',
            'action': f"Forte variabilité des factures. Optimisation de la régularité possible.",
            'priority': 'medium',
            'solutions': [
                f"Analyser les causes des pics de facturation",
                f"Installer des systèmes de monitoring en temps réel",
                f"Programmer les gros équipements sur plusieurs mois",
                f"Négocier un contrat à prix lissé"
            ],
            'roi_estime': f"5-10% d'économie par l'optimisation tarifaire"
        })
    
    # 5. Gestion administrative
    if results['basic_stats']['nb_factures'] > results['basic_stats']['nb_sites'] * 2:
        recommandations.append({
            'category': '📋 SIMPLIFICATION ADMINISTRATIVE',
            'action': f"{results['basic_stats']['nb_factures']} factures pour {results['basic_stats']['nb_sites']} sites. Simplification possible.",
            'priority': 'low',
            'solutions': [
                f"Demander une facturation groupée mensuelle",
                f"Automatiser le traitement comptable des factures",
                f"Négocier des échéances harmonisées",
                f"Mettre en place un portail client unique"
            ],
            'roi_estime': f"Économie administrative : 2-3h/mois de traitement"
        })
    
    # 6. Audit énergétique recommandé
    if montant_total > 50000:  # Pour les gros consommateurs
        recommandations.append({
            'category': '🔍 AUDIT ÉNERGÉTIQUE APPROFONDI',
            'action': f"Volume important ({montant_total:.0f}€). Audit professionnel recommandé.",
            'priority': 'medium',
            'solutions': [
                f"Audit énergétique complet par un bureau d'études",
                f"Étude de faisabilité énergies renouvelables",
                f"Analyse des courbes de charge détaillées",
                f"Optimisation des contrats de maintenance"
            ],
            'roi_estime': f"ROI typique : 15-25% d'économie soit {montant_total * 0.2:.0f}€/an"
        })
    
    results['recommendations'] = recommandations
    
    return results

def analyze_ademe_iso50001(df):
    """Analyse spécialisée ultra-avancée pour les données ADEME / ISO 50001"""
    print("🔍 Analyse spécialisée: Format ADEME / ISO 50001")
    
    results = {
        'data_format': 'ademe_iso50001',
        'file_info': {'format_name': 'ADEME / ISO 50001 (Management Énergétique)'},
        'basic_stats': {},
        'advanced_stats': {},
        'peaks': [],
        'recommendations': [],
        'cost_analysis': {},
        'iso_compliance': {},
        'performance_tracking': {},
        'improvement_plan': {},
        'graph_json': None
    }
    
    # Analyse des indicateurs de performance énergétique
    if 'consumption' in df.columns:
        consumption = df['consumption'].dropna()
        
        results['basic_stats'] = {
            'total_consumption': float(consumption.sum()),
            'avg_consumption': float(consumption.mean()),
            'nb_indicateurs': len(df),
            'types_energie': df['type_energie'].nunique() if 'type_energie' in df.columns else 1,
            'sites_analyses': df['site'].nunique() if 'site' in df.columns else 1,
            'responsables_energie': df['responsable_energie'].nunique() if 'responsable_energie' in df.columns else 1
        }
    
    # ANALYSE CONFORMITÉ ISO 50001
    conformite_score = 0
    criteres_iso = {
        'indicateurs_definis': len(df) >= 5,  # Au moins 5 indicateurs
        'objectifs_chiffres': 'objectif' in df.columns,
        'responsable_designe': 'responsable_energie' in df.columns,
        'suivi_periodique': 'periode' in df.columns,
        'performance_mesuree': 'performance_pourcent' in df.columns
    }
    
    conformite_score = sum(criteres_iso.values()) / len(criteres_iso) * 100
    
    results['iso_compliance'] = {
        'score_conformite': round(conformite_score, 1),
        'niveau_certification': 'Conforme' if conformite_score >= 80 else 'Partiel' if conformite_score >= 60 else 'Non conforme',
        'criteres_respectes': sum(criteres_iso.values()),
        'criteres_manquants': len(criteres_iso) - sum(criteres_iso.values()),
        'actions_requises': [
            'Définir plus d\'indicateurs énergétiques' if not criteres_iso['indicateurs_definis'] else None,
            'Fixer des objectifs chiffrés' if not criteres_iso['objectifs_chiffres'] else None,
            'Désigner un responsable énergie' if not criteres_iso['responsable_designe'] else None,
            'Mettre en place un suivi périodique' if not criteres_iso['suivi_periodique'] else None,
            'Mesurer les performances' if not criteres_iso['performance_mesuree'] else None
        ],
        'audit_interne_requis': conformite_score < 80
    }
    
    # ANALYSE PERFORMANCE VS OBJECTIFS
    if 'objectif' in df.columns and 'consumption' in df.columns:
        df['ecart_objectif'] = ((df['consumption'] - df['objectif']) / df['objectif'] * 100)
        df['performance_niveau'] = df['ecart_objectif'].apply(
            lambda x: 'Excellent' if x <= -10 else 'Bon' if x <= 0 else 'À améliorer' if x <= 10 else 'Critique'
        )
        
        performance_stats = df['performance_niveau'].value_counts()
        
        results['performance_tracking'] = {
            'objectifs_atteints': len(df[df['ecart_objectif'] <= 0]),
            'objectifs_depasses': len(df[df['ecart_objectif'] > 0]),
            'ecart_moyen_pourcent': float(df['ecart_objectif'].mean()),
            'meilleure_performance': float(df['ecart_objectif'].min()),
            'pire_performance': float(df['ecart_objectif'].max()),
            'repartition_performances': {
                'excellent': performance_stats.get('Excellent', 0),
                'bon': performance_stats.get('Bon', 0),
                'a_ameliorer': performance_stats.get('À améliorer', 0),
                'critique': performance_stats.get('Critique', 0)
            },
            'tendance_globale': 'Positive' if df['ecart_objectif'].mean() <= 0 else 'Négative',
            'volatilite_performance': float(df['ecart_objectif'].std())
        }
    
    # ANALYSE PAR TYPE D'ÉNERGIE
    if 'type_energie' in df.columns and 'consumption' in df.columns:
        energie_stats = df.groupby('type_energie').agg({
            'consumption': ['sum', 'mean', 'count'],
            'objectif': 'sum' if 'objectif' in df.columns else 'consumption'
        }).round(2)
        
        # Calcul de l'intensité énergétique par type
        intensites = {}
        for energie in df['type_energie'].unique():
            df_energie = df[df['type_energie'] == energie]
            intensites[energie] = {
                'consommation_totale': float(df_energie['consumption'].sum()),
                'part_du_mix': float(df_energie['consumption'].sum() / consumption.sum() * 100),
                'performance_moyenne': float(df_energie['ecart_objectif'].mean()) if 'ecart_objectif' in df_energie.columns else 0,
                'nb_indicateurs': len(df_energie),
                'priorite_action': 'Haute' if df_energie['ecart_objectif'].mean() > 10 else 'Moyenne' if df_energie['ecart_objectif'].mean() > 0 else 'Faible'
            }
        
        results['advanced_stats']['repartition_energies'] = intensites
        
        # Mix énergétique optimal
        mix_actuel = {energie: intensites[energie]['part_du_mix'] for energie in intensites}
        results['advanced_stats']['mix_energetique'] = {
            'actuel': mix_actuel,
            'recommandations_optimisation': 'Augmenter la part des énergies renouvelables' if mix_actuel.get('Electricite', 0) < 70 else 'Mix déjà optimisé'
        }
    
    # PLAN D'AMÉLIORATION CONTINUE
    plan_actions = []
    
    if 'performance_tracking' in results:
        perf = results['performance_tracking']
        
        # Actions basées sur la performance
        if perf['ecart_moyen_pourcent'] > 10:
            plan_actions.append({
                'axe': 'Performance énergétique',
                'action': 'Révision urgente des objectifs et mise en place d\'actions correctives',
                'delai': '3 mois',
                'impact_estime': 'Réduction 15-25% des écarts'
            })
        
        if perf['volatilite_performance'] > 20:
            plan_actions.append({
                'axe': 'Stabilité du système',
                'action': 'Améliorer la régularité des performances énergétiques',
                'delai': '6 mois',
                'impact_estime': 'Réduction 50% de la volatilité'
            })
    
    # Actions basées sur la conformité ISO
    if conformite_score < 80:
        plan_actions.append({
            'axe': 'Conformité ISO 50001',
            'action': f'Mise en conformité complète (score actuel: {conformite_score:.0f}%)',
            'delai': '12 mois',
            'impact_estime': 'Certification ISO 50001 complète'
        })
    
    results['improvement_plan'] = {
        'actions_prioritaires': plan_actions,
        'budget_estime': len(plan_actions) * 15000,  # 15k€ par axe d'amélioration
        'gain_attendu': {
            'economies_energetiques': '10-20% de la facture énergétique',
            'conformite_reglementaire': 'ISO 50001 + obligations BACS',
            'image_entreprise': 'Certification développement durable'
        },
        'calendrier_deploiement': {
            'phase_1_diagnostic': '1-2 mois',
            'phase_2_mise_en_oeuvre': '6-9 mois',
            'phase_3_certification': '3-4 mois'
        }
    }
    
    # RECOMMANDATIONS ISO 50001 ULTRA-SPÉCIALISÉES
    recommandations = []
    
    if 'performance_tracking' in results:
        perf = results['performance_tracking']
        if perf['ecart_moyen_pourcent'] > 5:
            nb_critiques = perf['repartition_performances']['critique']
            recommandations.append({
                'category': '🎯 PERFORMANCE ÉNERGÉTIQUE CRITIQUE',
                'action': f"Écart moyen de {perf['ecart_moyen_pourcent']:.1f}% vs objectifs. {nb_critiques} indicateurs en zone critique.",
                'priority': 'critical',
                'solutions': [
                    f"Réviser immédiatement les {nb_critiques} indicateurs critiques",
                    f"Mettre en place un plan d'actions correctives sous 30 jours",
                    f"Renforcer le monitoring des consommations",
                    f"Former les équipes aux bonnes pratiques énergétiques"
                ],
                'roi_estime': f"Retour aux objectifs : économie {abs(perf['ecart_moyen_pourcent']) * 0.5:.0f}% minimum"
            })
    
    if conformite_score < 80:
        recommandations.append({
            'category': '📋 MISE EN CONFORMITÉ ISO 50001',
            'action': f"Score conformité: {conformite_score:.0f}%. Certification ISO 50001 incomplète.",
            'priority': 'high',
            'solutions': [
                action for action in results['iso_compliance']['actions_requises'] if action
            ] + [
                f"Audit interne complet du système de management",
                f"Formation du responsable énergie aux exigences ISO 50001",
                f"Mise en place des revues énergétiques périodiques"
            ],
            'roi_estime': f"Certification ISO 50001 + éligibilité aides publiques"
        })
    
    if results['basic_stats']['types_energie'] > 1:
        recommandations.append({
            'category': '🔄 OPTIMISATION MULTI-ÉNERGIES',
            'action': f"Mix énergétique complexe ({results['basic_stats']['types_energie']} énergies). Optimisation possible.",
            'priority': 'medium',
            'solutions': [
                f"Analyser les synergies entre énergies (cogénération, récupération)",
                f"Optimiser le mix énergétique selon les coûts et impacts carbone",
                f"Étudier l'intégration d'énergies renouvelables",
                f"Mettre en place un système de pilotage multi-énergies"
            ],
            'roi_estime': f"5-15% d'optimisation du mix énergétique"
        })
    
    if results['basic_stats']['nb_indicateurs'] < 10:
        recommandations.append({
            'category': '📊 ENRICHISSEMENT DES INDICATEURS',
            'action': f"Seulement {results['basic_stats']['nb_indicateurs']} indicateurs. Enrichissement recommandé.",
            'priority': 'medium',
            'solutions': [
                f"Définir des indicateurs par usage (éclairage, chauffage, process)",
                f"Ajouter des indicateurs d'intensité énergétique (kWh/m², kWh/produit)",
                f"Mettre en place des indicateurs de performance carbone",
                f"Créer des tableaux de bord temps réel"
            ],
            'roi_estime': f"Pilotage fin = 10-20% d'économies supplémentaires"
        })
    
    recommandations.append({
        'category': '🌱 DÉVELOPPEMENT DURABLE',
        'action': "Intégrer la dimension développement durable dans votre stratégie énergétique.",
        'priority': 'low',
        'solutions': [
            f"Calculer et réduire votre bilan carbone énergétique",
            f"Étudier la faisabilité d'énergies renouvelables",
            f"Mettre en place des actions de sensibilisation",
            f"Communiquer sur vos performances énergétiques"
        ],
        'roi_estime': f"Image de marque + conformité réglementaire future"
    })
    
    results['recommendations'] = recommandations
    
    # ANALYSE ÉCONOMIQUE SPÉCIALISÉE
    if 'consumption' in df.columns:
        cout_energie_total = consumption.sum() * 0.15  # Prix moyen énergies
        
        # Calcul des économies par amélioration de performance
        if 'performance_tracking' in results:
            ecart_moyen = results['performance_tracking']['ecart_moyen_pourcent']
            economie_performance = abs(min(0, ecart_moyen)) / 100 * cout_energie_total
        else:
            economie_performance = cout_energie_total * 0.1  # 10% par défaut
        
        results['cost_analysis'] = {
            'cout_energie_actuel': round(cout_energie_total, 2),
            'economie_optimisation_performance': round(economie_performance, 2),
            'economie_iso50001': round(cout_energie_total * 0.05, 2),  # 5% par ISO 50001
            'cout_certification': 25000,  # Coût certification ISO 50001
            'roi_certification': round(25000 / max(1, economie_performance + cout_energie_total * 0.05), 1),
            'subventions_possibles': {
                'ademe_diagnostic': 'Jusqu\'à 50% du coût d\'audit',
                'certificats_economie_energie': 'CEE selon les actions',
                'credit_impot_transition': '30% des investissements'
            }
        }
    
    return results

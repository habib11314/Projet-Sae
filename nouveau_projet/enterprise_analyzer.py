import pandas as pd
import numpy as np

# Module d'analyse avancée pour fichiers entreprise (facturation, conso_sites, production_solaire...)
def analyze_enterprise_data(df):
    """
    Analyse avancée pour entreprises :
    - Objectifs de réduction & suivi
    - Vue par période (jour, nuit, WE, saison)
    - Projection économique
    - Analyse automatisée de pics anormaux
    - Adaptation multi-fichiers (facturation, conso, solaire...)
    """
    # Structure compatible avec l'application principale
    results = {
        'data_format': 'enterprise_facturation',
        'file_info': {'columns_detected': list(df.columns)},
        'basic_stats': {},
        'advanced_stats': {},
        'peaks': [],
        'trends': {},
        'recommendations': [],
        'cost_analysis': {},
        'environmental_impact': {},
        'benchmarking': {},
        'solutions': [],
        'graph_json': None
    }
    
    # 1. Statistiques globales
    total_consumption = df[df.columns[2]].sum()
    total_cost = df[df.columns[3]].sum() if df.shape[1] > 3 else None
    nb_sites = df[df.columns[1]].nunique()
    nb_months = df[df.columns[0]].nunique()
    avg_consumption = df[df.columns[2]].mean()
    
    # 2. Objectif de réduction (ex: -10%)
    reduction_target = 0.10
    reduction_target_kwh = total_consumption * reduction_target
    reduction_target_eur = total_cost * reduction_target if total_cost else 0
    
    # Remplir basic_stats avec la structure attendue
    results['basic_stats'] = {
        'total_consumption': total_consumption,
        'avg_consumption': avg_consumption,
        'max_consumption': df[df.columns[2]].max(),
        'min_consumption': df[df.columns[2]].min(),
        'std_consumption': df[df.columns[2]].std(),
        'nb_sites': nb_sites,
        'nb_months': nb_months,
        'reduction_target_kwh': reduction_target_kwh,
        'reduction_target_eur': reduction_target_eur
    }
    
    # 3. Suivi par site
    site_stats = df.groupby(df.columns[1])[[df.columns[2]]].sum().reset_index()
    if df.shape[1] > 3:
        site_cost_stats = df.groupby(df.columns[1])[[df.columns[3]]].sum().reset_index()
        site_stats = site_stats.merge(site_cost_stats, on=df.columns[1])
    site_stats['objectif_kwh'] = site_stats[df.columns[2]] * (1 - reduction_target)
    if total_cost:
        site_stats['objectif_eur'] = site_stats[df.columns[3]] * (1 - reduction_target) if df.shape[1] > 3 else None
    
    results['advanced_stats'] = {
        'site_stats': site_stats,
        'total_cost': total_cost
    }
    
    # 4. Détection de pics anormaux (écart-type)
    mean_consumption = df[df.columns[2]].mean()
    std_consumption = df[df.columns[2]].std()
    threshold = mean_consumption + 2 * std_consumption
    
    anomalies = df[df[df.columns[2]] > threshold]
    peaks = []
    for idx, row in anomalies.iterrows():
        peaks.append({
            'date': str(row[df.columns[0]]),
            'value': row[df.columns[2]],
            'severity': 'high',
            'percentage_above_avg': ((row[df.columns[2]] - mean_consumption) / mean_consumption) * 100,
            'impact_cost': (row[df.columns[2]] - mean_consumption) * 0.20 if total_cost else 0
        })
    
    results['peaks'] = peaks
    
    # 5. Projection économique (ex: -10% la nuit)
    nuit_projection = None
    if 'Nuit' in df.columns or 'nuit' in df.columns:
        nuit_col = 'Nuit' if 'Nuit' in df.columns else 'nuit'
        nuit_total = df[nuit_col].sum()
        nuit_savings = nuit_total * 0.10
        if total_cost:
            nuit_cost = total_cost * (nuit_total / total_consumption)
            nuit_savings_eur = nuit_cost * 0.10
        else:
            nuit_savings_eur = None
        nuit_projection = {'kwh': nuit_savings, 'eur': nuit_savings_eur}
    
    # 6. Vue saisonnière (si possible)
    saison_stats = None
    if any('saison' in c.lower() for c in df.columns):
        saison_col = [c for c in df.columns if 'saison' in c.lower()][0]
        saison_stats = df.groupby(saison_col)[df.columns[2]].sum().to_dict()
    
    # 7. Analyse des coûts complète
    results['cost_analysis'] = {
        'total_cost': total_cost if total_cost else 0,
        'average_daily_cost': (total_cost / nb_months * 30) if total_cost and nb_months > 0 else 0,
        'peak_cost_impact': sum([peak['impact_cost'] for peak in peaks]),
        'annual_projection': total_cost * 12 / nb_months if total_cost and nb_months > 0 else 0,
        'potential_savings': {
            'reduction_pics': sum([peak['impact_cost'] for peak in peaks]) * 0.8,
            'optimisation_generale': total_cost * 0.15 if total_cost else 0,
            'changement_tarification': total_cost * 0.10 if total_cost else 0,
            'solutions_technologiques': total_cost * 0.20 if total_cost else 0,
            'total_annuel': reduction_target_eur
        },
        'nuit_projection': nuit_projection,
        'saison_stats': saison_stats
    }
    
    # 8. Recommandations
    reco = []
    if total_cost:
        reco.append({
            'category': 'Objectifs',
            'action': f"Réduire la consommation de 10% pour économiser {reduction_target_eur:.0f} €/an",
            'priority': 'high',
            'impact': 'high'
        })
    
    if nuit_projection and nuit_projection['eur']:
        reco.append({
            'category': 'Optimisation nocturne',
            'action': f"Réduire de 10% la consommation nocturne : -{nuit_projection['eur']:.0f} €/an",
            'priority': 'medium',
            'impact': 'medium'
        })
    
    if len(peaks) > 0:
        reco.append({
            'category': 'Pics anormaux',
            'action': f"{len(peaks)} pics anormaux détectés : analysez les causes pour éviter les surcoûts",
            'priority': 'high',
            'impact': 'high'
        })
    
    reco.append({
        'category': 'Suivi multi-sites',
        'action': f"Surveiller les {nb_sites} sites pour optimiser la répartition des charges",
        'priority': 'medium',
        'impact': 'medium'
    })
    
    results['recommendations'] = reco
    
    # 9. Créer un graphique simple pour la compatibilité
    try:
        import plotly.graph_objs as go
        import plotly.utils
        import json
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df[df.columns[0]],
            y=df[df.columns[2]],
            mode='lines+markers',
            name='Consommation par site/période',
            line=dict(color='#2E86AB', width=3)
        ))
        
        fig.update_layout(
            title='Analyse Multi-Sites - Consommation Énergétique',
            xaxis_title='Période/Site',
            yaxis_title='Consommation (kWh)',
            height=500,
            template='plotly_white'
        )
        
        results['graph_json'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    except Exception as e:
        print(f"⚠️  Erreur génération graphique entreprise: {e}")
        results['graph_json'] = None
    
    return results

def load_and_analyze(filepath):
    df = pd.read_csv(filepath)
    return analyze_enterprise_data(df)

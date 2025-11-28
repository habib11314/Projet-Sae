#!/usr/bin/env python3
"""
Script pour corriger automatiquement toutes les références d'attributs manquants
"""

def fix_template():
    template_path = "templates/dashboard_advanced.html"
    
    # Lire le fichier
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correction de toutes les références avec la notation bracket
    replacements = [
        # File info
        ('analysis.file_info.columns_detected', "analysis['file_info']['columns_detected']"),
        ('analysis.file_info.total_records', "analysis['file_info']['total_records']"),
        ('analysis.file_info.date_range.start', "analysis['file_info']['date_range']['start']"),
        ('analysis.file_info.date_range.end', "analysis['file_info']['date_range']['end']"),
        ('analysis.file_info.date_range.duration_days', "analysis['file_info']['date_range']['duration_days']"),
        ('analysis.file_info.data_quality.quality_score', "analysis['file_info']['data_quality']['quality_score']"),
        
        # Statistics
        ('analysis.statistics.efficiency_score', "analysis['statistics']['efficiency_score']"),
        ('analysis.basic_stats.median_consumption', "analysis['basic_stats']['median_consumption']"),
        ('analysis.advanced_stats.quartiles.q1', "analysis['advanced_stats']['quartiles']['q1']"),
        ('analysis.advanced_stats.quartiles.q3', "analysis['advanced_stats']['quartiles']['q3']"),
        ('analysis.advanced_stats.quartiles.iqr', "analysis['advanced_stats']['quartiles']['iqr']"),
        ('analysis.advanced_stats.distribution.skewness', "analysis['advanced_stats']['distribution']['skewness']"),
        ('analysis.advanced_stats.distribution.kurtosis', "analysis['advanced_stats']['distribution']['kurtosis']"),
        ('analysis.advanced_stats.efficiency_metrics.consistency_rating', "analysis['advanced_stats']['efficiency_metrics'].get('consistency_rating', 'Non défini')"),
        ('analysis.advanced_stats.efficiency_metrics.stability_score', "analysis['advanced_stats']['efficiency_metrics']['stability_score']"),
        ('analysis.advanced_stats.efficiency_metrics.predictability_score', "analysis['advanced_stats']['efficiency_metrics']['predictability_score']"),
        ('analysis.advanced_stats.efficiency_metrics.overall_score', "analysis['advanced_stats']['efficiency_metrics']['overall_score']"),
        
        # Cost analysis - ces propriétés n'existent pas, les remplacer par des valeurs correctes
        ('analysis.cost_analysis.current_period.total_cost', "analysis['cost_analysis']['total_cost']"),
        ('analysis.cost_analysis.current_period.cost_per_day', "analysis['cost_analysis']['average_daily_cost']"),
        ('analysis.cost_analysis.current_period.base_cost', "analysis['cost_analysis']['cost_breakdown']['consommation_base']"),
        ('analysis.cost_analysis.current_period.peak_surcharge', "analysis['cost_analysis']['cost_breakdown']['pics_consommation']"),
        ('analysis.cost_analysis.annual_projection.estimated_cost', "analysis['cost_analysis']['annual_projection']"),
        ('analysis.cost_analysis.annual_projection.potential_savings', "analysis['cost_analysis']['potential_savings']['total_savings']"),
        ('analysis.cost_analysis.annual_projection.estimated_consumption', "(analysis['basic_stats']['avg_consumption'] * 365)"),
        ('analysis.cost_analysis.cost_breakdown.energy_cost', "analysis['cost_analysis']['cost_breakdown']['consommation_base']"),
        ('analysis.cost_analysis.cost_breakdown.peak_penalties', "analysis['cost_analysis']['cost_breakdown']['pics_consommation']"),
        ('analysis.cost_analysis.cost_breakdown.estimated_grid_fees', "(analysis['cost_analysis']['total_cost'] * 0.3)"),
        ('analysis.cost_analysis.cost_breakdown.taxes', "(analysis['cost_analysis']['total_cost'] * 0.2)"),
        
        # Environmental impact
        ('analysis.environmental_impact.co2_emissions.annual_projection', "analysis['environmental_impact']['annual_co2_projection']"),
        ('analysis.environmental_impact.environmental_rating', "analysis['environmental_impact']['environmental_rating']"),
    ]
    
    # Appliquer les remplacements
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Sauvegarder
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Template corrigé !")

if __name__ == '__main__':
    fix_template()

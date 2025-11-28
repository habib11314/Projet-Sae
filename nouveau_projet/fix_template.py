#!/usr/bin/env python3
"""
Script pour corriger automatiquement toutes les références d'attributs en notation bracket
"""

import re

def fix_template():
    template_path = "templates/dashboard_advanced.html"
    
    # Lire le fichier
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacements spécifiques pour billing_analysis
    replacements = [
        ('analysis.billing_analysis.total_cost', "analysis['billing_analysis']['total_cost']"),
        ('analysis.billing_analysis.avg_daily_cost', "analysis['billing_analysis']['avg_daily_cost']"),
        ('analysis.billing_analysis.projected_monthly', "analysis['billing_analysis']['projected_monthly']"),
        ('analysis.billing_analysis.projected_yearly', "analysis['billing_analysis']['projected_yearly']"),
        ('analysis.billing_analysis.cost_variability', "analysis['billing_analysis']['cost_variability']"),
        ('analysis.billing_analysis.cost_efficiency', "analysis['billing_analysis']['cost_efficiency']"),
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

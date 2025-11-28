"""
Test rapide pour EnergyInsight Business
"""
import sys
import os

print("=" * 60)
print("     TEST ENERGYINSIGHT BUSINESS")
print("=" * 60)
print()

# Test 1: Vérifier les modules requis
print("1. Vérification des modules requis...")
required_modules = [
    'flask', 'pandas', 'numpy', 'plotly', 'reportlab'
]

missing_modules = []
for module in required_modules:
    try:
        __import__(module)
        print(f"   ✓ {module}")
    except ImportError:
        print(f"   ✗ {module} - MANQUANT")
        missing_modules.append(module)

if missing_modules:
    print(f"\nModules manquants: {', '.join(missing_modules)}")
    print("Installation: pip install " + " ".join(missing_modules))
    sys.exit(1)

# Test 2: Vérifier les fichiers requis
print("\n2. Vérification des fichiers...")
required_files = [
    'app_business.py',
    'templates/dashboard_business.html',
    'templates/upload.html',
    'templates/index.html',
    'exemple_donnees_conso_entreprise.csv'
]

missing_files = []
for file in required_files:
    if os.path.exists(file):
        print(f"   ✓ {file}")
    else:
        print(f"   ✗ {file} - MANQUANT")
        missing_files.append(file)

if missing_files:
    print(f"\nFichiers manquants: {', '.join(missing_files)}")
    sys.exit(1)

# Test 3: Test de l'analyse business
print("\n3. Test de l'analyse business...")
try:
    import pandas as pd
    from app_business import analyze_business_data
    
    # Charger les données d'exemple
    df = pd.read_csv('exemple_donnees_conso_entreprise.csv')
    print(f"   ✓ Données chargées: {len(df)} lignes")
    
    # Analyser les données
    analysis = analyze_business_data(df)
    print(f"   ✓ Analyse terminée")
    
    # Vérifier les résultats
    if 'error' in analysis:
        print(f"   ✗ Erreur d'analyse: {analysis['error']}")
        sys.exit(1)
    
    print(f"   ✓ Score d'efficacité: {analysis['efficiency_score']['score']}/100")
    print(f"   ✓ Format détecté: {analysis['data_format']}")
    print(f"   ✓ Économies potentielles: {analysis['economic_projections']['annual_savings_potential']:.0f}€")
    
except Exception as e:
    print(f"   ✗ Erreur lors du test: {e}")
    sys.exit(1)

# Test 4: Test de génération de graphiques
print("\n4. Test de génération de graphiques...")
try:
    from app_business import create_business_charts
    
    charts = create_business_charts(df, analysis)
    print(f"   ✓ Graphiques générés: {len([c for c in charts.values() if c])} graphiques")
    
except Exception as e:
    print(f"   ✗ Erreur lors de la génération: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("     TOUS LES TESTS SONT RÉUSSIS ! ✅")
print("=" * 60)
print()
print("L'application EnergyInsight Business est prête à être utilisée.")
print("Lancez 'start_business.bat' ou 'python app_business.py' pour démarrer.")
print()
print("Fonctionnalités disponibles:")
print("   🔍 Analyse automatisée des pics anormaux")
print("   📊 Projections économiques détaillées")
print("   📅 Vue par période (HP/HC, zones, saisons)")
print("   🧾 Rapport PDF avec potentiel d'économies")
print("   🎯 Objectifs de réduction & plan d'action")
print("   📥 Import CSV/Excel de factures entreprise")
print()

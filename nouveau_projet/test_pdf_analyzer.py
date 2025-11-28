#!/usr/bin/env python3
"""
StatEnergie - Script de test pour l'analyse de factures PDF
"""

import os
import sys
from pdf_bill_analyzer import PDFBillAnalyzer
import pandas as pd

def main():
    """Test d'analyse d'un fichier PDF de facture"""
    print("=== Test d'analyse de facture PDF pour StatEnergie ===")
    
    # Vérifie si un chemin de fichier PDF est fourni en argument
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        # Cherche un fichier PDF d'exemple dans le dossier actuel
        pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
        if pdf_files:
            pdf_file = pdf_files[0]
            print(f"Utilisation du fichier PDF trouvé: {pdf_file}")
        else:
            print("ERREUR: Aucun fichier PDF trouvé. Veuillez fournir un chemin en argument.")
            print("Usage: python test_pdf_analyzer.py chemin/vers/facture.pdf")
            return
    
    # Vérifie que le fichier existe
    if not os.path.isfile(pdf_file):
        print(f"ERREUR: Le fichier {pdf_file} n'existe pas.")
        return
    
    try:
        print(f"Analyse du fichier: {pdf_file}")
        print("-" * 50)
        
        # Initialise l'analyseur de PDF
        pdf_analyzer = PDFBillAnalyzer()
        
        # Vérifie si les bibliothèques sont disponibles
        if not pdf_analyzer.can_process_pdf():
            print("ERREUR: Les bibliothèques nécessaires ne sont pas disponibles.")
            return
        
        # Traite le fichier PDF
        print("Traitement du fichier PDF...")
        bill_data = pdf_analyzer.process_pdf_bill(pdf_file)
        
        if "error" in bill_data:
            print(f"ERREUR: {bill_data['error']}")
            return
        
        # Affiche les données extraites
        print("\nDonnées extraites de la facture:")
        print("-" * 50)
        for key, value in bill_data.items():
            print(f"{key}: {value}")
        
        # Crée un DataFrame
        print("\nCréation du DataFrame...")
        df = pdf_analyzer.create_dataframe_from_bill(bill_data)
        
        if df is not None and not df.empty:
            print("\nAperçu du DataFrame créé:")
            print("-" * 50)
            print(df)
            
            # Enregistre le DataFrame en CSV pour test
            csv_file = pdf_file.replace('.pdf', '_extracted.csv')
            df.to_csv(csv_file, index=False)
            print(f"\nDonnées enregistrées dans: {csv_file}")
        else:
            print("ERREUR: Impossible de créer un DataFrame valide.")
            
    except Exception as e:
        print(f"ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

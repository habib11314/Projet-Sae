#!/usr/bin/env python3
"""
Test du module d'analyse de factures PDF amélioré
Ce script teste l'extraction de données à partir d'une facture PDF
"""

from pdf_bill_analyzer import PDFBillAnalyzer
import sys
import os

def test_pdf_extraction(file_path, extraction_mode="standard"):
    """Teste l'extraction de données d'une facture PDF"""
    print(f"=== TEST D'EXTRACTION PDF ===")
    print(f"Fichier: {file_path}")
    print(f"Mode: {extraction_mode}")
    print(f"===========================")
    
    if not os.path.exists(file_path):
        print(f"ERREUR: Le fichier {file_path} n'existe pas")
        return
    
    # Créer l'analyseur
    analyzer = PDFBillAnalyzer()
    
    # Vérifier que les bibliothèques sont disponibles
    if not analyzer.can_process_pdf():
        print("Les bibliothèques pour traiter les PDF ne sont pas disponibles")
        return
    
    # Options d'extraction
    options = {
        "extraction_mode": extraction_mode,
        "extract_tables": True,
        "debug_mode": True
    }
    
    # Extraire les données
    print("Extraction des données...")
    result = analyzer.process_pdf_bill(file_path, options)
    
    # Afficher les résultats
    if "error" in result:
        print(f"ERREUR: {result['error']}")
        if "debug_info" in result:
            print("\nStatistiques d'extraction:")
            for key, value in result["debug_info"].items():
                if key != "full_text" and key != "text_sample":
                    print(f"- {key}: {value}")
        
        print("\nTexte extrait (extrait):")
        debug_text = analyzer.get_debug_text()
        print(debug_text[:500] + "..." if len(debug_text) > 500 else debug_text)
    else:
        print("\nRésultat de l'extraction:")
        for key, value in result.items():
            if key != "debug_info":
                print(f"- {key}: {value}")
        
        if "debug_info" in result:
            print("\nStatistiques d'extraction:")
            print(f"- Méthode: {result['debug_info'].get('extraction_stats', {}).get('method', 'Inconnue')}")
            print(f"- Pages: {result['debug_info'].get('extraction_stats', {}).get('pages', 0)}")
            print(f"- Taille du texte: {result['debug_info'].get('text_length', 0)} caractères")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    # Utiliser le fichier spécifié en argument ou la facture exemple par défaut
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "facture_test.pdf"
    
    # Utiliser le mode spécifié en argument ou standard par défaut
    mode = sys.argv[2] if len(sys.argv) > 2 else "standard"
    
    test_pdf_extraction(file_path, mode)

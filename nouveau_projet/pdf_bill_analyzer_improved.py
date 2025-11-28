"""
EnergyInsight - Module d'analyse de factures PDF amélioré
Ce module extrait les données pertinentes des factures énergétiques en PDF
avec une robustesse améliorée pour gérer les cas complexes.
"""

import os
import re
import pandas as pd
from datetime import datetime
import tempfile
import io
import traceback

try:
    import PyPDF2
    print("PyPDF2 importé avec succès, version:", PyPDF2.__version__)
except ImportError as e:
    print("ERREUR: Impossible d'importer PyPDF2:", str(e))
    PyPDF2 = None

try:
    import pdfplumber
    print("pdfplumber importé avec succès, version:", pdfplumber.__version__)
except ImportError as e:
    print("ERREUR: Impossible d'importer pdfplumber:", str(e))
    pdfplumber = None

class PDFBillAnalyzerImproved:
    """
    Classe améliorée pour analyser les factures énergétiques en PDF
    et en extraire les données de consommation avec une meilleure robustesse.
    """
    
    def __init__(self):
        self.supported_providers = ["EDF", "ENGIE", "TotalEnergies", "Direct Energie", "Planète OUI"]
        self.debug_info = {}
        
    def can_process_pdf(self):
        """Vérifie si les bibliothèques PDF sont disponibles"""
        pdf_ready = PyPDF2 is not None or pdfplumber is not None
        
        if not pdf_ready:
            missing_libs = []
            if PyPDF2 is None:
                missing_libs.append("PyPDF2")
            if pdfplumber is None:
                missing_libs.append("pdfplumber")
            
            print(f"ERREUR: Les bibliothèques PDF suivantes sont manquantes: {', '.join(missing_libs)}")
            print("Veuillez les installer avec: pip install PyPDF2 pdfplumber")
        
        return pdf_ready
        
    def extract_text_from_pdf(self, file_path, extraction_mode="standard"):
        """Extrait le texte brut d'un fichier PDF selon le mode d'extraction"""
        text = ""
        extraction_stats = {"method": None, "pages": 0, "success": False, "error": None}
        extraction_methods_tried = []
        
        # Essayer d'abord avec pdfplumber qui est meilleur pour l'extraction de texte formaté
        if pdfplumber is not None:
            try:
                with pdfplumber.open(file_path) as pdf:
                    extraction_stats["pages"] = len(pdf.pages)
                    extraction_methods_tried.append("pdfplumber")
                    
                    # Mode standard: extraction simple page par page
                    if extraction_mode == "standard":
                        for page in pdf.pages:
                            page_text = page.extract_text() or ""
                            text += page_text
                            
                    # Mode agressif: extraire le texte avec plusieurs méthodes
                    elif extraction_mode == "aggressive":
                        for page in pdf.pages:
                            # Extraction de texte standard
                            page_text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""
                            text += page_text
                            
                            # Extraire les tableaux et les convertir en texte
                            try:
                                tables = page.extract_tables()
                                for table in tables:
                                    for row in table:
                                        text += " ".join([str(cell or "") for cell in row]) + "\n"
                            except Exception as table_err:
                                print(f"Avertissement: Impossible d'extraire les tableaux: {table_err}")
                                
                    extraction_stats["method"] = "pdfplumber"
                    extraction_stats["success"] = True
                    
                if text:
                    return text, extraction_stats
                    
            except Exception as e:
                print(f"Erreur avec pdfplumber: {e}")
                extraction_stats["error"] = str(e)
        
        # Retomber sur PyPDF2 si nécessaire ou si le texte est vide
        if PyPDF2 is not None and not text:
            try:
                extraction_methods_tried.append("PyPDF2")
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    extraction_stats["pages"] = len(reader.pages)
                    
                    for page_num in range(len(reader.pages)):
                        page_text = reader.pages[page_num].extract_text() or ""
                        text += page_text
                        
                extraction_stats["method"] = "PyPDF2"
                extraction_stats["success"] = True
                return text, extraction_stats
                
            except Exception as e:
                print(f"Erreur avec PyPDF2: {e}")
                if extraction_stats["error"] is None:
                    extraction_stats["error"] = str(e)
        
        # Si aucun texte n'a été extrait, essayer une approche plus agressive avec pdfplumber
        if not text and pdfplumber is not None and extraction_mode != "aggressive":
            try:
                extraction_methods_tried.append("pdfplumber-last-resort")
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        # Essayer avec des paramètres de tolérance plus élevés
                        page_text = page.extract_text(x_tolerance=5, y_tolerance=7) or ""
                        text += page_text
                        
                        # Extraire tous les mots individuellement
                        words = page.extract_words(keep_blank_chars=True)
                        for word in words:
                            text += word.get('text', '') + " "
                        text += "\n"
                
                extraction_stats["method"] = "pdfplumber-aggressive"
                extraction_stats["success"] = True
            except Exception as e:
                print(f"Erreur avec la méthode de dernier recours: {e}")
        
        extraction_stats["methods_tried"] = extraction_methods_tried
        return text, extraction_stats

    def extract_tables_from_pdf(self, file_path):
        """Extrait les tableaux d'un PDF si possible"""
        tables = []
        
        if pdfplumber is not None:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_tables = page.extract_tables()
                        if page_tables:
                            tables.extend(page_tables)
            except Exception as e:
                print(f"Erreur lors de l'extraction des tableaux: {e}")
                
        return tables

    def identify_provider(self, text):
        """Identifie le fournisseur d'énergie à partir du texte"""
        # Motifs spécifiques pour les fournisseurs, y compris les variations
        provider_patterns = {
            "EDF": [r'edf', r'électricité de france', r'tarif bleu', r'heures pleines/heures creuses'],
            "ENGIE": [r'engie', r'gdf', r'gaz de france', r'dolce vita'],
            "TotalEnergies": [r'total', r'totalenergies', r'total\s*energies'],
            "Direct Energie": [r'direct\s*energie'],
            "Planète OUI": [r'planète\s*oui', r'planete\s*oui']
        }
        
        text_lower = text.lower()
        confidence_scores = {}
        
        # Vérifier chaque fournisseur
        for provider, patterns in provider_patterns.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches += 1
            
            if matches > 0:
                confidence_scores[provider] = matches / len(patterns)
        
        if confidence_scores:
            # Retourner le fournisseur avec le score de confiance le plus élevé
            return max(confidence_scores.items(), key=lambda x: x[1])[0]
                    
        return "Non identifié"
    
    def extract_bill_data(self, text, provider, extraction_mode="standard"):
        """Extrait les données de facturation selon le fournisseur et le mode d'extraction"""
        bill_data = {
            "provider": provider,
            "bill_date": None,
            "consumption_kwh": None,
            "amount": None,
            "period_start": None,
            "period_end": None,
            "client_ref": None,
            "meter_number": None,
            "extraction_confidence": {}  # Nouveau: indique la confiance pour chaque champ
        }
        
        # Si un fournisseur spécifique est identifié, utiliser des méthodes dédiées
        if extraction_mode == "provider_specific" and provider != "Non identifié":
            method_name = f"extract_{provider.lower().replace(' ', '_')}_data"
            if hasattr(self, method_name):
                # Utiliser la méthode spécifique au fournisseur
                provider_data = getattr(self, method_name)(text)
                if provider_data:
                    # Fusionner les données spécifiques au fournisseur avec les données de base
                    bill_data.update(provider_data)
                    # Marquer la confiance comme élevée pour les champs extraits avec méthode spécifique
                    for key in provider_data:
                        if key != "provider_details" and provider_data[key] is not None:
                            bill_data["extraction_confidence"][key] = "élevée"
                    return bill_data
        
        # Mode d'extraction standard ou retour au mode générique
        # Formats de dates possibles
        date_patterns = [
            r'(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})',
            r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})'
        ]
        
        # Mode agressif: plus de patterns
        if extraction_mode == "aggressive":
            date_patterns.extend([
                r'du\s+(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})\s+au\s+(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})',
                r'période\s+du\s+(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})\s+au\s+(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})',
                r'facture\s+du\s+(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})',
                r'émise\s+le\s+(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})'
            ])
        
        # Extraction des dates
        dates = []
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dates.append(match.group(0))
        
        # Si on a au moins deux dates, on suppose que ce sont les dates de début et de fin
        if len(dates) >= 2:
            bill_data["period_start"] = dates[0]
            bill_data["period_end"] = dates[1]
            bill_data["extraction_confidence"]["period"] = "moyenne"
        elif len(dates) == 1:
            bill_data["bill_date"] = dates[0]
            bill_data["extraction_confidence"]["bill_date"] = "moyenne"
        
        # Patterns pour la consommation (kWh)
        kwh_patterns = [
            r'(\d+[\.,]?\d*)\s*kwh',
            r'consommation\s*:?\s*(\d+[\.,]?\d*)',
            r'consommé\s*:?\s*(\d+[\.,]?\d*)'
        ]
        
        # Mode agressif: plus de patterns pour la consommation
        if extraction_mode == "aggressive":
            kwh_patterns.extend([
                r'total\s+consommation\s*:?\s*(\d+[\.,]?\d*)',
                r'consommation\s+relevée\s*:?\s*(\d+[\.,]?\d*)',
                r'énergie\s+active\s*:?\s*(\d+[\.,]?\d*)',
                r'consommation\s+facturée\s*:?\s*(\d+[\.,]?\d*)',
                r'consommation\s+kwh\s*:?\s*(\d+[\.,]?\d*)',
                r'consommation\s+\(kwh\)\s*:?\s*(\d+[\.,]?\d*)',
                r'total\s+énergie\s*:?\s*(\d+[\.,]?\d*)',
                r'votre\s+consommation\s*:?\s*(\d+[\.,]?\d*)',
                r'consommation\s+d\'énergie\s*:?\s*(\d+[\.,]?\d*)',
                r'consommation\s+totale\s*:?\s*(\d+[\.,]?\d*)',
                r'index.*?(\d+[\.,]?\d*)\s*kwh',
                # Patterns avec proximité de "kWh"
                r'(\d+[\.,]?\d*)\s*(?=.*?kwh)'
            ])
        
        for pattern in kwh_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace(',', '.').replace(' ', '')
                    bill_data["consumption_kwh"] = float(value_str)
                    bill_data["extraction_confidence"]["consumption_kwh"] = "moyenne" if "kwh" in pattern.lower() else "faible"
                    break
                except ValueError:
                    pass
        
        # Patterns pour le montant (€)
        amount_patterns = [
            r'montant\s*(total|ttc|ht)?\s*:?\s*(\d+[\.,]?\d*)\s*€',
            r'total\s*(ttc)?\s*:?\s*(\d+[\.,]?\d*)\s*€',
            r'à\s*payer\s*:?\s*(\d+[\.,]?\d*)\s*€',
            r'montant.*?(\d+[\.,]?\d*)\s*€',
            r'(\d+[\.,]?\d*)\s*€'  # Pattern générique pour tout montant suivi du symbole €
        ]
        
        # Mode agressif: plus de patterns pour le montant
        if extraction_mode == "aggressive":
            amount_patterns.extend([
                r'total\s+facture\s*:?\s*(\d+[\.,]?\d*)\s*€',
                r'montant\s+de\s+votre\s+facture\s*:?\s*(\d+[\.,]?\d*)\s*€',
                r'montant\s+à\s+prélever\s*:?\s*(\d+[\.,]?\d*)\s*€',
                r'prélèvement\s+de\s*:?\s*(\d+[\.,]?\d*)\s*€',
                r'facture\s+d[\'e]\s*(\d+[\.,]?\d*)\s*€',
                r'somme\s+à\s+payer\s*:?\s*(\d+[\.,]?\d*)\s*€',
                r'montant\s+prélevé\s*:?\s*(\d+[\.,]?\d*)\s*€',
                r'montant\s+ttc\s*:?\s*(\d+[\.,]?\d*)\s*€',
                # Chiffres près du symbole euro
                r'(\d+[\.,]?\d*)\s*(?=.*?€)',
                r'total.*?(\d+[\.,]?\d*)\s*€'
            ])
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Le groupe 2 contient le montant si le pattern contient "montant (total|ttc|ht)"
                    # Sinon c'est le groupe 1
                    amount_group = 2 if ("montant" in pattern and len(match.groups()) > 1) else 1
                    value_str = match.group(amount_group).replace(',', '.').replace(' ', '')
                    bill_data["amount"] = float(value_str)
                    bill_data["extraction_confidence"]["amount"] = "élevée" if "montant" in pattern.lower() or "total" in pattern.lower() else "moyenne"
                    break
                except (ValueError, IndexError):
                    pass
                    
        # Patterns pour la référence client
        client_ref_patterns = [
            r'référence\s*client\s*:?\s*(\w+[\-\s]?\d+)',
            r'client\s*n[o°]?\s*:?\s*(\w+[\-\s]?\d+)',
            r'n[o°]?\s*client\s*:?\s*(\w+[\-\s]?\d+)'
        ]
        
        # Mode agressif: plus de patterns pour la référence client
        if extraction_mode == "aggressive":
            client_ref_patterns.extend([
                r'référence\s+compte\s*:?\s*(\w+[\-\s]?\d+)',
                r'identifiant\s+client\s*:?\s*(\w+[\-\s]?\d+)',
                r'compte\s+client\s*:?\s*(\w+[\-\s]?\d+)',
                r'numéro\s+client\s*:?\s*(\w+[\-\s]?\d+)',
                r'votre\s+référence\s*:?\s*(\w+[\-\s]?\d+)',
                r'n°\s*client\s*:?\s*(\w+[\-\s]?\d+)',
                r'ref\.?\s*client\s*:?\s*(\w+[\-\s]?\d+)'
            ])
        
        for pattern in client_ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bill_data["client_ref"] = match.group(1).replace('-', '').replace(' ', '')
                    bill_data["extraction_confidence"]["client_ref"] = "élevée" if "référence" in pattern.lower() else "moyenne"
                    break
                except IndexError:
                    pass
        
        # Patterns pour le numéro de compteur
        meter_number_patterns = [
            r'numéro\s*de\s*compteur\s*:?\s*(\w+[\-\s]?\d+)',
            r'compteur\s*n[o°]?\s*:?\s*(\w+[\-\s]?\d+)',
            r'référence\s*du\s*compteur\s*:?\s*(\w+[\-\s]?\d+)'
        ]
        
        # Mode agressif: plus de patterns pour le numéro de compteur
        if extraction_mode == "aggressive":
            meter_number_patterns.extend([
                r'numéro\s+de\s+point\s+de\s+livraison\s*:?\s*(\w+[\-\s]?\d+)',
                r'numéro\s+PL\s*:?\s*(\w+[\-\s]?\d+)',
                r'code\s+client\s*:?\s*(\w+[\-\s]?\d+)',
                r'p[dr][lm]\s*:?\s*(\w+[\-\s]?\d+)',
                r'point\s+de\s+livraison\s*:?\s*(\w+[\-\s]?\d+)',
                r'no\s+compteur\s*:?\s*(\w+[\-\s]?\d+)'
            ])
        
        for pattern in meter_number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bill_data["meter_number"] = match.group(1).replace('-', '').replace(' ', '')
                    bill_data["extraction_confidence"]["meter_number"] = "élevée" if "compteur" in pattern.lower() else "moyenne"
                    break
                except IndexError:
                    pass
        
        # Ajouter des informations de confiance globale
        bill_data["global_confidence"] = self._calculate_global_confidence(bill_data)
        
        return bill_data
    
    def _calculate_global_confidence(self, bill_data):
        """Calcule un score de confiance global pour l'extraction"""
        confidence = {
            "élevée": 3,
            "moyenne": 2,
            "faible": 1
        }
        
        # Calculer le score moyen de confiance
        total_score = 0
        count = 0
        
        for field, level in bill_data.get("extraction_confidence", {}).items():
            if level in confidence:
                total_score += confidence[level]
                count += 1
        
        # Vérifier si les champs critiques sont présents
        has_consumption = bill_data.get("consumption_kwh") is not None
        has_amount = bill_data.get("amount") is not None
        has_period = bill_data.get("period_start") is not None and bill_data.get("period_end") is not None
        
        if count == 0:
            return "inconnue"
        
        avg_score = total_score / count
        
        # Niveau de confiance basé sur le score moyen et la présence des champs critiques
        if avg_score > 2.5 and has_consumption and has_amount:
            return "élevée"
        elif avg_score > 1.5 and (has_consumption or has_amount):
            return "moyenne"
        else:
            return "faible"
    
    def process_pdf_bill(self, file_path, options=None):
        """Traite une facture PDF et extrait les données pertinentes"""
        if not self.can_process_pdf():
            return {"error": "Bibliothèques PDF manquantes. Veuillez installer PyPDF2 et pdfplumber."}
        
        # Options par défaut
        default_options = {
            "extraction_mode": "standard",
            "extract_tables": False,
            "debug_mode": False,
            "specific_provider": None,
            "retry_on_failure": True  # Nouvelle option
        }
        
        # Fusionner avec les options fournies
        if options is None:
            options = default_options
        else:
            for key, value in default_options.items():
                if key not in options:
                    options[key] = value
        
        # Réinitialiser les informations de debug
        self.debug_info = {
            "extraction_stats": None,
            "identified_provider": None,
            "extraction_mode": options["extraction_mode"],
            "tables_extracted": 0,
            "patterns_matched": {},
            "extraction_process": [],
            "text_length": 0,
            "text_sample": "",
            "retry_attempts": 0
        }
        
        try:
            # 1. Extraire le texte du PDF
            text, extraction_stats = self.extract_text_from_pdf(file_path, options["extraction_mode"])
            self.debug_info["extraction_stats"] = extraction_stats
            self.debug_info["extraction_process"].append(f"Extraction de texte: {len(text)} caractères")
            self.debug_info["text_length"] = len(text)
            
            # Stocker un échantillon du texte extrait
            if text:
                self.debug_info["text_sample"] = text[:500] + "..." if len(text) > 500 else text
            
            # Si le texte extrait est vide ou très court et que retry_on_failure est activé
            if (not text or len(text) < 50) and options["retry_on_failure"]:
                self.debug_info["retry_attempts"] += 1
                self.debug_info["extraction_process"].append("Texte extrait insuffisant, tentative avec mode agressif")
                
                # Réessayer avec le mode agressif
                text, extraction_stats = self.extract_text_from_pdf(file_path, "aggressive")
                self.debug_info["extraction_stats"] = extraction_stats
                self.debug_info["extraction_process"].append(f"Nouvelle extraction: {len(text)} caractères")
                self.debug_info["text_length"] = len(text)
                
                if text:
                    self.debug_info["text_sample"] = text[:500] + "..." if len(text) > 500 else text
                    options["extraction_mode"] = "aggressive"  # Passer en mode agressif pour la suite
            
            # Si toujours pas de texte exploitable
            if not text or len(text) < 20:
                return {
                    "error": "Impossible d'extraire du texte du PDF. Le fichier pourrait être protégé, scanné ou corrompu.",
                    "debug_info": self.debug_info
                }
            
            # 2. Identifier le fournisseur
            provider = options.get("specific_provider") or self.identify_provider(text)
            self.debug_info["identified_provider"] = provider
            self.debug_info["extraction_process"].append(f"Fournisseur identifié: {provider}")
            
            # 3. Extraire les données de facturation
            bill_data = self.extract_bill_data(text, provider, options["extraction_mode"])
            
            # 4. Si extraction échouée et retry_on_failure est activé
            if options["retry_on_failure"] and (
                bill_data.get("consumption_kwh") is None and 
                bill_data.get("amount") is None and 
                bill_data.get("retry_attempts", 0) < 2
            ):
                self.debug_info["retry_attempts"] += 1
                self.debug_info["extraction_process"].append(f"Extraction échouée, tentative avec mode {options['extraction_mode'] if options['extraction_mode'] != 'aggressive' else 'provider_specific'}")
                
                # Si déjà en mode agressif, essayer le mode spécifique au fournisseur
                new_mode = "provider_specific" if options["extraction_mode"] == "aggressive" else "aggressive"
                bill_data = self.extract_bill_data(text, provider, new_mode)
                bill_data["retry_attempts"] = self.debug_info["retry_attempts"]
            
            # 5. Extraire les tableaux si demandé
            if options["extract_tables"]:
                tables = self.extract_tables_from_pdf(file_path)
                self.debug_info["tables_extracted"] = len(tables)
                self.debug_info["extraction_process"].append(f"Tableaux extraits: {len(tables)}")
                
                # Ajouter les tableaux aux données
                if tables:
                    bill_data["tables"] = tables
                    
                    # Si pas de consommation détectée, tenter de l'extraire des tableaux
                    if bill_data.get("consumption_kwh") is None:
                        consumption = self._extract_consumption_from_tables(tables)
                        if consumption is not None:
                            bill_data["consumption_kwh"] = consumption
                            bill_data["extraction_confidence"]["consumption_kwh"] = "moyenne"
                            self.debug_info["extraction_process"].append(f"Consommation extraite des tableaux: {consumption} kWh")
            
            # 6. Ajouter les informations de debug
            if options["debug_mode"]:
                bill_data["debug_info"] = self.debug_info
            
            return bill_data
            
        except Exception as e:
            error_message = f"Erreur lors de l'analyse de la facture PDF: {str(e)}"
            traceback_info = traceback.format_exc()
            print(error_message)
            print(traceback_info)
            
            return {
                "error": error_message,
                "traceback": traceback_info,
                "debug_info": self.debug_info if options["debug_mode"] else None
            }
    
    def _extract_consumption_from_tables(self, tables):
        """Tente d'extraire la consommation des tableaux"""
        for table in tables:
            for row in table:
                for i, cell in enumerate(row):
                    # Ignorer les cellules vides
                    if not cell:
                        continue
                        
                    cell_str = str(cell).lower()
                    # Chercher des cellules contenant des mots-clés de consommation
                    if "consommation" in cell_str or "kwh" in cell_str or "kw h" in cell_str:
                        # Chercher des valeurs numériques dans cette ligne
                        for j, potential_value in enumerate(row):
                            if j != i and potential_value:  # Ignorer la cellule actuelle
                                try:
                                    # Nettoyer et convertir la valeur
                                    value_str = str(potential_value).replace(' ', '').replace(',', '.')
                                    # Extraire juste le nombre
                                    value_match = re.search(r'(\d+[,.]\d+|\d+)', value_str)
                                    if value_match:
                                        return float(value_match.group(1))
                                except (ValueError, TypeError):
                                    continue
        return None
    
    def extract_engie_data(self, text):
        """Extrait les données spécifiques des factures ENGIE"""
        data = {}
        self.debug_info["extraction_process"].append("Utilisation de l'extracteur spécifique ENGIE")
        
        # Période de facturation ENGIE
        period_pattern = r'(?:Période|Du)[\s:]+([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})\s+(?:au|à)\s+([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})'
        period_match = re.search(period_pattern, text, re.IGNORECASE)
        if period_match:
            data["period_start"] = period_match.group(1)
            data["period_end"] = period_match.group(2)
            self.debug_info["patterns_matched"]["period"] = True
        
        # Consommation kWh ENGIE - patterns étendus
        kwh_patterns = [
            r'(?:Consommation|Conso\.?|Total consommé)[\s:]+([\d\s]+[,.]\d*)\s*(?:kWh)',
            r'([\d\s]+[,.]\d*)\s*kWh(?:\s+consommés)',
            r'Consommation facturée[\s:]+([\d\s]+[,.]\d*)',
            r'Énergie facturée.*?([\d\s]+[,.]\d*)\s*kWh',
            r'Total.*?énergie.*?([\d\s]+[,.]\d*)\s*kWh',
            r'Consommation mesurée[\s:]+([\d\s]+[,.]\d*)',
            r'Quantité facturée[\s:]+([\d\s]+[,.]\d*)'
        ]
        
        for pattern in kwh_patterns:
            kwh_match = re.search(pattern, text, re.IGNORECASE)
            if kwh_match:
                try:
                    consumption = kwh_match.group(1).replace(' ', '').replace(',', '.')
                    data["consumption_kwh"] = float(consumption)
                    self.debug_info["patterns_matched"]["consumption"] = True
                    break
                except (ValueError, IndexError):
                    pass
        
        # Montant TTC ENGIE - patterns étendus
        amount_patterns = [
            r'(?:Montant|Total)(?:\s+à payer)?(?:\s+TTC)?[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:Montant|Total)(?:\s+de la facture)[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:somme|montant)(?:\s+à régler)[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'À payer[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'Montant prélevé[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'Solde[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:TTC|Total toutes taxes)[\s:]+([\d\s]+[,.]\d*)\s*€'
        ]
        
        for pattern in amount_patterns:
            amount_match = re.search(pattern, text, re.IGNORECASE)
            if amount_match:
                try:
                    amount = amount_match.group(1).replace(' ', '').replace(',', '.')
                    data["amount"] = float(amount)
                    self.debug_info["patterns_matched"]["amount"] = True
                    break
                except (ValueError, IndexError):
                    pass
        
        # Référence client ENGIE - patterns étendus
        ref_patterns = [
            r'(?:Référence|N°|Numéro)(?:\s+client|compte)[\s:]+([\w\d\s\-]+)',
            r'(?:Client|Compte)(?:\s+n°|numéro)[\s:]+([\w\d\s\-]+)',
            r'Votre référence[\s:]+([\w\d\s\-]+)',
            r'PCE[\s:]+([\w\d\s\-]+)',
            r'Référence contractuelle[\s:]+([\w\d\s\-]+)',
            r'Réf\.?[\s:]+([\w\d\s\-]+)'
        ]
        
        for pattern in ref_patterns:
            ref_match = re.search(pattern, text, re.IGNORECASE)
            if ref_match:
                data["client_ref"] = ref_match.group(1).strip()
                self.debug_info["patterns_matched"]["client_ref"] = True
                break
        
        # N° de compteur ENGIE - patterns étendus
        meter_patterns = [
            r'(?:Compteur|Point de livraison|PDL|PRM)[\s:]+([\w\d\s\-]+)',
            r'(?:N°|Numéro)(?:\s+de compteur)[\s:]+([\w\d\s\-]+)',
            r'PCE[\s:]+([\w\d\s\-]+)',
            r'Identifiant du compteur[\s:]+([\w\d\s\-]+)',
            r'Référence technique[\s:]+([\w\d\s\-]+)',
            r'N° de compteur[\s:]+([\w\d\s\-]+)'
        ]
        
        for pattern in meter_patterns:
            meter_match = re.search(pattern, text, re.IGNORECASE)
            if meter_match:
                data["meter_number"] = meter_match.group(1).strip()
                self.debug_info["patterns_matched"]["meter_number"] = True
                break
        
        # Adresse de consommation - patterns étendus
        address_pattern = r'(?:Adresse|Lieu)(?:\s+de consommation|du site)[\s:]+([\w\d\s,\-\'\.]+)'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            data["consumption_address"] = address_match.group(1).strip()
            self.debug_info["patterns_matched"]["address"] = True
        
        # Informations supplémentaires pour ENGIE
        data["provider_details"] = {
            "name": "ENGIE",
            "type": self._detect_energy_type(text)
        }
        
        return data
    
    def extract_edf_data(self, text):
        """Extrait les données spécifiques des factures EDF"""
        data = {}
        self.debug_info["extraction_process"].append("Utilisation de l'extracteur spécifique EDF")
        
        # Période de facturation EDF - patterns étendus
        period_patterns = [
            r'(?:Période|Du)[\s:]+([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})\s+(?:au|à)\s+([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})',
            r'(?:Relevé|Consommation)(?:\s+du|entre)(?:\s+|:)([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})(?:\s+|\s+et\s+|\s+au\s+)([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})',
            r'(?:facturé|facturation)(?:\s+du|entre)(?:\s+|:)([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})(?:\s+|\s+et\s+|\s+au\s+)([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})'
        ]
        
        for pattern in period_patterns:
            period_match = re.search(pattern, text, re.IGNORECASE)
            if period_match:
                data["period_start"] = period_match.group(1)
                data["period_end"] = period_match.group(2)
                self.debug_info["patterns_matched"]["period"] = True
                break
        
        # Consommation kWh EDF - patterns étendus
        kwh_patterns = [
            r'(?:Consommation|Conso\.?)(?:\s+totale)?[\s:]+([\d\s]+[,.]\d*)\s*(?:kWh)',
            r'([\d\s]+[,.]\d*)\s*kWh(?:\s+consommés)',
            r'(?:Total|Électricité)(?:\s+consommée)[\s:]+([\d\s]+[,.]\d*)',
            r'Consommation facturée[\s:]+([\d\s]+[,.]\d*)',
            r'Total\s+consommation(?:\s+|:)([\d\s]+[,.]\d*)',
            r'Heures (?:Pleines|Creuses)[\s:]+([\d\s]+[,.]\d*)\s*kWh',
            r'HP\s*\+\s*HC\s*=\s*([\d\s]+[,.]\d*)',
            r'consommation totale(?:\s+|:)([\d\s]+[,.]\d*)',
            r'Quantité facturée[\s:]+([\d\s]+[,.]\d*)',
            r'Total de vos consommations[\s:]+([\d\s]+[,.]\d*)'
        ]
        
        for pattern in kwh_patterns:
            kwh_match = re.search(pattern, text, re.IGNORECASE)
            if kwh_match:
                try:
                    consumption = kwh_match.group(1).replace(' ', '').replace(',', '.')
                    data["consumption_kwh"] = float(consumption)
                    self.debug_info["patterns_matched"]["consumption"] = True
                    break
                except (ValueError, IndexError):
                    pass
        
        # Montant TTC EDF - patterns étendus
        amount_patterns = [
            r'(?:Montant|Total)(?:\s+à payer)?(?:\s+TTC)?[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:Montant|Total)(?:\s+de la facture)[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:somme|montant)(?:\s+à régler)[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:Prélèvement|Montant prélevé)(?:\s+de)[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'Montant total TTC[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'Total de votre facture[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'À payer[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'Facturé[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'Votre règlement[\s:]+([\d\s]+[,.]\d*)\s*€'
        ]
        
        for pattern in amount_patterns:
            amount_match = re.search(pattern, text, re.IGNORECASE)
            if amount_match:
                try:
                    amount = amount_match.group(1).replace(' ', '').replace(',', '.')
                    data["amount"] = float(amount)
                    self.debug_info["patterns_matched"]["amount"] = True
                    break
                except (ValueError, IndexError):
                    pass
        
        # Référence client EDF - patterns étendus
        ref_patterns = [
            r'(?:Référence|N°|Numéro)(?:\s+client)[\s:]+([\w\d\s\-]+)',
            r'(?:Client)(?:\s+n°|numéro)[\s:]+([\w\d\s\-]+)',
            r'Compte EDF[\s:]+([\w\d\s\-]+)',
            r'N° compte[\s:]+([\w\d\s\-]+)',
            r'Identifiant client[\s:]+([\w\d\s\-]+)',
            r'Votre référence[\s:]+([\w\d\s\-]+)'
        ]
        
        for pattern in ref_patterns:
            ref_match = re.search(pattern, text, re.IGNORECASE)
            if ref_match:
                data["client_ref"] = ref_match.group(1).strip()
                self.debug_info["patterns_matched"]["client_ref"] = True
                break
        
        # N° de compteur ou PRM/PDL EDF - patterns étendus
        meter_patterns = [
            r'(?:PRM|PDL|Point de livraison)[\s:]+([\w\d\s\-]+)',
            r'(?:N°|Numéro)(?:\s+de compteur)[\s:]+([\w\d\s\-]+)',
            r'Compteur[\s:]+([\w\d\s\-]+)',
            r'Référence acheminement[\s:]+([\w\d\s\-]+)',
            r'N° d\'identification[\s:]+([\w\d\s\-]+)',
            r'PRM :[\s:]+([\w\d\s\-]+)'
        ]
        
        for pattern in meter_patterns:
            meter_match = re.search(pattern, text, re.IGNORECASE)
            if meter_match:
                data["meter_number"] = meter_match.group(1).strip()
                self.debug_info["patterns_matched"]["meter_number"] = True
                break
        
        # Adresse de consommation - patterns étendus
        address_patterns = [
            r'(?:Adresse|Lieu)(?:\s+de consommation|du site)[\s:]+([\w\d\s,\-\'\.]+)',
            r'(?:Site|Local)(?:\s+de consommation)[\s:]+([\w\d\s,\-\'\.]+)',
            r'Adresse desservie[\s:]+([\w\d\s,\-\'\.]+)'
        ]
        
        for pattern in address_patterns:
            address_match = re.search(pattern, text, re.IGNORECASE)
            if address_match:
                data["consumption_address"] = address_match.group(1).strip()
                self.debug_info["patterns_matched"]["address"] = True
                break
        
        # Informations supplémentaires pour EDF
        data["provider_details"] = {
            "name": "EDF",
            "type": "Électricité"  # EDF fournit principalement de l'électricité
        }
        
        return data
    
    def _detect_energy_type(self, text):
        """Détecte le type d'énergie mentionné dans le texte"""
        text_lower = text.lower()
        
        # Patterns pour l'électricité
        elec_patterns = [r'[ée]lectricit[ée]', r'kwh', r'kw h', r'heures? pleines?', r'heures? creuses?', r'hp/hc']
        gas_patterns = [r'gaz', r'm3', r'mètre cube', r'pcs', r'pouvoir calorifique']
        
        elec_matches = sum(1 for pattern in elec_patterns if re.search(pattern, text_lower))
        gas_matches = sum(1 for pattern in gas_patterns if re.search(pattern, text_lower))
        
        if elec_matches > gas_matches:
            return "Électricité"
        elif gas_matches > elec_matches:
            return "Gaz"
        elif elec_matches > 0:
            return "Électricité"
        elif gas_matches > 0:
            return "Gaz"
        else:
            return "Non spécifié"
    
    def get_debug_text(self):
        """Renvoie un texte formaté avec les informations de debug"""
        if not self.debug_info:
            return "Aucune information de diagnostic disponible."
            
        debug_text = "=== INFORMATIONS DE DIAGNOSTIC ===\n\n"
        
        # Informations d'extraction
        if "extraction_stats" in self.debug_info and self.debug_info["extraction_stats"]:
            stats = self.debug_info["extraction_stats"]
            debug_text += f"Méthode d'extraction: {stats.get('method', 'Non spécifiée')}\n"
            debug_text += f"Pages traitées: {stats.get('pages', 0)}\n"
            debug_text += f"Succès: {stats.get('success', False)}\n"
            if stats.get('error'):
                debug_text += f"Erreur: {stats.get('error')}\n"
            if 'methods_tried' in stats:
                debug_text += f"Méthodes essayées: {', '.join(stats['methods_tried'])}\n"
            debug_text += "\n"
        
        # Fournisseur identifié
        debug_text += f"Fournisseur détecté: {self.debug_info.get('identified_provider', 'Non identifié')}\n"
        debug_text += f"Mode d'extraction: {self.debug_info.get('extraction_mode', 'standard')}\n"
        debug_text += f"Tableaux extraits: {self.debug_info.get('tables_extracted', 0)}\n"
        debug_text += f"Tentatives d'extraction: {self.debug_info.get('retry_attempts', 0)}\n"
        debug_text += f"Caractères extraits: {self.debug_info.get('text_length', 0)}\n\n"
        
        # Patterns correspondants
        patterns_matched = self.debug_info.get("patterns_matched", {})
        debug_text += "Patterns détectés:\n"
        for pattern_name, matched in patterns_matched.items():
            debug_text += f"- {pattern_name}: {'✓' if matched else '✗'}\n"
        debug_text += "\n"
        
        # Processus d'extraction
        process_steps = self.debug_info.get("extraction_process", [])
        if process_steps:
            debug_text += "Étapes d'extraction:\n"
            for i, step in enumerate(process_steps, 1):
                debug_text += f"{i}. {step}\n"
                
        # Échantillon de texte
        if self.debug_info.get("text_sample"):
            debug_text += "\nÉchantillon du texte extrait:\n"
            debug_text += "---------------------------------\n"
            debug_text += self.debug_info.get("text_sample", "")
            debug_text += "\n---------------------------------\n"
        
        return debug_text
    
    def create_dataframe_from_bill(self, bill_data):
        """Crée un DataFrame à partir des données de facturation extraites"""
        if "error" in bill_data:
            return None
            
        # Données de base pour le DataFrame
        data = {
            "provider": [bill_data.get("provider", "Non spécifié")],
            "bill_date": [bill_data.get("bill_date", None)],
            "consumption_kwh": [bill_data.get("consumption_kwh", None)],
            "amount": [bill_data.get("amount", None)],
            "period_start": [bill_data.get("period_start", None)],
            "period_end": [bill_data.get("period_end", None)],
            "client_ref": [bill_data.get("client_ref", None)],
            "meter_number": [bill_data.get("meter_number", None)],
        }
        
        # Ajouter l'adresse de consommation si disponible
        if "consumption_address" in bill_data:
            data["consumption_address"] = [bill_data.get("consumption_address")]
        
        # Ajouter le type d'énergie si disponible
        if "provider_details" in bill_data and "type" in bill_data["provider_details"]:
            data["energy_type"] = [bill_data["provider_details"]["type"]]
            
        # Ajouter la confiance globale
        if "global_confidence" in bill_data:
            data["extraction_confidence"] = [bill_data["global_confidence"]]
        
        # Créer le DataFrame
        df = pd.DataFrame(data)
        
        # Si le DataFrame est vide ou ne contient pas de données utiles
        if df.empty or df["consumption_kwh"].isnull().all() and df["amount"].isnull().all():
            return None
        
        return df

"""
Fonctions d'aide pour intégrer l'analyseur PDF amélioré
"""

def analyze_pdf_file(file_path, options=None):
    """
    Analyse un fichier PDF de facture avec options avancées
    
    Args:
        file_path (str): Chemin du fichier PDF
        options (dict): Options d'extraction (mode, debug, etc.)
        
    Returns:
        dict: Données extraites de la facture
    """
    analyzer = PDFBillAnalyzerImproved()
    
    if options is None:
        options = {
            "extraction_mode": "standard",
            "extract_tables": True,
            "debug_mode": True,
            "retry_on_failure": True
        }
    
    return analyzer.process_pdf_bill(file_path, options)

def compare_extraction_results(file_path):
    """
    Compare les résultats des méthodes d'extraction standard et améliorée
    
    Args:
        file_path (str): Chemin du fichier PDF
        
    Returns:
        dict: Comparaison des résultats
    """
    standard_analyzer = PDFBillAnalyzer()
    improved_analyzer = PDFBillAnalyzerImproved()
    
    # Extraire avec les deux analyseurs
    standard_result = standard_analyzer.process_pdf_bill(file_path, {
        "extraction_mode": "standard",
        "debug_mode": True
    })
    
    improved_result = improved_analyzer.process_pdf_bill(file_path, {
        "extraction_mode": "standard",
        "extract_tables": True,
        "debug_mode": True,
        "retry_on_failure": True
    })
    
    # Comparer les résultats
    comparison = {
        "standard": {k: v for k, v in standard_result.items() if k != "debug_info"},
        "improved": {k: v for k, v in improved_result.items() if k != "debug_info"},
        "fields_found": {
            "standard": sum(1 for k, v in standard_result.items() 
                          if k not in ["debug_info", "error", "traceback", "provider"] and v is not None),
            "improved": sum(1 for k, v in improved_result.items() 
                          if k not in ["debug_info", "error", "traceback", "provider", "extraction_confidence", "global_confidence"] and v is not None)
        },
        "has_error": {
            "standard": "error" in standard_result,
            "improved": "error" in improved_result
        }
    }
    
    return comparison

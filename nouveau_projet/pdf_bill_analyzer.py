"""
StatEnergie - Module d'analyse de factures PDF
Ce module extrait les données pertinentes des factures énergétiques en PDF
pour les intégrer dans l'analyse de consommation.
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

class PDFBillAnalyzer:
    """
    Classe pour analyser les factures énergétiques en PDF
    et en extraire les données de consommation.
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
        
        # Essayer d'abord avec pdfplumber qui est meilleur pour l'extraction de texte formaté
        if pdfplumber is not None:
            try:
                with pdfplumber.open(file_path) as pdf:
                    extraction_stats["pages"] = len(pdf.pages)
                    
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
            "EDF": [r'edf', r'électricité de france', r'tarif bleu'],
            "ENGIE": [r'engie', r'gdf', r'gaz de france', r'dolce vita'],
            "TotalEnergies": [r'total', r'totalenergies', r'total\s*energies'],
            "Direct Energie": [r'direct\s*energie'],
            "Planète OUI": [r'planète\s*oui', r'planete\s*oui']
        }
        
        text_lower = text.lower()
        
        # Vérifier chaque fournisseur
        for provider, patterns in provider_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return provider
                    
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
            "meter_number": None
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
                r'consommation\s+d\'énergie\s*:?\s*(\d+[\.,]?\d*)'
            ])
        
        for pattern in kwh_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bill_data["consumption_kwh"] = float(match.group(1).replace(',', '.'))
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
                r'montant\s+prélevé\s*:?\s*(\d+[\.,]?\d*)\s*€'
            ])
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Le groupe 2 contient le montant si le pattern contient "montant (total|ttc|ht)"
                    # Sinon c'est le groupe 1
                    amount_group = 2 if ("montant" in pattern and len(match.groups()) > 1) else 1
                    bill_data["amount"] = float(match.group(amount_group).replace(',', '.'))
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
                r'votre\s+référence\s*:?\s*(\w+[\-\s]?\d+)'
            ])
        
        for pattern in client_ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bill_data["client_ref"] = match.group(1).replace('-', '').replace(' ', '')
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
                r'code\s+client\s*:?\s*(\w+[\-\s]?\d+)'
            ])
        
        for pattern in meter_number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bill_data["meter_number"] = match.group(1).replace('-', '').replace(' ', '')
                    break
                except IndexError:
                    pass
        
        return bill_data
    
    def process_pdf_bill(self, file_path, options=None):
        """Traite une facture PDF et extrait les données pertinentes"""
        if not self.can_process_pdf():
            return {"error": "Bibliothèques PDF manquantes. Veuillez installer PyPDF2 et pdfplumber."}
        
        # Options par défaut
        default_options = {
            "extraction_mode": "standard",
            "extract_tables": False,
            "debug_mode": False,
            "specific_provider": None
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
            "extraction_process": []
        }
        
        try:
            # 1. Extraire le texte du PDF
            text, extraction_stats = self.extract_text_from_pdf(file_path, options["extraction_mode"])
            self.debug_info["extraction_stats"] = extraction_stats
            self.debug_info["extraction_process"].append(f"Extraction de texte: {len(text)} caractères")
            
            # 2. Identifier le fournisseur
            provider = options.get("specific_provider") or self.identify_provider(text)
            self.debug_info["identified_provider"] = provider
            self.debug_info["extraction_process"].append(f"Fournisseur identifié: {provider}")
            
            # 3. Extraire les données de facturation
            bill_data = self.extract_bill_data(text, provider, options["extraction_mode"])
            
            # 4. Extraire les tableaux si demandé
            if options["extract_tables"]:
                tables = self.extract_tables_from_pdf(file_path)
                self.debug_info["tables_extracted"] = len(tables)
                self.debug_info["extraction_process"].append(f"Tableaux extraits: {len(tables)}")
                
                # Ajouter les tableaux aux données
                if tables:
                    bill_data["tables"] = tables
            
            # 5. Ajouter les informations de debug
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
        
        # Consommation kWh ENGIE
        kwh_patterns = [
            r'(?:Consommation|Conso\.?|Total consommé)[\s:]+([\d\s]+[,.]\d*)\s*(?:kWh)',
            r'([\d\s]+[,.]\d*)\s*kWh(?:\s+consommés)',
            r'Consommation facturée[\s:]+([\d\s]+[,.]\d*)'
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
        
        # Montant TTC ENGIE
        amount_patterns = [
            r'(?:Montant|Total)(?:\s+à payer)?(?:\s+TTC)?[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:Montant|Total)(?:\s+de la facture)[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:somme|montant)(?:\s+à régler)[\s:]+([\d\s]+[,.]\d*)\s*€'
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
        
        # Référence client ENGIE
        ref_patterns = [
            r'(?:Référence|N°|Numéro)(?:\s+client|compte)[\s:]+([\w\d\s]+)',
            r'(?:Client|Compte)(?:\s+n°|numéro)[\s:]+([\w\d\s]+)'
        ]
        
        for pattern in ref_patterns:
            ref_match = re.search(pattern, text, re.IGNORECASE)
            if ref_match:
                data["client_ref"] = ref_match.group(1).strip()
                self.debug_info["patterns_matched"]["client_ref"] = True
                break
        
        # N° de compteur ENGIE
        meter_patterns = [
            r'(?:Compteur|Point de livraison|PDL|PRM)[\s:]+([\w\d\s]+)',
            r'(?:N°|Numéro)(?:\s+de compteur)[\s:]+([\w\d\s]+)'
        ]
        
        for pattern in meter_patterns:
            meter_match = re.search(pattern, text, re.IGNORECASE)
            if meter_match:
                data["meter_number"] = meter_match.group(1).strip()
                self.debug_info["patterns_matched"]["meter_number"] = True
                break
        
        # Adresse de consommation
        address_pattern = r'(?:Adresse|Lieu)(?:\s+de consommation)[\s:]+([\w\d\s,\-]+)'
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
        
        # Période de facturation EDF
        period_pattern = r'(?:Période|Du)[\s:]+([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})\s+(?:au|à)\s+([\d]{1,2}\/[\d]{1,2}\/[\d]{2,4})'
        period_match = re.search(period_pattern, text, re.IGNORECASE)
        if period_match:
            data["period_start"] = period_match.group(1)
            data["period_end"] = period_match.group(2)
            self.debug_info["patterns_matched"]["period"] = True
        
        # Consommation kWh EDF
        kwh_patterns = [
            r'(?:Consommation|Conso\.?)(?:\s+totale)?[\s:]+([\d\s]+[,.]\d*)\s*(?:kWh)',
            r'([\d\s]+[,.]\d*)\s*kWh(?:\s+consommés)',
            r'(?:Total|Électricité)(?:\s+consommée)[\s:]+([\d\s]+[,.]\d*)'
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
        
        # Montant TTC EDF
        amount_patterns = [
            r'(?:Montant|Total)(?:\s+à payer)?(?:\s+TTC)?[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:Montant|Total)(?:\s+de la facture)[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:somme|montant)(?:\s+à régler)[\s:]+([\d\s]+[,.]\d*)\s*€',
            r'(?:Prélèvement|Montant prélevé)(?:\s+de)[\s:]+([\d\s]+[,.]\d*)\s*€'
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
        
        # Référence client EDF
        ref_patterns = [
            r'(?:Référence|N°|Numéro)(?:\s+client)[\s:]+([\w\d\s]+)',
            r'(?:Client)(?:\s+n°|numéro)[\s:]+([\w\d\s]+)'
        ]
        
        for pattern in ref_patterns:
            ref_match = re.search(pattern, text, re.IGNORECASE)
            if ref_match:
                data["client_ref"] = ref_match.group(1).strip()
                self.debug_info["patterns_matched"]["client_ref"] = True
                break
        
        # N° de compteur ou PRM/PDL EDF
        meter_patterns = [
            r'(?:PRM|PDL|Point de livraison)[\s:]+([\w\d\s]+)',
            r'(?:N°|Numéro)(?:\s+de compteur)[\s:]+([\w\d\s]+)'
        ]
        
        for pattern in meter_patterns:
            meter_match = re.search(pattern, text, re.IGNORECASE)
            if meter_match:
                data["meter_number"] = meter_match.group(1).strip()
                self.debug_info["patterns_matched"]["meter_number"] = True
                break
        
        # Adresse de consommation
        address_pattern = r'(?:Adresse|Lieu)(?:\s+de consommation)[\s:]+([\w\d\s,\-]+)'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            data["consumption_address"] = address_match.group(1).strip()
            self.debug_info["patterns_matched"]["address"] = True
        
        # Informations supplémentaires pour EDF
        data["provider_details"] = {
            "name": "EDF",
            "type": "Électricité"  # EDF fournit principalement de l'électricité
        }
        
        return data
    
    def _detect_energy_type(self, text):
        """Détecte le type d'énergie mentionné dans le texte"""
        if re.search(r'[ée]lectricit[ée]', text, re.IGNORECASE):
            return "Électricité"
        elif re.search(r'gaz', text, re.IGNORECASE):
            return "Gaz"
        else:
            return "Non spécifié"
    
    def get_debug_text(self):
        """Renvoie un texte formaté avec les informations de debug"""
        if not self.debug_info:
            return "Aucune information de debug disponible."
            
        debug_text = "=== INFORMATIONS DE DIAGNOSTIC ===\n\n"
        
        # Informations d'extraction
        if "extraction_stats" in self.debug_info and self.debug_info["extraction_stats"]:
            stats = self.debug_info["extraction_stats"]
            debug_text += f"Méthode d'extraction: {stats.get('method', 'Non spécifiée')}\n"
            debug_text += f"Pages traitées: {stats.get('pages', 0)}\n"
            debug_text += f"Succès: {stats.get('success', False)}\n"
            if stats.get('error'):
                debug_text += f"Erreur: {stats.get('error')}\n"
            debug_text += "\n"
        
        # Fournisseur identifié
        debug_text += f"Fournisseur détecté: {self.debug_info.get('identified_provider', 'Non identifié')}\n"
        debug_text += f"Mode d'extraction: {self.debug_info.get('extraction_mode', 'standard')}\n"
        debug_text += f"Tableaux extraits: {self.debug_info.get('tables_extracted', 0)}\n\n"
        
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
        
        # Créer le DataFrame
        df = pd.DataFrame(data)
        
        # Si le DataFrame est vide ou ne contient pas de données utiles
        if df.empty or df.isnull().all().all():
            return None
        
        return df

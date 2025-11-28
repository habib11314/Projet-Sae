#!/usr/bin/env python3
"""
Test d'analyse des factures PDF - EnergyInsight
Ce script démontre l'implémentation de l'analyse de factures PDF
"""

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import os
import pandas as pd
import tempfile
import uuid
from werkzeug.utils import secure_filename
from pdf_bill_analyzer import PDFBillAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pdf-analysis-test-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Stockage temporaire des résultats d'analyse PDF
pdf_analysis_results = {}

@app.route('/')
def index():
    """Page d'accueil avec bouton d'analyse PDF"""
    return render_template('pdf_analysis.html')

@app.route('/analyze-pdf', methods=['GET', 'POST'])
def analyze_pdf():
    """Analyse une facture PDF uploadée"""
    if request.method == 'POST':
        # Vérifier si un fichier a été téléchargé
        if 'pdf_file' not in request.files:
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        file = request.files['pdf_file']
        
        # Si l'utilisateur ne sélectionne pas de fichier, le navigateur envoie
        # un fichier sans nom
        if file.filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.pdf'):
            # Sauvegarder le fichier
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Analyser le PDF
            analyzer = PDFBillAnalyzer()
            result = analyzer.process_pdf_bill(file_path)
            
            # Générer un ID unique pour cette analyse
            pdf_id = str(uuid.uuid4())
            pdf_analysis_results[pdf_id] = {
                'result': result,
                'file_path': file_path
            }
            
            return render_template('pdf_analysis.html', result=result, pdf_id=pdf_id)
    
    return render_template('pdf_analysis.html')

@app.route('/analyze-sample-pdf')
def analyze_sample_pdf():
    """Analyse la facture exemple"""
    # Utiliser la facture exemple fournie
    file_path = 'facture_test.pdf'
    
    if not os.path.exists(file_path):
        flash('Facture exemple non trouvée')
        return redirect(url_for('index'))
    
    # Analyser le PDF
    analyzer = PDFBillAnalyzer()
    result = analyzer.process_pdf_bill(file_path)
    
    # Générer un ID unique pour cette analyse
    pdf_id = str(uuid.uuid4())
    pdf_analysis_results[pdf_id] = {
        'result': result,
        'file_path': file_path
    }
    
    return render_template('pdf_analysis.html', result=result, pdf_id=pdf_id)

@app.route('/export-pdf-analysis/<pdf_id>')
def export_pdf_analysis(pdf_id):
    """Exporte les résultats d'analyse au format CSV"""
    if pdf_id not in pdf_analysis_results:
        flash('Analyse non trouvée')
        return redirect(url_for('index'))
    
    result = pdf_analysis_results[pdf_id]['result']
    
    # Créer un DataFrame à partir des résultats
    analyzer = PDFBillAnalyzer()
    df = analyzer.create_dataframe_from_bill(result)
    
    if df is None:
        flash("Impossible de créer un fichier d'export")
        return redirect(url_for('index'))
    
    # Sauvegarder en CSV temporaire
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    df.to_csv(temp_file.name, index=False)
    
    # Envoyer le fichier CSV
    return send_file(
        temp_file.name,
        mimetype='text/csv',
        as_attachment=True,
        download_name='analyse_facture.csv'
    )

@app.route('/analyze-with-data/<pdf_id>')
def analyze_with_data(pdf_id):
    """Redirection vers le dashboard avec les données de la facture"""
    if pdf_id not in pdf_analysis_results:
        flash('Analyse non trouvée')
        return redirect(url_for('index'))
    
    result = pdf_analysis_results[pdf_id]['result']
    
    # Dans une application complète, on stockerait ces données en session
    # ou on redirigerait vers le module d'analyse avec ces données
    flash('Fonctionnalité à implémenter dans l\'application principale')
    return redirect(url_for('index'))

@app.route('/compare-pdf-data/<pdf_id>')
def compare_pdf_data(pdf_id):
    """Redirection vers la page de comparaison avec les données de la facture"""
    if pdf_id not in pdf_analysis_results:
        flash('Analyse non trouvée')
        return redirect(url_for('index'))
    
    flash('Fonctionnalité de comparaison à implémenter dans l\'application principale')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
#!/usr/bin/env python3
"""
Test de génération PDF pour EnergyInsight
"""

import pandas as pd
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def test_pdf_generation():
    """Test de la génération PDF"""
    print("🧪 Test de génération PDF...")
    
    # Données de test
    analysis = {
        'total_consumption': 1000.0,
        'avg_consumption': 50.0,
        'max_consumption': 150.0,
        'min_consumption': 10.0,
        'std_consumption': 25.0,
        'peaks': [
            {
                'date': '2025-01-01',
                'value': 150.0,
                'percentage_above_avg': 200.0,
                'severity': 'high'
            }
        ],
        'statistics': {
            'median': 45.0,
            'coefficient_variation': 0.5,
            'efficiency_score': 75.0
        },
        'recommendations': [
            {
                'title': 'Optimisation des heures de pointe',
                'message': 'Consommation élevée détectée en journée',
                'action': 'Décaler certains équipements vers les heures creuses',
                'priority': 'high',
                'savings_potential': '15-20%'
            }
        ]
    }
    
    filename = "test_data.csv"
    
    try:
        # Générer le PDF
        buffer = generate_professional_pdf(analysis, filename)
        
        # Sauvegarder le PDF de test
        with open('test_report.pdf', 'wb') as f:
            f.write(buffer.getvalue())
        
        print("✅ PDF généré avec succès: test_report.pdf")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_professional_pdf(analysis, filename, df=None):
    """Génère un rapport PDF professionnel complet"""
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2E86AB'),
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#2E86AB'),
        alignment=TA_LEFT
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Contenu du PDF
    story = []
    
    # Titre
    story.append(Paragraph("EnergyInsight", title_style))
    story.append(Paragraph("Rapport d'Analyse Énergétique Professionnel", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    # Informations du rapport
    info_data = [
        ['Fichier analysé:', filename],
        ['Date de génération:', datetime.now().strftime('%d/%m/%Y à %H:%M')],
        ['Période d\'analyse:', 'Données complètes du fichier'],
        ['Type d\'analyse:', 'Analyse avancée avec détection d\'anomalies']
    ]
    
    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4FD')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2E86AB'))
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Résumé exécutif
    story.append(Paragraph("Résumé Exécutif", heading_style))
    
    efficiency_score = analysis['statistics']['efficiency_score']
    if efficiency_score >= 75:
        summary = f"Votre installation présente une efficacité énergétique <b>excellente</b> ({efficiency_score:.1f}/100)."
    elif efficiency_score >= 50:
        summary = f"Votre installation présente une efficacité énergétique <b>modérée</b> ({efficiency_score:.1f}/100)."
    else:
        summary = f"Votre installation présente une efficacité énergétique <b>faible</b> ({efficiency_score:.1f}/100)."
    
    summary += f" L'analyse révèle {len(analysis['peaks'])} pics de consommation et "
    summary += f"une consommation moyenne de {analysis['avg_consumption']:.1f} kWh."
    
    story.append(Paragraph(summary, normal_style))
    story.append(Spacer(1, 15))
    
    # Statistiques détaillées
    story.append(Paragraph("Statistiques Détaillées", heading_style))
    
    stats_data = [
        ['Métrique', 'Valeur', 'Unité'],
        ['Consommation totale', f"{analysis['total_consumption']:.1f}", 'kWh'],
        ['Consommation moyenne', f"{analysis['avg_consumption']:.1f}", 'kWh'],
        ['Consommation maximale', f"{analysis['max_consumption']:.1f}", 'kWh'],
        ['Consommation minimale', f"{analysis['min_consumption']:.1f}", 'kWh'],
        ['Écart-type', f"{analysis['std_consumption']:.1f}", 'kWh'],
        ['Médiane', f"{analysis['statistics']['median']:.1f}", 'kWh'],
        ['Coefficient de variation', f"{analysis['statistics']['coefficient_variation']:.2f}", '-'],
        ['Score d\'efficacité', f"{efficiency_score:.1f}", '/100']
    ]
    
    stats_table = Table(stats_data, colWidths=[200, 100, 50])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2E86AB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Analyse des pics
    story.append(Paragraph("Analyse des Pics de Consommation", heading_style))
    
    if analysis['peaks']:
        story.append(Paragraph(f"<b>{len(analysis['peaks'])} pics de consommation</b> ont été détectés:", normal_style))
        
        peaks_data = [['Date', 'Consommation (kWh)', 'Dépassement (%)', 'Sévérité']]
        for peak in analysis['peaks'][:10]:  # Limiter à 10 pics
            peaks_data.append([
                peak['date'],
                f"{peak['value']:.1f}",
                f"{peak['percentage_above_avg']:.1f}%",
                peak['severity'].upper()
            ])
        
        peaks_table = Table(peaks_data, colWidths=[120, 100, 100, 80])
        peaks_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B6B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FF6B6B')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF5F5')])
        ]))
        
        story.append(peaks_table)
    else:
        story.append(Paragraph("✅ Aucun pic de consommation significatif détecté.", normal_style))
    
    story.append(Spacer(1, 20))
    
    # Recommandations
    story.append(Paragraph("Recommandations Personnalisées", heading_style))
    
    if analysis['recommendations']:
        for i, rec in enumerate(analysis['recommendations'][:5], 1):  # Limiter à 5 recommandations
            priority_color = {
                'high': colors.HexColor('#FF6B6B'),
                'medium': colors.HexColor('#FFA500'),
                'low': colors.HexColor('#4CAF50')
            }.get(rec['priority'], colors.black)
            
            story.append(Paragraph(f"<b>{i}. {rec['title']}</b>", 
                                 ParagraphStyle('RecTitle', parent=normal_style, textColor=priority_color)))
            story.append(Paragraph(f"<b>Diagnostic:</b> {rec['message']}", normal_style))
            story.append(Paragraph(f"<b>Action recommandée:</b> {rec['action']}", normal_style))
            story.append(Paragraph(f"<b>Potentiel d'économie:</b> {rec.get('savings_potential', 'Non estimé')}", normal_style))
            story.append(Spacer(1, 10))
    else:
        story.append(Paragraph("✅ Votre profil de consommation est optimal.", normal_style))
    
    # Conclusion
    story.append(Spacer(1, 20))
    story.append(Paragraph("Conclusion", heading_style))
    
    conclusion_text = f"""
    Cette analyse approfondie de votre consommation énergétique révèle un score d'efficacité de {efficiency_score:.1f}/100.
    Les recommandations ci-dessus vous permettront d'optimiser votre consommation et de réaliser des économies significatives.
    Pour un accompagnement personnalisé, n'hésitez pas à contacter nos experts EnergyInsight.
    """
    
    story.append(Paragraph(conclusion_text, normal_style))
    
    # Générer le PDF
    doc.build(story)
    
    # Réinitialiser le buffer
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    test_pdf_generation()

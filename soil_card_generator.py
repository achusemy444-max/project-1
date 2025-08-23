from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import os
import pandas as pd

class SoilHealthCardGenerator:
    def __init__(self):
        # 12 nutrients with ranges and units
        self.nutrient_ranges = {
            'nitrogen': {'low': 280, 'medium': 560, 'unit': 'kg/ha'},
            'phosphorus': {'low': 10, 'medium': 25, 'unit': 'kg/ha'},
            'potassium': {'low': 120, 'medium': 280, 'unit': 'kg/ha'},
            'ph': {'low': 5.5, 'medium': 8.5, 'unit': ''},
            'electrical_conductivity': {'low': 1, 'medium': 4, 'unit': 'dS/m'},
            'organic_carbon': {'low': 0.50, 'medium': 0.75, 'unit': '%'},
            'sulphur': {'low': 10, 'medium': 20, 'unit': 'mg/kg'},
            'zinc': {'low': 0.6, 'medium': 1.2, 'unit': 'mg/kg'},
            'boron': {'low': 0.5, 'medium': 1.0, 'unit': 'mg/kg'},
            'iron': {'low': 4.5, 'medium': 9.0, 'unit': 'mg/kg'},
            'manganese': {'low': 2, 'medium': 4, 'unit': 'mg/kg'},
            'copper': {'low': 0.2, 'medium': 0.4, 'unit': 'mg/kg'}
        }

    def get_nutrient_status(self, nutrient_key, value):
        if value is None or value == '':
            return 'NOT AVAILABLE'
        try:
            value = float(value)
            ranges = self.nutrient_ranges[nutrient_key]
            if value < ranges['low']:
                return 'LOW, DEFICIENT'
            elif value <= ranges['medium']:
                return 'MEDIUM, NEUTRAL'
            else:
                return 'HIGH, SUFFICIENT'
        except (ValueError, KeyError):
            return 'NOT AVAILABLE'

    def get_status_color(self, status):
        if 'LOW' in status:
            return colors.red
        elif 'HIGH' in status:
            return colors.green
        elif 'MEDIUM' in status:
            return colors.orange
        else:
            return colors.grey

    def create_pdf_card(self, file_path, data, nutrients, custom_remarks=""):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.pdfgen import canvas

        class WatermarkCanvas(canvas.Canvas):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
            def draw_watermark(self):
                self.saveState()
                self.setFont("Helvetica-Oblique", 12)
                self.setFillColor(colors.grey)
                self.drawCentredString(A4[0]/2, 20, "Developer: Achu Semy SCA, Tseminyu, Nagaland")
                self.restoreState()
            def _startPage(self):
                super()._startPage()
                if self._pageNumber == 1:
                    self.draw_watermark()

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor=colors.darkblue, alignment=1)
        story.append(Paragraph("SOIL HEALTH CARD", title_style))
        subtitle_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=14, spaceAfter=20, textColor=colors.black, alignment=1)
        story.append(Paragraph("Soil & Water Department SDO Office, Tseminyu, Nagaland", subtitle_style))

        # Header Table (remove Validity)
        header_data = [
            ['Center Name:', data.get('center_name', ''), 'Test ID:', data.get('test_id', '')],
            ['Address:', data.get('address', ''), 'Testing Date:', data.get('testing_date', '')]
        ]
        header_table = Table(header_data, colWidths=[1.5*inch, 3*inch, 1*inch, 2*inch])
        header_table.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        story.append(header_table)
        story.append(Spacer(1, 20))

        # Details Sections
        card_issued_data = [['Name:', data.get('farmer_name', '')], ['Address:', data.get('farmer_address', '')]]
        sample_info_data = [['Survey No.:', data.get('survey_no', '')], ['Selected Crop:', data.get('selected_crop', 'N/A')]]
        
        details_table_data = [
            [Paragraph("<b>CARD ISSUED TO</b>", styles['Normal']), Paragraph("<b>SAMPLE INFORMATION</b>", styles['Normal'])],
            [Table(card_issued_data, colWidths=[1*inch, 2.7*inch]), Table(sample_info_data, colWidths=[1.2*inch, 2.5*inch])]
        ]
        details_table = Table(details_table_data, colWidths=[3.7*inch, 3.7*inch])
        details_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(details_table)
        story.append(Spacer(1, 20))

        # Nutrient Table
        story.append(Paragraph("SOIL SAMPLE DETAILS", styles['Heading2']))
        nutrient_data = [['Nutrient', 'Value', 'Range (Low - Medium - High)', 'Status']]
        nutrient_labels = {k: k.replace('_', ' ').upper() for k in self.nutrient_ranges.keys()}
        for key, label in nutrient_labels.items():
            value = nutrients.get(key)
            if value is not None and value != '':
                unit = self.nutrient_ranges[key]['unit']
                ranges = self.nutrient_ranges[key]
                range_text = f"< {ranges['low']}  |  {ranges['low']}-{ranges['medium']}  |  > {ranges['medium']}"
                status = self.get_nutrient_status(key, value)
                nutrient_data.append([label, f"{value} {unit}", range_text, status])
        
        nutrient_table = Table(nutrient_data, colWidths=[2*inch, 1.5*inch, 2.5*inch, 1.5*inch])
        table_style = [('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)]
        for i, row in enumerate(nutrient_data[1:], 1):
            table_style.append(('BACKGROUND', (3, i), (3, i), self.get_status_color(row[3])))
        nutrient_table.setStyle(TableStyle(table_style))
        story.append(nutrient_table)
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("RECOMMENDATIONS", styles['Heading2']))
        recommendations = self.generate_recommendations(nutrients, data.get('selected_crop', ''))
        rec_data = [
            ['SOIL AMENDMENT', 'FERTILIZER COMBO 1', 'FERTILIZER COMBO 2'],
            [Paragraph("<br/>".join(recommendations['soil_conditioner']) or "N/A", styles['Normal']),
             Paragraph("<br/>".join(recommendations['fertilizer_combo_1']) or "N/A", styles['Normal']),
             Paragraph("<br/>".join(recommendations['fertilizer_combo_2']) or "N/A", styles['Normal'])]
        ]
        rec_table = Table(rec_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
        rec_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('VALIGN', (0,1), (-1,-1), 'TOP')]))
        story.append(rec_table)
        story.append(Spacer(1, 20))
        
        # Custom Remarks Section
        if custom_remarks:
            story.append(Paragraph("ADDITIONAL REMARKS", styles['Heading2']))
            remarks_formatted = custom_remarks.replace('\n', '<br/>')
            story.append(Paragraph(remarks_formatted, styles['Normal']))
            story.append(Spacer(1, 20))

        # Footer
        story.append(Paragraph("<i>Developer: Achu Semy (SCA, Tseminyu, Nagaland)</i>", styles['Italic']))
        doc.build(story, canvasmaker=WatermarkCanvas)

    def generate_recommendations(self, nutrients, crop_type):
        # Use the same logic as in main.py
        def get_nutrient_status_simple(value, nutrient_type):
            if value is None:
                return 'unknown'
            try:
                value = float(value)
                ranges = self.nutrient_ranges.get(nutrient_type)
                if ranges:
                    return 'low' if value < ranges['low'] else 'sufficient'
            except (ValueError, TypeError):
                return 'unknown'
            return 'unknown'

        recommendations = {
            'soil_conditioner': [],
            'fertilizer_combo_1': [],
            'fertilizer_combo_2': []
        }
        ph_value = nutrients.get('ph')
        if ph_value:
            if ph_value < 5.5:
                recommendations['soil_conditioner'].append('Lime application @ 2-4 t/ha')
            elif ph_value > 8.5:
                recommendations['soil_conditioner'].append('Gypsum application @ 2-3 t/ha')
        oc_value = nutrients.get('organic_carbon')
        if oc_value and oc_value < 0.5:
            recommendations['soil_conditioner'].append('FYM/Compost @ 10-12 t/ha')
        n_status = get_nutrient_status_simple(nutrients.get('nitrogen'), 'nitrogen')
        p_status = get_nutrient_status_simple(nutrients.get('phosphorus'), 'phosphorus')
        k_status = get_nutrient_status_simple(nutrients.get('potassium'), 'potassium')
        crop_recommendations = {
            'rice': {'low_n': 'Urea @ 130 kg/ha', 'low_p': 'SSP @ 250 kg/ha', 'low_k': 'MOP @ 100 kg/ha'},
            'wheat': {'low_n': 'Urea @ 120 kg/ha', 'low_p': 'DAP @ 120 kg/ha', 'low_k': 'MOP @ 80 kg/ha'},
            'maize': {'low_n': 'Urea @ 140 kg/ha', 'low_p': 'SSP @ 300 kg/ha', 'low_k': 'MOP @ 120 kg/ha'}
        }
        crop_lower = crop_type.lower() if crop_type else 'rice'
        if crop_lower in crop_recommendations:
            crop_rec = crop_recommendations[crop_lower]
            if n_status == 'low': recommendations['fertilizer_combo_1'].append(crop_rec['low_n'])
            if p_status == 'low': recommendations['fertilizer_combo_1'].append(crop_rec['low_p'])
            if k_status == 'low': recommendations['fertilizer_combo_1'].append(crop_rec['low_k'])
        for nutrient in ['zinc', 'boron', 'iron']:
            if get_nutrient_status_simple(nutrients.get(nutrient), nutrient) == 'low':
                if nutrient == 'zinc': recommendations['fertilizer_combo_2'].append('Zinc Sulphate @ 25 kg/ha')
                elif nutrient == 'boron': recommendations['fertilizer_combo_2'].append('Borax @ 10 kg/ha')
                elif nutrient == 'iron': recommendations['fertilizer_combo_2'].append('FeSO4 @ 25 kg/ha')
        return recommendations

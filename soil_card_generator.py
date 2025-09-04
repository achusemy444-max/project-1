from fpdf2 import FPDF
from datetime import datetime
import os
import csv

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

    def create_pdf_card(self, file_path, data, nutrients, custom_remarks=""):
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 10, "SOIL HEALTH CARD", 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, "Soil & Water Department SDO Office, Tseminyu, Nagaland", 0, 1, 'C')
        pdf.ln(10)

        # Header Information
        pdf.set_font("Arial", size=10)
        pdf.cell(95, 6, f"Center Name: {data.get('center_name', '')}", 0, 0)
        pdf.cell(95, 6, f"Test ID: {data.get('test_id', '')}", 0, 1)
        pdf.cell(95, 6, f"Address: {data.get('address', '')}", 0, 0)
        pdf.cell(95, 6, f"Testing Date: {data.get('testing_date', '')}", 0, 1)
        pdf.ln(10)

        # Farmer Details
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "CARD ISSUED TO", 0, 1)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, f"Name: {data.get('farmer_name', '')}", 0, 1)
        pdf.cell(0, 6, f"Address: {data.get('farmer_address', '')}", 0, 1)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "SAMPLE INFORMATION", 0, 1)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, f"Survey No.: {data.get('survey_no', '')}", 0, 1)
        pdf.cell(0, 6, f"Selected Crop: {data.get('selected_crop', 'N/A')}", 0, 1)
        pdf.ln(10)

        # Nutrient Table Header
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "SOIL SAMPLE DETAILS", 0, 1)
        pdf.ln(3)

        # Table headers
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 8, "Nutrient", 1, 0, 'C')
        pdf.cell(25, 8, "Value", 1, 0, 'C')
        pdf.cell(55, 8, "Range (L-M-H)", 1, 0, 'C')
        pdf.cell(35, 8, "Status", 1, 1, 'C')

        # Nutrient data
        pdf.set_font("Arial", size=8)
        for key, ranges in self.nutrient_ranges.items():
            value = nutrients.get(key)
            if value is not None and value != '':
                label = key.replace('_', ' ').title()
                unit = ranges['unit']
                range_text = f"<{ranges['low']} | {ranges['low']}-{ranges['medium']} | >{ranges['medium']}"
                status = self.get_nutrient_status(key, value)
                
                # Color based on status
                if 'LOW' in status:
                    pdf.set_text_color(255, 0, 0)  # Red
                elif 'HIGH' in status:
                    pdf.set_text_color(0, 128, 0)  # Green
                elif 'MEDIUM' in status:
                    pdf.set_text_color(255, 165, 0)  # Orange
                else:
                    pdf.set_text_color(128, 128, 128)  # Grey
                
                pdf.cell(45, 6, label, 1, 0)
                pdf.cell(25, 6, f"{value} {unit}", 1, 0)
                pdf.cell(55, 6, range_text, 1, 0)
                pdf.cell(35, 6, status, 1, 1)
                
                # Reset color
                pdf.set_text_color(0, 0, 0)

        pdf.ln(10)

        # Recommendations
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "RECOMMENDATIONS", 0, 1)
        pdf.ln(3)
        
        recommendations = self.generate_recommendations(nutrients, data.get('selected_crop', ''))
        
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(60, 8, "SOIL AMENDMENT", 1, 0, 'C')
        pdf.cell(60, 8, "FERTILIZER COMBO 1", 1, 0, 'C')
        pdf.cell(60, 8, "FERTILIZER COMBO 2", 1, 1, 'C')
        
        # Handle recommendations
        pdf.set_font("Arial", size=8)
        max_lines = max(
            len(recommendations['soil_conditioner']),
            len(recommendations['fertilizer_combo_1']),
            len(recommendations['fertilizer_combo_2']),
            1
        )
        
        for i in range(max_lines):
            soil_text = recommendations['soil_conditioner'][i] if i < len(recommendations['soil_conditioner']) else ""
            fert1_text = recommendations['fertilizer_combo_1'][i] if i < len(recommendations['fertilizer_combo_1']) else ""
            fert2_text = recommendations['fertilizer_combo_2'][i] if i < len(recommendations['fertilizer_combo_2']) else ""
            
            pdf.cell(60, 6, soil_text, 1, 0)
            pdf.cell(60, 6, fert1_text, 1, 0)
            pdf.cell(60, 6, fert2_text, 1, 1)

        # Custom Remarks
        if custom_remarks:
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "ADDITIONAL REMARKS", 0, 1)
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 6, custom_remarks)

        # Footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 6, "Developer: Achu Semy (SCA, Tseminyu, Nagaland)", 0, 1, 'C')

        # Save the PDF
        pdf.output(file_path)

    def generate_recommendations(self, nutrients, crop_type):
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
            if n_status == 'low': 
                recommendations['fertilizer_combo_1'].append(crop_rec['low_n'])
            if p_status == 'low': 
                recommendations['fertilizer_combo_1'].append(crop_rec['low_p'])
            if k_status == 'low': 
                recommendations['fertilizer_combo_1'].append(crop_rec['low_k'])

        for nutrient in ['zinc', 'boron', 'iron']:
            if get_nutrient_status_simple(nutrients.get(nutrient), nutrient) == 'low':
                if nutrient == 'zinc': 
                    recommendations['fertilizer_combo_2'].append('Zinc Sulphate @ 25 kg/ha')
                elif nutrient == 'boron': 
                    recommendations['fertilizer_combo_2'].append('Borax @ 10 kg/ha')
                elif nutrient == 'iron': 
                    recommendations['fertilizer_combo_2'].append('FeSO4 @ 25 kg/ha')

        return recommendations

    def generate_bulk_cards(self, csv_path, output_dir):
        """Generate bulk PDF cards from CSV file - using pure Python CSV instead of pandas"""
        try:
            count = 0
            errors = []
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for index, row in enumerate(csv_reader):
                    try:
                        # Convert row to data dict
                        data = {}
                        nutrients = {}
                        
                        # Map CSV columns to data fields
                        for column, value in row.items():
                            column_lower = column.lower().strip()
                            if column_lower in ['farmer_name', 'center_name', 'address', 'test_id', 
                                              'testing_date', 'survey_no', 'farmer_address', 'selected_crop']:
                                data[column_lower] = str(value).strip() if value else ''
                            elif column_lower in self.nutrient_ranges:
                                try:
                                    nutrients[column_lower] = float(value) if value else None
                                except ValueError:
                                    nutrients[column_lower] = None
                        
                        # Generate filename
                        farmer_name = data.get('farmer_name', f'farmer_{index}')
                        safe_name = "".join(c for c in farmer_name if c.isalnum() or c in (' ', '_', '-')).strip()
                        filename = f"soil_card_{safe_name}_{index}.pdf"
                        filepath = os.path.join(output_dir, filename)
                        
                        # Generate PDF
                        self.create_pdf_card(filepath, data, nutrients, "")
                        count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {index}: {str(e)}")
                        
            return count, errors
            
        except Exception as e:
            return 0, [f"Failed to read CSV: {str(e)}"]

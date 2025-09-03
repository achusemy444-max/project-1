from fpdf import FPDF
from datetime import datetime
import os
import pandas as pd

class SoilHealthCardGenerator:
    def __init__(self):
        # 12 nutrients with ranges and units (same as before)
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
        # Return RGB values instead of reportlab color objects
        if 'LOW' in status:
            return (255, 0, 0)  # Red
        elif 'HIGH' in status:
            return (0, 128, 0)  # Green
        elif 'MEDIUM' in status:
            return (255, 165, 0)  # Orange
        else:
            return (128, 128, 128)  # Grey

    def create_pdf_card(self, file_path, data, nutrients, custom_remarks=""):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(200, 10, txt="SOIL HEALTH CARD", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt="Soil & Water Department SDO Office, Tseminyu, Nagaland", ln=True, align='C')
        pdf.ln(10)

        # Header Information
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(95, 8, txt=f"Center Name: {data.get('center_name', '')}", ln=False)
        pdf.cell(95, 8, txt=f"Test ID: {data.get('test_id', '')}", ln=True)
        pdf.cell(95, 8, txt=f"Address: {data.get('address', '')}", ln=False)
        pdf.cell(95, 8, txt=f"Testing Date: {data.get('testing_date', '')}", ln=True)
        pdf.ln(10)

        # Card Details
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 8, txt="CARD ISSUED TO", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 6, txt=f"Name: {data.get('farmer_name', '')}", ln=True)
        pdf.cell(200, 6, txt=f"Address: {data.get('farmer_address', '')}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 8, txt="SAMPLE INFORMATION", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 6, txt=f"Survey No.: {data.get('survey_no', '')}", ln=True)
        pdf.cell(200, 6, txt=f"Selected Crop: {data.get('selected_crop', 'N/A')}", ln=True)
        pdf.ln(10)

        # Nutrient Table
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="SOIL SAMPLE DETAILS", ln=True)
        pdf.ln(5)

        # Table headers
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 8, txt="Nutrient", border=1, align='C')
        pdf.cell(30, 8, txt="Value", border=1, align='C')
        pdf.cell(60, 8, txt="Range (L-M-H)", border=1, align='C')
        pdf.cell(40, 8, txt="Status", border=1, align='C')
        pdf.ln()

        # Nutrient data
        pdf.set_font("Arial", size=9)
        for key, ranges in self.nutrient_ranges.items():
            value = nutrients.get(key)
            if value is not None and value != '':
                label = key.replace('_', ' ').title()
                unit = ranges['unit']
                range_text = f"<{ranges['low']} | {ranges['low']}-{ranges['medium']} | >{ranges['medium']}"
                status = self.get_nutrient_status(key, value)
                
                # Set color based on status
                color = self.get_status_color(status)
                pdf.set_text_color(color[0], color[1], color[2])
                
                pdf.cell(50, 6, txt=label, border=1)
                pdf.cell(30, 6, txt=f"{value} {unit}", border=1)
                pdf.cell(60, 6, txt=range_text, border=1)
                pdf.cell(40, 6, txt=status, border=1)
                pdf.ln()
                
                # Reset text color to black
                pdf.set_text_color(0, 0, 0)

        pdf.ln(10)

        # Recommendations
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="RECOMMENDATIONS", ln=True)
        pdf.ln(5)
        
        recommendations = self.generate_recommendations(nutrients, data.get('selected_crop', ''))
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(63, 8, txt="SOIL AMENDMENT", border=1, align='C')
        pdf.cell(63, 8, txt="FERTILIZER COMBO 1", border=1, align='C')
        pdf.cell(64, 8, txt="FERTILIZER COMBO 2", border=1, align='C')
        pdf.ln()
        
        pdf.set_font("Arial", size=9)
        # Handle multiline cells for recommendations
        max_lines = max(
            len(recommendations['soil_conditioner']),
            len(recommendations['fertilizer_combo_1']),
            len(recommendations['fertilizer_combo_2'])
        )
        
        for i in range(max(max_lines, 1)):
            soil_text = recommendations['soil_conditioner'][i] if i < len(recommendations['soil_conditioner']) else ""
            fert1_text = recommendations['fertilizer_combo_1'][i] if i < len(recommendations['fertilizer_combo_1']) else ""
            fert2_text = recommendations['fertilizer_combo_2'][i] if i < len(recommendations['fertilizer_combo_2']) else ""
            
            pdf.cell(63, 6, txt=soil_text, border=1)
            pdf.cell(63, 6, txt=fert1_text, border=1)
            pdf.cell(64, 6, txt=fert2_text, border=1)
            pdf.ln()

        # Custom Remarks
        if custom_remarks:
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 8, txt="ADDITIONAL REMARKS", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(200, 6, txt=custom_remarks)

        # Footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(200, 6, txt="Developer: Achu Semy (SCA, Tseminyu, Nagaland)", ln=True, align='C')

        # Save the PDF
        pdf.output(file_path)

    def generate_recommendations(self, nutrients, crop_type):
        # Same logic as before - returns recommendations dict
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
        """Generate bulk PDF cards from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Convert row to data dict
                    data = {}
                    nutrients = {}
                    
                    # Map CSV columns to data fields
                    for col in df.columns:
                        if col.lower() in ['farmer_name', 'center_name', 'address', 'test_id', 
                                         'testing_date', 'survey_no', 'farmer_address', 'selected_crop']:
                            data[col.lower()] = str(row[col]) if pd.notna(row[col]) else ''
                        elif col.lower() in self.nutrient_ranges:
                            nutrients[col.lower()] = float(row[col]) if pd.notna(row[col]) else None
                    
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
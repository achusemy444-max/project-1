from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.image import Image  # Import Kivy Image widget
from kivy.core.window import Window
import os

# Make sure this file exists in the same directory as main.py:
from soil_card_generator import SoilHealthCardGenerator

# Utility functions for recommendations (from your tkinter code)
def get_nutrient_status_simple(value, nutrient_type, generator_instance):
    if value is None:
        return 'unknown'
    try:
        value = float(value)
        ranges = generator_instance.nutrient_ranges.get(nutrient_type)
        if ranges:
            return 'low' if value < ranges['low'] else 'sufficient'
    except (ValueError, TypeError):
        return 'unknown'
    return 'unknown'

def generate_recommendations(nutrients, crop_type, generator_instance):
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
    n_status = get_nutrient_status_simple(nutrients.get('nitrogen'), 'nitrogen', generator_instance)
    p_status = get_nutrient_status_simple(nutrients.get('phosphorus'), 'phosphorus', generator_instance)
    k_status = get_nutrient_status_simple(nutrients.get('potassium'), 'potassium', generator_instance)
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
        if get_nutrient_status_simple(nutrients.get(nutrient), nutrient, generator_instance) == 'low':
            if nutrient == 'zinc': recommendations['fertilizer_combo_2'].append('Zinc Sulphate @ 25 kg/ha')
            elif nutrient == 'boron': recommendations['fertilizer_combo_2'].append('Borax @ 10 kg/ha')
            elif nutrient == 'iron': recommendations['fertilizer_combo_2'].append('FeSO4 @ 25 kg/ha')
    return recommendations

class CardDetailsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = GridLayout(cols=2, spacing=10, padding=10)
        self.inputs = {}
        details = ['farmer_name', 'center_name', 'address', 'test_id', 'testing_date', 'survey_no', 'farmer_address', 'selected_crop']
        for field in details:
            layout.add_widget(Label(text=field.replace('_',' ').title()))
            ti = TextInput(multiline=False)
            self.inputs[field] = ti
            layout.add_widget(ti)
        next_btn = Button(text="Next: Nutrient Values", size_hint_y=None, height=50)
        next_btn.bind(on_release=self.next_screen)
        layout.add_widget(next_btn)
        self.add_widget(layout)

    def next_screen(self, instance):
        # Save details to app
        for k, v in self.inputs.items():
            self.app.data[k] = v.text
        # Use self.app.root.current instead of self.app.sm.current
        self.app.root.current = 'nutrients'

class NutrientsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = GridLayout(cols=2, spacing=10, padding=10)
        self.inputs = {}
        for key, params in self.app.generator.nutrient_ranges.items():
            layout.add_widget(Label(text=f"{key.replace('_',' ').title()} ({params['unit']})"))
            ti = TextInput(multiline=False)
            self.inputs[key] = ti
            layout.add_widget(ti)
        layout.add_widget(Label(text="Custom Remarks"))
        self.remarks_input = TextInput(multiline=True, size_hint_y=None, height=100)
        layout.add_widget(self.remarks_input)
        next_btn = Button(text="Generate PDF", size_hint_y=None, height=50)
        next_btn.bind(on_release=self.generate_pdf)
        layout.add_widget(next_btn)
        self.add_widget(layout)

    def generate_pdf(self, instance):
        # Save nutrients to app
        for k, v in self.inputs.items():
            try:
                self.app.nutrients[k] = float(v.text) if v.text else None
            except ValueError:
                self.app.nutrients[k] = None
        self.app.remarks = self.remarks_input.text
        # Generate PDF
        try:
            # Use a safe default filename if farmer_name is empty
            farmer_name = self.app.data.get('farmer_name', '').strip() or 'user'
            # Remove invalid filename characters for Windows
            safe_name = "".join(c for c in farmer_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
            filename = f"soil_card_{safe_name}.pdf"
            # Save to user's Documents directory to avoid permission issues
            documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
            if not os.path.exists(documents_dir):
                documents_dir = os.path.expanduser("~")
            filepath = os.path.join(documents_dir, filename)
            self.app.generator.create_pdf_card(filepath, self.app.data, self.app.nutrients, self.app.remarks)
            self.app.root.current = 'done'
            self.app.done_screen.set_message(f"PDF generated:\n{filepath}")
        except Exception as e:
            popup = Popup(title="Error", content=Label(text=f"Could not generate PDF:\n{e}"), size_hint=(0.8,0.4))
            popup.open()

class BulkScreen(Screen):
    csv_path = StringProperty("")
    output_dir = StringProperty("")
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="Bulk CSV Generator", font_size=20))
        # CSV file chooser
        self.csv_chooser = FileChooserIconView(filters=['*.csv'], size_hint_y=0.4)
        layout.add_widget(self.csv_chooser)
        # Output directory chooser
        self.dir_chooser = FileChooserIconView(dirselect=True, size_hint_y=0.4)
        layout.add_widget(self.dir_chooser)
        # Generate button
        btn = Button(text="Generate Bulk PDFs from CSV", size_hint_y=None, height=50)
        btn.bind(on_release=self.generate_bulk)
        layout.add_widget(btn)
        self.add_widget(layout)

    def generate_bulk(self, instance):
        csv_files = self.csv_chooser.selection
        dirs = self.dir_chooser.selection
        if not csv_files or not dirs:
            popup = Popup(title="Input Missing", content=Label(text="Please select both a CSV file and an output directory."), size_hint=(0.8,0.4))
            popup.open()
            return
        csv_path = csv_files[0]
        output_dir = dirs[0]
        count, errors = self.app.generator.generate_bulk_cards(csv_path, output_dir)
        if errors:
            error_details = "\n".join(errors[:4])
            popup = Popup(title="Bulk Generation Complete", content=Label(text=f"Generated {count} cards.\n{len(errors)} errors.\nFirst errors:\n{error_details}"), size_hint=(0.8,0.6))
            popup.open()
        else:
            popup = Popup(title="Success", content=Label(text=f"Generated all {count} soil health cards in:\n{output_dir}"), size_hint=(0.8,0.4))
            popup.open()

class DoneScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.label = Label(text="")
        box.add_widget(self.label)
        # Add watermark label at the bottom
        watermark = Label(
            text="Developer: Achu Semy SCA, Tseminyu, Nagaland",
            font_size=14,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=30
        )
        box.add_widget(watermark)
        reset_btn = Button(text="Generate New Card", size_hint_y=None, height=50)
        reset_btn.bind(on_release=self.reset_app)
        box.add_widget(reset_btn)
        self.add_widget(box)

    def set_message(self, msg):
        self.label.text = msg

    def reset_app(self, instance):
        # Access the app instance directly
        app = App.get_running_app()
        app.data = {}
        app.nutrients = {}
        app.remarks = ""
        # Clear input fields in CardDetailsScreen
        for ti in app.card_details_screen.inputs.values():
            ti.text = ""
        # Clear input fields in NutrientsScreen
        for ti in app.nutrients_screen.inputs.values():
            ti.text = ""
        app.nutrients_screen.remarks_input.text = ""
        app.root.current = 'card'

class SettingsScreen(Screen):
    background_path = StringProperty("")

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Background Image Selection
        layout.add_widget(Label(text="Select Background Image:", size_hint_y=None, height=30))
        # Set the FileChooser to start in the user's home directory and restrict to user's folders
        user_home = os.path.expanduser("~")
        self.file_chooser = FileChooserIconView(
            path=user_home,
            filters=['*.png', '*.jpg', '*.jpeg'],
            size_hint_y=0.5,
            rootpath=user_home  # Restrict navigation to user's home
        )
        layout.add_widget(self.file_chooser)

        # Display Selected Image
        self.background_image = Image(source=self.background_path, allow_stretch=True, keep_ratio=False)
        layout.add_widget(self.background_image)

        # Button to Apply Background
        apply_btn = Button(text="Apply Background", size_hint_y=None, height=50)
        apply_btn.bind(on_release=self.apply_background)
        layout.add_widget(apply_btn)

        self.add_widget(layout)

    def apply_background(self, instance):
        if self.file_chooser.selection:
            self.background_path = self.file_chooser.selection[0]
            self.background_image.source = self.background_path
            self.app.root.background = self.background_path  # Apply to main app background
            popup = Popup(title="Background Applied", content=Label(text="Background image applied to the app."), size_hint=(0.8, 0.4))
            popup.open()
        else:
            popup = Popup(title="No Image Selected", content=Label(text="Please select a background image."), size_hint=(0.8, 0.4))
            popup.open()

class RootScreen(ScreenManager):
    background = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self._on_window_resize)
        default_bg = os.path.join(os.path.dirname(__file__), "picture.png")
        if os.path.exists(default_bg):
            self.background = default_bg
        self._bg_rect = None
        self._bg_bind = False
        self._setup_background()

    def _setup_background(self):
        from kivy.graphics import Rectangle, Color
        with self.canvas.before:
            Color(1, 1, 1, 1)
            if self.background:
                self._bg_rect = Rectangle(pos=self.pos, size=self.size, source=self.background)
            else:
                self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        # Only bind once to avoid stacking multiple callbacks
        if not self._bg_bind:
            self.bind(size=self._update_bg_rect, pos=self._update_bg_rect, background=self._update_bg_image)
            self._bg_bind = True

    def _on_window_resize(self, instance, width, height):
        self._update_bg_rect()

    def _update_bg_rect(self, *args):
        if self._bg_rect:
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size

    def _update_bg_image(self, *args):
        # Change the image source if background changes
        if self._bg_rect:
            self._bg_rect.source = self.background if self.background else ""

# Android permissions handling
try:
    from android.permissions import Permission, request_permissions, check_permission
    from android.storage import app_storage_path
    ANDROID = True
except ImportError:
    ANDROID = False
    app_storage_path = None

from kivy.clock import Clock

class SoilHealthCardApp(App):
    def build(self):
        # For Android: request permissions before showing main UI
        if ANDROID:
            self._layout = BoxLayout(orientation='vertical')
            self._status_label = Label(text='Checking permissions...')
            self._layout.add_widget(self._status_label)
            Clock.schedule_once(self.request_android_permissions, 0.5)
            return self._layout
        else:
            return self._build_main_ui()

    def request_android_permissions(self, dt):
        permissions = [
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ]
        has_permissions = all(check_permission(p) for p in permissions)
        if not has_permissions:
            self._status_label.text = 'Requesting storage permissions...'
            request_permissions(permissions, self.permission_callback)
        else:
            self._show_main_ui()

    def permission_callback(self, permissions, grant_results):
        if all(grant_results):
            self._status_label.text = 'Permissions granted!'
            Clock.schedule_once(lambda dt: self._show_main_ui(), 0.5)
        else:
            self._status_label.text = 'Permissions denied. App may not function properly.'
            retry_btn = Button(text='Retry Permission Request', size_hint_y=0.2)
            retry_btn.bind(on_press=lambda x: self.request_android_permissions(0))
            self._layout.add_widget(retry_btn)

    def _show_main_ui(self, *args):
        self._layout.clear_widgets()
        self._layout.add_widget(Label(text='Starting application...'))
        Clock.schedule_once(lambda dt: self._replace_with_main_ui(), 0.5)

    def _replace_with_main_ui(self, *args):
        self._layout.clear_widgets()
        self._layout.add_widget(self._build_main_ui())

    def _build_main_ui(self):
        Window.size = (800, 800)
        self.generator = SoilHealthCardGenerator()
        self.data = {}
        self.nutrients = {}
        self.remarks = ""

        self.root = RootScreen()  # Use RootScreen as the root
        self.card_details_screen = CardDetailsScreen(self, name='card')
        self.nutrients_screen = NutrientsScreen(self, name='nutrients')
        # Remove BulkScreen (CSV/bulk) if not needed
        # self.bulk_screen = BulkScreen(self, name='bulk')
        self.done_screen = DoneScreen(name='done')
        self.settings_screen = SettingsScreen(app=self, name='settings')  # Pass app instance

        self.root.add_widget(self.card_details_screen)
        self.root.add_widget(self.nutrients_screen)
        # self.root.add_widget(self.bulk_screen)
        self.root.add_widget(self.done_screen)
        self.root.add_widget(self.settings_screen)  # Add settings screen

        self.root.current = 'card'  # Start with card details screen

        return self.root

if __name__ == "__main__":
    import kivy
    import sys
    print(f"Kivy version: {kivy.__version__}")
    print(f"Python version: {sys.version}")
    SoilHealthCardApp().run()
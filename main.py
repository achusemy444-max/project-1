from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.core.window import Window
import os
import sys
import subprocess

# Local generator
from soil_card_generator import SoilHealthCardGenerator

# Small helpers

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
        if n_status == 'low':
            recommendations['fertilizer_combo_1'].append(crop_rec['low_n'])
        if p_status == 'low':
            recommendations['fertilizer_combo_1'].append(crop_rec['low_p'])
        if k_status == 'low':
            recommendations['fertilizer_combo_1'].append(crop_rec['low_k'])
    for nutrient in ['zinc', 'boron', 'iron']:
        if get_nutrient_status_simple(nutrients.get(nutrient), nutrient, generator_instance) == 'low':
            if nutrient == 'zinc':
                recommendations['fertilizer_combo_2'].append('Zinc Sulphate @ 25 kg/ha')
            elif nutrient == 'boron':
                recommendations['fertilizer_combo_2'].append('Borax @ 10 kg/ha')
            elif nutrient == 'iron':
                recommendations['fertilizer_combo_2'].append('FeSO4 @ 25 kg/ha')
    return recommendations


class CardDetailsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        outer = MDBoxLayout(orientation='vertical', spacing=10, padding=10)

        # Title / logo area
        title = MDLabel(text="Soil Health Card\nTseminyu, Nagaland", halign='center', theme_text_color='Primary', font_style='H5')
        outer.add_widget(title)

        form = GridLayout(cols=2, spacing=10, size_hint_y=None)
        # allow GridLayout height to grow with content
        form.bind(minimum_height=form.setter('height'))
        self.inputs = {}
        details = ['farmer_name', 'center_name', 'address', 'test_id', 'testing_date', 'survey_no', 'farmer_address', 'selected_crop']
        from kivy.uix.label import Label as KivyLabel
        from kivy.uix.textinput import TextInput as KivyTextInput
        for field in details:
            form.add_widget(KivyLabel(text=field.replace('_', ' ').title(), size_hint_y=None, height=40))
            ti = KivyTextInput(multiline=False, size_hint_y=None, height=40)
            self.inputs[field] = ti
            form.add_widget(ti)

        # Next button
        next_btn = MDRaisedButton(text="Next: Nutrient Values", size_hint=(1, None), height=48)
        next_btn.bind(on_release=self.next_screen)

        # Put the form inside a ScrollView so it fits portrait phones
        sv = ScrollView(size_hint=(1, 1))
        sv.add_widget(form)
        outer.add_widget(sv)
        outer.add_widget(next_btn)
        self.add_widget(outer)

    def next_screen(self, instance):
        for k, v in self.inputs.items():
            self.app.data[k] = v.text
        self.app.sm.current = 'nutrients'


class NutrientsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        outer = MDBoxLayout(orientation='vertical', spacing=10, padding=10)

        form = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))
        self.inputs = {}
        from kivy.uix.label import Label as KivyLabel
        from kivy.uix.textinput import TextInput as KivyTextInput
        for key, params in self.app.generator.nutrient_ranges.items():
            form.add_widget(KivyLabel(text=f"{key.replace('_', ' ').title()} ({params['unit']})", size_hint_y=None, height=40))
            ti = KivyTextInput(multiline=False, size_hint_y=None, height=40)
            self.inputs[key] = ti
            form.add_widget(ti)

        form.add_widget(KivyLabel(text="Custom Remarks", size_hint_y=None, height=30))
        self.remarks_input = KivyTextInput(multiline=True, size_hint_y=None, height=120)
        form.add_widget(self.remarks_input)

        gen_btn = MDRaisedButton(text="Generate PDF", size_hint=(1, None), height=48)
        gen_btn.bind(on_release=self.generate_pdf)

        # Wrap the form in a ScrollView for portrait phones
        sv = ScrollView(size_hint=(1, 1))
        sv.add_widget(form)
        outer.add_widget(sv)
        outer.add_widget(gen_btn)
        self.add_widget(outer)

    def generate_pdf(self, instance):
        for k, v in self.inputs.items():
            try:
                self.app.nutrients[k] = float(v.text) if v.text else None
            except ValueError:
                self.app.nutrients[k] = None
        self.app.remarks = self.remarks_input.text
        try:
            farmer_name = self.app.data.get('farmer_name', '').strip() or 'user'
            safe_name = "".join(c for c in farmer_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
            filename = f"soil_card_{safe_name}.pdf"
            documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
            if not os.path.exists(documents_dir):
                documents_dir = os.path.expanduser("~")
            filepath = os.path.join(documents_dir, filename)
            self.app.generator.create_pdf_card(filepath, self.app.data, self.app.nutrients, self.app.remarks)
            # Attempt to open the generated PDF automatically (platform-aware)
            try:
                if hasattr(os, 'startfile'):
                    # Windows
                    os.startfile(filepath)
                else:
                    # macOS / Linux
                    opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                    subprocess.Popen([opener, filepath])
            except Exception:
                # ignore open errors; user will still see the file path
                pass
            self.app.done_screen.set_message(f"PDF generated:\n{filepath}")
            self.app.sm.current = 'done'
        except Exception as e:
            dlg = MDDialog(title="Error", text=f"Could not generate PDF:\n{e}")
            dlg.open()


class BulkScreen(Screen):
    csv_path = StringProperty("")
    output_dir = StringProperty("")

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        outer = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        from kivy.uix.label import Label as KivyLabel

        outer.add_widget(KivyLabel(text="Bulk CSV Generator", size_hint_y=None, height=30))

        # Restrict file chooser to the user's home directory to avoid permission errors
        user_home = os.path.expanduser("~")
        self.csv_chooser = FileChooserIconView(filters=['*.csv'], size_hint_y=0.4, path=user_home, rootpath=user_home)
        outer.add_widget(self.csv_chooser)

        self.dir_chooser = FileChooserIconView(dirselect=True, size_hint_y=0.4, path=user_home, rootpath=user_home)
        outer.add_widget(self.dir_chooser)

        btn = MDRaisedButton(text="Generate Bulk PDFs from CSV", size_hint=(1, None), height=48)
        btn.bind(on_release=self.generate_bulk)
        outer.add_widget(btn)
        self.add_widget(outer)

    def generate_bulk(self, instance):
        csv_files = getattr(self, 'csv_chooser', None) and self.csv_chooser.selection or []
        dirs = getattr(self, 'dir_chooser', None) and self.dir_chooser.selection or []
        if not csv_files or not dirs:
            dlg = MDDialog(title="Input Missing", text="Please select both a CSV file and an output directory.")
            dlg.open()
            return
        csv_path = csv_files[0]
        output_dir = dirs[0]
        count, errors = self.app.generator.generate_bulk_cards(csv_path, output_dir)
        if errors:
            error_details = "\n".join(errors[:4])
            dlg = MDDialog(title="Bulk Generation Complete", text=f"Generated {count} cards.\n{len(errors)} errors.\nFirst errors:\n{error_details}")
            dlg.open()
        else:
            dlg = MDDialog(title="Success", text=f"Generated all {count} soil health cards in:\n{output_dir}")
            dlg.open()


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from kivy.uix.image import Image as KivyImage
        outer = MDBoxLayout(orientation='vertical')
        img_path = os.path.join(os.path.dirname(__file__), 'shclogo.png')
        if os.path.exists(img_path):
            img = KivyImage(source=img_path, allow_stretch=True, keep_ratio=True)
        else:
            img = KivyImage()
        outer.add_widget(img)
        self.add_widget(outer)


class DoneScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        outer = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        from kivy.uix.label import Label as KivyLabel

        self.label = KivyLabel(text="")
        outer.add_widget(self.label)

        watermark = KivyLabel(text="Developer: Achu Semy SCA, Tseminyu, Nagaland", size_hint_y=None, height=30)
        outer.add_widget(watermark)

        reset_btn = MDRaisedButton(text="Generate New Card", size_hint=(1, None), height=48)
        reset_btn.bind(on_release=self.reset_app)
        outer.add_widget(reset_btn)
        self.add_widget(outer)

    def set_message(self, msg):
        self.label.text = msg

    def reset_app(self, instance):
        app = MDApp.get_running_app()
        app.data = {}
        app.nutrients = {}
        app.remarks = ""
        for ti in app.card_details_screen.inputs.values():
            ti.text = ""
        for ti in app.nutrients_screen.inputs.values():
            ti.text = ""
        app.nutrients_screen.remarks_input.text = ""
        app.sm.current = 'card'


class SettingsScreen(Screen):
    background_path = StringProperty("")

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        outer = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        from kivy.uix.label import Label as KivyLabel

        outer.add_widget(KivyLabel(text="Select Background Image:", size_hint_y=None, height=30))

        user_home = os.path.expanduser("~")
        self.file_chooser = FileChooserIconView(path=user_home, filters=['*.png', '*.jpg', '*.jpeg'], size_hint_y=0.5)
        outer.add_widget(self.file_chooser)

        self.background_image = Image(source=self.background_path, allow_stretch=True, keep_ratio=False)
        outer.add_widget(self.background_image)

        apply_btn = MDRaisedButton(text="Apply Background", size_hint=(1, None), height=48)
        apply_btn.bind(on_release=self.apply_background)
        outer.add_widget(apply_btn)

        self.add_widget(outer)

    def apply_background(self, instance):
        if self.file_chooser.selection:
            self.background_path = self.file_chooser.selection[0]
            self.background_image.source = self.background_path
            self.app.sm.background = self.background_path
            dlg = MDDialog(title="Background Applied", text="Background image applied to the app.")
            dlg.open()
        else:
            dlg = MDDialog(title="No Image Selected", text="Please select a background image.")
            dlg.open()


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
        if self._bg_rect:
            self._bg_rect.source = self.background if self.background else ""


# Android permissions handling (optional)
try:
    from android.permissions import Permission, request_permissions, check_permission
    from android.storage import app_storage_path
    ANDROID = True
except Exception:
    ANDROID = False
    app_storage_path = None

from kivy.clock import Clock


class SoilHealthCardApp(MDApp):
    def build(self):
        if ANDROID:
            self._layout = MDBoxLayout(orientation='vertical')
            self._status_label = MDLabel(text='Checking permissions...')
            self._layout.add_widget(self._status_label)
            Clock.schedule_once(self.request_android_permissions, 0.5)
            return self._layout
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
            retry_btn = MDRaisedButton(text='Retry Permission Request', size_hint=(1, None), height=48)
            retry_btn.bind(on_release=lambda x: self.request_android_permissions(0))
            self._layout.add_widget(retry_btn)

    def _show_main_ui(self):
        self._layout.clear_widgets()
        self._layout.add_widget(MDLabel(text='Starting application...'))
        Clock.schedule_once(lambda dt: self._replace_with_main_ui(), 0.5)

    def _replace_with_main_ui(self, *args):
        self._layout.clear_widgets()
        self._layout.add_widget(self._build_main_ui())

    def _build_main_ui(self):
        # Try to enforce portrait mode on Android; fall back to a portrait window on desktop for testing
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            activity.setRequestedOrientation(1)  # SCREEN_ORIENTATION_PORTRAIT
        except Exception:
            Window.size = (360, 800)
        self.generator = SoilHealthCardGenerator()
        self.data = {}
        self.nutrients = {}
        self.remarks = ""
        # Screen manager and screens
        self.sm = RootScreen()
        self.splash_screen = SplashScreen(name='splash')
        self.card_details_screen = CardDetailsScreen(self, name='card')
        self.nutrients_screen = NutrientsScreen(self, name='nutrients')
        self.bulk_screen = BulkScreen(self, name='bulk')
        self.done_screen = DoneScreen(name='done')
        self.settings_screen = SettingsScreen(app=self, name='settings')

        # Add splash first so it shows on startup
        self.sm.add_widget(self.splash_screen)
        self.sm.add_widget(self.card_details_screen)
        self.sm.add_widget(self.nutrients_screen)
        self.sm.add_widget(self.bulk_screen)
        self.sm.add_widget(self.done_screen)
        self.sm.add_widget(self.settings_screen)

        # show splash first, then switch to main card screen after 3 seconds
        self.sm.current = 'splash'
        Clock.schedule_once(lambda dt: setattr(self.sm, 'current', 'card'), 3)

        # Some KivyMD versions may not expose MDToolbar under the same path.
        # Use a simple MD header (MDLabel inside an MDBoxLayout) to avoid compatibility issues.
        outer = MDBoxLayout(orientation='vertical')
        header = MDBoxLayout(size_hint_y=None, height=56, padding=8)
        title_lbl = MDLabel(text="Soil Health Card Tseminyu, Nagaland", halign='left', theme_text_color='Primary', font_style='H6')
        header.add_widget(title_lbl)
        outer.add_widget(header)
        outer.add_widget(self.sm)
        return outer


if __name__ == "__main__":
    import kivy
    import sys
    print(f"Kivy version: {kivy.__version__}")
    print(f"Python version: {sys.version}")
    SoilHealthCardApp().run()
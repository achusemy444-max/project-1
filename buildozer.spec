[app]
title = SHC Tseminyu
package.name = shctseminyu
package.domain = org.shctseminyu
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,txt,json,csv
icon.filename = %(source.dir)s/icon.png
version = 0.1.0
orientation = portrait
fullscreen = 0

# Python dependencies used by the app
requirements = python3,kivy==2.3.1,reportlab,pandas

# Android permissions
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET

# Android toolchain targets
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.bootstrap = sdl2

# Automation convenience for CI
android.accept_sdk_license = True

# Exclusions
exclude_patterns = tests,*.pyc,__pycache__/*,*.md,*.spec

# macOS notes (not used by CI)
osx.python_version = 3.13
osx.kivy_version = 2.3.1

# Logging
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1

[app:source_patterns]
+.*/main.py
+.*/soil_card_generator.py
+.*/permission_helper.py
+.*/icon.png
+.*/ICON.jpg
+.*/icon.jpg
+.*/picture.png
+.*/picture.jpg

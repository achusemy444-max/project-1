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

# Keep first build minimal; add pandas back after toolchain succeeds
requirements = python3,kivy==2.3.1,reportlab

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Toolchain pins
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.bootstrap = sdl2
android.accept_sdk_license = True

exclude_patterns = tests,*.pyc,__pycache__/*,*.md,*.spec

# Logging
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1

# Pin python-for-android so libffi/autotools are in sync
p4a.fork = kivy
p4a.branch = master

[app:source_patterns]
+.*/main.py
+.*/soil_card_generator.py
+.*/permission_helper.py
+.*/icon.png
+.*/ICON.jpg
+.*/icon.jpg
+.*/picture.png
+.*/picture.jpg

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

# Entry point requirements
requirements = python3,kivy==2.3.1,reportlab,pandas
# If builds are slow or fail due to pandas, remove pandas if not needed in production. [12]

# Permissions needed by the app (file saving, internet future-proofing)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET
# Runtime permission requests are already in main.py. Declaring here exposes them to Android. [7][11]

# Android target and toolchains
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.sdk_extra_args = --licenses
android.bootstrap = sdl2
# Use default Java from the image; p4a handles toolchain on CI. [17][18]

# Package build behavior
# Use master only if you hit AAB/SDK warnings; otherwise omit to use buildozer default p4a version. [18]
# p4a.branch = master

# Files to exclude
exclude_patterns = tests,*.pyc,__pycache__/*,*.md,*.spec

# iOS/macOS notes (not used on CI but set per request)
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

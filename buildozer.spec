[app]
# (str) Title of your application
title = SHC Tseminyu

# (str) Package name
package.name = shctseminyu

# (str) Package domain (reverse-DNS style)
package.domain = org.shctseminyu

# (str) Source code directory
source.dir = .

# (list) Include these file extensions in the APK
source.include_exts = py,kv,png,jpg,jpeg,txt,json,csv

# (str) Application icon
icon.filename = %(source.dir)s/icon.png

# (str) Application version
version = 0.1.0

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Fullscreen mode (1=true, 0=false)
fullscreen = 0

# (list) Application requirements
requirements = python3,kivy==2.3.1,reportlab,pandas,pillow

# (list) Permissions your app needs
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Android API to target
android.api = 33

# (int) Minimum API your app supports
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (str) Architectures to build for
android.archs = arm64-v8a,armeabi-v7a

# (str) Android bootstrap type
android.bootstrap = sdl2

# Accept Android SDK license during CI pipeline
android.accept_sdk_license = True

# (list) Exclude these patterns from the APK
exclude_patterns = tests,*.pyc,__pycache__/*,*.md,*.spec

# (int) Logging level (0=all, 1=debug, 2=info, 3=warn, 4=error, 5=critical only)
log_level = 2


[buildozer]
log_level = 2
warn_on_root = 1

[app:source_patterns]
# Include important sources explicitly
+.*/main.py
+.*/soil_card_generator.py
+.*/permission_helper.py
+.*/icon.png
+.*/ICON.jpg
+.*/icon.jpg
+.*/picture.png
+.*/picture.jpg

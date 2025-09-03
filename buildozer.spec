[app]
# (str) Title of your application
title = Soil Health Card

# (str) Package name (must be lowercase, no spaces)
package.name = shc_generator

# (str) Package domain (reverse domain notation)
package.domain = org.tseminyu

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all)
source.include_exts = py,png,jpg,kv,atlas,ttf,otf

# (str) Application versioning
version = 0.1

# (list) Application requirements - REMOVED pandas and reportlab completely
requirements = python3,kivy==2.3.1,https://github.com/kivymd/KivyMD/archive/master.zip,pillow,fpdf2,plyer

# (str) Presplash and icon
presplash.filename = %(source.dir)s/picture.png
icon.filename = %(source.dir)s/icon.png

# (list) Supported orientations
orientation = portrait

# (list) Permissions required by the app
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 34
# (int) Minimum API your APK / AAB will support.
android.minapi = 23

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) Format used to package the app for release / debug mode
android.release_artifact = aab
android.debug_artifact = apk

# p4a / buildozer tuning
p4a.branch = master
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
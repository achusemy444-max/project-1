[app]
# (str) Title of your application
title = SHC Generator

# (str) Package name (must be lowercase, no spaces)
package.name = shc_generator

# (str) Package domain (reverse domain notation)
package.domain = org.tseminyu

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
source.include_patterns = shclogo.png, picture.png, icon.png

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.3.1,https://github.com/kivymd/KivyMD/archive/master.zip,pillow,reportlab,pandas

# (str) Presplash of the application (packaged image shown before the app loads)
presplash.filename = %(source.dir)s/picture.png

# (str) Icon of the application
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

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = aab

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

# p4a settings
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
android.enable_androidx = True

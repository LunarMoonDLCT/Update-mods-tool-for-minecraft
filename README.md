# 🧰 Minecraft Mod Updater

A simple tool that updates your Minecraft mods via Modrinth and CurseForge.  
✅ Easy-to-use interface  
✅ Supports multiple loaders: `fabric`, `forge`, `quilt`, `neoforge`  

## 💡 Features

- Automatically updates mods by searching Modrinth first, then CurseForge if needed
- Saves updated mods into a separate folder (`updated_mods_yyyyMMdd_HHmmss`)
- Clean and user-friendly GUI built with `tkinter`

## 📦 Requirements (for running via Python)

- Python 3.8+
- Required packages:
  ```bash
  pip install requests toml

## 📦 How to build (for build to application file)
1. Install pyinstaller
    ```bash
    pip install pyinstaller
    ```
2. build code to app
    ```bash
    python -m pyinstaller --noconfirm --onefile --windowed --version-file=file_info.version --icon=download_icon.ico tool-update-mod-minecraft.py

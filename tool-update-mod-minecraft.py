#--------------------------------------#
# Import & Config
#--------------------------------------#

import os
import json
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
import threading
import webbrowser
import tkinter
from ctypes import windll
from datetime import datetime
import sv_ttk
from tkinter import ttk
import base64
import tempfile

try:
    import toml
except ImportError:
    toml = None

CURSEFORGE_API_KEY = "Dont-enter-API-KEY"
latest_output_folder = [""]

#--------------------------------------#
# Embedded Icon (Base64)
#--------------------------------------#

ICON_BASE64 = b'''
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
''' 

def create_temp_icon():
    icon_path = tempfile.NamedTemporaryFile(delete=False, suffix=".ico")
    icon_path.write(base64.b64decode(ICON_BASE64))
    icon_path.close()
    return icon_path.name

#--------------------------------------#
# Utility Functions
#--------------------------------------#

def sanitize_filename(name):
    import re
    return re.sub(r"[^\w\d\-_.]", "", name)

def log_print(log, message):
    log.insert(tk.END, message + "\n")
    log.see(tk.END)

#--------------------------------------#
# Mod Info Extraction
#--------------------------------------#

def extract_mod_info(jar_path):
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            if 'fabric.mod.json' in jar.namelist():
                with jar.open('fabric.mod.json') as f:
                    mod_json = json.load(f)
                    return mod_json.get("name") or mod_json.get("id")
            if 'quilt.mod.json' in jar.namelist():
                with jar.open('quilt.mod.json') as f:
                    mod_json = json.load(f)
                    q = mod_json.get("quilt_loader", {})
                    return q.get("name") or q.get("id")
            if 'META-INF/mods.toml' in jar.namelist() and toml:
                with jar.open('META-INF/mods.toml') as f:
                    data = toml.loads(f.read().decode('utf-8'))
                    mods = data.get("mods", [])
                    if mods and isinstance(mods, list):
                        return mods[0].get("modId")
    except Exception as e:
        print(f"❌ Error reading mod jar: {e}")
    return None

#--------------------------------------#
# Modrinth API
#--------------------------------------#

def search_modrinth(mod_id):
    url = f"https://api.modrinth.com/v2/search?query={mod_id}&limit=1"
    res = requests.get(url)
    if res.ok and res.json().get("hits"):
        return res.json()["hits"][0]["project_id"]
    return None

def get_latest_modrinth(project_id, mc_version, modloader):
    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    res = requests.get(url)
    if res.ok:
        for ver in res.json():
            loaders = ver.get('loaders', [])
            if mc_version in ver.get('game_versions', []) and modloader in loaders:
                for f in ver['files']:
                    if f['filename'].endswith('.jar'):
                        return f['url'], f['filename']
        print(f"⚠️ No {modloader} version found on Modrinth.")
    return None

#--------------------------------------#
# CurseForge API
#--------------------------------------#

def search_curseforge(mod_name):
    url = f"https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter={mod_name}&pageSize=1"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    res = requests.get(url, headers=headers)
    if res.ok and res.json()["data"]:
        return res.json()["data"][0]["id"]
    return None

def get_latest_curseforge(mod_id, mc_version, modloader):
    url = f"https://api.curseforge.com/v1/mods/{mod_id}/files"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    res = requests.get(url, headers=headers)
    if res.ok:
        for file in res.json()["data"]:
            if mc_version in file["gameVersions"] and modloader in file.get("modLoaders", []):
                return file["downloadUrl"], file["fileName"]
    return None

#--------------------------------------#
# Mod Update
#--------------------------------------#

def update_mod(filepath, mc_version, loader, output_dir, log):
    mod_id = extract_mod_info(filepath)
    if not mod_id:
        filename = os.path.splitext(os.path.basename(filepath))[0]
        mod_id = filename.split("-")[0]
        log_print(log, f"[!] Could not read mod ID, using file name: {mod_id}")
        print(f"[!] Could not read mod ID, using file name: {mod_id}")
    else:
        log_print(log, f"[*] Searching mod: {mod_id}")
        print(f"[*] Searching mod: {mod_id}")

    project_id = search_modrinth(mod_id)
    if project_id:
        result = get_latest_modrinth(project_id, mc_version, loader)
        if result:
            url, filename = result
            try:
                response = requests.get(url)
                if response.ok:
                    save_path = os.path.join(output_dir, sanitize_filename(filename))
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    log_print(log, f"[✓] Downloaded from Modrinth: {filename}")
                    print(f"[✓] Downloaded from Modrinth: {filename}")
                    return
            except Exception as e:
                print(f"Error downloading from Modrinth: {e}")
        log_print(log, "[!] No compatible version on Modrinth")
        print("[!] No compatible version on Modrinth")

    log_print(log, "[!] Trying CurseForge...")
    print("[!] Trying CurseForge...")
    mod_cid = search_curseforge(mod_id)
    if mod_cid:
        result = get_latest_curseforge(mod_cid, mc_version, loader)
        if result:
            url, filename = result
            try:
                response = requests.get(url)
                if response.ok:
                    save_path = os.path.join(output_dir, sanitize_filename(filename))
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    log_print(log, f"[✓] Downloaded from CurseForge: {filename}")
                    print(f"[✓] Downloaded from CurseForge: {filename}")
                    return
            except Exception as e:
                print(f"Error downloading from CurseForge: {e}")
    log_print(log, f"[!] Could not update: {mod_id}")
    print(f"[!] Could not update: {mod_id}")

#--------------------------------------#
# GUI Helpers
#--------------------------------------#

def select_folder():
    folder = filedialog.askdirectory(title="Select your mod folder")
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

def open_output_folder():
    if os.path.exists(latest_output_folder[0]):
        webbrowser.open(latest_output_folder[0])

def start_update():
    mods_folder = folder_entry.get()
    mc_version = mc_entry.get().strip()
    loader = loader_var.get().strip()
    if not os.path.isdir(mods_folder):
        messagebox.showerror("Error", "Mod folder not selected.")
        return
    if not mc_version or loader not in ["fabric", "forge", "quilt", "neoforge"]:
        messagebox.showerror("Error", "Please enter valid Minecraft version and loader.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.abspath(f"updated_mods_{timestamp}")
    latest_output_folder[0] = output_dir
    os.makedirs(output_dir, exist_ok=True)
    log_box.delete(1.0, tk.END)

    def task():
        for file in os.listdir(mods_folder):
            if file.endswith(".jar"):
                update_mod(os.path.join(mods_folder, file), mc_version, loader, output_dir, log_box)
        log_print(log_box, f"\n🎉 Done! Files saved to: {output_dir}")
        print(f"\n🎉 Done! Files saved to: {output_dir}")

    threading.Thread(target=task).start()

def about():
    print(f"đã mở LunarMoonDLCT đẹp zai :))")
    messagebox.showinfo("About this app", "This app was created by LunarMoonDLCT.\nDiscord: https://discord.com/users/1182279772571717632")

def confirm_exit():
    print(f"đã mở exit windows")
    if messagebox.askokcancel("Exit Confirmation", "Do you really want to exit?"):
        root.destroy()

#--------------------------------------#
# GUI Layout
#--------------------------------------#

try:
    windll.shcore.SetProcessDpiAwareness(1)
except AttributeError:
    pass

root = tk.Tk()
root.title("Minecraft Mod Updater")

try:
    root.iconbitmap(create_temp_icon())
except Exception as e:
    print(f"Warning: Could not set icon. {e}")

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10)

folder_entry = ttk.Entry(frame, width=40)
folder_entry.grid(row=0, column=1)
ttk.Button(frame, text="Select Mod Folder", command=select_folder).grid(row=0, column=2)

ttk.Label(frame, text="Minecraft Version:").grid(row=1, column=0)
mc_entry = ttk.Entry(frame)
mc_entry.grid(row=1, column=1)

ttk.Label(frame, text="Mod Loader:").grid(row=2, column=0)
loader_var = tkinter.StringVar(value="Choosen your modloader")
loader_menu = ttk.Combobox(frame, textvariable=loader_var, values=["fabric", "forge", "quilt", "neoforge"], state="readonly")
loader_menu.grid(row=2, column=1)

ttk.Button(frame, text="Start Update", command=start_update).grid(row=3, column=0, columnspan=2, pady=5)
ttk.Button(frame, text="Open Output Folder", command=open_output_folder).grid(row=3, column=2, padx=5)
ttk.Button(frame, text="About App", command=about).grid(row=0, column=4)

log_box = scrolledtext.ScrolledText(root, width=100, height=25)
log_box.pack(padx=10, pady=10)

root.protocol("WM_DELETE_WINDOW", confirm_exit)

sv_ttk.set_theme("dark")
root.mainloop()

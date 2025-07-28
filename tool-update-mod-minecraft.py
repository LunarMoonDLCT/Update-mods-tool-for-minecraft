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
try:
    import toml
except ImportError:
    toml = None

CURSEFORGE_API_KEY = "Dont-enter-API-KEY"
latest_output_folder = [""]

#--------------------------------------#
# Utility Functions
#--------------------------------------#
def sanitize_filename(name):
    import re
    return re.sub(r"[^\w\d\-_.]", "", name)

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
        mod_id = filename.split("-")[0]  # Only take name before version part
        log.insert(ttk.END, f"[!] Could not read mod ID, using file name: {mod_id}\n")
        print(f"[!] Could not read mod ID, using file name: {mod_id}")
    else:
        log.insert(ttk.END, f"[*] Searching mod: {mod_id}\n")
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
                    log.insert(ttk.END, f"[✓] Downloaded from Modrinth: {filename}\n")
                    print(f"[✓] Downloaded from Modrinth: {filename}")
                    return
            except Exception as e:
                print(f"Error downloading from Modrinth: {e}")
        log.insert(ttk.END, "[!] No compatible version on Modrinth\n")
        print("[!] No compatible version on Modrinth")

    log.insert(ttk.END, "[!] Trying CurseForge...\n")
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
                    log.insert(ttk.END, f"[✓] Downloaded from CurseForge: {filename}\n")
                    print(f"[✓] Downloaded from CurseForge: {filename}")
                    return
            except Exception as e:
                print(f"Error downloading from CurseForge: {e}")
    log.insert(ttk.END, f"[!] Could not update: {mod_id}\n")
    print(f"[!] Could not update: {mod_id}")

#--------------------------------------#
# GUI Helpers
#--------------------------------------#
def select_folder():
    folder = filedialog.askdirectory(title="Select your mod folder")
    if folder:
        folder_entry.delete(0, ttk.END)
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
    if not mc_version or loader not in ["fabric", "forge", "quilt","neoforge"]:
        messagebox.showerror("Error", "Please enter valid Minecraft version and loader.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.abspath(f"updated_mods_{timestamp}")
    latest_output_folder[0] = output_dir
    os.makedirs(output_dir, exist_ok=True)
    log_box.delete(1.0, ttk.END)

    def task():
        for file in os.listdir(mods_folder):
            if file.endswith(".jar"):
                update_mod(os.path.join(mods_folder, file), mc_version, loader, output_dir, log_box)
        log_box.insert(ttk.END, f"\n🎉 Done! Files saved to: {output_dir}\n")
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
    root.iconbitmap(os.path.join(os.path.dirname(__file__), "icon.ico"))
except Exception as e:
    print(f"Warning: Could not load icon. {e}")

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
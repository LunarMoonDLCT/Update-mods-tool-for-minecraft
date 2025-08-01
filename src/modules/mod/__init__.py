import json
import zipfile
import requests
import os
import tkinter as tk
from ..utils import sanitize_filename


try:
    import toml
except ImportError:
    toml = None

CURSEFORGE_API_KEY = "Dont-enter-API-KEY"

class ModUpdater:
    def __init__(self):
        self.latest_output_folder = [""]
        pass

    #--------------------------------------#
    # Mod Info Extraction
    #--------------------------------------#
    def extract_mod_info(self, jar_path):
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
    # Modrinth
    #--------------------------------------#
    def search_modrinth(self, mod_id):
        url = f"https://api.modrinth.com/v2/search?query={mod_id}&limit=1"
        res = requests.get(url)
        if res.ok and res.json().get("hits"):
            return res.json()["hits"][0]["project_id"]
        return None

    def get_latest_modrinth(self, project_id, mc_version, modloader):
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
    # CurseForge
    #--------------------------------------#
    def search_curseforge(self, mod_name):
        url = f"https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter={mod_name}&pageSize=1"
        headers = {"x-api-key": CURSEFORGE_API_KEY}
        res = requests.get(url, headers=headers)
        if res.ok and res.json()["data"]:
            return res.json()["data"][0]["id"]
        return None

    def get_latest_curseforge(self, mod_id, mc_version, modloader):
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
    def update_mod(self, filepath, mc_version, loader, output_dir, log):
        mod_id = self.extract_mod_info(filepath)
        if not mod_id:
            filename = os.path.splitext(os.path.basename(filepath))[0]
            mod_id = filename.split("-")[0]  # Only take name before version part
            log.insert(tk.END, f"[!] Could not read mod ID, using file name: {mod_id}\n")
            print(f"[!] Could not read mod ID, using file name: {mod_id}")
        else:
            log.insert(tk.END, f"[*] Searching mod: {mod_id}\n")
            print(f"[*] Searching mod: {mod_id}")

        project_id = self.search_modrinth(mod_id)
        if project_id:
            result = self.get_latest_modrinth(project_id, mc_version, loader)
            if result:
                url, filename = result
                try:
                    response = requests.get(url)
                    if response.ok:
                        save_path = os.path.join(output_dir, sanitize_filename(filename))
                        with open(save_path, 'wb') as f:
                            f.write(response.content)
                        log.insert(tk.END, f"[✓] Downloaded from Modrinth: {filename}\n")
                        print(f"[✓] Downloaded from Modrinth: {filename}")
                        if os.path.exists(filepath):
                            os.remove(filepath)
                            log.insert(tk.END, f"[✓] Removed old mod: {filepath}\n")
                            print(f"[*] Removed: {filepath}")
                        return
                    else:
                        log.insert(tk.END, f"[!] Failed to download from Modrinth: {filename}\n")
                        print(f"[!] Failed to download from Modrinth: {filename}")
                except Exception as e:
                    print(f"Error downloading from Modrinth: {e}")
        else:
            log.insert(tk.END, "[!] Mod not found on Modrinth\n")
            print("[!] Mod not found on Modrinth")

        log.insert(tk.END, "[!] Trying CurseForge...\n")
        print("[!] Trying CurseForge...")
        mod_cid = self.search_curseforge(mod_id)
        if mod_cid:
            result = self.get_latest_curseforge(mod_cid, mc_version, loader)
            if result:
                url, filename = result
                try:
                    response = requests.get(url)
                    if response.ok:
                        save_path = os.path.join(output_dir, sanitize_filename(filename))
                        with open(save_path, 'wb') as f:
                            f.write(response.content)
                        log.insert(tk.END, f"[✓] Downloaded from CurseForge: {filename}\n")
                        print(f"[✓] Downloaded from CurseForge: {filename}")
                        if os.path.exists(filepath):
                            os.remove(filepath)
                            log.insert(tk.END, f"[✓] Removed old mod: {filepath}\n")
                            print(f"[*] Removed: {filepath}")
                        return
                    else:
                        log.insert(tk.END, f"[!] Failed to download from CurseForge: {filename}\n")
                        print(f"[!] Failed to download from CurseForge: {filename}")
                except Exception as e:
                    print(f"Error downloading from CurseForge: {e}")
        else:
            log.insert(tk.END, "[!] Mod not found on CurseForge\n")
            print("[!] Mod not found on CurseForge")

        log.insert(tk.END, f"[!] Could not update: {mod_id}\n")
        print(f"[!] Could not update: {mod_id}")
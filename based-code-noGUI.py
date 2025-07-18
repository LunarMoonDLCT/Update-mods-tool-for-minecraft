#------Import lib------------#
import os #Hệ điều hành
import zipfile #file zip nhưng dùng jar
import json #Đọc json
import requests
import re
#----------------------------#

#-----Config here------------#
MINECRAFT_VERSION = "1.21.7"
MODLOADER = "fabric"
MODS_FOLDER = "./mods.old"
OUTPUT_FOLDER = "./updated_mods"
#----------------------------#

#----------config api--------#
CURSEFORGE_API_KEY = "Dont-enter-API-KEY" 
#----------------------------#

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

#---------Main code----------#

def sanitize_filename(name):
    return re.sub(r"[^\w\d\-_.]", "", name)
#--Check jar file in mod-----#
def get_mod_info_from_jar(jar_path):
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            # Fabric
            if 'fabric.mod.json' in jar.namelist():
                with jar.open('fabric.mod.json') as f:
                    mod_json = json.load(f)
                    return mod_json.get("name") or mod_json.get("id")

            # Quilt
            if 'quilt.mod.json' in jar.namelist():
                with jar.open('quilt.mod.json') as f:
                    mod_json = json.load(f)
                    q = mod_json.get("quilt_loader", {})
                    return q.get("name") or q.get("id")

            # Forge
            if 'META-INF/mods.toml' in jar.namelist():
                try:
                    import toml
                except ImportError:
                    print("⚠️ Thiếu thư viện 'toml'. Cài bằng: pip install toml")
                    return None
                with jar.open('META-INF/mods.toml') as f:
                    data = toml.loads(f.read().decode('utf-8'))
                    mods = data.get("mods", [])
                    if mods and isinstance(mods, list):
                        return mods[0].get("modId")
    except Exception as e:
        print(f"❌ Lỗi khi đọc mod jar: {e}")
    return None

#----------------------------#

#---Search mod in wed--------#

def search_modrinth(mod_name):
    url = f"https://api.modrinth.com/v2/search?query={mod_name}&limit=1" 
    res = requests.get(url)
    if res.ok and res.json()['hits']:
        return res.json()['hits'][0]['project_id']
        
        
        
        
    return None
#----------------------------#


#--Download latest ver mod---#

def get_latest_modrinth(project_id):
    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    res = requests.get(url)
    if not res.ok:
        return None
    for version in res.json():
        if MINECRAFT_VERSION in version['game_versions'] and MODLOADER in version['loaders']:
            for file in version['files']:
                if file['filename'].endswith(".jar"):
                    return file['url'], file['filename']
                    
                    
                    
                    
    return None
#----------------------------#


#-----CurseForge mod down----#


def search_curseforge(mod_name):
    url = f"https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter={mod_name}&pageSize=1"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    res = requests.get(url, headers=headers)
    if res.ok and res.json()["data"]:
        return res.json()["data"][0]["id"]
    return None


def get_latest_curseforge(mod_id):
    url = f"https://api.curseforge.com/v1/mods/{mod_id}/files"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    res = requests.get(url, headers=headers)
    if not res.ok:
        return None
    for file in res.json()["data"]:
        if MINECRAFT_VERSION in file["gameVersions"] and MODLOADER in file.get("modLoaders", []):
            return file["downloadUrl"], file["fileName"]
    return None
#----------------------------#

#-------MAIN LOOP------------#
for filename in os.listdir(MODS_FOLDER):
    if not filename.endswith(".jar"):
        continue
    jar_path = os.path.join(MODS_FOLDER, filename)
    print(f"\n🔍 Đang xử lý: {filename}")

    mod_name = get_mod_info_from_jar(jar_path)
    if not mod_name:
        print("⚠️Không lấy được mod từ file fabric.mod.json.")
        mod_name = os.path.splitext(filename)[0]

    print(f"→ Tên mod: {mod_name}")

    project_id = search_modrinth(mod_name)
    if project_id:
        result = get_latest_modrinth(project_id)
        if result:
            url, new_filename = result
            save_path = os.path.join(OUTPUT_FOLDER, sanitize_filename(new_filename))
            with open(save_path, "wb") as f:
                f.write(requests.get(url).content)
            print(f"✅ (Modrinth) Tải xong: {new_filename}")
            continue
        else:
            print("⚠️ Không tìm thấy phiên bản tương thích trên Modrinth.")

    print("🔁 Đang thử với CurseForge...")
    mod_id = search_curseforge(mod_name)
    if not mod_id:
        print(f"❌ Không tìm thấy mod trên CurseForge: {mod_name}")
        continue

    result = get_latest_curseforge(mod_id)
    if result:
        url, new_filename = result
        save_path = os.path.join(OUTPUT_FOLDER, sanitize_filename(new_filename))
        with open(save_path, "wb") as f:
            f.write(requests.get(url).content)
        print(f"✅ (CurseForge) Tải xong: {new_filename}")
    else:
        print(f"❌ Không có phiên bản tương thích trên CurseForge.")
        
#---Complate-----------------#


print("\n🎉 HOÀN TẤT rồi tận hưởng đi.")

#----------------------------#

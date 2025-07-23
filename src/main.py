import os
import tkinter
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import sv_ttk
from modules.mod import ModUpdater
from datetime import datetime
from ctypes import windll

md = ModUpdater()

latest_output_folder = [""]

#--------------------------------------#
# GUI Helpers
#--------------------------------------#
def select_folder():
    folder = filedialog.askdirectory(title="Select your mod folder")
    if folder:
        folder_entry.delete(0, tkinter.END)
        folder_entry.insert(0, folder)

def open_output_folder():
    if os.path.exists(latest_output_folder[0]):
        # webbrowser.open(latest_output_folder[0])  bro are we for real 😭😭😭😭😭😭🥀🥀🥀🥀🥀
        os.startfile(latest_output_folder[0])


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
    log_box.delete(1.0, tkinter.END)

    def task():
        for file in os.listdir(mods_folder):
            if file.endswith(".jar"):
                md.update_mod(os.path.join(mods_folder, file), mc_version, loader, output_dir, log_box)
        log_box.insert(tkinter.END, f"\n🎉 Done! Files saved to: {output_dir}\n")
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

root = tkinter.Tk()
root.title("Minecraft Mod Updater")

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
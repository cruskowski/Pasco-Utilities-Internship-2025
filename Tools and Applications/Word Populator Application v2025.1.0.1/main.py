from tkinter import Tk
from tkinter import ttk
from gui.main_screen import MainScreen
from gui.settings_screen import SettingsScreen
import os
import json
import sys

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

def load_template_paths():
    """Load template paths from settings.json."""
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            data = json.load(f)
        template_names = data.get("template_names")
        if not template_names:
            template_names = [data.get("template_name", "template.docx")]
    else:
        template_names = ["template.docx"]
    return [os.path.join(os.path.dirname(__file__), "assets", name) for name in template_names]

def show_main_screen(root):
    for widget in root.winfo_children():
        widget.destroy()
    template_paths = load_template_paths()
    MainScreen(root, template_paths, lambda: show_settings_screen(root)).pack(fill="both", expand=True)

def show_settings_screen(root):
    for widget in root.winfo_children():
        widget.destroy()
    SettingsScreen(root, lambda: show_main_screen(root)).pack(fill="both", expand=True)

def main():
    root = Tk()
    root.title("Word Template Helper")
    root.minsize(400, 400)  # Set a minimum window size

    # Set a modern ttk theme
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use('vista')
    else:
        style.theme_use('clam')

    style.configure('.', font=('Segoe UI', 11))

    icon_path = resource_path(os.path.join("assets", "gen.ico"))
    root.iconbitmap(icon_path)

    show_main_screen(root)
    root.mainloop()

if __name__ == "__main__":
    main()




import json
import os
from tkinter import Tk, StringVar, PhotoImage
from tkinter import ttk, Button
from gui.settings_screen import SettingsScreen
from gui.manual_entry_screen import ManualEntryScreen
from gui.preview_screen import PreviewScreen

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "settings.json")

class MainScreen(ttk.Frame):
    def __init__(self, master, template_paths, open_settings_callback):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.master = master
        self.template_paths = template_paths
        self.open_settings_callback = open_settings_callback
        self.template_names = [os.path.basename(path) for path in template_paths]
        self.current_template_index = 0
        self.user_data = None
        self.saved_files = []
        self.master.title("Word Template Helper")
        self.frame = ttk.Frame(self.master, padding=(10, 10))
        self.frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.load_settings()

        button_font = ("Segoe UI", 14, "bold")

        self.import_file_button = Button(self.frame, text="Import File", font = button_font, height=5, width = 20)
        self.import_file_button.pack(pady=(20, 5))
          # Add some space above
        # Only the Submit Manually button
        self.manual_btn = Button(self.frame, text="Submit Manually", command=self.open_manual_entry, font = button_font, height =5, width = 20)
        self.manual_btn.pack(pady=10)


        # Gear icon settings button at bottom right
        gear_path = os.path.join(os.path.dirname(__file__), "..", "assets", "gear.png")
        self.gear_icon = PhotoImage(file=gear_path)
        self.gear_icon = self.gear_icon.subsample(20, 20)
        self.settings_btn = Button(self.master, image=self.gear_icon, command=self.open_settings_callback)
        self.settings_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # bottom right with padding

    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
                self.placeholders = data.get("placeholders", [])
        else:
            self.placeholders = [
                {"name": "Name", "syntax": "{{NAME}}"},
                {"name": "Date", "syntax": "{{DATE}}"}
            ]

    def import_file(self):
        pass

    def open_manual_entry(self):
        # Remove all widgets from the root window
        for widget in self.master.winfo_children():
            widget.destroy()
        # Show the manual entry screen as a new page
        from gui.manual_entry_screen import ManualEntryScreen
        ManualEntryScreen(self.master, self.open_settings_callback, lambda: self.__class__(self.master, self.template_paths, self.open_settings_callback))

    def open_main_screen(self):
        # This should destroy current widgets and show the main screen again
        for widget in self.master.winfo_children():
            widget.destroy()
        from gui.main_screen import MainScreen
        template_paths = []  # Or reload as needed
        MainScreen(self.master, template_paths, self.open_settings_callback)

    def show_preview(self):
        is_last = self.current_index == len(self.template_paths) - 1
        PreviewScreen(
            self.master,
            self.user_data,
            self.template_paths[self.current_index],
            on_next=self.next_preview if not is_last else None,
            on_prev=self.prev_preview if self.current_index > 0 else None,
            on_save_all=self.save_all if is_last else None
        )

    def next_preview(self):
        self.current_index += 1
        self.show_preview()

    def prev_preview(self):
        self.current_index -= 1
        self.show_preview()

    def save_all(self):
        from docx import Document
        for idx, path in enumerate(self.template_paths):
            doc = Document(path)
            for paragraph in doc.paragraphs:
                for placeholder, value in self.user_data.items():
                    paragraph.text = paragraph.text.replace(placeholder, value)
            save_path = f"PopulatedDocument_{idx+1}.docx"
            doc.save(save_path)
            self.saved_files.append(save_path)
        from tkinter import messagebox
        messagebox.showinfo("Saved", f"All documents saved:\n" + "\n".join(self.saved_files))

    def open_settings(self):
        SettingsScreen(self.master, self.reload_program)

    def reload_program(self):
        if hasattr(self, 'frame') and self.frame:
            self.frame.destroy()
        self.__init__(self.master, self.template_paths)

    def on_template_selected(self, event):
        self.current_template_index = self.template_selector.current()
        # Now use self.template_paths[self.current_template_index] as the active template
        print("Selected template:", self.template_paths[self.current_template_index])
        # You can refresh preview or other UI here

    def add_template_name(new_template_name):
        # Load current settings
        with open(SETTINGS_PATH, "r") as f:
            data = json.load(f)
        template_names = data.get("template_names", [])
        # Add only if not already present
        if new_template_name not in template_names:
            template_names.append(new_template_name)
            data["template_names"] = template_names
            with open(SETTINGS_PATH, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Added template: {new_template_name}")
        else:
            print(f"Template {new_template_name} already exists.")



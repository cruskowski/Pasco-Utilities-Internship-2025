from tkinter import Frame, Label, Entry, Button, StringVar, messagebox, Listbox, END, IntVar
from tkinter import ttk, filedialog
import os
import json

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "settings.json")
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")

class SettingsScreen(Frame):
    def __init__(self, master, on_submit_callback):
        super().__init__(master)
        self.on_submit_callback = on_submit_callback

        # --- Placeholders Section (unchanged) ---
        self.placeholder_name_var = StringVar()
        self.placeholder_syntax_var = StringVar()

        Label(self, text="Placeholder Name:").pack(padx=10, pady=2)
        self.placeholder_name_entry = Entry(self, textvariable=self.placeholder_name_var)
        self.placeholder_name_entry.pack(padx=10, pady=2)

        Label(self, text="Placeholder Syntax:").pack(padx=10, pady=2)
        self.placeholder_syntax_entry = Entry(self, textvariable=self.placeholder_syntax_var)
        self.placeholder_syntax_entry.pack(padx=10, pady=2)

        self.add_placeholder_btn = Button(self, text="Add Placeholder", command=self.add_placeholder)
        self.add_placeholder_btn.pack(padx=10, pady=2)

        Label(self, text="Placeholders:").pack(padx=10, pady=2)
        self.placeholder_listbox = Listbox(self)
        self.placeholder_listbox.pack(padx=10, pady=2)

        # Add Delete Placeholders button under the listbox
        self.delete_placeholder_btn = Button(self, text="Delete Placeholder", command=self.delete_placeholder)
        self.delete_placeholder_btn.pack(padx=10, pady=(2, 10))

        self.load_placeholders()

        # --- Template Management Section (below placeholders) ---
        Label(self, text="Load Template Documents:").pack(padx=10, pady=(20,2), anchor="w")
        file_frame = ttk.Frame(self)
        file_frame.pack(fill="x", padx=10, pady=2)
        self.template_var = StringVar()
        self.file_entry = Entry(file_frame, textvariable=self.template_var, width=40)
        self.file_entry.pack(side="left", padx=5)
        self.browse_btn = Button(file_frame, text="Browse", command=self.browse_file)
        self.browse_btn.pack(side="left", padx=5)
        self.apply_btn = Button(file_frame, text="Apply", command=self.add_template)
        self.apply_btn.pack(side="left", padx=5)

        self.templates_frame = ttk.Frame(self)
        self.templates_frame.pack(fill="x", padx=10, pady=10)
        self.template_names, self.template_vars = self.load_template_names_and_vars()
        self.render_template_checkboxes()

        # --- Delete Loaded Template Button (place above Submit) ---
        self.delete_template_btn = Button(self, text="Delete Loaded Template", command=self.delete_template)
        self.delete_template_btn.pack(pady=(0, 10))

        # --- Submit Button ---
        self.submit_btn = Button(self, text="Submit Settings", command=self.submit_settings)
        self.submit_btn.pack(pady=10)

    # --- Placeholders Logic ---
    def load_placeholders(self):
        self.placeholder_listbox.delete(0, END)
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
            self.placeholders = data.get("placeholders", [])
            for ph in self.placeholders:
                self.placeholder_listbox.insert(END, f"{ph['name']} : {ph['syntax']}")
        else:
            self.placeholders = []

    def add_placeholder(self):
        name = self.placeholder_name_var.get().strip()
        syntax = self.placeholder_syntax_var.get().strip()
        if not name or not syntax:
            messagebox.showerror("Error", "Both name and syntax are required.")
            return
        for ph in self.placeholders:
            if ph["name"] == name:
                messagebox.showerror("Error", "Placeholder name already exists.")
                return
        self.placeholders.append({"name": name, "syntax": syntax})
        self.save_placeholders()
        self.load_placeholders()
        self.placeholder_name_var.set("")
        self.placeholder_syntax_var.set("")

    def delete_placeholder(self):
        selected = self.placeholder_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a placeholder to delete.")
            return
        index = selected[0]
        del self.placeholders[index]
        self.save_placeholders()
        self.load_placeholders()

    def save_placeholders(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data["placeholders"] = self.placeholders
        with open(SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=4)

    # --- Template Management Logic ---
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
        if file_path:
            self.template_var.set(file_path)

    def add_template(self):
        file_path = self.template_var.get()
        if not file_path or not os.path.isfile(file_path):
            messagebox.showerror("Error", "Please enter a valid file path.")
            return
        dest_path = os.path.join(ASSETS_PATH, os.path.basename(file_path))
        if not os.path.exists(ASSETS_PATH):
            os.makedirs(ASSETS_PATH)
        if not os.path.exists(dest_path):
            import shutil
            shutil.copy(file_path, dest_path)
        if os.path.basename(file_path) not in self.template_names:
            self.template_names.append(os.path.basename(file_path))
            self.template_vars.append(IntVar(value=1))
            self.render_template_checkboxes()
            self.save_template_names()
        self.template_var.set("")

    def load_template_names_and_vars(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
            names = data.get("template_names", [])
        else:
            names = []
        vars_ = [IntVar(value=1) for _ in names]
        return names, vars_

    def render_template_checkboxes(self):
        for widget in self.templates_frame.winfo_children():
            widget.destroy()
        for name, var in zip(self.template_names, self.template_vars):
            chk = ttk.Checkbutton(self.templates_frame, text=name, variable=var)
            chk.pack(anchor="w")

    def save_template_names(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data["template_names"] = self.template_names
        with open(SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=4)

    def submit_settings(self):
        # Save only checked templates
        selected = [name for name, var in zip(self.template_names, self.template_vars) if var.get()]
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data["template_names"] = selected
        data["placeholders"] = self.placeholders
        with open(SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=4)
        self.on_submit_callback()

    def delete_template(self):
        # Find checked templates
        selected_indices = [i for i, var in enumerate(self.template_vars) if var.get()]
        if not selected_indices:
            messagebox.showerror("Error", "Please check a template to delete.")
            return
        # Remove selected templates (from end to start)
        for idx in reversed(selected_indices):
            del self.template_names[idx]
            del self.template_vars[idx]
        self.save_template_names()
        self.render_template_checkboxes()
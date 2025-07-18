"""
Manages the list of placeholders and their syntax.
Handles loading/saving placeholder settings.
"""

import json
import os

class PlaceholderManager:
    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.placeholders = []  # List of dicts: {"name": ..., "syntax": ...}
        self.template_name = ""
        self.load_settings()

    def add_placeholder(self, name, syntax):
        self.placeholders.append({"name": name, "syntax": syntax})

    def set_template_name(self, template_name):
        self.template_name = template_name

    def save_settings(self):
        data = {
            "placeholders": self.placeholders,
            "template_name": self.template_name
        }
        with open(self.settings_path, "w") as f:
            json.dump(data, f)

    def load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as f:
                data = json.load(f)
                self.placeholders = data.get("placeholders", [])
                self.template_name = data.get("template_name", "")
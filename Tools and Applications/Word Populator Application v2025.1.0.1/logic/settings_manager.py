from typing import Dict, Any
import json
import os

class SettingsManager:
    def __init__(self, settings_file: str):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as file:
                return json.load(file)
        return {"placeholders": {}, "template_name": ""}

    def save_settings(self) -> None:
        with open(self.settings_file, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def add_placeholder(self, name: str, syntax: str) -> None:
        self.settings["placeholders"][name] = syntax
        self.save_settings()

    def set_template_name(self, template_name: str) -> None:
        self.settings["template_name"] = template_name
        self.save_settings()

    def get_placeholders(self) -> Dict[str, str]:
        return self.settings["placeholders"]

    def get_template_name(self) -> str:
        return self.settings["template_name"]
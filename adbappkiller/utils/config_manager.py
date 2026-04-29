import configparser
import os

class ConfigManager:
    def __init__(self, filename="config.ini"):
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.filepath = os.path.join(self.base_path, filename)
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                self.config.read(self.filepath, encoding='utf-8')
            except Exception:
                self.config["SETTINGS"] = {"output_dir": ""}
        else:
            self.config["SETTINGS"] = {"output_dir": ""}

    def save(self):
        try:
            with open(self.filepath, "w", encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_output_dir(self):
        try:
            return self.config.get("SETTINGS", "output_dir", fallback=None)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None

    def set_output_dir(self, path):
        if "SETTINGS" not in self.config:
            self.config["SETTINGS"] = {}
        self.config["SETTINGS"]["output_dir"] = path
        self.save()

import json
import os

from .paths import APP_CONFIG_FILE, PROJECT_ROOT


class AppConfig:
    def __init__(self):
        self.skills_dir = os.path.join(PROJECT_ROOT, "skills")
        self.mcp_settings_file = os.path.join(PROJECT_ROOT, "mcp", "settings.json")
        self.load()

    def load(self):
        if os.path.exists(APP_CONFIG_FILE):
            try:
                with open(APP_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.skills_dir = data.get("skills_dir", self.skills_dir)
                    self.mcp_settings_file = data.get("mcp_settings_file", self.mcp_settings_file)
            except Exception:
                pass

    def save(self):
        data = {"skills_dir": self.skills_dir, "mcp_settings_file": self.mcp_settings_file}
        with open(APP_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


app_config = AppConfig()


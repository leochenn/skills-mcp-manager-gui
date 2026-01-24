import json
import os
import time

from ..paths import HISTORY_FILE


class HistoryManager:
    def __init__(self):
        self.data = {"skills_dirs": [], "mcp_files": []}
        self.load()

    def load(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)

                for key in ["skills_dirs", "mcp_files"]:
                    cleaned_list = []
                    seen_paths = set()

                    temp_items = []
                    for item in self.data.get(key, []):
                        p = ""
                        t = 0
                        if isinstance(item, str):
                            p = item
                        elif isinstance(item, dict) and "path" in item:
                            p = item["path"]
                            t = item.get("time", 0)

                        if p:
                            p = os.path.normpath(p)
                            temp_items.append({"path": p, "time": t})

                    temp_items.sort(key=lambda x: x["time"], reverse=True)

                    for item in temp_items:
                        norm_p = os.path.normcase(item["path"])
                        if norm_p not in seen_paths:
                            seen_paths.add(norm_p)
                            cleaned_list.append(item)

                    self.data[key] = cleaned_list
            except Exception:
                pass

    def save(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def _add_path(self, key, path):
        path = os.path.normpath(path)
        self.data[key] = [
            item
            for item in self.data[key]
            if os.path.normcase(item["path"]) != os.path.normcase(path)
        ]
        self.data[key].insert(0, {"path": path, "time": time.time()})
        self.data[key].sort(key=lambda x: x.get("time", 0), reverse=True)
        self.data[key] = self.data[key][:10]
        self.save()

    def _remove_path(self, key, path):
        path = os.path.normpath(path)
        self.data[key] = [
            item
            for item in self.data[key]
            if os.path.normcase(item["path"]) != os.path.normcase(path)
        ]
        self.save()

    def add_skills_dir(self, path):
        self._add_path("skills_dirs", path)

    def add_mcp_file(self, path):
        self._add_path("mcp_files", path)

    def get_skills_dirs(self):
        return [item["path"] for item in self.data.get("skills_dirs", [])]

    def get_mcp_files(self):
        return [item["path"] for item in self.data.get("mcp_files", [])]

    def remove_skills_dir(self, path):
        self._remove_path("skills_dirs", path)

    def remove_mcp_file(self, path):
        self._remove_path("mcp_files", path)

    def get_all_history(self):
        skills = []
        for item in self.data.get("skills_dirs", []):
            skills.append({**item, "type": "skill"})

        mcp = []
        for item in self.data.get("mcp_files", []):
            mcp.append({**item, "type": "mcp"})

        all_items = skills + mcp
        all_items.sort(key=lambda x: x.get("time", 0), reverse=True)
        return all_items


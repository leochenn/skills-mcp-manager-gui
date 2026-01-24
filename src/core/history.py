import json
import os
import tempfile
import time

from ..paths import HISTORY_FILE


def _coerce_item(item):
    p = ""
    t = 0
    if isinstance(item, str):
        p = item
    elif isinstance(item, dict) and "path" in item:
        p = item["path"]
        t = item.get("time", 0)
    if not p:
        return None
    return {"path": os.path.normpath(p), "time": t}


def _clean_items(items):
    temp_items = []
    for item in items or []:
        coerced = _coerce_item(item)
        if coerced:
            temp_items.append(coerced)

    temp_items.sort(key=lambda x: x["time"], reverse=True)

    cleaned_list = []
    seen_paths = set()
    for item in temp_items:
        norm_p = os.path.normcase(item["path"])
        if norm_p not in seen_paths:
            seen_paths.add(norm_p)
            cleaned_list.append(item)

    return cleaned_list


class HistoryManager:
    def __init__(self, history_file=None):
        self.history_file = history_file or HISTORY_FILE
        self.data = {"skills_dirs": [], "mcp_files": []}
        self.load()

    def load(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)

                for key in ["skills_dirs", "mcp_files"]:
                    self.data[key] = _clean_items(self.data.get(key, []))
            except Exception:
                try:
                    base, ext = os.path.splitext(self.history_file)
                    corrupted_path = f"{base}.corrupt.{int(time.time())}{ext or '.json'}"
                    os.replace(self.history_file, corrupted_path)
                except Exception:
                    pass

        for key in ["skills_dirs", "mcp_files"]:
            self.data.setdefault(key, [])

    def save(self):
        try:
            target_dir = os.path.dirname(os.path.abspath(self.history_file))
            os.makedirs(target_dir, exist_ok=True)

            fd, tmp_path = tempfile.mkstemp(
                prefix="history.",
                suffix=".tmp",
                dir=target_dir,
                text=True,
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_path, self.history_file)
            finally:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
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

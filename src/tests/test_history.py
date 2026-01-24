import json
import os
import tempfile
import unittest
from unittest.mock import patch

import src.core.history as history_mod


class TestHistoryManager(unittest.TestCase):
    def test_add_dedup_and_limit(self):
        with tempfile.TemporaryDirectory() as td:
            history_path = os.path.join(td, "history.json")

            with patch.object(history_mod, "HISTORY_FILE", history_path):
                with patch.object(history_mod.time, "time", side_effect=list(range(100, 200))):
                    hm = history_mod.HistoryManager()
                    for i in range(12):
                        hm.add_skills_dir(os.path.join("C:\\x", f"p{i}"))
                    hm.add_skills_dir(os.path.join("C:\\x", "p5"))

                    skills = hm.get_skills_dirs()
                    self.assertEqual(len(skills), 10)
                    self.assertTrue(skills[0].lower().endswith(os.path.normcase(os.path.join("C:\\x", "p5"))))

                    hm2 = history_mod.HistoryManager()
                    self.assertEqual(hm2.get_skills_dirs(), skills)

    def test_load_cleans_mixed_formats(self):
        with tempfile.TemporaryDirectory() as td:
            history_path = os.path.join(td, "history.json")
            raw = {
                "skills_dirs": [
                    {"path": "C:\\a", "time": 2},
                    "C:\\b",
                    {"path": "C:\\A", "time": 3},
                    {"path": "", "time": 4},
                ],
                "mcp_files": ["C:\\m.json", {"path": "C:\\m.json", "time": 9}],
            }
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(raw, f)

            with patch.object(history_mod, "HISTORY_FILE", history_path):
                hm = history_mod.HistoryManager()
                self.assertEqual([p.lower() for p in hm.get_skills_dirs()], [os.path.normcase("C:\\A").lower(), os.path.normcase("C:\\b").lower()])
                self.assertEqual([p.lower() for p in hm.get_mcp_files()], [os.path.normcase("C:\\m.json").lower()])

    def test_corrupted_history_is_quarantined(self):
        with tempfile.TemporaryDirectory() as td:
            history_path = os.path.join(td, "history.json")
            with open(history_path, "w", encoding="utf-8") as f:
                f.write("{")

            with patch.object(history_mod, "HISTORY_FILE", history_path):
                hm = history_mod.HistoryManager()
                self.assertEqual(hm.get_skills_dirs(), [])

                quarantined = [p for p in os.listdir(td) if p.startswith("history.corrupt.")]
                self.assertEqual(len(quarantined), 1)

                hm.add_skills_dir(os.path.join("C:\\x", "p1"))
                self.assertTrue(os.path.exists(history_path))
                with open(history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.assertEqual(len(data.get("skills_dirs", [])), 1)


if __name__ == "__main__":
    unittest.main()


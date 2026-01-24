import os
import tempfile
import unittest

from src.core.history import HistoryManager
from src.utils.fs import calculate_dir_hash
from src.utils.jsonc import load_jsonc


class TestJsonc(unittest.TestCase):
    def test_load_jsonc_basic(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "a.jsonc")
            with open(p, "w", encoding="utf-8") as f:
                f.write(
                    '{\n'
                    '  // comment\n'
                    '  "a": 1,\n'
                    '  "url": "https://example.com/x//y",\n'
                    '  /* block */\n'
                    '  "b": 2\n'
                    "}\n"
                )
            data = load_jsonc(p)
            self.assertEqual(data["a"], 1)
            self.assertEqual(data["b"], 2)
            self.assertEqual(data["url"], "https://example.com/x//y")


class TestHash(unittest.TestCase):
    def test_calculate_dir_hash_stable(self):
        with tempfile.TemporaryDirectory() as td:
            f1 = os.path.join(td, "a.txt")
            f2 = os.path.join(td, "b.txt")
            with open(f1, "wb") as f:
                f.write(b"hello")
            with open(f2, "wb") as f:
                f.write(b"world")
            h1 = calculate_dir_hash(td)
            h2 = calculate_dir_hash(td)
            self.assertEqual(h1, h2)


class TestHistory(unittest.TestCase):
    def test_history_dedup_normcase(self):
        hm = HistoryManager()
        hm.data = {"skills_dirs": [], "mcp_files": []}
        hm._add_path("skills_dirs", r"C:\Temp\Foo")
        hm._add_path("skills_dirs", r"c:\temp\foo")
        self.assertEqual(len(hm.data["skills_dirs"]), 1)


if __name__ == "__main__":
    unittest.main()


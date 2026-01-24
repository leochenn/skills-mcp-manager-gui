import os
import tempfile
import unittest

from src.core.diff import collect_diff_files


class TestDiff(unittest.TestCase):
    def test_collect_diff_files_new_modified_deleted(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
            os.makedirs(os.path.join(src, "d"))
            os.makedirs(os.path.join(tgt, "d"))

            with open(os.path.join(src, "a.txt"), "w", encoding="utf-8") as f:
                f.write("A")
            with open(os.path.join(tgt, "a.txt"), "w", encoding="utf-8") as f:
                f.write("B")

            with open(os.path.join(src, "d", "new.txt"), "w", encoding="utf-8") as f:
                f.write("N")

            with open(os.path.join(tgt, "d", "old.txt"), "w", encoding="utf-8") as f:
                f.write("O")

            out = collect_diff_files(src, tgt, ignore_patterns=[])
            self.assertEqual(out, [("a.txt", "Modified"), (os.path.join("d", "new.txt"), "New"), (os.path.join("d", "old.txt"), "Deleted")])

    def test_collect_diff_files_ignores_by_gitignore(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
            with open(os.path.join(src, ".gitignore"), "w", encoding="utf-8") as f:
                f.write("ignored_dir\nignored.txt\n")

            os.makedirs(os.path.join(src, "ignored_dir"))
            os.makedirs(os.path.join(tgt, "ignored_dir"))
            with open(os.path.join(src, "ignored_dir", "a.txt"), "w", encoding="utf-8") as f:
                f.write("A")
            with open(os.path.join(tgt, "ignored_dir", "a.txt"), "w", encoding="utf-8") as f:
                f.write("B")
            with open(os.path.join(src, "ignored.txt"), "w", encoding="utf-8") as f:
                f.write("X")

            out = collect_diff_files(src, tgt)
            self.assertEqual(out, [(".gitignore", "New")])


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest

from src.core.compare import (
    build_mcp_right_rows,
    build_skills_right_rows,
    collect_source_skill_rel_paths,
    collect_target_skill_dirs,
    read_mcp_current_data,
)


class TestSkillsCompare(unittest.TestCase):
    def test_collect_target_skill_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "a"))
            os.makedirs(os.path.join(td, "b"))
            with open(os.path.join(td, "x.txt"), "w", encoding="utf-8") as f:
                f.write("x")
            items = collect_target_skill_dirs(td)
            self.assertEqual(set(items), {"a", "b"})

    def test_collect_source_skill_rel_paths(self):
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "g1", "s1"))
            os.makedirs(os.path.join(td, "s2"))
            with open(os.path.join(td, "g1", "s1", "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("x")
            with open(os.path.join(td, "s2", "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("y")
            rels = collect_source_skill_rel_paths(td)
            self.assertEqual(set(rels), {"g1/s1", "s2"})

    def test_build_skills_right_rows_statuses(self):
        with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as target_dir:
            os.makedirs(os.path.join(skills_dir, "g1", "s1"))
            with open(os.path.join(skills_dir, "g1", "s1", "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("hello")
            with open(os.path.join(skills_dir, "g1", "s1", "a.txt"), "w", encoding="utf-8") as f:
                f.write("a")

            rows, err = build_skills_right_rows(skills_dir, target_dir)
            self.assertIsNone(err)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "🆕 新增")
            self.assertFalse(rows[0]["is_diff"])
            self.assertEqual(rows[0]["name"], "s1")
            self.assertEqual(rows[0]["group"], "g1")

            dst = os.path.join(target_dir, "s1")
            os.makedirs(dst)
            with open(os.path.join(dst, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("hello")
            with open(os.path.join(dst, "a.txt"), "w", encoding="utf-8") as f:
                f.write("a")

            rows, err = build_skills_right_rows(skills_dir, target_dir)
            self.assertIsNone(err)
            self.assertEqual(rows[0]["status"], "✅ 一致")
            self.assertFalse(rows[0]["is_diff"])

            with open(os.path.join(dst, "a.txt"), "w", encoding="utf-8") as f:
                f.write("DIFF")
            rows, err = build_skills_right_rows(skills_dir, target_dir)
            self.assertIsNone(err)
            self.assertEqual(rows[0]["status"], "⚠️ 差异")
            self.assertTrue(rows[0]["is_diff"])


class TestMcpCompare(unittest.TestCase):
    def test_read_mcp_current_data_and_build_rows(self):
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "src.jsonc")
            tgt = os.path.join(td, "tgt.jsonc")
            with open(src, "w", encoding="utf-8") as f:
                f.write(
                    '{\n  "mcpServers": {\n    "a": {"x": 1},\n    "b": {"y": 2}\n  }\n}\n'
                )
            with open(tgt, "w", encoding="utf-8") as f:
                f.write(
                    '{\n  "mcpServers": {\n    "a": {"x": 1},\n    "b": {"y": 9}\n  }\n}\n'
                )

            current_data, left_items = read_mcp_current_data(tgt)
            self.assertEqual(left_items, ["a", "b"])

            rows, err = build_mcp_right_rows(src, current_data)
            self.assertIsNone(err)
            by_key = {r["key"]: r for r in rows}
            self.assertEqual(by_key["a"]["status"], "✅ 一致")
            self.assertFalse(by_key["a"]["is_diff"])
            self.assertEqual(by_key["b"]["status"], "⚠️ 差异")
            self.assertTrue(by_key["b"]["is_diff"])


if __name__ == "__main__":
    unittest.main()


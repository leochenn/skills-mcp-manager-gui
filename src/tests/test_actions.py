import os
import tempfile
import unittest

from src.core.actions import (
    delete_mcp_servers,
    delete_skill_dirs,
    get_install_final_output_dir,
    parse_github_tree_url,
    import_mcp_servers,
    import_skills_to_target,
)


class TestSkillActions(unittest.TestCase):
    def test_import_skills_to_target_flattens_and_overwrites(self):
        with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as target_dir:
            src_skill = os.path.join(skills_dir, "g1", "s1")
            os.makedirs(src_skill)
            with open(os.path.join(src_skill, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("desc")
            with open(os.path.join(src_skill, "a.txt"), "w", encoding="utf-8") as f:
                f.write("A")

            dst_skill = os.path.join(target_dir, "s1")
            os.makedirs(dst_skill)
            with open(os.path.join(dst_skill, "a.txt"), "w", encoding="utf-8") as f:
                f.write("OLD")

            errs = import_skills_to_target(
                skills_dir,
                target_dir,
                [{"rel_path": "g1/s1", "name": "s1"}],
            )
            self.assertEqual(errs, [])
            self.assertTrue(os.path.exists(os.path.join(dst_skill, "SKILL.md")))
            with open(os.path.join(dst_skill, "a.txt"), "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "A")

    def test_delete_skill_dirs(self):
        with tempfile.TemporaryDirectory() as target_dir:
            os.makedirs(os.path.join(target_dir, "a"))
            os.makedirs(os.path.join(target_dir, "b"))
            errs = delete_skill_dirs(target_dir, ["a", "b"])
            self.assertEqual(errs, [])
            self.assertFalse(os.path.exists(os.path.join(target_dir, "a")))
            self.assertFalse(os.path.exists(os.path.join(target_dir, "b")))


class TestMcpActions(unittest.TestCase):
    def test_delete_mcp_servers(self):
        data = {"mcpServers": {"a": {"x": 1}, "b": {"y": 2}}}
        out = delete_mcp_servers(data, ["a", "missing"])
        self.assertEqual(set(out["mcpServers"].keys()), {"b"})

    def test_import_mcp_servers(self):
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "src.jsonc")
            with open(src, "w", encoding="utf-8") as f:
                f.write('{ "mcpServers": { "a": {"x": 1}, "b": {"y": 2} } }')

            cur = {"mcpServers": {"a": {"x": 0}}}
            out = import_mcp_servers(cur, src, ["a", "b", "missing"])
            self.assertEqual(out["mcpServers"]["a"], {"x": 1})
            self.assertEqual(out["mcpServers"]["b"], {"y": 2})


if __name__ == "__main__":
    unittest.main()


class TestInstallActions(unittest.TestCase):
    def test_get_install_final_output_dir_valid(self):
        out = get_install_final_output_dir(
            "https://github.com/owner/repo/tree/main/path/to/skill",
            r"C:\Target",
        )
        self.assertEqual(out, os.path.join(r"C:\Target", "owner", "skill"))

    def test_get_install_final_output_dir_trailing_slash(self):
        out = get_install_final_output_dir(
            "https://github.com/owner/repo/tree/main/path/to/skill/",
            r"C:\Target",
        )
        self.assertEqual(out, os.path.join(r"C:\Target", "owner", "skill"))

    def test_get_install_final_output_dir_keeps_query_fragment(self):
        out = get_install_final_output_dir(
            "https://github.com/owner/repo/tree/main/path/to/skill?x=1#y",
            r"C:\Target",
        )
        self.assertEqual(out, os.path.join(r"C:\Target", "owner", "skill"))

    def test_get_install_final_output_dir_without_scheme(self):
        out = get_install_final_output_dir(
            "github.com/owner/repo/tree/main/path/to/skill",
            r"C:\Target",
        )
        self.assertEqual(out, os.path.join(r"C:\Target", "owner", "skill"))

    def test_get_install_final_output_dir_invalid(self):
        out = get_install_final_output_dir("not a url", r"C:\Target")
        self.assertIsNone(out)


class TestGitHubUrlParsing(unittest.TestCase):
    def test_parse_github_tree_url_valid(self):
        out = parse_github_tree_url("https://github.com/owner/repo/tree/main/path/to/skill")
        self.assertEqual(
            out,
            {
                "owner": "owner",
                "repo": "repo",
                "branch": "main",
                "folder_path": "path/to/skill",
                "skill_name": "skill",
            },
        )

    def test_parse_github_tree_url_not_github(self):
        out = parse_github_tree_url("https://example.com/owner/repo/tree/main/x")
        self.assertEqual(out.get("error"), "not_github")

    def test_parse_github_tree_url_parse_failed(self):
        out = parse_github_tree_url("https://github.com/owner/repo")
        self.assertEqual(out.get("error"), "parse_failed")

    def test_parse_github_tree_url_trailing_slash(self):
        out = parse_github_tree_url("https://github.com/owner/repo/tree/main/path/to/skill/")
        self.assertEqual(out.get("folder_path"), "path/to/skill")
        self.assertEqual(out.get("skill_name"), "skill")

    def test_parse_github_tree_url_keeps_query_fragment(self):
        out = parse_github_tree_url("https://github.com/owner/repo/tree/main/path/to/skill?x=1#y")
        self.assertEqual(out.get("folder_path"), "path/to/skill")
        self.assertEqual(out.get("skill_name"), "skill")

    def test_parse_github_tree_url_without_scheme(self):
        out = parse_github_tree_url("github.com/owner/repo/tree/main/path/to/skill")
        self.assertEqual(out.get("owner"), "owner")
        self.assertEqual(out.get("repo"), "repo")
        self.assertEqual(out.get("branch"), "main")
        self.assertEqual(out.get("folder_path"), "path/to/skill")
        self.assertEqual(out.get("skill_name"), "skill")

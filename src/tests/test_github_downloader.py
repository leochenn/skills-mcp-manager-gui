import os
import tempfile
import unittest
from unittest import mock

from src.core.github_downloader import GitHubDownloader


class _Resp:
    def __init__(self, status_code=200, json_data=None, content=b""):
        self.status_code = status_code
        self._json_data = json_data
        self.content = content

    def json(self):
        return self._json_data


class TestGitHubDownloader(unittest.TestCase):
    def test_download_single_skill_writes_files(self):
        logs = []

        def log_cb(msg, level="info"):
            logs.append((level, msg))

        def fake_get(url, headers=None):
            if url.startswith("https://api.github.com/repos/owner/repo/contents/path/to/skill?ref=main"):
                return _Resp(
                    200,
                    [
                        {
                            "type": "file",
                            "name": "SKILL.md",
                            "download_url": "https://download/SKILL.md",
                        },
                        {
                            "type": "file",
                            "name": "a.txt",
                            "download_url": "https://download/a.txt",
                        },
                    ],
                )
            if url == "https://download/SKILL.md":
                return _Resp(200, None, b"hello")
            if url == "https://download/a.txt":
                return _Resp(200, None, b"world")
            return _Resp(404, None, b"")

        with tempfile.TemporaryDirectory() as td, mock.patch(
            "src.core.github_downloader.requests.get", side_effect=fake_get
        ):
            d = GitHubDownloader(log_cb)
            ok = d.download(
                "https://github.com/owner/repo/tree/main/path/to/skill",
                td,
            )
            self.assertTrue(ok)
            skill_dir = os.path.join(td, "owner", "skill")
            self.assertTrue(os.path.isdir(skill_dir))
            with open(os.path.join(skill_dir, "SKILL.md"), "rb") as f:
                self.assertEqual(f.read(), b"hello")
            with open(os.path.join(skill_dir, "a.txt"), "rb") as f:
                self.assertEqual(f.read(), b"world")

    def test_download_collection_hoists_child_skill(self):
        logs = []

        def log_cb(msg, level="info"):
            logs.append((level, msg))

        def fake_get(url, headers=None):
            if url.startswith("https://api.github.com/repos/owner/repo/contents/skills?ref=main"):
                return _Resp(
                    200,
                    [
                        {"type": "dir", "name": "child", "url": "https://api/child"},
                        {"type": "dir", "name": "other", "url": "https://api/other"},
                    ],
                )
            if url == "https://api/child":
                return _Resp(
                    200,
                    [
                        {
                            "type": "file",
                            "name": "SKILL.md",
                            "download_url": "https://download/child/SKILL.md",
                        }
                    ],
                )
            if url == "https://api/other":
                return _Resp(200, [{"type": "file", "name": "readme.txt", "download_url": "https://download/other/readme.txt"}])
            if url == "https://download/child/SKILL.md":
                return _Resp(200, None, b"child-skill")
            if url == "https://download/other/readme.txt":
                return _Resp(200, None, b"ignore")
            return _Resp(404, None, b"")

        with tempfile.TemporaryDirectory() as td, mock.patch(
            "src.core.github_downloader.requests.get", side_effect=fake_get
        ):
            d = GitHubDownloader(log_cb)
            ok = d.download(
                "https://github.com/owner/repo/tree/main/skills",
                td,
            )
            self.assertTrue(ok)
            child_dir = os.path.join(td, "owner", "child")
            self.assertTrue(os.path.isdir(child_dir))
            with open(os.path.join(child_dir, "SKILL.md"), "rb") as f:
                self.assertEqual(f.read(), b"child-skill")

    def test_record_address_merges_siblings(self):
        logs = []

        def log_cb(msg, level="info"):
            logs.append((level, msg))

        with tempfile.TemporaryDirectory() as td:
            owner_dir = os.path.join(td, "owner")
            d = GitHubDownloader(log_cb)
            d._record_address(
                owner_dir,
                "https://github.com/owner/repo/tree/main/.agents/skills/art",
            )
            d._record_address(
                owner_dir,
                "https://github.com/owner/repo/tree/main/.agents/skills/brand",
            )
            addr_file = os.path.join(owner_dir, "github_address.txt")
            self.assertTrue(os.path.exists(addr_file))
            with open(addr_file, "r", encoding="utf-8") as f:
                lines = [x.strip() for x in f.read().splitlines() if x.strip()]
            self.assertEqual(lines, ["https://github.com/owner/repo/tree/main/.agents/skills"])


if __name__ == "__main__":
    unittest.main()


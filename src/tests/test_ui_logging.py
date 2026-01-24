import unittest

from src.ui.style.logging import get_log_icon_and_color


class TestUiLogging(unittest.TestCase):
    def test_error(self):
        colors = {"danger": "D", "success": "S", "primary": "P"}
        icon, color = get_log_icon_and_color("error", colors)
        self.assertEqual(icon, "❌ ")
        self.assertEqual(color, "D")

    def test_success(self):
        colors = {"danger": "D", "success": "S", "primary": "P"}
        icon, color = get_log_icon_and_color("success", colors)
        self.assertEqual(icon, "✅ ")
        self.assertEqual(color, "S")

    def test_dir(self):
        colors = {"danger": "D", "success": "S", "primary": "P"}
        icon, color = get_log_icon_and_color("dir", colors)
        self.assertEqual(icon, "📁 ")
        self.assertEqual(color, "P")

    def test_file_start(self):
        colors = {"danger": "D", "success": "S", "primary": "P"}
        icon, color = get_log_icon_and_color("file_start", colors)
        self.assertEqual(icon, "⬇️ ")
        self.assertIsNone(color)

    def test_default(self):
        colors = {"danger": "D", "success": "S", "primary": "P"}
        icon, color = get_log_icon_and_color("info", colors)
        self.assertEqual(icon, "")
        self.assertIsNone(color)


if __name__ == "__main__":
    unittest.main()

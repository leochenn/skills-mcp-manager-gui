import unittest

from src.ui.style.status import status_to_color


class TestUiStatus(unittest.TestCase):
    def test_status_to_color(self):
        colors = {"warning": "W", "success": "S"}
        self.assertEqual(status_to_color("✅ 一致", colors), "gray")
        self.assertEqual(status_to_color("⚠️ 差异", colors), "W")
        self.assertEqual(status_to_color("🆕 新增", colors), "S")


if __name__ == "__main__":
    unittest.main()

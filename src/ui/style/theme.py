from ..platform.deps import ctk


COLORS = {
    "primary": "#0067c0",
    "primary_hover": "#005a9e",
    "text_link": ("#0067c0", "#66b2ff"),
    "text_nested": ("#5c2d91", "#b4a0ff"),
    "success": "#107c10",
    "success_bg": ("#e6ffec", "#1e3a29"),
    "success_text": ("#107c10", "#00e676"),
    "warning": "#d83b01",
    "warning_bg": ("#ffebe9", "#3a1e1e"),
    "warning_text": ("#d83b01", "#ffaa44"),
    "danger": "#a80000",
    "bg_card": ("#ffffff", "#2b2b2b"),
    "item_card": ("#f8f9fa", "gray25"),
    "item_hover": ("#eef0f2", "gray30"),
    "text_sub": ("#606060", "#a0a0a0"),
    "neutral_bg": ("#f3f2f1", "gray35"),
    "neutral_text": ("#605e5c", "#c8c8c8"),
}


def setup_theme():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

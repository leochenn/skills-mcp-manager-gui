from ..platform.deps import ctk
from ..utils.window_utils import center_window_relative


class DescriptionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title(title)
        center_window_relative(self, parent, 600, 400)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()

        self.textbox = ctk.CTkTextbox(self, wrap="word", font=("Segoe UI", 12))
        self.textbox.pack(fill="both", expand=True, padx=20, pady=20)
        self.textbox.insert("1.0", content)
        self.textbox.configure(state="disabled")

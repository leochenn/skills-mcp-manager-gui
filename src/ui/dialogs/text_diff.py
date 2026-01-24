import difflib

from ..platform.deps import ctk
from ..utils.window_utils import center_window_relative


class TextDiffDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, text_source, text_target):
        super().__init__(parent)
        self.title(title)
        center_window_relative(self, parent, 900, 700)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()

        self.text_area = ctk.CTkTextbox(self, font=("Consolas", 12), wrap="none")
        self.text_area.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_diff(text_source, text_target)

    def show_diff(self, source, target):
        self.configure_tags()
        try:
            src_lines = source.splitlines(keepends=True)
            tgt_lines = target.splitlines(keepends=True)
            diff = difflib.unified_diff(tgt_lines, src_lines, fromfile="Target", tofile="Source")
            for line in diff:
                tag = None
                if line.startswith("---"):
                    tag = "diff_header_remove"
                elif line.startswith("+++"):
                    tag = "diff_header_add"
                elif line.startswith("@@"):
                    tag = "diff_info"
                elif line.startswith("+"):
                    tag = "diff_add"
                elif line.startswith("-"):
                    tag = "diff_remove"

                if tag:
                    self.text_area.insert("end", line, tag)
                else:
                    self.text_area.insert("end", line)
        except Exception as e:
            self.text_area.insert("end", f"Error: {e}")

    def configure_tags(self):
        try:
            mode = self.text_area._get_appearance_mode()
            text_widget = self.text_area._textbox
            if mode == "light":
                text_widget.tag_config("diff_add", foreground="#00a000", background="#e6ffec")
                text_widget.tag_config(
                    "diff_remove", foreground="#d00000", background="#ffebe9"
                )
                text_widget.tag_config("diff_info", foreground="#0000ff")
                text_widget.tag_config("diff_header_remove", foreground="#d00000")
                text_widget.tag_config("diff_header_add", foreground="#00a000")
            else:
                text_widget.tag_config("diff_add", foreground="#4caf50")
                text_widget.tag_config("diff_remove", foreground="#f44336")
                text_widget.tag_config("diff_info", foreground="#2196f3")
                text_widget.tag_config("diff_header_remove", foreground="#f44336")
                text_widget.tag_config("diff_header_add", foreground="#4caf50")
        except Exception:
            pass

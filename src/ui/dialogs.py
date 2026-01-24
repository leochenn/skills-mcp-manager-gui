import difflib
import json
import os
import shutil

from .deps import ctk
from .theme import COLORS
from .window_utils import center_window_relative
from ..utils.fs import get_ignore_patterns, is_text_file


class DiffViewerDialog(ctk.CTkToplevel):
    def __init__(self, parent, skill_name, source_path, target_path):
        super().__init__(parent)
        self.title(f"差异对比: {skill_name}")
        center_window_relative(self, parent, 1000, 800)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()

        self.source_path = source_path
        self.target_path = target_path

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.lbl_files = ctk.CTkLabel(
            self.left_frame, text="变动文件", font=("Segoe UI", 14, "bold")
        )
        self.lbl_files.pack(pady=5)

        self.file_list = ctk.CTkScrollableFrame(self.left_frame)
        self.file_list.pack(fill="both", expand=True, padx=5, pady=5)

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.right_frame, text="内容对比", font=("Segoe UI", 14, "bold")).pack(
            pady=5
        )

        self.text_area = ctk.CTkTextbox(self.right_frame, font=("Consolas", 12), wrap="none")
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)

        self.configure_tags()
        self.analyze_files()

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

    def analyze_files(self):
        self.diff_files = []

        patterns = get_ignore_patterns(self.source_path)
        ignore_func = shutil.ignore_patterns(*patterns) if patterns else None

        def walk_with_ignore(path):
            for root, dirs, files in os.walk(path):
                if ignore_func:
                    ignored = ignore_func(root, dirs + files)
                    dirs[:] = [d for d in dirs if d not in ignored]
                    files[:] = [f for f in files if f not in ignored]
                yield root, dirs, files

        for root, _, files in walk_with_ignore(self.source_path):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), self.source_path)
                tgt_f = os.path.join(self.target_path, rel_path)
                src_f = os.path.join(self.source_path, rel_path)

                if not os.path.exists(tgt_f):
                    self.diff_files.append((rel_path, "New"))
                elif self.is_different(src_f, tgt_f):
                    self.diff_files.append((rel_path, "Modified"))

        for root, _, files in walk_with_ignore(self.target_path):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), self.target_path)
                if not os.path.exists(os.path.join(self.source_path, rel_path)):
                    self.diff_files.append((rel_path, "Deleted"))

        self.diff_files.sort(key=lambda x: x[0])
        self.lbl_files.configure(text=f"变动文件 ({len(self.diff_files)})")

        for f, status in self.diff_files:
            btn = ctk.CTkButton(
                self.file_list,
                text=f"[{status}] {f}",
                anchor="w",
                fg_color="transparent",
                text_color=COLORS["text_sub"],
                hover_color=("gray90", "gray20"),
                command=lambda f=f, s=status: self.show_file_diff(f, s),
            )
            btn.pack(fill="x", pady=1)

    def is_different(self, f1, f2):
        try:
            with open(f1, "rb") as a, open(f2, "rb") as b:
                return a.read() != b.read()
        except Exception:
            return True

    def show_file_diff(self, rel_path, status):
        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", f"File: {rel_path} ({status})\n\n")

        if not is_text_file(rel_path):
            self.text_area.insert("end", "[Binary or unsupported text file diff]\n")
            return

        src_f = os.path.join(self.source_path, rel_path)
        tgt_f = os.path.join(self.target_path, rel_path)

        try:
            src_lines = []
            if os.path.exists(src_f):
                with open(src_f, "r", encoding="utf-8", errors="ignore") as f:
                    src_lines = f.readlines()

            tgt_lines = []
            if os.path.exists(tgt_f):
                with open(tgt_f, "r", encoding="utf-8", errors="ignore") as f:
                    tgt_lines = f.readlines()

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
            self.text_area.insert("end", f"Error: {e}\n")


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


class LoadingOverlay(ctk.CTkToplevel):
    def __init__(self, master, message="正在加载..."):
        super().__init__(master)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.transient(master)

        self.configure(fg_color=("gray95", "gray10"))
        self.attributes("-alpha", 0.9)

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.spinner = ctk.CTkProgressBar(self.center_frame, width=200, mode="indeterminate")
        self.spinner.pack(pady=20)
        self.spinner.start()

        self.label = ctk.CTkLabel(self.center_frame, text=message, font=("Segoe UI", 16))
        self.label.pack()

    def set_message(self, text):
        self.label.configure(text=text)


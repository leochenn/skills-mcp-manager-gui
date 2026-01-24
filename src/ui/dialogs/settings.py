import tkinter as tk
from tkinter import filedialog

from ...config import app_config
from ..platform.deps import ctk
from ..style.theme import COLORS
from ..utils.window_utils import center_window_relative


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("设置")
        center_window_relative(self, parent, 600, 350)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()

        self.skills_var = tk.StringVar(value=app_config.skills_dir)
        self.mcp_var = tk.StringVar(value=app_config.mcp_settings_file)

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="默认 Skills 仓库目录:", font=("Segoe UI", 12, "bold")).pack(
            anchor="w"
        )
        f1 = ctk.CTkFrame(frame, fg_color="transparent")
        f1.pack(fill="x", pady=(5, 15))
        ctk.CTkEntry(f1, textvariable=self.skills_var).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            f1, text="浏览", width=60, command=self.browse_skills, fg_color=COLORS["primary"]
        ).pack(side="left", padx=(5, 0))

        ctk.CTkLabel(frame, text="默认 MCP 配置文件:", font=("Segoe UI", 12, "bold")).pack(
            anchor="w"
        )
        f2 = ctk.CTkFrame(frame, fg_color="transparent")
        f2.pack(fill="x", pady=(5, 15))
        ctk.CTkEntry(f2, textvariable=self.mcp_var).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            f2, text="浏览", width=60, command=self.browse_mcp, fg_color=COLORS["primary"]
        ).pack(side="left", padx=(5, 0))

        ctk.CTkButton(frame, text="保存设置", command=self.save, fg_color=COLORS["primary"]).pack(
            side="right", pady=20
        )

    def browse_skills(self):
        path = filedialog.askdirectory(initialdir=self.skills_var.get())
        if path:
            self.skills_var.set(path)

    def browse_mcp(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            self.mcp_var.set(path)

    def save(self):
        app_config.skills_dir = self.skills_var.get()
        app_config.mcp_settings_file = self.mcp_var.get()
        app_config.save()
        self.destroy()

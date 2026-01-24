import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from ...config import app_config
from ...core.actions import get_install_final_output_dir
from ...core.github_downloader import GitHubDownloader
from ..platform.deps import ctk
from ..style.icons import ICON_BACK, load_icon
from ..style.logging import get_log_icon_and_color
from ..style.theme import COLORS


class InstallSkillsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.icon_back = load_icon(ICON_BACK, size=(16, 16))

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(
            header,
            text=" 返回",
            image=self.icon_back,
            command=controller.show_home,
            width=80,
            fg_color="transparent",
            border_width=1,
            text_color=("black", "white"),
        ).pack(side="left")
        ctk.CTkLabel(
            header, text="安装 Skills", font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"]
        ).pack(side="left", padx=20)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        input_frame = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        input_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(input_frame, text="GitHub 目录链接:", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(20, 5)
        )
        self.url_entry = ctk.CTkEntry(
            input_frame, placeholder_text="例如: https://github.com/langgenius/dify/tree/main/.agents/skills"
        )
        self.url_entry.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(input_frame, text="安装目标目录:", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(5, 5)
        )
        dir_box = ctk.CTkFrame(input_frame, fg_color="transparent")
        dir_box.pack(fill="x", padx=20, pady=(0, 20))

        self.target_var = tk.StringVar(value=app_config.skills_dir)
        ctk.CTkEntry(dir_box, textvariable=self.target_var).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            dir_box, text="浏览", width=60, command=self.browse_target, fg_color=COLORS["primary"]
        ).pack(side="left", padx=(5, 0))

        self.btn_install = ctk.CTkButton(
            input_frame,
            text="开始安装",
            command=self.start_install,
            fg_color=COLORS["primary"],
            height=40,
            font=("Segoe UI", 14, "bold"),
        )
        self.btn_install.pack(fill="x", padx=20, pady=(0, 20))

        log_frame = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        log_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(log_frame, text="安装进度", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(10, 5)
        )

        self.log_area = ctk.CTkScrollableFrame(log_frame, fg_color="transparent")
        self.log_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def browse_target(self):
        path = filedialog.askdirectory(initialdir=self.target_var.get())
        if path:
            self.target_var.set(path)

    def log(self, text, type="info"):
        self.after(0, lambda: self._add_log_item(text, type))

    def _add_log_item(self, text, type):
        row = ctk.CTkFrame(self.log_area, fg_color="transparent")
        row.pack(fill="x", pady=0)

        icon, color = get_log_icon_and_color(type, COLORS)

        kwargs = {"text": icon + text, "anchor": "w", "font": ("Consolas", 12)}
        if color:
            kwargs["text_color"] = color

        ctk.CTkLabel(row, **kwargs).pack(fill="x")

        self.update_idletasks()
        try:
            self.log_area._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def start_install(self):
        if hasattr(self, "is_installing") and self.is_installing:
            if self.downloader:
                self.downloader.stop_flag = True
                self.log("正在停止下载...", "warning")
                self.btn_install.configure(state="disabled", text="正在停止...")
            return

        url = self.url_entry.get().strip()
        target = self.target_var.get().strip()

        if not url:
            return messagebox.showerror("错误", "请输入 GitHub 链接")
        if not target:
            return messagebox.showerror("错误", "请选择目标目录")

        final_output_dir = get_install_final_output_dir(url, target)
        if final_output_dir and os.path.exists(final_output_dir):
            if not messagebox.askyesno("确认覆盖", f"目标目录已存在，是否覆盖？\n\n{final_output_dir}"):
                return

        if not os.path.exists(target):
            try:
                os.makedirs(target)
            except Exception as e:
                return messagebox.showerror("错误", f"无法创建目录: {e}")

        self.is_installing = True
        self.btn_install.configure(
            state="normal", text="停止安装", fg_color=COLORS["warning"], hover_color="#b33000"
        )

        for widget in self.log_area.winfo_children():
            widget.destroy()

        threading.Thread(target=self._run_install, args=(url, target), daemon=True).start()

    def _run_install(self, url, target):
        self.downloader = GitHubDownloader(self.log)
        success = self.downloader.download(url, target)
        self.is_installing = False
        self.downloader = None

        if success:
            self.after(0, lambda: self._install_finished("success"))
        else:
            self.after(0, lambda: self._install_finished("error"))

    def _install_finished(self, status):
        if status == "success":
            self.btn_install.configure(state="normal", text="已安装", fg_color=COLORS["primary"])
        else:
            self.btn_install.configure(state="normal", text="重试安装", fg_color=COLORS["primary"])

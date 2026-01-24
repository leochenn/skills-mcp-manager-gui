import os
from tkinter import filedialog, messagebox

from ..platform.deps import ctk
from ..dialogs import SettingsDialog
from ..style.icons import ICON_DELETE, ICON_FOLDER, ICON_IMPORT, ICON_MCP, ICON_SETTINGS, load_icon
from ..style.theme import COLORS


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.icon_skills = load_icon(ICON_FOLDER, size=(24, 24))
        self.icon_mcp = load_icon(ICON_MCP, size=(24, 24))
        self.icon_install = load_icon(ICON_IMPORT, size=(24, 24))
        self.icon_settings = load_icon(ICON_SETTINGS, size=(20, 20))

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=30)

        ctk.CTkLabel(
            header,
            text="Gemini Skills & MCP Manager",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["primary"],
        ).pack(side="left")
        ctk.CTkButton(
            header,
            text="",
            image=self.icon_settings,
            width=40,
            height=40,
            fg_color="transparent",
            hover_color=("gray90", "gray20"),
            command=self.open_settings,
        ).pack(side="right")

        dash_frame = ctk.CTkFrame(self, fg_color="transparent")
        dash_frame.pack(fill="x", padx=40, pady=20)

        self.create_dash_card(
            dash_frame, "Skills 管理", "管理和同步 AI Skills", self.icon_skills, self.on_manage_skills
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.create_dash_card(
            dash_frame, "安装 Skills", "从 GitHub 下载 Skills", self.icon_install, self.on_install_skills
        ).pack(side="left", fill="x", expand=True, padx=5)
        self.create_dash_card(
            dash_frame, "MCP 管理", "管理 MCP 服务器配置", self.icon_mcp, self.on_manage_mcp
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

        ctk.CTkLabel(self, text="最近使用的项目", font=("Segoe UI", 16, "bold"), anchor="w").pack(
            fill="x", padx=40, pady=(30, 10)
        )

        self.history_frame = ctk.CTkScrollableFrame(
            self, fg_color=("white", "gray20"), corner_radius=10, height=300
        )
        self.history_frame.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        self.refresh_history()

    def create_dash_card(self, parent, title, subtitle, icon, command):
        frame = ctk.CTkFrame(
            parent,
            fg_color=("white", "gray20"),
            corner_radius=10,
            border_width=1,
            border_color=("gray90", "gray30"),
        )

        def on_click(e):
            command()

        frame.bind("<Button-1>", on_click)

        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=20, pady=20)
        content.bind("<Button-1>", on_click)

        widgets = [frame, content]

        if icon:
            lbl_icon = ctk.CTkLabel(content, text="", image=icon)
            lbl_icon.pack(side="left", padx=(0, 15))
            lbl_icon.bind("<Button-1>", on_click)
            widgets.append(lbl_icon)

        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.pack(side="left", fill="y")
        text_frame.bind("<Button-1>", on_click)
        widgets.append(text_frame)

        l1 = ctk.CTkLabel(
            text_frame,
            text=title,
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["primary"],
            anchor="w",
        )
        l1.pack(anchor="w")
        l1.bind("<Button-1>", on_click)
        widgets.append(l1)

        l2 = ctk.CTkLabel(text_frame, text=subtitle, font=("Segoe UI", 12), text_color="gray", anchor="w")
        l2.pack(anchor="w")
        l2.bind("<Button-1>", on_click)
        widgets.append(l2)

        arrow = ctk.CTkLabel(content, text=">", font=("Segoe UI", 16, "bold"), text_color="gray")
        arrow.pack(side="right")
        arrow.bind("<Button-1>", on_click)
        widgets.append(arrow)

        def on_enter(e):
            frame.configure(border_color=COLORS["primary"])

        def on_leave(e):
            try:
                x, y = frame.winfo_pointerxy()
                widget_x = frame.winfo_rootx()
                widget_y = frame.winfo_rooty()
                if not (
                    widget_x <= x <= widget_x + frame.winfo_width()
                    and widget_y <= y <= widget_y + frame.winfo_height()
                ):
                    frame.configure(border_color=("gray90", "gray30"))
            except Exception:
                pass

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        return frame

    def refresh_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        icon_folder = load_icon(ICON_FOLDER, size=(20, 20))
        icon_file = load_icon(ICON_MCP, size=(20, 20))
        icon_del = load_icon(ICON_DELETE, size=(16, 16))

        def add_item(path, icon, command, delete_command):
            row = ctk.CTkFrame(self.history_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            content_frame = ctk.CTkFrame(row, fg_color="transparent")
            content_frame.pack(side="left", fill="x", expand=True)

            lbl_icon = ctk.CTkLabel(content_frame, text="", image=icon)
            lbl_icon.pack(side="left", padx=(0, 10))

            text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)

            lbl_name = ctk.CTkLabel(
                text_frame,
                text=os.path.basename(path),
                anchor="w",
                font=("Segoe UI", 12, "bold"),
                text_color=("black", "white"),
            )
            lbl_name.pack(anchor="w")

            lbl_path = ctk.CTkLabel(text_frame, text=path, anchor="w", font=("Segoe UI", 10), text_color="gray")
            lbl_path.pack(anchor="w")

            def on_click(e):
                command()

            def on_enter(e):
                row.configure(fg_color=("gray90", "gray25"))
                content_frame.configure(fg_color=("gray90", "gray25"))

            def on_leave(e):
                row.configure(fg_color="transparent")
                content_frame.configure(fg_color="transparent")

            for w in [row, content_frame, lbl_icon, text_frame, lbl_name, lbl_path]:
                w.bind("<Button-1>", on_click)
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)

            del_btn = ctk.CTkButton(
                row,
                text="",
                image=icon_del,
                width=30,
                height=30,
                fg_color="transparent",
                hover_color=("mistyrose", "darkred"),
                command=delete_command,
            )
            del_btn.pack(side="right", padx=5)

        all_items = self.controller.history_manager.get_all_history()

        for item in all_items:
            path = item["path"]
            if item["type"] == "skill":
                add_item(
                    path,
                    icon_folder,
                    lambda p=path: self.open_skill_path(p),
                    lambda p=path: self.del_skill(p),
                )
            else:
                add_item(
                    path,
                    icon_file,
                    lambda p=path: self.open_mcp_path(p),
                    lambda p=path: self.del_mcp(p),
                )

        if not all_items:
            ctk.CTkLabel(self.history_frame, text="暂无历史记录", text_color="gray").pack(pady=20)

    def open_settings(self):
        SettingsDialog(self)

    def on_manage_skills(self):
        path = filedialog.askdirectory(title="选择 Skills 目标目录")
        if path:
            self.controller.show_skills_page(path)

    def on_install_skills(self):
        self.controller.show_install_skills_page()

    def on_manage_mcp(self):
        path = filedialog.askopenfilename(title="选择 settings.json", filetypes=[("JSON", "*.json")])
        if path:
            self.controller.show_mcp_page(path)

    def open_skill_path(self, path):
        if os.path.exists(path):
            self.controller.show_skills_page(path)
        else:
            messagebox.showerror("错误", "目录不存在")

    def open_mcp_path(self, path):
        if os.path.exists(path):
            self.controller.show_mcp_page(path)
        else:
            messagebox.showerror("错误", "文件不存在")

    def del_skill(self, path):
        self.controller.history_manager.remove_skills_dir(path)
        self.refresh_history()

    def del_mcp(self, path):
        self.controller.history_manager.remove_mcp_file(path)
        self.refresh_history()

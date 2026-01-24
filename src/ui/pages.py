import json
import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from ..config import app_config
from ..core.github_downloader import GitHubDownloader
from ..utils.fs import calculate_dir_hash, get_ignore_patterns, get_skill_description
from ..utils.jsonc import load_jsonc
from .components import CompareListFrame, ScrollableCheckBoxFrame
from .deps import ctk
from .dialogs import DescriptionDialog, DiffViewerDialog, TextDiffDialog
from .icons import (
    ICON_BACK,
    ICON_DELETE,
    ICON_FOLDER,
    ICON_IMPORT,
    ICON_MCP,
    ICON_SETTINGS,
    load_icon,
)
from .theme import COLORS
from .window_utils import center_window_relative, show_message


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

        def add_item(path, type_name, icon, command, delete_command):
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
                    "Skill",
                    icon_folder,
                    lambda p=path: self.open_skill_path(p),
                    lambda p=path: self.del_skill(p),
                )
            else:
                add_item(
                    path,
                    "MCP",
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


class SkillsManagerPage(ctk.CTkFrame):
    def __init__(self, parent, controller, target_dir):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.target_dir = target_dir

        self.icon_back = load_icon(ICON_BACK, size=(16, 16))
        self.icon_import = load_icon(ICON_IMPORT, size=(16, 16))
        self.icon_del = load_icon(ICON_DELETE, size=(16, 16))

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

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20)
        ctk.CTkLabel(
            title_box, text="管理 Skills", font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"]
        ).pack(anchor="w")
        ctk.CTkLabel(title_box, text=target_dir, font=("Segoe UI", 12), text_color="gray").pack(
            anchor="w"
        )

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_card = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(left_card, text="📂 当前项目 (本地)", font=("Segoe UI", 14, "bold")).pack(
            pady=10, padx=10, anchor="w"
        )
        self.left_list = ScrollableCheckBoxFrame(left_card)
        self.left_list.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(
            left_card,
            text=" 删除选中",
            image=self.icon_del,
            fg_color=COLORS["danger"],
            hover_color="#800000",
            command=self.delete_selected,
        ).pack(fill="x", padx=10, pady=10)

        right_card = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        right_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

        right_header = ctk.CTkFrame(right_card, fg_color="transparent")
        right_header.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(right_header, text="☁️ 可用 Skills (源)", font=("Segoe UI", 14, "bold")).pack(
            side="left"
        )

        self.right_list = CompareListFrame(right_card, skills_dir=app_config.skills_dir)
        self.right_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.right_list.add_header([("选择", 4), ("名称", 15), ("状态", 8), ("操作", 5)])

        ctk.CTkButton(
            right_header,
            text="全部展开",
            width=60,
            height=20,
            font=("Segoe UI", 10),
            fg_color="transparent",
            border_width=1,
            text_color="gray",
            command=self.right_list.expand_all,
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            right_header,
            text="全部折叠",
            width=60,
            height=20,
            font=("Segoe UI", 10),
            fg_color="transparent",
            border_width=1,
            text_color="gray",
            command=self.right_list.collapse_all,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            right_card,
            text=" 导入 / 更新选中",
            image=self.icon_import,
            fg_color=COLORS["primary"],
            command=self.import_selected,
        ).pack(fill="x", padx=10, pady=10)

        self.after(100, self.refresh_all)

    def refresh_all(self):
        self.controller.show_loading("正在加载 Skills...")
        threading.Thread(target=self._refresh_thread, daemon=True).start()

    def _refresh_thread(self):
        try:
            target_skills = []
            if os.path.exists(self.target_dir):
                try:
                    target_skills = [
                        i
                        for i in os.listdir(self.target_dir)
                        if os.path.isdir(os.path.join(self.target_dir, i))
                    ]
                except Exception:
                    pass

            right_rows = []
            error_msg = None

            if not os.path.exists(app_config.skills_dir):
                error_msg = "源目录不存在，请在设置中配置"
            else:
                source_skills = []
                for root, dirs, files in os.walk(app_config.skills_dir):
                    if "SKILL.md" in files:
                        rel_path = os.path.relpath(root, app_config.skills_dir).replace("\\", "/")
                        source_skills.append(rel_path)

                for skill_rel_path in sorted(source_skills):
                    s_path = os.path.join(app_config.skills_dir, skill_rel_path)
                    t_path = os.path.join(self.target_dir, os.path.basename(skill_rel_path))

                    parts = skill_rel_path.split("/")
                    if len(parts) > 1:
                        group_name = "/".join(parts[:-1])
                        display_name = parts[-1]
                    else:
                        group_name = None
                        display_name = parts[0]

                    in_target = os.path.exists(t_path)

                    status = "🆕 新增"
                    color = COLORS["success"]
                    is_diff = False

                    if in_target:
                        patterns = get_ignore_patterns(s_path)
                        ignore_func = shutil.ignore_patterns(*patterns) if patterns else None

                        if calculate_dir_hash(s_path, ignore_func) == calculate_dir_hash(t_path, ignore_func):
                            status = "✅ 一致"
                            color = "gray"
                        else:
                            status = "⚠️ 差异"
                            color = COLORS["warning"]
                            is_diff = True

                    right_rows.append(
                        {
                            "name": display_name,
                            "rel_path": skill_rel_path,
                            "status": status,
                            "color": color,
                            "is_diff": is_diff,
                            "s_path": s_path,
                            "t_path": t_path,
                            "group": group_name,
                        }
                    )

            self.after(0, lambda: self._update_ui(target_skills, right_rows, error_msg))

        except Exception as e:
            self.after(0, lambda: self.controller.hide_loading())
            print(f"Error in refresh thread: {e}")

    def _update_ui(self, target_skills, right_rows, error_msg):
        self.left_list.clear()
        self.right_list.clear()

        for s in target_skills:
            self.left_list.add_item(s)

        if error_msg:
            self.right_list.set_message(error_msg)
        else:
            for row in right_rows:
                diff_cmd = None
                if row["is_diff"]:
                    diff_cmd = lambda s=row["name"], sp=row["s_path"], tp=row["t_path"]: DiffViewerDialog(
                        self, s, sp, tp
                    )

                self.right_list.add_row(
                    {"name": row["name"], "rel_path": row["rel_path"], "status": row["status"]},
                    status_color=row["color"],
                    diff_command=diff_cmd,
                    name_command=lambda s=row["name"], sp=row["s_path"]: DescriptionDialog(
                        self, f"Skill: {s}", get_skill_description(sp)
                    ),
                    group=row["group"],
                )

        self.controller.hide_loading()

    def delete_selected(self):
        items = self.left_list.get_checked_items()
        if not items:
            return
        if not messagebox.askyesno("确认", f"删除 {len(items)} 个 Skills？"):
            return
        for item in items:
            try:
                shutil.rmtree(os.path.join(self.target_dir, item))
            except Exception as e:
                print(e)
        self.refresh_all()

    def import_selected(self):
        items = self.right_list.get_checked_items()
        if not items:
            return
        for item in items:
            skill = item.get("rel_path", item["name"])
            src = os.path.join(app_config.skills_dir, skill)
            dst = os.path.join(self.target_dir, os.path.basename(skill))
            try:
                if os.path.exists(dst):
                    shutil.rmtree(dst)

                ignore_func = None
                patterns = get_ignore_patterns(src)
                if patterns:
                    ignore_func = shutil.ignore_patterns(*patterns)

                shutil.copytree(src, dst, ignore=ignore_func)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        self.refresh_all()
        show_message(self, "完成", "导入完成")


class MCPManagerPage(ctk.CTkFrame):
    def __init__(self, parent, controller, target_file):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.target_file = target_file

        self.icon_back = load_icon(ICON_BACK, size=(16, 16))
        self.icon_import = load_icon(ICON_IMPORT, size=(16, 16))
        self.icon_del = load_icon(ICON_DELETE, size=(16, 16))

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

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20)
        ctk.CTkLabel(
            title_box, text="管理 MCP", font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"]
        ).pack(anchor="w")
        ctk.CTkLabel(title_box, text=target_file, font=("Segoe UI", 12), text_color="gray").pack(
            anchor="w"
        )

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left_card = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(left_card, text="📂 当前配置 (本地)", font=("Segoe UI", 14, "bold")).pack(
            pady=10, padx=10, anchor="w"
        )
        self.left_list = ScrollableCheckBoxFrame(left_card)
        self.left_list.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(
            left_card,
            text=" 删除选中",
            image=self.icon_del,
            fg_color=COLORS["danger"],
            hover_color="#800000",
            command=self.delete_selected,
        ).pack(fill="x", padx=10, pady=10)

        right_card = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        right_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(right_card, text="☁️ 可用配置 (源)", font=("Segoe UI", 14, "bold")).pack(
            pady=10, padx=10, anchor="w"
        )
        self.right_list = CompareListFrame(right_card)
        self.right_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.right_list.add_header([("选择", 4), ("MCP ID", 15), ("状态", 8), ("操作", 5)])

        ctk.CTkButton(
            right_card,
            text=" 导入 / 更新选中",
            image=self.icon_import,
            fg_color=COLORS["primary"],
            command=self.import_selected,
        ).pack(fill="x", padx=10, pady=10)

        self.after(100, self.refresh_all)

    def refresh_all(self):
        self.controller.show_loading("正在加载 MCP 配置...")
        threading.Thread(target=self._refresh_thread, daemon=True).start()

    def _refresh_thread(self):
        try:
            current_data = {}
            left_items = []

            if os.path.exists(self.target_file):
                try:
                    current_data = load_jsonc(self.target_file)
                    left_items = sorted(current_data.get("mcpServers", {}).keys())
                except Exception:
                    pass

            right_rows = []
            error_msg = None

            if not os.path.exists(app_config.mcp_settings_file):
                error_msg = "源配置文件不存在"
            else:
                try:
                    source_data = load_jsonc(app_config.mcp_settings_file).get("mcpServers", {})
                    target_servers = current_data.get("mcpServers", {})

                    for key in sorted(source_data.keys()):
                        in_target = key in target_servers
                        status = "🆕 新增"
                        color = COLORS["success"]
                        is_diff = False

                        if in_target:
                            if source_data[key] == target_servers[key]:
                                status = "✅ 一致"
                                color = "gray"
                            else:
                                status = "⚠️ 差异"
                                color = COLORS["warning"]
                                is_diff = True

                        right_rows.append(
                            {
                                "key": key,
                                "status": status,
                                "color": color,
                                "is_diff": is_diff,
                                "source_val": source_data[key],
                                "target_val": target_servers.get(key, {}),
                            }
                        )
                except Exception as e:
                    error_msg = f"Error: {e}"

            self.after(0, lambda: self._update_ui(current_data, left_items, right_rows, error_msg))

        except Exception as e:
            self.after(0, lambda: self.controller.hide_loading())
            print(f"Error in refresh thread: {e}")

    def _update_ui(self, current_data, left_items, right_rows, error_msg):
        self.current_data = current_data
        self.left_list.clear()
        self.right_list.clear()

        for k in left_items:
            self.left_list.add_item(k)

        if error_msg:
            self.right_list.set_message(error_msg)
        else:
            for row in right_rows:
                diff_cmd = None
                if row["is_diff"]:
                    diff_cmd = lambda k=row["key"], s=row["source_val"], t=row["target_val"]: TextDiffDialog(
                        self, f"Diff: {k}", json.dumps(s, indent=2), json.dumps(t, indent=2)
                    )

                self.right_list.add_row(
                    {"name": row["key"], "status": row["status"]},
                    status_color=row["color"],
                    diff_command=diff_cmd,
                    name_command=lambda k=row["key"], v=row["source_val"]: DescriptionDialog(
                        self, k, json.dumps(v, indent=2)
                    ),
                )

        self.controller.hide_loading()

    def delete_selected(self):
        items = self.left_list.get_checked_items()
        if not items:
            return
        if not messagebox.askyesno("Confirm", "Delete selected?"):
            return
        servers = self.current_data.get("mcpServers", {})
        for i in items:
            if i in servers:
                del servers[i]
        self.current_data["mcpServers"] = servers
        self.save_target()
        self.refresh_all()

    def import_selected(self):
        items = self.right_list.get_checked_items()
        if not items:
            return
        source_data = load_jsonc(app_config.mcp_settings_file).get("mcpServers", {})
        if "mcpServers" not in self.current_data:
            self.current_data["mcpServers"] = {}
        for item in items:
            key = item["name"]
            if key in source_data:
                self.current_data["mcpServers"][key] = source_data[key]
        self.save_target()
        self.refresh_all()
        show_message(self, "Done", "Imported.")

    def save_target(self):
        with open(self.target_file, "w", encoding="utf-8") as f:
            json.dump(self.current_data, f, indent=2, ensure_ascii=False)


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

        color = None
        icon = ""
        if type == "error":
            color = COLORS["danger"]
            icon = "❌ "
        elif type == "success":
            color = COLORS["success"]
            icon = "✅ "
        elif type == "dir":
            color = COLORS["primary"]
            icon = "📁 "
        elif type == "file_start":
            icon = "⬇️ "

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

        try:
            parts = url.strip("/").split("/")
            if "github.com" in parts:
                owner = parts[3]
                folder_path = "/".join(parts[7:])
                skill_name = folder_path.split("/")[-1]

                final_output_dir = os.path.join(target, owner, skill_name)

                if os.path.exists(final_output_dir):
                    if not messagebox.askyesno(
                        "确认覆盖", f"目标目录已存在，是否覆盖？\n\n{final_output_dir}"
                    ):
                        return
        except Exception:
            pass

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

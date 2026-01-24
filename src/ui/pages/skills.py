import threading
from tkinter import messagebox

from ...config import app_config
from ...core.actions import delete_skill_dirs, import_skills_to_target
from ...core.compare import build_skills_right_rows, collect_target_skill_dirs
from ...utils.fs import get_skill_description
from ..components import CompareListFrame
from ..platform.deps import ctk
from ..dialogs import DescriptionDialog, DiffViewerDialog
from ..style.icons import ICON_BACK, ICON_DELETE, ICON_IMPORT, load_icon
from ..style.status import status_to_color
from ..style.theme import COLORS
from ..utils.window_utils import show_message
from .common import build_back_header, build_left_card


class SkillsManagerPage(ctk.CTkFrame):
    def __init__(self, parent, controller, target_dir):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.target_dir = target_dir

        self.icon_back = load_icon(ICON_BACK, size=(16, 16))
        self.icon_import = load_icon(ICON_IMPORT, size=(16, 16))
        self.icon_del = load_icon(ICON_DELETE, size=(16, 16))

        build_back_header(self, controller, "管理 Skills", target_dir, self.icon_back)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        _, self.left_list = build_left_card(content, "📂 当前项目 (本地)", self.icon_del, self.delete_selected)

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
            target_skills = collect_target_skill_dirs(self.target_dir)

            right_rows, error_msg = build_skills_right_rows(app_config.skills_dir, self.target_dir)
            if right_rows:
                for row in right_rows:
                    row["color"] = status_to_color(row.get("status", ""), COLORS)

            self.after(0, lambda: self._update_ui(target_skills, right_rows or [], error_msg))

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
        errors = delete_skill_dirs(self.target_dir, items)
        for name, err in errors:
            print(err)
        self.refresh_all()

    def import_selected(self):
        items = self.right_list.get_checked_items()
        if not items:
            return
        errors = import_skills_to_target(app_config.skills_dir, self.target_dir, items)
        for skill, err in errors:
            messagebox.showerror("Error", err)
        self.refresh_all()
        show_message(self, "完成", "导入完成")

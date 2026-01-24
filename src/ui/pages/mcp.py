import json
import threading
from tkinter import messagebox

from ...config import app_config
from ...core.actions import delete_mcp_servers, import_mcp_servers, save_mcp_target
from ...core.compare import build_mcp_right_rows, read_mcp_current_data
from ..components import CompareListFrame
from ..platform.deps import ctk
from ..dialogs import DescriptionDialog, TextDiffDialog
from ..style.icons import ICON_BACK, ICON_DELETE, ICON_IMPORT, load_icon
from ..style.status import status_to_color
from ..style.theme import COLORS
from ..utils.window_utils import show_message
from .common import build_back_header, build_left_card


class MCPManagerPage(ctk.CTkFrame):
    def __init__(self, parent, controller, target_file):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.target_file = target_file

        self.icon_back = load_icon(ICON_BACK, size=(16, 16))
        self.icon_import = load_icon(ICON_IMPORT, size=(16, 16))
        self.icon_del = load_icon(ICON_DELETE, size=(16, 16))

        build_back_header(self, controller, "管理 MCP", target_file, self.icon_back)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        _, self.left_list = build_left_card(content, "📂 当前配置 (本地)", self.icon_del, self.delete_selected)

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
            current_data, left_items = read_mcp_current_data(self.target_file)
            right_rows, error_msg = build_mcp_right_rows(app_config.mcp_settings_file, current_data)

            if right_rows:
                for row in right_rows:
                    row["color"] = status_to_color(row.get("status", ""), COLORS)

            self.after(
                0,
                lambda: self._update_ui(
                    current_data, left_items, right_rows or [], error_msg
                ),
            )

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
        self.current_data = delete_mcp_servers(self.current_data, items)
        self.save_target()
        self.refresh_all()

    def import_selected(self):
        items = self.right_list.get_checked_items()
        if not items:
            return
        keys = [item["name"] for item in items]
        self.current_data = import_mcp_servers(self.current_data, app_config.mcp_settings_file, keys)
        self.save_target()
        self.refresh_all()
        show_message(self, "Done", "Imported.")

    def save_target(self):
        save_mcp_target(self.target_file, self.current_data)

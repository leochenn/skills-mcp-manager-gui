import os
import webbrowser

from ..platform.deps import ctk
from ..style.theme import COLORS


class CompareListFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, skills_dir=None, **kwargs):
        super().__init__(master, **kwargs)
        self.rows = []
        self.groups = {}
        self.skills_dir = skills_dir

    def add_header(self, columns):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        for text, width in columns:
            ctk.CTkLabel(
                header_frame,
                text=text,
                width=width * 10,
                font=("Segoe UI", 12, "bold"),
                anchor="w",
            ).pack(side="left", padx=5)

    def add_group(self, name):
        if name in self.groups:
            return self.groups[name]

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", pady=(10, 2))

        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")

        arrow_btn = ctk.CTkButton(
            header_frame,
            text="▼",
            width=24,
            anchor="center",
            fg_color="transparent",
            text_color=("gray50", "gray70"),
            font=("Segoe UI", 11, "bold"),
            hover_color=("gray90", "gray25"),
            height=24,
            command=lambda n=name: self.toggle_group(n),
        )
        arrow_btn.pack(side="left")

        url = None
        if self.skills_dir:
            url_file = os.path.join(self.skills_dir, name, "github_address.txt")
            if os.path.exists(url_file):
                try:
                    with open(url_file, "r", encoding="utf-8") as f:
                        url = f.readline().strip()
                except Exception:
                    pass

        if url:
            name_label = ctk.CTkLabel(
                header_frame,
                text=name,
                anchor="w",
                text_color=COLORS["primary"],
                font=("Segoe UI", 11, "bold", "underline"),
            )

            def on_enter(e):
                name_label.configure(text_color=COLORS["text_link"], cursor="hand2")

            def on_leave(e):
                name_label.configure(text_color=COLORS["primary"], cursor="")

            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)
            name_label.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
            name_label.pack(side="left", padx=(0, 5))

        else:
            name_label = ctk.CTkLabel(
                header_frame,
                text=name,
                anchor="w",
                text_color=("gray50", "gray70"),
                font=("Segoe UI", 11, "bold"),
            )
            name_label.bind("<Button-1>", lambda e, n=name: self.toggle_group(n))
            name_label.pack(side="left", padx=(0, 5))

        spacer_frame = ctk.CTkFrame(header_frame, fg_color="transparent", height=24)
        spacer_frame.pack(side="left", fill="x", expand=True)

        def on_spacer_enter(e):
            spacer_frame.configure(fg_color=("gray90", "gray25"))

        def on_spacer_leave(e):
            spacer_frame.configure(fg_color="transparent")

        spacer_frame.bind("<Enter>", on_spacer_enter)
        spacer_frame.bind("<Leave>", on_spacer_leave)
        spacer_frame.bind("<Button-1>", lambda e, n=name: self.toggle_group(n))

        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(fill="x", padx=(10, 0))

        self.groups[name] = {
            "container": container,
            "arrow_btn": arrow_btn,
            "content": content,
            "expanded": True,
        }
        return self.groups[name]

    def toggle_group(self, name):
        group = self.groups.get(name)
        if not group:
            return

        if group["expanded"]:
            group["content"].pack_forget()
            group["arrow_btn"].configure(text="▶")
            group["expanded"] = False
        else:
            group["content"].pack(fill="x", padx=(10, 0))
            group["arrow_btn"].configure(text="▼")
            group["expanded"] = True

    def expand_all(self):
        for name in self.groups:
            group = self.groups[name]
            if not group["expanded"]:
                group["content"].pack(fill="x", padx=(10, 0))
                group["arrow_btn"].configure(text="▼")
                group["expanded"] = True

    def collapse_all(self):
        for name in self.groups:
            group = self.groups[name]
            if group["expanded"]:
                group["content"].pack_forget()
                group["arrow_btn"].configure(text="▶")
                group["expanded"] = False

    def add_row(
        self,
        data,
        can_check=True,
        default_check=False,
        status_color=None,
        diff_command=None,
        name_command=None,
        group=None,
    ):
        parent = self
        if group:
            g = self.add_group(group)
            parent = g["content"]

        row_frame = ctk.CTkFrame(parent, fg_color=COLORS["item_card"], corner_radius=6, height=40)
        row_frame.pack(fill="x", pady=4, padx=2)

        def on_enter(e):
            row_frame.configure(fg_color=COLORS["item_hover"])

        def on_leave(e):
            row_frame.configure(fg_color=COLORS["item_card"])

        row_frame.bind("<Enter>", on_enter)
        row_frame.bind("<Leave>", on_leave)

        checkbox = ctk.CTkCheckBox(
            row_frame, text="", width=24, checkbox_width=20, checkbox_height=20
        )
        if default_check:
            checkbox.select()
        if not can_check:
            checkbox.configure(state="disabled")
        checkbox.pack(side="left", padx=(10, 10), pady=10)
        checkbox.bind("<Enter>", on_enter)
        checkbox.bind("<Leave>", on_leave)

        def toggle_check(e):
            if can_check:
                if checkbox.get():
                    checkbox.deselect()
                else:
                    checkbox.select()

        row_frame.bind("<Button-1>", toggle_check)

        status_text = data.get("status", "")
        status_clean = (
            status_text.replace("✅ ", "")
            .replace("🆕 ", "")
            .replace("⚠️ ", "")
            .strip()
        )

        badge_bg = "gray"
        badge_text = "white"

        if "一致" in status_text:
            badge_bg = COLORS["neutral_bg"]
            badge_text = COLORS["neutral_text"]
            status_clean = "一致"
        elif "新增" in status_text:
            badge_bg = COLORS["success_bg"]
            badge_text = COLORS["success_text"]
            status_clean = "新增"
        elif "差异" in status_text:
            badge_bg = COLORS["warning_bg"]
            badge_text = COLORS["warning_text"]
            status_clean = "差异"

        status_frame = ctk.CTkFrame(row_frame, fg_color=badge_bg, corner_radius=10, height=24)
        status_frame.pack(side="right", padx=(5, 10))
        status_frame.bind("<Enter>", on_enter)
        status_frame.bind("<Leave>", on_leave)
        status_frame.bind("<Button-1>", toggle_check)

        ctk.CTkLabel(
            status_frame,
            text=f" {status_clean} ",
            text_color=badge_text,
            font=("Segoe UI", 11, "bold"),
        ).pack(padx=8, pady=2)

        for child in status_frame.winfo_children():
            child.bind("<Button-1>", toggle_check)

        if diff_command:
            diff_btn = ctk.CTkButton(
                row_frame,
                text="👁️",
                width=30,
                height=24,
                command=diff_command,
                fg_color="transparent",
                hover_color=("gray80", "gray40"),
                text_color=COLORS["text_sub"],
                font=("Segoe UI", 14),
            )
            diff_btn.pack(side="right", padx=5)
            diff_btn.bind("<Enter>", on_enter)
            diff_btn.bind("<Leave>", on_leave)

        name_color = COLORS["text_nested"] if group else COLORS["text_link"]

        if name_command:
            lbl = ctk.CTkLabel(
                row_frame,
                text=data["name"],
                anchor="w",
                text_color=name_color,
                font=("Segoe UI", 13, "bold"),
            )
            lbl.pack(side="left", padx=5)

            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", lambda e: name_command())

            try:
                lbl.configure(cursor="hand2")
            except Exception:
                pass
        else:
            lbl = ctk.CTkLabel(
                row_frame,
                text=data["name"],
                anchor="w",
                font=("Segoe UI", 13, "bold"),
                text_color=name_color,
            )
            lbl.pack(side="left", padx=5, fill="x", expand=True)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", toggle_check)

        self.rows.append({"checkbox": checkbox, "data": data})

    def get_checked_items(self):
        return [row["data"] for row in self.rows if row["checkbox"].get() == 1]

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.rows = []
        self.groups = {}

    def set_message(self, message):
        self.clear()
        ctk.CTkLabel(self, text=message, text_color="gray").pack(pady=20)

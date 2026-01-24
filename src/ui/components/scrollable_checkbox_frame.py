from ..platform.deps import ctk
from ..style.theme import COLORS


class ScrollableCheckBoxFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, item_list=None, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.checkboxes = []
        if item_list:
            for item in item_list:
                self.add_item(item)

    def add_item(self, item, command=None):
        frame = ctk.CTkFrame(self, fg_color=COLORS["item_card"], corner_radius=6, height=40)
        frame.pack(fill="x", pady=4, padx=2)

        def on_enter(e):
            frame.configure(fg_color=COLORS["item_hover"])

        def on_leave(e):
            frame.configure(fg_color=COLORS["item_card"])

        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)

        checkbox = ctk.CTkCheckBox(
            frame, text="", width=24, checkbox_width=20, checkbox_height=20
        )
        checkbox.pack(side="left", padx=(10, 10), pady=10)
        checkbox.bind("<Enter>", on_enter)
        checkbox.bind("<Leave>", on_leave)

        def toggle_check(e):
            if checkbox.get():
                checkbox.deselect()
            else:
                checkbox.select()

        frame.bind("<Button-1>", toggle_check)

        if command:
            btn = ctk.CTkButton(
                frame,
                text=item,
                anchor="w",
                fg_color="transparent",
                text_color=COLORS["primary"],
                command=command,
                height=24,
                hover_color=COLORS["item_hover"],
                font=("Segoe UI", 13, "bold"),
            )
            btn.pack(side="left", fill="x", expand=True, padx=5)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        else:
            lbl = ctk.CTkLabel(frame, text=item, anchor="w", font=("Segoe UI", 13, "bold"))
            lbl.pack(side="left", fill="x", expand=True, padx=5)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", toggle_check)

        self.checkboxes.append({"checkbox": checkbox, "value": item})

    def remove_item(self, item):
        for i, cb in enumerate(self.checkboxes):
            if cb["value"] == item:
                cb["checkbox"].master.destroy()
                self.checkboxes.pop(i)
                return

    def get_checked_items(self):
        return [cb["value"] for cb in self.checkboxes if cb["checkbox"].get() == 1]

    def clear(self):
        for cb in self.checkboxes:
            cb["checkbox"].master.destroy()
        self.checkboxes = []

    def set_message(self, message):
        self.clear()
        ctk.CTkLabel(self, text=message, text_color="gray").pack(pady=20)

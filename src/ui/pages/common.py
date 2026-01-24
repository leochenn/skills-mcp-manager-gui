from ..components import ScrollableCheckBoxFrame
from ..platform.deps import ctk
from ..style.theme import COLORS


def build_back_header(parent, controller, title, subtitle, icon_back):
    header = ctk.CTkFrame(parent, fg_color="transparent")
    header.pack(fill="x", padx=20, pady=20)

    ctk.CTkButton(
        header,
        text=" 返回",
        image=icon_back,
        command=controller.show_home,
        width=80,
        fg_color="transparent",
        border_width=1,
        text_color=("black", "white"),
    ).pack(side="left")

    title_box = ctk.CTkFrame(header, fg_color="transparent")
    title_box.pack(side="left", padx=20)
    ctk.CTkLabel(title_box, text=title, font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"]).pack(
        anchor="w"
    )
    ctk.CTkLabel(title_box, text=subtitle, font=("Segoe UI", 12), text_color="gray").pack(anchor="w")


def build_left_card(content, title, icon_del, delete_command):
    left_card = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
    left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

    ctk.CTkLabel(left_card, text=title, font=("Segoe UI", 14, "bold")).pack(
        pady=10, padx=10, anchor="w"
    )
    left_list = ScrollableCheckBoxFrame(left_card)
    left_list.pack(fill="both", expand=True, padx=10, pady=5)

    ctk.CTkButton(
        left_card,
        text=" 删除选中",
        image=icon_del,
        fg_color=COLORS["danger"],
        hover_color="#800000",
        command=delete_command,
    ).pack(fill="x", padx=10, pady=10)

    return left_card, left_list

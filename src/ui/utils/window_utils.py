from tkinter import messagebox

from ..platform.deps import ctk


def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def center_window_relative(window, parent, width, height):
    window.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def show_message(parent, title, message):
    try:
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.transient(parent)
        dialog.grab_set()

        w, h = 300, 150
        center_window_relative(dialog, parent, w, h)

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text=message, wraplength=260, font=("Segoe UI", 12)).pack(
            pady=(10, 20), expand=True
        )

        ctk.CTkButton(frame, text="确定", width=100, command=dialog.destroy).pack(
            pady=(0, 10)
        )

        dialog.lift()
        dialog.focus_force()
        parent.wait_window(dialog)
    except Exception:
        messagebox.showinfo(title, message)

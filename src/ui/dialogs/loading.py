from ..platform.deps import ctk


class LoadingOverlay(ctk.CTkToplevel):
    def __init__(self, master, message="正在加载..."):
        super().__init__(master)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.transient(master)

        self.configure(fg_color=("gray95", "gray10"))
        self.attributes("-alpha", 0.9)

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.spinner = ctk.CTkProgressBar(self.center_frame, width=200, mode="indeterminate")
        self.spinner.pack(pady=20)
        self.spinner.start()

        self.label = ctk.CTkLabel(self.center_frame, text=message, font=("Segoe UI", 16))
        self.label.pack()

    def set_message(self, text):
        self.label.configure(text=text)

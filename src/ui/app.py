from .deps import ctk
from .pages import HomePage, InstallSkillsPage, MCPManagerPage, SkillsManagerPage
from .window_utils import center_window
from ..core.history import HistoryManager
from .dialogs import LoadingOverlay


class SkillsManagerAppV3(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gemini Skills & MCP Manager")
        center_window(self, 1000, 750)

        self.history_manager = HistoryManager()
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.current_frame = None
        self.loading_overlay = None

        self.show_home()

    def show_loading(self, message="正在加载..."):
        if self.loading_overlay:
            self.loading_overlay.destroy()

        self.loading_overlay = LoadingOverlay(self, message)

        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        self.loading_overlay.geometry(f"{w}x{h}+{x}+{y}")

        self.loading_overlay.lift()
        self.update()

    def hide_loading(self):
        if self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None

    def show_home(self):
        self._switch(HomePage(self.container, self))

    def show_install_skills_page(self):
        self._switch(InstallSkillsPage(self.container, self))

    def show_skills_page(self, path):
        self.history_manager.add_skills_dir(path)
        self._switch(SkillsManagerPage(self.container, self, path))

    def show_mcp_page(self, path):
        self.history_manager.add_mcp_file(path)
        self._switch(MCPManagerPage(self.container, self, path))

    def _switch(self, frame):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)


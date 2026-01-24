from src.ui.app import SkillsManagerAppV3
from src.ui.style.theme import setup_theme


def main():
    setup_theme()
    app = SkillsManagerAppV3()
    app.mainloop()


if __name__ == "__main__":
    main()

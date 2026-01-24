import sys

try:
    import customtkinter as ctk
    from PIL import Image
except ImportError:
    print("Please install customtkinter and pillow: pip install customtkinter pillow")
    sys.exit(1)

__all__ = ["ctk", "Image"]


import customtkinter as ctk
from tkinter import ttk


def apply_tree_style():
    """Apply a consistent Treeview style matching the current appearance mode."""
    mode = ctk.get_appearance_mode()
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    if mode == "Dark":
        bg, fg, head_bg, sel = "#2b2b2b", "white", "#2d7d2d", "#1a5c1a"
    else:
        bg, fg, head_bg, sel = "#e0e0e0", "black", "#2d7d2d", "#5cb85c"

    style.configure("Treeview", background=bg, foreground=fg,
                    fieldbackground=bg, rowheight=28)
    style.configure("Treeview.Heading", background=head_bg, foreground="white",
                    font=("Arial", 10, "bold"))
    style.map("Treeview", background=[("selected", sel)])
    style.configure("Treeview.Scrollbar", background=bg)

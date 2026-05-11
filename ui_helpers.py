"""Shared UI utilities for the comshop app."""
import customtkinter as ctk


def bring_to_front(window):
    """Force a CTkToplevel to display on top after creation.

    Call this at the END of __init__ (after UI build). It works around a
    customtkinter bug where new CTkToplevel windows get hidden behind their
    parent.
    """
    window.after(10, lambda: _do_lift(window))


def _do_lift(window):
    try:
        window.lift()
        window.attributes("-topmost", True)
        window.after(120, lambda: _release_topmost(window))
        window.focus_force()
    except Exception:
        pass


def _release_topmost(window):
    try:
        window.attributes("-topmost", False)
    except Exception:
        pass


def section_header(parent, title: str, accent_color="#22c55e"):
    """Create a colored header bar with a title for a module window."""
    bar = ctk.CTkFrame(parent, height=58, corner_radius=0,
                       fg_color=("gray85", "gray17"))
    bar.pack(fill="x")
    bar.pack_propagate(False)

    accent = ctk.CTkFrame(parent, height=3, corner_radius=0, fg_color=accent_color)
    accent.pack(fill="x")

    ctk.CTkLabel(bar, text=title,
                 font=ctk.CTkFont(size=18, weight="bold")).pack(
        side="left", padx=24, pady=14)
    return bar


def stat_card(parent, title: str, icon: str, accent_color: str):
    """Build a polished stat card. Returns (card_frame, value_label)."""
    card = ctk.CTkFrame(parent, corner_radius=12)

    accent = ctk.CTkFrame(card, height=4, corner_radius=0, fg_color=accent_color)
    accent.pack(fill="x")

    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(padx=18, pady=14, fill="both", expand=True)

    ctk.CTkLabel(content, text=icon,
                 font=ctk.CTkFont(size=22)).pack(anchor="w")
    value_label = ctk.CTkLabel(content, text="—",
                               font=ctk.CTkFont(size=28, weight="bold"))
    value_label.pack(anchor="w", pady=(2, 0))
    ctk.CTkLabel(content, text=title,
                 font=ctk.CTkFont(size=11),
                 text_color="gray").pack(anchor="w")

    return card, value_label

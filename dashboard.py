import customtkinter as ctk
from tkinter import messagebox, ttk
from db_connection import get_connection
from tree_style import apply_tree_style
from ui_helpers import stat_card
from datetime import date


class Dashboard(ctk.CTkToplevel):
    def __init__(self, user: dict, login_window):
        super().__init__()
        self.user = user
        self.login_window = login_window
        self._after_id = None
        self._open_modules = {}  # name -> window instance

        self.title("OG Gaming Hub — Dashboard")
        self.geometry("1180x720")
        self.minsize(1100, 660)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._center()
        apply_tree_style()
        self._build_ui()
        self.refresh_stats()

        # ensure foreground on first show
        self.after(50, self._raise)

    def _raise(self):
        self.lift()
        self.focus_force()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1180) // 2
        y = (self.winfo_screenheight() - 720) // 2
        self.geometry(f"1180x720+{x}+{y}")

    # ── UI BUILD ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=230, corner_radius=0,
                               fg_color=("gray82", "gray13"))
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo / Title
        logo = ctk.CTkFrame(sidebar, fg_color="transparent", height=90)
        logo.pack(fill="x", pady=(20, 6))
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="⚡ OG GAMING HUB",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(6, 0))
        ctk.CTkLabel(logo, text="Gaming Hub Management",
                     font=ctk.CTkFont(size=11),
                     text_color="gray").pack()

        # Divider
        ctk.CTkFrame(sidebar, height=1, fg_color=("gray70", "gray25")).pack(
            fill="x", padx=16, pady=8)

        ctk.CTkLabel(sidebar, text="  MAIN MENU",
                     anchor="w",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="gray").pack(fill="x", padx=18, pady=(4, 4))

        nav_items = [
            ("🖥  PC Units",        self._open_pc_management),
            ("📦  Time Packages",   self._open_package_management),
            ("▶  Sessions",         self._open_sessions),
            ("🍔  Products",        self._open_product_management),
            ("🛒  Food POS",        self._open_food_pos),
            ("🖨  Printing",        self._open_printing),
            ("📋  Transactions",    self._open_transactions),
        ]
        for label, cmd in nav_items:
            self._sidebar_button(sidebar, label, cmd)

        # Bottom-pinned section
        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", pady=(0, 14))

        ctk.CTkFrame(bottom, height=1,
                     fg_color=("gray70", "gray25")).pack(fill="x", padx=16, pady=(6, 10))

        ctk.CTkLabel(
            bottom, text=f"👤  {self.user['full_name']}",
            anchor="w", font=ctk.CTkFont(size=12),
        ).pack(fill="x", padx=22, pady=4)

        self._theme_btn = ctk.CTkButton(
            bottom, text="☀  Light Mode", height=36,
            font=ctk.CTkFont(size=12),
            fg_color="transparent", border_width=1,
            anchor="w",
            command=self._toggle_theme,
        )
        self._theme_btn.pack(fill="x", padx=14, pady=(8, 4))

        ctk.CTkButton(
            bottom, text="⎋  Logout", height=36,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#b03a2e", hover_color="#e74c3c",
            anchor="w",
            command=self._logout,
        ).pack(fill="x", padx=14, pady=4)

    def _sidebar_button(self, parent, label, cmd):
        btn = ctk.CTkButton(
            parent, text=label, height=42,
            font=ctk.CTkFont(size=13),
            anchor="w",
            corner_radius=8,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray22"),
            command=cmd,
        )
        btn.pack(fill="x", padx=12, pady=2)
        return btn

    def _build_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        # ── Welcome bar ────────────────────────────────────────────────────────
        welcome = ctk.CTkFrame(content, fg_color="transparent")
        welcome.grid(row=0, column=0, padx=28, pady=(22, 6), sticky="ew")

        ctk.CTkLabel(
            welcome, text=f"Welcome, {self.user['full_name']}",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            welcome, text="Manage your computer shop operations from one place.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(anchor="w", pady=(2, 0))

        # ── Stat cards ─────────────────────────────────────────────────────────
        stats_outer = ctk.CTkFrame(content, fg_color="transparent")
        stats_outer.grid(row=1, column=0, padx=22, pady=(14, 8), sticky="ew")
        for col in range(4):
            stats_outer.columnconfigure(col, weight=1)

        cards = [
            ("Total PCs",       "🖥", "#3b82f6", "total_pcs"),
            ("Available",       "✓",  "#22c55e", "available"),
            ("Occupied",        "⏰", "#f59e0b", "occupied"),
            ("Today's Revenue", "💰", "#10b981", "revenue"),
        ]
        self._stat_labels = {}
        for i, (title, icon, color, key) in enumerate(cards):
            card, val_label = stat_card(stats_outer, title, icon, color)
            card.grid(row=0, column=i, padx=6, sticky="ew")
            self._stat_labels[key] = val_label

        # ── Recent transactions ────────────────────────────────────────────────
        recent_outer = ctk.CTkFrame(content, corner_radius=12)
        recent_outer.grid(row=2, column=0, padx=28, pady=(12, 24), sticky="nsew")

        header = ctk.CTkFrame(recent_outer, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 6))
        ctk.CTkLabel(
            header, text="📊  Recent Transactions",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(
            header, text="View All", width=90, height=30,
            command=self._open_transactions,
        ).pack(side="right")

        tree_frame = ctk.CTkFrame(recent_outer)
        tree_frame.pack(padx=14, pady=(4, 14), fill="both", expand=True)

        cols = ("Date & Time", "Type", "Customer", "Amount")
        self._recent_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        for col in cols:
            self._recent_tree.heading(col, text=col)
        self._recent_tree.column("Date & Time", width=170, anchor="center")
        self._recent_tree.column("Type", width=120, anchor="center")
        self._recent_tree.column("Customer", width=220)
        self._recent_tree.column("Amount", width=130, anchor="e")

        sb = ttk.Scrollbar(tree_frame, orient="vertical",
                           command=self._recent_tree.yview)
        self._recent_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._recent_tree.pack(fill="both", expand=True)

    # ── Refresh ───────────────────────────────────────────────────────────────
    def refresh_stats(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        conn = get_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM pc_units")
                total = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM pc_units WHERE status='available'")
                available = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM pc_units WHERE status='occupied'")
                occupied = c.fetchone()[0]
                c.execute(
                    "SELECT COALESCE(SUM(total_amount),0) FROM transactions "
                    "WHERE DATE(datetime)=%s AND (status IS NULL OR status='completed')",
                    (date.today(),),
                )
                revenue = float(c.fetchone()[0])

                self._stat_labels["total_pcs"].configure(text=str(total))
                self._stat_labels["available"].configure(text=str(available))
                self._stat_labels["occupied"].configure(text=str(occupied))
                self._stat_labels["revenue"].configure(text=f"₱{revenue:,.2f}")

                # Recent transactions (last 10)
                c.execute("""
                    SELECT t.datetime, t.type, t.customer_name, t.total_amount,
                           COALESCE(t.status,'completed')
                    FROM transactions t
                    ORDER BY t.datetime DESC
                    LIMIT 10
                """)
                rows = c.fetchall()
                self._recent_tree.delete(*self._recent_tree.get_children())
                type_labels = {"pc_rental": "PC Rental", "food": "Food", "printing": "Printing"}
                for dt, ttype, customer, amount, status in rows:
                    type_label = type_labels.get(ttype, ttype)
                    if status == "refunded":
                        type_label += " (Refunded)"
                    self._recent_tree.insert("", "end", values=(
                        dt.strftime("%Y-%m-%d %H:%M") if dt else "—",
                        type_label,
                        customer,
                        f"₱{float(amount):,.2f}",
                    ))
            finally:
                conn.close()
        self._after_id = self.after(30_000, self.refresh_stats)

    # ── Theme toggle ──────────────────────────────────────────────────────────
    def _toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("light")
            self._theme_btn.configure(text="🌙  Dark Mode")
        else:
            ctk.set_appearance_mode("dark")
            self._theme_btn.configure(text="☀  Light Mode")
        apply_tree_style()

    # ── Module openers (with duplicate-prevention) ────────────────────────────
    def _open(self, key, factory):
        existing = self._open_modules.get(key)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.lift()
                    existing.focus_force()
                    existing.attributes("-topmost", True)
                    existing.after(80, lambda: existing.attributes("-topmost", False))
                    return
            except Exception:
                pass
        self._open_modules[key] = factory()

    def _open_pc_management(self):
        from pc_management import PCManagement
        self._open("pc", lambda: PCManagement(self))

    def _open_package_management(self):
        from package_management import PackageManagement
        self._open("pkg", lambda: PackageManagement(self))

    def _open_sessions(self):
        from session_management import SessionManagement
        self._open("sess", lambda: SessionManagement(self, self.user))

    def _open_product_management(self):
        from product_management import ProductManagement
        self._open("prod", lambda: ProductManagement(self))

    def _open_food_pos(self):
        from food_pos import FoodPOS
        self._open("food", lambda: FoodPOS(self, self.user))

    def _open_printing(self):
        from printing_pos import PrintingPOS
        self._open("print", lambda: PrintingPOS(self, self.user))

    def _open_transactions(self):
        from transactions_history import TransactionsHistory
        self._open("trans", lambda: TransactionsHistory(self))

    # ── Window events ─────────────────────────────────────────────────────────
    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?", parent=self):
            if self._after_id:
                self.after_cancel(self._after_id)
            self.destroy()
            self.login_window.deiconify()

    def _on_close(self):
        if messagebox.askyesno("Exit", "Exit the application?", parent=self):
            if self._after_id:
                self.after_cancel(self._after_id)
            self.login_window.destroy()

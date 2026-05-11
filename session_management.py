import customtkinter as ctk
from tkinter import messagebox, ttk
from db_connection import get_connection
from tree_style import apply_tree_style
from ui_helpers import bring_to_front, section_header
from datetime import datetime


class SessionManagement(ctk.CTkToplevel):
    def __init__(self, dashboard, user: dict):
        super().__init__(dashboard)
        self.dashboard = dashboard
        self.user = user
        self._packages = []
        self._available_pcs = {}
        self._available_pcs_rate = {}
        self.title("Session Management")
        self.geometry("1080x650")
        self._center()
        apply_tree_style()
        self._build_ui()
        self._load_available_pcs()
        self._load_packages()
        self._refresh_sessions()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        bring_to_front(self)

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1080) // 2
        y = (self.winfo_screenheight() - 650) // 2
        self.geometry(f"1080x650+{x}+{y}")

    def _build_ui(self):
        section_header(self, "▶  Session Management", accent_color="#22c55e")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=18, pady=(14, 18), fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=1)

        # ── Left: Start session form ──────────────────────────────────────────
        left = ctk.CTkFrame(content, corner_radius=12)
        left.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(left, text="Start New Session",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(16, 8))

        ctk.CTkLabel(left, text="Select PC:", anchor="w").pack(padx=18, pady=(4, 2), fill="x")
        self.pc_combo = ctk.CTkComboBox(left, state="readonly", values=[],
                                        command=self._update_price_preview)
        self.pc_combo.pack(padx=18, fill="x")

        ctk.CTkLabel(left, text="Customer Name:", anchor="w").pack(padx=18, pady=(10, 2), fill="x")
        self.customer_entry = ctk.CTkEntry(left, height=36)
        self.customer_entry.pack(padx=18, fill="x")

        ctk.CTkLabel(left, text="Duration (hours):", anchor="w").pack(padx=18, pady=(10, 2), fill="x")
        self.hours_entry = ctk.CTkEntry(left, height=36, placeholder_text="e.g. 1, 2.5, 3")
        self.hours_entry.pack(padx=18, fill="x")
        self.hours_entry.bind("<KeyRelease>", self._update_price_preview)

        self._preview_label = ctk.CTkLabel(
            left, text="Enter duration to see price",
            font=ctk.CTkFont(size=11), text_color="gray",
            wraplength=200, justify="left",
        )
        self._preview_label.pack(padx=18, pady=(6, 0), fill="x")

        ctk.CTkButton(left, text="▶  Start Session", height=42,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._start_session).pack(padx=18, pady=20, fill="x")

        # ── Right: Active sessions ────────────────────────────────────────────
        right = ctk.CTkFrame(content, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")

        hdr = ctk.CTkFrame(right, fg_color="transparent")
        hdr.pack(padx=12, pady=(12, 6), fill="x")
        ctk.CTkLabel(hdr, text="Active Sessions",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(hdr, text="Refresh", width=80, height=30,
                      command=self._refresh_sessions).pack(side="right")
        ctk.CTkButton(hdr, text="End Session", width=110, height=30,
                      fg_color="#b03a2e", hover_color="#e74c3c",
                      command=self._end_session).pack(side="right", padx=6)

        tree_frame = ctk.CTkFrame(right)
        tree_frame.pack(padx=12, pady=4, fill="both", expand=True)

        cols = ("ID", "PC", "Customer", "Billing", "Start Time", "Duration / Price")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("ID", text="ID")
        self.tree.heading("PC", text="PC")
        self.tree.heading("Customer", text="Customer")
        self.tree.heading("Billing", text="Billing")
        self.tree.heading("Start Time", text="Start Time")
        self.tree.heading("Duration / Price", text="Duration / Price")
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("PC", width=90, anchor="center")
        self.tree.column("Customer", width=130)
        self.tree.column("Billing", width=110, anchor="center")
        self.tree.column("Start Time", width=150, anchor="center")
        self.tree.column("Duration / Price", width=130, anchor="center")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _load_available_pcs(self):
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute(
                "SELECT id, unit_name, rate_per_hour FROM pc_units "
                "WHERE status='available' ORDER BY unit_name"
            )
            rows = c.fetchall()
            self._available_pcs = {row[1]: row[0] for row in rows}
            self._available_pcs_rate = {row[1]: float(row[2]) for row in rows}
            self.pc_combo.configure(values=list(self._available_pcs.keys()))
            if rows:
                self.pc_combo.set(rows[0][1])
            else:
                self.pc_combo.set("")
        finally:
            conn.close()
        self._update_price_preview()

    def _load_packages(self):
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("SELECT id, package_name, hours, price FROM time_packages ORDER BY hours")
            self._packages = c.fetchall()  # (id, name, hours, price)
        finally:
            conn.close()
        self._update_price_preview()

    def _update_price_preview(self, *_):
        hours_str = self.hours_entry.get().strip()
        pc_name = self.pc_combo.get()
        rate = self._available_pcs_rate.get(pc_name, 20.0)

        if not hours_str:
            self._preview_label.configure(text="Enter duration to see price", text_color="gray")
            return
        try:
            hours = float(hours_str)
            if hours <= 0:
                raise ValueError
        except ValueError:
            self._preview_label.configure(text="Enter a valid number of hours", text_color="#e74c3c")
            return

        matched = next(
            (p for p in self._packages if abs(hours - float(p[2])) < 0.01), None
        )
        if matched:
            self._preview_label.configure(
                text=f"📦 Package: {matched[1]} — ₱{float(matched[3]):,.2f}",
                text_color="#22c55e",
            )
        else:
            self._preview_label.configure(
                text=f"⏱ Hourly: {hours}h × ₱{rate:,.2f}/hr = ₱{hours * rate:,.2f}",
                text_color="#f59e0b",
            )

    def _refresh_sessions(self):
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("""
                SELECT s.id, p.unit_name, s.customer_name, s.billing_type,
                       COALESCE(tp.package_name,''), s.start_time,
                       s.preset_hours, s.total_amount
                FROM sessions s
                JOIN pc_units p ON s.pc_id = p.id
                LEFT JOIN time_packages tp ON s.package_id = tp.id
                WHERE s.status='active'
                ORDER BY s.start_time
            """)
            rows = c.fetchall()
        finally:
            conn.close()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            sid, pc_name, customer, billing, pkg_name, start_time, preset_hrs, locked_amt = row
            hrs_str = f"{float(preset_hrs):.1f}h" if preset_hrs else "—"
            amt_str = f"₱{float(locked_amt):,.2f}" if locked_amt else "—"
            dur_price = f"{hrs_str} — {amt_str}"
            billing_label = (
                f"Package ({pkg_name})" if billing == "package" and pkg_name
                else billing.capitalize()
            )
            self.tree.insert("", "end", values=(
                sid, pc_name, customer, billing_label,
                start_time.strftime("%Y-%m-%d %H:%M"), dur_price,
            ))

    # ── Actions ────────────────────────────────────────────────────────────────
    def _start_session(self):
        pc_name = self.pc_combo.get().strip()
        customer = self.customer_entry.get().strip()
        hours_str = self.hours_entry.get().strip()

        if not pc_name or not customer or not hours_str:
            messagebox.showwarning("Validation", "Please fill in all required fields.", parent=self)
            return
        if pc_name not in self._available_pcs:
            messagebox.showwarning("Unavailable", "Selected PC is not available.", parent=self)
            return
        try:
            hours = float(hours_str)
            if hours <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Please enter a valid number of hours.", parent=self)
            return

        pc_id = self._available_pcs[pc_name]
        rate = self._available_pcs_rate.get(pc_name, 20.0)

        matched_pkg = next(
            (p for p in self._packages if abs(hours - float(p[2])) < 0.01), None
        )
        if matched_pkg:
            billing = "package"
            package_id = matched_pkg[0]
            locked_amount = float(matched_pkg[3])
        else:
            billing = "hourly"
            package_id = None
            locked_amount = round(hours * rate, 2)

        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO sessions "
                "(pc_id, customer_name, billing_type, package_id, preset_hours, "
                "start_time, total_amount, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,'active')",
                (pc_id, customer, billing, package_id, hours, datetime.now(), locked_amount),
            )
            c.execute("UPDATE pc_units SET status='occupied' WHERE id=%s", (pc_id,))
            conn.commit()
        finally:
            conn.close()

        self.customer_entry.delete(0, "end")
        self.hours_entry.delete(0, "end")
        self._preview_label.configure(text="Enter duration to see price", text_color="gray")
        self._load_available_pcs()
        self._refresh_sessions()
        self.dashboard.refresh_stats()

        billing_desc = (
            f"Package: {matched_pkg[1]} — ₱{locked_amount:,.2f}"
            if matched_pkg
            else f"Hourly: {hours}h × ₱{rate:,.2f}/hr = ₱{locked_amount:,.2f}"
        )
        messagebox.showinfo(
            "Session Started",
            f"Session started for {customer} on {pc_name}.\n{billing_desc}",
            parent=self,
        )

    def _end_session(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an active session.", parent=self)
            return

        session_id = self.tree.item(sel[0])["values"][0]

        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor(dictionary=True)
            c.execute("""
                SELECT s.*, p.unit_name, p.rate_per_hour,
                       tp.package_name, tp.price AS pkg_price
                FROM sessions s
                JOIN pc_units p ON s.pc_id = p.id
                LEFT JOIN time_packages tp ON s.package_id = tp.id
                WHERE s.id = %s
            """, (session_id,))
            sess = c.fetchone()
        finally:
            conn.close()

        if not sess:
            return

        # Price was locked at session start — use it directly
        amount = float(sess["total_amount"])
        preset_hrs = float(sess["preset_hours"]) if sess["preset_hours"] else 0.0

        if sess["billing_type"] == "package":
            item_name = (
                f"{sess['unit_name']} — {sess['package_name']} "
                f"({preset_hrs:.1f}h)"
            )
        else:
            item_name = (
                f"{sess['unit_name']} — {preset_hrs:.1f}h × "
                f"₱{float(sess['rate_per_hour']):.2f}/hr"
            )

        end_time = datetime.now()
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute(
                "UPDATE sessions SET end_time=%s, status='completed' WHERE id=%s",
                (end_time, session_id),
            )
            c.execute("UPDATE pc_units SET status='available' WHERE id=%s", (sess["pc_id"],))
            c.execute(
                "INSERT INTO transactions "
                "(type, reference_id, customer_name, total_amount, processed_by) "
                "VALUES ('pc_rental',%s,%s,%s,%s)",
                (session_id, sess["customer_name"], amount, self.user["id"]),
            )
            trans_id = c.lastrowid
            c.execute(
                "INSERT INTO transaction_items "
                "(transaction_id, item_name, quantity, unit_price, subtotal) "
                "VALUES (%s,%s,%s,%s,%s)",
                (trans_id, item_name, 1, amount, amount),
            )
            conn.commit()
        finally:
            conn.close()

        self._load_available_pcs()
        self._refresh_sessions()
        self.dashboard.refresh_stats()

        ReceiptDialog(self, {
            "trans_id": trans_id,
            "type": "PC Rental",
            "customer": sess["customer_name"],
            "items": [(item_name, 1, amount, amount)],
            "total": amount,
            "duration": f"{preset_hrs:.1f} hour(s)",
        })


class ReceiptDialog(ctk.CTkToplevel):
    def __init__(self, parent, data: dict):
        super().__init__(parent)
        self.title("Receipt")
        self.geometry("440x460")
        self.resizable(False, False)
        self._build(data)
        self.grab_set()
        bring_to_front(self)

    def _build(self, d):
        ctk.CTkLabel(self, text="COMSHOP RECEIPT",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 4))
        ctk.CTkLabel(self, text="─" * 46, text_color="gray").pack()

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(padx=30, pady=8, fill="x")
        for label, val in [
            ("Transaction #", str(d.get("trans_id", "—"))),
            ("Type", d.get("type", "—")),
            ("Customer", d.get("customer", "—")),
        ]:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"{label}:", width=130, anchor="w",
                         font=ctk.CTkFont(size=12)).pack(side="left")
            ctk.CTkLabel(row, text=val, anchor="w",
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        if d.get("duration"):
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text="Duration:", width=130, anchor="w",
                         font=ctk.CTkFont(size=12)).pack(side="left")
            ctk.CTkLabel(row, text=d["duration"], anchor="w",
                         font=ctk.CTkFont(size=12)).pack(side="left")

        ctk.CTkLabel(self, text="─" * 46, text_color="gray").pack(pady=4)
        ctk.CTkLabel(self, text="Items:", font=ctk.CTkFont(size=12, weight="bold"),
                     anchor="w").pack(padx=30, fill="x")

        for item_name, qty, unit_price, subtotal in d.get("items", []):
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(padx=30, fill="x", pady=1)
            ctk.CTkLabel(row, text=f"• {item_name}", anchor="w",
                         font=ctk.CTkFont(size=11)).pack(side="left")
            ctk.CTkLabel(row, text=f"₱{subtotal:,.2f}", anchor="e",
                         font=ctk.CTkFont(size=11)).pack(side="right")

        ctk.CTkLabel(self, text="─" * 46, text_color="gray").pack(pady=4)
        ctk.CTkLabel(self, text=f"TOTAL:  ₱{d.get('total', 0):,.2f}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=4)

        ctk.CTkButton(self, text="Close", height=38, command=self.destroy).pack(
            padx=30, pady=16, fill="x")

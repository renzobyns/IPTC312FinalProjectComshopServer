import customtkinter as ctk
from tkinter import messagebox, ttk
from db_connection import get_connection
from tree_style import apply_tree_style
from ui_helpers import bring_to_front, section_header


class PCManagement(ctk.CTkToplevel):
    def __init__(self, dashboard):
        super().__init__(dashboard)
        self.dashboard = dashboard
        self.title("PC Units Management")
        self.geometry("860x600")
        self._center()
        self._all_rows = []
        apply_tree_style()
        self._build_ui()
        self._load_data()
        bring_to_front(self)

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 860) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"860x600+{x}+{y}")

    def _build_ui(self):
        section_header(self, "🖥  PC Units Management", accent_color="#3b82f6")

        # Search + buttons row
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(padx=22, pady=(16, 6), fill="x")

        ctk.CTkLabel(top, text="Search:").pack(side="left")
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())
        ctk.CTkEntry(top, textvariable=self._search_var, width=220, height=34).pack(side="left", padx=8)

        ctk.CTkButton(top, text="Refresh", width=88, height=34,
                      command=self._load_data).pack(side="right", padx=4)
        ctk.CTkButton(top, text="Delete", width=80, height=34,
                      fg_color="#b03a2e", hover_color="#e74c3c",
                      command=self._delete).pack(side="right", padx=4)
        ctk.CTkButton(top, text="Edit", width=72, height=34,
                      command=self._edit).pack(side="right", padx=4)
        ctk.CTkButton(top, text="Add PC", width=88, height=34,
                      command=self._add).pack(side="right", padx=4)
        ctk.CTkButton(top, text="Set All Rates", width=110, height=34,
                      fg_color="#1d4ed8", hover_color="#2563eb",
                      command=self._set_all_rates).pack(side="right", padx=4)

        # Treeview
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(padx=22, pady=(8, 22), fill="both", expand=True)

        cols = ("ID", "Unit Name", "Status", "Rate / Hour")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Unit Name", text="Unit Name")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Rate / Hour", text="Rate / Hour")
        self.tree.column("ID", width=55, anchor="center")
        self.tree.column("Unit Name", width=200)
        self.tree.column("Status", width=140, anchor="center")
        self.tree.column("Rate / Hour", width=130, anchor="center")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", lambda _: self._edit())

    def _load_data(self):
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("SELECT id, unit_name, status, rate_per_hour FROM pc_units ORDER BY id")
            self._all_rows = c.fetchall()
            self._populate(self._all_rows)
        finally:
            conn.close()

    def _filter(self):
        q = self._search_var.get().lower()
        self._populate([r for r in self._all_rows if q in r[1].lower()])

    def _populate(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], f"₱{float(row[3]):,.2f}"))

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a PC unit.", parent=self)
            return None
        return self.tree.item(sel[0])["values"][0]

    def _add(self):
        PCForm(self, mode="add", on_save=self._on_save)

    def _edit(self):
        pc_id = self._selected_id()
        if pc_id is None:
            return
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor(dictionary=True)
            c.execute("SELECT * FROM pc_units WHERE id=%s", (pc_id,))
            data = c.fetchone()
        finally:
            conn.close()
        PCForm(self, mode="edit", data=data, on_save=self._on_save)

    def _delete(self):
        pc_id = self._selected_id()
        if pc_id is None:
            return
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM sessions WHERE pc_id=%s AND status='active'", (pc_id,))
            if c.fetchone()[0] > 0:
                messagebox.showwarning("Cannot Delete",
                                       "This PC has an active session. End the session first.", parent=self)
                return
            c.execute("SELECT COUNT(*) FROM sessions WHERE pc_id=%s", (pc_id,))
            if c.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Cannot Delete",
                    "This PC has session history records and cannot be deleted.\n"
                    "You can set its status to Maintenance instead.",
                    parent=self,
                )
                return
        finally:
            conn.close()
        if not messagebox.askyesno("Confirm Delete", "Delete this PC unit?", parent=self):
            return
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("DELETE FROM pc_units WHERE id=%s", (pc_id,))
            conn.commit()
            self._on_save()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Delete Failed", f"Could not delete PC unit.\n\n{e}", parent=self)
        finally:
            conn.close()

    def _set_all_rates(self):
        SetAllRatesDialog(self, on_save=self._on_save)

    def _on_save(self):
        self._load_data()
        self.dashboard.refresh_stats()


class PCForm(ctk.CTkToplevel):
    def __init__(self, parent, mode, data=None, on_save=None):
        super().__init__(parent)
        self.mode = mode
        self.data = data
        self.on_save = on_save
        self.title("Add PC Unit" if mode == "add" else "Edit PC Unit")
        self.geometry("370x310")
        self._build()
        self.grab_set()
        bring_to_front(self)

    def _build(self):
        ctk.CTkLabel(self, text="Unit Name:", anchor="w").pack(padx=30, pady=(22, 4), fill="x")
        self.name_entry = ctk.CTkEntry(self, height=38)
        self.name_entry.pack(padx=30, fill="x")

        ctk.CTkLabel(self, text="Status:", anchor="w").pack(padx=30, pady=(12, 4), fill="x")
        self.status_menu = ctk.CTkOptionMenu(
            self, values=["available", "occupied", "maintenance"], height=38)
        self.status_menu.pack(padx=30, fill="x")

        ctk.CTkLabel(self, text="Rate per Hour (₱):", anchor="w").pack(padx=30, pady=(12, 4), fill="x")
        self.rate_entry = ctk.CTkEntry(self, height=38)
        self.rate_entry.pack(padx=30, fill="x")

        if self.data:
            self.name_entry.insert(0, self.data["unit_name"])
            self.status_menu.set(self.data["status"])
            self.rate_entry.insert(0, str(self.data["rate_per_hour"]))

        ctk.CTkButton(self, text="Save", height=42, command=self._save).pack(padx=30, pady=18, fill="x")

    def _save(self):
        name = self.name_entry.get().strip()
        status = self.status_menu.get()
        rate_str = self.rate_entry.get().strip()

        if not name or not rate_str:
            messagebox.showwarning("Validation", "Please fill in all required fields.", parent=self)
            return
        try:
            rate = float(rate_str)
            if rate <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Please enter a valid positive number for rate.", parent=self)
            return

        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            if self.mode == "add":
                c.execute(
                    "INSERT INTO pc_units (unit_name, status, rate_per_hour) VALUES (%s,%s,%s)",
                    (name, status, rate),
                )
            else:
                c.execute(
                    "UPDATE pc_units SET unit_name=%s, status=%s, rate_per_hour=%s WHERE id=%s",
                    (name, status, rate, self.data["id"]),
                )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()


class SetAllRatesDialog(ctk.CTkToplevel):
    """Set the same hourly rate for every PC unit at once."""

    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Set Rate for All PCs")
        self.geometry("360x230")
        self.resizable(False, False)
        self._build()
        self.grab_set()
        bring_to_front(self)

    def _build(self):
        ctk.CTkLabel(self, text="Set Rate for All PCs",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(22, 4))
        ctk.CTkLabel(self, text="This will update the rate for every PC unit.",
                     font=ctk.CTkFont(size=11), text_color="gray").pack()

        ctk.CTkLabel(self, text="New Rate per Hour (₱):", anchor="w").pack(
            padx=30, pady=(16, 4), fill="x")
        self.rate_entry = ctk.CTkEntry(self, height=40, placeholder_text="e.g. 12.00")
        self.rate_entry.pack(padx=30, fill="x")
        self.rate_entry.bind("<Return>", lambda _: self._save())

        ctk.CTkButton(self, text="Apply to All PCs", height=42,
                      fg_color="#1d4ed8", hover_color="#2563eb",
                      command=self._save).pack(padx=30, pady=18, fill="x")

    def _save(self):
        rate_str = self.rate_entry.get().strip()
        try:
            rate = float(rate_str)
            if rate <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation",
                                   "Please enter a valid positive number for rate.", parent=self)
            return

        if not messagebox.askyesno(
            "Confirm",
            f"Set ₱{rate:,.2f}/hr for ALL PC units?\nThis will overwrite individual rates.",
            parent=self,
        ):
            return

        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("UPDATE pc_units SET rate_per_hour = %s", (rate,))
            affected = c.rowcount
            conn.commit()
        finally:
            conn.close()

        messagebox.showinfo("Done", f"Updated {affected} PC unit(s) to ₱{rate:,.2f}/hr.", parent=self)
        if self.on_save:
            self.on_save()
        self.destroy()

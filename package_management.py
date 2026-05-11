import customtkinter as ctk
from tkinter import messagebox, ttk
from db_connection import get_connection
from tree_style import apply_tree_style
from ui_helpers import bring_to_front, section_header


class PackageManagement(ctk.CTkToplevel):
    def __init__(self, dashboard):
        super().__init__(dashboard)
        self.dashboard = dashboard
        self.title("Time Packages Management")
        self.geometry("740x520")
        self._center()
        self._all_rows = []
        apply_tree_style()
        self._build_ui()
        self._load_data()
        bring_to_front(self)

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 740) // 2
        y = (self.winfo_screenheight() - 520) // 2
        self.geometry(f"740x520+{x}+{y}")

    def _build_ui(self):
        section_header(self, "📦  Time Packages Management", accent_color="#a855f7")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=22, pady=(16, 6), fill="x")
        ctk.CTkButton(btn_frame, text="Add Package", width=110, height=34,
                      command=self._add).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="Edit", width=72, height=34,
                      command=self._edit).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="Delete", width=80, height=34,
                      fg_color="#b03a2e", hover_color="#e74c3c",
                      command=self._delete).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="Refresh", width=88, height=34,
                      command=self._load_data).pack(side="right", padx=4)

        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(padx=22, pady=(8, 22), fill="both", expand=True)

        cols = ("ID", "Package Name", "Hours", "Price")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=55, anchor="center")
        self.tree.column("Package Name", width=220)
        self.tree.column("Hours", width=100, anchor="center")
        self.tree.column("Price", width=120, anchor="center")

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
            c.execute("SELECT id, package_name, hours, price FROM time_packages ORDER BY hours")
            self._all_rows = c.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in self._all_rows:
                self.tree.insert("", "end",
                                 values=(row[0], row[1], f"{float(row[2]):.1f} hr(s)", f"₱{float(row[3]):,.2f}"))
        finally:
            conn.close()

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a package.", parent=self)
            return None
        return self.tree.item(sel[0])["values"][0]

    def _add(self):
        PackageForm(self, mode="add", on_save=self._load_data)

    def _edit(self):
        pkg_id = self._selected_id()
        if pkg_id is None:
            return
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor(dictionary=True)
            c.execute("SELECT * FROM time_packages WHERE id=%s", (pkg_id,))
            data = c.fetchone()
        finally:
            conn.close()
        PackageForm(self, mode="edit", data=data, on_save=self._load_data)

    def _delete(self):
        pkg_id = self._selected_id()
        if pkg_id is None:
            return
        if not messagebox.askyesno("Confirm Delete", "Delete this package?", parent=self):
            return
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("DELETE FROM time_packages WHERE id=%s", (pkg_id,))
            conn.commit()
        finally:
            conn.close()
        self._load_data()


class PackageForm(ctk.CTkToplevel):
    def __init__(self, parent, mode, data=None, on_save=None):
        super().__init__(parent)
        self.mode = mode
        self.data = data
        self.on_save = on_save
        self.title("Add Package" if mode == "add" else "Edit Package")
        self.geometry("360x300")
        self._build()
        self.grab_set()
        bring_to_front(self)

    def _build(self):
        ctk.CTkLabel(self, text="Package Name:", anchor="w").pack(padx=30, pady=(22, 4), fill="x")
        self.name_entry = ctk.CTkEntry(self, height=38)
        self.name_entry.pack(padx=30, fill="x")

        ctk.CTkLabel(self, text="Hours:", anchor="w").pack(padx=30, pady=(12, 4), fill="x")
        self.hours_entry = ctk.CTkEntry(self, height=38, placeholder_text="e.g. 1.0")
        self.hours_entry.pack(padx=30, fill="x")

        ctk.CTkLabel(self, text="Price (₱):", anchor="w").pack(padx=30, pady=(12, 4), fill="x")
        self.price_entry = ctk.CTkEntry(self, height=38, placeholder_text="e.g. 15.00")
        self.price_entry.pack(padx=30, fill="x")

        if self.data:
            self.name_entry.insert(0, self.data["package_name"])
            self.hours_entry.insert(0, str(self.data["hours"]))
            self.price_entry.insert(0, str(self.data["price"]))

        ctk.CTkButton(self, text="Save", height=42, command=self._save).pack(padx=30, pady=18, fill="x")

    def _save(self):
        name = self.name_entry.get().strip()
        hours_str = self.hours_entry.get().strip()
        price_str = self.price_entry.get().strip()

        if not name or not hours_str or not price_str:
            messagebox.showwarning("Validation", "Please fill in all required fields.", parent=self)
            return
        try:
            hours = float(hours_str)
            price = float(price_str)
            if hours <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation",
                                   "Please enter valid positive numbers for hours and price.", parent=self)
            return

        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            if self.mode == "add":
                c.execute(
                    "INSERT INTO time_packages (package_name, hours, price) VALUES (%s,%s,%s)",
                    (name, hours, price),
                )
            else:
                c.execute(
                    "UPDATE time_packages SET package_name=%s, hours=%s, price=%s WHERE id=%s",
                    (name, hours, price, self.data["id"]),
                )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()

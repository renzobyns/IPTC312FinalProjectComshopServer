import customtkinter as ctk
from tkinter import messagebox, ttk
from db_connection import get_connection
from tree_style import apply_tree_style
from ui_helpers import bring_to_front, section_header


class ProductManagement(ctk.CTkToplevel):
    def __init__(self, dashboard):
        super().__init__(dashboard)
        self.dashboard = dashboard
        self.title("Products Management")
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
        section_header(self, "🍔  Products Management", accent_color="#f59e0b")

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
        ctk.CTkButton(top, text="Add Product", width=100, height=34,
                      command=self._add).pack(side="right", padx=4)

        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(padx=22, pady=(8, 22), fill="both", expand=True)

        cols = ("ID", "Name", "Category", "Price", "Stock")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=55, anchor="center")
        self.tree.column("Name", width=200)
        self.tree.column("Category", width=120, anchor="center")
        self.tree.column("Price", width=110, anchor="center")
        self.tree.column("Stock", width=100, anchor="center")

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
            c.execute("SELECT id, name, category, price, stock FROM products ORDER BY category, name")
            self._all_rows = c.fetchall()
            self._populate(self._all_rows)
        finally:
            conn.close()

    def _filter(self):
        q = self._search_var.get().lower()
        self._populate([r for r in self._all_rows if q in r[1].lower() or q in r[2].lower()])

    def _populate(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            stock_display = str(row[4])
            tag = "low" if row[4] <= 5 else ""
            self.tree.insert("", "end",
                             values=(row[0], row[1], row[2].capitalize(), f"₱{float(row[3]):,.2f}", stock_display),
                             tags=(tag,))
        self.tree.tag_configure("low", foreground="#e74c3c")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a product.", parent=self)
            return None
        return self.tree.item(sel[0])["values"][0]

    def _add(self):
        ProductForm(self, mode="add", on_save=self._load_data)

    def _edit(self):
        prod_id = self._selected_id()
        if prod_id is None:
            return
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor(dictionary=True)
            c.execute("SELECT * FROM products WHERE id=%s", (prod_id,))
            data = c.fetchone()
        finally:
            conn.close()
        ProductForm(self, mode="edit", data=data, on_save=self._load_data)

    def _delete(self):
        prod_id = self._selected_id()
        if prod_id is None:
            return
        if not messagebox.askyesno("Confirm Delete", "Delete this product?", parent=self):
            return
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("DELETE FROM products WHERE id=%s", (prod_id,))
            conn.commit()
        finally:
            conn.close()
        self._load_data()


class ProductForm(ctk.CTkToplevel):
    def __init__(self, parent, mode, data=None, on_save=None):
        super().__init__(parent)
        self.mode = mode
        self.data = data
        self.on_save = on_save
        self.title("Add Product" if mode == "add" else "Edit Product")
        self.geometry("370x430")
        self._build()
        self.grab_set()
        bring_to_front(self)

    def _build(self):
        ctk.CTkLabel(self, text="Name:", anchor="w").pack(padx=30, pady=(22, 4), fill="x")
        self.name_entry = ctk.CTkEntry(self, height=38)
        self.name_entry.pack(padx=30, fill="x")

        ctk.CTkLabel(self, text="Category:", anchor="w").pack(padx=30, pady=(12, 4), fill="x")
        self.cat_menu = ctk.CTkOptionMenu(self, values=["food", "drink"], height=38)
        self.cat_menu.pack(padx=30, fill="x")

        ctk.CTkLabel(self, text="Price (₱):", anchor="w").pack(padx=30, pady=(12, 4), fill="x")
        self.price_entry = ctk.CTkEntry(self, height=38)
        self.price_entry.pack(padx=30, fill="x")

        ctk.CTkLabel(self, text="Stock:", anchor="w").pack(padx=30, pady=(12, 4), fill="x")
        self.stock_entry = ctk.CTkEntry(self, height=38)
        self.stock_entry.pack(padx=30, fill="x")

        if self.data:
            self.name_entry.insert(0, self.data["name"])
            self.cat_menu.set(self.data["category"])
            self.price_entry.insert(0, str(self.data["price"]))
            self.stock_entry.insert(0, str(self.data["stock"]))

        ctk.CTkButton(self, text="Save", height=42, command=self._save).pack(padx=30, pady=18, fill="x")

    def _save(self):
        name = self.name_entry.get().strip()
        category = self.cat_menu.get()
        price_str = self.price_entry.get().strip()
        stock_str = self.stock_entry.get().strip()

        if not name or not price_str or not stock_str:
            messagebox.showwarning("Validation", "Please fill in all required fields.", parent=self)
            return
        try:
            price = float(price_str)
            stock = int(stock_str)
            if price <= 0 or stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation",
                                   "Please enter a valid positive number for price and a non-negative integer for stock.",
                                   parent=self)
            return

        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            if self.mode == "add":
                c.execute(
                    "INSERT INTO products (name, category, price, stock) VALUES (%s,%s,%s,%s)",
                    (name, category, price, stock),
                )
            else:
                c.execute(
                    "UPDATE products SET name=%s, category=%s, price=%s, stock=%s WHERE id=%s",
                    (name, category, price, stock, self.data["id"]),
                )
            conn.commit()
        finally:
            conn.close()
        if self.on_save:
            self.on_save()
        self.destroy()

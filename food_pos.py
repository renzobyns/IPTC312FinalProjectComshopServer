import customtkinter as ctk
from tkinter import messagebox, ttk, simpledialog
from db_connection import get_connection
from tree_style import apply_tree_style
from ui_helpers import bring_to_front, section_header
from session_management import ReceiptDialog


class FoodPOS(ctk.CTkToplevel):
    def __init__(self, dashboard, user: dict):
        super().__init__(dashboard)
        self.dashboard = dashboard
        self.user = user
        self._cart = {}  # product_id -> {name, price, qty, stock}
        self.title("Food & Drinks POS")
        self.geometry("1000x650")
        self._center()
        apply_tree_style()
        self._build_ui()
        self._load_products()
        bring_to_front(self)

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1000) // 2
        y = (self.winfo_screenheight() - 650) // 2
        self.geometry(f"1000x650+{x}+{y}")

    def _build_ui(self):
        section_header(self, "🛒  Food & Drinks — Point of Sale", accent_color="#ef4444")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=18, pady=(14, 18), fill="both", expand=True)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        # ── Left: Product grid ────────────────────────────────────────────────
        left = ctk.CTkFrame(content, corner_radius=12)
        left.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(left, text="Products",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(12, 6))

        self.product_scroll = ctk.CTkScrollableFrame(left)
        self.product_scroll.pack(padx=10, pady=4, fill="both", expand=True)
        self._product_btns = []

        # ── Right: Cart ───────────────────────────────────────────────────────
        right = ctk.CTkFrame(content, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(right, text="Cart",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(12, 6))

        tree_frame = ctk.CTkFrame(right)
        tree_frame.pack(padx=10, pady=4, fill="both", expand=True)

        cols = ("Item", "Qty", "Price", "Subtotal")
        self.cart_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse", height=10)
        for col in cols:
            self.cart_tree.heading(col, text=col)
        self.cart_tree.column("Item", width=130)
        self.cart_tree.column("Qty", width=40, anchor="center")
        self.cart_tree.column("Price", width=70, anchor="center")
        self.cart_tree.column("Subtotal", width=80, anchor="center")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.cart_tree.pack(fill="both", expand=True)

        # Total label
        self.total_label = ctk.CTkLabel(right, text="Total: ₱0.00",
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.total_label.pack(pady=8)

        # Cart buttons
        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.pack(padx=10, pady=(0, 8), fill="x")
        ctk.CTkButton(btn_row, text="Remove", width=90, height=34,
                      fg_color="#b03a2e", hover_color="#e74c3c",
                      command=self._remove_item).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="Clear", width=80, height=34,
                      fg_color="gray", hover_color="#555",
                      command=self._clear_cart).pack(side="left", padx=4)
        ctk.CTkButton(right, text="✔  Checkout", height=44,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._checkout).pack(padx=10, pady=(0, 12), fill="x")

    def _load_products(self):
        for btn in self._product_btns:
            btn.destroy()
        self._product_btns.clear()

        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("SELECT id, name, category, price, stock FROM products ORDER BY category, name")
            rows = c.fetchall()
        finally:
            conn.close()

        for i, (pid, name, category, price, stock) in enumerate(rows):
            label_text = f"{name}\n₱{float(price):,.2f}\nStock: {stock}"
            btn = ctk.CTkButton(
                self.product_scroll,
                text=label_text,
                height=70,
                font=ctk.CTkFont(size=12),
                state="normal" if stock > 0 else "disabled",
                fg_color=("gray70", "gray30") if stock == 0 else None,
                command=lambda p=pid, n=name, pr=float(price), s=stock: self._add_to_cart(p, n, pr, s),
            )
            row, col = divmod(i, 3)
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self._product_btns.append(btn)

        for col in range(3):
            self.product_scroll.columnconfigure(col, weight=1)

        self._product_data = {row[0]: {"name": row[1], "price": float(row[3]), "stock": row[4]}
                              for row in rows}

    def _add_to_cart(self, product_id, name, price, stock):
        if product_id in self._cart:
            if self._cart[product_id]["qty"] >= stock:
                messagebox.showwarning("Insufficient Stock",
                                       f"Insufficient stock for {name}.", parent=self)
                return
            self._cart[product_id]["qty"] += 1
        else:
            self._cart[product_id] = {"name": name, "price": price, "qty": 1, "stock": stock}
        self._refresh_cart()

    def _refresh_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        total = 0.0
        for pid, item in self._cart.items():
            subtotal = item["price"] * item["qty"]
            total += subtotal
            self.cart_tree.insert("", "end", iid=str(pid),
                                  values=(item["name"], item["qty"],
                                          f"₱{item['price']:,.2f}", f"₱{subtotal:,.2f}"))
        self.total_label.configure(text=f"Total: ₱{total:,.2f}")

    def _remove_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an item to remove.", parent=self)
            return
        pid = int(sel[0])
        del self._cart[pid]
        self._refresh_cart()

    def _clear_cart(self):
        if self._cart and messagebox.askyesno("Clear Cart", "Clear all items?", parent=self):
            self._cart.clear()
            self._refresh_cart()

    def _checkout(self):
        if not self._cart:
            messagebox.showwarning("Empty Cart", "Please add items to the cart first.", parent=self)
            return

        customer = simpledialog.askstring("Customer Name", "Enter customer name:", parent=self)
        if not customer or not customer.strip():
            return
        customer = customer.strip()

        # Validate stock once more
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            for pid, item in self._cart.items():
                c.execute("SELECT stock FROM products WHERE id=%s", (pid,))
                row = c.fetchone()
                if not row or row[0] < item["qty"]:
                    messagebox.showerror("Stock Error",
                                         f"Insufficient stock for {item['name']}.", parent=self)
                    return

            total = sum(item["price"] * item["qty"] for item in self._cart.values())

            c.execute(
                "INSERT INTO transactions (type, customer_name, total_amount, processed_by) "
                "VALUES ('food',%s,%s,%s)",
                (customer, total, self.user["id"]),
            )
            trans_id = c.lastrowid

            items_for_receipt = []
            for pid, item in self._cart.items():
                subtotal = item["price"] * item["qty"]
                c.execute(
                    "INSERT INTO transaction_items (transaction_id, item_name, quantity, unit_price, subtotal) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (trans_id, item["name"], item["qty"], item["price"], subtotal),
                )
                c.execute("UPDATE products SET stock = stock - %s WHERE id=%s", (item["qty"], pid))
                items_for_receipt.append((item["name"], item["qty"], item["price"], subtotal))

            conn.commit()
        finally:
            conn.close()

        self._cart.clear()
        self._refresh_cart()
        self._load_products()
        self.dashboard.refresh_stats()

        ReceiptDialog(self, {
            "trans_id": trans_id,
            "type": "Food Sale",
            "customer": customer,
            "items": items_for_receipt,
            "total": total,
        })

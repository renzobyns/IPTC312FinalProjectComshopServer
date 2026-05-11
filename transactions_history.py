import customtkinter as ctk
from tkinter import messagebox, ttk
from db_connection import get_connection
from tree_style import apply_tree_style
from ui_helpers import bring_to_front, section_header
from datetime import date, datetime


class TransactionsHistory(ctk.CTkToplevel):
    def __init__(self, dashboard):
        super().__init__(dashboard)
        self.dashboard = dashboard
        self.title("Transaction History")
        self.geometry("1020x660")
        self._center()
        apply_tree_style()
        self._build_ui()
        self._load_data()
        bring_to_front(self)

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1020) // 2
        y = (self.winfo_screenheight() - 660) // 2
        self.geometry(f"1020x660+{x}+{y}")

    def _build_ui(self):
        section_header(self, "📋  Transaction History", accent_color="#8b5cf6")

        # ── Filter bar ─────────────────────────────────────────────────────────
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(padx=22, pady=(16, 6), fill="x")

        ctk.CTkLabel(filter_frame, text="Type:").pack(side="left")
        self._type_var = ctk.StringVar(value="All")
        type_menu = ctk.CTkOptionMenu(filter_frame, variable=self._type_var, width=130, height=32,
                                      values=["All", "pc_rental", "food", "printing"],
                                      command=lambda _: self._load_data())
        type_menu.pack(side="left", padx=8)

        ctk.CTkLabel(filter_frame, text="Status:").pack(side="left")
        self._status_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(filter_frame, variable=self._status_var, width=120, height=32,
                          values=["All", "Completed", "Refunded"],
                          command=lambda _: self._load_data()).pack(side="left", padx=8)

        ctk.CTkLabel(filter_frame, text="Customer:").pack(side="left")
        self._cust_var = ctk.StringVar()
        self._cust_var.trace_add("write", lambda *_: self._load_data())
        ctk.CTkEntry(filter_frame, textvariable=self._cust_var, width=160, height=32).pack(side="left", padx=8)

        ctk.CTkLabel(filter_frame, text="Date (YYYY-MM-DD):").pack(side="left")
        self._date_var = ctk.StringVar()
        self._date_var.trace_add("write", lambda *_: self._load_data())
        ctk.CTkEntry(filter_frame, textvariable=self._date_var, width=130, height=32).pack(side="left", padx=8)

        ctk.CTkButton(filter_frame, text="Refresh", width=84, height=32,
                      command=self._load_data).pack(side="right", padx=4)
        ctk.CTkButton(filter_frame, text="Clear Filters", width=100, height=32,
                      fg_color="gray", hover_color="#555",
                      command=self._clear_filters).pack(side="right", padx=4)

        # ── Treeview ───────────────────────────────────────────────────────────
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(padx=22, pady=(8, 0), fill="both", expand=True)

        cols = ("ID", "Type", "Customer", "Total", "Date & Time", "Processed By", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Type", width=110, anchor="center")
        self.tree.column("Customer", width=150)
        self.tree.column("Total", width=100, anchor="center")
        self.tree.column("Date & Time", width=150, anchor="center")
        self.tree.column("Processed By", width=130)
        self.tree.column("Status", width=100, anchor="center")

        self.tree.tag_configure("refunded", foreground="#ef4444")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self._view_detail)

        # ── Summary footer ─────────────────────────────────────────────────────
        footer = ctk.CTkFrame(self, corner_radius=0, height=48)
        footer.pack(fill="x", padx=0)
        footer.pack_propagate(False)

        self._summary_label = ctk.CTkLabel(
            footer, text="",
            font=ctk.CTkFont(size=12),
        )
        self._summary_label.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(footer, text="Double-click a row to view items",
                     text_color="gray", font=ctk.CTkFont(size=11)).pack(side="right", padx=20)

    def _build_query(self):
        conditions = []
        params = []
        type_val = self._type_var.get()
        if type_val != "All":
            conditions.append("t.type = %s")
            params.append(type_val)

        status_val = self._status_var.get()
        if status_val == "Completed":
            conditions.append("(t.status = 'completed' OR t.status IS NULL)")
        elif status_val == "Refunded":
            conditions.append("t.status = 'refunded'")

        cust = self._cust_var.get().strip()
        if cust:
            conditions.append("t.customer_name LIKE %s")
            params.append(f"%{cust}%")

        date_str = self._date_var.get().strip()
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                conditions.append("DATE(t.datetime) = %s")
                params.append(date_str)
            except ValueError:
                pass

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        return where, params

    def _load_data(self):
        where, params = self._build_query()
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute(f"""
                SELECT t.id, t.type, t.customer_name, t.total_amount,
                       t.datetime, COALESCE(u.full_name,'—'), COALESCE(t.status,'completed')
                FROM transactions t
                LEFT JOIN users u ON t.processed_by = u.id
                {where}
                ORDER BY t.datetime DESC
            """, params)
            rows = c.fetchall()

            c.execute(f"""
                SELECT COUNT(*), COALESCE(SUM(t.total_amount),0),
                       COALESCE(SUM(CASE WHEN DATE(t.datetime)=CURDATE() THEN t.total_amount ELSE 0 END),0)
                FROM transactions t
                {where}
            """, params)
            count, total_rev, today_rev = c.fetchone()
        finally:
            conn.close()

        self.tree.delete(*self.tree.get_children())
        type_labels = {"pc_rental": "PC Rental", "food": "Food", "printing": "Printing"}
        for row in rows:
            tid, ttype, customer, amount, dt, processed, status = row
            tag = ("refunded",) if status == "refunded" else ()
            self.tree.insert("", "end", tags=tag, values=(
                tid,
                type_labels.get(ttype, ttype),
                customer,
                f"₱{float(amount):,.2f}",
                dt.strftime("%Y-%m-%d %H:%M") if dt else "—",
                processed,
                "Refunded" if status == "refunded" else "Completed",
            ))

        self._summary_label.configure(
            text=f"Records: {count}   |   Filtered Total: ₱{float(total_rev):,.2f}   |   Today's Revenue: ₱{float(today_rev):,.2f}"
        )

    def _clear_filters(self):
        self._type_var.set("All")
        self._status_var.set("All")
        self._cust_var.set("")
        self._date_var.set("")

    def _view_detail(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        trans_id = self.tree.item(sel[0])["values"][0]
        TransactionDetail(self, trans_id)


class TransactionDetail(ctk.CTkToplevel):
    def __init__(self, parent, trans_id: int):
        super().__init__(parent)
        self.title(f"Transaction #{trans_id} — Details")
        self.geometry("540x440")
        apply_tree_style()
        self._build(trans_id)
        self.grab_set()
        bring_to_front(self)

    def _build(self, trans_id):
        ctk.CTkLabel(self, text=f"Transaction #{trans_id}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(16, 6))

        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor(dictionary=True)
            c.execute("""
                SELECT t.*, COALESCE(u.full_name,'—') as proc_name
                FROM transactions t
                LEFT JOIN users u ON t.processed_by = u.id
                WHERE t.id=%s
            """, (trans_id,))
            trans = c.fetchone()
            c.execute("SELECT * FROM transaction_items WHERE transaction_id=%s", (trans_id,))
            items = c.fetchall()
        finally:
            conn.close()

        if not trans:
            ctk.CTkLabel(self, text="Transaction not found.").pack()
            return

        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(padx=24, pady=4, fill="x")
        type_labels = {"pc_rental": "PC Rental", "food": "Food", "printing": "Printing"}
        status_label = "Refunded" if trans.get("status") == "refunded" else "Completed"
        for label, val in [
            ("Type:", type_labels.get(trans["type"], trans["type"])),
            ("Status:", status_label),
            ("Customer:", trans["customer_name"]),
            ("Date/Time:", trans["datetime"].strftime("%Y-%m-%d %H:%M:%S") if trans["datetime"] else "—"),
            ("Processed By:", trans["proc_name"]),
        ]:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=label, width=120, anchor="w",
                         font=ctk.CTkFont(size=12)).pack(side="left")
            ctk.CTkLabel(row, text=str(val), anchor="w",
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        ctk.CTkLabel(self, text="Items:", font=ctk.CTkFont(size=13, weight="bold"),
                     anchor="w").pack(padx=24, pady=(8, 4), fill="x")

        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(padx=24, pady=4, fill="both", expand=True)
        cols = ("Item", "Qty", "Unit Price", "Subtotal")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=6)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("Item", width=200)
        tree.column("Qty", width=50, anchor="center")
        tree.column("Unit Price", width=90, anchor="center")
        tree.column("Subtotal", width=90, anchor="center")

        for item in items:
            tree.insert("", "end", values=(
                item["item_name"], item["quantity"],
                f"₱{float(item['unit_price']):,.2f}",
                f"₱{float(item['subtotal']):,.2f}",
            ))
        tree.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text=f"TOTAL: ₱{float(trans['total_amount']):,.2f}",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=6)

        ctk.CTkButton(self, text="Close", height=36, command=self.destroy).pack(
            padx=24, pady=10, fill="x")

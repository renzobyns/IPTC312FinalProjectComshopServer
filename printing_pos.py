import customtkinter as ctk
from tkinter import messagebox
from db_connection import get_connection
from ui_helpers import bring_to_front, section_header
from session_management import ReceiptDialog


class PrintingPOS(ctk.CTkToplevel):
    def __init__(self, dashboard, user: dict):
        super().__init__(dashboard)
        self.dashboard = dashboard
        self.user = user
        self._services = []
        self.title("Printing Services")
        self.geometry("520x500")
        self.resizable(False, False)
        self._center()
        self._build_ui()
        self._load_services()
        bring_to_front(self)

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 520) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"520x500+{x}+{y}")

    def _build_ui(self):
        section_header(self, "🖨  Printing Services", accent_color="#06b6d4")

        form = ctk.CTkFrame(self, corner_radius=12)
        form.pack(padx=40, pady=(18, 16), fill="x")

        ctk.CTkLabel(form, text="Service Type:", anchor="w").pack(padx=24, pady=(20, 4), fill="x")
        self.service_menu = ctk.CTkOptionMenu(form, values=[], height=38,
                                              command=self._update_total)
        self.service_menu.pack(padx=24, fill="x")

        ctk.CTkLabel(form, text="Customer Name:", anchor="w").pack(padx=24, pady=(14, 4), fill="x")
        self.customer_entry = ctk.CTkEntry(form, height=38)
        self.customer_entry.pack(padx=24, fill="x")

        ctk.CTkLabel(form, text="Number of Pages:", anchor="w").pack(padx=24, pady=(14, 4), fill="x")
        self.pages_entry = ctk.CTkEntry(form, height=38, placeholder_text="e.g. 5")
        self.pages_entry.pack(padx=24, fill="x")
        self.pages_entry.bind("<KeyRelease>", lambda _: self._update_total())

        self.total_label = ctk.CTkLabel(form, text="Total: ₱0.00",
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.total_label.pack(pady=10)

        ctk.CTkButton(form, text="Process Transaction", height=44,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._process).pack(padx=24, pady=(0, 20), fill="x")

    def _load_services(self):
        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute("SELECT id, service_name, price_per_page FROM print_services ORDER BY id")
            self._services = c.fetchall()
        finally:
            conn.close()
        labels = [f"{s[1]} — ₱{float(s[2]):,.2f}/page" for s in self._services]
        self.service_menu.configure(values=labels if labels else ["No services"])
        if labels:
            self.service_menu.set(labels[0])

    def _get_selected_service(self):
        label = self.service_menu.get()
        for svc in self._services:
            if f"{svc[1]} — ₱{float(svc[2]):,.2f}/page" == label:
                return svc
        return None

    def _update_total(self, *_):
        svc = self._get_selected_service()
        if not svc:
            return
        try:
            pages = int(self.pages_entry.get())
            if pages <= 0:
                raise ValueError
            total = pages * float(svc[2])
            self.total_label.configure(text=f"Total: ₱{total:,.2f}")
        except (ValueError, TypeError):
            self.total_label.configure(text="Total: ₱0.00")

    def _process(self):
        customer = self.customer_entry.get().strip()
        pages_str = self.pages_entry.get().strip()
        svc = self._get_selected_service()

        if not customer:
            messagebox.showwarning("Validation", "Please fill in all required fields.", parent=self)
            return
        if not svc:
            messagebox.showwarning("Validation", "Please select a print service.", parent=self)
            return
        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation",
                                   "Please enter a valid positive number for pages.", parent=self)
            return

        total = pages * float(svc[2])
        item_name = f"{svc[1]} × {pages} page(s)"

        conn = get_connection()
        if not conn:
            return
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO transactions (type, customer_name, total_amount, processed_by) "
                "VALUES ('printing',%s,%s,%s)",
                (customer, total, self.user["id"]),
            )
            trans_id = c.lastrowid
            c.execute(
                "INSERT INTO transaction_items (transaction_id, item_name, quantity, unit_price, subtotal) "
                "VALUES (%s,%s,%s,%s,%s)",
                (trans_id, item_name, pages, float(svc[2]), total),
            )
            conn.commit()
        finally:
            conn.close()

        self.customer_entry.delete(0, "end")
        self.pages_entry.delete(0, "end")
        self.total_label.configure(text="Total: ₱0.00")
        self.dashboard.refresh_stats()

        ReceiptDialog(self, {
            "trans_id": trans_id,
            "type": "Printing",
            "customer": customer,
            "items": [(item_name, pages, float(svc[2]), total)],
            "total": total,
        })

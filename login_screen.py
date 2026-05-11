import customtkinter as ctk
from tkinter import messagebox
from auth import verify_login


class LoginScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OG Gaming Hub")
        self.geometry("440x540")
        self.resizable(False, False)
        self._center()
        self._build_ui()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 440) // 2
        y = (self.winfo_screenheight() - 540) // 2
        self.geometry(f"440x540+{x}+{y}")

    def _build_ui(self):
        ctk.CTkLabel(self, text="⚡", font=ctk.CTkFont(size=48)).pack(pady=(40, 0))
        ctk.CTkLabel(self, text="OG GAMING HUB", font=ctk.CTkFont(size=38, weight="bold")).pack(pady=(0, 2))
        ctk.CTkLabel(self, text="Gaming Hub Management", font=ctk.CTkFont(size=14)).pack()
        ctk.CTkLabel(self, text="Administrator Login", font=ctk.CTkFont(size=11),
                     text_color="gray").pack(pady=(4, 26))

        frame = ctk.CTkFrame(self, corner_radius=14)
        frame.pack(padx=44, fill="x")

        ctk.CTkLabel(frame, text="Username", anchor="w",
                     font=ctk.CTkFont(size=13)).pack(padx=24, pady=(22, 4), fill="x")
        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Enter username", height=42)
        self.username_entry.pack(padx=24, fill="x")

        ctk.CTkLabel(frame, text="Password", anchor="w",
                     font=ctk.CTkFont(size=13)).pack(padx=24, pady=(14, 4), fill="x")

        pw_row = ctk.CTkFrame(frame, fg_color="transparent")
        pw_row.pack(padx=24, fill="x")
        self.password_entry = ctk.CTkEntry(pw_row, placeholder_text="Enter password",
                                           show="●", height=42)
        self.password_entry.pack(side="left", fill="x", expand=True)
        self._show_pw = False
        ctk.CTkButton(
            pw_row, text="👁", width=42, height=42,
            fg_color="transparent", hover_color=("gray75", "gray25"),
            command=self._toggle_password,
        ).pack(side="left", padx=(6, 0))

        self.login_btn = ctk.CTkButton(
            frame, text="LOGIN", height=46,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._attempt_login,
        )
        self.login_btn.pack(padx=24, pady=22, fill="x")

        self.password_entry.bind("<Return>", lambda _: self._attempt_login())
        self.username_entry.bind("<Return>", lambda _: self.password_entry.focus())

    def _toggle_password(self):
        self._show_pw = not self._show_pw
        self.password_entry.configure(show="" if self._show_pw else "●")

    def _attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Validation", "Please fill in all required fields.", parent=self)
            return

        self.login_btn.configure(state="disabled", text="Logging in...")
        self.update()

        user = verify_login(username, password)

        self.login_btn.configure(state="normal", text="LOGIN")

        if user:
            from dashboard import Dashboard
            self.withdraw()
            dash = Dashboard(user, self)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=self)
            self.password_entry.delete(0, "end")
            self.password_entry.focus()

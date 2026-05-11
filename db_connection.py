import mysql.connector
from tkinter import messagebox

_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "comshop_db",
    "port": 3306,
}


def get_connection():
    try:
        return mysql.connector.connect(**_CONFIG)
    except mysql.connector.Error as e:
        messagebox.showerror(
            "Database Connection Error",
            f"Cannot connect to the database.\n"
            f"Please make sure XAMPP MySQL is running.\n\n"
            f"Details: {e}",
        )
        return None

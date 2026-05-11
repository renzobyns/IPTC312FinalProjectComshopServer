import hashlib
from db_connection import get_connection


def hash_password(plain_text: str) -> str:
    return hashlib.sha256(plain_text.encode()).hexdigest()


def verify_login(username: str, plain_password: str):
    """Return user dict on success, None on failure."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, full_name FROM users "
            "WHERE username = %s AND password_hash = %s",
            (username, hash_password(plain_password)),
        )
        return cursor.fetchone()
    finally:
        conn.close()

import sqlite3
from django.conf import settings


def get_conn():
    conn = sqlite3.connect(settings.BOT_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_users():
    with get_conn() as conn:
        return conn.execute(
            "SELECT user_id, phone, first_name, role, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()


def get_user(user_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT user_id, phone, first_name, role, created_at FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()


def set_role(user_id, role):
    with get_conn() as conn:
        conn.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))
        conn.commit()


def delete_user(user_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()


def get_user_count():
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def get_all_korxonalar():
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, nomi, inn, created_at FROM korxonalar ORDER BY id"
        ).fetchall()


def get_korxona(k_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, nomi, inn, created_at FROM korxonalar WHERE id = ?", (k_id,)
        ).fetchone()


def add_korxona(nomi, inn):
    with get_conn() as conn:
        conn.execute("INSERT INTO korxonalar (nomi, inn) VALUES (?, ?)", (nomi, inn))
        conn.commit()


def update_korxona(k_id, nomi, inn):
    with get_conn() as conn:
        conn.execute("UPDATE korxonalar SET nomi = ?, inn = ? WHERE id = ?", (nomi, inn, k_id))
        conn.commit()


def delete_korxona(k_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM korxonalar WHERE id = ?", (k_id,))
        conn.commit()


def inn_exists(inn, exclude_id=None):
    with get_conn() as conn:
        if exclude_id:
            row = conn.execute(
                "SELECT 1 FROM korxonalar WHERE inn = ? AND id != ?", (inn, exclude_id)
            ).fetchone()
        else:
            row = conn.execute("SELECT 1 FROM korxonalar WHERE inn = ?", (inn,)).fetchone()
        return row is not None


def get_all_hisobotlar():
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, user_id, first_name, role, file_id, file_name, sent_at FROM hisobotlar ORDER BY sent_at DESC"
        ).fetchall()


def get_bot_active():
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = 'bot_active'").fetchone()
        return row[0] == "1" if row else True


def set_bot_active(active: bool):
    with get_conn() as conn:
        conn.execute(
            "UPDATE settings SET value = ? WHERE key = 'bot_active'",
            ("1" if active else "0",)
        )
        conn.commit()

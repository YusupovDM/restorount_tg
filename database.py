import sqlite3

from config import DB_PATH, TOTAL_TABLES, WINDOW_TABLES

DB_NAME = DB_PATH


def create_table():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                date           TEXT    NOT NULL,   -- 12.10.2026
                time           TEXT    NOT NULL,   -- 18:00
                guests         INTEGER NOT NULL,
                near_window    INTEGER NOT NULL,   -- 1 / 0
                status         TEXT    NOT NULL,   -- awaiting_payment / confirmed / cancelled
                payment_status TEXT    NOT NULL,   -- not_required / pending / paid
                created_at     TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_booking(user_id, date, time, guests, near_window, status, payment_status):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "INSERT INTO bookings (user_id, date, time, guests, near_window, status, payment_status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, date, time, guests, int(near_window), status, payment_status),
        )
        return cursor.lastrowid


def get_booking(booking_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
        return dict(row) if row else None


def get_user_bookings(user_id):
    """Активные (не отменённые) брони пользователя."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM bookings WHERE user_id = ? AND status != 'cancelled' ORDER BY id",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def cancel_booking(booking_id, user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "UPDATE bookings SET status = 'cancelled' "
            "WHERE id = ? AND user_id = ? AND status != 'cancelled'",
            (booking_id, user_id),
        )
        return cursor.rowcount > 0


def mark_paid(booking_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE bookings SET status = 'confirmed', payment_status = 'paid' WHERE id = ?",
            (booking_id,),
        )


def count_confirmed(date, time, near_window):
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM bookings "
            "WHERE date = ? AND time = ? AND near_window = ? AND status = 'confirmed'",
            (date, time, int(near_window)),
        ).fetchone()
        return row[0]


def is_slot_available(date, time, near_window):
    """Есть ли свободный столик (у окна или в зале) на это время."""
    capacity = WINDOW_TABLES if near_window else TOTAL_TABLES - WINDOW_TABLES
    return count_confirmed(date, time, near_window) < capacity

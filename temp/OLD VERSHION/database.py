import sqlite3

conn = sqlite3.connect("store.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    product TEXT,
    plan TEXT,
    payment_method TEXT,
    status TEXT
)
""")

conn.commit()


def create_order(user_id, username, product, plan, payment):
    cursor.execute(
        "INSERT INTO orders (user_id, username, product, plan, payment_method, status) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, username, product, plan, payment, "pending")
    )
    conn.commit()

    return cursor.lastrowid
import sqlite3

conn = sqlite3.connect("store.db", check_same_thread=False)
cursor = conn.cursor()

# -------------------------
# Subscription Orders Table
# -------------------------
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

# -------------------------
# Game Requests Table
# -------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS game_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    customer_name TEXT,
    game_name TEXT,
    platform TEXT,
    request_type TEXT,
    plan TEXT,
    preferred_payment TEXT,
    notes TEXT,
    offered_price TEXT,
    final_payment_method TEXT,
    status TEXT
)
""")

conn.commit()


# -------------------------
# Subscription Orders
# -------------------------
def create_order(user_id, username, product, plan, payment):
    cursor.execute(
        """
        INSERT INTO orders (user_id, username, product, plan, payment_method, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, username, product, plan, payment, "pending_confirmation")
    )
    conn.commit()
    return cursor.lastrowid


def update_order_status(order_id, status):
    cursor.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (status, order_id)
    )
    conn.commit()


def get_order(order_id):
    cursor.execute(
        """
        SELECT id, user_id, username, product, plan, payment_method, status
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    )
    return cursor.fetchone()


# -------------------------
# Game Requests
# -------------------------
def create_game_request(
    user_id,
    username,
    customer_name,
    game_name,
    platform,
    request_type,
    plan,
    preferred_payment,
    notes,
):
    cursor.execute(
        """
        INSERT INTO game_requests (
            user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            username,
            customer_name,
            game_name,
            platform,
            request_type,
            plan,
            preferred_payment,
            notes,
            "",
            "",
            "waiting_pricing",
        )
    )
    conn.commit()
    return cursor.lastrowid


def get_game_request(request_id):
    cursor.execute(
        """
        SELECT
            id, user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status
        FROM game_requests
        WHERE id = ?
        """,
        (request_id,)
    )
    return cursor.fetchone()


def update_game_request_status(request_id, status):
    cursor.execute(
        "UPDATE game_requests SET status = ? WHERE id = ?",
        (status, request_id)
    )
    conn.commit()


def set_game_request_price(request_id, price):
    cursor.execute(
        """
        UPDATE game_requests
        SET offered_price = ?, status = ?
        WHERE id = ?
        """,
        (price, "price_sent", request_id)
    )
    conn.commit()


def set_game_request_final_payment(request_id, payment_method):
    cursor.execute(
        """
        UPDATE game_requests
        SET final_payment_method = ?, status = ?
        WHERE id = ?
        """,
        (payment_method, "waiting_game_payment_screenshot", request_id)
    )
    conn.commit()
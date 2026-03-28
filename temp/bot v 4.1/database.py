import logging
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger("premium_store_bot.database")

conn = sqlite3.connect("store.db", check_same_thread=False)
conn.row_factory = None
cursor = conn.cursor()


@contextmanager
def db_transaction():
    try:
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("Database transaction failed")
        raise


def execute(query, params=()):
    with db_transaction():
        cursor.execute(query, params)
    return cursor


def fetch_one(query, params=()):
    cursor.execute(query, params)
    return cursor.fetchone()


def fetch_columns(table_name: str):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


# -------------------------
# Users Table
# -------------------------
execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    language TEXT DEFAULT 'en'
)
""")

# -------------------------
# Subscription Orders Table
# -------------------------
execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    product TEXT,
    plan TEXT,
    payment_method TEXT,
    status TEXT,
    delivery_text TEXT DEFAULT ''
)
""")

orders_columns = fetch_columns("orders")
if "delivery_text" not in orders_columns:
    execute("ALTER TABLE orders ADD COLUMN delivery_text TEXT DEFAULT ''")

# -------------------------
# Game Requests Table
# -------------------------
execute("""
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
    status TEXT,
    delivery_text TEXT DEFAULT ''
)
""")

game_columns = fetch_columns("game_requests")
if "delivery_text" not in game_columns:
    execute("ALTER TABLE game_requests ADD COLUMN delivery_text TEXT DEFAULT ''")


# -------------------------
# Users
# -------------------------
def get_user_language(user_id):
    row = fetch_one("SELECT language FROM users WHERE user_id = ?", (user_id,))
    return row[0] if row else None


def set_user_language(user_id, username, language):
    execute(
        """
        INSERT INTO users (user_id, username, language)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            language = excluded.language
        """,
        (user_id, username, language)
    )
    logger.info("DB set_user_language | user_id=%s | language=%s", user_id, language)


# -------------------------
# Subscription Orders
# -------------------------
def create_order(user_id, username, product, plan, payment):
    result = execute(
        """
        INSERT INTO orders (user_id, username, product, plan, payment_method, status, delivery_text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, username, product, plan, payment, "pending_confirmation", "")
    )
    order_id = result.lastrowid
    logger.info(
        "DB create_order | order_id=%s | user_id=%s | product=%s | plan=%s",
        order_id,
        user_id,
        product,
        plan,
    )
    return order_id


def update_order_status(order_id, status):
    execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (status, order_id)
    )
    logger.info("DB update_order_status | order_id=%s | status=%s", order_id, status)


def get_order(order_id):
    return fetch_one(
        """
        SELECT id, user_id, username, product, plan, payment_method, status, delivery_text
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    )


def set_order_delivery(order_id, delivery_text):
    execute(
        """
        UPDATE orders
        SET delivery_text = ?, status = ?
        WHERE id = ?
        """,
        (delivery_text, "delivered", order_id)
    )
    logger.info("DB set_order_delivery | order_id=%s | status=delivered", order_id)


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
    result = execute(
        """
        INSERT INTO game_requests (
            user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status, delivery_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            "",
        )
    )
    request_id = result.lastrowid
    logger.info(
        "DB create_game_request | request_id=%s | user_id=%s | game_name=%s | platform=%s",
        request_id,
        user_id,
        game_name,
        platform,
    )
    return request_id


def get_game_request(request_id):
    return fetch_one(
        """
        SELECT
            id, user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status, delivery_text
        FROM game_requests
        WHERE id = ?
        """,
        (request_id,)
    )


def update_game_request_status(request_id, status):
    execute(
        "UPDATE game_requests SET status = ? WHERE id = ?",
        (status, request_id)
    )
    logger.info("DB update_game_request_status | request_id=%s | status=%s", request_id, status)


def set_game_request_price(request_id, price):
    execute(
        """
        UPDATE game_requests
        SET offered_price = ?, status = ?
        WHERE id = ?
        """,
        (price, "price_sent", request_id)
    )
    logger.info("DB set_game_request_price | request_id=%s | price=%s", request_id, price)


def set_game_request_final_payment(request_id, payment_method):
    execute(
        """
        UPDATE game_requests
        SET final_payment_method = ?, status = ?
        WHERE id = ?
        """,
        (payment_method, "waiting_game_payment_screenshot", request_id)
    )
    logger.info(
        "DB set_game_request_final_payment | request_id=%s | payment_method=%s",
        request_id,
        payment_method,
    )


def set_game_request_delivery(request_id, delivery_text):
    execute(
        """
        UPDATE game_requests
        SET delivery_text = ?, status = ?
        WHERE id = ?
        """,
        (delivery_text, "delivered", request_id)
    )
    logger.info("DB set_game_request_delivery | request_id=%s | status=delivered", request_id)

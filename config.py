import os
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"{name} is missing from .env")
    return value.strip()


def _get_int_env(name: str, default: str | None = None, required: bool = False) -> int:
    raw = os.getenv(name, default)
    if raw is None or not str(raw).strip():
        if required:
            raise ValueError(f"{name} is missing from .env")
        raise ValueError(f"{name} is empty")
    try:
        return int(str(raw).strip())
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid integer") from exc


def _get_admin_user_ids() -> set[int]:
    raw = os.getenv("ADMIN_USER_IDS", "")
    ids = set()
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if not item.isdigit():
            raise ValueError("ADMIN_USER_IDS must contain comma-separated numeric Telegram user IDs")
        ids.add(int(item))
    return ids


BOT_TOKEN = _require_env("BOT_TOKEN")
SUPPORT_GROUP_ID = _get_int_env("SUPPORT_GROUP_ID", required=True)
ORDERS_GROUP_ID = _get_int_env("ORDERS_GROUP_ID", default=str(SUPPORT_GROUP_ID), required=False)

STORE_NAME = os.getenv("STORE_NAME", "Premium Subs Jordan 🇯🇴").strip()
CLIQ_NAME = _require_env("CLIQ_NAME")
USDT_WALLET = _require_env("USDT_WALLET")
USDT_NETWORK = os.getenv("USDT_NETWORK", "Solana (SOL)").strip()
SUPPORT_USERNAME = _require_env("SUPPORT_USERNAME")

ADMIN_USER_IDS = _get_admin_user_ids()
ADMIN_LANG = os.getenv("ADMIN_LANG", "en").strip().lower()
if ADMIN_LANG not in {"ar", "en"}:
    ADMIN_LANG = "en"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper()
LOG_DIR = os.getenv("LOG_DIR", "logs").strip() or "logs"
LOG_FILE = os.getenv("LOG_FILE", os.path.join(LOG_DIR, "bot.log")).strip()


def validate_config(logger=None):
    warnings = []

    if not ADMIN_USER_IDS:
        warnings.append("ADMIN_USER_IDS is empty. Administrative actions will be blocked.")
    if not STORE_NAME:
        raise ValueError("STORE_NAME cannot be empty")
    if not USDT_NETWORK:
        raise ValueError("USDT_NETWORK cannot be empty")
    if not LOG_DIR:
        raise ValueError("LOG_DIR cannot be empty")
    if not LOG_FILE:
        raise ValueError("LOG_FILE cannot be empty")

    for warning in warnings:
        if logger:
            logger.warning(warning)

    return True

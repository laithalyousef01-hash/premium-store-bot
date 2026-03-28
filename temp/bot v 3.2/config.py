import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# جروب الدعم الحالي
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID"))

# جروب الأوردرات - إن لم يوجد في .env سيستخدم نفس جروب الدعم
ORDERS_GROUP_ID = int(os.getenv("ORDERS_GROUP_ID", os.getenv("SUPPORT_GROUP_ID")))

STORE_NAME = "Premium Subs Jordan 🇯🇴"

CLIQ_NAME = "PREMIUMJO1"
USDT_WALLET = "CwErrEJ9KnP67jeWtNttuDmnk9BiN7RLqaY39nQCQLUH"
USDT_NETWORK = "Solana (SOL)"
SUPPORT_USERNAME = "https://t.me/+6OSsHHXiQQFlYTJk"
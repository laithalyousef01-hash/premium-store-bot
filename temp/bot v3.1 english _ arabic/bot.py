import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import config
from database import (
    create_order,
    update_order_status,
    get_order,
    set_order_delivery,
    create_game_request,
    get_game_request,
    update_game_request_status,
    set_game_request_price,
    set_game_request_final_payment,
    set_game_request_delivery,
    get_user_language,
    set_user_language,
)


with open("products.json", "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


TEXTS = {
    "en": {
        "choose_language": "Choose your language / اختر لغتك",
        "language_saved": "✅ Language updated successfully.",
        "welcome": f"Welcome to {config.STORE_NAME}\nChoose an option:",
        "menu_subscriptions": "🛒 Subscriptions",
        "menu_request_game": "🎮 Request Game",
        "menu_payments": "💳 Payment Methods",
        "menu_support": "🛠 Support",
        "menu_language": "🌐 Language",
        "back": "⬅ Back",
        "main_menu": "🏠 Main Menu",
        "choose_subscription": "Choose a subscription:",
        "product_not_found": "Product not found.",
        "choose_payment": "Choose payment method:",
        "session_expired": "Session expired. Please start again.",
        "missing_order_data": "Missing order data. Please start again.",
        "payments_info": (
            f"💳 Payment Methods\n\n"
            f"1) CliQ / Bank Transfer\n"
            f"Receiver Name: {config.CLIQ_NAME}\n\n"
            f"2) USDT Wallet\n"
            f"Network: {config.USDT_NETWORK}\n"
            f"Address:\n{config.USDT_WALLET}\n\n"
            f"⚠️ Please send only on {config.USDT_NETWORK}"
        ),
        "support_info": f"🛠 Support\n\nFor help, contact:\n{config.SUPPORT_USERNAME}",
        "usdt_payment_title": "💰 USDT Payment",
        "bank_payment_title": "🏦 CliQ / Bank Transfer",
        "receiver_name": "Receiver Name",
        "after_payment_confirm": "After sending the payment, press Confirm Purchase.",
        "confirm_purchase": "✅ Confirm Purchase",
        "purchase_confirmed": "✅ Purchase confirmed successfully",
        "send_payment_screenshot": "Now send the payment screenshot here.",
        "order_send_error": "There is a problem sending the order to support. Please try again later.",
        "payment_screenshot_received": "✅ Payment screenshot received.",
        "team_review_deliver": "Our team will review it and deliver your product soon.",
        "payment_screenshot_error": "There is a problem sending your payment screenshot to support. Please contact support.",
        "confirm_first": "Please confirm your purchase first, then send the payment screenshot.",
        "request_game_name": "🎮 Enter the game name.\n\nExample:\nEA FC 25",
        "choose_platform": "🎮 Choose the platform:",
        "choose_request_type": "📦 Choose the request type:",
        "choose_plan": "📅 Choose the plan or duration:",
        "choose_preferred_payment": "💳 Choose the preferred payment method:",
        "send_notes": "📝 Send any extra notes, or press Skip Notes.",
        "skip_notes": "Skip Notes",
        "submit_game_request": "✅ Submit Game Request",
        "edit": "✏ Edit",
        "game_summary_title": "🎮 Game Request Summary",
        "game_name": "Game Name",
        "platform": "Platform",
        "type": "Type",
        "plan": "Plan",
        "preferred_payment": "Preferred Payment",
        "notes": "Notes",
        "press_submit": "Press Submit to send your request.",
        "game_request_sent": "✅ Your game request was sent successfully.",
        "team_review_contact_price": "Our team will review it and contact you with the price.",
        "game_request_send_error": "There is a problem sending your request right now. Please try again later.",
        "price_accepted": "✅ Price accepted",
        "choose_payment_method": "Choose the payment method:",
        "customer_accepted_price": "Customer accepted the price for request",
        "request_cancelled_success": "❌ Request cancelled successfully.",
        "customer_cancelled_price": "Customer cancelled the price for request",
        "game_request_not_found": "Request not found.",
        "game_payment_usdt": "💰 Game Payment - USDT",
        "game_payment_bank": "🏦 Game Payment - CliQ / Bank",
        "send_game_screenshot": "Now send the payment screenshot here.",
        "game_payment_screenshot_received": "✅ Payment screenshot received.",
        "team_review_deliver_game": "Our team will review it and deliver your game soon.",
        "game_payment_screenshot_error": "There is a problem sending your payment screenshot to support. Please contact support.",
        "not_available_user": "❌ Sorry, your requested game is currently not available.",
        "please_start_menu": "Please use /start and choose an option from the menu.",
        "accept_price": "✅ Accept Price",
        "cancel": "❌ Cancel",
        "language_ar": "العربية",
        "language_en": "English",
        "request_id": "Request ID",
        "order_id": "Order ID",
        "price": "Price",
        "product": "Product",
        "payment_method": "Payment Method",
        "status": "Status",
        "customer_name": "Customer Name",
        "username": "Username",
        "quick_contact": "Quick Contact",
        "user_id": "User ID",
        "waiting_manual_pricing": "Waiting for manual pricing",
        "waiting_payment_screenshot": "Waiting for payment screenshot",
        "paid_awaiting_delivery": "Paid - Awaiting delivery",
        "delivered_subscription": "📦 Your subscription has been delivered successfully.",
        "delivered_game": "🎮 Your game order has been delivered successfully.",
        "thank_you": f"Thank you for choosing {config.STORE_NAME}.",
        "send_price_prompt": "Send the price now for request",
        "send_delivery_subscription_prompt": "Send the delivery details now for subscription order",
        "send_delivery_game_prompt": "Send the delivery details now for game request",
        "delivered_success_subscription": "Subscription order delivered successfully.",
        "delivered_success_game": "Game request delivered successfully.",
        "failed_deliver_subscription": "Failed to deliver subscription order.",
        "failed_deliver_game": "Failed to deliver game request.",
        "marked_unavailable": "Marked request as not available.",
        "price_sent_to_customer": "Price sent to customer for request",
        "failed_send_price": "Failed to send price to the customer for request",
        "available_game_message": "🎮 Your requested game is available ✅",
        "confirm_continue": "Please confirm to continue.",
        "profile": "Profile",
        "instructions": "Instructions",
        "change_password_note": "Change password after login",
        "other": "Other",
        "subscription": "Subscription",
        "topup": "Top-up",
        "code": "Code",
        "account": "Account",
        "one_month": "1 Month",
        "three_months": "3 Months",
        "six_months": "6 Months",
        "twelve_months": "12 Months",
        "lifetime": "Lifetime",
        "standard": "Standard",
        "deliver_subscription_btn": "📦 Deliver Subscription",
        "deliver_game_btn": "🎮 Deliver Game",
        "send_price_btn": "💵 Send Price",
        "not_available_btn": "❌ Not Available",
    },
    "ar": {
        "choose_language": "اختر لغتك / Choose your language",
        "language_saved": "✅ تم تحديث اللغة بنجاح.",
        "welcome": f"مرحبًا بك في {config.STORE_NAME}\nاختر من القائمة:",
        "menu_subscriptions": "🛒 الاشتراكات",
        "menu_request_game": "🎮 طلب لعبة",
        "menu_payments": "💳 طرق الدفع",
        "menu_support": "🛠 الدعم",
        "menu_language": "🌐 اللغة",
        "back": "⬅ رجوع",
        "main_menu": "🏠 القائمة الرئيسية",
        "choose_subscription": "اختر الاشتراك:",
        "product_not_found": "المنتج غير موجود.",
        "choose_payment": "اختر طريقة الدفع:",
        "session_expired": "انتهت الجلسة. ابدأ من جديد.",
        "missing_order_data": "بيانات الطلب ناقصة. ابدأ من جديد.",
        "payments_info": (
            f"💳 طرق الدفع\n\n"
            f"1) تحويل CliQ / بنك\n"
            f"اسم المستلم: {config.CLIQ_NAME}\n\n"
            f"2) محفظة USDT\n"
            f"الشبكة: {config.USDT_NETWORK}\n"
            f"العنوان:\n{config.USDT_WALLET}\n\n"
            f"⚠️ الرجاء الإرسال فقط على {config.USDT_NETWORK}"
        ),
        "support_info": f"🛠 الدعم\n\nللمساعدة تواصل عبر:\n{config.SUPPORT_USERNAME}",
        "usdt_payment_title": "💰 الدفع عبر USDT",
        "bank_payment_title": "🏦 التحويل البنكي / CliQ",
        "receiver_name": "اسم المستلم",
        "after_payment_confirm": "بعد إرسال الدفعة اضغط تأكيد الشراء.",
        "confirm_purchase": "✅ تأكيد الشراء",
        "purchase_confirmed": "✅ تم تأكيد الشراء بنجاح",
        "send_payment_screenshot": "الآن أرسل صورة الدفع هنا.",
        "order_send_error": "يوجد مشكلة في إرسال الطلب إلى الدعم. حاول مرة أخرى لاحقًا.",
        "payment_screenshot_received": "✅ تم استلام صورة الدفع.",
        "team_review_deliver": "سيتم مراجعتها وتسليم المنتج قريبًا.",
        "payment_screenshot_error": "يوجد مشكلة في إرسال صورة الدفع إلى الدعم. الرجاء التواصل مع الدعم.",
        "confirm_first": "الرجاء تأكيد الشراء أولًا ثم إرسال صورة الدفع.",
        "request_game_name": "🎮 اكتب اسم اللعبة.\n\nمثال:\nEA FC 25",
        "choose_platform": "🎮 اختر المنصة:",
        "choose_request_type": "📦 اختر نوع الطلب:",
        "choose_plan": "📅 اختر الخطة أو المدة:",
        "choose_preferred_payment": "💳 اختر طريقة الدفع المفضلة:",
        "send_notes": "📝 اكتب أي ملاحظات إضافية أو اضغط تخطي.",
        "skip_notes": "تخطي الملاحظات",
        "submit_game_request": "✅ إرسال طلب اللعبة",
        "edit": "✏ تعديل",
        "game_summary_title": "🎮 ملخص طلب اللعبة",
        "game_name": "اسم اللعبة",
        "platform": "المنصة",
        "type": "النوع",
        "plan": "الخطة",
        "preferred_payment": "الدفع المفضل",
        "notes": "الملاحظات",
        "press_submit": "اضغط إرسال لإتمام طلبك.",
        "game_request_sent": "✅ تم إرسال طلب اللعبة بنجاح.",
        "team_review_contact_price": "سيتم مراجعة الطلب والتواصل معك بالسعر.",
        "game_request_send_error": "يوجد مشكلة في إرسال الطلب الآن. حاول لاحقًا.",
        "price_accepted": "✅ تم قبول السعر",
        "choose_payment_method": "اختر طريقة الدفع:",
        "customer_accepted_price": "العميل وافق على السعر للطلب",
        "request_cancelled_success": "❌ تم إلغاء الطلب بنجاح.",
        "customer_cancelled_price": "العميل ألغى السعر للطلب",
        "game_request_not_found": "الطلب غير موجود.",
        "game_payment_usdt": "💰 دفع اللعبة عبر USDT",
        "game_payment_bank": "🏦 دفع اللعبة عبر CliQ / بنك",
        "send_game_screenshot": "الآن أرسل صورة الدفع هنا.",
        "game_payment_screenshot_received": "✅ تم استلام صورة الدفع.",
        "team_review_deliver_game": "سيتم مراجعتها وتسليم اللعبة قريبًا.",
        "game_payment_screenshot_error": "يوجد مشكلة في إرسال صورة الدفع إلى الدعم. الرجاء التواصل مع الدعم.",
        "not_available_user": "❌ عذرًا، اللعبة المطلوبة غير متوفرة حاليًا.",
        "please_start_menu": "الرجاء استخدام /start ثم اختيار خيار من القائمة.",
        "accept_price": "✅ قبول السعر",
        "cancel": "❌ إلغاء",
        "language_ar": "العربية",
        "language_en": "English",
        "request_id": "رقم الطلب",
        "order_id": "رقم الأوردر",
        "price": "السعر",
        "product": "المنتج",
        "payment_method": "طريقة الدفع",
        "status": "الحالة",
        "customer_name": "اسم العميل",
        "username": "اسم المستخدم",
        "quick_contact": "تواصل سريع",
        "user_id": "معرّف المستخدم",
        "waiting_manual_pricing": "بانتظار التسعير اليدوي",
        "waiting_payment_screenshot": "بانتظار صورة الدفع",
        "paid_awaiting_delivery": "تم الدفع - بانتظار التسليم",
        "delivered_subscription": "📦 تم تسليم الاشتراك بنجاح.",
        "delivered_game": "🎮 تم تسليم اللعبة بنجاح.",
        "thank_you": f"شكرًا لاختيارك {config.STORE_NAME}.",
        "send_price_prompt": "أرسل السعر الآن للطلب",
        "send_delivery_subscription_prompt": "أرسل الآن بيانات التسليم لطلب الاشتراك",
        "send_delivery_game_prompt": "أرسل الآن بيانات التسليم لطلب اللعبة",
        "delivered_success_subscription": "تم تسليم طلب الاشتراك بنجاح.",
        "delivered_success_game": "تم تسليم طلب اللعبة بنجاح.",
        "failed_deliver_subscription": "فشل تسليم طلب الاشتراك.",
        "failed_deliver_game": "فشل تسليم طلب اللعبة.",
        "marked_unavailable": "تم تعليم الطلب كغير متوفر.",
        "price_sent_to_customer": "تم إرسال السعر للعميل للطلب",
        "failed_send_price": "فشل إرسال السعر للعميل للطلب",
        "available_game_message": "🎮 اللعبة المطلوبة متوفرة ✅",
        "confirm_continue": "يرجى التأكيد للمتابعة.",
        "profile": "الملف الشخصي",
        "instructions": "التعليمات",
        "change_password_note": "غيّر كلمة المرور بعد تسجيل الدخول",
        "other": "أخرى",
        "subscription": "اشتراك",
        "topup": "شحن",
        "code": "كود",
        "account": "حساب",
        "one_month": "شهر واحد",
        "three_months": "3 أشهر",
        "six_months": "6 أشهر",
        "twelve_months": "12 شهر",
        "lifetime": "مدى الحياة",
        "standard": "قياسي",
        "deliver_subscription_btn": "📦 تسليم الاشتراك",
        "deliver_game_btn": "🎮 تسليم اللعبة",
        "send_price_btn": "💵 إرسال السعر",
        "not_available_btn": "❌ غير متوفر",
    },
}


def get_lang(user_id):
    lang = get_user_language(user_id)
    return lang if lang in ("ar", "en") else "en"


def t(user_id, key):
    lang = get_lang(user_id)
    return TEXTS[lang][key]


def localize_value(user_id, value: str) -> str:
    mapping = {
        "Subscription": t(user_id, "subscription"),
        "Top-up": t(user_id, "topup"),
        "Code": t(user_id, "code"),
        "Account": t(user_id, "account"),
        "1 Month": t(user_id, "one_month"),
        "3 Months": t(user_id, "three_months"),
        "6 Months": t(user_id, "six_months"),
        "12 Months": t(user_id, "twelve_months"),
        "Lifetime": t(user_id, "lifetime"),
        "Standard": t(user_id, "standard"),
        "Other": t(user_id, "other"),
    }
    return mapping.get(value, value)


# -------------------------
# Keyboards
# -------------------------
def language_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("العربية", callback_data="set_lang|ar"),
            InlineKeyboardButton("English", callback_data="set_lang|en"),
        ]
    ])


def main_menu_keyboard(user_id) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t(user_id, "menu_subscriptions"), callback_data="subscriptions")],
        [InlineKeyboardButton(t(user_id, "menu_request_game"), callback_data="request_game")],
        [InlineKeyboardButton(t(user_id, "menu_payments"), callback_data="payments")],
        [InlineKeyboardButton(t(user_id, "menu_support"), callback_data="support")],
        [InlineKeyboardButton(t(user_id, "menu_language"), callback_data="change_language")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main_keyboard(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "back"), callback_data="main_menu")]
    ])


def build_back_keyboard(user_id, callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "back"), callback_data=callback_data)]
    ])


def payment_keyboard(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("USDT", callback_data="pay_usdt")],
        [InlineKeyboardButton("CliQ / Bank", callback_data="pay_bank")],
        [InlineKeyboardButton(t(user_id, "back"), callback_data="subscriptions")],
    ])


def confirm_order_keyboard(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "confirm_purchase"), callback_data="confirm_purchase")],
        [InlineKeyboardButton(t(user_id, "back"), callback_data="change_payment")],
        [InlineKeyboardButton(t(user_id, "main_menu"), callback_data="main_menu")],
    ])


def game_platform_keyboard(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("PS5", callback_data="game_platform|PS5"),
            InlineKeyboardButton("PS4", callback_data="game_platform|PS4"),
        ],
        [
            InlineKeyboardButton("PC", callback_data="game_platform|PC"),
            InlineKeyboardButton("Xbox", callback_data="game_platform|Xbox"),
        ],
        [
            InlineKeyboardButton("Steam", callback_data="game_platform|Steam"),
            InlineKeyboardButton(localize_value(user_id, "Other"), callback_data="game_platform|Other"),
        ],
        [InlineKeyboardButton(t(user_id, "back"), callback_data="main_menu")],
    ])


def game_type_keyboard(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(localize_value(user_id, "Subscription"), callback_data="game_type|Subscription"),
            InlineKeyboardButton(localize_value(user_id, "Top-up"), callback_data="game_type|Top-up"),
        ],
        [
            InlineKeyboardButton(localize_value(user_id, "Code"), callback_data="game_type|Code"),
            InlineKeyboardButton(localize_value(user_id, "Account"), callback_data="game_type|Account"),
        ],
        [InlineKeyboardButton(t(user_id, "back"), callback_data="request_game")],
    ])


def game_plan_keyboard(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(localize_value(user_id, "1 Month"), callback_data="game_plan|1 Month"),
            InlineKeyboardButton(localize_value(user_id, "3 Months"), callback_data="game_plan|3 Months"),
        ],
        [
            InlineKeyboardButton(localize_value(user_id, "6 Months"), callback_data="game_plan|6 Months"),
            InlineKeyboardButton(localize_value(user_id, "12 Months"), callback_data="game_plan|12 Months"),
        ],
        [
            InlineKeyboardButton(localize_value(user_id, "Lifetime"), callback_data="game_plan|Lifetime"),
            InlineKeyboardButton(localize_value(user_id, "Standard"), callback_data="game_plan|Standard"),
        ],
        [InlineKeyboardButton(localize_value(user_id, "Other"), callback_data="game_plan|Other")],
        [InlineKeyboardButton(t(user_id, "back"), callback_data="request_game")],
    ])


def game_payment_keyboard(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("USDT", callback_data="game_payment|USDT"),
            InlineKeyboardButton("CliQ / Bank", callback_data="game_payment|CliQ / Bank"),
        ],
        [InlineKeyboardButton(localize_value(user_id, "Other"), callback_data="game_payment|Other")],
        [InlineKeyboardButton(t(user_id, "back"), callback_data="request_game")],
    ])


def game_notes_keyboard(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "skip_notes"), callback_data="game_notes_skip")],
        [InlineKeyboardButton(t(user_id, "back"), callback_data="request_game")],
    ])


def game_request_summary_keyboard(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "submit_game_request"), callback_data="submit_game_request")],
        [InlineKeyboardButton(t(user_id, "edit"), callback_data="request_game")],
        [InlineKeyboardButton(t(user_id, "main_menu"), callback_data="main_menu")],
    ])


def game_admin_request_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(TEXTS["en"]["send_price_btn"], callback_data=f"game_admin_price|{request_id}"),
            InlineKeyboardButton(TEXTS["en"]["not_available_btn"], callback_data=f"game_admin_unavailable|{request_id}"),
        ]
    ])


def game_user_price_keyboard(user_id, request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t(user_id, "accept_price"), callback_data=f"game_accept_price|{request_id}"),
            InlineKeyboardButton(t(user_id, "cancel"), callback_data=f"game_cancel_price|{request_id}"),
        ]
    ])


def game_user_payment_choice_keyboard(user_id, request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("USDT", callback_data=f"game_pay|{request_id}|USDT")],
        [InlineKeyboardButton("CliQ / Bank", callback_data=f"game_pay|{request_id}|CliQ / Bank")],
        [InlineKeyboardButton(t(user_id, "main_menu"), callback_data="main_menu")],
    ])


def game_admin_paid_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS["en"]["deliver_game_btn"], callback_data=f"game_admin_deliver|{request_id}")]
    ])


def subscription_admin_paid_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS["en"]["deliver_subscription_btn"], callback_data=f"sub_admin_deliver|{order_id}")]
    ])


# -------------------------
# Helpers
# -------------------------
def reset_user_flow(context: ContextTypes.DEFAULT_TYPE):
    keys = [
        "product_id",
        "product_name",
        "plan_name",
        "plan_price",
        "payment_method",
        "order_id",
        "awaiting_game_request",
        "awaiting_payment_screenshot",
        "awaiting_game_payment_screenshot",
        "game_checkout_request_id",
        "game_step",
        "game_name",
        "game_platform",
        "game_type",
        "game_plan",
        "game_payment",
        "game_notes",
        "admin_waiting_price_for_request",
        "admin_waiting_subscription_delivery_for_order",
        "admin_waiting_game_delivery_for_request",
    ]
    for key in keys:
        context.user_data.pop(key, None)


def get_user_name(user) -> str:
    if user.full_name:
        return user.full_name
    if user.first_name:
        return user.first_name
    return "Unknown"


def get_username(user) -> str:
    return f"@{user.username}" if user.username else "No username"


def get_contact_text(user_id: int, username: str) -> str:
    if username:
        return f"@{username}"
    return f"<a href=\"tg://user?id={user_id}\">Open Customer Chat</a>"


def find_product_by_id(product_id: str):
    for product in PRODUCTS["subscriptions"]:
        if product["id"] == product_id:
            return product
    return None


def build_game_request_summary(user_id, context: ContextTypes.DEFAULT_TYPE) -> str:
    return (
        f"{t(user_id, 'game_summary_title')}\n\n"
        f"{t(user_id, 'game_name')}: {context.user_data.get('game_name', '-')}\n"
        f"{t(user_id, 'platform')}: {localize_value(user_id, context.user_data.get('game_platform', '-'))}\n"
        f"{t(user_id, 'type')}: {localize_value(user_id, context.user_data.get('game_type', '-'))}\n"
        f"{t(user_id, 'plan')}: {localize_value(user_id, context.user_data.get('game_plan', '-'))}\n"
        f"{t(user_id, 'preferred_payment')}: {localize_value(user_id, context.user_data.get('game_payment', '-'))}\n"
        f"{t(user_id, 'notes')}: {context.user_data.get('game_notes', '-')}\n\n"
        f"{t(user_id, 'press_submit')}"
    )


# -------------------------
# Group Messages
# -------------------------
async def send_order_summary_to_orders_group(
    context: ContextTypes.DEFAULT_TYPE,
    user,
    order_id: int,
    product_name: str,
    plan_name: str,
    plan_price,
    payment_method: str,
):
    text = (
        f"🛒 <b>New Confirmed Order</b>\n\n"
        f"<b>{TEXTS['en']['order_id']}:</b> #{order_id}\n"
        f"<b>{TEXTS['en']['customer_name']}:</b> {get_user_name(user)}\n"
        f"<b>{TEXTS['en']['username']}:</b> {get_username(user)}\n"
        f"<b>{TEXTS['en']['quick_contact']}:</b> {get_contact_text(user.id, user.username or '')}\n"
        f"<b>{TEXTS['en']['user_id']}:</b> <code>{user.id}</code>\n"
        f"<b>{TEXTS['en']['product']}:</b> {product_name}\n"
        f"<b>{TEXTS['en']['plan']}:</b> {plan_name}\n"
        f"<b>{TEXTS['en']['price']}:</b> ${plan_price}\n"
        f"<b>{TEXTS['en']['payment_method']}:</b> {payment_method}\n"
        f"<b>{TEXTS['en']['status']}:</b> {TEXTS['en']['waiting_payment_screenshot']}"
    )

    try:
        await context.bot.send_message(
            chat_id=config.ORDERS_GROUP_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        return True
    except Exception as e:
        print("ORDER GROUP SEND ERROR:", e)
        return False


async def forward_payment_screenshot_to_orders_group(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    order_id: int,
    product_name: str,
    plan_name: str,
    plan_price,
    payment_method: str,
):
    user = update.effective_user
    message = update.message

    try:
        await context.bot.forward_message(
            chat_id=config.ORDERS_GROUP_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )

        text = (
            f"💳 <b>Payment Screenshot Received</b>\n\n"
            f"<b>{TEXTS['en']['order_id']}:</b> #{order_id}\n"
            f"<b>{TEXTS['en']['customer_name']}:</b> {get_user_name(user)}\n"
            f"<b>{TEXTS['en']['username']}:</b> {get_username(user)}\n"
            f"<b>{TEXTS['en']['quick_contact']}:</b> {get_contact_text(user.id, user.username or '')}\n"
            f"<b>{TEXTS['en']['user_id']}:</b> <code>{user.id}</code>\n"
            f"<b>{TEXTS['en']['product']}:</b> {product_name}\n"
            f"<b>{TEXTS['en']['plan']}:</b> {plan_name}\n"
            f"<b>{TEXTS['en']['price']}:</b> ${plan_price}\n"
            f"<b>{TEXTS['en']['payment_method']}:</b> {payment_method}\n"
            f"<b>{TEXTS['en']['status']}:</b> {TEXTS['en']['paid_awaiting_delivery']}"
        )

        await context.bot.send_message(
            chat_id=config.ORDERS_GROUP_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=subscription_admin_paid_keyboard(order_id),
        )
        return True

    except Exception as e:
        print("PAYMENT SCREENSHOT FORWARD ERROR:", e)
        return False


async def send_game_request_to_orders_group(
    context: ContextTypes.DEFAULT_TYPE,
    request_id: int,
    user_id: int,
    username: str,
    customer_name: str,
):
    request = get_game_request(request_id)
    if not request:
        return False

    (
        _id,
        _user_id,
        _username,
        _customer_name,
        game_name,
        platform,
        request_type,
        plan,
        preferred_payment,
        notes,
        offered_price,
        final_payment_method,
        status,
        delivery_text,
    ) = request

    text = (
        f"🎮 <b>New Game Request</b>\n\n"
        f"<b>{TEXTS['en']['request_id']}:</b> #G{request_id}\n"
        f"<b>{TEXTS['en']['customer_name']}:</b> {customer_name}\n"
        f"<b>{TEXTS['en']['username']}:</b> {('@' + username) if username else 'No username'}\n"
        f"<b>{TEXTS['en']['quick_contact']}:</b> {get_contact_text(user_id, username or '')}\n"
        f"<b>{TEXTS['en']['user_id']}:</b> <code>{user_id}</code>\n\n"
        f"<b>{TEXTS['en']['game_name']}:</b> {game_name}\n"
        f"<b>{TEXTS['en']['platform']}:</b> {platform}\n"
        f"<b>{TEXTS['en']['type']}:</b> {request_type}\n"
        f"<b>{TEXTS['en']['plan']}:</b> {plan}\n"
        f"<b>{TEXTS['en']['preferred_payment']}:</b> {preferred_payment}\n"
        f"<b>{TEXTS['en']['notes']}:</b> {notes}\n\n"
        f"<b>{TEXTS['en']['status']}:</b> {TEXTS['en']['waiting_manual_pricing']}"
    )

    try:
        await context.bot.send_message(
            chat_id=config.ORDERS_GROUP_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=game_admin_request_keyboard(request_id),
        )
        return True
    except Exception as e:
        print("GAME REQUEST SEND ERROR:", e)
        return False


# -------------------------
# Commands
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)

    if not lang:
        await update.message.reply_text(
            TEXTS["en"]["choose_language"],
            reply_markup=language_keyboard(),
        )
        return

    reset_user_flow(context)
    await update.message.reply_text(
        t(user.id, "welcome"),
        reply_markup=main_menu_keyboard(user.id),
    )


# -------------------------
# Button Handler
# -------------------------
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if query.data.startswith("set_lang|"):
        lang = query.data.split("|", 1)[1]
        set_user_language(user.id, user.username or "", lang)
        reset_user_flow(context)
        await query.edit_message_text(TEXTS[lang]["language_saved"])
        await context.bot.send_message(
            chat_id=user.id,
            text=TEXTS[lang]["welcome"],
            reply_markup=main_menu_keyboard(user.id),
        )
        return

    if query.data == "change_language":
        await query.edit_message_text(
            t(user.id, "choose_language"),
            reply_markup=language_keyboard(),
        )
        return

    if query.data == "main_menu":
        reset_user_flow(context)
        await query.edit_message_text(
            t(user.id, "welcome"),
            reply_markup=main_menu_keyboard(user.id),
        )
        return

    if query.data == "subscriptions":
        reset_user_flow(context)
        keyboard = []

        for product in PRODUCTS["subscriptions"]:
            keyboard.append([
                InlineKeyboardButton(product["name"], callback_data=f"product_{product['id']}")
            ])

        keyboard.append([InlineKeyboardButton(t(user.id, "back"), callback_data="main_menu")])

        await query.edit_message_text(
            t(user.id, "choose_subscription"),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if query.data.startswith("product_"):
        product_id = query.data.split("_", 1)[1]
        product = find_product_by_id(product_id)

        if not product:
            await query.edit_message_text(
                t(user.id, "product_not_found"),
                reply_markup=back_to_main_keyboard(user.id),
            )
            return

        keyboard = []
        for idx, plan in enumerate(product["plans"]):
            keyboard.append([
                InlineKeyboardButton(
                    f"{plan['name']} - ${plan['price']}",
                    callback_data=f"select_plan|{product_id}|{idx}"
                )
            ])

        keyboard.append([InlineKeyboardButton(t(user.id, "back"), callback_data="subscriptions")])

        await query.edit_message_text(
            f"{product['name']} Plans:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if query.data.startswith("select_plan|"):
        _, product_id, plan_index = query.data.split("|")
        product = find_product_by_id(product_id)

        if not product:
            await query.edit_message_text(
                t(user.id, "product_not_found"),
                reply_markup=back_to_main_keyboard(user.id),
            )
            return

        plan_index = int(plan_index)
        selected_plan = product["plans"][plan_index]

        context.user_data["product_id"] = product["id"]
        context.user_data["product_name"] = product["name"]
        context.user_data["plan_name"] = selected_plan["name"]
        context.user_data["plan_price"] = selected_plan["price"]

        await query.edit_message_text(
            f"{t(user.id, 'product')}: {product['name']}\n"
            f"{t(user.id, 'plan')}: {selected_plan['name']}\n"
            f"{t(user.id, 'price')}: ${selected_plan['price']}\n\n"
            f"{t(user.id, 'choose_payment')}",
            reply_markup=payment_keyboard(user.id),
        )
        return

    if query.data == "pay_usdt":
        context.user_data["payment_method"] = f"USDT - {config.USDT_NETWORK}"

        product_name = context.user_data.get("product_name")
        plan_name = context.user_data.get("plan_name")
        plan_price = context.user_data.get("plan_price")

        await query.edit_message_text(
            f"{t(user.id, 'usdt_payment_title')}\n\n"
            f"{t(user.id, 'product')}: {product_name}\n"
            f"{t(user.id, 'plan')}: {plan_name}\n"
            f"{t(user.id, 'price')}: ${plan_price}\n\n"
            f"Network: {config.USDT_NETWORK}\n"
            f"Wallet Address:\n{config.USDT_WALLET}\n\n"
            f"⚠️ Send only on {config.USDT_NETWORK}\n\n"
            f"{t(user.id, 'after_payment_confirm')}",
            reply_markup=confirm_order_keyboard(user.id),
        )
        return

    if query.data == "pay_bank":
        context.user_data["payment_method"] = "CliQ / Bank"

        product_name = context.user_data.get("product_name")
        plan_name = context.user_data.get("plan_name")
        plan_price = context.user_data.get("plan_price")

        await query.edit_message_text(
            f"{t(user.id, 'bank_payment_title')}\n\n"
            f"{t(user.id, 'product')}: {product_name}\n"
            f"{t(user.id, 'plan')}: {plan_name}\n"
            f"{t(user.id, 'price')}: ${plan_price}\n\n"
            f"{t(user.id, 'receiver_name')}:\n{config.CLIQ_NAME}\n\n"
            f"{t(user.id, 'after_payment_confirm')}",
            reply_markup=confirm_order_keyboard(user.id),
        )
        return

    if query.data == "change_payment":
        product_name = context.user_data.get("product_name")
        plan_name = context.user_data.get("plan_name")
        plan_price = context.user_data.get("plan_price")

        if not product_name or not plan_name:
            await query.edit_message_text(
                t(user.id, "session_expired"),
                reply_markup=back_to_main_keyboard(user.id),
            )
            return

        await query.edit_message_text(
            f"{t(user.id, 'product')}: {product_name}\n"
            f"{t(user.id, 'plan')}: {plan_name}\n"
            f"{t(user.id, 'price')}: ${plan_price}\n\n"
            f"{t(user.id, 'choose_payment')}",
            reply_markup=payment_keyboard(user.id),
        )
        return

    if query.data == "confirm_purchase":
        product_name = context.user_data.get("product_name")
        plan_name = context.user_data.get("plan_name")
        plan_price = context.user_data.get("plan_price")
        payment_method = context.user_data.get("payment_method")

        if not product_name or not plan_name or not payment_method:
            await query.edit_message_text(
                t(user.id, "missing_order_data"),
                reply_markup=back_to_main_keyboard(user.id),
            )
            return

        order_id = create_order(
            user_id=user.id,
            username=user.username if user.username else "",
            product=product_name,
            plan=plan_name,
            payment=payment_method,
        )

        update_order_status(order_id, "waiting_for_payment_screenshot")

        context.user_data["order_id"] = order_id
        context.user_data["awaiting_payment_screenshot"] = True

        sent = await send_order_summary_to_orders_group(
            context=context,
            user=user,
            order_id=order_id,
            product_name=product_name,
            plan_name=plan_name,
            plan_price=plan_price,
            payment_method=payment_method,
        )

        if not sent:
            await query.edit_message_text(
                t(user.id, "order_send_error"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t(user.id, "main_menu"), callback_data="main_menu")]
                ]),
            )
            return

        await query.edit_message_text(
            f"{t(user.id, 'purchase_confirmed')}\n\n"
            f"{t(user.id, 'order_id')}: #{order_id}\n"
            f"{t(user.id, 'product')}: {product_name}\n"
            f"{t(user.id, 'plan')}: {plan_name}\n"
            f"{t(user.id, 'price')}: ${plan_price}\n"
            f"{t(user.id, 'payment_method')}: {payment_method}\n\n"
            f"{t(user.id, 'send_payment_screenshot')}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t(user.id, "main_menu"), callback_data="main_menu")]
            ]),
        )
        return

    if query.data == "payments":
        await query.edit_message_text(
            t(user.id, "payments_info"),
            reply_markup=back_to_main_keyboard(user.id),
        )
        return

    if query.data == "support":
        await query.edit_message_text(
            t(user.id, "support_info"),
            reply_markup=back_to_main_keyboard(user.id),
        )
        return

    # User side - game flow
    if query.data == "request_game":
        reset_user_flow(context)
        context.user_data["awaiting_game_request"] = True
        context.user_data["game_step"] = "name"

        await query.edit_message_text(
            t(user.id, "request_game_name"),
            reply_markup=build_back_keyboard(user.id, "main_menu"),
        )
        return

    if query.data.startswith("game_platform|"):
        value = query.data.split("|", 1)[1]
        context.user_data["game_platform"] = value
        context.user_data["game_step"] = "type"

        await query.edit_message_text(
            t(user.id, "choose_request_type"),
            reply_markup=game_type_keyboard(user.id),
        )
        return

    if query.data.startswith("game_type|"):
        value = query.data.split("|", 1)[1]
        context.user_data["game_type"] = value
        context.user_data["game_step"] = "plan"

        await query.edit_message_text(
            t(user.id, "choose_plan"),
            reply_markup=game_plan_keyboard(user.id),
        )
        return

    if query.data.startswith("game_plan|"):
        value = query.data.split("|", 1)[1]
        context.user_data["game_plan"] = value
        context.user_data["game_step"] = "payment"

        await query.edit_message_text(
            t(user.id, "choose_preferred_payment"),
            reply_markup=game_payment_keyboard(user.id),
        )
        return

    if query.data.startswith("game_payment|"):
        value = query.data.split("|", 1)[1]
        context.user_data["game_payment"] = value
        context.user_data["game_step"] = "notes"

        await query.edit_message_text(
            t(user.id, "send_notes"),
            reply_markup=game_notes_keyboard(user.id),
        )
        return

    if query.data == "game_notes_skip":
        context.user_data["game_notes"] = "No"
        context.user_data["game_step"] = "done"

        await query.edit_message_text(
            build_game_request_summary(user.id, context),
            reply_markup=game_request_summary_keyboard(user.id),
        )
        return

    if query.data == "submit_game_request":
        request_id = create_game_request(
            user_id=user.id,
            username=user.username if user.username else "",
            customer_name=get_user_name(user),
            game_name=context.user_data.get("game_name", "-"),
            platform=context.user_data.get("game_platform", "-"),
            request_type=context.user_data.get("game_type", "-"),
            plan=context.user_data.get("game_plan", "-"),
            preferred_payment=context.user_data.get("game_payment", "-"),
            notes=context.user_data.get("game_notes", "-"),
        )

        sent = await send_game_request_to_orders_group(
            context=context,
            request_id=request_id,
            user_id=user.id,
            username=user.username if user.username else "",
            customer_name=get_user_name(user),
        )

        if not sent:
            await query.edit_message_text(
                t(user.id, "game_request_send_error"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t(user.id, "main_menu"), callback_data="main_menu")]
                ]),
            )
            return

        await query.edit_message_text(
            f"{t(user.id, 'game_request_sent')}\n"
            f"{t(user.id, 'request_id')}: #G{request_id}\n"
            f"{t(user.id, 'team_review_contact_price')}"
        )

        reset_user_flow(context)
        return

    if query.data.startswith("game_accept_price|"):
        request_id = int(query.data.split("|")[1])
        request = get_game_request(request_id)

        if not request:
            await query.edit_message_text(t(user.id, "game_request_not_found"))
            return

        (
            _id, user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status, delivery_text,
        ) = request

        update_game_request_status(request_id, "waiting_payment_method")

        await query.edit_message_text(
            f"{t(user.id, 'price_accepted')}\n\n"
            f"{t(user.id, 'game_name')}: {game_name}\n"
            f"{t(user.id, 'platform')}: {localize_value(user.id, platform)}\n"
            f"{t(user.id, 'price')}: ${offered_price}\n\n"
            f"{t(user.id, 'choose_payment_method')}",
            reply_markup=game_user_payment_choice_keyboard(user.id, request_id),
        )

        await context.bot.send_message(
            chat_id=config.ORDERS_GROUP_ID,
            text=f"{t(user.id, 'customer_accepted_price')} #G{request_id}.",
        )
        return

    if query.data.startswith("game_cancel_price|"):
        request_id = int(query.data.split("|")[1])
        request = get_game_request(request_id)

        if not request:
            await query.edit_message_text(t(user.id, "game_request_not_found"))
            return

        update_game_request_status(request_id, "cancelled_by_customer")

        await query.edit_message_text(t(user.id, "request_cancelled_success"))

        await context.bot.send_message(
            chat_id=config.ORDERS_GROUP_ID,
            text=f"{t(user.id, 'customer_cancelled_price')} #G{request_id}.",
        )
        return

    if query.data.startswith("game_pay|"):
        _, request_id_str, payment_method = query.data.split("|", 2)
        request_id = int(request_id_str)

        request = get_game_request(request_id)
        if not request:
            await query.edit_message_text(t(user.id, "game_request_not_found"))
            return

        (
            _id, user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status, delivery_text,
        ) = request

        set_game_request_final_payment(request_id, payment_method)

        context.user_data["awaiting_game_payment_screenshot"] = True
        context.user_data["game_checkout_request_id"] = request_id

        if payment_method == "USDT":
            await query.edit_message_text(
                f"{t(user.id, 'game_payment_usdt')}\n\n"
                f"{t(user.id, 'request_id')}: #G{request_id}\n"
                f"{t(user.id, 'game_name')}: {game_name}\n"
                f"{t(user.id, 'platform')}: {localize_value(user.id, platform)}\n"
                f"{t(user.id, 'price')}: ${offered_price}\n\n"
                f"Network: {config.USDT_NETWORK}\n"
                f"Wallet Address:\n{config.USDT_WALLET}\n\n"
                f"⚠️ Send only on {config.USDT_NETWORK}\n\n"
                f"{t(user.id, 'send_game_screenshot')}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t(user.id, "main_menu"), callback_data="main_menu")]
                ]),
            )
            return

        await query.edit_message_text(
            f"{t(user.id, 'game_payment_bank')}\n\n"
            f"{t(user.id, 'request_id')}: #G{request_id}\n"
            f"{t(user.id, 'game_name')}: {game_name}\n"
            f"{t(user.id, 'platform')}: {localize_value(user.id, platform)}\n"
            f"{t(user.id, 'price')}: ${offered_price}\n\n"
            f"{t(user.id, 'receiver_name')}:\n{config.CLIQ_NAME}\n\n"
            f"{t(user.id, 'send_game_screenshot')}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t(user.id, "main_menu"), callback_data="main_menu")]
            ]),
        )
        return

    # Admin side
    if query.data.startswith("game_admin_price|"):
        request_id = int(query.data.split("|")[1])
        context.user_data["admin_waiting_price_for_request"] = request_id
        await query.message.reply_text(
            f"{TEXTS['en']['send_price_prompt']} #G{request_id}.\n\nExample:\n20"
        )
        return

    if query.data.startswith("game_admin_unavailable|"):
        request_id = int(query.data.split("|")[1])
        request = get_game_request(request_id)

        if not request:
            await query.answer("Request not found.")
            return

        (
            _id, user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status, delivery_text,
        ) = request

        update_game_request_status(request_id, "not_available")

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"{t(user_id, 'not_available_user')}\n\n"
                    f"{t(user_id, 'request_id')}: #G{request_id}\n"
                    f"{t(user_id, 'game_name')}: {game_name}\n"
                    f"{t(user_id, 'platform')}: {localize_value(user_id, platform)}"
                ),
            )
        except Exception as e:
            print("SEND UNAVAILABLE TO USER ERROR:", e)

        await query.message.reply_text(TEXTS["en"]["marked_unavailable"])
        return

    if query.data.startswith("game_admin_deliver|"):
        request_id = int(query.data.split("|")[1])
        context.user_data["admin_waiting_game_delivery_for_request"] = request_id

        await query.message.reply_text(
            f"{TEXTS['en']['send_delivery_game_prompt']} #G{request_id}.\n\n"
            f"Example:\n"
            f"Email: test@gmail.com\n"
            f"Password: 123456\n"
            f"Code: ABCD-1234\n"
            f"Notes: Enjoy"
        )
        return

    if query.data.startswith("sub_admin_deliver|"):
        order_id = int(query.data.split("|")[1])
        context.user_data["admin_waiting_subscription_delivery_for_order"] = order_id

        await query.message.reply_text(
            f"{TEXTS['en']['send_delivery_subscription_prompt']} #{order_id}.\n\n"
            f"Example:\n"
            f"Email: test@gmail.com\n"
            f"Password: 123456\n"
            f"Profile: 2\n"
            f"Notes: Change password after login"
        )
        return


# -------------------------
# Message Handler
# -------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = update.effective_user

    if (
        message.chat_id == config.ORDERS_GROUP_ID
        and context.user_data.get("admin_waiting_price_for_request")
        and message.text
    ):
        request_id = context.user_data.get("admin_waiting_price_for_request")
        price = message.text.strip()

        request = get_game_request(request_id)
        if not request:
            await message.reply_text("Game request not found.")
            context.user_data.pop("admin_waiting_price_for_request", None)
            return

        (
            _id, user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status, delivery_text,
        ) = request

        set_game_request_price(request_id, price)

        user_text = (
            f"{t(user_id, 'available_game_message')}\n\n"
            f"{t(user_id, 'request_id')}: #G{request_id}\n"
            f"{t(user_id, 'game_name')}: {game_name}\n"
            f"{t(user_id, 'platform')}: {localize_value(user_id, platform)}\n"
            f"{t(user_id, 'type')}: {localize_value(user_id, request_type)}\n"
            f"{t(user_id, 'plan')}: {localize_value(user_id, plan)}\n"
            f"{t(user_id, 'price')}: ${price}\n\n"
            f"{t(user_id, 'confirm_continue')}"
        )

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=user_text,
                reply_markup=game_user_price_keyboard(user_id, request_id),
            )
            await message.reply_text(f"{TEXTS['en']['price_sent_to_customer']} #G{request_id}.")
        except Exception as e:
            print("SEND PRICE TO USER ERROR:", e)
            await message.reply_text(f"{TEXTS['en']['failed_send_price']} #G{request_id}.")

        context.user_data.pop("admin_waiting_price_for_request", None)
        return

    if (
        message.chat_id == config.ORDERS_GROUP_ID
        and context.user_data.get("admin_waiting_subscription_delivery_for_order")
        and message.text
    ):
        order_id = context.user_data.get("admin_waiting_subscription_delivery_for_order")
        delivery_text = message.text.strip()

        order = get_order(order_id)
        if not order:
            await message.reply_text("Order not found.")
            context.user_data.pop("admin_waiting_subscription_delivery_for_order", None)
            return

        (
            _id, user_id, username, product, plan, payment_method, status, current_delivery_text
        ) = order

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"{t(user_id, 'delivered_subscription')}\n\n"
                    f"{t(user_id, 'order_id')}: #{order_id}\n"
                    f"{t(user_id, 'product')}: {product}\n"
                    f"{t(user_id, 'plan')}: {plan}\n\n"
                    f"{delivery_text}\n\n"
                    f"{t(user_id, 'thank_you')}"
                ),
            )
            set_order_delivery(order_id, delivery_text)
            await message.reply_text(TEXTS["en"]["delivered_success_subscription"])
        except Exception as e:
            print("DELIVER SUBSCRIPTION ERROR:", e)
            await message.reply_text(TEXTS["en"]["failed_deliver_subscription"])

        context.user_data.pop("admin_waiting_subscription_delivery_for_order", None)
        return

    if (
        message.chat_id == config.ORDERS_GROUP_ID
        and context.user_data.get("admin_waiting_game_delivery_for_request")
        and message.text
    ):
        request_id = context.user_data.get("admin_waiting_game_delivery_for_request")
        delivery_text = message.text.strip()

        request = get_game_request(request_id)
        if not request:
            await message.reply_text("Game request not found.")
            context.user_data.pop("admin_waiting_game_delivery_for_request", None)
            return

        (
            _id, user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status, current_delivery_text,
        ) = request

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"{t(user_id, 'delivered_game')}\n\n"
                    f"{t(user_id, 'request_id')}: #G{request_id}\n"
                    f"{t(user_id, 'game_name')}: {game_name}\n"
                    f"{t(user_id, 'platform')}: {localize_value(user_id, platform)}\n"
                    f"{t(user_id, 'plan')}: {localize_value(user_id, plan)}\n\n"
                    f"{delivery_text}\n\n"
                    f"{t(user_id, 'thank_you')}"
                ),
            )
            set_game_request_delivery(request_id, delivery_text)
            await message.reply_text(TEXTS["en"]["delivered_success_game"])
        except Exception as e:
            print("DELIVER GAME ERROR:", e)
            await message.reply_text(TEXTS["en"]["failed_deliver_game"])

        context.user_data.pop("admin_waiting_game_delivery_for_request", None)
        return

    if context.user_data.get("awaiting_game_request") and message.text:
        text = message.text.strip()
        step = context.user_data.get("game_step")

        if step == "name":
            context.user_data["game_name"] = text
            context.user_data["game_step"] = "platform"

            await message.reply_text(
                t(user.id, "choose_platform"),
                reply_markup=game_platform_keyboard(user.id),
            )
            return

        if step == "notes":
            context.user_data["game_notes"] = text
            context.user_data["game_step"] = "done"

            await message.reply_text(
                build_game_request_summary(user.id, context),
                reply_markup=game_request_summary_keyboard(user.id),
            )
            return

    if message.photo and context.user_data.get("awaiting_payment_screenshot"):
        order_id = context.user_data.get("order_id")

        if not order_id:
            await message.reply_text(t(user.id, "confirm_first"))
            return

        product_name = context.user_data.get("product_name")
        plan_name = context.user_data.get("plan_name")
        plan_price = context.user_data.get("plan_price")
        payment_method = context.user_data.get("payment_method")

        sent = await forward_payment_screenshot_to_orders_group(
            update=update,
            context=context,
            order_id=order_id,
            product_name=product_name,
            plan_name=plan_name,
            plan_price=plan_price,
            payment_method=payment_method,
        )

        if not sent:
            await message.reply_text(t(user.id, "payment_screenshot_error"))
            return

        update_order_status(order_id, "paid_waiting_delivery")

        await message.reply_text(
            f"{t(user.id, 'payment_screenshot_received')}\n"
            f"{t(user.id, 'order_id')}: #{order_id}\n"
            f"{t(user.id, 'team_review_deliver')}"
        )

        reset_user_flow(context)
        return

    if message.photo and context.user_data.get("awaiting_game_payment_screenshot"):
        request_id = context.user_data.get("game_checkout_request_id")
        request = get_game_request(request_id) if request_id else None

        if not request:
            await message.reply_text(t(user.id, "game_request_not_found"))
            return

        (
            _id, user_id, username, customer_name, game_name, platform,
            request_type, plan, preferred_payment, notes,
            offered_price, final_payment_method, status, delivery_text,
        ) = request

        try:
            await context.bot.forward_message(
                chat_id=config.ORDERS_GROUP_ID,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
            )

            group_text = (
                f"💳 <b>Game Payment Screenshot Received</b>\n\n"
                f"<b>{TEXTS['en']['request_id']}:</b> #G{request_id}\n"
                f"<b>{TEXTS['en']['customer_name']}:</b> {customer_name}\n"
                f"<b>{TEXTS['en']['username']}:</b> {('@' + username) if username else 'No username'}\n"
                f"<b>{TEXTS['en']['quick_contact']}:</b> {get_contact_text(user_id, username or '')}\n"
                f"<b>{TEXTS['en']['user_id']}:</b> <code>{user_id}</code>\n\n"
                f"<b>{TEXTS['en']['game_name']}:</b> {game_name}\n"
                f"<b>{TEXTS['en']['platform']}:</b> {platform}\n"
                f"<b>{TEXTS['en']['type']}:</b> {request_type}\n"
                f"<b>{TEXTS['en']['plan']}:</b> {plan}\n"
                f"<b>{TEXTS['en']['price']}:</b> ${offered_price}\n"
                f"<b>{TEXTS['en']['payment_method']}:</b> {final_payment_method}\n"
                f"<b>{TEXTS['en']['status']}:</b> {TEXTS['en']['paid_awaiting_delivery']}"
            )

            await context.bot.send_message(
                chat_id=config.ORDERS_GROUP_ID,
                text=group_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=game_admin_paid_keyboard(request_id),
            )

        except Exception as e:
            print("GAME PAYMENT SCREENSHOT SEND ERROR:", e)
            await message.reply_text(t(user.id, "game_payment_screenshot_error"))
            return

        update_game_request_status(request_id, "paid_waiting_delivery")

        await message.reply_text(
            f"{t(user.id, 'game_payment_screenshot_received')}\n"
            f"{t(user.id, 'request_id')}: #G{request_id}\n"
            f"{t(user.id, 'team_review_deliver_game')}"
        )

        reset_user_flow(context)
        return

    if message.text:
        await message.reply_text(t(user.id, "please_start_menu"))


def main():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
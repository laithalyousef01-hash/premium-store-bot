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
    create_game_request,
    get_game_request,
    update_game_request_status,
    set_game_request_price,
    set_game_request_final_payment,
)


with open("products.json", "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


# -------------------------
# Helpers
# -------------------------
def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🛒 Subscriptions", callback_data="subscriptions")],
        [InlineKeyboardButton("🎮 Request Game", callback_data="request_game")],
        [InlineKeyboardButton("💳 Payment Methods", callback_data="payments")],
        [InlineKeyboardButton("🛠 Support", callback_data="support")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back", callback_data="main_menu")]
    ])


def build_back_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back", callback_data=callback_data)]
    ])


def payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("USDT", callback_data="pay_usdt")],
        [InlineKeyboardButton("CliQ / Bank", callback_data="pay_bank")],
        [InlineKeyboardButton("⬅ Back", callback_data="subscriptions")],
    ])


def confirm_order_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm Purchase", callback_data="confirm_purchase")],
        [InlineKeyboardButton("⬅ Back", callback_data="change_payment")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])


def game_platform_keyboard() -> InlineKeyboardMarkup:
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
            InlineKeyboardButton("Other", callback_data="game_platform|Other"),
        ],
        [InlineKeyboardButton("⬅ Back", callback_data="main_menu")],
    ])


def game_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Subscription", callback_data="game_type|Subscription"),
            InlineKeyboardButton("Top-up", callback_data="game_type|Top-up"),
        ],
        [
            InlineKeyboardButton("Code", callback_data="game_type|Code"),
            InlineKeyboardButton("Account", callback_data="game_type|Account"),
        ],
        [InlineKeyboardButton("⬅ Back", callback_data="request_game")],
    ])


def game_plan_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1 Month", callback_data="game_plan|1 Month"),
            InlineKeyboardButton("3 Months", callback_data="game_plan|3 Months"),
        ],
        [
            InlineKeyboardButton("6 Months", callback_data="game_plan|6 Months"),
            InlineKeyboardButton("12 Months", callback_data="game_plan|12 Months"),
        ],
        [
            InlineKeyboardButton("Lifetime", callback_data="game_plan|Lifetime"),
            InlineKeyboardButton("Standard", callback_data="game_plan|Standard"),
        ],
        [InlineKeyboardButton("Other", callback_data="game_plan|Other")],
        [InlineKeyboardButton("⬅ Back", callback_data="request_game")],
    ])


def game_payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("USDT", callback_data="game_payment|USDT"),
            InlineKeyboardButton("CliQ / Bank", callback_data="game_payment|CliQ / Bank"),
        ],
        [InlineKeyboardButton("Other", callback_data="game_payment|Other")],
        [InlineKeyboardButton("⬅ Back", callback_data="request_game")],
    ])


def game_notes_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Skip Notes", callback_data="game_notes_skip")],
        [InlineKeyboardButton("⬅ Back", callback_data="request_game")],
    ])


def game_request_summary_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Submit Game Request", callback_data="submit_game_request")],
        [InlineKeyboardButton("✏ Edit", callback_data="request_game")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])


def game_admin_request_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💵 Send Price", callback_data=f"game_admin_price|{request_id}"),
            InlineKeyboardButton("❌ Not Available", callback_data=f"game_admin_unavailable|{request_id}"),
        ]
    ])


def game_user_price_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Accept Price", callback_data=f"game_accept_price|{request_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"game_cancel_price|{request_id}"),
        ]
    ])


def game_user_payment_choice_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("USDT", callback_data=f"game_pay|{request_id}|USDT")],
        [InlineKeyboardButton("CliQ / Bank", callback_data=f"game_pay|{request_id}|CliQ / Bank")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])


def game_admin_paid_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Mark Delivered", callback_data=f"game_admin_delivered|{request_id}")]
    ])


def reset_user_flow(context: ContextTypes.DEFAULT_TYPE):
    keys = [
        "flow",
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


def build_game_request_summary(context: ContextTypes.DEFAULT_TYPE) -> str:
    return (
        f"🎮 Game Request Summary\n\n"
        f"Game Name: {context.user_data.get('game_name', '-')}\n"
        f"Platform: {context.user_data.get('game_platform', '-')}\n"
        f"Type: {context.user_data.get('game_type', '-')}\n"
        f"Plan: {context.user_data.get('game_plan', '-')}\n"
        f"Preferred Payment: {context.user_data.get('game_payment', '-')}\n"
        f"Notes: {context.user_data.get('game_notes', '-')}\n\n"
        f"Press Submit to send your request."
    )


# -------------------------
# Orders Group Senders
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
        f"<b>Order ID:</b> #{order_id}\n"
        f"<b>Customer Name:</b> {get_user_name(user)}\n"
        f"<b>Username:</b> {get_username(user)}\n"
        f"<b>Quick Contact:</b> {get_contact_text(user.id, user.username or '')}\n"
        f"<b>User ID:</b> <code>{user.id}</code>\n"
        f"<b>Product:</b> {product_name}\n"
        f"<b>Plan:</b> {plan_name}\n"
        f"<b>Price:</b> ${plan_price}\n"
        f"<b>Payment Method:</b> {payment_method}\n"
        f"<b>Status:</b> Waiting for payment screenshot"
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
            f"<b>Order ID:</b> #{order_id}\n"
            f"<b>Customer Name:</b> {get_user_name(user)}\n"
            f"<b>Username:</b> {get_username(user)}\n"
            f"<b>Quick Contact:</b> {get_contact_text(user.id, user.username or '')}\n"
            f"<b>User ID:</b> <code>{user.id}</code>\n"
            f"<b>Product:</b> {product_name}\n"
            f"<b>Plan:</b> {plan_name}\n"
            f"<b>Price:</b> ${plan_price}\n"
            f"<b>Payment Method:</b> {payment_method}\n"
            f"<b>Status:</b> Paid - Awaiting delivery"
        )

        await context.bot.send_message(
            chat_id=config.ORDERS_GROUP_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
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
    ) = request

    text = (
        f"🎮 <b>New Game Request</b>\n\n"
        f"<b>Request ID:</b> #G{request_id}\n"
        f"<b>Customer Name:</b> {customer_name}\n"
        f"<b>Username:</b> {('@' + username) if username else 'No username'}\n"
        f"<b>Quick Contact:</b> {get_contact_text(user_id, username or '')}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n\n"
        f"<b>Game Name:</b> {game_name}\n"
        f"<b>Platform:</b> {platform}\n"
        f"<b>Type:</b> {request_type}\n"
        f"<b>Plan:</b> {plan}\n"
        f"<b>Preferred Payment:</b> {preferred_payment}\n"
        f"<b>Notes:</b> {notes}\n\n"
        f"<b>Status:</b> Waiting for manual pricing"
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
    reset_user_flow(context)
    await update.message.reply_text(
        f"Welcome to {config.STORE_NAME}\nChoose an option:",
        reply_markup=main_menu_keyboard(),
    )


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.chat_id != config.ORDERS_GROUP_ID:
        await message.reply_text("This command can only be used in the orders group.")
        return

    if len(context.args) < 2:
        await message.reply_text("Usage: /price <request_id> <amount>\nExample: /price 5 20")
        return

    try:
        request_id = int(context.args[0])
        price = " ".join(context.args[1:]).strip()
    except Exception:
        await message.reply_text("Invalid request ID.")
        return

    request = get_game_request(request_id)
    if not request:
        await message.reply_text("Game request not found.")
        return

    (
        _id,
        user_id,
        username,
        customer_name,
        game_name,
        platform,
        request_type,
        plan,
        preferred_payment,
        notes,
        offered_price,
        final_payment_method,
        status,
    ) = request

    set_game_request_price(request_id, price)

    user_text = (
        f"🎮 Your requested game is available ✅\n\n"
        f"Game: {game_name}\n"
        f"Platform: {platform}\n"
        f"Type: {request_type}\n"
        f"Plan: {plan}\n"
        f"Price: ${price}\n\n"
        f"Please confirm to continue."
    )

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=user_text,
            reply_markup=game_user_price_keyboard(request_id),
        )
        await message.reply_text(f"Price ${price} sent to customer for request #G{request_id}.")
    except Exception as e:
        print("SEND PRICE TO USER ERROR:", e)
        await message.reply_text(
            f"Failed to send price to the customer for request #G{request_id}. "
            f"The user may not have an active chat with the bot."
        )


# -------------------------
# Button Handler
# -------------------------
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        reset_user_flow(context)
        await query.edit_message_text(
            f"Welcome to {config.STORE_NAME}\nChoose an option:",
            reply_markup=main_menu_keyboard(),
        )
        return

    if query.data == "subscriptions":
        reset_user_flow(context)
        keyboard = []

        for product in PRODUCTS["subscriptions"]:
            keyboard.append([
                InlineKeyboardButton(
                    product["name"],
                    callback_data=f"product_{product['id']}"
                )
            ])

        keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="main_menu")])

        await query.edit_message_text(
            "Choose a subscription:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if query.data.startswith("product_"):
        product_id = query.data.split("_", 1)[1]
        product = find_product_by_id(product_id)

        if not product:
            await query.edit_message_text(
                "Product not found.",
                reply_markup=back_to_main_keyboard(),
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

        keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="subscriptions")])

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
                "Product not found.",
                reply_markup=back_to_main_keyboard(),
            )
            return

        plan_index = int(plan_index)
        selected_plan = product["plans"][plan_index]

        context.user_data["product_id"] = product["id"]
        context.user_data["product_name"] = product["name"]
        context.user_data["plan_name"] = selected_plan["name"]
        context.user_data["plan_price"] = selected_plan["price"]

        await query.edit_message_text(
            f"Product: {product['name']}\n"
            f"Plan: {selected_plan['name']}\n"
            f"Price: ${selected_plan['price']}\n\n"
            f"Choose payment method:",
            reply_markup=payment_keyboard(),
        )
        return

    if query.data == "pay_usdt":
        context.user_data["payment_method"] = f"USDT - {config.USDT_NETWORK}"

        product_name = context.user_data.get("product_name")
        plan_name = context.user_data.get("plan_name")
        plan_price = context.user_data.get("plan_price")

        await query.edit_message_text(
            f"💰 USDT Payment\n\n"
            f"Product: {product_name}\n"
            f"Plan: {plan_name}\n"
            f"Price: ${plan_price}\n\n"
            f"Network: {config.USDT_NETWORK}\n"
            f"Wallet Address:\n{config.USDT_WALLET}\n\n"
            f"⚠️ Send only on {config.USDT_NETWORK}\n\n"
            f"After sending the payment, press Confirm Purchase.",
            reply_markup=confirm_order_keyboard(),
        )
        return

    if query.data == "pay_bank":
        context.user_data["payment_method"] = "CliQ / Bank"

        product_name = context.user_data.get("product_name")
        plan_name = context.user_data.get("plan_name")
        plan_price = context.user_data.get("plan_price")

        await query.edit_message_text(
            f"🏦 CliQ / Bank Transfer\n\n"
            f"Product: {product_name}\n"
            f"Plan: {plan_name}\n"
            f"Price: ${plan_price}\n\n"
            f"Receiver Name:\n{config.CLIQ_NAME}\n\n"
            f"After sending the payment, press Confirm Purchase.",
            reply_markup=confirm_order_keyboard(),
        )
        return

    if query.data == "change_payment":
        product_name = context.user_data.get("product_name")
        plan_name = context.user_data.get("plan_name")
        plan_price = context.user_data.get("plan_price")

        if not product_name or not plan_name:
            await query.edit_message_text(
                "Session expired. Please start again.",
                reply_markup=back_to_main_keyboard(),
            )
            return

        await query.edit_message_text(
            f"Product: {product_name}\n"
            f"Plan: {plan_name}\n"
            f"Price: ${plan_price}\n\n"
            f"Choose payment method:",
            reply_markup=payment_keyboard(),
        )
        return

    if query.data == "confirm_purchase":
        user = query.from_user

        product_name = context.user_data.get("product_name")
        plan_name = context.user_data.get("plan_name")
        plan_price = context.user_data.get("plan_price")
        payment_method = context.user_data.get("payment_method")

        if not product_name or not plan_name or not payment_method:
            await query.edit_message_text(
                "Missing order data. Please start again.",
                reply_markup=back_to_main_keyboard(),
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
                "There is a problem sending the order to support. Please try again later.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ]),
            )
            return

        await query.edit_message_text(
            f"✅ Purchase confirmed successfully\n\n"
            f"Order ID: #{order_id}\n"
            f"Product: {product_name}\n"
            f"Plan: {plan_name}\n"
            f"Price: ${plan_price}\n"
            f"Payment Method: {payment_method}\n\n"
            f"Now send the payment screenshot here.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]),
        )
        return

    if query.data == "payments":
        await query.edit_message_text(
            f"💳 Payment Methods\n\n"
            f"1) CliQ / Bank Transfer\n"
            f"Receiver Name: {config.CLIQ_NAME}\n\n"
            f"2) USDT Wallet\n"
            f"Network: {config.USDT_NETWORK}\n"
            f"Address:\n{config.USDT_WALLET}\n\n"
            f"⚠️ Please send only on {config.USDT_NETWORK}",
            reply_markup=back_to_main_keyboard(),
        )
        return

    if query.data == "support":
        await query.edit_message_text(
            f"🛠 Support\n\n"
            f"For help, contact:\n{config.SUPPORT_USERNAME}",
            reply_markup=back_to_main_keyboard(),
        )
        return

    # -------------------------
    # Game Request: User Side
    # -------------------------
    if query.data == "request_game":
        reset_user_flow(context)
        context.user_data["awaiting_game_request"] = True
        context.user_data["game_step"] = "name"

        await query.edit_message_text(
            "🎮 Enter the game name.\n\nExample:\nEA FC 25",
            reply_markup=build_back_keyboard("main_menu"),
        )
        return

    if query.data.startswith("game_platform|"):
        value = query.data.split("|", 1)[1]
        context.user_data["game_platform"] = value
        context.user_data["game_step"] = "type"

        await query.edit_message_text(
            "📦 Choose the request type:",
            reply_markup=game_type_keyboard(),
        )
        return

    if query.data.startswith("game_type|"):
        value = query.data.split("|", 1)[1]
        context.user_data["game_type"] = value
        context.user_data["game_step"] = "plan"

        await query.edit_message_text(
            "📅 Choose the plan or duration:",
            reply_markup=game_plan_keyboard(),
        )
        return

    if query.data.startswith("game_plan|"):
        value = query.data.split("|", 1)[1]
        context.user_data["game_plan"] = value
        context.user_data["game_step"] = "payment"

        await query.edit_message_text(
            "💳 Choose the preferred payment method:",
            reply_markup=game_payment_keyboard(),
        )
        return

    if query.data.startswith("game_payment|"):
        value = query.data.split("|", 1)[1]
        context.user_data["game_payment"] = value
        context.user_data["game_step"] = "notes"

        await query.edit_message_text(
            "📝 Send any extra notes, or press Skip Notes.",
            reply_markup=game_notes_keyboard(),
        )
        return

    if query.data == "game_notes_skip":
        context.user_data["game_notes"] = "No"
        context.user_data["game_step"] = "done"

        await query.edit_message_text(
            build_game_request_summary(context),
            reply_markup=game_request_summary_keyboard(),
        )
        return

    if query.data == "submit_game_request":
        user = query.from_user

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
                "There is a problem sending your request right now. Please try again later.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ]),
            )
            return

        await query.edit_message_text(
            f"✅ Your game request was sent successfully.\n"
            f"Request ID: #G{request_id}\n"
            f"Our team will review it and contact you with the price."
        )

        reset_user_flow(context)
        return

    if query.data.startswith("game_accept_price|"):
        request_id = int(query.data.split("|")[1])
        request = get_game_request(request_id)

        if not request:
            await query.edit_message_text("Request not found.")
            return

        (
            _id,
            user_id,
            username,
            customer_name,
            game_name,
            platform,
            request_type,
            plan,
            preferred_payment,
            notes,
            offered_price,
            final_payment_method,
            status,
        ) = request

        update_game_request_status(request_id, "waiting_payment_method")

        await query.edit_message_text(
            f"✅ Price accepted\n\n"
            f"Game: {game_name}\n"
            f"Platform: {platform}\n"
            f"Price: ${offered_price}\n\n"
            f"Choose the payment method:",
            reply_markup=game_user_payment_choice_keyboard(request_id),
        )

        await context.bot.send_message(
            chat_id=config.ORDERS_GROUP_ID,
            text=f"Customer accepted the price for request #G{request_id}.",
        )
        return

    if query.data.startswith("game_cancel_price|"):
        request_id = int(query.data.split("|")[1])
        request = get_game_request(request_id)

        if not request:
            await query.edit_message_text("Request not found.")
            return

        update_game_request_status(request_id, "cancelled_by_customer")

        await query.edit_message_text("❌ Request cancelled successfully.")

        await context.bot.send_message(
            chat_id=config.ORDERS_GROUP_ID,
            text=f"Customer cancelled the price for request #G{request_id}.",
        )
        return

    if query.data.startswith("game_pay|"):
        _, request_id_str, payment_method = query.data.split("|", 2)
        request_id = int(request_id_str)

        request = get_game_request(request_id)
        if not request:
            await query.edit_message_text("Request not found.")
            return

        (
            _id,
            user_id,
            username,
            customer_name,
            game_name,
            platform,
            request_type,
            plan,
            preferred_payment,
            notes,
            offered_price,
            final_payment_method,
            status,
        ) = request

        set_game_request_final_payment(request_id, payment_method)

        context.user_data["awaiting_game_payment_screenshot"] = True
        context.user_data["game_checkout_request_id"] = request_id

        if payment_method == "USDT":
            await query.edit_message_text(
                f"💰 Game Payment - USDT\n\n"
                f"Request ID: #G{request_id}\n"
                f"Game: {game_name}\n"
                f"Platform: {platform}\n"
                f"Price: ${offered_price}\n\n"
                f"Network: {config.USDT_NETWORK}\n"
                f"Wallet Address:\n{config.USDT_WALLET}\n\n"
                f"⚠️ Send only on {config.USDT_NETWORK}\n\n"
                f"Now send the payment screenshot here.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ]),
            )
            return

        await query.edit_message_text(
            f"🏦 Game Payment - CliQ / Bank\n\n"
            f"Request ID: #G{request_id}\n"
            f"Game: {game_name}\n"
            f"Platform: {platform}\n"
            f"Price: ${offered_price}\n\n"
            f"Receiver Name:\n{config.CLIQ_NAME}\n\n"
            f"Now send the payment screenshot here.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]),
        )
        return

    # -------------------------
    # Game Request: Admin Side
    # -------------------------
    if query.data.startswith("game_admin_price|"):
        request_id = int(query.data.split("|")[1])

        await query.answer()
        await query.message.reply_text(
            f"To send a price for request #G{request_id}, use:\n/price {request_id} 20"
        )
        return

    if query.data.startswith("game_admin_unavailable|"):
        request_id = int(query.data.split("|")[1])
        request = get_game_request(request_id)

        if not request:
            await query.answer("Request not found.")
            return

        (
            _id,
            user_id,
            username,
            customer_name,
            game_name,
            platform,
            request_type,
            plan,
            preferred_payment,
            notes,
            offered_price,
            final_payment_method,
            status,
        ) = request

        update_game_request_status(request_id, "not_available")

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"❌ Sorry, your requested game is currently not available.\n\n"
                    f"Request ID: #G{request_id}\n"
                    f"Game: {game_name}\n"
                    f"Platform: {platform}"
                ),
            )
        except Exception as e:
            print("SEND UNAVAILABLE TO USER ERROR:", e)

        await query.message.reply_text(f"Marked request #G{request_id} as not available.")
        return

    if query.data.startswith("game_admin_delivered|"):
        request_id = int(query.data.split("|")[1])
        request = get_game_request(request_id)

        if not request:
            await query.answer("Request not found.")
            return

        (
            _id,
            user_id,
            username,
            customer_name,
            game_name,
            platform,
            request_type,
            plan,
            preferred_payment,
            notes,
            offered_price,
            final_payment_method,
            status,
        ) = request

        update_game_request_status(request_id, "delivered")

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"📦 Your order has been delivered successfully.\n\n"
                    f"Request ID: #G{request_id}\n"
                    f"Game: {game_name}\n"
                    f"Platform: {platform}\n\n"
                    f"Thank you for choosing {config.STORE_NAME}."
                ),
            )
        except Exception as e:
            print("SEND DELIVERED TO USER ERROR:", e)

        await query.message.reply_text(f"Request #G{request_id} marked as delivered.")
        return


# -------------------------
# Message Handler
# -------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Game request creation flow
    if context.user_data.get("awaiting_game_request") and message.text:
        text = message.text.strip()
        step = context.user_data.get("game_step")

        if step == "name":
            context.user_data["game_name"] = text
            context.user_data["game_step"] = "platform"

            await message.reply_text(
                "🎮 Choose the platform:",
                reply_markup=game_platform_keyboard(),
            )
            return

        if step == "notes":
            context.user_data["game_notes"] = text
            context.user_data["game_step"] = "done"

            await message.reply_text(
                build_game_request_summary(context),
                reply_markup=game_request_summary_keyboard(),
            )
            return

    # Subscription payment screenshot
    if message.photo and context.user_data.get("awaiting_payment_screenshot"):
        order_id = context.user_data.get("order_id")

        if not order_id:
            await message.reply_text(
                "Please confirm your purchase first, then send the payment screenshot."
            )
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
            await message.reply_text(
                "There is a problem sending your payment screenshot to support. Please contact support."
            )
            return

        update_order_status(order_id, "paid_waiting_delivery")

        await message.reply_text(
            f"✅ Payment screenshot received.\n"
            f"Order ID: #{order_id}\n"
            f"Our team will review it and deliver your product soon."
        )

        reset_user_flow(context)
        return

    # Game payment screenshot
    if message.photo and context.user_data.get("awaiting_game_payment_screenshot"):
        request_id = context.user_data.get("game_checkout_request_id")
        request = get_game_request(request_id) if request_id else None

        if not request:
            await message.reply_text("Game request not found.")
            return

        (
            _id,
            user_id,
            username,
            customer_name,
            game_name,
            platform,
            request_type,
            plan,
            preferred_payment,
            notes,
            offered_price,
            final_payment_method,
            status,
        ) = request

        try:
            await context.bot.forward_message(
                chat_id=config.ORDERS_GROUP_ID,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
            )

            group_text = (
                f"💳 <b>Game Payment Screenshot Received</b>\n\n"
                f"<b>Request ID:</b> #G{request_id}\n"
                f"<b>Customer Name:</b> {customer_name}\n"
                f"<b>Username:</b> {('@' + username) if username else 'No username'}\n"
                f"<b>Quick Contact:</b> {get_contact_text(user_id, username or '')}\n"
                f"<b>User ID:</b> <code>{user_id}</code>\n\n"
                f"<b>Game Name:</b> {game_name}\n"
                f"<b>Platform:</b> {platform}\n"
                f"<b>Type:</b> {request_type}\n"
                f"<b>Plan:</b> {plan}\n"
                f"<b>Price:</b> ${offered_price}\n"
                f"<b>Payment Method:</b> {final_payment_method}\n"
                f"<b>Status:</b> Paid - Awaiting delivery"
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
            await message.reply_text(
                "There is a problem sending your payment screenshot to support. Please contact support."
            )
            return

        update_game_request_status(request_id, "paid_waiting_delivery")

        await message.reply_text(
            f"✅ Payment screenshot received.\n"
            f"Request ID: #G{request_id}\n"
            f"Our team will review it and deliver your game soon."
        )

        reset_user_flow(context)
        return

    # Anything else
    if message.text:
        await message.reply_text(
            "Please use /start and choose an option from the menu."
        )


def main():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# تنظیمات لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالت‌های گفتگو
(
    STATE_NONE,
    STATE_NERKH_ARZ,
    STATE_ARZESH,
    STATE_BIMEH,
    STATE_KERAYE_HAML,
    STATE_MAKHAZ,
    STATE_PASMAND,
) = range(7)


# نگهداری اطلاعات کاربر
class UserData:
    def __init__(self):
        self.state = STATE_NONE
        self.nerkh_arz = None
        self.arzesh = None
        self.bimeh = None
        self.keraye_haml = None
        self.makhaz = None
        self.has_pasmand = False


users: dict[int, UserData] = {}


def to_farsi_number(number: int) -> str:
    en_to_fa = str.maketrans("0123456789,", "۰۱۲۳۴۵۶۷۸۹٬")
    return f"{number:,}".translate(en_to_fa)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    users[user_id] = UserData()
    users[user_id].state = STATE_NERKH_ARZ
    await update.message.reply_text(
        "🤖 به ربات محاسبه حقوق گمرکی خوش آمدید!\n\n"
        "لطفاً نرخ ارز را وارد کنید (ریال):"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in users or users[user_id].state == STATE_NONE:
        await update.message.reply_text("لطفاً ابتدا فرمان /start را ارسال کنید.")
        return

    user_data = users[user_id]
    text = update.message.text.strip()

    try:
        if user_data.state == STATE_NERKH_ARZ:
            value = int(text)
            if value < 1000:
                await update.message.reply_text(
                    "❌ مقدار باید حداقل ۱۰۰۰ ریال باشد. لطفاً مجدداً وارد کنید."
                )
                return
            user_data.nerkh_arz = value
            user_data.state = STATE_ARZESH
            await update.message.reply_text(
                "✅ دریافت شد.\n\nلطفاً ارزش FOB کالا را وارد کنید (دلار):"
            )

        elif user_data.state == STATE_ARZESH:
            value = float(text)
            if value < 1:
                await update.message.reply_text(
                    "❌ مقدار باید حداقل ۱ دلار باشد. لطفاً مجدداً وارد کنید."
                )
                return
            user_data.arzesh = value
            user_data.state = STATE_BIMEH
            await update.message.reply_text(
                "✅ دریافت شد.\n\nلطفاً مبلغ بیمه را وارد کنید (ریال):"
            )

        elif user_data.state == STATE_BIMEH:
            value = float(text)
            if value < 0:
                await update.message.reply_text(
                    "❌ مقدار نمی‌تواند منفی باشد. لطفاً مجدداً وارد کنید."
                )
                return
            user_data.bimeh = value
            user_data.state = STATE_KERAYE_HAML
            await update.message.reply_text(
                "✅ دریافت شد.\n\nلطفاً مبلغ کرایه حمل را وارد کنید (ریال):"
            )

        elif user_data.state == STATE_KERAYE_HAML:
            value = int(text)
            if value < 0:
                await update.message.reply_text(
                    "❌ مقدار نمی‌تواند منفی باشد. لطفاً مجدداً وارد کنید."
                )
                return
            user_data.keraye_haml = value
            user_data.state = STATE_MAKHAZ
            await update.message.reply_text(
                "✅ دریافت شد.\n\nلطفاً ماخذ (درصد) را وارد کنید (۰ تا ۱۰۰):"
            )

        elif user_data.state == STATE_MAKHAZ:
            value = float(text)
            if not (0 <= value <= 100):
                await update.message.reply_text(
                    "❌ مقدار باید بین ۰ تا ۱۰۰ باشد. لطفاً مجدداً وارد کنید."
                )
                return
            user_data.makhaz = value
            user_data.state = STATE_PASMAND

            keyboard = [
                [InlineKeyboardButton("بله", callback_data="yes")],
                [InlineKeyboardButton("خیر", callback_data="no")],
            ]
            await update.message.reply_text(
                "❓ آیا محاسبه پسماند نیاز است؟",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

    except ValueError:
        await update.message.reply_text("❌ مقدار نامعتبر است. لطفاً فقط عدد وارد کنید.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in users or users[user_id].state != STATE_PASMAND:
        await query.edit_message_text(
            "لطفاً ابتدا /start را ارسال کنید و مراحل را دنبال کنید."
        )
        return

    user_data = users[user_id]
    user_data.has_pasmand = query.data == "yes"

    # محاسبات
    fob = user_data.nerkh_arz * user_data.arzesh
    cif = fob + user_data.bimeh + user_data.keraye_haml
    hoghogh = cif * user_data.makhaz / 100
    helal = hoghogh / 1000
    pasmand = cif * 0.5 / 1000 if user_data.has_pasmand else 0
    vat = (cif + hoghogh + helal) * 0.10
    total = hoghogh + helal + vat + pasmand

    # ارسال نتیجه
    result = (
        "📦 نتیجه محاسبات نهایی:\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        f"🔹 CIF کالا: {to_farsi_number(round(cif))} ریال\n"
        f"🔸 حقوق ورودی: {to_farsi_number(round(hoghogh))} ریال\n"
        f"🩺 یک درصد هلال احمر: {to_farsi_number(round(helal))} ریال\n"
    )
    if user_data.has_pasmand:
        result += f"♻️ پسماند: {to_farsi_number(round(pasmand))} ریال\n"
    result += (
        f"💰 مالیات ارزش افزوده: {to_farsi_number(round(vat))} ریال\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        f"💳 مجموع پرداختی: {to_farsi_number(round(total))} ریال\n\n"
        "برای محاسبه دوباره /start را بزنید."
    )
    await query.edit_message_text(result)
    users[user_id].state = STATE_NONE


def main() -> None:
    # توکن ربات را اینجا وارد کنید
    TOKEN = "8108601920:AAG5tBsCi8xrsnWsEmKI7HvQe5neivLyF_M"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))

    logger.info("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()

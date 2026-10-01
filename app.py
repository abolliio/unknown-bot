"""
بات دریافت پیام برای تلگرام
- هر پیامی که کاربر بفرسته، همراه با نام / یوزرنیم / آیدی عددی برای صاحب بات ارسال می‌شود.
- صاحب بات با Reply روی پیام می‌تونه جواب بده و جواب به همون شخص می‌رسه.
"""
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

logging.basicConfig(level=logging.INFO)

TOKEN = "8817145486:AAG7MzfcYAx656haHq63qm4zPehprpVwZcI"
OWNER_ID = 8835416900


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋 پیامت رو بفرست تا به صاحب بات برسه.\n\n"
        "⚠️ توجه: صاحب بات نام، یوزرنیم و آیدی عددی حساب تلگرامت رو می‌بینه."
    )


async def from_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پیام کاربر -> صاحب بات (همراه با مشخصات فرستنده)"""
    user = update.effective_user
    msg = update.message

    header = (
        "📩 پیام جدید\n"
        f"نام: {user.full_name}\n"
        f"یوزرنیم: {'@' + user.username if user.username else '—'}\n"
        f"آیدی: {user.id}"
    )
    header_msg = await context.bot.send_message(OWNER_ID, header)
    copied = await msg.copy(OWNER_ID, reply_to_message_id=header_msg.message_id)

    context.bot_data[header_msg.message_id] = user.id
    context.bot_data[copied.message_id] = user.id

    await msg.reply_text("✅ پیامت ارسال شد.")


async def from_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """جواب صاحب بات (با Reply) -> کاربر"""
    replied = update.message.reply_to_message
    if not replied:
        await update.message.reply_text("برای جواب دادن، روی پیام کاربر Reply بزن.")
        return

    target = context.bot_data.get(replied.message_id)
    if not target:
        await update.message.reply_text("گیرنده‌ی این پیام پیدا نشد.")
        return

    await update.message.copy(target)
    await update.message.reply_text("✅ جواب ارسال شد.")


def main():
    persistence = PicklePersistence(filepath="bot_data.pkl")
    app = Application.builder().token(TOKEN).persistence(persistence).build()

    owner = filters.User(OWNER_ID)
    app.add_handler(CommandHandler("start", start, filters.ChatType.PRIVATE))
    app.add_handler(MessageHandler(owner & ~filters.COMMAND, from_owner))
    app.add_handler(
        MessageHandler(filters.ChatType.PRIVATE & ~owner & ~filters.COMMAND, from_user)
    )

    app.run_polling()


if __name__ == "__main__":
    main()

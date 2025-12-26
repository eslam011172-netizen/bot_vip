import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN=5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g")

CHANNELS = ["@Muslim_vip1"]
ADMIN_ID = 5083996619
DATA_FILE = "data.json"


if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"users": {}, "refs": {}}


def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


async def is_subscribed(bot, user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    if user_id not in data["users"]:
        data["users"][user_id] = {"invites": 0}
        save()

        if context.args:
            ref = context.args[0]
            if ref != user_id:
                data["refs"].setdefault(ref, [])
                if user_id not in data["refs"][ref]:
                    data["refs"][ref].append(user_id)
                    data["users"].setdefault(ref, {"invites": 0})
                    data["users"][ref]["invites"] += 1
                    save()

    if not await is_subscribed(context.bot, user.id):
        buttons = [
            [InlineKeyboardButton("📢 اشترك في القناة", url="https://t.me/Muslim_vip1")],
            [InlineKeyboardButton("✅ تحقّق", callback_data="check")]
        ]
        await update.message.reply_text(
            "📌 لازم تشترك في القناة الأول",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    link = f"https://t.me/{context.bot.username}?start={user_id}"
    invites = data["users"][user_id]["invites"]

    await update.message.reply_text(
        f"✅ أهلاً بيك!\n\n"
        f"👥 عدد الدعوات: {invites}\n\n"
        f"🔗 رابط الدعوة الخاص بك:\n{link}"
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await is_subscribed(context.bot, query.from_user.id):
        await query.edit_message_text("✅ تم التحقق بنجاح\nاكتب /start")
    else:
        await query.answer("❌ لسه مش مشترك", show_alert=True)


async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check, pattern="check"))
    print("Bot is running...")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
import os, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g")

CHANNELS = ["@Muslim_vip1"]
BOT = "@VersatileVIP_bot"      # غيره
ADMIN_ID = 5083996619رقم_ايديك   # غيره

DATA_FILE = "data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"users": {}, "refs": {}}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def subscribed(bot, user_id):
    try:
        for ch in CHANNELS:
            m = await bot.get_chat_member(ch, user_id)
            if m.status not in ["member", "administrator", "creator"]:
                return False
        return True
    except:
        return False

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 رابط الدعوة", callback_data="link")],
        [InlineKeyboardButton("👥 دعواتي", callback_data="count")],
        [InlineKeyboardButton("🏆 أفضل الداعمين", callback_data="top")],
        [InlineKeyboardButton("📢 القناة", url="https://t.me/Muslim_vip1")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)

    if not await subscribed(context.bot, user.id):
        await update.message.reply_text("❌ اشترك في القناة أولاً")
        return

    if uid not in data["users"]:
        data["users"][uid] = 0
        if context.args:
            ref = context.args[0]
            if ref != uid and uid not in data["refs"]:
                data["refs"][uid] = ref
                data["users"][ref] = data["users"].get(ref, 0) + 1
                save()

    await update.message.reply_text(
        "👋 أهلاً بك\nانشر رابطك واجمع نقاط 🎯",
        reply_markup=menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = str(q.from_user.id)

    if q.data == "link":
        await q.message.reply_text(f"https://t.me/{BOT[1:]}?start={uid}")

    elif q.data == "count":
        c = data["users"].get(uid, 0)
        await q.message.reply_text(f"👥 دعواتك: {c}")

    elif q.data == "top":
        top = sorted(data["users"].items(), key=lambda x: x[1], reverse=True)[:5]
        msg = "🏆 أفضل الداعمين:\n"
        for i,(u,c) in enumerate(top,1):
            msg += f"{i}- {c} دعوة\n"
        await q.message.reply_text(msg)

    await q.answer()

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()

if __name__ == "__main__":
    main()
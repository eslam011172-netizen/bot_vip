import telebot
from telebot import types

# ====== الإعدادات ======
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
FORCE_CHANNEL = "@Muslim_vip1"   # يوزر القناة
bot = telebot.TeleBot(TOKEN)

# ====== فحص الاشتراك ======
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ====== زر الاشتراك ======
def force_sub_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "📢 اشترك في القناة",
            url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "✅ تحقق",
            callback_data="check_sub"
        )
    )
    return markup

# ====== القائمة الرئيسية ======
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 رصيدي", "👥 دعوة أصدقاء")
    markup.row("🎁 المكافآت")
    return markup

# ====== /start ======
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        bot.send_message(
            message.chat.id,
            "🚫 لازم تشترك في القناة الأول",
            reply_markup=force_sub_markup()
        )
        return

    bot.send_message(
        message.chat.id,
        "👋 أهلاً بيك في البوت\n\nاختر من القائمة 👇",
        reply_markup=main_menu()
    )

# ====== زر التحقق ======
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم الاشتراك")
        bot.send_message(
            call.message.chat.id,
            "✔️ تم التحقق بنجاح\nاكتب /start"
        )
    else:
        bot.answer_callback_query(
            call.id,
            "❌ لسه مش مشترك",
            show_alert=True
        )

# ====== الأزرار ======
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(message):
    bot.send_message(message.chat.id, "💰 رصيدك: 0")

@bot.message_handler(func=lambda m: m.text == "👥 دعوة أصدقاء")
def invite(message):
    bot.send_message(
        message.chat.id,
        f"👥 رابطك:\nhttps://t.me/{bot.get_me().username}?start={message.from_user.id}"
    )

@bot.message_handler(func=lambda m: m.text == "🎁 المكافآت")
def rewards(message):
    bot.send_message(
        message.chat.id,
        "🎁 المكافآت:\n\n50 نقطة = جائزة 🎉\n100 نقطة = VIP ⭐"
    )

# ====== تشغيل البوت ======
print("Bot is running...")
bot.infinity_polling()

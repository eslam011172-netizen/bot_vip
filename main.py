import telebot
from telebot import types

# ================== الإعدادات ==================
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
FORCE_CHANNEL = "@Muslim_vip1"
ADMIN_ID = 5083996619

bot = telebot.TeleBot(TOKEN)

# ================== قاعدة بيانات مؤقتة ==================
users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "points": 0,
            "vip": False
        }
    return users[uid]

# ================== فحص الاشتراك ==================
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def force_sub_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "📢 اشترك في القناة",
            url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
        )
    )
    markup.add(
        types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub")
    )
    return markup

# ================== القوائم ==================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 رصيدي", "👥 دعوة أصدقاء")
    markup.row("🛒 المتجر", "⭐ VIP")
    markup.row("👑 لوحة الأدمن")
    return markup

def shop_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔥 ملف هيدشوت - 50 نقطة")
    markup.row("🎁 هدية VIP - 200 نقطة")
    markup.row("⬅️ رجوع")
    return markup

# ================== start + إحالة ==================
@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    user = get_user(uid)

    if not is_subscribed(uid):
        bot.send_message(
            message.chat.id,
            "🚫 لازم تشترك في القناة الأول",
            reply_markup=force_sub_markup()
        )
        return

    if message.text.startswith("/start "):
        ref = message.text.split()[1]
        if ref.isdigit() and int(ref) != uid:
            ref_user = get_user(int(ref))
            ref_user["points"] += 10
            bot.send_message(int(ref), "🎉 جالك صديق جديد +10 نقاط")

    bot.send_message(
        message.chat.id,
        "👋 أهلاً بيك في بوت Versatile VIP\nاختر من القائمة 👇",
        reply_markup=main_menu()
    )

# ================== تحقق الاشتراك ==================
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم الاشتراك")
        bot.send_message(call.message.chat.id, "اكتب /start")
    else:
        bot.answer_callback_query(call.id, "❌ اشترك الأول", show_alert=True)

# ================== الرصيد ==================
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"💰 رصيدك: {user['points']} نقطة"
    )

# ================== دعوة ==================
@bot.message_handler(func=lambda m: m.text == "👥 دعوة أصدقاء")
def invite(message):
    bot.send_message(
        message.chat.id,
        f"👥 رابطك:\nhttps://t.me/{bot.get_me().username}?start={message.from_user.id}"
    )

# ================== المتجر ==================
@bot.message_handler(func=lambda m: m.text == "🛒 المتجر")
def shop(message):
    bot.send_message(
        message.chat.id,
        "🛒 المتجر",
        reply_markup=shop_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🔥 ملف هيدشوت - 50 نقطة")
def buy_file(message):
    user = get_user(message.from_user.id)
    if user["points"] < 50:
        bot.send_message(message.chat.id, "❌ نقاطك غير كافية")
        return

    user["points"] -= 50
    bot.send_document(
        message.chat.id,
        open("headshot.pdf", "rb"),
        caption="🔥 ملف الهيدشوت – مبروك 🎉"
    )

@bot.message_handler(func=lambda m: m.text == "🎁 هدية VIP - 200 نقطة")
def buy_vip(message):
    user = get_user(message.from_user.id)
    if user["points"] < 200:
        bot.send_message(message.chat.id, "❌ محتاج 200 نقطة")
        return

    user["points"] -= 200
    user["vip"] = True
    bot.send_message(message.chat.id, "⭐ تم تفعيل VIP بنجاح 👑")

# ================== رجوع ==================
@bot.message_handler(func=lambda m: m.text == "⬅️ رجوع")
def back(message):
    bot.send_message(
        message.chat.id,
        "القائمة الرئيسية",
        reply_markup=main_menu()
    )

# ================== لوحة الأدمن ==================
@bot.message_handler(func=lambda m: m.text == "👑 لوحة الأدمن")
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "👑 لوحة الأدمن\n\nعدد المستخدمين: "
        + str(len(users))
    )

# ================== تشغيل ==================
print("Bot is running...")
bot.infinity_polling()

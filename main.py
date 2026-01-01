import telebot
from telebot import types
import json
import os

# ================== الإعدادات ==================
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
FORCE_CHANNEL = "@Muslim_vip1"
ADMIN_ID = 5083996619

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"

# ================== تحميل / حفظ البيانات ==================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data()

def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "points": 0,
            "invites": 0
        }
        save_data(users)
    return users[uid]

# ================== فحص الاشتراك ==================
def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return m.status in ["member", "administrator", "creator"]
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
    markup.add(types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
    return markup

# ================== القوائم ==================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 رصيدي", "👥 دعوة أصدقاء")
    markup.row("🛒 المتجر", "🔋 شحن نقاط")
    return markup

def shop_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎯 ملف Headshot", callback_data="buy_headshot")
    )
    return markup

# ================== /start ==================
@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id

    if not is_subscribed(uid):
        bot.send_message(
            message.chat.id,
            "🚫 اشترك في القناة أولاً",
            reply_markup=force_sub_markup()
        )
        return

    get_user(uid)

    bot.send_message(
        message.chat.id,
        "👋 أهلاً بيك\nاختر من القائمة 👇",
        reply_markup=main_menu()
    )

# ================== تحقق الاشتراك ==================
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم")
        bot.send_message(call.message.chat.id, "✔️ اكتب /start")
    else:
        bot.answer_callback_query(call.id, "❌ لسه", show_alert=True)

# ================== الرصيد ==================
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"💰 نقاطك: {user['points']}\n👥 دعواتك: {user['invites']}"
    )

# ================== دعوة ==================
@bot.message_handler(func=lambda m: m.text == "👥 دعوة أصدقاء")
def invite(message):
    uid = message.from_user.id
    bot.send_message(
        message.chat.id,
        f"👥 رابطك:\nhttps://t.me/{bot.get_me().username}?start={uid}\n\n+5 نقاط لكل صديق"
    )

# ================== المتجر ==================
@bot.message_handler(func=lambda m: m.text == "🛒 المتجر")
def shop(message):
    bot.send_message(
        message.chat.id,
        "🛒 متجر النقاط\nاختر المنتج 👇",
        reply_markup=shop_menu()
    )

# ================== شراء Headshot ==================
@bot.callback_query_handler(func=lambda c: c.data == "buy_headshot")
def buy_headshot(call):
    uid = str(call.from_user.id)
    user = get_user(uid)
    price = 50

    if user["points"] < price:
        bot.answer_callback_query(call.id, "❌ نقاطك غير كافية", show_alert=True)
        return

    # خصم النقاط
    user["points"] -= price
    save_data(users)

    # تسليم تلقائي (رابط / ملف)
    bot.send_message(
        call.message.chat.id,
        "✅ تم الشراء بنجاح 🎉\n\n📦 رابط الملف:\nhttps://example.com/headshot.zip"
    )

# ================== شحن نقاط ==================
@bot.message_handler(func=lambda m: m.text == "🔋 شحن نقاط")
def charge(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💳 تواصل مع الأدمن", url="https://t.me/YourAdmin")
    )
    bot.send_message(
        message.chat.id,
        "🔋 لشحن النقاط تواصل مع الأدمن 👇",
        reply_markup=markup
    )

# ================== إحالات ==================
@bot.message_handler(func=lambda m: m.text.startswith("/start "))
def referral(message):
    uid = str(message.from_user.id)
    ref = message.text.split()[-1]

    if ref != uid:
        user = get_user(uid)
        if "referred" not in user:
            user["referred"] = True
            users[ref]["points"] += 5
            users[ref]["invites"] += 1
            save_data(users)

# ================== تشغيل ==================
print("Bot is running...")
bot.infinity_polling(skip_pending=True)

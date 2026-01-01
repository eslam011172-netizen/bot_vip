import telebot
from telebot import types
import threading
import json
import os

# ================== الإعدادات ==================
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
FORCE_CHANNEL = "@Muslim_vip1"
ADMINS = [5083996619]  # حط ID الأدمن
DATA_FILE = "users.json"

bot = telebot.TeleBot(TOKEN, threaded=True)

# ================== إدارة البيانات ==================
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_user(user_id):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"points": 0}
        save_users(users)
    return users[str(user_id)]

def update_points(user_id, amount):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"points": 0}
    users[uid]["points"] += amount
    save_users(users)

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
    markup.add(types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
    return markup

# ================== القوائم ==================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 رصيدي", "👥 دعوة أصدقاء")
    markup.row("🎁 المكافآت")
    return markup

def admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ إضافة نقاط", "➖ خصم نقاط")
    markup.row("📢 رسالة جماعية", "📊 إحصائيات")
    markup.row("⬅️ رجوع")
    return markup

# ================== /start ==================
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

    get_user(user_id)

    bot.send_message(
        message.chat.id,
        "👋 أهلاً بيك في Versatile VIP Bot\n\nاختر من القائمة 👇",
        reply_markup=main_menu()
    )

# ================== تحقق الاشتراك ==================
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم الاشتراك")
        bot.send_message(call.message.chat.id, "✔️ تم التحقق\nاكتب /start")
    else:
        bot.answer_callback_query(call.id, "❌ لسه مش مشترك", show_alert=True)

# ================== المستخدم ==================
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 رصيدك: {user['points']} نقطة")

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

# ================== الأدمن ==================
@bot.message_handler(commands=["admin"])
def admin(message):
    if message.from_user.id in ADMINS:
        bot.send_message(
            message.chat.id,
            "👑 لوحة تحكم الأدمن",
            reply_markup=admin_menu()
        )

# إضافة نقاط
@bot.message_handler(func=lambda m: m.text == "➕ إضافة نقاط" and m.from_user.id in ADMINS)
def add_points_step1(message):
    msg = bot.send_message(message.chat.id, "✍️ أرسل: ID عدد_النقاط")
    bot.register_next_step_handler(msg, add_points_step2)

def add_points_step2(message):
    try:
        uid, amount = message.text.split()
        update_points(uid, int(amount))
        bot.send_message(message.chat.id, "✅ تم إضافة النقاط")
    except:
        bot.send_message(message.chat.id, "❌ صيغة خاطئة")

# خصم نقاط
@bot.message_handler(func=lambda m: m.text == "➖ خصم نقاط" and m.from_user.id in ADMINS)
def remove_points_step1(message):
    msg = bot.send_message(message.chat.id, "✍️ أرسل: ID عدد_النقاط")
    bot.register_next_step_handler(msg, remove_points_step2)

def remove_points_step2(message):
    try:
        uid, amount = message.text.split()
        update_points(uid, -int(amount))
        bot.send_message(message.chat.id, "✅ تم خصم النقاط")
    except:
        bot.send_message(message.chat.id, "❌ صيغة خاطئة")

# إحصائيات
@bot.message_handler(func=lambda m: m.text == "📊 إحصائيات" and m.from_user.id in ADMINS)
def stats(message):
    users = load_users()
    bot.send_message(
        message.chat.id,
        f"📊 الإحصائيات:\n👥 عدد المستخدمين: {len(users)}"
    )

# رجوع
@bot.message_handler(func=lambda m: m.text == "⬅️ رجوع")
def back(message):
    bot.send_message(message.chat.id, "⬅️ رجوع", reply_markup=main_menu())

# ================== تشغيل سريع ==================
def run_bot():
    bot.infinity_polling(skip_pending=True, none_stop=True, timeout=20)

threading.Thread(target=run_bot).start()

print("🚀 Bot is running fast & stable")

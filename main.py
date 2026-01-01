import telebot
from telebot import types
import json
import time
import os

# ========= الإعدادات =========
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
FORCE_CHANNEL = "@Muslim_vip1"
ADMINS = [5083996619]  # ايدي الأدمن
DATA_FILE = "users.json"

bot = telebot.TeleBot(TOKEN, threaded=True)

# ========= تحميل / حفظ البيانات =========
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_users()
last_action = {}

# ========= أدوات =========
def is_admin(uid):
    return uid in ADMINS

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def anti_spam(uid, sec=2):
    now = time.time()
    if uid in last_action and now - last_action[uid] < sec:
        return False
    last_action[uid] = now
    return True

def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"points": 0, "invites": 0}
        save_users(users)
    return users[uid]

# ========= القوائم =========
def main_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("💰 رصيدي", "👥 دعوة أصدقاء")
    m.row("🎁 المكافآت")
    return m

def admin_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("➕ إضافة نقاط", "➖ خصم نقاط")
    m.row("📊 إحصائيات", "📢 إذاعة")
    m.row("⬅️ خروج")
    return m

# ========= /start =========
@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id

    if not anti_spam(uid):
        return

    if not is_subscribed(uid):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "📢 اشترك في القناة",
                url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
            )
        )
        markup.add(types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
        bot.send_message(message.chat.id, "🚫 لازم تشترك في القناة الأول", reply_markup=markup)
        return

    get_user(uid)

    if is_admin(uid):
        bot.send_message(message.chat.id, "👑 لوحة الأدمن", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, "👋 أهلاً بيك", reply_markup=main_menu())

# ========= تحقق الاشتراك =========
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم الاشتراك")
        bot.send_message(call.message.chat.id, "اكتب /start")
    else:
        bot.answer_callback_query(call.id, "❌ اشترك ثم حاول", show_alert=True)

# ========= المستخدم =========
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(message):
    u = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 رصيدك: {u['points']} نقطة")

@bot.message_handler(func=lambda m: m.text == "👥 دعوة أصدقاء")
def invite(message):
    uid = message.from_user.id
    bot.send_message(
        message.chat.id,
        f"👥 رابطك:\nhttps://t.me/{bot.get_me().username}?start={uid}\n+5 نقاط لكل دعوة"
    )

@bot.message_handler(func=lambda m: m.text == "🎁 المكافآت")
def rewards(message):
    bot.send_message(
        message.chat.id,
        "🎁 المكافآت:\n\n50 نقطة = ملف 🔥\n100 نقطة = VIP ⭐"
    )

# ========= لوحة الأدمن =========
@bot.message_handler(func=lambda m: m.text == "➕ إضافة نقاط" and is_admin(m.from_user.id))
def add_points(message):
    msg = bot.send_message(message.chat.id, "ارسل: ايدي عدد")
    bot.register_next_step_handler(msg, process_add)

def process_add(message):
    try:
        uid, amount = message.text.split()
        user = get_user(uid)
        user["points"] += int(amount)
        save_users(users)
        bot.send_message(message.chat.id, "✅ تم الإضافة")
    except:
        bot.send_message(message.chat.id, "❌ صيغة خطأ")

@bot.message_handler(func=lambda m: m.text == "➖ خصم نقاط" and is_admin(m.from_user.id))
def remove_points(message):
    msg = bot.send_message(message.chat.id, "ارسل: ايدي عدد")
    bot.register_next_step_handler(msg, process_remove)

def process_remove(message):
    try:
        uid, amount = message.text.split()
        user = get_user(uid)
        user["points"] = max(0, user["points"] - int(amount))
        save_users(users)
        bot.send_message(message.chat.id, "✅ تم الخصم")
    except:
        bot.send_message(message.chat.id, "❌ صيغة خطأ")

@bot.message_handler(func=lambda m: m.text == "📊 إحصائيات" and is_admin(m.from_user.id))
def stats(message):
    bot.send_message(message.chat.id, f"👥 عدد المستخدمين: {len(users)}")

@bot.message_handler(func=lambda m: m.text == "📢 إذاعة" and is_admin(m.from_user.id))
def broadcast(message):
    msg = bot.send_message(message.chat.id, "اكتب الرسالة")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    sent = 0
    for uid in users:
        try:
            bot.send_message(uid, message.text)
            sent += 1
        except:
            pass
    bot.send_message(message.chat.id, f"✅ تم الإرسال لـ {sent}")

@bot.message_handler(func=lambda m: m.text == "⬅️ خروج")
def exit_admin(message):
    bot.send_message(message.chat.id, "تم الخروج", reply_markup=main_menu())

# ========= تشغيل =========
print("Bot is running...")
bot.infinity_polling(skip_pending=True, none_stop=True, timeout=20)

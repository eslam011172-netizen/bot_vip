from telebot import types
from utils.users import (
    get_user,
    add_points,
    remove_points,
    ban_user,
    get_all_users
)
import json
import os

ADMINS = [5083996619]  # حط ايديك هنا

ADMIN_STATE = {}

# ================== أدوات ==================
def is_admin(user_id):
    return user_id in ADMINS

def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================== لوحة الأدمن ==================
def admin_panel(bot, message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ الأمر ده مش متاح")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ إضافة نقاط", "➖ خصم نقاط")
    markup.add("📢 رسالة جماعية", "📊 إحصائيات")
    markup.add("🚫 حظر مستخدم", "⬅️ رجوع")

    bot.send_message(
        message.chat.id,
        "👑 لوحة تحكم الأدمن",
        reply_markup=markup
    )

# ================== إضافة نقاط ==================
def add_points_step(bot, message):
    ADMIN_STATE[message.from_user.id] = "ADD_POINTS"
    bot.send_message(message.chat.id, "✏️ ابعت:\nuser_id عدد_النقاط\nمثال:\n123456789 50")

def handle_add_points(bot, message):
    try:
        uid, pts = map(int, message.text.split())
        add_points(uid, pts)
        bot.send_message(message.chat.id, f"✅ تم إضافة {pts} نقطة للمستخدم {uid}")
    except:
        bot.send_message(message.chat.id, "❌ صيغة غلط")
    ADMIN_STATE.pop(message.from_user.id, None)

# ================== خصم نقاط ==================
def remove_points_step(bot, message):
    ADMIN_STATE[message.from_user.id] = "REMOVE_POINTS"
    bot.send_message(message.chat.id, "✏️ ابعت:\nuser_id عدد_النقاط")

def handle_remove_points(bot, message):
    try:
        uid, pts = map(int, message.text.split())
        remove_points(uid, pts)
        bot.send_message(message.chat.id, f"➖ تم خصم {pts} نقطة من {uid}")
    except:
        bot.send_message(message.chat.id, "❌ صيغة غلط")
    ADMIN_STATE.pop(message.from_user.id, None)

# ================== رسالة جماعية ==================
def broadcast_step(bot, message):
    ADMIN_STATE[message.from_user.id] = "BROADCAST"
    bot.send_message(message.chat.id, "📢 ابعت الرسالة اللي هتتبعت لكل المستخدمين")

def handle_broadcast(bot, message):
    users = get_all_users()
    sent = 0
    for uid in users:
        try:
            bot.send_message(uid, message.text)
            sent += 1
        except:
            pass
    bot.send_message(message.chat.id, f"✅ تم الإرسال لـ {sent} مستخدم")
    ADMIN_STATE.pop(message.from_user.id, None)

# ================== إحصائيات ==================
def stats(bot, message):
    users = get_all_users()
    bot.send_message(
        message.chat.id,
        f"📊 إحصائيات البوت:\n\n👥 عدد المستخدمين: {len(users)}"
    )

# ================== حظر مستخدم ==================
def ban_step(bot, message):
    ADMIN_STATE[message.from_user.id] = "BAN"
    bot.send_message(message.chat.id, "🚫 ابعت user_id للحظر")

def handle_ban(bot, message):
    try:
        uid = int(message.text)
        ban_user(uid)
        bot.send_message(message.chat.id, f"🚫 تم حظر المستخدم {uid}")
    except:
        bot.send_message(message.chat.id, "❌ ايدي غلط")
    ADMIN_STATE.pop(message.from_user.id, None)

# ================== المعالج العام ==================
def admin_router(bot, message):
    uid = message.from_user.id

    if not is_admin(uid):
        return

    if message.text == "/admin":
        admin_panel(bot, message)

    elif message.text == "➕ إضافة نقاط":
        add_points_step(bot, message)

    elif message.text == "➖ خصم نقاط":
        remove_points_step(bot, message)

    elif message.text == "📢 رسالة جماعية":
        broadcast_step(bot, message)

    elif message.text == "📊 إحصائيات":
        stats(bot, message)

    elif message.text == "🚫 حظر مستخدم":
        ban_step(bot, message)

    elif uid in ADMIN_STATE:
        state = ADMIN_STATE[uid]
        if state == "ADD_POINTS":
            handle_add_points(bot, message)
        elif state == "REMOVE_POINTS":
            handle_remove_points(bot, message)
        elif state == "BROADCAST":
            handle_broadcast(bot, message)
        elif state == "BAN":
            handle_ban(bot, message)

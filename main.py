import telebot
import json
import time
import os

# ================== الإعدادات ==================
TOKEN = "PUT_YOUR_BOT_TOKEN"
BOT_USERNAME = "@VersatileVIP_bot"
CHANNEL = "@Muslim_vip1"
ADMIN_ID = 5083996619  # حط ايديك هنا

CPA_LINK = "https://example.com/cpa-offer"

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"

# ================== التخزين ==================
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "points": 0,
            "invites": 0,
            "last_collect": 0,
            "referred": False
        }
        save_users()
    return users[uid]

# ================== القائمة ==================
def menu(is_admin=False):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 رصيدي", "🎯 جمع دولارات")
    markup.row("👥 دعوة أصدقاء", "🎁 المكافآت")
    markup.row("📢 القناة")
    if is_admin:
        markup.row("🛠 لوحة الأدمن")
    return markup

# ================== START + إحالة ==================
@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.from_user.id
    user = get_user(uid)

    # إحالة (مرة واحدة)
    if msg.text.startswith("/start "):
        ref = msg.text.split()[1]
        if ref.isdigit() and ref != str(uid) and not user["referred"]:
            ref_user = get_user(ref)
            ref_user["points"] += 5
            ref_user["invites"] += 1
            user["referred"] = True
            save_users()
            bot.send_message(int(ref), "🎉 صديق جديد عن طريقك +5 دولارات")

    is_admin = uid == ADMIN_ID

    bot.send_message(
        msg.chat.id,
        "👋 أهلاً بيك\n\n💵 اجمع دولارات واستبدلها بمكافآت\n⚠️ الدولارات نقاط داخل البوت",
        reply_markup=menu(is_admin)
    )

# ================== الرصيد ==================
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(msg):
    user = get_user(msg.from_user.id)
    bot.send_message(
        msg.chat.id,
        f"💰 رصيدك: {user['points']} دولار\n👥 دعواتك: {user['invites']}"
    )

# ================== جمع دولارات (منع تحايل) ==================
@bot.message_handler(func=lambda m: m.text == "🎯 جمع دولارات")
def collect(msg):
    user = get_user(msg.from_user.id)
    now = time.time()

    if now - user["last_collect"] < 60:
        bot.send_message(msg.chat.id, "⏳ استنى دقيقة قبل ما تجمع تاني")
        return

    user["points"] += 1
    user["last_collect"] = now
    save_users()

    bot.send_message(msg.chat.id, "✅ حصلت على 1 دولار")

# ================== الدعوة ==================
@bot.message_handler(func=lambda m: m.text == "👥 دعوة أصدقاء")
def invite(msg):
    uid = msg.from_user.id
    bot.send_message(
        msg.chat.id,
        f"👥 رابطك:\nhttps://t.me/{BOT_USERNAME}?start={uid}\n\n+5 دولارات لكل صديق"
    )

# ================== المكافآت + CPA ==================
@bot.message_handler(func=lambda m: m.text == "🎁 المكافآت")
def rewards(msg):
    user = get_user(msg.from_user.id)

    text = (
        "🎁 المكافآت:\n\n"
        "🎯 50 دولار = ملف ربح\n"
        "🎯 100 دولار = عرض CPA\n"
        "🎯 200 دولار = محتوى VIP\n\n"
    )

    if user["points"] >= 100:
        text += f"🔥 عرض CPA متاح:\n{CPA_LINK}"
    else:
        text += "🔒 عرض CPA يفتح عند 100 دولار"

    bot.send_message(msg.chat.id, text)

# ================== القناة ==================
@bot.message_handler(func=lambda m: m.text == "📢 القناة")
def channel(msg):
    bot.send_message(msg.chat.id, f"📢 تابع القناة:\n{CHANNEL}")

# ================== لوحة الأدمن ==================
@bot.message_handler(func=lambda m: m.text == "🛠 لوحة الأدمن")
def admin_panel(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    total_users = len(users)
    total_points = sum(u["points"] for u in users.values())

    bot.send_message(
        msg.chat.id,
        f"🛠 لوحة الأدمن\n\n"
        f"👥 المستخدمين: {total_users}\n"
        f"💰 إجمالي الدولارات: {total_points}\n\n"
        f"لإذاعة رسالة:\n/send نص الرسالة"
    )

# ================== إذاعة ==================
@bot.message_handler(commands=["send"])
def broadcast(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    text = msg.text.replace("/send", "").strip()
    if not text:
        return

    for uid in users:
        try:
            bot.send_message(int(uid), text)
        except:
            pass

    bot.send_message(msg.chat.id, "✅ تم الإرسال")

# ================== تشغيل ==================
bot.infinity_polling()
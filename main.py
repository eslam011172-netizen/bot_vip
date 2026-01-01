import telebot
from telebot import types

# ====== الإعدادات ======
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
FORCE_CHANNEL = "@Muslim_vip1"
ADMIN_ID = 5083996619   # 🔴 حط ايدي حسابك هنا

bot = telebot.TeleBot(TOKEN)

# ====== تخزين مؤقت (لاحقًا نحوله JSON) ======
users = {}
admin_state = {}

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
    markup.add(types.InlineKeyboardButton("📢 اشترك في القناة",
        url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"))
    markup.add(types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
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
    users.setdefault(user_id, {"points": 0})

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

# ====== تحقق الاشتراك ======
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم الاشتراك")
        bot.send_message(call.message.chat.id, "✔️ تم التحقق\nاكتب /start")
    else:
        bot.answer_callback_query(call.id, "❌ لسه مش مشترك", show_alert=True)

# =======================
# 👑 لوحة الأدمن
# =======================

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "❌ غير مصرح")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ إضافة نقاط", "➖ خصم نقاط")
    markup.row("📢 رسالة جماعية", "📊 إحصائيات")
    markup.row("⬅️ رجوع")

    bot.send_message(message.chat.id, "👑 لوحة تحكم الأدمن", reply_markup=markup)

# ====== إضافة نقاط ======
@bot.message_handler(func=lambda m: m.text == "➕ إضافة نقاط")
def add_points(message):
    if message.from_user.id != ADMIN_ID: return
    admin_state["mode"] = "add"
    bot.send_message(message.chat.id, "✍️ ارسل:\nID عدد_النقاط")

# ====== خصم نقاط ======
@bot.message_handler(func=lambda m: m.text == "➖ خصم نقاط")
def remove_points(message):
    if message.from_user.id != ADMIN_ID: return
    admin_state["mode"] = "remove"
    bot.send_message(message.chat.id, "✍️ ارسل:\nID عدد_النقاط")

# ====== رسالة جماعية ======
@bot.message_handler(func=lambda m: m.text == "📢 رسالة جماعية")
def broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    admin_state["mode"] = "broadcast"
    bot.send_message(message.chat.id, "✍️ ارسل الرسالة")

# ====== إحصائيات ======
@bot.message_handler(func=lambda m: m.text == "📊 إحصائيات")
def stats(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_message(
        message.chat.id,
        f"👥 المستخدمين: {len(users)}\n💰 إجمالي النقاط: {sum(u['points'] for u in users.values())}"
    )

# ====== رجوع ======
@bot.message_handler(func=lambda m: m.text == "⬅️ رجوع")
def back(message):
    bot.send_message(message.chat.id, "⬅️ تم الرجوع", reply_markup=main_menu())

# ====== تنفيذ أوامر الأدمن ======
@bot.message_handler(func=lambda m: message.from_user.id == ADMIN_ID)
def admin_actions(message):
    if "mode" not in admin_state: return

    try:
        if admin_state["mode"] in ["add", "remove"]:
            uid, pts = map(int, message.text.split())
            users.setdefault(uid, {"points": 0})
            if admin_state["mode"] == "add":
                users[uid]["points"] += pts
                bot.send_message(message.chat.id, "✅ تم إضافة النقاط")
            else:
                users[uid]["points"] -= pts
                bot.send_message(message.chat.id, "➖ تم الخصم")

        elif admin_state["mode"] == "broadcast":
            sent = 0
            for uid in users:
                try:
                    bot.send_message(uid, message.text)
                    sent += 1
                except:
                    pass
            bot.send_message(message.chat.id, f"📢 تم الإرسال لـ {sent} مستخدم")

    except:
        bot.send_message(message.chat.id, "❌ صيغة خطأ")

    admin_state.clear()

# =======================
# أزرار المستخدم
# =======================

@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(message):
    points = users.get(message.from_user.id, {}).get("points", 0)
    bot.send_message(message.chat.id, f"💰 رصيدك: {points}")

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

# ====== تشغيل ======
print("Bot is running...")
bot.infinity_polling()

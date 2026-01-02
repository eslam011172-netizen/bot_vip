import telebot
from telebot import types
import json
import os

# ========== الإعدادات ==========
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
ADMIN_ID = 5083996619
FORCE_CHANNEL = "@Muslim_vip1"

DATA_FILE = "data.json"
FILES_DIR = "files"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ========== تهيئة ==========
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "products": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ========== أدوات ==========
def get_user(uid):
    uid = str(uid)
    if uid not in data["users"]:
        data["users"][uid] = {"points": 0, "invited": False}
        save_data()
    return data["users"][uid]

def is_subscribed(uid):
    try:
        m = bot.get_chat_member(FORCE_CHANNEL, uid)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

def force_markup():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"))
    kb.add(types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
    return kb

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 رصيدي", "🛒 المتجر")
    kb.row("👥 دعوة أصدقاء")
    return kb

def admin_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➕ إضافة نقاط", callback_data="admin_add"))
    kb.add(types.InlineKeyboardButton("➖ خصم نقاط", callback_data="admin_remove"))
    kb.add(types.InlineKeyboardButton("🛒 إضافة منتج", callback_data="admin_product"))
    return kb

# ========== /start ==========
@bot.message_handler(commands=["start"])
def start(m):
    uid = m.from_user.id

    if not is_subscribed(uid):
        bot.send_message(m.chat.id, "🚫 اشترك في القناة أولاً", reply_markup=force_markup())
        return

    user = get_user(uid)

    # إحالة
    if " " in m.text:
        ref = m.text.split()[1]
        if ref.isdigit() and ref != str(uid) and not user["invited"]:
            get_user(ref)["points"] += 5
            user["invited"] = True
            save_data()

    bot.send_message(m.chat.id, "👋 أهلاً بيك", reply_markup=main_menu())

    if uid == ADMIN_ID:
        bot.send_message(m.chat.id, "👑 لوحة الأدمن", reply_markup=admin_menu())

# ========== تحقق الاشتراك ==========
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_sub(c):
    if is_subscribed(c.from_user.id):
        bot.send_message(c.message.chat.id, "✅ تم التحقق\nاكتب /start")
    else:
        bot.answer_callback_query(c.id, "❌ لسه مش مشترك", show_alert=True)

# ========== المستخدم ==========
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(m):
    u = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 رصيدك: <b>{u['points']}</b> نقطة")

@bot.message_handler(func=lambda m: m.text == "👥 دعوة أصدقاء")
def invite(m):
    bot.send_message(
        m.chat.id,
        f"🔗 رابطك:\nhttps://t.me/{bot.get_me().username}?start={m.from_user.id}\n+5 نقاط لكل صديق"
    )

# ========== المتجر ==========
@bot.message_handler(func=lambda m: m.text == "🛒 المتجر")
def shop(m):
    if not data["products"]:
        bot.send_message(m.chat.id, "❌ لا يوجد منتجات حالياً")
        return

    kb = types.InlineKeyboardMarkup()
    for pid, p in data["products"].items():
        kb.add(types.InlineKeyboardButton(
            f"{p['name']} - {p['price']} نقطة",
            callback_data=f"buy_{pid}"
        ))
    bot.send_message(m.chat.id, "🛒 اختر منتج:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    u = get_user(c.from_user.id)
    p = data["products"].get(pid)

    if not p:
        bot.answer_callback_query(c.id, "❌ المنتج غير موجود", show_alert=True)
        return

    if u["points"] < p["price"]:
        bot.answer_callback_query(c.id, "❌ رصيد غير كافي", show_alert=True)
        return

    if not os.path.exists(p["file"]):
        bot.answer_callback_query(c.id, "❌ الملف غير موجود", show_alert=True)
        return

    u["points"] -= p["price"]
    save_data()

    bot.send_document(c.message.chat.id, open(p["file"], "rb"))
    bot.answer_callback_query(c.id, "✅ تم التسليم")

# ========== لوحة الأدمن ==========
admin_state = {}

@bot.callback_query_handler(func=lambda c: c.from_user.id == ADMIN_ID)
def admin_buttons(c):
    if c.data == "admin_add":
        admin_state[c.from_user.id] = "add"
        bot.send_message(c.message.chat.id, "أرسل:\nID\nعدد_النقاط")
    elif c.data == "admin_remove":
        admin_state[c.from_user.id] = "remove"
        bot.send_message(c.message.chat.id, "أرسل:\nID\nعدد_النقاط")
    elif c.data == "admin_product":
        admin_state[c.from_user.id] = "product"
        bot.send_message(c.message.chat.id, "أرسل:\nاسم|سعر|اسم_الملف")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_input(m):
    if m.from_user.id not in admin_state:
        return

    state = admin_state[m.from_user.id]
    text = m.text.strip()

    try:
        if state in ["add", "remove"]:
            uid, pts = text.split("\n")
            pts = int(pts)
            u = get_user(uid)
            u["points"] += pts if state == "add" else -pts
            if u["points"] < 0:
                u["points"] = 0
            save_data()
            bot.send_message(m.chat.id, "✅ تم التنفيذ")

        elif state == "product":
            parts = text.split("|")
            if len(parts) != 3:
                bot.send_message(m.chat.id, "❌ الصيغة غلط\nاستخدم:\nاسم|سعر|اسم_الملف")
                return
            name, price, file = parts
            pid = str(len(data["products"]) + 1)
            data["products"][pid] = {
                "name": name,
                "price": int(price),
                "file": f"{FILES_DIR}/{file}"
            }
            save_data()
            bot.send_message(m.chat.id, "✅ تم إضافة المنتج")

    except Exception as e:
        bot.send_message(m.chat.id, f"❌ خطأ:\n{e}")

    admin_state.pop(m.from_user.id, None)

# ========== تشغيل ==========
print("Bot running...")
bot.infinity_polling(skip_pending=True)

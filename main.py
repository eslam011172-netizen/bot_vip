import telebot
from telebot import types
import json, os

# ================== الإعدادات ==================
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
ADMIN_ID = 5083996619
FORCE_CHANNEL = "@Muslim_vip1"

DATA_FILE = "data.json"
FILES_DIR = "files"

bot = telebot.TeleBot(TOKEN)

# ================== تحميل / حفظ ==================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "products": {}, "vip": []}
    return json.load(open(DATA_FILE, "r", encoding="utf-8"))

def save_data():
    json.dump(data, open(DATA_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

data = load_data()

# ================== أدوات ==================
def is_subscribed(uid):
    try:
        m = bot.get_chat_member(FORCE_CHANNEL, uid)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

def get_user(uid):
    uid = str(uid)
    if uid not in data["users"]:
        data["users"][uid] = {"points": 0, "invited": False}
        save_data()
    return data["users"][uid]

# ================== الكيبورد ==================
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 رصيدي", "🛒 المتجر")
    kb.row("🎯 مهام CPA", "🎁 الهدايا")
    kb.row("⭐ VIP", "👥 دعوة أصدقاء")
    return kb

def admin_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("➕ نقاط", callback_data="add_points"),
        types.InlineKeyboardButton("➖ خصم", callback_data="remove_points")
    )
    kb.add(types.InlineKeyboardButton("🛒 إضافة منتج", callback_data="add_product"))
    kb.add(types.InlineKeyboardButton("⭐ إضافة VIP", callback_data="add_vip"))
    return kb

# ================== START ==================
@bot.message_handler(commands=["start"])
def start(m):
    uid = m.from_user.id

    if not is_subscribed(uid):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اشترك", url=f"https://t.me/{FORCE_CHANNEL[1:]}"))
        kb.add(types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
        bot.send_message(m.chat.id, "اشترك أولاً", reply_markup=kb)
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

# ================== تحقق اشتراك ==================
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_sub(c):
    if is_subscribed(c.from_user.id):
        bot.send_message(c.message.chat.id, "✅ تم\nاكتب /start")
    else:
        bot.answer_callback_query(c.id, "❌ لسه", show_alert=True)

# ================== المستخدم ==================
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(m):
    u = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 رصيدك: {u['points']} نقطة")

@bot.message_handler(func=lambda m: m.text == "👥 دعوة أصدقاء")
def invite(m):
    bot.send_message(
        m.chat.id,
        f"🔗 رابطك:\nhttps://t.me/{bot.get_me().username}?start={m.from_user.id}\n+5 نقاط"
    )

# ================== CPA ==================
@bot.message_handler(func=lambda m: m.text == "🎯 مهام CPA")
def cpa(m):
    bot.send_message(m.chat.id, "🎯 نفّذ المهام\n💰 استلم نقاط\n🛒 اصرفها في المتجر")

# ================== VIP ==================
@bot.message_handler(func=lambda m: m.text == "⭐ VIP")
def vip(m):
    if str(m.from_user.id) in data["vip"]:
        bot.send_message(m.chat.id, "⭐ أنت VIP")
    else:
        bot.send_message(m.chat.id, "⭐ اشترك VIP للحصول على خصومات")

# ================== المتجر ==================
@bot.message_handler(func=lambda m: m.text == "🛒 المتجر")
def shop(m):
    if not data["products"]:
        bot.send_message(m.chat.id, "❌ لا يوجد منتجات")
        return

    kb = types.InlineKeyboardMarkup()
    for pid, p in data["products"].items():
        kb.add(types.InlineKeyboardButton(
            f"{p['name']} - {p['price']}💰",
            callback_data=f"buy_{pid}"
        ))
    bot.send_message(m.chat.id, "🛒 اختر منتج:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    u = get_user(c.from_user.id)
    p = data["products"].get(pid)

    if not p:
        return

    if u["points"] < p["price"]:
        bot.answer_callback_query(c.id, "❌ رصيد غير كافي", show_alert=True)
        return

    u["points"] -= p["price"]
    save_data()

    bot.send_document(
        c.message.chat.id,
        open(p["file"], "rb"),
        caption="✅ تم التسليم تلقائيًا"
    )

    bot.answer_callback_query(c.id, "🟢 تمت")

# ================== لوحة الأدمن ==================
state = {}

@bot.callback_query_handler(func=lambda c: c.from_user.id == ADMIN_ID)
def admin(c):
    state[c.from_user.id] = c.data
    if c.data == "add_points":
        bot.send_message(c.message.chat.id, "ID\nنقاط")
    elif c.data == "remove_points":
        bot.send_message(c.message.chat.id, "ID\nنقاط")
    elif c.data == "add_product":
        bot.send_message(c.message.chat.id, "اسم|سعر|اسم_الملف")
    elif c.data == "add_vip":
        bot.send_message(c.message.chat.id, "ID")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_input(m):
    if m.from_user.id not in state:
        return

    s = state.pop(m.from_user.id)
    t = m.text.strip()

    if s in ["add_points", "remove_points"]:
        uid, pts = t.split("\n")
        u = get_user(uid)
        u["points"] += int(pts) if s == "add_points" else -int(pts)
        u["points"] = max(0, u["points"])
        save_data()
        bot.send_message(m.chat.id, "✅ تم")

    elif s == "add_product":
        name, price, file = t.split("|")
        pid = str(len(data["products"]) + 1)
        data["products"][pid] = {
            "name": name,
            "price": int(price),
            "file": f"{FILES_DIR}/{file}"
        }
        save_data()
        bot.send_message(m.chat.id, "🛒 أُضيف")

    elif s == "add_vip":
        data["vip"].append(t)
        save_data()
        bot.send_message(m.chat.id, "⭐ VIP أُضيف")

# ================== تشغيل ==================
print("Bot running...")
bot.infinity_polling(skip_pending=True)

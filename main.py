import telebot
from telebot import types
import json, os

# ========= الإعدادات =========
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
ADMIN_ID = 5083996619
FORCE_CHANNEL = "@Muslim_vip1"

DATA_FILE = "data.json"
FILES_DIR = "files"

bot = telebot.TeleBot(TOKEN)

# ========= تحميل / حفظ =========
def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "users": {},
            "categories": {
                "files": "📁 ملفات",
                "pubg": "🎮 PUBG",
                "vip": "⭐ VIP"
            },
            "products": {}
        }
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ========= أدوات =========
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
    kb.add(types.InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"))
    kb.add(types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
    return kb

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 رصيدي", "🛒 المتجر")
    kb.row("👥 دعوة أصدقاء")
    return kb

# ========= /start =========
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

# ========= تحقق =========
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check(c):
    if is_subscribed(c.from_user.id):
        bot.send_message(c.message.chat.id, "✅ تم التحقق\nاكتب /start")
    else:
        bot.answer_callback_query(c.id, "❌ لسه مش مشترك", show_alert=True)

# ========= المستخدم =========
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance(m):
    u = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 رصيدك: {u['points']} نقطة")

@bot.message_handler(func=lambda m: m.text == "👥 دعوة أصدقاء")
def invite(m):
    bot.send_message(
        m.chat.id,
        f"🔗 رابطك:\nhttps://t.me/{bot.get_me().username}?start={m.from_user.id}\n+5 نقاط لكل صديق"
    )

# ========= المتجر =========
@bot.message_handler(func=lambda m: m.text == "🛒 المتجر")
def shop(m):
    kb = types.InlineKeyboardMarkup()
    for k, v in data["categories"].items():
        kb.add(types.InlineKeyboardButton(v, callback_data=f"cat_{k}"))
    bot.send_message(m.chat.id, "🛒 اختر القسم:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
def show_cat(c):
    cat = c.data.split("_")[1]
    kb = types.InlineKeyboardMarkup()
    for pid, p in data["products"].items():
        if p["cat"] == cat:
            kb.add(types.InlineKeyboardButton(
                f"{p['name']} - {p['price']} نقطة",
                callback_data=f"buy_{pid}"
            ))
    bot.edit_message_text("📦 المنتجات:", c.message.chat.id, c.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(c):
    pid = c.data.split("_")[1]
    u = get_user(c.from_user.id)
    p = data["products"].get(pid)

    if not p:
        return

    if u["points"] < p["price"]:
        bot.answer_callback_query(c.id, "❌ نقاطك غير كافية", show_alert=True)
        return

    u["points"] -= p["price"]
    save_data()

    bot.send_document(c.message.chat.id, open(p["file"], "rb"), caption="✅ تم التسليم تلقائياً")
    bot.answer_callback_query(c.id, "🎉 تم الشراء")

# ========= لوحة الأدمن =========
def admin_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➕ إضافة نقاط", callback_data="add_points"))
    kb.add(types.InlineKeyboardButton("🛒 إضافة منتج", callback_data="add_product"))
    return kb

state = {}

@bot.callback_query_handler(func=lambda c: c.from_user.id == ADMIN_ID)
def admin_cb(c):
    if c.data == "add_points":
        state[c.from_user.id] = "points"
        bot.send_message(c.message.chat.id, "أرسل:\nID\nالنقاط")
    elif c.data == "add_product":
        state[c.from_user.id] = "product"
        bot.send_message(c.message.chat.id, "أرسل:\nالاسم|السعر|القسم|اسم_الملف")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_input(m):
    if m.from_user.id not in state:
        return

    s = state[m.from_user.id]
    t = m.text.strip()

    if s == "points":
        uid, pts = t.split("\n")
        get_user(uid)["points"] += int(pts)
        save_data()
        bot.send_message(m.chat.id, "✅ تم إضافة النقاط")

    elif s == "product":
        name, price, cat, file = t.split("|")
        pid = str(len(data["products"]) + 1)
        data["products"][pid] = {
            "name": name,
            "price": int(price),
            "cat": cat,
            "file": f"{FILES_DIR}/{file}"
        }
        save_data()
        bot.send_message(m.chat.id, "✅ تم إضافة المنتج")

    state.pop(m.from_user.id, None)

# ========= تشغيل =========
print("Bot running...")
bot.infinity_polling(skip_pending=True)

import telebot
from telebot import types
import json, os

# ========== الإعدادات ==========
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
ADMIN_ID = 5083996619
FORCE_CHANNEL = "@Muslim_vip1"

bot = telebot.TeleBot(TOKEN, threaded=True)

DATA_FILE = "data.json"
FILES_DIR = "files"

os.makedirs(FILES_DIR, exist_ok=True)

# ========== البيانات ==========
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "products": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

def get_user(uid):
    uid = str(uid)
    if uid not in data["users"]:
        data["users"][uid] = {"points": 0, "invited": False}
        save_data()
    return data["users"][uid]

# ========== اشتراك ==========
def is_subscribed(uid):
    try:
        m = bot.get_chat_member(FORCE_CHANNEL, uid)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

def force_markup():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 اشترك في القناة",
        url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"))
    kb.add(types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
    return kb

# ========== القوائم ==========
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 رصيدي", "🛒 المتجر")
    kb.row("🎁 الهدايا", "👥 دعوة أصدقاء")
    return kb

def admin_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➕ إضافة نقاط", callback_data="ap"))
    kb.add(types.InlineKeyboardButton("➖ خصم نقاط", callback_data="rp"))
    kb.add(types.InlineKeyboardButton("🛒 إضافة منتج", callback_data="addp"))
    return kb

# ========== START ==========
@bot.message_handler(commands=["start"])
def start(m):
    uid = m.from_user.id

    if not is_subscribed(uid):
        bot.send_message(m.chat.id, "🚫 اشترك أولاً", reply_markup=force_markup())
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

# ========== تحقق ==========
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check(c):
    if is_subscribed(c.from_user.id):
        bot.send_message(c.message.chat.id, "✅ تم التحقق\n/start")
    else:
        bot.answer_callback_query(c.id, "❌ لسه", show_alert=True)

# ========== المستخدم ==========
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

    if not p: return
    if u["points"] < p["price"]:
        bot.answer_callback_query(c.id, "❌ رصيدك غير كافي", show_alert=True)
        return

    u["points"] -= p["price"]
    save_data()
    bot.send_document(c.message.chat.id, open(p["file"], "rb"))
    bot.answer_callback_query(c.id, "✅ تم التسليم")

# ========== هدايا ==========
@bot.message_handler(func=lambda m: m.text == "🎁 الهدايا")
def gifts(m):
    bot.send_message(m.chat.id, "🎁 الهدايا متاحة داخل المتجر")

# ========== الأدمن ==========
state = {}

@bot.callback_query_handler(func=lambda c: c.from_user.id == ADMIN_ID)
def admin(c):
    if c.data in ["ap", "rp", "addp"]:
        state[c.from_user.id] = c.data
        if c.data == "addp":
            bot.send_message(c.message.chat.id, "اسم|سعر|اسم_الملف")
        else:
            bot.send_message(c.message.chat.id, "ID\nالنقاط")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_input(m):
    if m.from_user.id not in state: return
    s = state[m.from_user.id]

    if s in ["ap", "rp"]:
        uid, pts = m.text.split("\n")
        u = get_user(uid)
        if s == "ap":
            u["points"] += int(pts)
        else:
            u["points"] = max(0, u["points"] - int(pts))
        save_data()
        bot.send_message(m.chat.id, "✅ تم")

    elif s == "addp":
        name, price, file = m.text.split("|")
        pid = str(len(data["products"]) + 1)
        data["products"][pid] = {
            "name": name,
            "price": int(price),
            "file": f"{FILES_DIR}/{file}"
        }
        save_data()
        bot.send_message(m.chat.id, "✅ المنتج اتضاف")

    state.pop(m.from_user.id, None)

# ========== تشغيل ==========
print("Bot running...")
bot.infinity_polling(skip_pending=True)

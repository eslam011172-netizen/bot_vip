import telebot
from telebot import types
import json, os

# ================== CONFIG ==================
TOKEN = "PUT_YOUR_TOKEN"
FORCE_CHANNEL = "@Muslim_vip1"
ADMIN_ID = 5083996619
DATA_FILE = "users.json"

bot = telebot.TeleBot(TOKEN, threaded=True)

# ================== DATABASE ==================
def load():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

db = load()

def user(uid):
    uid = str(uid)
    if uid not in db:
        db[uid] = {
            "points": 0,
            "invites": 0,
            "vip": False
        }
        save(db)
    return db[uid]

# ================== FORCE SUB ==================
def subscribed(uid):
    try:
        m = bot.get_chat_member(FORCE_CHANNEL, uid)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

def sub_markup():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("📢 اشترك", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"))
    m.add(types.InlineKeyboardButton("✅ تحقق", callback_data="check"))
    return m

# ================== MENUS ==================
def main_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("💰 رصيدي", "👥 دعوة")
    m.row("🛒 المتجر", "💎 VIP")
    m.row("🎯 عروض CPA")
    return m

def shop_menu():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🎯 ملف Headshot (50)", callback_data="buy_headshot"))
    return m

# ================== START ==================
@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.from_user.id

    if not subscribed(uid):
        bot.send_message(msg.chat.id, "🚫 اشترك أولاً", reply_markup=sub_markup())
        return

    user(uid)

    # referral
    if len(msg.text.split()) > 1:
        ref = msg.text.split()[1]
        if ref != str(uid) and "ref" not in db[str(uid)]:
            db[str(uid)]["ref"] = True
            db[ref]["points"] += 5
            db[ref]["invites"] += 1
            save(db)

    bot.send_message(msg.chat.id, "👋 أهلاً بك", reply_markup=main_menu())

# ================== CHECK ==================
@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(c):
    if subscribed(c.from_user.id):
        bot.answer_callback_query(c.id, "✅ تم")
        bot.send_message(c.message.chat.id, "اكتب /start")
    else:
        bot.answer_callback_query(c.id, "❌ لسه", show_alert=True)

# ================== BALANCE ==================
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def bal(msg):
    u = user(msg.from_user.id)
    bot.send_message(msg.chat.id, f"💰 نقاطك: {u['points']}\n👥 دعواتك: {u['invites']}")

# ================== INVITE ==================
@bot.message_handler(func=lambda m: m.text == "👥 دعوة")
def invite(msg):
    bot.send_message(msg.chat.id,
        f"https://t.me/{bot.get_me().username}?start={msg.from_user.id}\n+5 نقاط")

# ================== SHOP ==================
@bot.message_handler(func=lambda m: m.text == "🛒 المتجر")
def shop(msg):
    bot.send_message(msg.chat.id, "🛒 اختر المنتج", reply_markup=shop_menu())

@bot.callback_query_handler(func=lambda c: c.data == "buy_headshot")
def buy(c):
    u = user(c.from_user.id)
    if u["points"] < 50:
        bot.answer_callback_query(c.id, "❌ نقاطك غير كافية", show_alert=True)
        return
    u["points"] -= 50
    save(db)
    bot.send_message(c.message.chat.id,
        "✅ تم الشراء\n📦 الرابط:\nhttps://example.com/headshot.zip")

# ================== VIP ==================
@bot.message_handler(func=lambda m: m.text == "💎 VIP")
def vip(msg):
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("💳 اشترك VIP", url="https://t.me/YourAdmin"))
    bot.send_message(msg.chat.id, "💎 مزايا VIP", reply_markup=m)

# ================== CPA ==================
@bot.message_handler(func=lambda m: m.text == "🎯 عروض CPA")
def cpa(msg):
    bot.send_message(msg.chat.id,
        "🎯 نفّذ العرض واربح نقاط:\nhttps://cpa-offer-link.com")

# ================== ADMIN ==================
@bot.message_handler(commands=["admin"])
def admin(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.send_message(msg.chat.id, "👑 لوحة الأدمن\n/users.json")

# ================== RUN ==================
print("Bot Running...")
bot.infinity_polling(skip_pending=True)

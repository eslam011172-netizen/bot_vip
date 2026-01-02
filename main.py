import telebot
from telebot import types
import json, os, time

# ================== الإعدادات ==================
TOKEN = "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"
ADMIN_ID = 5083996619
FORCE_CHANNEL = "@Muslim_vip1"

DATA_FILE = "data.json"
FILES_DIR = "files"

bot = telebot.TeleBot(TOKEN)

# ================== تحميل / حفظ ==================
def load():
    if not os.path.exists(DATA_FILE):
        return {
            "users": {},
            "products": {},
            "vip": [],
            "coupons": {},
            "logs": [],
            "stats": {"users":0,"sales":0}
        }
    return json.load(open(DATA_FILE,"r",encoding="utf-8"))

def save():
    json.dump(data,open(DATA_FILE,"w",encoding="utf-8"),ensure_ascii=False,indent=2)

data = load()

# ================== أدوات ==================
def subscribed(uid):
    try:
        m = bot.get_chat_member(FORCE_CHANNEL, uid)
        return m.status in ["member","administrator","creator"]
    except:
        return False

def get_user(uid):
    uid=str(uid)
    if uid not in data["users"]:
        data["users"][uid]={
            "points":0,
            "vip":False,
            "ref":False,
            "last":0
        }
        data["stats"]["users"]+=1
        save()
    return data["users"][uid]

def log(uid,action):
    data["logs"].append({
        "user":uid,
        "action":action,
        "time":int(time.time())
    })
    save()

# ================== القوائم ==================
def main_menu():
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 رصيدي","🛒 المتجر")
    kb.row("🎯 CPA","🎟 كوبون")
    kb.row("⭐ VIP","👥 دعوة")
    return kb

def admin_menu():
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➕ شحن",callback_data="charge"))
    kb.add(types.InlineKeyboardButton("📦 منتج",callback_data="product"))
    kb.add(types.InlineKeyboardButton("📩 بث",callback_data="broadcast"))
    kb.add(types.InlineKeyboardButton("📊 إحصائيات",callback_data="stats"))
    return kb

# ================== START ==================
@bot.message_handler(commands=["start"])
def start(m):
    uid=m.from_user.id
    if not subscribed(uid):
        kb=types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اشترك",url=f"https://t.me/{FORCE_CHANNEL[1:]}"))
        kb.add(types.InlineKeyboardButton("✅ تحقق",callback_data="check"))
        bot.send_message(m.chat.id,"اشترك أولاً",reply_markup=kb)
        return

    u=get_user(uid)

    if " " in m.text:
        ref=m.text.split()[1]
        if ref.isdigit() and ref!=str(uid) and not u["ref"]:
            get_user(ref)["points"]+=10
            u["ref"]=True
            save()
            bot.send_message(ref,"🎉 كسبت 10 نقاط إحالة")

    bot.send_message(m.chat.id,"👋 أهلاً",reply_markup=main_menu())

    if uid==ADMIN_ID:
        bot.send_message(m.chat.id,"👑 لوحة الأدمن",reply_markup=admin_menu())

# ================== رصيد ==================
@bot.message_handler(func=lambda m:m.text=="💰 رصيدي")
def bal(m):
    u=get_user(m.from_user.id)
    bot.send_message(m.chat.id,f"💰 {u['points']} نقطة")

# ================== CPA ==================
@bot.message_handler(func=lambda m:m.text=="🎯 CPA")
def cpa(m):
    bot.send_message(m.chat.id,"🎯 كل دعوة = 10 نقاط\n💰 بيع = عمولة")

# ================== كوبون ==================
@bot.message_handler(func=lambda m:m.text=="🎟 كوبون")
def coupon(m):
    bot.send_message(m.chat.id,"📥 أرسل كود الخصم")

@bot.message_handler(func=lambda m:m.text.startswith("CP-"))
def use_coupon(m):
    c=m.text
    u=get_user(m.from_user.id)
    if c in data["coupons"]:
        u["points"]+=data["coupons"][c]
        del data["coupons"][c]
        save()
        bot.send_message(m.chat.id,"✅ تم الخصم")
    else:
        bot.send_message(m.chat.id,"❌ غير صالح")

# ================== VIP ==================
@bot.message_handler(func=lambda m:m.text=="⭐ VIP")
def vip(m):
    u=get_user(m.from_user.id)
    if u["vip"]:
        bot.send_message(m.chat.id,"⭐ انت VIP")
    elif u["points"]>=100:
        u["points"]-=100
        u["vip"]=True
        data["vip"].append(str(m.from_user.id))
        save()
        bot.send_message(m.chat.id,"🎉 تم التفعيل")
    else:
        bot.send_message(m.chat.id,"❌ 100 نقطة")

# ================== المتجر ==================
@bot.message_handler(func=lambda m:m.text=="🛒 المتجر")
def shop(m):
    kb=types.InlineKeyboardMarkup()
    for pid,p in data["products"].items():
        if p.get("vip") and not get_user(m.from_user.id)["vip"]:
            continue
        if p.get("end") and time.time()>p["end"]:
            continue
        kb.add(types.InlineKeyboardButton(
            f"{p['name']} - {p['price']}💰",
            callback_data=f"buy_{pid}"
        ))
    bot.send_message(m.chat.id,"🛒 المنتجات:",reply_markup=kb)

@bot.callback_query_handler(func=lambda c:c.data.startswith("buy_"))
def buy(c):
    pid=c.data.split("_")[1]
    u=get_user(c.from_user.id)
    p=data["products"].get(pid)
    if not p: return
    if u["points"]<p["price"]:
        bot.answer_callback_query(c.id,"❌ رصيدك قليل",show_alert=True)
        return
    u["points"]-=p["price"]
    data["stats"]["sales"]+=1
    save()
    log(c.from_user.id,f"شراء {p['name']}")
    bot.send_document(c.message.chat.id,open(p["file"],"rb"))
    bot.send_message(c.message.chat.id,"🔔 تم الشراء")

# ================== الأدمن ==================
state={}

@bot.callback_query_handler(func=lambda c:c.from_user.id==ADMIN_ID)
def adm(c):
    state[c.from_user.id]=c.data
    if c.data=="charge":
        bot.send_message(c.message.chat.id,"ID\nنقاط")
    if c.data=="product":
        bot.send_message(c.message.chat.id,"اسم|سعر|ملف|vip(0/1)|ثواني")
    if c.data=="broadcast":
        bot.send_message(c.message.chat.id,"📩 الرسالة")
    if c.data=="stats":
        s=data["stats"]
        bot.send_message(c.message.chat.id,
            f"👥 {s['users']}\n💰 مبيعات {s['sales']}")

@bot.message_handler(func=lambda m:m.from_user.id==ADMIN_ID)
def adm_in(m):
    if m.from_user.id not in state: return
    s=state.pop(m.from_user.id)
    t=m.text

    if s=="charge":
        uid,pts=t.split("\n")
        get_user(uid)["points"]+=int(pts)
        save()
        bot.send_message(uid,"🔔 تم شحن نقاط")
        bot.send_message(m.chat.id,"✅")

    if s=="product":
        name,price,file,vip,sec=t.split("|")
        pid=str(len(data["products"])+1)
        data["products"][pid]={
            "name":name,
            "price":int(price),
            "file":f"{FILES_DIR}/{file}",
            "vip":vip=="1",
            "end":time.time()+int(sec) if sec!="0" else None
        }
        save()
        bot.send_message(m.chat.id,"📦 تم")

    if s=="broadcast":
        for uid in data["users"]:
            try: bot.send_message(uid,t)
            except: pass
        bot.send_message(m.chat.id,"📩 تم البث")

# ================== تشغيل ==================
print("Bot running...")
bot.infinity_polling(skip_pending=True)

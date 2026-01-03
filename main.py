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
            "last_collect":0
        }
        data["stats"]["users"]+=1
        save()
    return data["users"][uid]

def log(uid,action):
    data["logs"].append({
        "user":str(uid),
        "action":action,
        "time":int(time.time())
    })
    save()

# ================== القوائم ==================
def main_menu():
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🎁 جمع نقاط","💰 رصيدي")
    kb.row("🛒 المتجر","🎮 شحن PUBG")
    kb.row("🔥 ملفات VIP","👥 دعوة")
    kb.row("⭐ VIP","🧾 سجلّي")
    return kb

def admin_menu():
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➕ شحن نقاط",callback_data="charge"))
    kb.add(types.InlineKeyboardButton("📦 إضافة منتج",callback_data="product"))
    kb.add(types.InlineKeyboardButton("📩 بث رسالة",callback_data="broadcast"))
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
        bot.send_message(m.chat.id,"🚫 اشترك في القناة أولاً",reply_markup=kb)
        return

    u=get_user(uid)

    if " " in m.text:
        ref=m.text.split()[1]
        if ref.isdigit() and ref!=str(uid) and not u["ref"]:
            get_user(ref)["points"]+=10
            u["ref"]=True
            log(ref,"دعوة مستخدم +10")
            save()

    bot.send_message(
        m.chat.id,
        f"""👋 أهلاً بيك  
💰 رصيدك: {u['points']} نقطة

🎁 اجمع نقاط واشتري:
• ملفات هيدشوت VIP
• شحن PUBG UC
• مميزات خاصة

⚠️ كل الشراء بالنقاط فقط""",
        reply_markup=main_menu()
    )

    if uid==ADMIN_ID:
        bot.send_message(m.chat.id,"👑 لوحة الأدمن",reply_markup=admin_menu())

# ================== جمع نقاط ==================
@bot.message_handler(func=lambda m:m.text=="🎁 جمع نقاط")
def collect(m):
    u=get_user(m.from_user.id)
    now=int(time.time())
    if now - u["last_collect"] < 86400:
        left = 86400 - (now - u["last_collect"])
        h = left//3600
        bot.send_message(m.chat.id,f"⏳ حاول بعد {h} ساعة")
        return

    u["points"]+=5
    u["last_collect"]=now
    log(m.from_user.id,"جمع نقاط يومي +5")
    save()
    bot.send_message(m.chat.id,"🎉 كسبت 5 نقاط")

# ================== رصيد ==================
@bot.message_handler(func=lambda m:m.text=="💰 رصيدي")
def bal(m):
    u=get_user(m.from_user.id)
    bot.send_message(m.chat.id,f"💰 رصيدك: {u['points']} نقطة")

# ================== سجل ==================
@bot.message_handler(func=lambda m:m.text=="🧾 سجلّي")
def mylog(m):
    uid=str(m.from_user.id)
    logs=[l for l in data["logs"] if l["user"]==uid][-5:]
    if not logs:
        bot.send_message(m.chat.id,"📭 لا يوجد عمليات")
        return
    text="🧾 آخر عملياتك:\n\n"
    for l in logs:
        text+=f"• {l['action']}\n"
    bot.send_message(m.chat.id,text)

# ================== دعوة ==================
@bot.message_handler(func=lambda m:m.text=="👥 دعوة")
def invite(m):
    bot.send_message(
        m.chat.id,
        f"🔗 رابطك:\nhttps://t.me/{bot.get_me().username}?start={m.from_user.id}\n🎁 +10 نقاط"
    )

# ================== VIP ==================
@bot.message_handler(func=lambda m:m.text=="⭐ VIP")
def vip(m):
    u=get_user(m.from_user.id)
    if u["vip"]:
        bot.send_message(m.chat.id,"⭐ أنت VIP بالفعل")
    elif u["points"]>=100:
        u["points"]-=100
        u["vip"]=True
        log(m.from_user.id,"تفعيل VIP")
        save()
        bot.send_message(m.chat.id,"🎉 تم تفعيل VIP")
    else:
        bot.send_message(m.chat.id,"❌ تحتاج 100 نقطة")

# ================== المتجر ==================
@bot.message_handler(func=lambda m:m.text=="🛒 المتجر")
def shop(m):
    kb=types.InlineKeyboardMarkup()
    count=0
    for pid,p in data["products"].items():
        if p.get("vip") and not get_user(m.from_user.id)["vip"]:
            continue
        kb.add(types.InlineKeyboardButton(
            f"{p['name']} - {p['price']}💰",
            callback_data=f"buy_{pid}"
        ))
        count+=1

    if count==0:
        bot.send_message(m.chat.id,"📦 لا توجد منتجات حالياً\n🎁 اجمع نقاط وانتظر الجديد")
        return

    bot.send_message(m.chat.id,"🛒 اختر منتج:",reply_markup=kb)

# ================== PUBG ==================
@bot.message_handler(func=lambda m:m.text=="🎮 شحن PUBG")
def pubg(m):
    kb=types.InlineKeyboardMarkup()
    count=0
    for pid,p in data["products"].items():
        if p.get("cat")=="pubg":
            kb.add(types.InlineKeyboardButton(
                f"{p['name']} - {p['price']}💰",
                callback_data=f"buy_{pid}"
            ))
            count+=1

    if count==0:
        bot.send_message(m.chat.id,"🎮 لا يوجد شحن حالياً")
        return

    bot.send_message(m.chat.id,"🎮 شحن PUBG:",reply_markup=kb)

# ================== ملفات VIP ==================
@bot.message_handler(func=lambda m:m.text=="🔥 ملفات VIP")
def vip_files(m):
    if not get_user(m.from_user.id)["vip"]:
        bot.send_message(m.chat.id,"🔒 القسم خاص بـ VIP")
        return
    kb=types.InlineKeyboardMarkup()
    count=0
    for pid,p in data["products"].items():
        if p.get("vip"):
            kb.add(types.InlineKeyboardButton(
                f"{p['name']} - {p['price']}💰",
                callback_data=f"buy_{pid}"
            ))
            count+=1

    if count==0:
        bot.send_message(m.chat.id,"🔥 لا توجد ملفات حالياً")
        return

    bot.send_message(m.chat.id,"🔥 ملفات VIP:",reply_markup=kb)

# ================== شراء ==================
@bot.callback_query_handler(func=lambda c:c.data.startswith("buy_"))
def buy(c):
    pid=c.data.split("_")[1]
    u=get_user(c.from_user.id)
    p=data["products"].get(pid)
    if not p: return
    if u["points"]<p["price"]:
        bot.answer_callback_query(c.id,"❌ رصيدك غير كافي",show_alert=True)
        return
    u["points"]-=p["price"]
    data["stats"]["sales"]+=1
    log(c.from_user.id,f"شراء {p['name']}")
    save()
    bot.send_document(c.message.chat.id,open(p["file"],"rb"))
    bot.send_message(c.message.chat.id,"✅ تم التسليم")

# ================== الأدمن ==================
state={}

@bot.callback_query_handler(func=lambda c:c.from_user.id==ADMIN_ID)
def adm(c):
    state[c.from_user.id]=c.data
    if c.data=="charge":
        bot.send_message(c.message.chat.id,"ID\nنقاط")
    if c.data=="product":
        bot.send_message(c.message.chat.id,"اسم|سعر|ملف|vip(0/1)|cat(pubg/vip/normal)")
    if c.data=="broadcast":
        bot.send_message(c.message.chat.id,"📩 الرسالة")
    if c.data=="stats":
        s=data["stats"]
        bot.send_message(c.message.chat.id,f"👥 {s['users']}\n💰 {s['sales']} عملية")

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

    if s=="product":
        name,price,file,vip,cat=t.split("|")
        pid=str(len(data["products"])+1)
        data["products"][pid]={
            "name":name,
            "price":int(price),
            "file":f"{FILES_DIR}/{file}",
            "vip":vip=="1",
            "cat":cat
        }
        save()
        bot.send_message(m.chat.id,"📦 تم إضافة المنتج")

    if s=="broadcast":
        for uid in data["users"]:
            try: bot.send_message(uid,t)
            except: pass
        bot.send_message(m.chat.id,"📩 تم البث")

# ================== تشغيل ==================
print("Bot running...")
bot.infinity_polling(skip_pending=True)

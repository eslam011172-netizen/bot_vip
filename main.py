import os
import telebot

from handlers.start import start
from handlers.balance import balance_handler
from handlers.invite import invite_handler
from handlers.admin import admin_handler

# ========== الإعدادات ==========
TOKEN = os.getenv("5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g") or "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# ========== ربط الهاندلرز ==========
@bot.message_handler(commands=["start"])
def start_cmd(message):
    start(message, bot)


balance_handler(bot)
invite_handler(bot)
admin_handler(bot)


# ========== تشغيل البوت ==========
print("🤖 Bot is running...")
bot.infinity_polling(skip_pending=True)
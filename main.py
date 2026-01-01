import telebot
import os

from handlers.start import start_handler

# 🔑 التوكن (يفضل يكون ENV لكن حاليًا مباشر)
TOKEN = os.getenv("BOT_TOKEN", "5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# ===== START =====
@bot.message_handler(commands=['start'])
def start_cmd(message):
    start_handler(bot, message)


# ===== RUN =====
print("Bot is running...")
bot.infinity_polling()

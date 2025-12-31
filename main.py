import telebot
import time
import os

TOKEN = os.environ.get("5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g")

if not TOKEN:
    print("❌ BOT_TOKEN not found")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def reply(message):
    bot.reply_to(message, "✅ البوت شغال")

print("🤖 Bot started")

while True:
    try:
        bot.polling(non_stop=True, interval=3)
    except Exception as e:
        print("Error:", e)
        time.sleep(5)

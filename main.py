import telebot
import os
import time

TOKEN = os.getenv("5644960695:AAGx5jysi7ZYFFQw14LNIlcS2bpRCXWAg6g")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "✅ البوت شغال تمام على Koyeb!\n\nاكتب أي حاجة وهيترد عليك"
    )

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, f"📩 وصلني: {message.text}")

print("🤖 Bot is running...")

while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print("❌ Error:", e)
        time.sleep(5)

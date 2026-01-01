Enterfrom telebot import types
from utils.users import add_user

def start_handler(bot, message):
    add_user(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("رصيدي 💰", "دعوة أصدقاء 👥")

    bot.send_message(
        message.chat.id,
        "أهلاً بيك 👋",
        reply_markup=markup
    )

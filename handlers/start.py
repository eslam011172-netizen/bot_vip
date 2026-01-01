from telebot import types
from utils.users import add_user
from utils.force_subscribe import check_sub
from config import FORCE_CHANNEL

def start_handler(bot, message):
    user_id = message.from_user.id

    if not check_sub(bot, user_id, FORCE_CHANNEL):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"),
            types.InlineKeyboardButton("✅ تحقق", callback_data="check_sub")
        )
        bot.send_message(
            message.chat.id,
            "🚫 لازم تشترك في القناة الأول",
            reply_markup=markup
        )
        return

    add_user(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("رصيدي 💰", "دعوة أصدقاء 👥")

    bot.send_message(
        message.chat.id,
        "أهلاً بيك 👋",
        reply_markup=markup
    )

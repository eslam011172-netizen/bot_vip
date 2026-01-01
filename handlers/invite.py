from telebot import types
from utils.users import get_user, add_user
from utils.referrals import add_referral


def invite_handler(bot):
    @bot.message_handler(commands=['invite'])
    def invite(message):
        user_id = message.from_user.id
        user = get_user(user_id)

        if not user:
            add_user(user_id)

        bot_username = bot.get_me().username
        invite_link = f"https://t.me/{bot_username}?start={user_id}"

        text = (
            "🎁 رابط الدعوة الخاص بيك:\n\n"
            f"{invite_link}\n\n"
            "كل شخص يدخل من الرابط ده هتكسب عليه 🎉"
        )

        bot.send_message(message.chat.id, text)

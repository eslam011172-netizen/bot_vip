from utils.users import get_user, add_user


def balance_handler(bot):
    @bot.message_handler(commands=['balance'])
    def balance(message):
        user_id = message.from_user.id
        user = get_user(user_id)

        if not user:
            add_user(user_id)
            balance = 0
        else:
            balance = user.get("balance", 0)

        text = f"💰 رصيدك الحالي: {balance}"
        bot.send_message(message.chat.id, text)

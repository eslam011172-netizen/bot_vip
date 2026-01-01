from utils.users import get_user, add_user, add_balance

ADMIN_ID = 5083996619  # ← حط ID بتاعك هنا


def admin_handler(bot):
    @bot.message_handler(commands=['admin'])
    def admin_panel(message):
        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.chat.id, "❌ الأمر ده للأدمن فقط")
            return

        bot.send_message(
            message.chat.id,
            "⚙️ لوحة تحكم الأدمن\n\n"
            "/addbalance user_id amount\n"
            "مثال:\n"
            "/addbalance 123456789 50"
        )

    @bot.message_handler(commands=['addbalance'])
    def add_balance_cmd(message):
        if message.from_user.id != ADMIN_ID:
            return

        try:
            _, user_id, amount = message.text.split()
            user_id = int(user_id)
            amount = int(amount)

            if not get_user(user_id):
                add_user(user_id)

            add_balance(user_id, amount)

            bot.send_message(
                message.chat.id,
                f"✅ تم إضافة {amount} نقطة للمستخدم {user_id}"
            )

        except Exception:
            bot.send_message(
                message.chat.id,
                "❌ استخدم الأمر كده:\n/addbalance user_id amount"
            )

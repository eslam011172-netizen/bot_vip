from utils.users import get_user, add_user, add_balance


def add_referral(referrer_id, new_user_id):
    referrer = get_user(referrer_id)

    if not referrer:
        add_user(referrer_id)

    # مكافأة الدعوة
    add_balance(referrer_id, 5)

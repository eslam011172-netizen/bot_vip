import json
import os

DATA_FILE = "data/users.json"


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))


def add_user(user_id, username=None):
    users = load_users()
    users[str(user_id)] = {
        "balance": 0,
        "username": username,
        "invites": 0
    }
    save_users(users)


def add_balance(user_id, amount):
    users = load_users()
    users[str(user_id)]["balance"] += amount
    save_users(users)

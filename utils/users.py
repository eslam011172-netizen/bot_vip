import json
import os
from datetime import datetime

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
    uid = str(user_id)

    if uid not in users:
        users[uid] = {
            "points": 0,
            "invites": 0,
            "joined": datetime.utcnow().isoformat()
        }
        save_users(users)

    return users[uid]


def add_points(user_id, amount):
    users = load_users()
    uid = str(user_id)
    users.setdefault(uid, {
        "points": 0,
        "invites": 0
    })
    users[uid]["points"] += amount
    save_users(users)


def add_invite(user_id):
    users = load_users()
    uid = str(user_id)
    users.setdefault(uid, {
        "points": 0,
        "invites": 0
    })
    users[uid]["invites"] += 1
    save_users(users)

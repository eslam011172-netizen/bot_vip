import json
import threading

LOCK = threading.Lock()
FILE = "data/users.json"

def load_users():
    with open(FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with LOCK:
        with open(FILE, "w") as f:
            json.dump(data, f, indent=2)

def add_user(user_id):
    data = load_users()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {
            "points": 0,
            "invites": 0
        }
        save_users(data)

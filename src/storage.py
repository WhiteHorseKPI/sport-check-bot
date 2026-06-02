import json
from constants import Path, Key

def load_data():
    if Path.DATA_FILE.exists():
        with open(Path.DATA_FILE) as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(Path.DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def increment_all(user_ids):
    data = load_data()
    sick = set(data.get(Key.SICK, []))
    for user_id in user_ids:
        if user_id in sick:
            continue  # frozen counter while on sick leave
        data[user_id] = data.get(user_id, 0) + 1
    save_data(data)

def reset_counter(user_id):
    data = load_data()
    data[user_id] = 0
    save_data(data)
    return data

def get_sick():
    return list(load_data().get(Key.SICK, []))

def is_sick(user_id):
    return user_id in load_data().get(Key.SICK, [])

def mark_sick(user_id):
    data = load_data()
    sick = set(data.get(Key.SICK, []))
    sick.add(user_id)
    data[Key.SICK] = sorted(sick)
    save_data(data)

def clear_sick(user_id):
    data = load_data()
    sick = set(data.get(Key.SICK, []))
    sick.discard(user_id)
    data[Key.SICK] = sorted(sick)
    save_data(data)

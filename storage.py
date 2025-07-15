import json
from constants import Path

def load_data():
    if Path.DATA_FILE.exists():
        with open(Path.DATA_FILE) as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(Path.DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def increment_all():
    data = load_data()
    for name in data.keys():
        if name == "_pinned":
            continue
        data[name] = data.get(name, 0) + 1
    save_data(data)

def reset_counter(user_id):
    data = load_data()
    if user_id in data:
        data[user_id] = 0
        save_data(data)
    return data

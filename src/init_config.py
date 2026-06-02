"""Generate config.yaml from recent Telegram updates.

Usage:
    1. Create the bot with @BotFather and add it to your group.
    2. Disable privacy mode for the bot (@BotFather -> /setprivacy -> Disable)
       so it can read group messages.
    3. Ask every participant to send any message in the group (e.g. /done).
    4. Run:
           SPORT_BOT_TOKEN=YOUR_BOT_TOKEN python init_config.py

The script reads the bot's pending updates, extracts the group chat id and the
id/name of everyone who wrote a message, and writes config.yaml.
"""

import json
import os
import urllib.request

import yaml

from constants import Key, Path

TOKEN = os.environ[Key.TOKEN]
API_URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"


def fetch_updates():
    with urllib.request.urlopen(API_URL) as response:
        payload = json.load(response)
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API error: {payload}")
    return payload["result"]


def collect_config(updates):
    chat_id = None
    users = {}
    for update in updates:
        message = update.get("message") or update.get("edited_message")
        if not message:
            continue
        chat = message["chat"]
        if chat["type"] in ("group", "supergroup"):
            chat_id = chat["id"]
        sender = message.get("from")
        if sender and not sender.get("is_bot"):
            user_id = str(sender["id"])
            name = sender.get("first_name") or sender.get("username") or user_id
            users[user_id] = {Key.USER_NAME: name, Key.USER_ID: user_id}
    return chat_id, list(users.values())


def main():
    updates = fetch_updates()
    if not updates:
        print("No updates found. Make sure the bot is in the group and that "
              "participants have sent a message recently, then try again.")
        return

    chat_id, users = collect_config(updates)
    if chat_id is None:
        print("No group chat found in updates. Add the bot to your group and "
              "send a message there.")
        return

    config = {Key.CHAT_ID: chat_id, Key.USERS: users}
    with open(Path.CONFIG_FILE, "w") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"Wrote {Path.CONFIG_FILE} with chat_id={chat_id} and "
          f"{len(users)} user(s):")
    for user in users:
        print(f"  - {user[Key.USER_NAME]} ({user[Key.USER_ID]})")


if __name__ == "__main__":
    main()

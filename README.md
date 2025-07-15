
---

# 🏋️‍♂️ Telegram Sports Discipline Bot

This Telegram bot is designed to **track how many consecutive days each group member has missed sports training**. It helps maintain discipline by encouraging daily participation and showing everyone’s progress (or lack of it 😅)

---

## ✅ Features

* ⏰ **Daily Message at 06:00** with each participant’s name and number of missed days
* 📌 The daily message is automatically **pinned** in the chat for visibility
* 🧮 The counter for each person increases by 1 each day
* ✅ Participants can use the `/done` command to **reset their counter to 0** when they’ve completed their daily training
* 🔄 The bot automatically **edits the last pinned message** after each `/done`

---

## 📁 Project Structure

```
telegram-sports-bot/
├── bot.py              # Main bot logic + scheduler
├── storage.py          # Simple persistent storage
├── config.yaml         # Participant names and chat ID
├── data.json           # Auto-generated daily counters
├── bot.log             # Auto-generated log file
└── README.md           # This file
```

---

## 🔧 Setup Instructions

### 1. Install Requirements

Tested on Python 3.12 only
```bash
python3.12 -m pip install python-telegram-bot==20.7 apscheduler pyyaml
```

### 2. Create `config.yaml`

```yaml
chat_id: -1001234567890  # Replace with your actual group chat ID
users:
  - {"name": "Bob", "id": "0123456789"}
  - {"name": "Alice", "id": "9876543210"}
```

> 💡 Use `@userinfobot` in Telegram to get the `chat_id` of your group

### 3. Run the Bot

```bash
SPORT_BOT_TOKEN=YOUR_BOT_TOKEN python3.12 bot.py
```

---

## 💬 Usage

* Every day at 06:00, the bot sends and pins a message like:

  ```
  📅 Daily Report:
    - Alice: 3
    - Bob: 0
    - Charlie: 1
  ```

* When Bob finishes his training, he types:

  ```
  /done
  ```

* The bot resets Bob’s counter to 0 and edits the pinned message

---

## 🧠 How It Works

* The bot maintains a simple JSON file (`data.json`) with counters for each participant
* Every day, the counter for each user increases by 1
* When a participant submits `/done`, their counter is reset to 0
* The updated report is edited in-place in the pinned message

---

## 🚀 Future Ideas

* Add a leaderboard of consistency
* Send private reminders to people whose counter is > 3
* Add commands to set pause due to illness

---

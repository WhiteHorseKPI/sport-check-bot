
---

# 🏋️‍♂️ Telegram Sports Discipline Bot

This Telegram bot is designed to **track how many consecutive days each group member has missed sports training**. It helps maintain discipline by encouraging daily participation and showing everyone’s progress (or lack of it 😅)

---

## ✅ Features

* ⏰ **Daily Message at 06:00** with each participant’s name and number of missed days
* 📌 The daily message is automatically **pinned** in the chat for visibility
* 🧮 The counter for each person increases by 1 each day
* 🔄 The bot automatically **edits the last pinned message** after each command

### Commands

| Command | What it does |
|---------|--------------|
| `/done` | Mark today's training as done — resets your counter to `0` |
| `/daily_stats` | Show the current report on demand (without waiting for 06:00) |
| `/sick_leave` | Go on sick leave — your counter is **frozen** (stops increasing) and shown as 🤒 in the report. Each morning the bot asks whether you're still sick. |
| `/back_to_business` | End sick leave and reset your counter to `0` |

---

## 📁 Project Structure

```
sport-check-bot/
├── src/                        # Application code
│   ├── bot.py                  # Main bot logic + scheduler
│   ├── storage.py              # Simple persistent storage
│   ├── constants.py            # Paths and config keys
│   └── init_config.py          # Helper to auto-generate config.yaml
├── deploy/                     # Raspberry Pi / systemd hosting
│   ├── deploy.sh               # Push to the Pi from your Mac
│   ├── install.sh              # Set up venv + service on the Pi
│   ├── sport-check-bot.service # systemd unit
│   ├── bot.env.example         # Token file template
│   └── README.md               # Deployment guide
├── requirements.txt            # Python dependencies
├── config.yaml                 # Participant names and chat ID
├── data.json                   # Auto-generated daily counters
├── bot.log                     # Auto-generated log file
└── README.md                   # This file
```

> Runtime files (`config.yaml`, `data.json`, `bot.log`) are created in the
> project root, alongside `src/`.

---

## 🔧 Setup Instructions

### 1. Prepare a Virtual Environment

Requires Python 3.12+ (works on 3.13). Creating an isolated virtual environment keeps the bot's dependencies separate from your system packages.

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows (PowerShell / cmd)
```

> 💡 Once activated, your shell prompt is prefixed with `(venv)`. Run `deactivate` to exit the environment.

### 2. Install Requirements

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

### 3. Create `config.yaml`

The config file looks like this:

```yaml
chat_id: -1001234567890  # Your group chat ID
users:
  - {"name": "Bob", "id": "0123456789"}
  - {"name": "Alice", "id": "9876543210"}
```

#### Generate it automatically (recommended)

Instead of hunting down the chat ID and every user ID by hand, let the
`init_config.py` script build `config.yaml` for you:

1. Create the bot with [@BotFather](https://t.me/BotFather) and add it to your group.
2. Disable privacy mode so the bot can read group messages:
   `@BotFather` → `/setprivacy` → select your bot → **Disable**.
3. Ask every participant to send any message in the group (e.g. `/done`).
4. Run the script with your bot token:

   ```bash
   SPORT_BOT_TOKEN=YOUR_BOT_TOKEN python src/init_config.py
   ```

The script reads the bot's pending updates, extracts the group `chat_id` and the
`id`/`name` of everyone who posted a message, and writes `config.yaml`. Re-run it
any time new members join (after they've sent a message).

#### Or fill it in manually

> 💡 Use `@userinfobot` in Telegram to get the `chat_id` of your group, then add each participant's name and id by hand.

### 4. Run the Bot

With the virtual environment activated:

```bash
SPORT_BOT_TOKEN=YOUR_BOT_TOKEN python src/bot.py
```

---

## 📡 Deploy to a Raspberry Pi

To run the bot 24/7 on a Raspberry Pi under `systemd`, see
[`deploy/README.md`](deploy/README.md). In short, from your Mac:

```bash
deploy/deploy.sh washer@<pi-ip>
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

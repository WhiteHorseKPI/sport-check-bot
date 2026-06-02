import pathlib
from datetime import datetime


class Path:
    # constants.py lives in src/, so the project root is one level up.
    # Runtime files (config/data/log) live there, separate from the code.
    PROJECT_ROOT = pathlib.Path(__file__).parent.parent
    CONFIG_FILE = PROJECT_ROOT / "config.yaml"
    LOG_FILE = PROJECT_ROOT / "bot.log"
    DATA_FILE = PROJECT_ROOT / "data.json"

class Key:
    CHAT_ID = "chat_id"
    USERS = "users"
    TOKEN = "SPORT_BOT_TOKEN"
    USER_ID = "id"
    USER_NAME = "name"
    PINNED_MESSAGE = "_pinned"
    SICK = "_sick"  # list of user ids currently on sick leave

    # Bot commands
    DONE_CMD = "done"
    STATS_CMD = "daily_stats"
    SICK_CMD = "sick_leave"
    BACK_CMD = "back_to_business"

class Date:
    START_DAY = datetime(2025, 4, 23).date()

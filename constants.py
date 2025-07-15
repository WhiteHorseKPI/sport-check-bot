import pathlib
from datetime import datetime


class Path:
    PROJECT_ROOT = pathlib.Path(__file__).parent
    CONFIG_FILE = PROJECT_ROOT / "config.yaml"
    LOG_FILE = PROJECT_ROOT / "bot.log"
    DATA_FILE = PROJECT_ROOT / "data.json"

class Key:
    CHAT_ID = "chat_id"
    USERS = "users"
    TOKEN = "SPORT_BOT_TOKEN"
    DONE_CMD = "done"
    USER_ID = "id"
    USER_NAME = "name"
    PINNED_MESSAGE = "_pinned"

class Date:
    START_DAY = datetime(2025, 4, 23).date()

import asyncio
import logging
import os
import yaml

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from constants import Path, Key, Date
from storage import increment_all, reset_counter, load_data, save_data


logging.basicConfig(level=logging.WARNING, filename=Path.LOG_FILE)
logger = logging.getLogger(__name__)

TOKEN = os.getenv(Key.TOKEN)
with open(Path.CONFIG_FILE) as f:
    config = yaml.safe_load(f)
CHAT_ID = config[Key.CHAT_ID]
USERS = config[Key.USERS]


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler(Key.DONE_CMD, done_command))
    setup_scheduler(app, USERS)
    app.run_polling()


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context._chat_id != CHAT_ID:
        logger.warning("Tried access from different chat")
        return
    user_id = str(update.effective_user.id)
    if user_id not in [user[Key.USER_ID] for user in USERS]:
        await update.message.reply_text("You are not in the tracked list.")
        return
    reset_counter(user_id)

    data = load_data()
    daily_message = construct_daily_message(data)
    try:
        await context.bot.edit_message_text(chat_id=CHAT_ID,
                                            message_id=data[Key.PINNED_MESSAGE],
                                            text=daily_message)
        await update.message.reply_text(f"✅ {update.effective_user.name}, great work!")
    except Exception as e:
        logger.error(f"Caught Exception during message modification: {e}")


def setup_scheduler(bot_app, users):
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_message, 'cron', hour=6, minute=00, args=[bot_app, users])
    scheduler.start()


def send_daily_message(app, users):
    asyncio.run(send_daily_message_async(app, users))


async def send_daily_message_async(app, users):
    increment_all()
    data = load_data()
    daily_message = construct_daily_message(data)
    message = await app.bot.send_message(CHAT_ID, daily_message)
    await app.bot.pin_chat_message(CHAT_ID, message.message_id, disable_notification=True)

    data[Key.PINNED_MESSAGE] = message.message_id
    save_data(data)


def construct_daily_message(data):
    users_info = "\n".join(f"  - {user[Key.USER_NAME]}: {data[user[Key.USER_ID]]}" for user in USERS)
    day_count =abs((date.today() - Date.START_DAY).days)
    daily_message = f"📅 Daily Report {day_count}:\n{users_info}"
    return daily_message

if __name__ == "__main__":
    main()

import asyncio
import logging
import os
import yaml

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from constants import Path, Key, Date
from storage import (increment_all, reset_counter, load_data, save_data,
                     mark_sick, clear_sick, get_sick)


# Log to stderr (captured by systemd's journal -> `journalctl`) AND to bot.log.
# Third-party libraries stay at WARNING to keep the journal readable; our own
# logger is more verbose.
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(Path.LOG_FILE)],
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TOKEN = os.getenv(Key.TOKEN)
with open(Path.CONFIG_FILE) as f:
    config = yaml.safe_load(f)
CHAT_ID = config[Key.CHAT_ID]
USERS = config[Key.USERS]


def main():
    logger.info("Starting bot for chat %s with %d users", CHAT_ID, len(USERS))
    app = ApplicationBuilder().token(TOKEN).post_init(register_commands).build()
    app.add_handler(CommandHandler(Key.DONE_CMD, done_command))
    app.add_handler(CommandHandler(Key.STATS_CMD, daily_stats_command))
    app.add_handler(CommandHandler(Key.SICK_CMD, sick_leave_command))
    app.add_handler(CommandHandler(Key.BACK_CMD, back_to_business_command))
    setup_scheduler(app, USERS)
    app.run_polling()


async def register_commands(app):
    """Publish the command list so Telegram shows autocomplete hints."""
    await app.bot.set_my_commands([
        BotCommand(Key.DONE_CMD, "Mark today's training as done (reset your counter)"),
        BotCommand(Key.STATS_CMD, "Show the current report"),
        BotCommand(Key.SICK_CMD, "Go on sick leave (freeze your counter)"),
        BotCommand(Key.BACK_CMD, "Return from sick leave"),
    ])


def resolve_tracked_user(update, context):
    """Return (user_id, name) if the request is from the tracked group and a
    known user, otherwise None. Logs/handles the rejection cases."""
    if context._chat_id != CHAT_ID:
        logger.warning("Tried access from different chat")
        return None
    user_id = str(update.effective_user.id)
    if user_id not in [user[Key.USER_ID] for user in USERS]:
        return None
    return user_id, update.effective_user.name


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resolved = resolve_tracked_user(update, context)
    if resolved is None:
        return
    user_id, name = resolved

    clear_sick(user_id)  # finishing training implies you're not on sick leave
    reset_counter(user_id)
    logger.info("Reset counter for %s (%s)", name, user_id)

    await refresh_report(context.bot)
    await update.message.reply_text(f"✅ {name}, great work!")


async def daily_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context._chat_id != CHAT_ID:
        logger.warning("Tried access from different chat")
        return
    await update.message.reply_text(construct_daily_message(load_data()))


async def sick_leave_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resolved = resolve_tracked_user(update, context)
    if resolved is None:
        return
    user_id, name = resolved

    mark_sick(user_id)
    logger.info("Marked %s (%s) on sick leave", name, user_id)

    await refresh_report(context.bot)
    await update.message.reply_text(
        f"🤒 {name} is on sick leave. Your counter is frozen and I'll check in "
        f"daily. Send /back_to_business when you're ready to train again."
    )


async def back_to_business_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resolved = resolve_tracked_user(update, context)
    if resolved is None:
        return
    user_id, name = resolved

    clear_sick(user_id)
    reset_counter(user_id)
    logger.info("Cleared sick leave for %s (%s)", name, user_id)

    await refresh_report(context.bot)
    await update.message.reply_text(f"💪 Welcome back, {name}! Counter reset — let's go.")


async def refresh_report(bot):
    """Edit the pinned daily report in place, or post a fresh one if none is
    pinned yet (e.g. a command before the first 06:00 run)."""
    data = load_data()
    daily_message = construct_daily_message(data)
    pinned_message_id = data.get(Key.PINNED_MESSAGE)
    if pinned_message_id is not None:
        try:
            await bot.edit_message_text(chat_id=CHAT_ID,
                                        message_id=pinned_message_id,
                                        text=daily_message)
        except Exception as e:
            logger.error(f"Caught Exception during message modification: {e}")
    else:
        logger.warning("No pinned message found; posting a new daily report")
        await post_daily_message(bot, data, daily_message)


def setup_scheduler(bot_app, users):
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_message, 'cron', hour=6, minute=00, args=[bot_app, users])
    scheduler.start()


def send_daily_message(app, users):
    asyncio.run(send_daily_message_async(app, users))


async def send_daily_message_async(app, users):
    increment_all([user[Key.USER_ID] for user in users])
    data = load_data()
    daily_message = construct_daily_message(data)
    await post_daily_message(app.bot, data, daily_message)
    await check_in_sick_users(app.bot, users)


async def check_in_sick_users(bot, users):
    """Ask everyone still on sick leave whether they're recovered."""
    sick = set(get_sick())
    for user in users:
        if user[Key.USER_ID] not in sick:
            continue
        await bot.send_message(
            CHAT_ID,
            f"🤒 {user[Key.USER_NAME]}, are you still on sick leave? "
            f"Send /back_to_business when you're ready to train again."
        )


async def post_daily_message(bot, data, daily_message):
    """Send the daily report, pin it, and remember the pinned message id."""
    message = await bot.send_message(CHAT_ID, daily_message)
    await bot.pin_chat_message(CHAT_ID, message.message_id, disable_notification=True)

    data[Key.PINNED_MESSAGE] = message.message_id
    save_data(data)
    logger.info("Sent and pinned daily report (message_id=%s)", message.message_id)


def construct_daily_message(data):
    sick = set(data.get(Key.SICK, []))
    lines = []
    for user in USERS:
        user_id = user[Key.USER_ID]
        if user_id in sick:
            status = "🤒 sick leave"
        else:
            status = data.get(user_id, 0)
        lines.append(f"  - {user[Key.USER_NAME]}: {status}")
    users_info = "\n".join(lines)
    day_count = abs((date.today() - Date.START_DAY).days)
    daily_message = f"📅 Daily Report {day_count}:\n{users_info}"
    return daily_message

if __name__ == "__main__":
    main()

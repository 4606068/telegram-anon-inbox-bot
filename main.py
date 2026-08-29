import logging
from logging.handlers import RotatingFileHandler

import telebot

from config import (
    ADMIN_ID,
    ADMIN_NOT_REPLIED,
    ADMIN_REPLIED_NOT_TO_USER,
    BOT_API_TOKEN,
    DEVELOPER_ID,
    EMOJI,
    LOG_FILE,
    START_USER_MSG,
)
from db import create_db, get_user_emoji, get_user_id, register_user

# ------------------------------------------------------------------ #
#  Logging                                                            #
# ------------------------------------------------------------------ #
# RotatingFileHandler caps the log at 1 MB and keeps 3 old copies,
# so it never grows unbounded.  StreamHandler mirrors output to the
# terminal while the bot is running.
_file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
    handlers=[_file_handler, logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Bot setup                                                          #
# ------------------------------------------------------------------ #
bot = telebot.TeleBot(BOT_API_TOKEN)
create_db()


def _notify_dev(error: str) -> None:
    """Best-effort error notification to the developer account."""
    try:
        bot.send_message(DEVELOPER_ID, f"⚠️ Error: {error}")
    except Exception:
        pass  # don't let a notification failure mask the original error


# ------------------------------------------------------------------ #
#  Command handlers                                                   #
# ------------------------------------------------------------------ #

@bot.message_handler(commands=["start"])
def cmd_start(message) -> None:
    try:
        user = message.from_user
        logger.info("CMD /start  user=%s", user.id)

        if user.id != ADMIN_ID:
            register_user(user)
            bot.send_message(user.id, START_USER_MSG)

    except Exception as e:
        logger.error("Error in /start  user=%s  error=%s", message.from_user.id, e)
        _notify_dev(str(e))


@bot.message_handler(commands=["log"])
def cmd_log(message) -> None:
    try:
        logger.info("CMD /log  user=%s", message.from_user.id)

        if message.from_user.id == DEVELOPER_ID:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                bot.send_document(DEVELOPER_ID, f)

    except Exception as e:
        logger.error("Error in /log  user=%s  error=%s", message.from_user.id, e)
        _notify_dev(str(e))


# ------------------------------------------------------------------ #
#  Message handler                                                    #
# ------------------------------------------------------------------ #

@bot.message_handler(content_types=["text", "photo"])
def receive(message) -> None:
    try:
        content_type: str = message.content_type

        if message.chat.id == ADMIN_ID:
            _handle_admin_message(message, content_type)
        else:
            _handle_user_message(message, content_type)

    except Exception as e:
        logger.error("Error in receive  user=%s  error=%s", message.from_user.id, e)
        _notify_dev(str(e))


def _handle_admin_message(message, content_type: str) -> None:
    """Route the admin's reply back to the correct user."""
    if not message.reply_to_message:
        bot.send_message(ADMIN_ID, ADMIN_NOT_REPLIED)
        logger.info("Admin sent message without reply target")
        return

    reply = message.reply_to_message
    source_text = reply.text if reply.content_type == "text" else (reply.caption or "")
    user_emoji = source_text[0] if source_text else ""

    if user_emoji not in EMOJI:
        bot.send_message(ADMIN_ID, ADMIN_REPLIED_NOT_TO_USER)
        logger.info("Admin replied to non-user message (emoji=%r)", user_emoji)
        return

    user_id = get_user_id(user_emoji)
    if user_id is None:
        bot.send_message(ADMIN_ID, "Пользователь не найден.")
        logger.warning("No user found for emoji %r", user_emoji)
        return

    if content_type == "text":
        bot.send_message(user_id, message.text)
    else:
        bot.send_photo(user_id, message.photo[-1].file_id, message.caption or "")

    logger.info("Admin -> user %s  [%s]", user_id, content_type)


def _handle_user_message(message, content_type: str) -> None:
    """Forward the user's message to the admin, prefixed with their emoji."""
    emoji = get_user_emoji(message.chat.id)

    if emoji is None:
        # User somehow bypassed /start — prompt them to register.
        bot.send_message(message.chat.id, START_USER_MSG)
        logger.warning("Unregistered user %s tried to send a message", message.chat.id)
        return

    header = f"{emoji}:\n"

    if content_type == "text":
        bot.send_message(ADMIN_ID, header + message.text)
    else:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, header + (message.caption or ""))

    logger.info("User %s (%s) -> admin  [%s]", message.chat.id, emoji, content_type)


# ------------------------------------------------------------------ #
#  Entry point                                                        #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    logger.info("Bot starting up")
    bot.polling(non_stop=True, interval=0)

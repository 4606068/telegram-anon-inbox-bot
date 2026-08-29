from dotenv import load_dotenv
import os

load_dotenv()

try:
    BOT_API_TOKEN: str = os.environ["BOT_API_TOKEN"]
    ADMIN_ID: int     = int(os.environ["ADMIN_ID"])
    DEVELOPER_ID: int = int(os.environ["DEVELOPER_ID"])
except KeyError as e:
    raise SystemExit(f"Missing required environment variable: {e}") from e

DATABASE = "users.db"
LOG_FILE = "bot.log"

# Messages
START_USER_MSG           = "Стартовое сообщение для юзера."
ADMIN_NOT_REPLIED        = "Выберите сообщение для ответа."
ADMIN_REPLIED_NOT_TO_USER = "Ответьте на сообщение от пользователя."

# Keep EMOJI as a list so multi-codepoint emoji are never split.
EMOJI: list[str] = [
    "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯",
    "🦁", "🐮", "🐷", "🐸", "🐵", "🐔", "🐧", "🐦", "🐤", "🐺",
    "🐗", "🐴", "🦄", "🦋", "🐞", "🐝", "🐡", "🐠", "🐟", "🐳",
]

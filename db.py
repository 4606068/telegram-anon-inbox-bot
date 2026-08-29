import sqlite3
from config import DATABASE, EMOJI

# A single connection reused across all calls.
# check_same_thread=False is required because telebot dispatches
# handlers on worker threads, not the main thread.
_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DATABASE, check_same_thread=False)
    return _conn


def create_db() -> None:
    get_conn().execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT,
            user_id  INTEGER PRIMARY KEY,
            emoji    TEXT    UNIQUE NOT NULL
        )
    """)
    get_conn().commit()


def register_user(user) -> None:
    """Assign an unused emoji to *user* and store them. No-op if already registered."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    if cursor.fetchone():
        return

    cursor.execute("SELECT emoji FROM users")
    used = {row[0] for row in cursor.fetchall()}

    for emoji in EMOJI:
        if emoji not in used:
            cursor.execute(
                "INSERT INTO users (username, user_id, emoji) VALUES (?, ?, ?)",
                (user.username, user.id, emoji),
            )
            conn.commit()
            return

    raise RuntimeError("No available emojis left for new users.")


def get_user_emoji(user_id: int) -> str | None:
    """Return the emoji assigned to *user_id*, or None if not found."""
    cursor = get_conn().cursor()
    cursor.execute("SELECT emoji FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def get_user_id(emoji: str) -> int | None:
    """Return the user_id for the given *emoji*, or None if not found."""
    cursor = get_conn().cursor()
    cursor.execute("SELECT user_id FROM users WHERE emoji = ?", (emoji,))
    row = cursor.fetchone()
    return row[0] if row else None

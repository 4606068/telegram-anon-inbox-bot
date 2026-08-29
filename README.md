# Anon Inbox Bot

[🇬🇧 English](README.md) | [🇷🇺 Русский](README.ru.md)

A Telegram bot that lets users send anonymous messages to an admin. Each user is assigned a unique emoji identifier, so the admin can reply to the right person by replying to their message — without ever seeing their real identity.

## Features
- Users message the bot → the message is forwarded to the admin, prefixed with the user's emoji
- Admin replies to a forwarded message → the bot routes the reply back to the correct user
- Supports text and photos
- Rotating log file (capped at 1 MB, keeps 3 backups)
- Errors are reported to the developer's Telegram account
- Config via environment variables (`.env`), no secrets in code

## Tech stack
- Python 3
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (`telebot`)
- SQLite (user ↔ emoji mapping)
- python-dotenv

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# fill in BOT_API_TOKEN, ADMIN_ID, DEVELOPER_ID in .env
python main.py
```

## Commands
- `/start` — register and get a welcome message (users)
- `/log` — download the current log file (developer only)

## License
MIT

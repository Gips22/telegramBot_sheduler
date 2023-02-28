"""Конфиги, переменные окружения задаются тут."""
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID", "")

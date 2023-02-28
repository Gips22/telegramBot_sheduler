"""Настройка конфигурации бота"""
from aiogram import Bot, Dispatcher

from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

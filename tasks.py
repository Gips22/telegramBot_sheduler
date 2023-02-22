"""Модуль тасков для celery worker"""
import redis
from celery import Celery
from bot import bot
from loguru import logger
import asyncio

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")

app_celery = Celery('tasks',
                    broker='redis://127.0.0.1:6379/0')  # создание ЭК Celery приложения с именем 'tasks' и настройкой брокера сообщений на Redis, который запущен на локальной машине по адресу localhost:6379/0.

r = redis.Redis(host="127.0.0.1", port=6379)


@app_celery.task(name='tasks.add')
def send_todo_message(text, chat_id):
    asyncio.run(func(text, chat_id))


async def func(text, chat_id):
    message = text
    await bot.send_message(chat_id=chat_id, text=message)


@app_celery.task(name='taskd.overdue')
def send_overdue_task_message():
    pass

"""Модуль тасков для celery worker и beat"""
import asyncio
import datetime
from aiogram.types import ParseMode

import redis
from celery import Celery
from loguru import logger
from celery.schedules import crontab

import db
from bot import bot
from config import TELEGRAM_ACCESS_ID

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")
app_celery = Celery('tasks', broker='redis://127.0.0.1:6379/0', include=['tasks'])
r = redis.Redis(host="127.0.0.1", port=6379)


@app_celery.task(name='tasks.add')
def create_celery_task_send_message(text: str, chat_id: str) -> None:
    """Таска для отправки напоминания о задаче"""
    asyncio.run(send_notification_message(text, chat_id))


async def send_notification_message(text: str, chat_id: str) -> None:
    """Отправляем напоминалку"""
    message = text
    await bot.send_message(chat_id=chat_id, text=message)


@app_celery.task(name='tasks.check_overdue_tasks')
def check_overdue_tasks(chat_id: str) -> None:
    """Проверка просроченных задач для shedule. Ежедневно, в заданное время."""
    logger.info("Задача по поиску незавершенных тасков и отправки уведомления запущена...")
    now = datetime.datetime.now()
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM task WHERE completed=false AND reminder_time <= '{now}'")
    overdue_tasks = cursor.fetchall()
    if overdue_tasks:
        message = f"Количество просроченных задач у вас: {len(overdue_tasks)}\n\n"
        for task in overdue_tasks:
            message += f"id={task[0]}. Задача: {task[1]}\n"
        asyncio.run(send_overdue_notification_message(message, chat_id))
    else:
        message = f"У вас нет просроченных задач. Ура!"
        asyncio.run(send_overdue_notification_message(message, chat_id))


async def send_overdue_notification_message(text, chat_id):
    """Отправка уведомления о просроченных тасках"""
    message = text
    await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)


app_celery.conf.beat_schedule = {
    'check_overdue_tasks': {
        'task': 'tasks.check_overdue_tasks',
        'schedule': crontab(hour=16, minute=47),
        'args': (TELEGRAM_ACCESS_ID,)
    },
}

app_celery.conf.update(
    timezone='Europe/Moscow',
)

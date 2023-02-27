"""Модуль тасков для celery worker"""
import redis
from aiogram.types import ParseMode
from celery import Celery
from bot import bot
from loguru import logger
import asyncio
import datetime
import db
from celery.schedules import crontab


logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")
app_celery = Celery('tasks', broker='redis://127.0.0.1:6379/0', include=['tasks'])
r = redis.Redis(host="127.0.0.1", port=6379)


@app_celery.task(name='tasks.add')
def create_celery_task_send_message(text, chat_id):
    asyncio.run(send_notification_message(text, chat_id))


async def send_notification_message(text, chat_id):
    message = text
    await bot.send_message(chat_id=chat_id, text=message)


@app_celery.task(name='tasks.ppp')
def check_overdue_tasks(chat_id):
    logger.info("Задача по поиску незавершенных тасков и отправки уведомления запущена...")
    now = datetime.datetime.now()
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM task WHERE completed=false AND reminder_time <= '{now}'")
    overdue_tasks = cursor.fetchall()
    if overdue_tasks:
        message = f"У вас {len(overdue_tasks)} просроченных задач:\n\n"
        for task in overdue_tasks:
            message += f"{task[1]}\n"
        asyncio.run(send_overdue_notification_message(message, chat_id))
    else:
        message = f"У вас нет просроченных задач. Ура!"
        asyncio.run(send_overdue_notification_message(message, chat_id))

async def send_overdue_notification_message(text, chat_id):
    message = text
    await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)


app_celery.conf.beat_schedule = {
    'check_overdue_tasks': {
        'task': 'tasks.ppp',
        'schedule': crontab(hour=10, minute=43),
        'args': (68968821,)
    },
}

app_celery.conf.update(
    timezone='Europe/Moscow',
)
"""Модуль тасков для celery worker"""
import redis
from aiogram.types import ParseMode
from celery import Celery
from bot import bot
from loguru import logger
import asyncio
import datetime
import db
import logging
# from celery.schedules import crontab
# from celery import beat

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
    logging.info('check_overdue_tasks called')
    print("GHGHGHGHGHG")
    now = datetime.datetime.now()
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM task WHERE completed=false AND reminder_time <= '{now}'")
    overdue_tasks = cursor.fetchall()
    print(overdue_tasks, type(overdue_tasks))
    if overdue_tasks:
        message = f"You have {len(overdue_tasks)} overdue tasks:\n\n"
        for task in overdue_tasks:
            message += f"{task[1]}\n"
            print(message)
        chat_id = chat_id
        print(chat_id)
        asyncio.run(send_overdue_notification_message(message, chat_id))


async def send_overdue_notification_message(text, chat_id):
    print("start send overdue")
    message = text
    await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)

def testo(chat_id):
    print("тестик", chat_id)



def set_beat_shedule(chat_id):
    print("set_beat_shedule starts")
    app_celery.conf.beat_schedule = {
        'create_celery_task_send_message': {
            'task': 'tasks.add',
            'schedule': 5.0,
            'args': (chat_id,)
        }
    }
    testo(chat_id)


app_celery.conf.beat_schedule = {
    'check_overdue_tasks': {
        'task': 'tasks.ppp',
        'schedule': 3.0,
        'args': (68968821, )
    },
}
app_celery.conf.timezone = 'UTC'



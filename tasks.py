"""Модуль тасков для celery worker"""
import redis
from celery import Celery
from bot import bot

app_celery = Celery('tasks', broker='redis://127.0.0.1:6379/0')  # создание ЭК Celery приложения с именем 'tasks' и настройкой брокера сообщений на Redis, который запущен на локальной машине по адресу localhost:6379/0.

r = redis.Redis(host="127.0.0.1", port=6379)


@app_celery.task(name='tasks.add')
async def send_todo_message(text, chat_id):
    print("OOOOOOO")
    await bot.send_message(text=text, chat_id=chat_id)


@app_celery.task(name='tasks.overdue')
def send_overdue_task_message():
    pass

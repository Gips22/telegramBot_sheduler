"""Модуль тасков для celery worker"""
import redis
from celery import Celery
from bot import bot

app_celery = Celery('tasks', broker='redis://redis:6379/0',
                    backend='redis://redis:6379/0')  # создание ЭК Celery приложения с именем 'tasks' и настройкой брокера сообщений на Redis, который запущен на локальной машине по адресу localhost:6379/0.

r = redis.Redis(host="redis", port=6379)


@app_celery.task(name='task_todo.add')
def send_todo_message(text):
    pass


@app_celery.task(name='overdue_task.add')
def send_overdue_task_message():
    pass

from typing import List, NamedTuple, Optional
from datetime import datetime
import asyncio

import redis

from exeptions import NotCorrectDateTime
import db
from bot import bot
from tasks import create_celery_task_send_message

r = redis.Redis(host="127.0.0.1", port=6379)


class Task(NamedTuple):
    id: Optional[int]
    task_name: str


class Message(NamedTuple):
    task_text: str
    data_time: datetime


def show_current_task_list():
    cursor = db.get_cursor()
    cursor.execute("SELECT * FROM task WHERE completed IS 0")
    data = cursor.fetchall()
    all_tasks = [Task(id=row[0], task_name=row[1]) for row in data]
    return all_tasks


def show_completed_task_list() -> List[Task]:
    """Возвращает 10 последних завершенных задач"""
    cursor = db.get_cursor()
    cursor.execute(
        "SELECT id, task_name FROM task WHERE completed = 1 "
        "ORDER BY created_time DESC LIMIT 10"
    )
    rows = cursor.fetchall()
    last_tasks = [Task(id=row[0], task_name=row[1]) for row in rows]
    return last_tasks


async def add_task(raw_message: str, chat_id):
    parsed_message = _parse_message(raw_message, chat_id)
    await _check_datatime_is_correct(parsed_message.data_time, chat_id)
    cursor = db.get_cursor()
    chat_id = chat_id
    try:
        cursor.execute(
            f"insert into task(task_name, reminder_time) "
            f"values "
            f"('{parsed_message.task_text}', '{parsed_message.data_time}')"
        )
        db.connection.commit()
    except Exception as ex:
        print(ex)

    message = "Задача добавлена в планировщик!"
    await bot.send_message(text=message, chat_id=chat_id)
    create_celery_task_send_message.apply_async(args=[parsed_message.task_text, chat_id], eta=parsed_message.data_time)


def complete_task(row_id):
    cursor = db.get_cursor()
    cursor.execute(f"UPDATE task "
                   f"SET completed = 1 "
                   f"WHERE id = {row_id}")
    db.connection.commit()


def delete_task(row_id: int) -> None:
    """Удаляет задачу по идентификатору"""
    db.delete("task", row_id)


def delete_all_tasks():
    cursor = db.get_cursor()
    cursor.execute(
        "delete from task;"
    )
    db.connection.commit()


def show_month_stat():
    """Делаем 2 запроса в БД и возвращазем их для составления статистики."""
    cursor = db.get_cursor()
    cursor.execute("SELECT COUNT(*) FROM task WHERE created_time >= date('now', '-1 month');")
    all_task_last_month = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM task WHERE completed = 1 AND created_time >= date('now', '-1 month');")
    completed_tasks_last_month = cursor.fetchall()
    return all_task_last_month, completed_tasks_last_month


def _parse_message(raw_message: str, chat_id) -> Message:
    words = raw_message.split()
    time_str = None
    date_str = None
    for word in words:
        if ':' in word and len(word) == 5:
            time_str = word
        elif '.' in word and len(word) == 10:
            date_str = word
    if not time_str or not date_str:
        asyncio.create_task(send_error_message(chat_id))
        raise NotCorrectDateTime
    data_obj = datetime.strptime(date_str + " " + time_str, "%d.%m.%Y %H:%M")
    task_text = ' '.join(words[:-2])
    return Message(task_text=task_text, data_time=data_obj)

async def send_error_message(chat_id):
    message = "Неверный формат. \n\nВведите /start для справки.\n" \
              "Или название задачи, дату и время напоминания, в формате: 'Купить молоко 22.02.2024 11:00'"
    await bot.send_message(chat_id=chat_id, text=message)


async def _check_datatime_is_correct(datatime, chat_id):
    if datatime < datetime.now():
        await bot.send_message(text="Введеная дата задачи некорректная (меньше текущей).", chat_id=chat_id)
        raise NotCorrectDateTime

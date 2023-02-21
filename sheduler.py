from typing import List, NamedTuple, Optional
from datetime import datetime
from exeptions import NotCorrectDateTime
import db
from worker import app_celery
from bot import bot
import redis

r = redis.Redis(host="127.0.0.1", port=6379)

class Task(NamedTuple):
    id: Optional[int]
    task_name: str


class Message(NamedTuple):
    task_text: str
    data_time: datetime


def _parse_message(raw_message: str) -> Message:
    words = raw_message.split()
    time_str = None
    date_str = None
    for word in words:
        if ':' in word and len(word) == 5:
            time_str = word
        elif '.' in word and len(word) == 10:
            date_str = word
    if not time_str or not date_str:
        raise NotCorrectDateTime
    data_obj = datetime.strptime(date_str + " " + time_str, "%d.%m.%Y %H:%M")
    task_text = ' '.join(words[:-2])
    return Message(task_text=task_text, data_time=data_obj)


async def add_task(raw_message: str, chat_id):
    parsed_message = _parse_message(raw_message)
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
    create_notification_to_celery(parsed_message.task_text, chat_id)


def create_notification_to_celery(text, chat_id):
    app_celery.send_task('tasks.add', args=[text, chat_id], countdown=10)


def delete_task(row_id: int) -> None:
    """Удаляет задачу по идентификатору"""
    db.delete("task", row_id)


def delete_all_tasks():
    cursor = db.get_cursor()
    cursor.execute(
        "delete from task"
    )


def show_current_task_list():
    pass


def show_completed_task_list() -> List[Task]:
    """Возвращает 10 последних завершенных задач"""
    cursor = db.get_cursor()
    cursor.execute(
        "select id, task_name from task"
        "order by created desc limit 10"
    )
    rows = cursor.fetchall()
    last_tasks = [Task(id=row[0], task_name=row[1]) for row in rows]
    return last_tasks


def get_month_statistics():
    """За последний месяц вы поставили n задач, из них выполнили m задач"""
    pass

"""Сервер Telegram бота. Точка входа."""
from aiogram import types, executor

import sheduler
from bot import dp
from middlewares import AccessMiddleware
from config import TELEGRAM_ACCESS_ID

dp.middleware.setup(AccessMiddleware(TELEGRAM_ACCESS_ID))


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        f"Привет, {message.from_user.username} c id {message.from_user.id}! Я бот-планировщик.\n \n"
        "Напиши мне: \n \n"
        "название задачи дату и время напоминания, в формате: 'Купить молоко 22.02.2024 11:00'\n\n"
        "/list, чтобы показать список актуальных задач. \n \n"
        "/completed_list, чтобы показать список заверщенных задач. \n \n"
        "+ и id задачи, чтобы завершить задачу по ее идентификатору. \n \n"
        "- и id задачи, чтобы удалить задачу по ее идентификатору. \n \n"
        "/del_all, удалить все задачи. \n \n"
        "/month_stat, для просмотра статистики за месяц.")


@dp.message_handler(lambda message: message.text.startswith('+'))
async def complete_task(message: types.Message):
    """Завершить задачу по ее идентификатору"""
    row_id = int(message.text[1:])
    sheduler.complete_task(row_id)
    await message.answer("Задача успешно завершена")


@dp.message_handler(commands=["list"])
async def show_task_list(message: types.Message):
    """Показывает список текущих/не заверщенных задач"""
    final_message = "Список всех актуальных задач: \n\n"
    task_list = sheduler.show_current_task_list()
    if not task_list:
        await message.answer("У вас пока нет актуальных задач")
    else:
        for i in task_list:
            final_message += f"id={i.id}. Задача: {i.task_name} \n"
        await message.answer(final_message)


@dp.message_handler(commands=["completed_list"])
async def show_completed_task(message: types.Message):
    """Показывает список из 10 последних завершенных задач"""
    final_message = "Список последних завершенных задач: \n\n"
    completed_tasks = sheduler.show_completed_task_list()
    if not completed_tasks:
        await message.answer("У вас пока нет заверщенных задач.")
    else:
        for i in completed_tasks:
            final_message += f"id={i.id}. Задача: {i.task_name} \n"
        await message.answer(final_message)


@dp.message_handler(lambda message: message.text.startswith('-'))
async def del_task(message: types.Message):
    """Удаляет одну задачу по её идентификатору (id)"""
    row_id = int(message.text[1:])
    sheduler.delete_task(row_id)
    answer_message = "Задача успешно удалена."
    await message.answer(answer_message)


@dp.message_handler(commands=["del_all"])
async def del_all_tasks(message: types.Message):
    """Удаляет все задачи"""
    sheduler.delete_all_tasks()
    await message.answer("Все задачи успешно удалены. Жду новых ^^")


@dp.message_handler(commands=["month_stat"])
async def get_month_stat(message: types.Message):
    """Выводит статистику количества поставленных за последний месяц задач. Также пишет сколько из них выполнено"""
    all_task_last_month, completed_tasks_last_month = sheduler.show_month_stat()
    await message.answer(f"Количество задач, поставленных за последний месяц: {all_task_last_month[0][0]}. \n \n"
                         f"Из них выполнено: {completed_tasks_last_month[0][0]}.")


@dp.message_handler()
async def add_task(message: types.Message):
    """Добавляет задачу в планировщик"""
    if not message.text.startswith("/"):
        chat_id = message.chat.id
        await sheduler.add_task(message.text, chat_id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

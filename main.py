from aiogram import Bot, Dispatcher, executor, types
from config import TELEGRAM_BOT_TOKEN

import sheduler

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        f"Привет, {message.from_user.username} c id {message.from_user.id}! Я бот, который может помочь тебе сделать что-то полезное.\n"
        "Напиши мне: \n \n"
        "/add, чтобы добавить задачу. \n"
        "/complete, номер задачи, завершить задачу по ее идентификатору. \n"
        "/list, чтобы показать список актуальных задач. \n"
        "/completed_list, чтобы показать список заверщенных задач. \n"
        "/del, номер задачи, чтобы удалить задачу по ее идентификатору.")


@dp.message_handler(commands=["add"])
async def add_task(message: types.Message):
    """Добавляет задачу в планировщик"""
    # result = my_function()
    await message.answer(f"Результат: ....")


@dp.message_handler(commands=["complete"])
async def complete_task(message: types.Message):
    """Завершить задачу по ее идентификатору"""
    await message.answer("Задача успешно завершена")


@dp.message_handler(commands=["list"])
async def show_task_list(message: types.Message):
    """Показывает список текущих задач"""
    sheduler.show_current_task_list()
    await message.answer("...")


@dp.message_handler(commands=["completed_list"])
async def show_completed_task(message: types.Message):
    """Показывает список из 10 последних завершенных задач"""
    sheduler.show_completed_task_list()
    await message.answer("...")


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_task(message: types.Message):
    """Удаляет одну задачу по её идентификатору"""
    row_id = int(message.text[4:])
    sheduler.delete_task(row_id)
    answer_message = "Задача успешно удалена"
    await message.answer(answer_message)


@dp.message_handler(commands=["del_all"])
async def del_all_tasks(message: types.Message):
    sheduler.delete_all_tasks()
    await message.answer("Все задачи успешно удалены")


@dp.message_handler(commands=["month_stat"])
async def get_month_stat(message: types.Message):
    await message.answer("За последний месяц вы поставили n задач, из них выполнили m задач")
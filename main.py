import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
import json

def load_habits():
    try:
        with open('habits.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data

def save_habits(data):
    with open('habits.json', 'w' ,encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2 )



load_dotenv()
token = os.getenv('BOT_TOKEN')

bot = Bot(token=token)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer('Приветствую в трекер привычек!')

@dp.message(Command('add_habit'))
async def add_habit_handler(message: Message, command: CommandObject):
    habits = load_habits()
    habit_name = command.args
    if not habit_name:
        return await message.answer('''Введите команду коректно:
        /add_habit привычка''')
    if habit_name not in habits:
        habits.setdefault(habit_name, [])
        save_habits(habits)
        await message.answer('Привычка успешно добавлена')
    else:
        await message.answer('Привычка уже добавлена')





async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
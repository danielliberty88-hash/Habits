import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
import datetime
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

def current_streak(habit, habits):
    if not habits[habit]:
        return 0
    streak = 0
    habits[habit].sort()
    for i in range(len(habits[habit])-1,0,-1):
        d1 = datetime.datetime.strptime(habits[habit][i], '%d.%m.%Y')
        d2 = datetime.datetime.strptime(habits[habit][i-1], '%d.%m.%Y')
        if (d1-d2).days != 1:
            break
        else:
            streak += 1
    return streak + 1

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

@dp.message(Command('done'))
async def done_handler(message: Message, command: CommandObject):
    habits = load_habits()
    habit_name = command.args
    if habit_name not in habits:
        return await message.answer('Привычка еще не добавлена!')
    today = datetime.datetime.now().strftime('%d.%m.%Y')
    if today not in habits[habit_name]:
        habits[habit_name].append(today)
        await message.answer(f'Привычка {habit_name} выполнена!')
    else:
        await message.answer(f'Привычка {habit_name} уже выполнена!')
    save_habits(habits)

@dp.message(Command('list'))
async def list_handler(message: Message):
    habits = load_habits()
    if not habits:
        return await message.answer('У тебя еще нет привычек. Добавь через /add_habit ')
    all_streaks = ''
    for habit in habits:
        all_streaks += f'{habit} серия:{current_streak(habit,habits)}🔥' + '\n'
    await message.answer(all_streaks.rstrip())

@dp.message(Command('del'))
async def del_handler(message: Message, command: CommandObject):
    habit_name = command.args
    habits = load_habits()
    if not habits:
        return await message.answer('Удалять нечего!')
    elif habit_name == 'all':
        habits.clear()
    elif habit_name not in habits:
        return await message.answer('Такой привычки итак нет!')
    else:
        habits.pop(habit_name)
    save_habits(habits)
    await message.answer('Удаление прошло успешно')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
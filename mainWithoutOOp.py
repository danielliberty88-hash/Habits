# import asyncio
# import os
# from aiogram import Bot, Dispatcher
# from dotenv import load_dotenv
# from aiogram.filters import CommandStart
# from aiogram.types import Message
# from aiogram.filters import Command
# from aiogram.filters.command import CommandObject
# import datetime
# import json
#
# def weekly_count(dates):
#     weekly_count = {}
#
#     for i in range(len(dates)):
#         d = datetime.datetime.strptime(dates[i], '%d.%m.%Y').isocalendar()
#         key = (d.year, d.week)
#         weekly_count[key] = weekly_count.setdefault(key, 0) + 1
#
#     return weekly_count
#
#
# def weekly_streak(dates, target):
#     counts = weekly_count(dates)
#     current_date = datetime.datetime.now()
#     streak = 0
#
#     while True:
#         current_date = current_date - datetime.timedelta(days=7)
#         iso = current_date.isocalendar()
#         week_key = (iso.year, iso.week)
#         week_counts = counts.get(week_key, 0)
#
#         if week_counts >= target:
#             streak += 1
#         else:
#             break
#
#     return streak
#
# def load_habits():
#     try:
#         with open('habits.json', 'r', encoding='utf-8') as f:
#             data = json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         data = {}
#
#     return data
#
# def save_habits(data):
#     with open('habits.json', 'w' ,encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2 )
#
# def current_streak(habit, habits):
#     dates = habits[habit]['dates']
#
#     if not dates:
#         return 0
#
#     streak = 0
#     dates.sort()
#     last_date = datetime.datetime.strptime(dates[-1], '%d.%m.%Y')
#
#     if (datetime.datetime.now()-last_date).days > 1:
#         return 0
#
#     for i in range(len(dates) - 1, 0, -1):
#         d1 = datetime.datetime.strptime(dates[i], '%d.%m.%Y')
#         d2 = datetime.datetime.strptime(dates[i - 1], '%d.%m.%Y')
#         if (d1-d2).days != 1:
#             break
#         else:
#             streak += 1
#
#     return streak + 1
#
# load_dotenv()
# token = os.getenv('BOT_TOKEN')
#
# bot = Bot(token=token)
# dp = Dispatcher()
#
# @dp.message(Command('add_spec_habit'))
# async def ad_spec_habit(message: Message , command: CommandObject):
#     habits = load_habits()
#     text = command.args
#     if not text or not text.strip() or len(text.split())!=2 or not (text.split()[1]).isdigit():
#         return await message.answer('Введите название привычки корректно /add_spec_habit {habit_name} {target}!!!')
#     habit = command.args.split()[0]
#     target = command.args.split()[1]
#     if habit in habits:
#         return await message.answer('Ваша привычка уже добавлена!')
#
#     habits[habit] = {"dates": [], "type": "weekly"}
#     habits[habit]['target'] = int(target)
#     save_habits(habits)
#     await message.answer(f'привычка: {habit} успешно добавлена')
#
# @dp.message(CommandStart())
# async def start_handler(message: Message):
#     await message.answer('Приветствую в трекер привычек!')
#
# @dp.message(Command('add_habit'))
# async def add_habit_handler(message: Message, command: CommandObject):
#     habits = load_habits()
#     habit_name = command.args
#
#     if not habit_name or not habit_name.strip():
#         return await message.answer('Введите название привычки!!!')
#
#     habit_name = habit_name.strip().lower()
#
#     if habit_name not in habits:
#         habits.setdefault(habit_name, {"dates": [], "type": "daily"})
#         save_habits(habits)
#         await message.answer('Привычка успешно добавлена')
#     else:
#         await message.answer('Привычка уже добавлена')
#
# @dp.message(Command('done'))
# async def done_handler(message: Message, command: CommandObject):
#     habits = load_habits()
#     habit_name = command.args
#
#     if not habit_name or not habit_name.strip():
#         return await message.answer('Введите название привычки!!!')
#
#     habit_name = habit_name.strip().lower()
#
#     if habit_name not in habits:
#         return await message.answer('Привычка еще не добавлена!')
#
#     today = datetime.datetime.now().strftime('%d.%m.%Y')
#
#     if today not in habits[habit_name]['dates']:
#         habits[habit_name]['dates'].append(today)
#         await message.answer(f'Привычка {habit_name} выполнена!')
#     else:
#         await message.answer(f'Привычка {habit_name} уже выполнена!')
#
#     save_habits(habits)
#
# @dp.message(Command('list'))
# async def list_handler(message: Message):
#     habits = load_habits()
#
#     if not habits:
#         return await message.answer('У тебя еще нет привычек. Добавь через /add_habit ')
#     all_streaks = ''
#
#     for habit in habits:
#         if habits[habit]['type'] == 'weekly':
#             all_streaks += f'{habit} серия: {weekly_streak(habits[habit]["dates"], habits[habit]['target'])}🔥' + '\n'
#         elif habits[habit]['type'] == 'daily':
#             all_streaks += f'{habit} серия:{current_streak(habit, habits)}🔥' + '\n'
#
#     await message.answer(all_streaks.rstrip())
#
# @dp.message(Command('del'))
# async def del_handler(message: Message, command: CommandObject):
#     habits = load_habits()
#     habit_name = command.args
#
#     if not habit_name or not habit_name.strip():
#         return await message.answer('Введите название привычки!!!')
#
#     habit_name = habit_name.strip().lower()
#
#     if not habits:
#         return await message.answer('Удалять нечего!')
#     elif habit_name == 'all':
#         habits.clear()
#     elif habit_name not in habits:
#         return await message.answer('Такой привычки итак нет!')
#     else:
#         habits.pop(habit_name)
#
#     save_habits(habits)
#     await message.answer('Удаление прошло успешно')
#
# @dp.message(Command('help'))
# async def help_handler(message: Message):
#     await message.answer('''/add_habit <название> — добавить привычку
# /done <название> — отметить выполнение
# /list — список привычек со стриками
# /del <название или all> — удалить привычку
# /help — это сообщение''')
#
# async def main():
#     await dp.start_polling(bot)
#
# if __name__ == '__main__':
#     asyncio.run(main())
import asyncio
import os
import json
import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from models import HabitTracker,Habit,Storage
from aiogram import F
from aiogram import BaseMiddleware

class TrackerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id
        else:
            chat_id = event.chat.id
        tracker = tracker_daily_reset(chat_id)
        data['tracker'] = tracker
        return await handler(event, data)

load_dotenv()
Token = os.getenv("BOT_TOKEN")

bot = Bot(token=Token)
dp = Dispatcher()
dp.message.middleware(TrackerMiddleware())
dp.callback_query.middleware(TrackerMiddleware())

trackers = {}

def get_tracker(chat_id):
    if chat_id not in trackers:
        trackers[chat_id] = HabitTracker(chat_id)
    return trackers[chat_id]


def tracker_daily_reset(chat_id):
    tracker = get_tracker(chat_id)
    tracker.daily_reset()
    return tracker


@dp.message(Command('start'))
async def start_handler(message: Message):
    await message.answer('Привет! я трекер-привычек чтоб узнать все мои команды напиши /help')



@dp.message(Command('edit_days'))
async def edit_days_handler(message: Message, tracker: HabitTracker):
    buttons = []
    for habit in tracker.habits:
        button = InlineKeyboardButton(text=habit.name, callback_data=f'edit_days_{habit.name}')
        buttons.append([button])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer('Выберете привычку для изменения', reply_markup=keyboard)

@dp.callback_query(F.data.startswith('edit_days_'))
async def edit_days_callback_handler(callback: CallbackQuery, tracker: HabitTracker):
    buttons = []
    habit_name = callback.data.split('_', maxsplit=2)[-1]
    day_names = [('mon', 'Пн'), ('tue', 'Вт'), ('wed', 'Ср'), ('thu', 'Чт'), ('fri', 'Пт'), ('sat', 'Сб'), ('sun', 'Вс')]
    for habit in tracker.habits:
        if habit_name == habit.name:
            for day, name in day_names:
                if day in habit.days:
                    flag = '✅'
                else:
                    flag = '⬜'
                day_status = f'{name}: {flag}'
                button = InlineKeyboardButton(text=day_status, callback_data=f'toggleday_{habit.name}_{day}')
                buttons.append([button])
    ready_button = InlineKeyboardButton(text='готово', callback_data='toggle_to_ready_button')
    buttons.append([ready_button])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer('Выберите день/дни', reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith('toggleday_'))
async def toggleday_handler(callback: CallbackQuery, tracker: HabitTracker):
    parts = callback.data.rsplit('_', maxsplit=1)
    d = parts[1]
    habit_name = parts[0][len('toggleday_'):]
    new_days = tracker.toggle_habit_day(habit_name, d)
    buttons = []
    day_names = [('mon', 'Пн'), ('tue', 'Вт'), ('wed', 'Ср'), ('thu', 'Чт'), ('fri', 'Пт'), ('sat', 'Сб'),
                 ('sun', 'Вс')]
    for habit in tracker.habits:
        if habit_name == habit.name:
            for day, name in day_names:
                if day in new_days:
                    flag = '✅'
                else:
                    flag = '⬜'
                day_status = f'{name}: {flag}'
                button = InlineKeyboardButton(text=day_status, callback_data=f'toggleday_{habit.name}_{day}')
                buttons.append([button])
    ready_button = InlineKeyboardButton(text='готово', callback_data='toggle_to_ready_button')
    buttons.append([ready_button])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_reply_markup(reply_markup = keyboard)
    await callback.answer()

@dp.callback_query(F.data == 'toggle_to_ready_button')
async def toggle_to_ready_button_handler(callback: CallbackQuery):
    await callback.message.answer('Обновление завершено')
    await callback.answer()


@dp.message(Command('freeze'))
async def freeze_handler(message: Message, tracker: HabitTracker):
    buttons = []
    for habit in tracker.habits:
        button = InlineKeyboardButton(text=habit.name, callback_data=f'freeze_{habit.name}')
        buttons.append([button])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer('Выберите привычку для заморозки', reply_markup=keyboard)


@dp.callback_query(F.data.startswith('freeze_'))
async def freeze_habit_handler(callback: CallbackQuery, tracker: HabitTracker):
    habit_name = callback.data.split('_', maxsplit=1)[1]
    result = tracker.habit_froze(habit_name)
    await callback.message.answer(result)
    await callback.answer()


@dp.message(Command('unfreeze'))
async def unfreeze_handler(message: Message, tracker: HabitTracker):
    buttons = []
    for habit in tracker.habits:
        button = InlineKeyboardButton(text=habit.name, callback_data=f'unfreeze_{habit.name}')
        buttons.append([button])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer('Выберите привычку для разморозки', reply_markup=keyboard)


@dp.callback_query(F.data.startswith('unfreeze_'))
async def unfreeze_habit_handler(callback: CallbackQuery, tracker: HabitTracker):
    habit_name = callback.data.split('_', maxsplit=1)[1]
    result = tracker.habit_unfroze(habit_name)
    await callback.message.answer(result)
    await callback.answer()




@dp.message(Command('del'))
async def del_handler(message: Message, tracker: HabitTracker):
    buttons = []
    for habit in tracker.habits:
        button = InlineKeyboardButton(text=habit.name, callback_data=f'del_{habit.name}')
        buttons.append([button])
    delete_all_button = InlineKeyboardButton(text='Удалить всe', callback_data='delete_all_habits')
    buttons.append([delete_all_button])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer('Выберите привычку для удаления', reply_markup=keyboard)


@dp.callback_query(F.data=='delete_all_habits')
async def del_all_habits_handler(callback: CallbackQuery):
    confirm_button = InlineKeyboardButton(text='Да, удалить все', callback_data='delete_all_confirm')
    cancel_button = InlineKeyboardButton(text='Нет, отменить удаление', callback_data='delete_all_cancel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[confirm_button, cancel_button]])
    await callback.message.answer('Вы уверены что хотите удалить все?', reply_markup=keyboard)


@dp.callback_query(F.data=='delete_all_confirm')
async def delete_all_confirm_handler(callback: CallbackQuery, tracker: HabitTracker):
    tracker.delete_all_habits()
    await callback.message.answer('Удаление прошло успешно')

@dp.callback_query(F.data=='delete_all_cancel')
async def delete_all_cancel_handler(callback: CallbackQuery):
    await callback.message.answer('Удаление отменено')


@dp.callback_query(F.data.startswith('del_'))
async def del_callback_handler(callback: CallbackQuery, tracker: HabitTracker):
    habit_name = callback.data.split('_', maxsplit=1)[1]
    result = tracker.delete_habit(habit_name)
    await callback.message.answer(result)
    await callback.answer()


@dp.message(Command('add'))
async def add_handler(message: Message, command: CommandObject, tracker: HabitTracker):
    text = command.args
    if text is None:
        await message.answer('Пример /add habit target')
        return

    text_list = text.split()
    habit_name = text_list[0]

    if len(text_list) >= 3:
        await message.answer('Введите команду коректно')
        return

    if len(text_list) == 1:
        result = tracker.add_habit(habit_name, 1)
        await message.answer(result)
        return

    try:
        habit_target = int(text_list[1])
    except ValueError:
        await message.answer('второй аргумент строго число')
        return

    result = tracker.add_habit(habit_name, habit_target)
    await message.answer(result)

@dp.message(Command('list'))
async def list_handler(message: Message, tracker: HabitTracker):
    await message.answer(tracker.daily_summary())

@dp.message(Command('weekly_report'))
async def weekly_report_handler(message: Message, tracker: HabitTracker):
    await message.answer(tracker.weekly_report())


@dp.message(Command('done'))
async def done_handler(message: Message, tracker: HabitTracker):
    buttons = []
    for habit in tracker.habits:
        button = InlineKeyboardButton(text=habit.name, callback_data=f'done_{habit.name}')
        buttons.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer('Выберите привычку', reply_markup=keyboard)

@dp.callback_query(F.data.startswith('done_'))
async def data_click_handler(callback: CallbackQuery, tracker: HabitTracker):
    habit_name = callback.data.split('_', maxsplit=1)[1]
    result = tracker.complete_habit(habit_name)
    await callback.message.answer(result)
    await callback.answer()


@dp.message(Command('help'))
async def help_handler(message: Message):
    text = (
         '/add habit target — добавить привычку (target необязателен)\n'
        '/done — отметить привычку выполненной\n'
        '/list — посмотреть все привычки на сегодня\n'
        '/weekly_report — недельный отчёт по каждой привычке\n'
        '/del — удалить привычку\n'
        '/freeze — заморозить привычку (пауза без потери стрика)\n'
        '/unfreeze — разморозить привычку\n'
    )
    await message.answer(text)

@dp.message()
async def empty_handler(message: Message):
    await message.answer('Не понимаю эту команду. Список команд — /help')

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())



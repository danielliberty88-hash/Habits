import json
import datetime


class Habit:
    def __init__(self, name, target, days=None, streak=0, completed_today=False, completed_date=None, history=None, frozen=False):
        self.name = name
        self.target = target
        self.streak = streak
        self.completed_today = completed_today
        self.completed_date = completed_date
        self.frozen = frozen

        if days is None:
            self.days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        else:
            self.days = days

        if history is None:
            self.history = []
        else:
            self.history = history

    def active_today(self):
        flag = False
        day = datetime.datetime.now().strftime('%a').lower()

        if not self.frozen:
            if day in self.days:
                flag = True

        return flag

    def previous_schedule_date(self):
        day = datetime.date.today() - datetime.timedelta(days=1)
        while True:
            day_name = day.strftime('%a').lower()
            if day_name in self.days:
                return day
            day = day - datetime.timedelta(days=1)





class HabitTracker:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.storage = Storage(f'habits_{chat_id}.json')
        self.habits = self.storage.load_habits()


    def add_habit(self, name , target, days=None):
        for habit in self.habits:
            if habit.name == name:
                return('Привычка уже добавлена!')
        self.habits.append(Habit(name, target, days))
        self.storage.dump_habits(self.habits)
        return('Привычка добавлена успешно!')


    def complete_habit(self, name):
        for habit in self.habits:
            if habit.name == name:
                if not habit.active_today():
                    return('Привычка сегодня не активна')

                if not habit.completed_today:
                    habit.streak += 1
                    habit.completed_today = True
                    habit.completed_date = datetime.date.today()
                    habit.history.append(datetime.date.today())
                    self.storage.dump_habits(self.habits)
                    return('Успешно выполнено!')
                else:
                    return('Выполнено сегодня')


        return('Такой привычки нет!')


    def daily_summary(self):
        lines = []
        if not self.habits:
            return 'Привычек пока нет, добавьте через /add'
        for habit in self.habits:
            if habit.active_today():
                flag = 'выполнено' if habit.completed_today else 'не выполнено'
                lines.append(f'{habit.name} стрик: {habit.streak} сегодня: {flag}')
            else:
                lines.append(f'{habit.name} стрик: {habit.streak}')
        return '\n'.join(lines)

    def daily_reset(self):
        today = datetime.date.today()
        for habit in self.habits:
            if habit.frozen:
                continue
            if habit.completed_date is not None:
                if habit.completed_date < habit.previous_schedule_date():
                    habit.streak = 0
            if habit.completed_date != today:
                habit.completed_today = False
        self.storage.dump_habits(self.habits)


    def delete_habit(self, name):
        for habit in self.habits:
            if habit.name == name:
                self.habits.remove(habit)
                self.storage.dump_habits(self.habits)
                return f'привычка {name} успешно удалена'
        return f'такой привычки нет'

    def delete_all_habits(self):
        self.habits = []
        self.storage.dump_habits(self.habits)
        return 'Все привыки удалены'


    def weekly_report(self):
        today = datetime.date.today()
        result = []

        if not self.habits:
            return 'Привычек еще нет добавь через /add'

        for habit in self.habits:
            habit_result = ''
            for i in range(6,-1,-1):
                symbol = ''
                day = today - datetime.timedelta(days=i)
                day_name = day.strftime('%a').lower()

                if day_name not in habit.days:
                    symbol = '⬬'
                elif day in habit.history:
                    symbol = '✅'
                else:
                    symbol = '❌'

                habit_result += f'{day_name}: {symbol}' + ' | '
            result.append(f'{habit.name}\n{habit_result[:-3]}')

        return '\n'.join(result)


    def habit_froze(self, habit_name):
        for habit in self.habits:
            if habit.name == habit_name:
                if habit.frozen:
                    return f'{habit.name} и так заморожена'
                habit.frozen = True
                self.storage.dump_habits(self.habits)
                return f'{habit.name} успешно заморожена'

        return 'не найдено привычки'

    def habit_unfroze(self, habit_name):
        for habit in self.habits:
            if habit.name == habit_name:
                if not habit.frozen:
                    return f'{habit.name} и так не заморожена'
                habit.frozen = False

                today = datetime.date.today()
                if habit.completed_date != today:
                    habit.completed_today = False
                if habit.completed_date is not None:
                    prev = habit.previous_schedule_date()
                    if habit.completed_date < prev:
                        habit.completed_date = prev

                self.storage.dump_habits(self.habits)
                return f'{habit.name} разморожена'
        return 'Не найдено привычки'


    def toggle_habit_day(self, habit_name, day):
        for habit in self.habits:
            if habit.name == habit_name:
                habit.remove(day)
            else:
                habit.append(day)
            self.storage.dump_habits(self.habits)
            return habit.days
        return None






class Storage:
    def __init__(self, filename):
        self.filename = filename

    def dump_habits(self, habits):
        data = []
        for habit in habits:
            data.append({'name': habit.name,
                         'target': habit.target,
                         'streak': habit.streak,
                         'days': habit.days,
                         'completed_today': habit.completed_today,
                         'completed_date': str(habit.completed_date) if habit.completed_date else None,
                         'history': [str(date) for date in habit.history],
                         'frozen': habit.frozen

                        })

        with open(self.filename, 'w',  encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)


    def load_habits(self):
        res = []
        try:
            with open(self.filename, 'r', encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return []


        for habit in data:
            history_dates = [datetime.date.fromisoformat(d) for d in habit['history']]
            last_day = habit['completed_date']
            if last_day is not None:
                last_day = datetime.date.fromisoformat(last_day)
            res.append(Habit(habit['name'],
                             habit['target'],
                             habit['days'],
                             habit['streak'],
                             habit['completed_today'],
                             last_day,
                             history_dates,
                             habit.get('frozen', False)
                             ))

        return res
import pandas as pd

from logic.birthday_calculation import find_birthdays
from logic.honor_calculation import find_honors


def birthday_occasion(number):
    return str(number) + ". Geburtstag"


def honor_occasion(number):
    return str(number) + " Jahre Mitgliedschaft"


# birthdays and honors (of the selectable numbers) in the next days, sorted by date: [(date, occasion, name)];
# the members that count for birthdays and for honors can differ (passive members, settings of the club)
def find_upcoming(birthday_members, honor_members, birthdays, honors, today, days=30):
    start = pd.Timestamp(today).normalize()
    end = start + pd.Timedelta(days=days)
    rows = [(entry.date, birthday_occasion(entry.number), entry.member.full_name())
            for entry in find_birthdays(birthday_members, birthdays, start, end)]
    rows += [(entry.date, honor_occasion(entry.number), entry.member.full_name())
             for entry in find_honors(honor_members, honors, start, end)]
    return sorted(rows)

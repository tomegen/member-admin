import os
import pandas as pd
from logic.calendar_export import write_entries_into_ics
from logic.date_utils import shift_years
from model.entry import Entry


# find all members with one of the given birthdays in the selected timeframe
def find_birthdays(members, birthdays, from_date, to_date):
    return [Entry(birthday, member, shift_years(member.birthday, birthday))
            for birthday in birthdays
            for member in members
            if is_birthday(member, birthday, from_date, to_date)]


# function to write all the birthdays into an ics file (all-day events)
def write_birthdays_into_ics(members, birthdays, from_date, to_date, ics_filename, reminder_days=0):
    return write_entries_into_ics(
        find_birthdays(members, birthdays, from_date, to_date),
        summary=lambda entry: str(entry.number) + ". Geburtstag " + entry.member.full_name(),
        description=lambda entry: str(entry.number) + '. Geburtstag von ' + entry.member.full_name(),
        ics_filename=ics_filename, reminder_days=reminder_days)


# function to write all the birthdays into a txt file; minimal = only name and date, no personal details
def write_birthdays_into_txt(members, birthdays, from_date, to_date, txt_filename, minimal=False):
    text = "Geburtstage vom " + str(from_date.strftime('%d.%m.%Y')) + " bis zum " + str(to_date.strftime('%d.%m.%Y'))
    text += os.linesep *2

    entries = find_birthdays(members, birthdays, from_date, to_date)
    for birthday in birthdays:
        text += str(birthday) + ". Geburtstag: "
        text += os.linesep
        for entry in entries:
            if entry.number == birthday:
                text = entry.print(text, minimal)
        text += os.linesep*3

    # Write the text to the selected file
    with open(txt_filename, "w", encoding="utf-8", newline="") as file:
        file.write(text)
    return True


# function to calculate if a member has birthday in the selected timeframe
def is_birthday(member, birthday, from_date, to_date):
    if not member.is_member or pd.isna(member.birthday):
        return False
    from_date = shift_years(from_date, -birthday)
    to_date = shift_years(to_date, -birthday)

    return bool((member.birthday >= from_date) & (member.birthday <= to_date))

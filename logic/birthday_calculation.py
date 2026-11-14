import os
import uuid
import pandas as pd
from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone
from logic.date_utils import shift_years
from model.entry import Entry


# find all members with one of the given birthdays in the selected timeframe
def find_birthdays(members, birthdays, from_date, to_date):
    return [Entry(birthday, member, shift_years(member.birthday, birthday))
            for birthday in birthdays
            for member in members
            if is_birthday(member, birthday, from_date, to_date)]


# function to write all the birthdays into an ics file (all-day events)
def write_birthdays_into_ics(members, birthdays, from_date, to_date, ics_filename):
    # Create a new calendar
    cal = Calendar()
    cal.add('prodid', '-//member-admin//Mitgliederverwaltung//DE')
    cal.add('version', '2.0')

    for entry in find_birthdays(members, birthdays, from_date, to_date):
        member = entry.member
        event_date = entry.date.date()
        # Create an event
        event = Event()
        event.add('summary', value=str(entry.number) + ". Geburtstag " + member.full_name())
        event.add('dtstart', event_date)
        event.add('dtend', event_date + timedelta(days=1))
        event.add('description', str(entry.number) + '. Geburtstag von ' + member.full_name())
        # stable id: importing the same file twice does not create duplicates
        event.add('uid', str(uuid.uuid5(uuid.NAMESPACE_DNS, member.full_name() + "|" + str(event_date)
                                        + "|" + str(entry.number))) + "@member-admin")
        event.add('dtstamp', datetime.now(timezone.utc))
        # Add the event to the calendar
        cal.add_component(event)

    # Write the text to the selected file
    with open(ics_filename, "wb") as file:
        file.write(cal.to_ical())
    return True


# function to write all the birthdays into a txt file
def write_birthdays_into_txt(members, birthdays, from_date, to_date, txt_filename):
    text = "Geburtstage vom " + str(from_date.strftime('%d.%m.%Y')) + " bis zum " + str(to_date.strftime('%d.%m.%Y'))
    text += os.linesep *2

    entries = find_birthdays(members, birthdays, from_date, to_date)
    for birthday in birthdays:
        text += str(birthday) + ". Geburtstag: "
        text += os.linesep
        for entry in entries:
            if entry.number == birthday:
                text = entry.member.print(text)
        text += os.linesep*3

    # Write the text to the selected file
    with open(txt_filename, "w", encoding="utf-8", newline="") as file:
        file.write(text)
    return True


# function to calculate if a member has birthday in the selected timeframe
def is_birthday(member, birthday, from_date, to_date):
    if member.member == 0 or pd.isna(member.birthday):
        return False
    from_date = shift_years(from_date, -birthday)
    to_date = shift_years(to_date, -birthday)

    return bool((member.birthday >= from_date) & (member.birthday <= to_date))

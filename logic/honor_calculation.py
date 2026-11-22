import os
import pandas as pd
from logic.calendar_export import write_entries_into_ics
from logic.date_utils import shift_years
from model.entry import Entry


# find all members with one of the given honors (years of membership) in the selected timeframe
def find_honors(members, honors, from_date, to_date):
    return [Entry(honor, member, shift_years(member.member_since, honor))
            for honor in honors
            for member in members
            if is_honor(member, honor, from_date, to_date)]


# write all the honors into an ics file (all-day events)
def write_honors_into_ics(members, honors, from_date, to_date, ics_filename, reminder_days=0):
    return write_entries_into_ics(
        find_honors(members, honors, from_date, to_date),
        summary=lambda entry: str(entry.number) + " Jahre Mitgliedschaft " + entry.member.full_name(),
        description=lambda entry: str(entry.number) + ' Jahre Mitgliedschaft von ' + entry.member.full_name(),
        ics_filename=ics_filename, reminder_days=reminder_days, uid_kind="honor|")


# write all the honors into a txt file; minimal = only name and date, no personal details
def write_honors_into_txt(members, honors, from_date, to_date, txt_filename, minimal=False):
    text = "Ehrungen vom " + str(from_date.strftime('%d.%m.%Y')) + " bis zum " + str(to_date.strftime('%d.%m.%Y'))
    text += os.linesep *2

    # loop through all the honors
    entries = find_honors(members, honors, from_date, to_date)
    for honor in honors:
        text += str(honor) + " Jahre Ehrung: "
        text += os.linesep
        for entry in entries:
            if entry.number == honor:
                text = entry.print(text, minimal)
        text += os.linesep*3

    # Write the text to the selected file
    with open(txt_filename, "w", encoding="utf-8", newline="") as file:
        file.write(text)
    return True


# Calculate if a member will get an honor
def is_honor(member, honor, from_date, to_date):
    if not member.is_member or pd.isna(member.member_since):
        return False
    from_date = shift_years(from_date, -honor)
    to_date = shift_years(to_date, -honor)

    return bool((member.member_since >= from_date) & (member.member_since <= to_date))

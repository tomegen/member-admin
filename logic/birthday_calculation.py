import pandas as pd
import os
from icalendar import Calendar, Event
from datetime import timedelta


def write_birthdays_into_ics(members, birthdays, from_date, to_date, ics_filename):
    # Create a new calendar
    cal = Calendar()

    for birthday in birthdays:
        print("Process birthday: " + str(birthday))
        for member in members:
            if is_birthday(member, birthday, from_date, to_date):
                # Create an event
                event = Event()
                event.add('summary', value=str(birthday) + ". Geburtstag " + member.first_name + " " + member.last_name)
                event.add('dtstart', pd.Timestamp(year=member.birthday.year + birthday, month=member.birthday.month,
                                                  day=member.birthday.day))
                event.add('dtend', pd.Timestamp(year=member.birthday.year + birthday, month=member.birthday.month,
                                                  day=member.birthday.day) + timedelta(days=1))
                event.add('location', '')
                event.add('description', str(birthday) + '. Geburtstag von ' + member.first_name + " " + member.last_name)
                # Add the event to the calendar
                cal.add_component(event)


    # calculate all the possibilities
    # Write the text to the selected file
    with open(ics_filename, "wb") as file:
        file.write(cal.to_ical())

    return True


def write_birthdays_into_txt(members, birthdays, from_date, to_date, txt_filename):
    text = "Geburtstage vom " + str(from_date.strftime('%d.%m.%Y')) + " bis zum " + str(to_date.strftime('%d.%m.%Y'))
    text += os.linesep *2

    for birthday in birthdays:
        print("Process birthday: " + str(birthday))
        text += str(birthday) + ". Geburtstag: "
        text += os.linesep
        for member in members:
            if is_birthday(member, birthday, from_date, to_date):
                text = member.print(text)
        text += os.linesep*3

    # calculate all the possibilities
    # Write the text to the selected file
    with open(txt_filename, "w") as file:
        file.write(text)

    return True

def is_birthday(member, birthday, from_date, to_date):
    if member.member == 0:
        return False
    from_date = pd.Timestamp(year=from_date.year - birthday, month=from_date.month, day=from_date.day)
    to_date = pd.Timestamp(year=to_date.year - birthday, month=to_date.month, day=to_date.day)

    return (member.birthday >= from_date) & (member.birthday <= to_date)

def print_member(member, text):
    #mandatory (first_name, last_name, birthday, member_since)
    text += member.first_name + " " + member.last_name + os.linesep
    text += "Geburtstag: " + str(member.birthday.strftime('%d.%m.%Y')) + os.linesep

    if member.phone_number or member.mobile_phone:
        text += "Nummer: "
        if member.phone_number:
            text += member.phone_number
            if member.mobile_phone:
                text += " / " + member.mobile_phone

        else:
            text += member.mobile_phone

        text += os.linesep

    # Anschrift
    if member.plz or member.ort or member.street:
        text += "Anschrift: " + os.linesep
        if member.plz:
            text += member.plz
            if member.ort:
                text += " " + member.ort
            text += os.linesep

        else:
            if member.ort:
                text += member.ort + os.linesep

        if member.street:
            text += member.street + os.linesep

    text += os.linesep*2

    return text
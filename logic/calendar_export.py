import uuid
from datetime import datetime, timedelta, timezone

from icalendar import Alarm, Calendar, Event


# write entries as all-day events into an ics file; reminder_days = 0 means no reminder
# uid_kind keeps the ids of different kinds of events apart (the birthday ids stay as they were)
def write_entries_into_ics(entries, summary, description, ics_filename, reminder_days=0, uid_kind=""):
    cal = Calendar()
    cal.add('prodid', '-//member-admin//Mitgliederverwaltung//DE')
    cal.add('version', '2.0')

    for entry in entries:
        event_date = entry.date.date()
        event = Event()
        event.add('summary', value=summary(entry))
        event.add('dtstart', event_date)
        event.add('dtend', event_date + timedelta(days=1))
        event.add('description', description(entry))
        # stable id: importing the same file twice does not create duplicates
        event.add('uid', str(uuid.uuid5(uuid.NAMESPACE_DNS, uid_kind + entry.member.full_name() + "|" + str(event_date)
                                        + "|" + str(entry.number))) + "@member-admin")
        event.add('dtstamp', datetime.now(timezone.utc))
        if reminder_days > 0:
            event.add_component(reminder(summary(entry), reminder_days))
        cal.add_component(event)

    with open(ics_filename, "wb") as file:
        file.write(cal.to_ical())
    return True


# the reminder shows up at 9 o'clock, the given number of days before the (all-day) event
def reminder(text, days):
    alarm = Alarm()
    alarm.add('action', 'DISPLAY')
    alarm.add('description', text)
    alarm.add('trigger', timedelta(days=-days, hours=9))
    return alarm

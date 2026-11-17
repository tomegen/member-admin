import os

from model.member import format_date


class Entry:
    # one result line: a member with an occasion (e.g. 75th birthday, 25 years membership) on a date

    def __init__(self, number, member, date):
        self.number = number
        self.member = member
        self.date = date

    # minimal: only name and date of the occasion, no birthday, phone or address (e.g. for the press)
    def print(self, text, minimal=False):
        if minimal:
            return text + self.member.full_name() + " – " + format_date(self.date) + os.linesep
        return self.member.print(text)

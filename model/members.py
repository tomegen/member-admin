import pandas as pd
from logic.date_utils import shift_years
from model import club_file, schema
from model.checks import plausibility_issues
from model.club_settings import ClubSettings, read_settings
from model.functions import read_functions
from model.issue import Issue  # noqa: F401 (also imported from here)
from model.member import Member
from model.schema import ACTIVE, LEFT, PASSIVE
from model.values import parse_date, to_text  # noqa: F401 (also imported from here)

READ_ERROR = ("Die Datei konnte nicht gelesen werden.\n\nIst sie vielleicht noch in einem anderen Programm "
              "geöffnet?\n\nTechnische Details: ")
NOT_STANDARD = ("Diese Datei ist keine Mitgliederliste im Format der App. Bitte über „Liste aus einem anderen "
                "Programm übernehmen“ importieren.")


class MemberListError(Exception):
    pass


def missing_columns_error(missing, found):
    return MemberListError("In der Excel-Datei wurden diese Spalten nicht gefunden: " + ", ".join(missing) +
                           ".\n\nGefundene Überschriften in Zeile 1: " +
                           ", ".join(str(heading) for heading in found) +
                           "\n\nBitte benennen Sie die Überschrift in Excel entsprechend um, z. B. in „" +
                           missing[0] + "“.")


class Members:

    # a member list in the standard format (model/schema.py); any other list goes through the import (importer/)
    def __init__(self, filename, today=None):

        today = pd.Timestamp.now().normalize() if today is None else pd.Timestamp(today)
        self.members = []
        self.issues = []
        self.filename = filename
        self.today = today
        self.snapshot = None             # state when read, to keep the changes of others (store.transaction)
        self.settings = ClubSettings()
        self.functions = []              # rows of the sheet "Funktionen" (model.functions.Function)
        self.file_id = None              # from the sheet "Info": the same in copies and conflict copies
        try:
            data = club_file.read_bytes(filename)
        except OSError as e:
            raise MemberListError(READ_ERROR + str(e))
        try:
            book = club_file.open_book(data)
        except Exception:   # e.g. .xls, .csv or no excel file at all
            raise MemberListError(NOT_STANDARD)
        if not club_file.is_standard(book):
            raise MemberListError(NOT_STANDARD)
        self.standard = True
        rows = self.read_standard(book, data, today)
        self.issues += plausibility_issues(rows, today)
        self.members = [member for _, member in rows]

    def read_standard(self, book, data, today):
        try:
            rows, issues, keys = club_file.read_members(book, today)
        except club_file.MissingColumns as e:
            raise missing_columns_error(e.missing, e.found)
        self.settings, setting_issues = read_settings(book)
        setting_issues += [Issue(row, member.full_name(), False, "Austritt vor mehr als " +
                                 str(self.settings.delete_after) + " Jahren: laut Löschfrist kann der Eintrag "
                                 "endgültig gelöscht werden (Tab „Mitglieder“).")
                           for row, member in rows if self.is_due(member)]
        self.functions, function_issues = read_functions(book, [(member.nr, member.full_name()) for _, member in rows])
        self.issues += issues + setting_issues + function_issues
        self.snapshot = club_file.Snapshot(club_file.file_hash(data), keys)
        self.file_id = to_text(club_file.read_info(book).get(schema.FILE_ID_KEY)) or None
        return rows

    # left members whose exit is longer ago than the deletion period of the club (never, if there is none)
    def deletion_due(self):
        return [member for member in self.members if self.is_due(member)]

    def is_due(self, member):
        years = self.settings.delete_after
        return years is not None and member.status == LEFT and member.nr is not None and \
            not pd.isna(member.exit_date) and shift_years(member.exit_date, years) <= self.today

    def functions_of(self, nr):
        return [function for function in self.functions if function.nr == nr]

    # members that count for "birthdays", "honors" or "statistics": the active ones, the passive ones if the
    # settings of the club say so
    def counted(self, purpose):
        passive = self.settings.passive(purpose)
        return [member for member in self.members
                if member.status == ACTIVE or (passive and member.status == PASSIVE)]

    # Calculate the total members
    def calculate_members(self):
        return sum(1 for member in self.members if member.is_member)

    # Calculate the former members / entries that are not counted
    def calculate_inactive(self):
        return sum(1 for member in self.members if not member.is_member)

    # Calculate the new members in the given year (default: current year)
    def calculate_new_members(self, year=None):
        if year is None:
            year = pd.Timestamp.now().year
        return sum(1 for member in self.members
                   if member.is_member and not pd.isna(member.member_since) and member.member_since.year == year)

import pandas as pd
from logic.date_utils import shift_years
from model import club_file, schema
from model.checks import plausibility_issues
from model.club_settings import ClubSettings, read_settings
from model.columns import detect_columns, missing_mandatory
from model.functions import read_functions
from model.issue import Issue  # noqa: F401 (also imported from here)
from model.member import Member
from model.schema import ACTIVE, LEFT, PASSIVE
from model.values import parse_date, to_text  # noqa: F401 (also imported from here)

READ_ERROR = ("Die Datei konnte nicht gelesen werden.\n\nIst es eine Excel-Datei (.xlsx oder .xls) "
              "und ist sie vielleicht noch in einem anderen Programm geöffnet?\n\nTechnische Details: ")


class MemberListError(Exception):
    pass


def missing_columns_error(missing, found):
    return MemberListError("In der Excel-Datei wurden diese Spalten nicht gefunden: " + ", ".join(missing) +
                           ".\n\nGefundene Überschriften in Zeile 1: " +
                           ", ".join(str(heading) for heading in found) +
                           "\n\nBitte benennen Sie die Überschrift in Excel entsprechend um, z. B. in „" +
                           missing[0] + "“.")


class Members:

    # a file in the standard format (model/schema.py) is read with all fields; an old list with the
    # columns found by their heading (until the import assistant converts it)
    def __init__(self, filename, config, today=None):

        today = pd.Timestamp.now().normalize() if today is None else pd.Timestamp(today)
        self.members = []
        self.issues = []
        self.filename = filename
        self.today = today
        self.snapshot = None   # only for the standard file, which the app can change
        self.settings = ClubSettings()   # an old list has no settings sheet: defaults
        self.functions = []              # rows of the sheet "Funktionen" (model.functions.Function)
        self.file_id = None              # from the sheet "Info": the same in copies and conflict copies
        try:
            data = club_file.read_bytes(filename)
        except OSError as e:
            raise MemberListError(READ_ERROR + str(e))
        try:
            book = club_file.open_book(data)
        except Exception:   # e.g. .xls: the old reader reads it or reports the problem
            book = None
        self.standard = book is not None and club_file.is_standard(book)
        if self.standard:
            rows = self.read_standard(book, data, today)
            self.issues += plausibility_issues(rows, today, since_label="Eintritt")
        else:
            rows = self.read_old_list(config)
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

    # an old list: first sheet, heading in row 1, "Mitglied" is 1 or 0
    def read_old_list(self, config):
        try:
            self.sheet = pd.read_excel(self.filename, sheet_name=0)
        except Exception as e:
            raise MemberListError(READ_ERROR + str(e))

        # the columns are recognized by their heading (usual spellings, or the name from config.ini)
        columns = detect_columns(list(self.sheet.columns), config)
        missing_columns = missing_mandatory(columns)
        if missing_columns:
            raise missing_columns_error(missing_columns, list(self.sheet.columns))

        last_names = self.sheet[columns["last_name"]]
        first_names = self.sheet[columns["first_name"]]
        streets = self.optional_column(columns["street"])
        plzs = self.optional_column(columns["plz"])
        orte = self.optional_column(columns["ort"])
        birthdays = self.sheet[columns["birthday"]]
        phones = self.optional_column(columns["phone"])
        mobile_phones = self.optional_column(columns["mobile_phone"])
        members_since = self.sheet[columns["member_since"]]
        ibans = self.optional_column(columns["iban"])
        references = self.optional_column(columns["reference"])
        member_status = self.sheet[columns["member"]]
        rows = []

        for i in range(len(last_names)):
            row = i + 2  # row number in excel (row 1 is the header)

            # rows without any content are skipped
            mandatory_values = [last_names[i], first_names[i], birthdays[i], members_since[i], member_status[i]]
            if all(pd.isna(value) for value in mandatory_values):
                continue

            # mandatory params
            last_name = to_text(last_names[i])
            first_name = to_text(first_names[i])
            member_since = parse_date(members_since[i])
            birthday = parse_date(birthdays[i])
            member = pd.to_numeric(member_status[i], errors="coerce")
            name = (first_name + " " + last_name).strip() or "(ohne Namen)"

            if member not in (0, 1):
                self.issues.append(Issue(row, name, False, "Mitglied-Status fehlt oder ist nicht 0/1, das Mitglied "
                                                           "wird nicht mitgezählt."))
            active = member == 1

            if not last_name or not first_name:
                self.issues.append(Issue(row, name, active, "Vorname oder Nachname fehlt."))

            if pd.isna(member_since):
                reason = "fehlt" if pd.isna(members_since[i]) else "ist nicht lesbar: " + to_text(members_since[i])
                self.issues.append(Issue(row, name, active, "Mitglied seit " + reason +
                                         ", es kann keine Ehrung berechnet werden."))

            if pd.isna(birthday):
                reason = "fehlt" if pd.isna(birthdays[i]) else "ist nicht lesbar: " + to_text(birthdays[i])
                self.issues.append(Issue(row, name, active, "Geburtstag " + reason +
                                         ", es kann kein Geburtstag berechnet werden."))

            entry = Member(last_name=last_name,
                           first_name=first_name,
                           street=to_text(streets[i]),
                           plz=to_text(plzs[i]),
                           ort=to_text(orte[i]),
                           birthday=birthday,
                           phone_number=to_text(phones[i]),
                           mobile_phone=to_text(mobile_phones[i]),
                           member_since=member_since,
                           iban=to_text(ibans[i]),
                           reference=to_text(references[i]),
                           status=ACTIVE if active else LEFT if member == 0 else "")
            rows.append((row, entry))
        return rows

    # an optional column that is not in the excel file is treated as empty
    def optional_column(self, name):
        if name is not None:
            return self.sheet[name]
        return pd.Series(float("nan"), index=self.sheet.index)

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

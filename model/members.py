import numbers

import pandas as pd
from model.checks import plausibility_issues
from model.columns import detect_columns, missing_mandatory
from model.issue import Issue  # noqa: F401 (also imported from here)
from model.member import Member


class MemberListError(Exception):
    pass


# excel cells formatted as number hold a serial day number (not nanoseconds)
def parse_date(value):
    if pd.isna(value):
        return pd.NaT
    if isinstance(value, numbers.Real):  # also numpy numbers
        return pd.to_datetime(value, unit="D", origin="1899-12-30")
    # iso text (1967-06-01) is read as it is, german text (01.06.1967) is read day first
    parsed = pd.to_datetime(value, format="ISO8601", errors="coerce")
    if pd.isna(parsed):
        parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    return parsed


# cell content as text: empty cells become "", numbers like 12345.0 become "12345"
def to_text(value):
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


class Members:

    def __init__(self, filename, config, today=None):

        today = pd.Timestamp.now().normalize() if today is None else pd.Timestamp(today)
        self.members = []
        self.issues = []
        self.filename = filename
        try:
            self.sheet = pd.read_excel(filename, sheet_name=0)
        except Exception as e:
            raise MemberListError("Die Datei konnte nicht gelesen werden.\n\nIst es eine Excel-Datei (.xlsx oder .xls) "
                                  "und ist sie vielleicht noch in einem anderen Programm geöffnet?\n\n"
                                  "Technische Details: " + str(e))

        # the columns are recognized by their heading (usual spellings, or the name from config.ini)
        columns = detect_columns(list(self.sheet.columns), config)
        missing_columns = missing_mandatory(columns)
        if missing_columns:
            raise MemberListError("In der Excel-Datei wurden diese Spalten nicht gefunden: " +
                                  ", ".join(missing_columns) + ".\n\nGefundene Überschriften in Zeile 1: " +
                                  ", ".join(str(heading) for heading in self.sheet.columns) +
                                  "\n\nBitte benennen Sie die Überschrift in Excel entsprechend um, z. B. in „" +
                                  missing_columns[0] + "“.")

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
                member = 0
            member = int(member)
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
                           member=member)
            self.members.append(entry)
            rows.append((row, entry))

        self.issues += plausibility_issues(rows, today)

    # an optional column that is not in the excel file is treated as empty
    def optional_column(self, name):
        if name is not None:
            return self.sheet[name]
        return pd.Series(float("nan"), index=self.sheet.index)

    # Calculate the total members
    def calculate_members(self):
        return sum(member.member for member in self.members)

    # Calculate the former members / entries that are not counted
    def calculate_inactive(self):
        return sum(1 for member in self.members if member.member == 0)

    # Calculate the new members in the given year (default: current year)
    def calculate_new_members(self, year=None):
        if year is None:
            year = pd.Timestamp.now().year
        return sum(member.member for member in self.members
                   if not pd.isna(member.member_since) and member.member_since.year == year)

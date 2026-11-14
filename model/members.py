import numbers

import pandas as pd
from model.member import Member


class MemberListError(Exception):
    pass


# a problem found in the member list; row is the row number as shown in excel
class Issue:

    def __init__(self, row, name, active, message):
        self.row = row
        self.name = name
        self.active = active
        self.message = message


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

    def __init__(self, filename, config):

        self.members = []
        self.issues = []
        self.filename = filename
        try:
            self.sheet = pd.read_excel(filename, sheet_name=0)
        except Exception as e:
            raise MemberListError("Die Datei konnte nicht gelesen werden.\n\nIst es eine Excel-Datei (.xlsx oder .xls) "
                                  "und ist sie vielleicht noch in einem anderen Programm geöffnet?\n\n"
                                  "Technische Details: " + str(e))

        # mandatory columns have to exist in the excel file
        mandatory_columns = [config.last_name_config, config.first_name_config, config.birthdays_config,
                             config.member_since_config, config.member_config]
        missing_columns = [column for column in mandatory_columns if column not in self.sheet.columns]
        if missing_columns:
            raise MemberListError("In der Excel-Datei fehlen Pflichtspalten: " + ", ".join(missing_columns))

        last_names = self.sheet[config.last_name_config]
        first_names = self.sheet[config.first_name_config]
        streets = self.optional_column(config.street_config)
        plzs = self.optional_column(config.plz_config)
        orte = self.optional_column(config.ort_config)
        birthdays = self.sheet[config.birthdays_config]
        phones = self.optional_column(config.phone_config)
        mobile_phones = self.optional_column(config.mobile_phone_config)
        members_since = self.sheet[config.member_since_config]
        ibans = self.optional_column(config.iban_config)
        references = self.optional_column(config.reference_config)
        member_status = self.sheet[config.member_config]

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

            self.members.append(Member(last_name=last_name,
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
                                       member=member))

    # an optional column that is not in the excel file is treated as empty
    def optional_column(self, name):
        if name in self.sheet.columns:
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

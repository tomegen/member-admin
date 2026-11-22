import datetime
import hashlib
import io
import numbers
from collections import namedtuple

import pandas as pd
from openpyxl import load_workbook

from model import schema
from model.columns import normalize
from model.issue import Issue
from model.member import Member
from model.values import parse_date, to_text

# headings that only the standard file has (an old list may also have "Name" or "Status", not all of these)
STANDARD_MARKERS = {normalize(heading) for heading in ("Nr", "Geschlecht", "Status", "Eintritt")}


# mandatory columns of the standard file are missing; found are the headings of row 1
class MissingColumns(Exception):

    def __init__(self, missing, found):
        super().__init__(", ".join(missing))
        self.missing = missing
        self.found = found


# state of the file when it was read: hash of its bytes and the cell keys (see cell_key) of each member by nr.
# Saving compares with it to keep the changes that others made in the meantime (store/transaction.py)
Snapshot = namedtuple("Snapshot", "hash rows")


# the file is read once as bytes: hash and content are the same state, and no file handle stays open
def read_bytes(path):
    with open(path, "rb") as file:
        return file.read()


def file_hash(data):
    return hashlib.sha256(data).hexdigest()


# the standard file is read with openpyxl: it gives the real excel row numbers and is the base for writing
def open_book(data):
    return load_workbook(io.BytesIO(data), read_only=True, data_only=True)


# value of a cell without creating it: in a book opened for writing, sheet.cell() and iter_rows() add empty cells
# to the file
def peek(sheet, row, column):
    cell = sheet._cells.get((row, column))
    return None if cell is None else cell.value


# the values of the first columns of a sheet as rows of tuples, the same for books opened to read or to write
def sheet_rows(sheet, columns):
    if not hasattr(sheet, "_cells"):   # read only
        return [tuple(row) + (None,) * (columns - len(row))
                for row in sheet.iter_rows(max_col=columns, values_only=True)]
    last = max((row for row, _ in sheet._cells), default=0)
    return [tuple(peek(sheet, row, column) for column in range(1, columns + 1)) for row in range(1, last + 1)]


def members_sheet(book):
    return book[schema.MEMBERS_SHEET] if schema.MEMBERS_SHEET in book.sheetnames else book.worksheets[0]


def headings(sheet):
    first = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
    return [to_text(value) for value in first]


# key -> value from column A and B of the info sheet
def read_info(book):
    if schema.INFO_SHEET not in book.sheetnames:
        return {}
    return {to_text(row[0]): row[1] for row in book[schema.INFO_SHEET].iter_rows(max_col=2, values_only=True)
            if len(row) == 2 and to_text(row[0])}


# a file in the standard format has the info sheet with the schema version or the typical headings
def is_standard(book):
    if schema.SCHEMA_KEY in read_info(book):
        return True
    return STANDARD_MARKERS <= {normalize(heading) for heading in headings(members_sheet(book))}


def is_standard_file(path):
    try:
        book = open_book(read_bytes(path))
    except Exception:   # e.g. .xls or no excel file at all: the old reader reports it
        return False
    return is_standard(book)


# a cell value in a form that compares the same however it was written: dates as 2026-11-22, 5.0 as 5, text stripped
def cell_key(value):
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return ""
    if isinstance(value, datetime.date):
        return pd.Timestamp(value).date().isoformat()
    return to_text(value)


# a value of a dropdown, case does not matter; a first letter is fine if it is unique ("m" = männlich, "a" is not)
def choice(value, allowed):
    text = to_text(value).casefold()
    for option in allowed:
        if text == option.casefold():
            return option
    starting = [option for option in allowed if len(text) == 1 and option.casefold().startswith(text)]
    return starting[0] if len(starting) == 1 else ""


def whole_number(value):
    if isinstance(value, numbers.Real) and float(value).is_integer() and value > 0:
        return int(value)
    text = to_text(value)
    return int(text) if text.isdigit() and int(text) > 0 else None


# reads the sheet "Mitglieder": ([(excel row, Member)], [Issue], {nr: {field: cell key}});
# the columns are found by their heading
def read_members(book, today):
    sheet = members_sheet(book)
    found = {normalize(heading): index for index, heading in reversed(list(enumerate(headings(sheet))))}
    positions = {column.field: found[normalize(column.heading)] for column in schema.MEMBER_COLUMNS
                 if normalize(column.heading) in found}
    missing = [column.heading for column in schema.MEMBER_COLUMNS
               if column.mandatory and column.field not in positions]
    if missing:
        raise MissingColumns(missing, headings(sheet))

    rows, issues, numbers_seen, keys = [], [], {}, {}
    for row, cells in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        values = {field: cells[index] if index < len(cells) else None for field, index in positions.items()}
        if all(to_text(value) == "" for value in values.values()):
            continue   # empty rows (also the prepared ones with date format and dropdowns) are skipped

        member = Member(last_name=to_text(values["last_name"]),
                        first_name=to_text(values["first_name"]),
                        street=to_text(values.get("street")),
                        plz=to_text(values.get("plz")),
                        ort=to_text(values.get("ort")),
                        birthday=parse_date(values["birthday"]),
                        phone_number=to_text(values.get("phone")),
                        mobile_phone=to_text(values.get("mobile_phone")),
                        member_since=parse_date(values["member_since"]),
                        iban=to_text(values.get("iban")),
                        reference=to_text(values.get("reference")),
                        status=choice(values["status"], schema.STATUSES),
                        nr=whole_number(values.get("nr")),
                        gender=choice(values["gender"], schema.GENDERS),
                        exit_date=parse_date(values.get("exit_date")),
                        exit_reason=to_text(values.get("exit_reason")),
                        department=to_text(values.get("department")),
                        fee_class=to_text(values.get("fee_class")),
                        email=to_text(values.get("email")),
                        note=to_text(values.get("note")))
        issues += row_issues(row, member, values, numbers_seen, today)
        rows.append((row, member))
        if member.nr is not None and numbers_seen.get(member.nr) == row:
            keys[member.nr] = {field: cell_key(value) for field, value in values.items()}
    return rows, issues, keys


# findings of one row of the standard file; numbers_seen collects nr -> first excel row
def row_issues(row, member, values, numbers_seen, today):
    name = member.full_name() or "(ohne Namen)"
    active = member.is_member
    issues = []

    def add(message):
        issues.append(Issue(row, name, active, message))

    if not member.status:
        add("Status fehlt oder ist ungültig (erlaubt: " + ", ".join(schema.STATUSES) +
            "), das Mitglied wird nicht mitgezählt.")
    if not member.last_name or not member.first_name:
        add("Vorname oder Nachname fehlt.")
    if not member.gender:
        add("Geschlecht fehlt oder ist ungültig (erlaubt: " + ", ".join(schema.GENDERS) + ").")
    for field, label, consequence in (("member_since", "Eintritt", "es kann keine Ehrung berechnet werden."),
                                      ("birthday", "Geburtstag", "es kann kein Geburtstag berechnet werden.")):
        if pd.isna(getattr(member, field)):
            reason = "fehlt" if to_text(values[field]) == "" else "ist nicht lesbar: " + to_text(values[field])
            add(label + " " + reason + ", " + consequence)

    raw_nr = to_text(values.get("nr"))
    if member.nr is None:
        add("Mitgliedsnummer (Nr) fehlt." if raw_nr == "" else
            "Mitgliedsnummer (Nr) ist keine ganze Zahl: " + raw_nr)
    elif member.nr in numbers_seen:
        add("Mitgliedsnummer " + str(member.nr) + " ist doppelt vergeben (auch in Zeile " +
            str(numbers_seen[member.nr]) + ").")
    else:
        numbers_seen[member.nr] = row

    raw_exit = to_text(values.get("exit_date"))
    if raw_exit and pd.isna(member.exit_date):
        add("Austritt am ist nicht lesbar: " + raw_exit)
    if member.status == schema.LEFT and not raw_exit:
        add("Status ist „ausgetreten“, aber „Austritt am“ fehlt.")
    if member.is_member and not pd.isna(member.exit_date) and member.exit_date <= today:
        add("„Austritt am“ liegt in der Vergangenheit, der Status ist aber „" + member.status + "“.")
    return issues

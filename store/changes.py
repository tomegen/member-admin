from collections import namedtuple

import pandas as pd

from model import schema
from model.club_file import cell_key
from model.columns import normalize
from store.sheet import COLUMNS_BY_FIELD, COLUMNS_BY_HEADING, cell_value, is_empty, last_used_row
from store.errors import Conflict, Duplicate, FieldConflict, SaveError

# a line of the sheet "Änderungsprotokoll"; old and new are cell keys (see cell_key)
LogEntry = namedtuple("LogEntry", "nr name action field old new")

# The changes below are functions change(book, members) for store.transaction.save: they get the file as it is
# right now and return the lines for the change log.


def key_of(field, value):
    return cell_key(cell_value(COLUMNS_BY_FIELD[field], value))


# a member changed in the app: values are {field: new value}, base the cell keys when the member was read
# (Members.snapshot). A field that somebody else changed in the meantime is kept; if both changed it, Conflict
def update_member(nr, base, values, action="geändert"):
    def change(book, members):
        rows = members.rows_with(nr)
        if not rows:
            raise Conflict(nr, [], {}, missing=True)
        if len(rows) > 1:
            raise SaveError("Die Mitgliedsnummer " + str(nr) + " steht in der Datei mehrmals (Zeilen " +
                            ", ".join(str(row) for row in rows) + "). Bitte zuerst in Excel korrigieren.")
        row = rows[0]
        theirs = members.keys(row)
        writes, conflicts = [], []
        for field, value in values.items():
            mine, old = key_of(field, value), base.get(field, "")
            if mine == old:
                continue   # not changed here: whatever is in the file now stays
            if theirs.get(field, "") in (old, mine):
                writes.append((field, value, mine))
            else:
                conflicts.append(FieldConflict(field, COLUMNS_BY_FIELD[field].heading, old, mine, theirs[field]))
        if conflicts:
            raise Conflict(nr, conflicts, theirs)
        for field, value, _ in writes:
            members.set(row, field, value)
        name = members.name(row)
        return [LogEntry(nr, name, action, COLUMNS_BY_FIELD[field].heading, theirs.get(field, ""), mine)
                for field, value, mine in writes if theirs.get(field, "") != mine]
    return change


# a new member gets the next free nr and the row below the last member; same name and birthday as somebody in the
# file raises Duplicate, unless allow_duplicate
def add_member(values, allow_duplicate=False):
    def change(book, members):
        same = (key_of("last_name", values.get("last_name")).casefold(),
                key_of("first_name", values.get("first_name")).casefold(),
                key_of("birthday", values.get("birthday")))
        if not allow_duplicate:
            for row, _ in members.rows():
                keys = members.keys(row)
                if (keys.get("last_name", "").casefold(), keys.get("first_name", "").casefold(),
                        keys.get("birthday", "")) == same:
                    raise Duplicate(row, members.name(row))
        nr = members.highest_nr() + 1
        row = members.last_row() + 1
        members.set(row, "nr", nr)
        for field, value in values.items():
            if field != "nr":
                members.set(row, field, value)
        return [LogEntry(nr, members.name(row), "angelegt", "", "", "")]
    return change


# rows added by hand without a nr get the next numbers; a nr that is not a number ("x") is left for a person to fix
def assign_numbers():
    def change(book, members):
        entries, nr = [], members.highest_nr()
        for row, number in members.rows():
            if number is None and is_empty(members.get(row, "nr")):
                nr += 1
                members.set(row, "nr", nr)
                entries.append(LogEntry(nr, members.name(row), "Nummer vergeben", "Nr", "", str(nr)))
        return entries
    return change


# how a value appears in the change log: dates as 24.12.1960, the IBAN only with its start and end
def log_text(heading, key):
    column = COLUMNS_BY_HEADING.get(normalize(heading))
    if not key or column is None:
        return key
    if column.kind == "date":
        return pd.Timestamp(key).strftime("%d.%m.%Y")
    if column.field == "iban":
        compact = key.replace(" ", "")
        return compact[:2] + "** … " + compact[-4:] if len(compact) > 8 else "****"
    return key


def append_log(book, entries, editor, now):
    sheet = book[schema.LOG_SHEET]
    row = last_used_row(sheet) + 1
    for entry in entries:
        values = [now, editor, entry.nr, entry.name, entry.action, entry.field,
                  log_text(entry.field, entry.old), log_text(entry.field, entry.new)]
        for column, value in enumerate(values, start=1):
            sheet.cell(row=row, column=column, value=value if value != "" else None)
        sheet.cell(row=row, column=1).number_format = "DD.MM.YYYY HH:MM"
        row += 1

from collections import namedtuple

import pandas as pd

from model import schema
from model.club_file import cell_key, heading_columns, sheet_rows
from model.club_settings import SETTINGS_COLUMNS, general_text, read_settings
from model.columns import normalize
from model.functions import function_key, read_functions
from store.errors import Conflict, Duplicate, FieldConflict, SaveError
from store.sheet import COLUMNS_BY_FIELD, COLUMNS_BY_HEADING, cell_value, is_empty, last_used_row

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
# file raises Duplicate, unless allow_duplicate. functions: [(function, from, to, note)] of the new member
def add_member(values, allow_duplicate=False, functions=(), action="angelegt"):
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
        if functions:
            FunctionSheet(book).append(nr, members.name(row), functions)
        return [LogEntry(nr, members.name(row), action, "", "", "")]
    return change


# saves the result of a comparison (logic.merge): new people are added, the chosen fields of the others are changed
# (base_rows: Members.snapshot.rows when the file was read); leave: nr of members that are marked as left
def merge_members(items, base_rows, leave=(), exit_date=None, action="Import"):
    parts = []
    for item in items:
        if item.member is not None and item.chosen:
            values = {d.field: item.values[d.field] for d in item.differences if d.field in item.chosen}
            parts.append(update_member(item.nr, base_rows[item.nr], values, action=action))
        elif item.member is None and item.take:
            values = {field: value for field, value in item.values.items() if field != "nr"}
            parts.append(add_member(values, allow_duplicate=True, action=action))
    for nr in leave:
        parts.append(update_member(nr, base_rows[nr], {"status": schema.LEFT, "exit_date": exit_date},
                                   action="Austritt"))
    return combine(*parts)


# several changes in one save, e.g. the data of a member and its functions
def combine(*changes):
    def change(book, members):
        return [entry for part in changes for entry in part(book, members)]
    return change


# "Kassier (01.01.2020 – ), Jugendwart (2015 – 2019)" for the change log; functions are function keys
def functions_text(functions):
    def date(key):
        return pd.Timestamp(key).strftime("%d.%m.%Y") if key else ""
    return ", ".join(function + " (" + date(start) + " – " + date(end) + ")" + (" " + note if note else "")
                     for function, start, end, note in functions)


def wanted_keys(functions):
    return [(function.strip(), cell_key(start), cell_key(end), note.strip()) for function, start, end, note in functions]


class FunctionSheet:

    def __init__(self, book):
        self.sheet = book[schema.FUNCTIONS_SHEET]
        rows = sheet_rows(self.sheet, 8)
        columns = heading_columns(rows[0] if rows else ())
        self.columns = [columns.get(normalize(heading)) for heading in schema.FUNCTION_HEADINGS]
        if self.columns[0] is None or self.columns[2] is None:
            raise SaveError("Im Blatt „Funktionen“ fehlen die Überschriften „Nr“ oder „Funktion“. Bitte in Excel "
                            "ergänzen, dann neu einlesen.")

    # values: (function, from, to, note) with dates as date, timestamp or None
    def write(self, row, nr, name, values):
        for column, value in zip(self.columns, (nr, name) + tuple(values)):
            if column is None:
                continue
            if is_empty(value):   # also NaT, which has a year as well
                value = None
            elif hasattr(value, "year"):
                value = pd.Timestamp(value).date()
            cell = self.sheet.cell(row=row, column=column, value=value)
            if hasattr(value, "year"):
                cell.number_format = "DD.MM.YYYY"

    def append(self, nr, name, functions):
        row = last_used_row(self.sheet) + 1
        for values in functions:
            self.write(row, nr, name, values)
            row += 1


# the functions of a member as edited in the app: base are the function keys when read (Members.functions_of),
# functions the wanted [(function, from, to, note)]. Rows of other members stay; if somebody changed the
# functions of this member in the meantime, SaveError
def update_functions(nr, base, functions):
    def change(book, members):
        people = [(number, members.name(row)) for row, number in members.rows()]
        fresh, _ = read_functions(book, people)
        current = [function for function in fresh if function.nr == nr]
        name = dict((number, text) for number, text in people if number is not None).get(nr, "")
        if [function_key(function) for function in current] != list(base):
            raise SaveError("Die Funktionen von " + name + " wurden inzwischen von jemand anderem geändert. "
                            "Bitte neu einlesen und die Änderung wiederholen.")
        wanted = wanted_keys(functions)
        if wanted == list(base):
            return []
        sheet = FunctionSheet(book)
        rows = [function.row for function in current]
        for row, values in zip(rows, functions):
            sheet.write(row, nr, name, values)
        for row in sorted(rows[len(functions):], reverse=True):
            sheet.sheet.delete_rows(row)
        sheet.append(nr, name, functions[len(rows):])
        return [LogEntry(nr, name, "geändert", "Funktionen", functions_text(base), functions_text(wanted))]
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


# text of a settings area for the change log: "Geburtstag 60 Präsentkorb, Jubiläum 25", "Fußball, Tennis", "ja"
def area_text(label, value):
    if not isinstance(value, tuple):
        return str(general_text(label, value))
    parts = []
    for item in value:
        words = item if isinstance(item, tuple) else (item,)
        parts.append(" ".join("keine" if word == -1 else str(word) for word in words if word != ""))
    return ", ".join(parts)


# the settings dialog saved new settings; base are the settings when the file was read. An area (occasions, a list,
# a general setting) that somebody else changed in the meantime is kept; if both changed it, SaveError
def update_settings(base, new):
    def change(book, members):
        fresh, _ = read_settings(book)
        before, wanted, now = base.areas(), new.areas(), fresh.areas()
        changed = [label for label in wanted if wanted[label] != before[label]]
        conflicts = [label for label in changed if now[label] not in (before[label], wanted[label])]
        if conflicts:
            raise SaveError("Diese Einstellungen wurden inzwischen von jemand anderem geändert: " +
                            ", ".join(conflicts) + ". Bitte neu einlesen und die Änderung wiederholen.")
        sheet = book[schema.SETTINGS_SHEET]
        rows = sheet_rows(sheet, SETTINGS_COLUMNS)
        columns = heading_columns(rows[0] if rows else ())
        entries = []
        for label in changed:
            if now[label] == wanted[label]:
                continue
            if label == "Anlässe":
                notes = {(o.kind, o.years): o.note for o in fresh.occasions}
                write_occasions(sheet, columns, [o._replace(note=notes.get((o.kind, o.years), ""))
                                                 for o in new.occasions])
            elif label in new.lists:
                write_column(sheet, column_of(columns, label), new.lists[label])
            else:
                write_general(sheet, columns, label, new.general[label])
            entries.append(LogEntry(None, "", "Einstellungen", label, *log_difference(label, now[label], wanted[label])))
        return entries
    return change


# old and new text for the change log; of occasions and lists only what was removed and added
def log_difference(label, old, new):
    if not isinstance(old, tuple):
        return area_text(label, old), area_text(label, new)
    removed, added = tuple(item for item in old if item not in new), tuple(item for item in new if item not in old)
    if not removed and not added:
        return "", "(Reihenfolge geändert)"
    return area_text(label, removed), area_text(label, added)


def column_of(columns, heading):
    index = columns.get(normalize(heading))
    if index is None:
        raise SaveError("Im Blatt „Einstellungen“ fehlt die Überschrift „" + heading + "“. Bitte in Excel "
                        "ergänzen, dann neu einlesen.")
    return index


# replaces the values of a column below the heading; existing cells keep their format and dropdown
def write_column(sheet, column, values, first_row=2):
    for (row, index), cell in list(sheet._cells.items()):
        if index == column and row >= first_row:
            cell.value = None
    for row, value in enumerate(values, start=first_row):
        sheet.cell(row=row, column=column, value=value)


def write_occasions(sheet, columns, occasions):
    order = sorted(occasions, key=lambda o: (o.kind != schema.BIRTHDAY, -1 if o.years is None else o.years))
    for heading, values in zip(schema.OCCASION_HEADINGS,
                               ([o.kind for o in order], ["keine" if o.years is None else o.years for o in order],
                                [o.gift or None for o in order], [o.note or None for o in order])):
        write_column(sheet, column_of(columns, heading), values)


def write_general(sheet, columns, key, value):
    key_column = column_of(columns, schema.GENERAL_HEADINGS[0])
    value_column = column_of(columns, schema.GENERAL_HEADINGS[1])
    rows = [row for (row, index), cell in sheet._cells.items()
            if index == key_column and row > 1 and normalize(cell_key(cell.value)) == normalize(key)]
    if rows:
        row = min(rows)
    else:
        row = max([r for (r, index), cell in sheet._cells.items() if index == key_column and cell_key(cell.value)],
                  default=1) + 1
        sheet.cell(row=row, column=key_column, value=key)
    sheet.cell(row=row, column=value_column, value=general_text(key, value))


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

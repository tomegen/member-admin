from collections import namedtuple

import pandas as pd

from model import schema
from model.club_file import cell_key, heading_columns, sheet_rows, whole_number
from model.columns import normalize
from model.issue import Issue
from model.values import parse_date, to_text

SHEET_NAME = "Blatt „Funktionen“"   # shown in the data check instead of a member name

# a row of the sheet "Funktionen": excel row, nr of the member, name as written there, function, from, to (NaT = open)
Function = namedtuple("Function", "row nr name function start end note")


# what is compared when the functions of a member are saved (see store.changes.update_functions)
def function_key(function):
    return function.function, cell_key(function.start), cell_key(function.end), function.note


# "Max Muster", "Muster Max" and "muster, max" are the same name
def name_key(text):
    return frozenset(word for word in normalize_words(text) if word)


def normalize_words(text):
    return [normalize(word) for word in to_text(text).replace(",", " ").split()]


# rows without a nr belong to the member whose name is unique in the member list; {name key: nr or None}
def numbers_by_name(people):
    found = {}
    for nr, name in people:
        if nr is not None:
            key = name_key(name)
            found[key] = None if key in found else nr
    return found


# reads the sheet "Funktionen": ([Function], [Issue]); people are (nr, name) of the member list (nr may be None)
def read_functions(book, people):
    if schema.FUNCTIONS_SHEET not in book.sheetnames:
        return [], []
    rows = sheet_rows(book[schema.FUNCTIONS_SHEET], 8)
    if not rows:
        return [], []
    columns = heading_columns(rows[0])
    nr_column, name_column, function_column, start_column, end_column, note_column = (
        columns.get(normalize(heading)) for heading in schema.FUNCTION_HEADINGS)
    if nr_column is None or function_column is None:
        return [], [Issue(1, SHEET_NAME, True, "Die Überschriften „Nr“ und „Funktion“ fehlen, die Funktionen "
                                                 "können nicht gelesen werden.")]

    def value(values, column):
        return values[column - 1] if column else None

    known = {nr for nr, _ in people if nr is not None}
    by_name = numbers_by_name(people)
    functions, issues = [], []
    for row, values in enumerate(rows[1:], start=2):
        if all(to_text(cell) == "" for cell in values):
            continue
        name = to_text(value(values, name_column))
        raw_nr = to_text(value(values, nr_column))
        nr = whole_number(value(values, nr_column))
        start, end = parse_date(value(values, start_column)), parse_date(value(values, end_column))
        function = Function(row, nr, name, to_text(value(values, function_column)), start, end,
                            to_text(value(values, note_column)))

        def problem(message):
            issues.append(Issue(row, SHEET_NAME, True, (name + ": " if name else "") + message))

        if nr is None and not raw_nr and by_name.get(name_key(name)) is not None:
            function = function._replace(nr=by_name[name_key(name)])   # entered by hand with the name only
        elif nr is None:
            problem("Mitgliedsnummer fehlt oder ist ungültig" + (": " + raw_nr if raw_nr else "") + ".")
        elif nr not in known:
            problem("Mitgliedsnummer " + str(nr) + " gibt es im Blatt „Mitglieder“ nicht.")
        if not function.function:
            problem("Funktion fehlt.")
        for label, column, date in (("von", start_column, start), ("bis", end_column, end)):
            if pd.isna(date) and to_text(value(values, column)):
                problem("„" + label + "“ ist kein Datum: " + to_text(value(values, column)))
        if not pd.isna(start) and not pd.isna(end) and end < start:
            problem("„bis“ liegt vor „von“.")
        functions.append(function)
    return functions, issues

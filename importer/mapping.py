import re

import pandas as pd

from importer.gender import estimate_genders
from importer.reader import is_empty_row
from model import schema
from model.club_file import whole_number
from model.columns import FIELDS, detect_columns, normalize
from model.values import parse_date, to_text

COLUMNS = {column.field: column for column in schema.MEMBER_COLUMNS}
MANDATORY = [column.field for column in schema.MEMBER_COLUMNS if column.mandatory]
HEADER_SEARCH = 10   # the heading is searched in the first rows (lists often start with a title)

# targets of a column besides the fields of the standard
IGNORE, NOTE, NAME_BOTH, PLZ_ORT = "", "note+", "name+first", "plz+ort"
SPECIAL_TARGETS = [(IGNORE, "– nicht übernehmen –"), (NOTE, "in „Bemerkung“ übernehmen"),
                   (NAME_BOTH, "Name und Vorname (in einer Spalte)"), (PLZ_ORT, "PLZ und Ort (in einer Spalte)")]
TARGETS = SPECIAL_TARGETS[:2] + [(column.field, column.heading) for column in schema.MEMBER_COLUMNS] + \
    SPECIAL_TARGETS[2:]

# usual headings of the fields that model.columns does not know (it knows the ones of the old lists)
USUAL = {
    "nr": ["nr", "mitgliedsnummer", "mitgliedsnr", "mitgliednr", "mitglnr", "nummer", "id", "mglnr"],
    "gender": ["geschlecht", "anrede", "gender", "sex"],
    "exit_date": ["austritt", "austrittam", "austrittsdatum", "ausgetretenam", "ausgetreten"],
    "exit_reason": ["austrittsgrund", "grund", "kuendigungsgrund"],
    "department": ["abteilung", "sparte", "gruppe", "mannschaft"],
    "fee_class": ["beitragsklasse", "beitragsart", "beitrag", "tarif", "beitragsgruppe"],
    "email": ["email", "mail", "emailadresse", "mailadresse"],
    "note": ["bemerkung", "bemerkungen", "notiz", "notizen", "kommentar", "hinweis"],
}
FIELD_OF_OLD = {"phone": "phone", "member": "status"}   # names in model.columns that differ

STATUS_WORDS = {schema.ACTIVE: ["1", "x", "ja", "j", "aktiv", "a", "true", "wahr", "yes", "mitglied", ""],
                schema.PASSIVE: ["p", "passiv", "foerdermitglied", "fordermitglied", "foerderer", "passivesmitglied"],
                schema.LEFT: ["0", "nein", "n", "ausgetreten", "inaktiv", "false", "falsch", "no", "ex",
                              "gekuendigt", "gekundigt", "ehemalig"]}
GENDER_WORDS = {"männlich": ["herr", "herrn", "hr", "m", "mann", "maennlich", "mannlich", "male"],
                "weiblich": ["frau", "fr", "w", "weiblich", "f", "female"],
                "divers": ["d", "divers"]}


def known_headings(config):
    found = {normalize(getattr(config, attribute)) for attribute, _, _, _ in FIELDS.values()}
    found.update(name for _, _, usual, _ in FIELDS.values() for name in usual)
    found.update(name for usual in USUAL.values() for name in usual)
    return found


# the row with the most known headings in the first rows (lists often start with a title); index in rows
def guess_header_row(rows, config):
    known = known_headings(config)
    best, best_score = None, 0
    for index, row in enumerate(rows[:HEADER_SEARCH]):
        if is_empty_row(row):
            continue
        if best is None:
            best = index
        score = sum(1 for value in row if normalize(to_text(value)) in known)
        if score > best_score:
            best, best_score = index, score
    return best or 0


# the list below the heading: (headings, [(row number in the file, cells)]); columns without heading and
# without values are left out
class Table:

    def __init__(self, source, header_row):
        rows = source.rows
        width = max((len(row) for row in rows), default=0)
        padded = [list(row) + [None] * (width - len(row)) for row in rows]
        heading_row = padded[header_row] if padded else []
        data = [(number, row) for number, row in enumerate(padded[header_row + 1:], start=header_row + 2)
                if not is_empty_row(row)]
        used = [index for index in range(width)
                if to_text(heading_row[index]) or any(to_text(row[index]) for _, row in data)]
        self.headings = [to_text(heading_row[index]) or "Spalte " + str(index + 1) for index in used]
        self.rows = [(number, [row[index] for index in used]) for number, row in data]

    def values(self, column):
        return [cells[column] for _, cells in self.rows]

    def examples(self, column, count=3):
        found = []
        for value in self.values(column):
            text = to_text(value)
            if text and text not in found:
                found.append(text)
            if len(found) == count:
                break
        return found


def share(values, test):
    texts = [to_text(value) for value in values if to_text(value)]
    return sum(1 for text in texts if test(text)) / len(texts) if texts else 0


# a target per column of the table, from the headings and from the content
def suggest_columns(table, config):
    detected = detect_columns(table.headings, config)
    targets = [IGNORE] * len(table.headings)
    for field, heading in detected.items():
        if heading is not None:
            targets[table.headings.index(heading)] = FIELD_OF_OLD.get(field, field)
    for field, usual in USUAL.items():
        if field in targets:
            continue
        for index, heading in enumerate(table.headings):
            if targets[index] == IGNORE and normalize(heading) in usual:
                targets[index] = field
                break

    # a town column with "12345 Musterstadt" and no postcode column
    if "ort" in targets and "plz" not in targets and \
            share(table.values(targets.index("ort")), lambda text: re.match(r"\d{4,5}\s+\S", text)) > 0.5:
        targets[targets.index("ort")] = PLZ_ORT
    # one column "Name" with "Muster, Max" or "Max Muster" and no first name column
    if "first_name" not in targets and "last_name" in targets:
        index = targets.index("last_name")
        if share(table.values(index), lambda text: "," in text or " " in text) > 0.5:
            targets[index] = NAME_BOTH
    for index, heading in enumerate(table.headings):
        if targets[index] != IGNORE:
            continue
        values = table.values(index)
        if "email" not in targets and share(values, lambda text: "@" in text) > 0.5:
            targets[index] = "email"
        elif "iban" not in targets and share(values, lambda text: re.match(r"[A-Z]{2}\d{2}", text)) > 0.5:
            targets[index] = "iban"
        elif not {"plz", "ort", PLZ_ORT} & set(targets) and \
                share(values, lambda text: re.match(r"\d{4,5}\s+\S", text)) > 0.5:
            targets[index] = PLZ_ORT
    return targets


# the different values of a column, in the order of their first appearance ("" for empty cells)
def distinct_values(table, column):
    return list(dict.fromkeys(to_text(value) for value in table.values(column)))


def suggest_value(kind, raw):
    words = STATUS_WORDS if kind == "status" else GENDER_WORDS
    key = normalize(raw)
    if not key and to_text(raw):
        return ""   # e.g. "?": only an empty cell counts as empty
    for target, options in words.items():
        if key in options:
            return target
    return ""


# "Muster, Max" -> ("Muster", "Max"), "Max Peter Muster" -> ("Muster", "Max Peter")
def split_name(text):
    text = to_text(text)
    if "," in text:
        last, first = text.split(",", 1)
        return last.strip(), first.strip()
    words = text.split()
    if len(words) < 2:
        return text, ""
    return words[-1], " ".join(words[:-1])


# "12345 Musterstadt" -> ("12345", "Musterstadt"); without a postcode everything is the town
def split_plz_ort(text):
    text = to_text(text)
    match = re.match(r"(\d{4,5})\s+(.*)", text)
    return (match.group(1), match.group(2).strip()) if match else ("", text)


# one member as it will be imported: values {field: value}, include = taken over, estimated = fields guessed
class ImportRow:

    def __init__(self, number, values, unreadable):
        self.number = number            # row in the original file
        self.values = values
        self.unreadable = unreadable    # {field: text that is no valid value}
        self.include = True
        self.estimated = set()

    def name(self):
        return (self.values.get("first_name", "") + " " + self.values.get("last_name", "")).strip()

    # problems that prevent the import of this row: [(field, message)]
    def problems(self):
        found = []
        for field in MANDATORY:
            if field in self.unreadable:
                found.append((field, COLUMNS[field].heading + " ist nicht lesbar: " + self.unreadable[field]))
            elif not self.values.get(field) or (COLUMNS[field].kind == "date" and pd.isna(self.values[field])):
                found.append((field, COLUMNS[field].heading + " fehlt"))
        if self.values.get("status") == schema.LEFT and is_missing(self.values.get("exit_date")):
            found.append(("exit_date", "Austritt am fehlt (Status ausgetreten)"))
        return found

    # unreadable optional values are left out: shown as a hint, but they do not block
    def hints(self):
        return [COLUMNS[field].heading + " nicht lesbar: " + text for field, text in self.unreadable.items()
                if field not in MANDATORY]


def is_missing(value):
    return value is None or value == "" or (not isinstance(value, str) and pd.isna(value))


# the rows of the table as ImportRows. targets per column (suggest_columns), value_maps {"status"/"gender":
# {raw: target}}; without status column members are active, or left when their exit date has passed
def convert(table, targets, value_maps, today):
    rows = []
    for number, cells in table.rows:
        values, unreadable, notes = {}, {}, []
        for index, target in enumerate(targets):
            raw = cells[index]
            text = to_text(raw)
            if target == IGNORE or not text:
                continue
            if target == NOTE:
                notes.append(table.headings[index] + ": " + text)
            elif target == NAME_BOTH:
                values["last_name"], values["first_name"] = split_name(text)
            elif target == PLZ_ORT:
                values["plz"], values["ort"] = split_plz_ort(text)
            elif COLUMNS[target].kind == "date":
                date = parse_date(raw)
                if pd.isna(date):
                    unreadable[target] = text
                else:
                    values[target] = date
            elif target in ("status", "gender"):
                values[target] = value_maps.get(target, {}).get(text, suggest_value(target, text))
            elif target == "nr":
                values["nr"] = whole_number(raw)
            elif target == "note":
                notes.insert(0, text)
            else:
                values[target] = text
        if notes:
            values["note"] = "\n".join(notes)
        if "status" not in targets:
            exit_date = values.get("exit_date")
            values["status"] = schema.LEFT if exit_date is not None and exit_date <= today else schema.ACTIVE
        elif not text_of(cells, targets, "status"):   # empty cell: as chosen for "(leer)", active by default
            values["status"] = value_maps.get("status", {}).get("", schema.ACTIVE)
        rows.append(ImportRow(number, values, unreadable))
    estimate_genders(rows)
    return rows


def text_of(cells, targets, field):
    return to_text(cells[targets.index(field)]) if field in targets else ""


# the fields the list really has (a value that the app filled in or estimated is not one of them)
def given_fields(targets):
    found = set()
    for target in targets:
        if target == NAME_BOTH:
            found |= {"last_name", "first_name"}
        elif target == PLZ_ORT:
            found |= {"plz", "ort"}
        elif target == NOTE:
            found.add("note")
        elif target:
            found.add(target)
    return found


# the rows that are taken over get their numbers: a valid nr of the old list stays if it is unique, all others
# get the next free numbers
def assign_numbers(rows):
    taken = [row for row in rows if row.include]
    seen, keep = set(), set()
    for row in taken:
        nr = row.values.get("nr")
        if nr is not None and nr not in seen:
            seen.add(nr)
            keep.add(id(row))
    next_nr = max(seen, default=0)
    for row in taken:
        if id(row) not in keep:
            next_nr += 1
            row.values["nr"] = next_nr

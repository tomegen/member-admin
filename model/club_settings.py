from collections import namedtuple

from model import schema
from model.club_file import choice, sheet_rows, whole_number
from model.columns import normalize
from model.issue import Issue
from model.values import to_text

SHEET_NAME = "Blatt „Einstellungen“"   # shown in the data check instead of a member name
SETTINGS_COLUMNS = 11                  # A to K

# one row of the occasions; years None means "keine" (nothing of this kind is celebrated)
Occasion = namedtuple("Occasion", "kind years gift note")
PURPOSES = {"birthdays": schema.PASSIVE_BIRTHDAYS, "honors": schema.PASSIVE_HONORS,
            "statistics": schema.PASSIVE_STATISTICS}
YES_NO = ["ja", "nein"]


# the settings of a club, kept in its member file; what is not in the file has the default
class ClubSettings:

    def __init__(self, occasions=(), lists=None, general=None):
        self.occasions = list(occasions)
        self.lists = {name: list((lists or {}).get(name, [])) for name, _ in schema.VALUE_LISTS}
        self.general = {key: parse_general(key, value)[0] for key, value in schema.GENERAL_DEFAULTS}
        self.general.update(general or {})

    # the selectable numbers of a kind (birthday or honor); without any row of this kind the defaults apply
    def numbers(self, kind, defaults):
        rows = [occasion for occasion in self.occasions if occasion.kind == kind]
        if not rows:
            return list(defaults)
        return sorted({occasion.years for occasion in rows if occasion.years is not None})

    def gifts(self, kind):
        return {occasion.years: occasion.gift for occasion in self.occasions
                if occasion.kind == kind and occasion.years is not None and occasion.gift}

    # do passive members count for "birthdays", "honors" or "statistics"
    def passive(self, purpose):
        return self.general[PURPOSES[purpose]]

    @property
    def club_name(self):
        return self.general[schema.CLUB_NAME]

    @property
    def delete_after(self):
        return self.general[schema.DELETE_AFTER]

    @property
    def reminder_days(self):
        return self.general[schema.REMINDER_DAYS]

    # the parts that are saved and compared one by one: {label: value that compares}; notes are not compared
    def areas(self):
        found = {"Anlässe": tuple(sorted((o.kind, -1 if o.years is None else o.years, o.gift)
                                         for o in self.occasions))}
        found.update({name: tuple(values) for name, values in self.lists.items()})
        found.update(self.general)
        return found


# text of a general setting in the file -> (value, problem or None); with a problem the value is not used
def parse_general(key, value):
    text = to_text(value)
    if key == schema.CLUB_NAME:
        return text, None
    if key == schema.DELETE_AFTER:
        if text.casefold() in ("", "nie"):
            return None, None
        number = whole_number(value)
        return (number, None) if number is not None else (None, "„" + text + "“ ist keine Zahl von Jahren oder „nie“")
    if key == schema.REMINDER_DAYS:
        if text in ("", "0"):
            return 0, None
        number = whole_number(value)
        return (number, None) if number is not None else (None, "„" + text + "“ ist keine Zahl von Tagen")
    answer = choice(value, YES_NO)
    if answer:
        return answer == "ja", None
    return True, "„" + text + "“ ist nicht „ja“ oder „nein“"


# value of a general setting -> text in the file
def general_text(key, value):
    if key == schema.DELETE_AFTER:
        return "nie" if value is None else value
    if isinstance(value, bool):
        return "ja" if value else "nein"
    return value


# column numbers (1 = A) by their heading in row 1 of the settings sheet
def settings_columns(first_row):
    found = {}
    for index, heading in enumerate(first_row, start=1):
        found.setdefault(normalize(to_text(heading)), index)
    return found


# reads the sheet "Einstellungen": (ClubSettings, [Issue]); a missing sheet means defaults
def read_settings(book):
    if schema.SETTINGS_SHEET not in book.sheetnames:
        return ClubSettings(), []
    rows = sheet_rows(book[schema.SETTINGS_SHEET], SETTINGS_COLUMNS)
    if not rows:
        return ClubSettings(), []
    columns = settings_columns(rows[0])
    issues = []

    def problem(row, message):
        issues.append(Issue(row, SHEET_NAME, True, message))

    def column(heading):
        return columns.get(normalize(heading))

    occasions = []
    kind_column, years_column = column(schema.OCCASION_HEADINGS[0]), column(schema.OCCASION_HEADINGS[1])
    gift_column, note_column = column(schema.OCCASION_HEADINGS[2]), column(schema.OCCASION_HEADINGS[3])
    if kind_column is None or years_column is None:
        problem(1, "Die Überschriften „Anlass“ und „Jahre“ fehlen, es gelten die Standardwerte.")
    else:
        for row, values in enumerate(rows[1:], start=2):
            raw_kind, raw_years = to_text(values[kind_column - 1]), to_text(values[years_column - 1])
            if not raw_kind and not raw_years:
                continue
            kind = choice(raw_kind, [schema.BIRTHDAY, schema.HONOR])
            years = whole_number(values[years_column - 1])
            if not kind:
                problem(row, "Anlass „" + raw_kind + "“ ist weder Geburtstag noch Jubiläum.")
            elif years is None and raw_years.casefold() != "keine":
                problem(row, "„" + raw_years + "“ ist keine Zahl von Jahren (oder „keine“).")
            else:
                occasions.append(Occasion(kind, years,
                                          to_text(values[gift_column - 1]) if gift_column else "",
                                          to_text(values[note_column - 1]) if note_column else ""))

    lists = {}
    for name, _ in schema.VALUE_LISTS:
        index = column(name)
        values = [to_text(values[index - 1]) for values in rows[1:]] if index else []
        lists[name] = list(dict.fromkeys(value for value in values if value))   # without gaps and twins

    general = {}
    key_column, value_column = column(schema.GENERAL_HEADINGS[0]), column(schema.GENERAL_HEADINGS[1])
    if key_column and value_column:
        known = {normalize(key): key for key, _ in schema.GENERAL_DEFAULTS}
        for row, values in enumerate(rows[1:], start=2):
            key = known.get(normalize(to_text(values[key_column - 1])))
            if key is not None:
                value, message = parse_general(key, values[value_column - 1])
                if message:
                    problem(row, key + ": " + message + ", es gilt der Standardwert.")
                else:
                    general[key] = value
    return ClubSettings(occasions, lists, general), issues

import uuid

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter, quote_sheetname
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

from model import schema

ROWS = 1000          # rows prepared with date format and checks
LIST_ROWS = 200      # rows of each list in the settings sheet
LAST_DATE = 73415    # excel serial number of 01.01.2100
TEXT_FIELDS = ("plz", "phone", "mobile_phone", "iban")   # stored as text, so a leading 0 stays

INSTRUCTIONS = [
    "So pflegen Sie die Mitgliederliste",
    "",
    "• Auf dem Blatt „Mitglieder“ steht pro Zeile ein Mitglied. Die Überschriften in Zeile 1 nicht ändern.",
    "  Spalten dürfen verschoben und eigene Spalten ergänzt werden.",
    "• Blau hinterlegte Spalten sind Pflicht: Name, Vorname, Geschlecht, Geburtstag, Eintritt, Status.",
    "• „Nr“ bei neuen Mitgliedern leer lassen, die App vergibt die Nummer. Nummern nie ändern oder doppelt vergeben.",
    "• Austritt: Status „ausgetreten“ wählen und „Austritt am“ eintragen. Die Zeile nicht löschen.",
    "• Datumsfelder als Datum eingeben, z. B. 24.12.1960 (Excel prüft das).",
    "• Abteilungen, Beitragsklassen und Funktionen werden im Blatt „Einstellungen“ gepflegt und erscheinen dann",
    "  als Auswahl. Dort steht auch, welche Geburtstage und Jubiläen gefeiert werden (eine Zeile je Anlass).",
    "• Das Blatt „Änderungsprotokoll“ schreibt die App (nur Änderungen, die über die App gemacht werden).",
    "• Die Datei kann in Dropbox, OneDrive, Google Drive oder Nextcloud liegen und auch am Smartphone bearbeitet",
    "  werden. Bitte nicht gleichzeitig am selben Mitglied arbeiten. Danach in der App „Neu einlesen“ klicken.",
    "• Dieses Blatt und die Angaben darunter nicht löschen, die App erkennt daran ihre Datei.",
]


def write_headings(sheet, columns):
    # columns: (heading, width, mandatory?, hint or None)
    for index, (heading, width, mandatory, hint) in enumerate(columns, start=1):
        cell = sheet.cell(row=1, column=index, value=heading)
        cell.font = Font(bold=True, color="FFFFFF" if mandatory else "000000")
        cell.fill = PatternFill("solid", fgColor="2563EB" if mandatory else "D9D9D9")
        cell.alignment = Alignment(vertical="center")
        if hint:
            cell.comment = Comment(hint, "Mitgliederverwaltung")
        sheet.column_dimensions[cell.column_letter].width = width
    sheet.row_dimensions[1].height = 24
    sheet.freeze_panes = "A2"


def date_check():
    return DataValidation(type="date", operator="between", formula1="1", formula2=str(LAST_DATE),
                          showErrorMessage=True, errorTitle="Kein Datum",
                          error="Bitte ein Datum eingeben, z. B. 24.12.1960.")


def number_check(highest=999999):
    return DataValidation(type="whole", operator="between", formula1="1", formula2=str(highest),
                          showErrorMessage=True, errorTitle="Keine Zahl", error="Bitte eine ganze Zahl eingeben.")


# a dropdown; the values are written inline ("a,b") or are a defined name of a list in the settings sheet.
# lists of the club only warn: they may still be empty when somebody starts typing
def list_check(values=None, name=None):
    if values:
        return DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True,
                              showErrorMessage=True, errorTitle="Ungültiger Wert",
                              error="Bitte einen Wert aus der Auswahl nehmen: " + ", ".join(values) + ".")
    return DataValidation(type="list", formula1=name, allow_blank=True, showErrorMessage=True, errorStyle="warning",
                          errorTitle="Unbekannter Wert",
                          error="Dieser Wert steht nicht in der Liste im Blatt „Einstellungen“. Trotzdem übernehmen?")


def check_for(kind):
    if kind == "date":
        return date_check()
    if kind == "number":
        return number_check()
    if kind == "gender":
        return list_check(schema.GENDERS)
    if kind == "status":
        return list_check(schema.STATUSES)
    if kind.startswith("list:"):
        return list_check(name=kind.split(":", 1)[1])
    return None


def add_check(sheet, check, letter, last_row):
    if check is not None:
        sheet.add_data_validation(check)
        check.add(letter + "2:" + letter + str(last_row))


def write_members_sheet(sheet):
    sheet.title = schema.MEMBERS_SHEET
    columns = schema.MEMBER_COLUMNS
    write_headings(sheet, [(c.heading, c.width, c.mandatory, c.hint) for c in columns])
    sheet.freeze_panes = "D2"   # nr, name and first name stay visible when scrolling to the right (also on phones)
    sheet.auto_filter.ref = "A1:" + get_column_letter(len(columns)) + str(ROWS + 1)
    for index, column in enumerate(columns, start=1):
        letter = get_column_letter(index)
        add_check(sheet, check_for(column.kind), letter, ROWS + 1)
        number_format = "DD.MM.YYYY" if column.kind == "date" else "@" if column.field in TEXT_FIELDS else None
        if number_format:
            for row in range(2, ROWS + 2):
                sheet.cell(row=row, column=index).number_format = number_format


def write_functions_sheet(sheet):
    hints = ["Mitgliedsnummer aus dem Blatt „Mitglieder“.", "Name, nur zur Lesbarkeit (maßgeblich ist die Nr).",
             "Auswahl aus dem Blatt „Einstellungen“.", "Beginn, z. B. 01.04.2020.", "Ende (leer = bis heute).", None]
    widths = [7, 24, 22, 12, 12, 30]
    mandatory = [True, False, True, False, False, False]
    write_headings(sheet, list(zip(schema.FUNCTION_HEADINGS, widths, mandatory, hints)))
    add_check(sheet, number_check(), "A", ROWS + 1)
    add_check(sheet, list_check(name="Funktionen"), "C", ROWS + 1)
    for letter in ("D", "E"):
        add_check(sheet, date_check(), letter, ROWS + 1)
        for row in range(2, ROWS + 2):
            sheet[letter + str(row)].number_format = "DD.MM.YYYY"


# without config the occasions stay empty: then the defaults apply (used when the sheet is rebuilt)
def write_settings_sheet(sheet, config):
    write_headings(sheet, [
        ("Anlass", 13, True, "Geburtstag oder Jubiläum. Eine Zeile je Anlass, der gefeiert wird."),
        ("Jahre", 8, True, "z. B. 60 (Geburtstag) oder 25 (Jahre Mitgliedschaft)."),
        ("Geschenk/Maßnahme", 28, False, "z. B. Präsentkorb, Urkunde, Besuch durch den Vorstand."),
        ("Bemerkung", 24, False, None),
    ])
    occasions = [] if config is None else ([(schema.BIRTHDAY, n) for n in config.birthday_config] +
                                           [(schema.HONOR, n) for n in config.honor_config])
    for row, (occasion, years) in enumerate(occasions, start=2):
        sheet.cell(row=row, column=1, value=occasion)
        sheet.cell(row=row, column=2, value=years)
    add_check(sheet, list_check([schema.BIRTHDAY, schema.HONOR]), "A", LIST_ROWS + 1)
    years = number_check(120)
    years.errorStyle = "warning"   # "keine" is allowed: no birthdays at all
    add_check(sheet, years, "B", LIST_ROWS + 1)

    for name, letter in schema.VALUE_LISTS:
        cell = sheet[letter + "1"]
        cell.value = name
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9D9D9")
        cell.comment = Comment("Ein Wert je Zeile. Erscheint als Auswahl im Blatt „Mitglieder“ bzw. „Funktionen“.",
                               "Mitgliederverwaltung")
        sheet.column_dimensions[letter].width = 18
        reference = quote_sheetname(schema.SETTINGS_SHEET) + "!$" + letter + "$2:$" + letter + "$" + str(LIST_ROWS + 1)
        sheet.parent.defined_names[name] = DefinedName(name, attr_text=reference)

    for column, (heading, width) in zip(("J", "K"), zip(schema.GENERAL_HEADINGS, (26, 22))):
        cell = sheet[column + "1"]
        cell.value = heading
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9D9D9")
        sheet.column_dimensions[column].width = width
    for row, (key, value) in enumerate(schema.GENERAL_DEFAULTS, start=2):
        sheet["J" + str(row)] = key
        sheet["K" + str(row)] = value


def write_log_sheet(sheet):
    widths = [17, 16, 7, 24, 14, 18, 24, 24]
    write_headings(sheet, [(heading, width, False, None) for heading, width in zip(schema.LOG_HEADINGS, widths)])


def write_info_sheet(sheet):
    for row, text in enumerate(INSTRUCTIONS, start=1):
        sheet.cell(row=row, column=1, value=text)
    sheet.cell(row=1, column=1).font = Font(bold=True, size=14)
    sheet.column_dimensions["A"].width = 110
    sheet.column_dimensions["B"].width = 40
    write_info_keys(sheet, len(INSTRUCTIONS) + 2, [schema.SCHEMA_KEY, schema.FILE_ID_KEY, schema.NEXT_NR_KEY])


# the keys the app reads in column A, their values in column B (a new file id); starting at the given row
def write_info_keys(sheet, row, keys):
    nr_column = quote_sheetname(schema.MEMBERS_SHEET) + "!A:A"
    values = {schema.SCHEMA_KEY: schema.SCHEMA_VERSION, schema.FILE_ID_KEY: str(uuid.uuid4()),
              schema.NEXT_NR_KEY: "=MAX(" + nr_column + ")+1"}
    for offset, key in enumerate(keys):
        sheet.cell(row=row + offset, column=1, value=key).font = Font(bold=True)
        sheet.cell(row=row + offset, column=2, value=values[key]).alignment = Alignment(horizontal="left")


# an empty member list in the standard format: all sheets, dropdowns and checks for the input, a new file id;
# the occasions in the settings sheet are the current choices (config.ini or the settings of the app)
def write_member_template(path, config):
    book = Workbook()
    write_members_sheet(book.active)
    write_functions_sheet(book.create_sheet(schema.FUNCTIONS_SHEET))
    write_settings_sheet(book.create_sheet(schema.SETTINGS_SHEET), config)
    write_log_sheet(book.create_sheet(schema.LOG_SHEET))
    write_info_sheet(book.create_sheet(schema.INFO_SHEET))
    book.save(path)
    return True

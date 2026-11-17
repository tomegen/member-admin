from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from model.columns import FIELDS

ROWS = 1000          # rows prepared with date format and checks
LAST_DATE = 73415    # excel serial number of 01.01.2100

# (field, width, hint shown when the heading cell is selected); the heading and mandatory? come from FIELDS
COLUMNS = [
    ("last_name", 20, "Nachname des Mitglieds."),
    ("first_name", 18, "Vorname des Mitglieds."),
    ("birthday", 14, "Geburtsdatum, z. B. 24.12.1960. Für Geburtstage."),
    ("member_since", 14, "Eintrittsdatum, z. B. 01.04.2005. Für Ehrungen."),
    ("member", 10, "1 = aktives Mitglied, 0 = ausgetreten. Zeilen bitte nicht löschen, sondern auf 0 setzen."),
    ("street", 24, "Straße und Hausnummer (freiwillig)."),
    ("plz", 8, "Postleitzahl (freiwillig)."),
    ("ort", 18, "Wohnort (freiwillig)."),
    ("phone", 16, "Telefon (freiwillig)."),
    ("mobile_phone", 16, "Mobilnummer (freiwillig)."),
    ("iban", 30, "IBAN (freiwillig)."),
    ("reference", 16, "Mandatsreferenz (freiwillig)."),
]

INSTRUCTIONS = [
    "So füllen Sie die Mitgliederliste aus",
    "",
    "• Auf dem Blatt „Mitglieder“ steht pro Zeile ein Mitglied. Die Überschriften in Zeile 1 nicht ändern.",
    "• Blau hinterlegte Spalten sind Pflicht, graue sind freiwillig.",
    "• Datumsfelder als Datum eingeben, z. B. 24.12.1960 (Excel prüft das).",
    "• „Mitglied“: 1 = aktiv, 0 = ausgetreten. Ausgetretene Personen nicht löschen, sondern auf 0 setzen.",
    "• Die Liste kann auch auf dem Smartphone gepflegt werden. Danach in der App „Neu einlesen“ klicken.",
    "• Dieses Blatt darf stehen bleiben, die App liest nur das erste Blatt („Mitglieder“).",
]


# an empty member list with the expected columns, date format and dropdown / checks for the input
def write_member_template(path, config):
    book = Workbook()
    sheet = book.active
    sheet.title = "Mitglieder"

    for index, (field, width, hint) in enumerate(COLUMNS, start=1):
        attribute, _, _, mandatory = FIELDS[field]
        cell = sheet.cell(row=1, column=index, value=getattr(config, attribute))
        cell.font = Font(bold=True, color="FFFFFF" if mandatory else "000000")
        cell.fill = PatternFill("solid", fgColor="2563EB" if mandatory else "D9D9D9")
        cell.alignment = Alignment(vertical="center")
        cell.comment = Comment(hint, "Mitgliederverwaltung")
        sheet.column_dimensions[cell.column_letter].width = width
    sheet.row_dimensions[1].height = 24
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = "A1:" + sheet.cell(row=1, column=len(COLUMNS)).column_letter + str(ROWS + 1)

    dates = DataValidation(type="date", operator="between", formula1="1", formula2=str(LAST_DATE),
                           showErrorMessage=True, errorTitle="Kein Datum",
                           error="Bitte ein Datum eingeben, z. B. 24.12.1960.")
    status = DataValidation(type="list", formula1='"1,0"', allow_blank=True, showErrorMessage=True,
                            errorTitle="Ungültiger Wert", error="Bitte 1 (aktiv) oder 0 (ausgetreten) wählen.")
    sheet.add_data_validation(dates)
    sheet.add_data_validation(status)
    positions = {field: index for index, (field, *_) in enumerate(COLUMNS, start=1)}
    for row in range(2, ROWS + 2):
        for field in ("birthday", "member_since"):
            sheet.cell(row=row, column=positions[field]).number_format = "DD.MM.YYYY"
    letters = {field: sheet.cell(row=1, column=position).column_letter for field, position in positions.items()}
    dates.add(letters["birthday"] + "2:" + letters["birthday"] + str(ROWS + 1))
    dates.add(letters["member_since"] + "2:" + letters["member_since"] + str(ROWS + 1))
    status.add(letters["member"] + "2:" + letters["member"] + str(ROWS + 1))

    help_sheet = book.create_sheet("Anleitung")
    for row, text in enumerate(INSTRUCTIONS, start=1):
        help_sheet.cell(row=row, column=1, value=text)
    help_sheet.cell(row=1, column=1).font = Font(bold=True, size=14)
    help_sheet.column_dimensions["A"].width = 110

    book.save(path)
    return True


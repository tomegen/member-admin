import pandas as pd

COLUMNS = ["Anlass", "Datum", "Vorname", "Name", "Geburtstag", "Mitglied seit", "Telefon", "Mobil",
           "Straße", "PLZ", "Ort"]
MINIMAL_COLUMNS = COLUMNS[:4]   # without birthday, phone and address


# one table row per entry, sorted by date; used for the excel export and the preview in the app
def entries_to_rows(entries, occasion, minimal=False):
    rows = []
    for entry in sorted(entries, key=lambda e: (e.date, e.member.last_name, e.member.first_name)):
        member = entry.member
        row = [occasion(entry.number), entry.date, member.first_name, member.last_name, member.birthday,
               member.member_since, member.phone_number, member.mobile_phone, member.street, member.plz,
               member.ort]
        rows.append(row[:len(MINIMAL_COLUMNS)] if minimal else row)
    return rows


# write the entries into an excel file (dates as real excel dates)
def write_entries_into_xlsx(entries, occasion, xlsx_filename, minimal=False):
    table = pd.DataFrame(entries_to_rows(entries, occasion, minimal), columns=MINIMAL_COLUMNS if minimal else COLUMNS)
    with pd.ExcelWriter(xlsx_filename, engine="openpyxl", datetime_format="DD.MM.YYYY") as writer:
        table.to_excel(writer, index=False, sheet_name="Auswertung")
        sheet = writer.sheets["Auswertung"]
        for column in sheet.columns:
            width = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column)
            sheet.column_dimensions[column[0].column_letter].width = min(max(width + 2, 12), 40)
    return True

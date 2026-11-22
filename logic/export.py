import pandas as pd

COLUMNS = ["Anlass", "Datum", "Vorname", "Name", "Geburtstag", "Mitglied seit", "Telefon", "Mobil",
           "Straße", "PLZ", "Ort"]
MINIMAL_COLUMNS = COLUMNS[:4]   # without birthday, phone and address
GIFT_COLUMN = "Geschenk/Maßnahme"


# one table row per entry, sorted by date; with gifts ({number: gift} of the club) a column for them after the date
def entries_to_rows(entries, occasion, minimal=False, gifts=None):
    rows = []
    for entry in sorted(entries, key=lambda e: (e.date, e.member.last_name, e.member.first_name)):
        member = entry.member
        row = [occasion(entry.number), entry.date, member.first_name, member.last_name, member.birthday,
               member.member_since, member.phone_number, member.mobile_phone, member.street, member.plz,
               member.ort]
        if minimal:
            row = row[:len(MINIMAL_COLUMNS)]
        elif gifts:
            row.insert(2, gifts.get(entry.number, ""))
        rows.append(row)
    return rows


def columns_for(minimal=False, gifts=None):
    if minimal:
        return MINIMAL_COLUMNS
    return COLUMNS[:2] + [GIFT_COLUMN] + COLUMNS[2:] if gifts else COLUMNS


# write the entries into an excel file (dates as real excel dates)
def write_entries_into_xlsx(entries, occasion, xlsx_filename, minimal=False, gifts=None):
    table = pd.DataFrame(entries_to_rows(entries, occasion, minimal, gifts), columns=columns_for(minimal, gifts))
    with pd.ExcelWriter(xlsx_filename, engine="openpyxl", datetime_format="DD.MM.YYYY") as writer:
        table.to_excel(writer, index=False, sheet_name="Auswertung")
        sheet = writer.sheets["Auswertung"]
        for column in sheet.columns:
            width = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column)
            sheet.column_dimensions[column[0].column_letter].width = min(max(width + 2, 12), 40)
    return True

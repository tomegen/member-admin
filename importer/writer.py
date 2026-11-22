import os
from datetime import datetime

from openpyxl import load_workbook

from importer.mapping import assign_numbers
from logic.template import write_member_template
from model import schema
from model.club_file import heading_columns, sheet_rows
from model.club_settings import SETTINGS_COLUMNS
from store.changes import LogEntry, append_log, column_of, write_column, write_general
from store.repair import repair
from store.sheet import MemberSheet


# a new standard file with the rows that are taken over; the original list is not touched. Departments and fee
# classes found in the list become the choices in the settings sheet; the numbers of the old list stay if unique
def write_standard_file(path, rows, config, source_name, editor, club_name="", now=None):
    now = now or datetime.now().replace(microsecond=0)
    taken = [row for row in rows if row.include]
    assign_numbers(taken)
    write_member_template(path, config)
    book = load_workbook(path)
    members = MemberSheet(book)
    for number, row in enumerate(sorted(taken, key=lambda row: row.values["nr"]), start=2):
        for field, value in row.values.items():
            members.set(number, field, value)

    sheet = book[schema.SETTINGS_SHEET]
    columns = heading_columns(sheet_rows(sheet, SETTINGS_COLUMNS)[0])
    for name, field in (("Abteilungen", "department"), ("Beitragsklassen", "fee_class")):
        values = sorted({row.values[field] for row in taken if row.values.get(field)})
        write_column(sheet, column_of(columns, name), values)
    if club_name:
        write_general(sheet, columns, schema.CLUB_NAME, club_name)

    repair(book, members)   # the checks reach below the last member, also for long lists
    append_log(book, [LogEntry(None, "", "Import", "", "", str(len(taken)) + " Mitglieder aus " +
                               os.path.basename(source_name))], editor, now)
    book.save(path)
    return len(taken)

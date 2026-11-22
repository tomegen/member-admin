from openpyxl.utils import get_column_letter, quote_sheetname
from openpyxl.workbook.defined_name import DefinedName

from logic.template import (LIST_ROWS, ROWS, add_check, check_for, write_functions_sheet, write_info_keys,
                            write_info_sheet, write_log_sheet, write_settings_sheet)
from model import schema
from model.club_file import read_info
from store.sheet import last_used_row

# Excel on phones, Google Sheets and LibreOffice sometimes drop dropdowns, checks or names. Before every save the
# app puts back what the standard needs; own columns, own checks and the data of the club stay as they are.


def repair(book, member_sheet):
    for column in schema.MEMBER_COLUMNS:
        if column.field not in member_sheet.columns:
            member_sheet.add_column(column)
    renew_member_checks(member_sheet)

    for title, write in ((schema.FUNCTIONS_SHEET, write_functions_sheet),
                         (schema.SETTINGS_SHEET, lambda sheet: write_settings_sheet(sheet, None)),
                         (schema.LOG_SHEET, write_log_sheet)):
        if title not in book.sheetnames:
            write(book.create_sheet(title))
    if schema.INFO_SHEET not in book.sheetnames:
        write_info_sheet(book.create_sheet(schema.INFO_SHEET))
    else:
        info = read_info(book)
        missing = [key for key in (schema.SCHEMA_KEY, schema.FILE_ID_KEY) if key not in info]
        if missing:
            sheet = book[schema.INFO_SHEET]
            write_info_keys(sheet, last_used_row(sheet) + 2, missing)

    for name, letter in schema.VALUE_LISTS:
        if name not in book.defined_names:
            reference = (quote_sheetname(schema.SETTINGS_SHEET) + "!$" + letter + "$2:$" + letter + "$" +
                         str(LIST_ROWS + 1))
            book.defined_names[name] = DefinedName(name, attr_text=reference)


# the checks of the standard columns are written again where the columns are now (they may have been moved);
# checks of other columns are kept. The rows reach well below the last member
def renew_member_checks(member_sheet):
    sheet = member_sheet.sheet
    ours = set(member_sheet.columns.values())
    sheet.data_validations.dataValidation = [
        check for check in sheet.data_validations.dataValidation
        if not any(ours & set(range(area.min_col, area.max_col + 1)) for area in check.sqref.ranges)]
    last_row = max(ROWS, member_sheet.last_row() + ROWS // 2) + 1
    for column in schema.MEMBER_COLUMNS:
        add_check(sheet, check_for(column.kind), get_column_letter(member_sheet.columns[column.field]), last_row)

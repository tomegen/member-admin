import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from model import schema
from model.club_file import cell_key, members_sheet, peek, whole_number
from model.columns import normalize

COLUMNS_BY_HEADING = {normalize(column.heading): column for column in schema.MEMBER_COLUMNS}
COLUMNS_BY_FIELD = {column.field: column for column in schema.MEMBER_COLUMNS}


def is_empty(value):
    return cell_key(value) == ""


# sets the value of a cell, also to empty (sheet.cell(..., value=None) would leave the old value)
def write_cell(sheet, row, column, value):
    cell = sheet.cell(row=row, column=column)
    cell.value = value
    return cell


# last row of a sheet with content; prepared rows with only formats or dropdowns do not count
def last_used_row(sheet):
    return max((row for (row, _), cell in sheet._cells.items() if row > 1 and not is_empty(cell.value)), default=1)


# python value -> value for a cell of this column: dates as date, nr as int, everything else as text, empty as None
def cell_value(column, value):
    if value is None or (not isinstance(value, str) and pd.isna(value)) or str(value).strip() == "":
        return None
    if column.kind == "date":
        return pd.Timestamp(value).date()
    if column.kind == "number":
        return int(value)
    return str(value).strip()


# the sheet "Mitglieder" of a workbook opened for writing; columns are found by their heading (they may be moved)
class MemberSheet:

    def __init__(self, book):
        self.sheet = members_sheet(book)
        self.columns = {}   # field -> column number
        for cell in self.sheet[1]:
            column = COLUMNS_BY_HEADING.get(normalize(cell.value if cell.value is not None else ""))
            if column is not None and column.field not in self.columns:
                self.columns[column.field] = cell.column

    def get(self, row, field):
        return peek(self.sheet, row, self.columns[field]) if field in self.columns else None

    def keys(self, row):
        return {field: cell_key(self.get(row, field)) for field in self.columns}

    def set(self, row, field, value):
        column = COLUMNS_BY_FIELD[field]
        cell = write_cell(self.sheet, row, self.columns[field], cell_value(column, value))
        if column.kind == "date":
            cell.number_format = "DD.MM.YYYY"

    def name(self, row):
        return (cell_key(self.get(row, "first_name")) + " " + cell_key(self.get(row, "last_name"))).strip()

    def last_row(self):
        return last_used_row(self.sheet)

    # rows with content: [(row, nr or None)]; a nr that is not a whole number counts as None
    def rows(self):
        found = []
        for row in range(2, self.last_row() + 1):
            if any(not is_empty(self.get(row, field)) for field in self.columns):
                found.append((row, whole_number(self.get(row, "nr"))))
        return found

    def rows_with(self, nr):
        return [row for row, number in self.rows() if number == nr]

    def highest_nr(self):
        return max((number for _, number in self.rows() if number is not None), default=0)

    # a column of the standard that is missing (e.g. deleted by hand) is added after the last heading
    def add_column(self, column):
        index = max((cell.column for cell in self.sheet[1] if not is_empty(cell.value)), default=0) + 1
        cell = self.sheet.cell(row=1, column=index, value=column.heading)
        cell.font = Font(bold=True, color="FFFFFF" if column.mandatory else "000000")
        cell.fill = PatternFill("solid", fgColor="2563EB" if column.mandatory else "D9D9D9")
        cell.alignment = Alignment(vertical="center")
        self.sheet.column_dimensions[cell.column_letter].width = column.width
        self.columns[column.field] = index

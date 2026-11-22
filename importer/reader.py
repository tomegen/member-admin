import csv
import io
import os
from collections import Counter

import pandas as pd

from model.club_file import open_book, read_bytes
from model.values import to_text

ENCODINGS = ["utf-8-sig", "cp1252"]   # utf-8 with or without BOM, else the usual windows encoding (umlauts)
DELIMITERS = [";", ",", "\t"]
DELIMITER_NAMES = {";": "Semikolon (;)", ",": "Komma (,)", "\t": "Tabulator"}


class SourceError(Exception):
    pass


# a list to import as it is in its file: all rows of one sheet (lists of cell values), nothing interpreted yet
class Source:

    def __init__(self, path, rows, sheet_names=(), sheet=None, encoding=None, delimiter=None):
        self.path = path
        self.rows = rows
        self.sheet_names = list(sheet_names)
        self.sheet = sheet
        self.encoding = encoding
        self.delimiter = delimiter

    @property
    def is_csv(self):
        return self.encoding is not None


def is_empty_row(row):
    return all(to_text(value) == "" for value in row)


# reads .xlsx, .xls or .csv; sheet (excel), encoding and delimiter (csv) are found when not given
def read_source(path, sheet=None, encoding=None, delimiter=None):
    extension = os.path.splitext(path)[1].lower()
    try:
        if extension in (".csv", ".txt"):
            return read_csv(path, encoding, delimiter)
        if extension == ".xls":
            return read_xls(path, sheet)
        return read_xlsx(path, sheet)
    except SourceError:
        raise
    except Exception as error:
        raise SourceError("Die Datei konnte nicht gelesen werden. Ist es eine Excel-Datei (.xlsx, .xls) oder eine "
                          "CSV-Datei, und ist sie vielleicht noch in einem anderen Programm geöffnet?\n\n"
                          "Technische Details: " + str(error))


def first_sheet_with_data(sheets):
    for name, rows in sheets.items():
        if any(not is_empty_row(row) for row in rows):
            return name
    return next(iter(sheets))


def pick(sheets, sheet):
    sheet = sheet if sheet in sheets else first_sheet_with_data(sheets)
    return sheet, sheets[sheet]


def read_xlsx(path, sheet):
    book = open_book(read_bytes(path))
    sheets = {name: [list(row) for row in book[name].iter_rows(values_only=True)] for name in book.sheetnames}
    sheet, rows = pick(sheets, sheet)
    return Source(path, rows, book.sheetnames, sheet)


def read_xls(path, sheet):
    frames = pd.read_excel(path, sheet_name=None, header=None, dtype=object)
    sheets = {name: [[None if not isinstance(value, str) and pd.isna(value) else value for value in row]
                     for row in frame.itertuples(index=False)] for name, frame in frames.items()}
    sheet, rows = pick(sheets, sheet)
    return Source(path, rows, list(frames), sheet)


def read_csv(path, encoding, delimiter):
    data = read_bytes(path)
    for candidate in ([encoding] if encoding else ENCODINGS):
        try:
            text = data.decode(candidate)
            encoding = candidate
            break
        except UnicodeDecodeError:
            continue
    else:
        raise SourceError("Die Zeichen in der CSV-Datei konnten nicht gelesen werden (unbekannte Kodierung).")
    delimiter = delimiter or guess_delimiter(text)
    rows = [row for row in csv.reader(io.StringIO(text), delimiter=delimiter)]
    return Source(path, rows, encoding=encoding, delimiter=delimiter)


# the delimiter that splits the most of the first lines into the same number of columns (more than one);
# a title line above the table has one column with every delimiter and does not count
def guess_delimiter(text):
    lines = [line for line in text.splitlines()[:20] if line.strip()]

    def score(delimiter):
        counts = Counter(len(next(csv.reader([line], delimiter=delimiter))) for line in lines)
        columns, number = max(((c, n) for c, n in counts.items() if c > 1), key=lambda item: (item[1], item[0]),
                              default=(0, 0))
        return number, columns
    return max(DELIMITERS, key=score)

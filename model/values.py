import datetime
import numbers

import pandas as pd


# excel cells formatted as number hold a serial day number (not nanoseconds)
def parse_date(value):
    if pd.isna(value):
        return pd.NaT
    if isinstance(value, datetime.date):  # also datetime, as openpyxl reads date cells
        return pd.Timestamp(value).normalize()
    if isinstance(value, numbers.Real):  # also numpy numbers
        return pd.to_datetime(value, unit="D", origin="1899-12-30")
    # iso text (1967-06-01) is read as it is, german text (01.06.1967) is read day first
    parsed = pd.to_datetime(value, format="ISO8601", errors="coerce")
    if pd.isna(parsed):
        parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    return parsed


# cell content as text: empty cells become "", numbers like 12345.0 become "12345"
def to_text(value):
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()

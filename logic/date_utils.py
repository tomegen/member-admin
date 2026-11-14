import pandas as pd


# move a date by a number of years; 29.02. falls back to 28.02. if the target year is no leap year
def shift_years(date, years):
    year = date.year + years
    day = date.day
    if date.month == 2 and day == 29 and not pd.Timestamp(year=year, month=1, day=1).is_leap_year:
        day = 28
    return pd.Timestamp(year=year, month=date.month, day=day)

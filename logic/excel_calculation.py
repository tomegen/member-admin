import pandas as pd



def calculate_member_count(filename):
    sheet = pd.read_excel(filename, sheet_name=0)
    column_values = sheet[MEMBER]
    members = 0
    for x in column_values:
        members = members + x
    print(members)
    return members


def calculate_birthdays(filename):
    sheet = pd.read_excel(filename, sheet_name=0)
    column_values = sheet[BIRTHDAY]
    members = M
    for x in column_values:
        print(pd.to_datetime(x))
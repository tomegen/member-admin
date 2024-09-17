import pandas as pd
import os


# write all the honors into a txt file
def write_honors_into_txt(members, honors, from_date, to_date, txt_filename):
    text = "Ehrungen vom " + str(from_date.strftime('%d.%m.%Y')) + " bis zum " + str(to_date.strftime('%d.%m.%Y'))
    text += os.linesep *2

    # loop through all the honors
    for honor in honors:
        print("Process birthday: " + str(honor))
        text += str(honor) + " Jahre Ehrung: "
        text += os.linesep
        for member in members:
            if is_honor(member, honor, from_date, to_date):
                text = member.print(text)
        text += os.linesep*3

    # Write the text to the selected file
    with open(txt_filename, "w") as file:
        file.write(text)
    return True


# Calculate if a member will get an honor
def is_honor(member, honor, from_date, to_date):
    if member.member == 0:
        return False
    from_date = pd.Timestamp(year=from_date.year - honor, month=from_date.month, day=from_date.day)
    to_date = pd.Timestamp(year=to_date.year - honor, month=to_date.month, day=to_date.day)

    return (member.member_since >= from_date) & (member.member_since <= to_date)

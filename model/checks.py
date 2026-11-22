import pandas as pd

from logic.date_utils import shift_years
from model.issue import Issue

MAX_AGE = 110


# age in full years on the given day (a leap day birthday counts on 28.02. in other years, as everywhere else)
def age_on(birthday, day):
    years = day.year - birthday.year
    return years - 1 if shift_years(birthday, years) > day else years


# findings that do not depend on a single empty cell: members is [(excel row, Member)]
def plausibility_issues(rows, today):
    issues = []
    names = {}
    for row, member in rows:
        name = member.full_name() or "(ohne Namen)"
        active = member.is_member
        birthday, since = member.birthday, member.member_since

        if not pd.isna(birthday):
            age = age_on(birthday, today)
            if age < 0 or age > MAX_AGE:
                issues.append(Issue(row, name, active, "Der Geburtstag ergibt ein Alter von " + str(age) +
                                    " Jahren – Tippfehler beim Jahr?"))
        if not pd.isna(since) and since > today + pd.Timedelta(days=366):
            issues.append(Issue(row, name, active, "Eintritt liegt mehr als ein Jahr in der Zukunft – "
                                                   "Tippfehler beim Jahr?"))
        if not pd.isna(birthday) and not pd.isna(since) and since < birthday:
            issues.append(Issue(row, name, active, "Eintritt liegt vor dem Geburtstag."))

        # same name and same birthday: most likely entered twice (same name only is often family)
        if member.full_name() and not pd.isna(birthday):
            key = (member.full_name().casefold(), birthday)
            if key in names:
                issues.append(Issue(row, name, active, "Möglicherweise doppelt eingetragen (gleicher Name und "
                                                       "Geburtstag wie in Zeile " + str(names[key]) + ")."))
            else:
                names[key] = row
    return issues

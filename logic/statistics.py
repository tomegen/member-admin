import pandas as pd

from model.checks import age_on

# age groups as the sport associations ask for them (Bestandserhebung): (from, to); to = None is open ended
AGE_GROUPS = [(0, 6), (7, 14), (15, 18), (19, 26), (27, 40), (41, 60), (61, None)]


def age_group_label(low, high):
    if low == 0:
        return "bis " + str(high) + " Jahre"
    if high is None:
        return "über " + str(low - 1) + " Jahre"
    return str(low) + " bis " + str(high) + " Jahre"


# numbers of the active members on the given day: counts per age group, average age and membership duration
class Statistics:

    def __init__(self, members, year, stichtag, groups=AGE_GROUPS):
        active = [member for member in members if member.member == 1]
        self.year = year
        self.stichtag = stichtag
        self.active = len(active)
        self.new_members = sum(1 for member in active
                               if not pd.isna(member.member_since) and member.member_since.year == year)

        ages = [age_on(member.birthday, stichtag) for member in active if not pd.isna(member.birthday)]
        self.unknown_birthday = len(active) - len(ages)
        self.average_age = sum(ages) / len(ages) if ages else None
        self.groups = [(age_group_label(low, high),
                        sum(1 for age in ages if age >= low and (high is None or age <= high)))
                       for low, high in groups]
        self.outside_groups = len(ages) - sum(count for _, count in self.groups)  # e.g. a birthday in the future

        years = [age_on(member.member_since, stichtag) for member in active
                 if not pd.isna(member.member_since) and member.member_since <= stichtag]
        self.average_membership_years = sum(years) / len(years) if years else None

    def rows(self):
        return [("Aktive Mitglieder", self.active),
                ("Neue Mitglieder " + str(self.year), self.new_members),
                ("Durchschnittsalter am Stichtag", self.average_age),
                ("Durchschnittliche Mitgliedsdauer in Jahren", self.average_membership_years),
                ("Ohne bekannten Geburtstag", self.unknown_birthday)]


def write_statistics_into_xlsx(statistics, xlsx_filename):
    stichtag = statistics.stichtag.strftime("%d.%m.%Y")
    figures = pd.DataFrame([(name, "" if value is None else round(value, 1) if isinstance(value, float) else value)
                            for name, value in statistics.rows()], columns=["Kennzahl", "Wert"])
    total = max(sum(count for _, count in statistics.groups), 1)
    groups = pd.DataFrame([(label, count, round(count / total * 100, 1)) for label, count in statistics.groups],
                          columns=["Altersgruppe am " + stichtag, "Anzahl", "Anteil in %"])
    with pd.ExcelWriter(xlsx_filename, engine="openpyxl") as writer:
        figures.to_excel(writer, index=False, sheet_name="Kennzahlen")
        groups.to_excel(writer, index=False, sheet_name="Altersgruppen")
        for sheet in writer.sheets.values():
            for column in sheet.columns:
                width = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column)
                sheet.column_dimensions[column[0].column_letter].width = min(max(width + 2, 12), 46)
    return True

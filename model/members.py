import pandas as pd
from tkinter import messagebox as mb
from model.member import Member

class MemberListError(Exception):
    pass


class Members:

    def __init__(self, filename, config):

        self.members = []
        self.filename = filename
        self.sheet = pd.read_excel(filename, sheet_name=0)

        # mandatory columns have to exist in the excel file
        mandatory_columns = [config.last_name_config, config.first_name_config, config.birthdays_config,
                             config.member_since_config, config.member_config]
        missing_columns = [column for column in mandatory_columns if column not in self.sheet.columns]
        if missing_columns:
            raise MemberListError("In der Excel-Datei fehlen Pflichtspalten: " + ", ".join(missing_columns))

        last_names = self.sheet[config.last_name_config]
        first_names = self.sheet[config.first_name_config]
        streets = self.optional_column(config.street_config)
        plzs = self.optional_column(config.plz_config)
        orte = self.optional_column(config.ort_config)
        birthdays = self.sheet[config.birthdays_config]
        phones = self.optional_column(config.phone_config)
        mobile_phones = self.optional_column(config.mobile_phone_config)
        members_since = self.sheet[config.member_since_config]
        ibans = self.optional_column(config.iban_config)
        references = self.optional_column(config.reference_config)
        member_status = self.sheet[config.member_config]

        for i in range(len(last_names)):
            # mandatory params
            last_name = str(last_names[i])
            first_name = str(first_names[i])
            member_since = pd.to_datetime(members_since[i])
            birthday = pd.to_datetime(birthdays[i])
            member = pd.to_numeric(member_status[i], errors="coerce")

            if last_name == "nan":
                mb.showwarning("Param missing", "last_name param is missing. Param: " + last_name)
                last_name = ""

            if first_name == "nan":
                mb.showwarning("Param missing", "first_name param is missing. Param: " + first_name)
                first_name = ""

            if str(member_since) == "NaT":
                mb.showwarning("Param missing", "member_since param is missing. Member: " + first_name + " " + last_name)
                member_since = pd.Timestamp(year=1000, month=1, day=1)

            if str(birthday) == "NaT":
                mb.showwarning("Param missing", "birthday param is missing. Member: " + first_name + " " + last_name)
                birthday = pd.Timestamp(year=1000, month=1, day=1)

            if member not in (0, 1):
                mb.showwarning("Param missing", "member param is missing or not 0/1, therefore don`t count the member. Member: " + first_name + " " + last_name)
                member = 0
            member = int(member)


            #optional params
            street = str(streets[i])
            plz = str(plzs[i])
            ort = str(orte[i])
            phone_number = str(phones[i])
            mobile_phone = str(mobile_phones[i])
            iban = str(ibans[i])
            reference = str(references[i])


            if street == "nan":
                street = ""

            if plz == "nan":
                plz = ""

            if ort == "nan":
                ort = ""

            if phone_number == "nan":
                phone_number = ""

            if mobile_phone == "nan":
                mobile_phone = ""

            if iban == "nan":
                iban = ""

            if reference == "nan":
                reference = ""

            member = Member(last_name=last_name,
                                       first_name=first_name,
                                       street = street,
                                       plz=plz,
                                       ort=ort,
                                       birthday=birthday,
                                       phone_number=phone_number,
                                       mobile_phone=mobile_phone,
                                       member_since=member_since,
                                       iban=iban,
                                       reference=reference,
                                       member=member)

            self.members.append(member)

    # an optional column that is not in the excel file is treated as empty
    def optional_column(self, name):
        if name in self.sheet.columns:
            return self.sheet[name]
        return pd.Series(float("nan"), index=self.sheet.index)

    # Calculate the total members
    def calculate_members(self):
        member_count = 0
        for x in self.members:
            member_count = member_count + x.member

        print("Member total count: " + str(member_count))
        return member_count

    # Calculate the new members in the given year (default: current year)
    def calculate_new_members(self, year=None):
        member_count = 0
        if year is None:
            year = pd.Timestamp.now().year
        for member in self.members:
            if member.member_since.year == year:
                member_count = member.member + member_count

        print("New member count: " + str(member_count))
        return member_count


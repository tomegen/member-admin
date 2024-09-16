import pandas as pd

from logic.member import Member

class Members:

    def __init__(self, filename, config):

        self.members = []
        self.filename = filename
        self.sheet = pd.read_excel(filename, sheet_name=0)

        last_names = self.sheet[config.last_name_config]
        first_names = self.sheet[config.first_name_config]
        streets = self.sheet[config.street_config]
        plzs = self.sheet[config.plz_config]
        orte = self.sheet[config.ort_config]
        birthdays = self.sheet[config.birthdays_config]
        phones = self.sheet[config.phone_config]
        mobile_phones = self.sheet[config.mobile_phone_config]
        members_since = self.sheet[config.member_since_config]
        ibans = self.sheet[config.iban_config]
        references = self.sheet[config.reference_config]
        member_status = self.sheet[config.member_config]

        for i in range(len(last_names)):
            self.members.append(Member(last_name=str(last_names[i]), first_name=str(first_names[i]), street = str(streets[i]),
                                     plz=str(plzs[i]), ort=str(orte[i]), birthday=pd.to_datetime(birthdays[i]), phone_number=str(phones[i]),
                                     mobile_phone=str(mobile_phones[i]), member_since=pd.to_datetime(members_since[i]),
                                     iban=str(ibans[i]), reference=str(references[i]), member=member_status[i]))


#TODO: improve validations, so that it`s not possible to have empty birthday or memberSince/lastName/firstName

    def calculate_members(self):
        member_count = 0
        for x in self.members:
            member_count = member_count + x.member

        print("Member count: " + str(member_count))
        return member_count

    def calculate_new_members(self):
        member_count = 0
        current_year = pd.Timestamp.now()
        for member in self.members:
            if member.member_since.year == current_year.year:
                member_count = member.member + member_count

        print("New member count: " + str(member_count))
        return member_count


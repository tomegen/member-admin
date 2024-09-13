import pandas as pd

from logic.member import Member

class Members:
    SECOND_NAME = "Name"
    FIRST_NAME = "Vorname"
    STREET = "Strasse"
    PLZ = "Plz"
    ORT = "Ort"
    BIRTHDAY = "Geburtstag"
    PHONE = "Telefon"
    MOBILE_PHONE = "Mobil"
    MEMBER_SINCE = "Mitglied seit"
    IBAN = "IBAN"
    REFERENCE = "Mandatreferenz"
    MEMBER = 'Mitglied'

    def __init__(self, filename):

        self.members = []
        self.filename = filename
        self.sheet = pd.read_excel(filename, sheet_name=0)

        second_names = self.sheet[self.SECOND_NAME]
        first_names = self.sheet[self.FIRST_NAME]
        streets = self.sheet[self.STREET]
        plzs = self.sheet[self.PLZ]
        orte = self.sheet[self.ORT]
        birthdays = self.sheet[self.BIRTHDAY]
        phones = self.sheet[self.PHONE]
        mobile_phones = self.sheet[self.MOBILE_PHONE]
        members_since = self.sheet[self.MEMBER_SINCE]
        ibans = self.sheet[self.IBAN]
        references = self.sheet[self.REFERENCE]
        member_status = self.sheet[self.MEMBER]

        for i in range(len(second_names)):
            self.members.append(Member(last_name=second_names[i], first_name=first_names[i], street = streets[i],
                                     plz=plzs[i], ort=orte[i], birthday=pd.to_datetime(birthdays[i]), phone_number=phones[i],
                                     mobile_phone=mobile_phones[i], member_since=pd.to_datetime(members_since[i]), iban=ibans[i],
                                     reference=references[i], member=member_status[i]))


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

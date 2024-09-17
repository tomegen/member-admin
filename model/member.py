import os

class Member:

    def __init__(self, last_name, first_name, street, plz, ort, birthday, phone_number, mobile_phone, member_since,
                 iban, reference, member):
        self.last_name = last_name
        self.first_name = first_name
        self.street = street
        self.plz = plz
        self.ort = ort
        self.birthday = birthday
        self.phone_number = phone_number
        self.mobile_phone = mobile_phone
        self.member_since = member_since
        self.iban = iban
        self.reference = reference
        self.member = member


    def print(self, text):
        text += self.first_name + " " + self.last_name + os.linesep

        # Geburtstag:
        text += "Geburtstag: " + str(self.birthday.strftime('%d.%m.%Y')) + os.linesep

        # Mitglied seit:
        text += "Mitglied seit: " + str(self.member_since.strftime('%d.%m.%Y')) + os.linesep

        # Telefonnummern
        if self.phone_number or self.mobile_phone:
            text += "Nummer: "
            if self.phone_number:
                text += self.phone_number
                if self.mobile_phone:
                    text += " / " + self.mobile_phone
            else:
                text += self.mobile_phone
            text += os.linesep

        # Anschrift
        if self.plz or self.ort or self.street:
            text += "Anschrift: " + os.linesep
            if self.plz:
                text += self.plz
                if self.ort:
                    text += " " + self.ort
                text += os.linesep
            else:
                if self.ort:
                    text += self.ort + os.linesep
            if self.street:
                text += self.street + os.linesep
        text += os.linesep * 2

        return text

from datetime import datetime


class Member:
    last_name = ""
    first_name = ""
    street = ""
    plz = ""
    ort = ""
    birthday = ""
    phone_number = ""
    mobile_phone = ""
    member_since = ""
    iban = ""
    reference = ""
    member = 0



    def __init__(self, last_name, first_name, street, plz, ort, birthday, phone_number, mobile_phone, member_since, iban, reference, member):
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



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

        if self.last_name == "nan":
            self.last_name = ""

        if self.first_name == "nan":
            self.first_name = ""

        if self.street == "nan":
            self.street = ""

        if self.plz == "nan":
            self.plz = ""

        if self.ort == "nan":
            self.ort = ""

        if self.phone_number == "nan":
            self.phone_number = ""

        if self.mobile_phone == "nan":
            self.mobile_phone = ""

        if self.iban == "nan":
            self.iban = ""

        if self.reference == "nan":
            self.reference = ""
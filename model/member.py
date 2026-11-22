import os

import pandas as pd

from model.schema import ACTIVE, PASSIVE


def format_date(date):
    return "unbekannt" if pd.isna(date) else str(date.strftime('%d.%m.%Y'))


class Member:

    # status is aktiv, passiv, ausgetreten or "" (unknown, not counted); nr is None while it is not assigned
    def __init__(self, last_name, first_name, street="", plz="", ort="", birthday=pd.NaT, phone_number="",
                 mobile_phone="", member_since=pd.NaT, iban="", reference="", status=ACTIVE, nr=None, gender="",
                 exit_date=pd.NaT, exit_reason="", department="", fee_class="", email="", note=""):
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
        self.status = status
        self.nr = nr
        self.gender = gender
        self.exit_date = exit_date
        self.exit_reason = exit_reason
        self.department = department
        self.fee_class = fee_class
        self.email = email
        self.note = note

    # active and passive members count, former members and an unknown status do not
    @property
    def is_member(self):
        return self.status in (ACTIVE, PASSIVE)

    def full_name(self):
        return (self.first_name + " " + self.last_name).strip()

    def print(self, text):
        text += self.full_name() + os.linesep

        # Geburtstag:
        text += "Geburtstag: " + format_date(self.birthday) + os.linesep

        # Mitglied seit:
        text += "Mitglied seit: " + format_date(self.member_since) + os.linesep

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

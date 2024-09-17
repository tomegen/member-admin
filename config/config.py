import configparser
from tkinter import messagebox as mb


class Config:
    CONFIG_NAME = "config.ini"
    def __init__(self):
        try:
            config = configparser.ConfigParser()
            config.read(self.CONFIG_NAME)

            # set values:
            self.birthday_config = [int(num) for num in config.get("birthday", "possibilities").split(",")]
            self.honor_config = [int(num) for num in config.get("honor", "possibilities").split(",")]
            self.last_name_config = config.get("excel_columns", "last_name")
            self.first_name_config = config.get("excel_columns", "first_name")
            self.birthdays_config = config.get("excel_columns", "birthday")
            self.street_config = config.get("excel_columns", "street")
            self.plz_config = config.get("excel_columns", "plz")
            self.ort_config = config.get("excel_columns", "ort")
            self.phone_config = config.get("excel_columns", "phone")
            self.mobile_phone_config = config.get("excel_columns", "mobile_phone")
            self.member_since_config = config.get("excel_columns", "member_since")
            self.iban_config = config.get("excel_columns", "iban")
            self.reference_config = config.get("excel_columns", "reference")
            self.member_config = config.get("excel_columns", "member")

            if not self.last_name_config or not self.first_name_config or not self.birthday_config or not self.member_since_config:
                mb.showerror("Problem mit Konfigurationsdatei", "Vorname, Nachname, Geburtstag oder Mitglied seit Config ist nicht gegeben!")

        except Exception as e:
            mb.showerror("Problem mit Konfigurationsdatei", "Die Konfigurationsdatei config.ini fehlt oder ist fehlerhaft! Fehler:" + str(e))
import configparser
import os
import sys

# used when config.ini is missing or leaves a setting out, so the app also works without the file
DEFAULTS = {
    "birthday": {"possibilities": "16,18,20,30,40,50,60,65,70,75,80,85,90,95,100,105,110"},
    "honor": {"possibilities": "15,20,25,30,35,40,45,50,55,60,65,70,75"},
    "excel_columns": {
        "last_name": "Name", "first_name": "Vorname", "birthday": "Geburtstag", "street": "Strasse", "plz": "Plz",
        "ort": "Ort", "phone": "Telefon", "mobile_phone": "Mobil", "member_since": "Mitglied seit", "iban": "IBAN",
        "reference": "Mandatreferenz", "member": "Mitglied",
    },
}


class ConfigError(Exception):
    pass


# "16, 18 20;30" -> [16, 18, 20, 30] (sorted, no duplicates); ValueError with a readable message otherwise
def parse_numbers(text, highest=120):
    parts = text.replace(";", ",").replace(" ", ",").split(",")
    numbers = set()
    for part in parts:
        if not part:
            continue
        if not part.isdigit() or not 1 <= int(part) <= highest:
            raise ValueError("„" + part + "“ ist keine gültige Zahl (erlaubt: 1 bis " + str(highest) + ").")
        numbers.add(int(part))
    if not numbers:
        raise ValueError("Bitte mindestens eine Zahl eingeben.")
    return sorted(numbers)


class Config:
    CONFIG_NAME = "config.ini"

    # config.ini is searched next to the exe / the .app (so it can be edited), then in the bundled
    # default of the packaged app, then in the project root. It is independent of the working directory.
    @staticmethod
    def config_path():
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = []
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(sys.executable)
            candidates.append(exe_dir)
            # macOS: <folder>/Mitgliederverwaltung.app/Contents/MacOS/<exe> -> <folder>
            candidates.append(os.path.abspath(os.path.join(exe_dir, "..", "..", "..")))
            candidates.append(getattr(sys, "_MEIPASS", exe_dir))
        candidates.append(project_root)
        for directory in candidates:
            path = os.path.join(directory, Config.CONFIG_NAME)
            if os.path.isfile(path):
                return path
        return None

    # without a path, a missing config.ini is fine (defaults); a path that was asked for has to exist
    def __init__(self, path=None):
        try:
            config = configparser.ConfigParser()
            config.read_dict(DEFAULTS)
            path = path or self.config_path()
            if path and not config.read(path, encoding="utf-8"):
                raise ConfigError("Datei nicht gefunden: " + path)

            # set values:
            self.birthday_config = parse_numbers(config.get("birthday", "possibilities"))
            self.honor_config = parse_numbers(config.get("honor", "possibilities"))
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
        except Exception as e:
            raise ConfigError("Die Konfigurationsdatei config.ini fehlt oder ist fehlerhaft! Fehler: " + str(e))

        if not (self.last_name_config and self.first_name_config and self.birthdays_config
                and self.member_since_config and self.member_config):
            raise ConfigError("In der config.ini fehlt der Spaltenname für Nachname, Vorname, Geburtstag, "
                              "Mitglied seit oder Mitglied.")

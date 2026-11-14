import configparser
import os
import sys


class ConfigError(Exception):
    pass


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
        return os.path.join(candidates[0], Config.CONFIG_NAME)

    def __init__(self, path=None):
        try:
            path = path or self.config_path()
            config = configparser.ConfigParser()
            if not config.read(path, encoding="utf-8"):
                raise ConfigError("Datei nicht gefunden: " + path)

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
        except Exception as e:
            raise ConfigError("Die Konfigurationsdatei config.ini fehlt oder ist fehlerhaft! Fehler: " + str(e))

        if not (self.last_name_config and self.first_name_config and self.birthdays_config
                and self.member_since_config and self.member_config):
            raise ConfigError("In der config.ini fehlt der Spaltenname für Nachname, Vorname, Geburtstag, "
                              "Mitglied seit oder Mitglied.")

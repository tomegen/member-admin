import re
import unicodedata

# field -> (name of the attribute in Config, name shown to the user, usual headings, mandatory?)
# headings are written normalized (see normalize); the name from config.ini is always tried first
FIELDS = {
    "last_name": ("last_name_config", "Name", ["name", "nachname", "familienname", "lastname", "surname"], True),
    "first_name": ("first_name_config", "Vorname", ["vorname", "firstname", "rufname"], True),
    "birthday": ("birthdays_config", "Geburtstag",
                 ["geburtstag", "geburtsdatum", "gebdatum", "geb", "geboren", "birthday", "birthdate"],
                 True),
    "member_since": ("member_since_config", "Mitglied seit",
                     ["mitgliedseit", "mitgliedsseit", "eintritt", "eintrittsdatum", "beitritt", "beitrittsdatum",
                      "eintrittam", "membersince"], True),
    "member": ("member_config", "Mitglied", ["mitglied", "aktiv", "aktivesmitglied", "status", "member"], True),
    "street": ("street_config", "Strasse", ["strasse", "str", "strassehausnummer", "adresse", "anschrift"], False),
    "plz": ("plz_config", "Plz", ["plz", "postleitzahl", "zip"], False),
    "ort": ("ort_config", "Ort", ["ort", "wohnort", "stadt"], False),
    "phone": ("phone_config", "Telefon", ["telefon", "tel", "telefonnummer", "festnetz", "phone"], False),
    "mobile_phone": ("mobile_phone_config", "Mobil", ["mobil", "mobiltelefon", "mobilnummer", "handy", "mobile"],
                     False),
    "iban": ("iban_config", "IBAN", ["iban"], False),
    "reference": ("reference_config", "Mandatreferenz", ["mandatreferenz", "mandatsreferenz", "sepamandat"], False),
}


# "Mitglied seit", "mitglied_seit " and "Straße" become "mitgliedseit" and "strasse"
def normalize(heading):
    text = str(heading).replace("ß", "ss").replace("ẞ", "ss")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]", "", text.lower())


# which column of the excel file holds which field: {field: column heading or None}
# a column is used for one field only; the configured name wins over the usual headings
def detect_columns(headings, config):
    by_name = {}
    for heading in headings:
        by_name.setdefault(normalize(heading), heading)
    found, used = {}, set()
    for field, (attribute, _, usual, _) in FIELDS.items():
        found[field] = None
        for name in [normalize(getattr(config, attribute))] + usual:
            heading = by_name.get(name)
            if heading is not None and heading not in used:
                found[field] = heading
                used.add(heading)
                break
    return found


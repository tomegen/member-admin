from collections import namedtuple

# the standard member file of the app (see PLAN_DATA_STORAGE.md); a new version needs an upgrade path
SCHEMA_VERSION = 1

MEMBERS_SHEET = "Mitglieder"
FUNCTIONS_SHEET = "Funktionen"
SETTINGS_SHEET = "Einstellungen"
LOG_SHEET = "Änderungsprotokoll"
INFO_SHEET = "Info"

ACTIVE, PASSIVE, LEFT = "aktiv", "passiv", "ausgetreten"
STATUSES = [ACTIVE, PASSIVE, LEFT]
GENDERS = ["männlich", "weiblich", "divers"]

# kind: text, number, date, gender, status or list:<defined name of a list in the settings sheet>
Column = namedtuple("Column", "field heading mandatory kind width hint")

MEMBER_COLUMNS = [
    Column("nr", "Nr", False, "number", 7,
           "Mitgliedsnummer. Bei neuen Mitgliedern leer lassen, die App vergibt sie. Nie ändern oder doppelt vergeben."),
    Column("last_name", "Name", True, "text", 20, "Nachname."),
    Column("first_name", "Vorname", True, "text", 18, "Vorname."),
    Column("gender", "Geschlecht", True, "gender", 12, "männlich, weiblich oder divers (Auswahl)."),
    Column("birthday", "Geburtstag", True, "date", 13, "Geburtsdatum, z. B. 24.12.1960. Für Geburtstage."),
    Column("member_since", "Eintritt", True, "date", 13, "Eintrittsdatum, z. B. 01.04.2005. Für Ehrungen."),
    Column("status", "Status", True, "status", 13,
           "aktiv, passiv oder ausgetreten (Auswahl). Ausgetretene nicht löschen, sondern auf „ausgetreten“ setzen."),
    Column("exit_date", "Austritt am", False, "date", 13, "Datum des Austritts, z. B. 31.12.2026."),
    Column("exit_reason", "Austrittsgrund", False, "text", 20, "Grund des Austritts (freiwillig)."),
    Column("department", "Abteilung", False, "list:Abteilungen", 16, "Auswahl aus dem Blatt „Einstellungen“."),
    Column("fee_class", "Beitragsklasse", False, "list:Beitragsklassen", 16, "Auswahl aus dem Blatt „Einstellungen“."),
    Column("street", "Straße", False, "text", 24, "Straße und Hausnummer (freiwillig)."),
    Column("plz", "PLZ", False, "text", 8, "Postleitzahl (freiwillig)."),
    Column("ort", "Ort", False, "text", 18, "Wohnort (freiwillig)."),
    Column("phone", "Telefon", False, "text", 16, "Telefon (freiwillig)."),
    Column("mobile_phone", "Mobil", False, "text", 16, "Mobilnummer (freiwillig)."),
    Column("email", "E-Mail", False, "text", 26, "E-Mail-Adresse (freiwillig)."),
    Column("iban", "IBAN", False, "text", 30, "IBAN (freiwillig)."),
    Column("reference", "Mandatsreferenz", False, "text", 16, "Mandatsreferenz (freiwillig)."),
    Column("note", "Bemerkung", False, "text", 30,
           "Freitext (freiwillig). Bitte keine sensiblen Angaben wie Gesundheit eintragen."),
]

FUNCTION_HEADINGS = ["Nr", "Mitglied", "Funktion", "von", "bis", "Bemerkung"]
LOG_HEADINGS = ["Zeitpunkt", "Bearbeiter", "Nr", "Mitglied", "Aktion", "Feld", "alt", "neu"]

# settings sheet: small lists next to each other, each with a fixed heading in row 1
OCCASION_HEADINGS = ["Anlass", "Jahre", "Geschenk/Maßnahme", "Bemerkung"]   # columns A-D
BIRTHDAY, HONOR = "Geburtstag", "Jubiläum"
VALUE_LISTS = [("Abteilungen", "F"), ("Beitragsklassen", "G"), ("Funktionen", "H")]   # defined name = heading
GENERAL_HEADINGS = ["Einstellung", "Wert"]   # columns J-K
CLUB_NAME = "Vereinsname"
DELETE_AFTER = "Löschfrist in Jahren"
REMINDER_DAYS = "Erinnerung (Tage vorher)"
PASSIVE_BIRTHDAYS = "Passive bei Geburtstagen"
PASSIVE_HONORS = "Passive bei Ehrungen"
PASSIVE_STATISTICS = "Passive in der Statistik"
GENERAL_DEFAULTS = [(CLUB_NAME, ""), (DELETE_AFTER, "nie"), (REMINDER_DAYS, 7),
                    (PASSIVE_BIRTHDAYS, "ja"), (PASSIVE_HONORS, "ja"), (PASSIVE_STATISTICS, "ja")]

# info sheet: key in column A, value in column B
SCHEMA_KEY = "Schema-Version"
FILE_ID_KEY = "Datei-ID"
NEXT_NR_KEY = "Nächste freie Nr"

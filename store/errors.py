from collections import namedtuple

# heading is shown to the user; base, mine and theirs are cell keys (when read, entered in the app, in the file now)
FieldConflict = namedtuple("FieldConflict", "field heading base mine theirs")


# a problem while saving; the message is shown as it is, nothing was written
class SaveError(Exception):
    pass


class FileLocked(SaveError):

    def __init__(self, owner):
        super().__init__("Die Mitgliederliste ist gerade in Excel oder einem anderen Programm geöffnet" +
                         (" (von " + owner + ")" if owner else "") +
                         ". Bitte dort schließen und noch einmal speichern.")
        self.owner = owner


# somebody else changed the same field (fields) or removed the member (missing); theirs is the row in the file now
class Conflict(SaveError):

    def __init__(self, nr, fields, theirs, missing=False):
        super().__init__("Mitglied " + str(nr) + (" ist nicht mehr in der Datei." if missing else
                                                  " wurde inzwischen von jemand anderem geändert."))
        self.nr = nr
        self.fields = fields
        self.theirs = theirs
        self.missing = missing


class Duplicate(SaveError):

    def __init__(self, row, name):
        super().__init__(name + " steht schon in der Liste (Zeile " + str(row) + ", gleicher Name und Geburtstag).")
        self.row = row
        self.name = name

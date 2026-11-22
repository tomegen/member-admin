import datetime
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation

from config.config import Config
from logic.template import write_member_template
from model.club_file import read_bytes
from model.members import Members
from store import backups
from model.club_settings import ClubSettings, Occasion
from logic.merge import CHANGED, NEW, SAME, SIMILAR, compare, member_values
from store.changes import (add_member, assign_numbers, combine, delete_members, merge_members, update_functions,
                           update_member, update_settings)
from store.conflict_copies import conflict_copies, move_to_backups
from store.errors import Conflict, Duplicate, FileLocked, SaveError
from store.transaction import lock_owner, save

NOW = datetime.datetime(2026, 11, 22, 14, 2, 12)
PEOPLE = [
    {"Nr": 1, "Name": "Muster", "Vorname": "Max", "Geschlecht": "männlich", "Geburtstag": datetime.date(1967, 6, 1),
     "Eintritt": datetime.date(2002, 5, 5), "Status": "aktiv", "PLZ": "01234"},
    {"Nr": 2, "Name": "Beispiel", "Vorname": "Eva", "Geschlecht": "weiblich", "Geburtstag": datetime.date(1970, 2, 13),
     "Eintritt": datetime.date(2010, 1, 1), "Status": "passiv"},
]


class StoreTest(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "Mitglieder.xlsx")
        write_member_template(self.path, self.config)
        self.edit_in_excel(lambda sheet: self.write_people(sheet, PEOPLE))

    # somebody changes the file outside the app (excel, phone): change(sheet "Mitglieder") or change(book)
    def edit_in_excel(self, change, whole_book=False):
        book = load_workbook(self.path)
        change(book if whole_book else book["Mitglieder"])
        book.save(self.path)

    @staticmethod
    def write_people(sheet, people, first_row=2):
        position = {cell.value: cell.column for cell in sheet[1]}
        for row, person in enumerate(people, start=first_row):
            for heading, value in person.items():
                sheet.cell(row=row, column=position[heading], value=value)

    def read(self):
        return Members(self.path, today=datetime.date(2026, 11, 22))

    def member(self, nr):
        return [member for member in self.read().members if member.nr == nr][0]

    def log(self):
        sheet = load_workbook(self.path)["Änderungsprotokoll"]
        return [row[1:] for row in sheet.iter_rows(min_row=2, values_only=True) if row[0] is not None]


class UpdateTest(StoreTest):

    def test_change_is_written_with_log_and_backup(self):
        snapshot = self.read().snapshot
        saved = save(self.path, update_member(1, snapshot.rows[1], {"ort": "Musterstadt", "email": "max@example.org"}),
                     "Vorstand A", now=NOW)
        self.assertEqual((self.member(1).ort, self.member(1).email), ("Musterstadt", "max@example.org"))
        self.assertEqual(self.member(1).plz, "01234")
        self.assertEqual(self.log(), [("Vorstand A", 1, "Max Muster", "geändert", "Ort", None, "Musterstadt"),
                                      ("Vorstand A", 1, "Max Muster", "geändert", "E-Mail", None, "max@example.org")])
        self.assertEqual(os.path.basename(saved.backup), "Mitglieder 2026-11-22 140212.xlsx")
        self.assertIsNone(load_workbook(saved.backup)["Mitglieder"]["N2"].value)   # the state before
        self.assertEqual(self.read().snapshot.hash, saved.hash)
        self.assertEqual(self.read().issues, [])

    def test_changes_of_others_in_other_rows_and_fields_stay(self):
        snapshot = self.read().snapshot
        self.edit_in_excel(lambda sheet: (sheet.cell(row=3, column=14, value="Anderswo"),     # Ort of Eva
                                          sheet.cell(row=2, column=15, value="0123 4567")))    # Telefon of Max
        save(self.path, update_member(1, snapshot.rows[1], {"ort": "Musterstadt"}), "A", now=NOW)
        self.assertEqual((self.member(1).ort, self.member(1).phone_number), ("Musterstadt", "0123 4567"))
        self.assertEqual(self.member(2).ort, "Anderswo")

    def test_same_field_changed_by_both_is_a_conflict_until_decided(self):
        snapshot = self.read().snapshot
        self.edit_in_excel(lambda sheet: sheet.cell(row=2, column=14, value="Handystadt"))
        with self.assertRaises(Conflict) as error:
            save(self.path, update_member(1, snapshot.rows[1], {"ort": "Musterstadt"}), "A", now=NOW)
        conflict = error.exception
        self.assertEqual([(f.heading, f.base, f.mine, f.theirs) for f in conflict.fields],
                         [("Ort", "", "Musterstadt", "Handystadt")])
        self.assertEqual(self.member(1).ort, "Handystadt")                       # nothing written
        self.assertFalse(os.path.isdir(backups.backup_folder(self.path)))
        # the user keeps the own value: saved again with the file as base
        save(self.path, update_member(1, conflict.theirs, {"ort": "Musterstadt"}), "A", now=NOW)
        self.assertEqual(self.member(1).ort, "Musterstadt")

    def test_same_value_from_both_is_no_conflict_and_nothing_is_written(self):
        snapshot = self.read().snapshot
        self.edit_in_excel(lambda sheet: sheet.cell(row=2, column=14, value="Musterstadt"))
        before = read_bytes(self.path)
        saved = save(self.path, update_member(1, snapshot.rows[1], {"ort": "Musterstadt"}), "A", now=NOW)
        self.assertEqual((saved.entries, saved.backup), ([], None))
        self.assertEqual(read_bytes(self.path), before)
        self.assertFalse(os.path.isdir(backups.backup_folder(self.path)))

    def test_unchanged_values_from_the_dialog_do_not_overwrite_the_file(self):
        snapshot = self.read().snapshot
        self.edit_in_excel(lambda sheet: sheet.cell(row=2, column=14, value="Handystadt"))
        save(self.path, update_member(1, snapshot.rows[1], {"ort": "", "first_name": "Maximilian"}), "A", now=NOW)
        self.assertEqual((self.member(1).ort, self.member(1).first_name), ("Handystadt", "Maximilian"))

    def test_a_field_can_be_emptied(self):
        snapshot = self.read().snapshot
        save(self.path, update_member(1, snapshot.rows[1], {"plz": "", "phone": None}), "A", now=NOW)
        self.assertEqual(self.member(1).plz, "")
        self.assertIsNone(load_workbook(self.path)["Mitglieder"]["M2"].value)
        self.assertEqual(self.log()[-1][4:], ("PLZ", "01234", None))

    def test_dates_and_status(self):
        snapshot = self.read().snapshot
        save(self.path, update_member(2, snapshot.rows[2], {"status": "ausgetreten",
                                                            "exit_date": datetime.date(2026, 12, 31),
                                                            "birthday": datetime.date(1970, 2, 13)},
                                      action="Austritt"), "A", now=NOW)
        member = self.member(2)
        self.assertEqual((member.status, member.exit_date.date()), ("ausgetreten", datetime.date(2026, 12, 31)))
        self.assertEqual(self.log()[-1][3:], ("Austritt", "Austritt am", None, "31.12.2026"))
        self.assertEqual(load_workbook(self.path)["Mitglieder"]["H3"].number_format, "DD.MM.YYYY")

    def test_moved_member_is_found_by_its_number(self):
        snapshot = self.read().snapshot
        self.edit_in_excel(lambda sheet: sheet.insert_rows(2, amount=3))   # e.g. sorted differently
        save(self.path, update_member(2, snapshot.rows[2], {"ort": "Neustadt"}), "A", now=NOW)
        self.assertEqual(self.member(2).ort, "Neustadt")
        self.assertEqual(self.member(1).ort, "")

    def test_removed_member_is_a_conflict(self):
        snapshot = self.read().snapshot
        self.edit_in_excel(lambda sheet: sheet.delete_rows(3))
        with self.assertRaises(Conflict) as error:
            save(self.path, update_member(2, snapshot.rows[2], {"ort": "Neustadt"}), "A", now=NOW)
        self.assertTrue(error.exception.missing)

    def test_iban_is_masked_in_the_log(self):
        snapshot = self.read().snapshot
        save(self.path, update_member(1, snapshot.rows[1], {"iban": "DE02 1203 0000 0000 2020 51"}), "A", now=NOW)
        self.assertEqual(self.log()[-1][5:], (None, "DE** … 2051"))
        self.assertEqual(self.member(1).iban, "DE02 1203 0000 0000 2020 51")


class AddTest(StoreTest):

    def values(self, **extra):
        values = {"last_name": "Neu", "first_name": "Nina", "gender": "weiblich",
                  "birthday": datetime.date(2001, 3, 4), "member_since": datetime.date(2026, 11, 1),
                  "status": "aktiv"}
        values.update(extra)
        return values

    def test_new_member_gets_the_next_number_below_the_last_row(self):
        saved = save(self.path, add_member(self.values()), "A", now=NOW)
        self.assertEqual(saved.entries[0][:3], (3, "Nina Neu", "angelegt"))
        members = self.read()
        self.assertEqual([(m.nr, m.first_name) for m in members.members], [(1, "Max"), (2, "Eva"), (3, "Nina")])
        self.assertEqual(members.issues, [])

    def test_number_after_the_highest_also_when_added_by_hand_meanwhile(self):
        self.edit_in_excel(lambda sheet: self.write_people(sheet, [dict(PEOPLE[0], Nr=7, Vorname="Udo")], 4))
        save(self.path, add_member(self.values()), "A", now=NOW)
        self.assertEqual(self.member(8).first_name, "Nina")

    def test_duplicate_is_reported_unless_wanted(self):
        values = self.values(last_name="muster", first_name="MAX", birthday=datetime.date(1967, 6, 1))
        with self.assertRaises(Duplicate) as error:
            save(self.path, add_member(values), "A", now=NOW)
        self.assertEqual((error.exception.row, error.exception.name), (2, "Max Muster"))
        save(self.path, add_member(values, allow_duplicate=True), "A", now=NOW)
        self.assertEqual(len(self.read().members), 3)


class NumbersTest(StoreTest):

    def test_rows_without_number_get_one_and_wrong_numbers_stay(self):
        self.edit_in_excel(lambda sheet: self.write_people(sheet, [dict(PEOPLE[0], Nr=None, Vorname="Udo"),
                                                                   dict(PEOPLE[0], Nr="x", Vorname="Ina"),
                                                                   dict(PEOPLE[0], Nr=None, Vorname="Tom")], 4))
        saved = save(self.path, assign_numbers(), "A", now=NOW)
        self.assertEqual([(e.nr, e.name) for e in saved.entries], [(3, "Udo Muster"), (4, "Tom Muster")])
        self.assertEqual([m.nr for m in self.read().members], [1, 2, 3, None, 4])


class SafetyTest(StoreTest):

    def change(self):
        return update_member(1, self.read().snapshot.rows[1], {"ort": "Musterstadt"})

    def test_open_in_excel_stops_with_the_name_of_the_user(self):
        with open(os.path.join(self.tmp.name, "~$Mitglieder.xlsx"), "wb") as file:
            file.write(bytes([5]) + b"Vorst" + b" " * 50)
        self.assertEqual(lock_owner(self.path), "Vorst")
        before = read_bytes(self.path)
        with self.assertRaises(FileLocked) as error:
            save(self.path, self.change(), "A", now=NOW)
        self.assertIn("(von Vorst)", str(error.exception))
        self.assertEqual(read_bytes(self.path), before)
        save(self.path, self.change(), "A", now=NOW, ignore_lock=True)       # the user decided to save anyway
        self.assertEqual(self.member(1).ort, "Musterstadt")

    def test_libreoffice_lock_file(self):
        with open(os.path.join(self.tmp.name, ".~lock.Mitglieder.xlsx#"), "w") as file:
            file.write("Kassier,host,kassier,22.11.2026 14:00,")
        self.assertEqual(lock_owner(self.path), "Kassier")

    def test_file_locked_while_replacing_leaves_no_temporary_file(self):
        before = read_bytes(self.path)
        with mock.patch("store.transaction.os.replace", side_effect=PermissionError("in use")):
            with self.assertRaises(FileLocked):
                save(self.path, self.change(), "A", now=NOW)
        self.assertEqual(read_bytes(self.path), before)
        self.assertEqual(sorted(os.listdir(self.tmp.name)), ["Mitglieder.xlsx", "Sicherungen"])

    def test_file_changed_during_the_save_is_read_again(self):
        change = self.change()
        calls = []

        def change_while_saving(book, members):
            if not calls:   # the first time somebody saves on the phone at the same moment
                self.edit_in_excel(lambda sheet: sheet.cell(row=3, column=14, value="Handystadt"))
            calls.append(1)
            return change(book, members)

        save(self.path, change_while_saving, "A", now=NOW)
        self.assertEqual(len(calls), 2)
        self.assertEqual((self.member(1).ort, self.member(2).ort), ("Musterstadt", "Handystadt"))

    def test_missing_mandatory_column_stops_without_writing(self):
        change = self.change()
        self.edit_in_excel(lambda sheet: sheet.cell(row=1, column=2, value="Nachname"))
        with self.assertRaises(SaveError) as error:
            save(self.path, change, "A", now=NOW)
        self.assertIn("fehlen diese Spalten: Name", str(error.exception))


class RepairTest(StoreTest):

    def test_own_columns_moved_columns_and_own_checks_stay(self):
        def own_column(sheet):
            sheet.insert_cols(1)
            sheet["A1"] = "Mein Feld"
            sheet["A2"] = "bleibt"
            own = DataValidation(type="list", formula1='"x,y"')
            sheet.add_data_validation(own)
            own.add("A2:A50")
        self.edit_in_excel(own_column)
        save(self.path, update_member(1, self.read().snapshot.rows[1], {"ort": "Musterstadt"}), "A", now=NOW)
        sheet = load_workbook(self.path)["Mitglieder"]
        self.assertEqual((sheet["A2"].value, sheet["O2"].value), ("bleibt", "Musterstadt"))   # Ort moved to O
        checks = {str(check.sqref): check.formula1 for check in sheet.data_validations.dataValidation}
        self.assertEqual(checks["A2:A50"], '"x,y"')
        self.assertEqual(checks["E2:E1001"], '"männlich,weiblich,divers"')                     # moved with the column
        self.assertNotIn("D2:D1001", checks)

    def test_lost_checks_sheets_names_and_columns_come_back(self):
        def damage(book):
            book["Mitglieder"].data_validations.dataValidation = []
            book["Mitglieder"].delete_cols(18)        # IBAN
            del book["Info"]
            del book["Änderungsprotokoll"]
            del book.defined_names["Abteilungen"]
        self.edit_in_excel(damage, whole_book=True)
        save(self.path, update_member(1, self.read().snapshot.rows[1], {"ort": "Musterstadt"}), "A", now=NOW)
        book = load_workbook(self.path)
        sheet = book["Mitglieder"]
        self.assertEqual(len(sheet.data_validations.dataValidation), 8)
        self.assertEqual(sheet.cell(row=1, column=20).value, "IBAN")
        self.assertIn("Info", book.sheetnames)
        self.assertIn("Abteilungen", book.defined_names)
        self.assertEqual(len(self.log()), 1)
        self.assertTrue(self.read().standard)

    def test_saving_does_not_fill_the_file_with_empty_cells(self):
        size = os.path.getsize(self.path)
        for town in ("A", "B", "C"):
            save(self.path, update_member(1, self.read().snapshot.rows[1], {"ort": town}), "A", now=NOW)
        self.assertLess(os.path.getsize(self.path), size * 1.2)


class SettingsTest(StoreTest):

    def edit_settings(self, cells):
        self.edit_in_excel(lambda book: [book["Einstellungen"].__setitem__(coordinate, value)
                                         for coordinate, value in cells.items()], whole_book=True)

    def clear_occasions(self):
        def clear(book):
            sheet = book["Einstellungen"]
            for row in range(2, 60):
                for letter in "ABCD":
                    sheet[letter + str(row)] = None
        self.edit_in_excel(clear, whole_book=True)

    def test_template_has_the_defaults(self):
        settings = self.read().settings
        self.assertEqual(settings.numbers("Geburtstag", []), self.config.birthday_config)
        self.assertEqual(settings.numbers("Jubiläum", []), self.config.honor_config)
        self.assertEqual((settings.club_name, settings.delete_after, settings.reminder_days), ("", None, 7))
        self.assertTrue(settings.passive("birthdays"))
        self.assertEqual(settings.lists["Abteilungen"], [])

    def test_occasions_gifts_and_lists_written_by_hand(self):
        self.clear_occasions()
        self.edit_settings({"A2": "Geburtstag", "B2": 70, "C2": "Präsentkorb", "A3": "geburtstag", "B3": "60",
                            "A4": "Jubiläum", "B4": "keine", "A5": "Feier", "B5": 5, "A6": "Geburtstag", "B6": "x",
                            "F2": "Fußball", "F4": "Tennis", "F5": "Fußball"})
        members = self.read()
        settings = members.settings
        self.assertEqual(settings.numbers("Geburtstag", [1]), [60, 70])
        self.assertEqual(settings.numbers("Jubiläum", [1]), [])
        self.assertEqual(settings.gifts("Geburtstag"), {70: "Präsentkorb"})
        self.assertEqual(settings.lists["Abteilungen"], ["Fußball", "Tennis"])
        self.assertEqual([(i.row, i.name) for i in members.issues],
                         [(5, "Blatt „Einstellungen“"), (6, "Blatt „Einstellungen“")])

    def test_passive_members_count_as_the_club_wants(self):
        self.edit_settings({"K5": "nein", "K4": "x"})                        # passive at birthdays: no
        members = self.read()
        self.assertEqual([m.first_name for m in members.counted("birthdays")], ["Max"])
        self.assertEqual([m.first_name for m in members.counted("honors")], ["Max", "Eva"])
        self.assertEqual(members.settings.reminder_days, 7)                   # "x" is not a number: default
        self.assertIn("Erinnerung (Tage vorher)", members.issues[0].message)
        self.edit_settings({"K4": 0})
        self.assertEqual((self.read().settings.reminder_days, self.read().issues), (0, []))

    def test_settings_are_saved_area_by_area(self):
        self.edit_settings({"D2": "Notiz bleibt"})          # note of the first occasion (Geburtstag 16)
        base = self.read().settings
        new = ClubSettings([Occasion("Jubiläum", 25, "Urkunde", ""), Occasion("Geburtstag", 16, "", ""),
                            Occasion("Geburtstag", 60, "Präsentkorb", "")],
                           {"Abteilungen": ["Fußball", "Tennis"]},
                           {"Vereinsname": "TSV Beispiel", "Passive bei Ehrungen": False})
        self.edit_settings({"G2": "Erwachsene"})            # somebody adds a fee class meanwhile
        saved = save(self.path, update_settings(base, new), "Vorstand A", now=NOW)
        settings = self.read().settings
        self.assertEqual([tuple(o) for o in settings.occasions],
                         [("Geburtstag", 16, "", "Notiz bleibt"), ("Geburtstag", 60, "Präsentkorb", ""),
                          ("Jubiläum", 25, "Urkunde", "")])
        self.assertEqual((settings.lists["Abteilungen"], settings.lists["Beitragsklassen"]),
                         (["Fußball", "Tennis"], ["Erwachsene"]))
        self.assertEqual((settings.club_name, settings.passive("honors"), settings.reminder_days),
                         ("TSV Beispiel", False, 7))
        self.assertEqual([entry.field for entry in saved.entries],
                         ["Anlässe", "Abteilungen", "Vereinsname", "Passive bei Ehrungen"])
        self.assertEqual(self.log()[-1][3:], ("Einstellungen", "Passive bei Ehrungen", "ja", "nein"))
        self.assertEqual(self.log()[0][4:], ("Anlässe", "Geburtstag 18, Geburtstag 20, Geburtstag 30, Geburtstag "
                                             "40, Geburtstag 50, Geburtstag 60, Geburtstag 65, Geburtstag 70, Geburtstag "
                                             "75, Geburtstag 80, Geburtstag 85, Geburtstag 90, Geburtstag 95, Geburtstag "
                                             "100, Geburtstag 105, Geburtstag 110, Jubiläum 15, Jubiläum 20, Jubiläum 25, "
                                             "Jubiläum 30, Jubiläum 35, Jubiläum 40, Jubiläum 45, Jubiläum 50, Jubiläum 55, "
                                             "Jubiläum 60, Jubiläum 65, Jubiläum 70, Jubiläum 75",
                                             "Geburtstag 60 Präsentkorb, Jubiläum 25 Urkunde"))
        self.assertEqual(self.log()[1][4:], ("Abteilungen", None, "Fußball, Tennis"))
        self.assertEqual(load_workbook(self.path)["Einstellungen"]["K6"].value, "nein")
        self.assertEqual(len(load_workbook(self.path)["Einstellungen"].data_validations.dataValidation), 2)

    def test_same_area_changed_by_both_is_refused(self):
        base = self.read().settings
        self.edit_settings({"F2": "Handball"})
        new = ClubSettings(base.occasions, {"Abteilungen": ["Fußball"]}, base.general)
        with self.assertRaises(SaveError) as error:
            save(self.path, update_settings(base, new), "A", now=NOW)
        self.assertIn("Abteilungen", str(error.exception))
        self.assertEqual(self.read().settings.lists["Abteilungen"], ["Handball"])

    def test_missing_general_key_is_added(self):
        self.edit_settings({"J2": None, "K2": None})       # Vereinsname deleted by hand
        base = self.read().settings
        new = ClubSettings(base.occasions, base.lists, dict(base.general, Vereinsname="TSV Beispiel"))
        save(self.path, update_settings(base, new), "A", now=NOW)
        self.assertEqual(self.read().settings.club_name, "TSV Beispiel")


class FunctionsTest(StoreTest):
    KASSIER = ("Kassier", datetime.date(2020, 1, 1), None, "")

    def write_functions(self, rows):
        def write(book):
            sheet = book["Funktionen"]
            for row, values in enumerate(rows, start=2):
                for column, value in enumerate(values, start=1):
                    sheet.cell(row=row, column=column, value=value)
        self.edit_in_excel(write, whole_book=True)

    def keys(self, nr):
        from model.functions import function_key
        return [function_key(function) for function in self.read().functions_of(nr)]

    def test_functions_by_number_or_unique_name_and_findings(self):
        self.write_functions([(1, "Max Muster", "Kassier", datetime.date(2020, 1, 1)),
                              (None, "Beispiel, Eva", "Jugendwart", datetime.date(2015, 1, 1), datetime.date(2019, 12, 31)),
                              (9, "Udo", "Beisitzer"),
                              (None, "Niemand Bekannt", "Schriftführer"),
                              (2, "Eva Beispiel", None, datetime.date(2021, 1, 1), datetime.date(2020, 1, 1))])
        members = self.read()
        self.assertEqual([(f.row, f.nr, f.function) for f in members.functions],
                         [(2, 1, "Kassier"), (3, 2, "Jugendwart"), (4, 9, "Beisitzer"), (5, None, "Schriftführer"),
                          (6, 2, "")])
        found = [(i.row, i.message) for i in members.issues]
        self.assertEqual(found, [(4, "Udo: Mitgliedsnummer 9 gibt es im Blatt „Mitglieder“ nicht."),
                                 (5, "Niemand Bekannt: Mitgliedsnummer fehlt oder ist ungültig."),
                                 (6, "Eva Beispiel: Funktion fehlt."),
                                 (6, "Eva Beispiel: „bis“ liegt vor „von“.")])
        self.assertEqual([f.function for f in members.functions_of(2)], ["Jugendwart", ""])

    def test_functions_of_a_member_are_replaced_and_others_stay(self):
        self.write_functions([(1, "Max Muster", "Kassier", datetime.date(2020, 1, 1)),
                              (2, "Eva Beispiel", "Jugendwart"),
                              (1, "Max Muster", "Beisitzer", datetime.date(2010, 1, 1), datetime.date(2019, 12, 31))])
        base = self.keys(1)
        saved = save(self.path, update_functions(1, base, [("Vorsitzender", datetime.date(2024, 3, 1), None, "")]),
                     "A", now=NOW)
        members = self.read()
        self.assertEqual([(f.row, f.nr, f.name, f.function) for f in members.functions],
                         [(2, 1, "Max Muster", "Vorsitzender"), (3, 2, "Eva Beispiel", "Jugendwart")])
        self.assertEqual(members.functions_of(1)[0].start, datetime.datetime(2024, 3, 1))
        self.assertEqual(saved.entries[0][2:5], ("geändert", "Funktionen",
                                                 "Kassier (01.01.2020 – ), Beisitzer (01.01.2010 – 31.12.2019)"))
        save(self.path, update_functions(1, self.keys(1), [("Vorsitzender", datetime.date(2024, 3, 1), None, ""),
                                                          self.KASSIER]), "A", now=NOW)
        self.assertEqual([(f.row, f.function) for f in self.read().functions],
                         [(2, "Vorsitzender"), (3, "Jugendwart"), (4, "Kassier")])

    def test_an_end_date_can_be_removed(self):
        self.write_functions([(1, "Max Muster", "Kassier", datetime.date(2020, 1, 1), datetime.date(2022, 1, 1))])
        save(self.path, update_functions(1, self.keys(1), [self.KASSIER]), "A", now=NOW)
        self.assertTrue(pd.isna(self.read().functions_of(1)[0].end))

    def test_functions_changed_meanwhile_are_not_overwritten(self):
        self.write_functions([(1, "Max Muster", "Kassier")])
        base = self.keys(1)
        self.write_functions([(1, "Max Muster", "Kassierer")])
        with self.assertRaises(SaveError):
            save(self.path, update_functions(1, base, [self.KASSIER]), "A", now=NOW)

    def test_member_and_functions_in_one_save_and_new_member_with_functions(self):
        change = combine(update_member(1, self.read().snapshot.rows[1], {"ort": "Musterstadt"}),
                         update_functions(1, [], [self.KASSIER]))
        saved = save(self.path, change, "A", now=NOW)
        self.assertEqual([entry.field for entry in saved.entries], ["Ort", "Funktionen"])
        self.assertEqual(len(os.listdir(backups.backup_folder(self.path))), 1)
        values = {"last_name": "Neu", "first_name": "Nina", "gender": "weiblich", "status": "aktiv",
                  "birthday": datetime.date(2001, 3, 4), "member_since": datetime.date(2026, 11, 1)}
        save(self.path, add_member(values, functions=[("Jugendwart", None, None, "ab sofort")]), "A", now=NOW)
        self.assertEqual([(f.nr, f.name, f.function, f.note) for f in self.read().functions_of(3)],
                         [(3, "Nina Neu", "Jugendwart", "ab sofort")])
        self.assertEqual(self.read().issues, [])


class MergeTest(StoreTest):

    @staticmethod
    def incoming(*rows):
        return [(values, set(values)) for values in rows]

    def test_people_are_matched_and_compared(self):
        members = self.read().members
        items, only = compare(self.incoming(
            {"last_name": "Muster", "first_name": "Max", "birthday": datetime.date(1967, 6, 1), "ort": "Neustadt",
             "plz": ""},                                                     # empty never empties
            {"last_name": "beispiel", "first_name": "EVA", "email": "eva@example.org"},        # name only
            {"last_name": "Muster", "first_name": "Max", "birthday": datetime.date(1990, 1, 1)},  # same name only
            {"last_name": "Neu", "first_name": "Nina", "birthday": datetime.date(2001, 3, 4)}), members)
        self.assertEqual([item.kind for item in items], [CHANGED, CHANGED, SIMILAR, NEW])
        self.assertEqual([(d.heading, d.current, d.incoming) for d in items[0].differences], [("Ort", "", "Neustadt")])
        self.assertEqual(items[1].nr, 2)
        self.assertIn("nur über den Namen", items[1].note)
        self.assertIn("Nr 1", items[2].note)
        self.assertEqual(([item.take for item in items], only), ([False, False, False, True], []))

    def test_number_counts_only_with_the_same_name(self):
        members = self.read().members
        items, only = compare(self.incoming({"nr": 1, "last_name": "Muster", "first_name": "Max"},
                                            {"nr": 2, "last_name": "Andere", "first_name": "Person"}),
                              members, by_number=True)
        self.assertEqual([(item.kind, item.nr) for item in items], [(SAME, 1), (NEW, None)])
        self.assertEqual([member.first_name for member in only], ["Eva"])

    def test_chosen_changes_new_people_and_leavers_are_saved_at_once(self):
        members = self.read()
        items, only = compare(self.incoming(
            {"last_name": "Muster", "first_name": "Max", "ort": "Neustadt", "phone": "0123"},
            {"last_name": "Neu", "first_name": "Nina", "gender": "weiblich", "birthday": datetime.date(2001, 3, 4),
             "member_since": datetime.date(2026, 11, 1), "status": "aktiv"}), members.members)
        self.assertEqual(items[0].chosen, {"ort", "phone"})                   # empty in the file: taken by default
        items[0].chosen.discard("phone")
        saved = save(self.path, merge_members(items, members.snapshot.rows, leave=[2],
                                              exit_date=datetime.date(2026, 12, 31)), "A", now=NOW)
        self.assertEqual([(e.nr, e.action, e.field) for e in saved.entries],
                         [(1, "Import", "Ort"), (3, "Import", ""), (2, "Austritt", "Status"), (2, "Austritt", "Austritt am")])
        after = self.read()
        self.assertEqual((self.member(1).ort, self.member(1).phone_number), ("Neustadt", ""))
        self.assertEqual((self.member(3).first_name, self.member(2).status), ("Nina", "ausgetreten"))
        self.assertEqual(len(os.listdir(backups.backup_folder(self.path))), 1)
        self.assertEqual(after.issues, [])


class ConflictCopyTest(StoreTest):

    def copy_as(self, name):
        target = os.path.join(self.tmp.name, name)
        with open(target, "wb") as file:
            file.write(read_bytes(self.path))
        return target

    def test_copies_with_the_same_file_id_are_found(self):
        copy = self.copy_as("Mitglieder (Konfliktkopie von Eva 2026-11-22).xlsx")
        self.copy_as("~$Mitglieder.xlsx")
        other = os.path.join(self.tmp.name, "Mitglieder (2).xlsx")
        write_member_template(other, self.config)                            # another file with another id
        members = self.read()
        self.assertTrue(members.file_id)
        self.assertEqual(conflict_copies(self.path, members.file_id), [copy])
        moved = move_to_backups(copy, NOW)
        self.assertEqual(os.path.basename(moved), "Mitglieder (Konfliktkopie von Eva 2026-11-22) 2026-11-22 140212.xlsx")
        self.assertEqual(conflict_copies(self.path, members.file_id), [])

    def test_a_missing_folder_has_no_copies(self):
        self.assertEqual(conflict_copies(os.path.join(self.tmp.name, "weg", "Mitglieder.xlsx"), "id"), [])

    def test_changes_in_a_copy_are_compared_by_number(self):
        copy = self.copy_as("Mitglieder-LAPTOP.xlsx")
        book = load_workbook(copy)
        book["Mitglieder"]["N2"] = "Kopiestadt"
        book.save(copy)
        current, other = self.read(), Members(copy)
        incoming = [(dict(member_values(m), nr=m.nr), set(member_values(m))) for m in other.members]
        items, only = compare(incoming, current.members, by_number=True)
        self.assertEqual([(item.kind, [d.incoming for d in item.differences]) for item in items],
                         [(CHANGED, ["Kopiestadt"]), (SAME, [])])


class DeleteTest(StoreTest):

    def leave(self, nr, row, exit_date):
        self.edit_in_excel(lambda sheet: (sheet.cell(row=row, column=7, value="ausgetreten"),
                                          sheet.cell(row=row, column=8, value=exit_date)))

    def test_deletion_period_finds_left_members(self):
        self.leave(1, 2, datetime.date(2015, 12, 31))
        self.assertEqual(self.read().deletion_due(), [])                    # "nie" in the template
        self.edit_in_excel(lambda book: book["Einstellungen"].__setitem__("K3", 10), whole_book=True)
        members = self.read()
        self.assertEqual([m.nr for m in members.deletion_due()], [1])       # 31.12.2025 is before 22.11.2026
        self.assertIn("laut Löschfrist", members.issues[0].message)
        self.assertFalse(members.issues[0].active)
        self.edit_in_excel(lambda book: book["Einstellungen"].__setitem__("K3", 11), whole_book=True)
        self.assertEqual(self.read().deletion_due(), [])

    def test_delete_removes_row_functions_and_personal_data_in_the_log(self):
        save(self.path, combine(update_member(1, self.read().snapshot.rows[1], {"ort": "Musterstadt"}),
                                update_functions(1, [], [("Kassier", None, None, "")]),
                                update_functions(2, [], [("Jugendwart", None, None, "")])), "A", now=NOW)
        saved = save(self.path, delete_members([(1, "Max Muster")]), "A", now=NOW)
        self.assertEqual([(e.nr, e.name, e.action) for e in saved.entries], [(1, "", "gelöscht")])
        members = self.read()
        self.assertEqual([(m.nr, m.first_name) for m in members.members], [(2, "Eva")])
        self.assertEqual([(f.nr, f.function) for f in members.functions], [(2, "Jugendwart")])
        log = self.log()
        self.assertEqual([row for row in log if row[1] == 1],
                         [("A", 1, None, "geändert", "Ort", None, None), ("A", 1, None, "geändert", "Funktionen", None, None),
                          ("A", 1, None, "gelöscht", None, None, None)])
        self.assertEqual([row[2] for row in log if row[1] == 2], ["Eva Beispiel"])          # others stay
        self.assertEqual(members.issues, [])

    def test_the_number_of_a_deleted_member_is_not_used_again(self):
        save(self.path, delete_members([(2, "Eva Beispiel")]), "A", now=NOW)
        values = {"last_name": "Neu", "first_name": "Nina", "gender": "weiblich", "status": "aktiv",
                  "birthday": datetime.date(2001, 3, 4), "member_since": datetime.date(2026, 11, 1)}
        save(self.path, add_member(values), "A", now=NOW)
        self.assertEqual([m.nr for m in self.read().members], [1, 3])

    def test_a_member_changed_meanwhile_is_not_deleted(self):
        self.edit_in_excel(lambda sheet: sheet.cell(row=2, column=3, value="Moritz"))
        with self.assertRaises(SaveError):
            save(self.path, delete_members([(1, "Max Muster")]), "A", now=NOW)
        self.assertEqual(len(self.read().members), 2)


class BackupTest(unittest.TestCase):

    def test_latest_and_one_per_month_are_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = os.path.join(tmp, backups.FOLDER)
            os.makedirs(folder)
            times = [datetime.datetime(2024, 1, 1) + datetime.timedelta(days=10 * n) for n in range(100)]
            for time in times:
                open(os.path.join(folder, "Mitglieder " + time.strftime(backups.STAMP) + ".xlsx"), "w").close()
            open(os.path.join(folder, "Andere Datei 2024-01-01 000000.xlsx"), "w").close()
            now = times[-1]
            backups.rotate(folder, "Mitglieder", now)
            kept = [time for time, _ in backups.backups_of(folder, "Mitglieder")]
            self.assertEqual(kept[-30:], times[-30:])
            older = kept[:-30]
            self.assertEqual(len({(t.year, t.month) for t in older}), len(older))   # one per month
            self.assertTrue(all((now - t).days < 380 for t in older))
            self.assertTrue(os.path.exists(os.path.join(folder, "Andere Datei 2024-01-01 000000.xlsx")))

    def test_two_backups_in_the_same_second(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "Mitglieder.xlsx")
            first, second = backups.write_backup(path, b"1", NOW), backups.write_backup(path, b"2", NOW)
            self.assertNotEqual(first, second)
            self.assertEqual(read_bytes(second), b"2")


if __name__ == "__main__":
    unittest.main()

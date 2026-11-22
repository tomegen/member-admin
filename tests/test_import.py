import datetime
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
from openpyxl import Workbook, load_workbook

from config.config import Config
from importer.gender import gender_of_first_name
from importer.mapping import (IGNORE, NAME_BOTH, NOTE, PLZ_ORT, Table, assign_numbers, convert, distinct_values,
                              guess_header_row, split_name, split_plz_ort, suggest_columns, suggest_value)
from importer.reader import SourceError, read_source
from importer.writer import write_standard_file
from model.club_file import read_bytes
from model.members import Members

OLD_LIST = os.path.join(ROOT, "tests", "fixtures", "old_list.xlsx")
TODAY = pd.Timestamp("2026-11-22")


class ImportTest(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def xlsx(self, rows, name="liste.xlsx"):
        book = Workbook()
        for row in rows:
            book.active.append(row)
        path = os.path.join(self.tmp.name, name)
        book.save(path)
        return path

    def csv(self, text, encoding="utf-8", name="liste.csv"):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding=encoding, newline="") as file:
            file.write(text)
        return path

    def table(self, path):
        source = read_source(path)
        return Table(source, guess_header_row(source.rows, self.config))

    def rows(self, path, value_maps=None):
        table = self.table(path)
        return convert(table, suggest_columns(table, self.config), value_maps or {}, TODAY)


class ReaderTest(ImportTest):

    def test_csv_with_semicolon_and_windows_umlauts(self):
        path = self.csv("Name;Vorname;Ort\nMüller;Jürgen;Köln\nBeispiel;Eva;Musterstadt, Nord\n", "cp1252")
        source = read_source(path)
        self.assertEqual((source.encoding, source.delimiter), ("cp1252", ";"))
        self.assertEqual(source.rows[1], ["Müller", "Jürgen", "Köln"])

    def test_csv_with_a_title_line_above_the_table(self):
        source = read_source(self.csv("Mitgliederliste\n\nAnrede;Name;Geb.\nHerr;Müller, Jürgen;01.06.1967\n"))
        self.assertEqual(source.delimiter, ";")
        self.assertEqual(guess_header_row(source.rows, self.config), 2)   # title, empty line, heading

    def test_csv_with_comma_and_utf8_bom(self):
        source = read_source(self.csv("﻿Name,Vorname\n\"Muster, Max\",x\n"))
        self.assertEqual((source.encoding, source.delimiter), ("utf-8-sig", ","))
        self.assertEqual(source.rows[0], ["Name", "Vorname"])

    def test_title_rows_above_the_heading_and_empty_columns(self):
        path = self.xlsx([["Mitgliederliste TSV Beispiel"], [], ["Stand: 2026"],
                          ["Nachname", "Vorname", None, "Geburtsdatum"], ["Muster", "Max", None, datetime.date(1967, 6, 1)],
                          [], ["Beispiel", "Eva", None, "13.02.1970"]])
        table = self.table(path)
        self.assertEqual(table.headings, ["Nachname", "Vorname", "Geburtsdatum"])
        self.assertEqual([number for number, _ in table.rows], [5, 7])     # rows of the file

    def test_several_sheets_take_the_first_with_data(self):
        book = Workbook()
        book.active.title = "Deckblatt"
        book.create_sheet("Mitglieder").append(["Name", "Vorname"])
        path = os.path.join(self.tmp.name, "zwei.xlsx")
        book.save(path)
        source = read_source(path)
        self.assertEqual((source.sheet, source.sheet_names), ("Mitglieder", ["Deckblatt", "Mitglieder"]))
        self.assertEqual(read_source(path, sheet="Deckblatt").rows, [])

    def test_unreadable_file(self):
        path = self.csv("kein excel", name="kaputt.xlsx")
        with self.assertRaises(SourceError):
            read_source(path)


class MappingTest(ImportTest):

    def test_old_list_of_the_app(self):
        table = self.table(OLD_LIST)
        targets = suggest_columns(table, self.config)
        self.assertEqual(dict(zip(table.headings, targets)),
                         {"Name": "last_name", "Vorname": "first_name", "Strasse": "street", "Plz": "plz",
                          "Ort": "ort", "Geburtstag": "birthday", "Telefon": "phone", "Mobil": "mobile_phone",
                          "Mitglied seit": "member_since", "IBAN": "iban", "Mandatreferenz": "reference",
                          "Mitglied": "status"})

    def test_other_software_and_content(self):
        path = self.xlsx([["Mitgl.-Nr.", "Anrede", "Name", "Anschrift", "Wohnort", "Kontakt", "Sparte", "Geb.",
                           "Eintritt", "Info"],
                          [7, "Herr", "Muster, Max", "Weg 1", "12345 Musterstadt", "max@example.org", "Tennis",
                           "01.06.1967", "05.05.2002", "zahlt bar"]])
        table = self.table(path)
        targets = dict(zip(table.headings, suggest_columns(table, self.config)))
        self.assertEqual(targets, {"Mitgl.-Nr.": "nr", "Anrede": "gender", "Name": NAME_BOTH, "Anschrift": "street",
                                   "Wohnort": PLZ_ORT, "Kontakt": "email", "Sparte": "department",
                                   "Geb.": "birthday", "Eintritt": "member_since", "Info": IGNORE})

    def test_values_names_and_towns(self):
        self.assertEqual([suggest_value("status", raw) for raw in ("1", "X", "aktiv", "0", "Passiv", "", "?")],
                         ["aktiv", "aktiv", "aktiv", "ausgetreten", "passiv", "aktiv", ""])
        self.assertEqual([suggest_value("gender", raw) for raw in ("Herr", "Frau", "w", "Familie")],
                         ["männlich", "weiblich", "weiblich", ""])
        self.assertEqual([split_name(text) for text in ("Muster, Max", "Max Peter Muster", "Muster")],
                         [("Muster", "Max"), ("Muster", "Max Peter"), ("Muster", "")])
        self.assertEqual([split_plz_ort(text) for text in ("01234 Musterstadt", "Musterstadt")],
                         [("01234", "Musterstadt"), ("", "Musterstadt")])
        self.assertEqual([gender_of_first_name(name) for name in ("Jürgen", "Anna-Lena", "Hans Peter", "Kim")],
                         ["männlich", "weiblich", "männlich", ""])
        # added from a real club list (genders as told by the club)
        self.assertEqual({gender_of_first_name(name) for name in ("Xaver", "Dimitrios", "Constantin", "André", "Robin")},
                         {"männlich"})
        self.assertEqual({gender_of_first_name(name) for name in ("Leonie", "Marleen", "Sofie", "Maxima", "Annika")},
                         {"weiblich"})


class ConvertTest(ImportTest):

    def test_rows_with_problems_estimates_and_notes(self):
        path = self.xlsx([["Name", "Vorname", "Geschlecht", "Geburtstag", "Eintritt", "Aktiv", "Austritt", "Info"],
                          ["Muster", "Max", "m", 28353, "01.01.2000", "x", None, "zahlt bar"],
                          ["Beispiel", "Eva", None, "13.02.1970", None, "0", "31.12.2020", None],
                          ["Probe", "Kim", "", "irgendwann", "2010-01-01", "", None, None],
                          ["Test", "Udo", "", "1980-01-01", "2010-01-01", "?", None, None]])
        table = self.table(path)
        targets = suggest_columns(table, self.config)
        targets[7] = NOTE
        rows = convert(table, targets, {"status": {"?": "passiv"}}, TODAY)
        max_, eva, kim, udo = rows
        self.assertEqual((max_.values["gender"], max_.values["birthday"], max_.values["status"], max_.values["note"]),
                         ("männlich", pd.Timestamp("1977-08-16"), "aktiv", "Info: zahlt bar"))
        self.assertEqual((eva.values["gender"], eva.estimated, eva.values["status"]),
                         ("weiblich", {"gender"}, "ausgetreten"))
        self.assertEqual((eva.problems(), eva.gaps()), ([], [("member_since", "Eintritt fehlt – kann später ergänzt werden")]))
        self.assertEqual((kim.values["gender"], kim.estimated), ("männlich", {"gender"}))   # majority of the list
        self.assertEqual((kim.problems(), kim.hints()), ([], ["Geburtstag nicht lesbar: irgendwann – bleibt leer"]))
        self.assertEqual(kim.values["status"], "aktiv")                                     # empty cell
        self.assertEqual((udo.values["status"], udo.problems()), ("passiv", []))

    def test_unknown_exit_date_does_not_block_but_names_and_status_do(self):
        path = self.xlsx([["Name", "Vorname", "Geschlecht", "Geburtstag", "Eintritt", "Aktiv"],
                          ["Muster", "Max", "m", None, None, "0"],
                          [None, "Eva", "w", "13.02.1970", "2000-01-01", "weg"]])
        max_, eva = self.rows(path)
        self.assertEqual(max_.problems(), [])
        self.assertEqual([field for field, _ in max_.gaps()], ["birthday", "member_since", "exit_date"])
        self.assertEqual([field for field, _ in eva.problems()], ["last_name", "status"])

    def test_without_status_column_the_exit_date_decides(self):
        path = self.xlsx([["Name", "Vorname", "Geburtstag", "Eintritt", "Austritt"],
                          ["Muster", "Max", "1967-06-01", "2000-01-01", "2020-12-31"],
                          ["Beispiel", "Eva", "1970-02-13", "2000-01-01", "2027-12-31"]])
        self.assertEqual([row.values["status"] for row in self.rows(path)], ["ausgetreten", "aktiv"])

    def test_numbers_of_the_old_list_stay_if_unique(self):
        path = self.xlsx([["Nr", "Name", "Vorname"], [5, "A", "a"], [5, "B", "b"], [None, "C", "c"], ["x", "D", "d"],
                          [2, "E", "e"]])
        rows = self.rows(path)
        rows[4].include = False
        assign_numbers(rows)
        self.assertEqual([row.values.get("nr") for row in rows], [5, 6, 7, 8, 2])

    def test_distinct_values_in_order(self):
        table = self.table(self.xlsx([["Name", "Aktiv"], ["A", "x"], ["B", None], ["C", "x"], ["D", "0"]]))
        self.assertEqual(distinct_values(table, 1), ["x", "", "0"])


class WriterTest(ImportTest):

    def test_old_list_becomes_a_standard_file_and_stays_unchanged(self):
        before = read_bytes(OLD_LIST)
        rows = self.rows(OLD_LIST)
        target = os.path.join(self.tmp.name, "Mitglieder.xlsx")
        self.assertEqual(write_standard_file(target, rows, self.config, OLD_LIST, "Vorstand A", "TSV Beispiel"), 1)
        self.assertEqual(read_bytes(OLD_LIST), before)
        members = Members(target)
        max_ = members.members[0]
        self.assertTrue(members.standard)
        self.assertEqual((max_.nr, max_.last_name, max_.gender, max_.status, max_.plz, max_.iban),
                         (1, "Mustermann", "männlich", "aktiv", "32794", "DE897324908732070"))
        self.assertEqual((max_.birthday, max_.member_since), (pd.Timestamp("1974-01-08"), pd.Timestamp("1974-01-01")))
        self.assertEqual([i.message for i in members.issues], ["Eintritt liegt vor dem Geburtstag."])   # as in the list
        self.assertEqual(members.settings.club_name, "TSV Beispiel")
        log = [row for row in load_workbook(target)["Änderungsprotokoll"].iter_rows(min_row=2, values_only=True)]
        self.assertEqual(log[0][1:], ("Vorstand A", None, None, "Import", None, None, "1 Mitglieder aus old_list.xlsx"))

    def test_departments_become_choices_and_excluded_rows_are_left_out(self):
        path = self.xlsx([["Name", "Vorname", "Geschlecht", "Geburtstag", "Eintritt", "Abteilung"],
                          ["Muster", "Max", "m", "1967-06-01", "2000-01-01", "Tennis"],
                          ["Beispiel", "Eva", "w", "1970-02-13", "2000-01-01", "Fußball"],
                          ["Probe", "Udo", "m", "1980-01-01", "2000-01-01", "Schach"]])
        rows = self.rows(path)
        rows[2].include = False
        target = os.path.join(self.tmp.name, "Mitglieder.xlsx")
        write_standard_file(target, rows, self.config, path, "A")
        members = Members(target)
        self.assertEqual([m.first_name for m in members.members], ["Max", "Eva"])
        self.assertEqual(members.settings.lists["Abteilungen"], ["Fußball", "Tennis"])


if __name__ == "__main__":
    unittest.main()

import datetime
import os
import sys
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
from PySide6.QtCore import QCoreApplication, QDate, QSettings, Qt
from PySide6.QtWidgets import QApplication

from openpyxl import load_workbook

from config.config import Config
from logic.template import write_member_template
from model.club_file import read_bytes
from ui.import_wizard import ImportWizard
from ui.main_window import MainWindow, TAB_ISSUES

OLD_LIST = os.path.join(ROOT, "tests", "fixtures", "old_list.xlsx")
app = QApplication.instance() or QApplication([])
# tests must not touch the settings of the real app
QCoreApplication.setOrganizationName("MitgliederverwaltungTest")
QCoreApplication.setApplicationName("tests")


# the import assistant is modal: a test that opens it by accident fails instead of waiting forever
def no_unexpected_import(test):
    patcher = mock.patch.object(ImportWizard, "exec", side_effect=AssertionError("unexpected import assistant"))
    patcher.start()
    test.addCleanup(patcher.stop)


def day(text):
    return None if text is None else datetime.date.fromisoformat(text)


class UiTest(unittest.TestCase):

    def setUp(self):
        QSettings().clear()
        no_unexpected_import(self)
        self.config = Config()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.window = MainWindow(self.config)
        self.addCleanup(self.window.close)

    # a standard file; rows are [name, first name, birthday, entry, 1 = member / 0 = left, mobile]
    def write_excel(self, rows):
        path = os.path.join(self.tmp.name, "members.xlsx")
        write_member_template(path, self.config)
        book = load_workbook(path)
        sheet = book["Mitglieder"]
        for row, (last, first, birthday, since, member, mobile) in enumerate(rows, start=2):
            values = {1: row - 1, 2: last, 3: first, 4: "männlich", 5: day(birthday), 6: day(since),
                      7: "aktiv" if member else "ausgetreten", 8: None if member else datetime.date(2020, 1, 1),
                      16: mobile or None}
            for column, value in values.items():
                sheet.cell(row=row, column=column, value=value)
        book.save(path)
        return path

    def sample(self):
        return self.write_excel([
            ["Muster", "Max", "1967-06-01", "2002-05-05", 1, "0171"],     # 60. birthday and 25 years in 2027
            ["Beispiel", "Eva", "1952-02-29", "2010-01-01", 1, ""],       # 75. birthday (leap day) in 2027
            ["Alt", "Karl", "1967-03-03", "2002-03-03", 0, ""],           # not counted
            ["Lücke", "Anna", None, "2020-01-01", 1, ""],                 # birthday missing
        ])

    def test_starts_on_welcome_page_and_loads_a_file(self):
        self.assertIs(self.window.stack.currentWidget(), self.window.welcome)
        self.assertTrue(self.window.load_file(self.sample()))
        self.assertIs(self.window.stack.currentWidget(), self.window.view)

    def test_unreadable_file_stays_on_welcome_page(self):
        from unittest import mock
        path = os.path.join(self.tmp.name, "broken.xlsx")
        with open(path, "w") as file:
            file.write("kein Excel")
        with mock.patch.object(self.window, "show_error") as show_error:
            self.assertFalse(self.window.load_file(path))
        show_error.assert_called_once()
        self.assertIs(self.window.stack.currentWidget(), self.window.welcome)

    def test_year_drives_preview_and_overview(self):
        self.window.load_file(self.sample())
        self.window.year_spin.setValue(2027)
        self.assertEqual(self.window.birthdays.table.rowCount(), 2)
        self.assertEqual(self.window.honors.table.rowCount(), 1)
        self.assertEqual(self.window.overview.active_card[1].text(), "3")
        self.assertIn("2027", self.window.birthdays.year_radio.text())
        self.window.year_spin.setValue(2030)
        self.assertEqual(self.window.birthdays.table.rowCount(), 0)
        self.assertFalse(self.window.birthdays.txt_button.isEnabled())

    def test_selection_and_custom_range(self):
        self.window.load_file(self.sample())
        self.window.year_spin.setValue(2027)
        page = self.window.birthdays
        page.set_all_checked(False)
        self.assertEqual(page.table.rowCount(), 0)
        page.checkboxes[page.spec.numbers.index(60)].setChecked(True)
        self.assertEqual(page.table.rowCount(), 1)
        page.set_all_checked(True)
        page.custom_radio.setChecked(True)
        page.from_edit.setDate(QDate(2027, 7, 1))
        self.assertEqual(page.table.rowCount(), 0)  # 28.02. and 01.06. are both before July
        page.from_edit.setDate(QDate(2027, 6, 1))
        self.assertEqual(page.table.rowCount(), 1)  # 01.06. is included (the range is inclusive)
        page.from_edit.setDate(QDate(2027, 1, 1))
        page.to_edit.setDate(QDate(2026, 12, 1))
        self.assertFalse(page.txt_button.isEnabled())
        self.assertIn("vor dem Start", page.count_label.text())

    def test_preview_is_sorted_by_date(self):
        self.window.load_file(self.sample())
        self.window.year_spin.setValue(2027)
        dates = [self.window.birthdays.table.item(row, 0).text() for row in range(2)]
        self.assertEqual(dates, ["28.02.2027", "01.06.2027"])

    def test_all_exports_are_written(self):
        self.window.load_file(self.sample())
        self.window.year_spin.setValue(2027)
        for page in (self.window.birthdays, self.window.honors):
            for kind in ("txt", "xlsx", "ics"):
                path = os.path.join(self.tmp.name, page.spec.file_stem + "." + kind)
                page.write(kind, path)
                self.assertGreater(os.path.getsize(path), 0, kind)

    def test_issue_tab_counts_only_active_members_and_can_show_all(self):
        self.window.load_file(self.sample())
        self.assertEqual(self.window.tabs.tabText(TAB_ISSUES), "Datenprüfung (1)")
        self.assertEqual(self.window.issues.table.rowCount(), 1)
        self.assertEqual(self.window.issues.table.item(0, 0).text(), "5")  # Excel row of the incomplete member

    def test_clean_list_shows_a_check_mark(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2002-05-05", 1, "0171"]])
        self.window.load_file(path)
        self.assertEqual(self.window.tabs.tabText(TAB_ISSUES), "Datenprüfung ✓")
        self.assertIn("Keine Auffälligkeiten", self.window.issues.summary_label.text())

    def test_reload_picks_up_changes_and_last_file_is_remembered(self):
        path = self.sample()
        self.window.load_file(path)
        self.assertEqual(QSettings().value("last_file"), path)
        self.write_excel([["Muster", "Max", "1967-06-01", "2002-05-05", 1, "0171"]])
        self.window.reload()
        self.assertEqual(self.window.overview.active_card[1].text(), "1")

    def test_overview_shows_what_is_coming_up(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2002-05-05", 1, ""],
                                 ["Beispiel", "Eva", "1970-01-01", "2010-01-01", 1, ""]])
        self.window.load_file(path)
        self.window.overview.refresh(self.window.members, 2027, [60], [25], today=pd.Timestamp("2027-05-04"))
        table = self.window.overview.upcoming_table
        self.assertEqual([(table.item(r, 0).text(), table.item(r, 1).text()) for r in range(table.rowCount())],
                         [("05.05.2027", "25 Jahre Mitgliedschaft"), ("01.06.2027", "60. Geburtstag")])
        self.window.overview.refresh(self.window.members, 2027, [60], [25], today=pd.Timestamp("2027-08-01"))
        self.assertEqual(table.rowCount(), 0)
        self.assertIn("nichts an", self.window.overview.upcoming_label.text())

    def test_numbers_chosen_in_version_0_1_go_into_new_files(self):
        from unittest import mock
        QSettings().setValue("birthday_numbers", "60, 75, 80")
        window = MainWindow(Config())
        self.addCleanup(window.close)
        path = os.path.join(self.tmp.name, "neu.xlsx")
        with mock.patch("ui.main_window.save_file", side_effect=lambda parent, name, flt, write: write(path)):
            window.welcome.template_requested.emit()
        window.load_file(path)
        self.assertEqual(window.birthdays.spec.numbers, [60, 75, 80])
        self.assertEqual(window.honors.spec.numbers, window.default_honors)

    def test_minimal_option_and_reminder_are_used_for_the_files(self):
        self.window.load_file(self.sample())
        self.window.year_spin.setValue(2027)
        page = self.window.birthdays
        page.minimal_check.setChecked(True)
        page.reminder_spin.setValue(14)
        xlsx, ics = os.path.join(self.tmp.name, "a.xlsx"), os.path.join(self.tmp.name, "a.ics")
        page.write("xlsx", xlsx)
        page.write("ics", ics)
        self.assertEqual(list(pd.read_excel(xlsx).columns), ["Anlass", "Datum", "Vorname", "Name"])
        with open(ics, "rb") as file:
            self.assertIn(b"TRIGGER:-P13DT15H", file.read().replace(b"\r\n", b""))

    def test_statistics_tab_follows_the_year(self):
        self.window.load_file(self.sample())
        self.window.year_spin.setValue(2027)
        page = self.window.statistics_page
        self.assertEqual(page.stichtag_edit.date(), QDate(2027, 12, 31))
        self.assertEqual(page.statistics.active, 3)
        self.assertEqual(page.figures_table.item(0, 1).text(), "3")
        self.assertEqual(page.groups_table.rowCount(), 7)
        self.assertEqual(page.statistics.unknown_birthday, 1)
        self.assertIn("1 Mitglieder", page.note_label.text())
        self.window.year_spin.setValue(2028)
        self.assertEqual(page.stichtag_edit.date(), QDate(2028, 12, 31))

    def test_template_button_writes_a_usable_list(self):
        from unittest import mock
        path = os.path.join(self.tmp.name, "vorlage.xlsx")
        with mock.patch("ui.main_window.save_file", side_effect=lambda parent, name, flt, write: write(path)):
            self.window.welcome.template_requested.emit()
        self.assertTrue(self.window.load_file(path))
        self.assertEqual(self.window.members.members, [])

    def test_screenshots_show_start_page_and_every_tab(self):
        from mitgliederverwaltung import take_screenshots
        folder = os.path.join(self.tmp.name, "shots")
        self.assertTrue(take_screenshots(self.window, self.sample(), folder))
        names = sorted(os.listdir(folder))
        self.assertEqual(len(names), 1 + self.window.tabs.count())
        self.assertEqual(names[:2], ["0_Start.png", "1_Ubersicht.png"])


# a standard file with two members and the settings of a club; no tests of its own
class StandardFileBase(unittest.TestCase):

    def setUp(self):
        QSettings().clear()
        no_unexpected_import(self)
        QSettings().setValue("editor_name", "Vorstand A")
        self.config = Config()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.window = MainWindow(self.config)
        self.addCleanup(self.window.close)
        self.window.show_error = lambda title, text: self.errors.append(text)
        self.errors = []
        self.path = os.path.join(self.tmp.name, "Mitglieder.xlsx")
        write_member_template(self.path, self.config)
        book = load_workbook(self.path)
        sheet, settings = book["Mitglieder"], book["Einstellungen"]
        for row, values in enumerate([[1, "Muster", "Max", "männlich", datetime.date(1967, 6, 1),
                                       datetime.date(2002, 5, 5), "aktiv"],
                                      [2, "Beispiel", "Eva", "weiblich", datetime.date(1967, 3, 3),
                                       datetime.date(2002, 3, 3), "passiv"]], start=2):
            for column, value in enumerate(values, start=1):
                sheet.cell(row=row, column=column, value=value)
        for row in range(2, 40):
            for letter in "ABCD":
                settings[letter + str(row)] = None
        for row, values in enumerate([("Geburtstag", 60, "Präsentkorb"), ("Jubiläum", 25, "Urkunde")], start=2):
            for column, value in enumerate(values, start=1):
                settings.cell(row=row, column=column, value=value)
        settings["K2"], settings["K4"], settings["K5"] = "TSV Beispiel", 3, "nein"   # passive at birthdays: no
        book.save(self.path)
        self.window.year_spin.setValue(2027)
        self.assertTrue(self.window.load_file(self.path))


class StandardFileUiTest(StandardFileBase):

    def test_the_file_brings_numbers_gifts_reminder_and_club_name(self):
        page = self.window.birthdays
        self.assertEqual(page.spec.numbers, [60])
        self.assertEqual(self.window.honors.spec.numbers, [25])
        self.assertEqual(page.table.rowCount(), 1)                          # Eva is passive: not at birthdays
        self.assertEqual(page.table.item(0, 2).text(), "Präsentkorb")
        self.assertFalse(page.table.isColumnHidden(2))
        self.assertEqual(self.window.honors.table.rowCount(), 2)           # but at honors
        self.assertEqual(page.reminder_spin.value(), 3)
        self.assertIn("TSV Beispiel", self.window.file_label.text())
        self.assertIsNone(QSettings().value("reminder_days"))              # the reminder of the club is not stored here

    def test_settings_dialog_saves_into_the_file(self):
        from unittest import mock
        from ui.club_settings_dialog import ClubSettingsDialog

        def fill(dialog):
            dialog.club_edit.setText("TSV Neu")
            dialog.list_edits["Abteilungen"].setPlainText("Fußball\n\nTennis\nFußball")
            dialog.passive_checks["Passive bei Geburtstagen"].setChecked(True)
            dialog.accept()
            return dialog.result()

        with mock.patch.object(ClubSettingsDialog, "exec", fill):
            self.window.open_settings()
        self.assertEqual(self.errors, [])
        settings = self.window.members.settings
        self.assertEqual((settings.club_name, settings.lists["Abteilungen"]), ("TSV Neu", ["Fußball", "Tennis"]))
        self.assertEqual(self.window.birthdays.table.rowCount(), 2)        # passive now count at birthdays
        self.assertEqual([tuple(o)[:3] for o in settings.occasions], [("Geburtstag", 60, "Präsentkorb"),
                                                                     ("Jubiläum", 25, "Urkunde")])
        log = list(load_workbook(self.path)["Änderungsprotokoll"].iter_rows(min_row=2, values_only=True))
        self.assertEqual([(row[1], row[5]) for row in log], [("Vorstand A", "Abteilungen"),
                                                             ("Vorstand A", "Vereinsname"),
                                                             ("Vorstand A", "Passive bei Geburtstagen")])

    def test_settings_dialog_without_changes_does_not_touch_the_file(self):
        from unittest import mock
        from ui.club_settings_dialog import ClubSettingsDialog
        before = os.path.getmtime(self.path)
        with mock.patch.object(ClubSettingsDialog, "exec", lambda dialog: dialog.accept() or dialog.result()):
            self.window.open_settings()
        self.assertEqual(os.path.getmtime(self.path), before)
        self.assertFalse(os.path.isdir(os.path.join(self.tmp.name, "Sicherungen")))

    def test_dialog_keeps_defaults_and_refuses_twins(self):
        from model.club_settings import ClubSettings
        from ui.club_settings_dialog import ClubSettingsDialog
        unchanged = ClubSettingsDialog(ClubSettings(), [60, 70], [25], "A", self.window)
        self.assertEqual(unchanged.occasion_table.rowCount(), 3)           # the defaults are shown ...
        unchanged.accept()
        self.assertEqual(unchanged.settings.occasions, [])                 # ... but not written into the file
        twins = ClubSettingsDialog(ClubSettings(), [60, 70], [25], "A", self.window)
        twins.occasion_table.cellWidget(1, 1).setValue(60)
        twins.accept()
        self.assertIn("Geburtstag 60 steht doppelt", twins.error_label.text())

    def test_open_file_asks_before_saving_anyway(self):
        from store.changes import update_settings
        with open(os.path.join(self.tmp.name, "~$Mitglieder.xlsx"), "wb") as file:
            file.write(bytes([4]) + b"Eva " + b" " * 40)
        settings = self.window.members.settings
        new = type(settings)(settings.occasions, settings.lists, dict(settings.general, Vereinsname="X"))
        questions = []
        self.window.ask = lambda title, text: questions.append(text) or False
        self.assertFalse(self.window.save_change(update_settings(settings, new)))
        self.assertIn("(von Eva)", questions[0])
        self.window.ask = lambda title, text: True
        self.assertTrue(self.window.save_change(update_settings(settings, new)))
        self.assertEqual(self.window.members.settings.club_name, "X")


class MemberEditingUiTest(StandardFileBase):

    def setUp(self):
        super().setUp()
        self.window.ask = lambda title, text: self.questions.append(text) or True
        self.questions = []

    def edit_in_excel(self, cells):
        book = load_workbook(self.path)
        for coordinate, value in cells.items():
            book["Mitglieder"][coordinate] = value
        book.save(self.path)

    def member(self, nr):
        return [m for m in self.window.members.members if m.nr == nr][0]

    @staticmethod
    def filling(values, functions=()):
        def fill(dialog):
            for field, value in values.items():
                widget = dialog.widgets[field]
                if hasattr(widget, "set_value"):
                    widget.set_value(value)
                elif hasattr(widget, "setCurrentText"):
                    widget.setCurrentText(value)
                elif hasattr(widget, "setPlainText"):
                    widget.setPlainText(value)
                else:
                    widget.setText(value)
            for function in functions:
                dialog.add_function_row(*function)
            dialog.accept()
            return dialog.result()
        return fill

    def test_members_tab_lists_filters_and_searches(self):
        page = self.window.members_page
        self.assertEqual(self.window.tabs.widget(1), page)
        self.assertEqual(page.table.rowCount(), 2)
        page.status_box.setCurrentText("passiv")
        self.assertEqual([page.table.item(r, 2).text() for r in range(page.table.rowCount())], ["Eva"])
        page.status_box.setCurrentText("alle Einträge")
        page.search_edit.setText("must")
        self.assertEqual(page.count_label.text(), "1 von 2 Einträgen")
        self.assertFalse(page.numbers_button.isVisible())
        self.window.overview.open_tab.emit("honors")                      # buttons on the overview
        self.assertIs(self.window.tabs.currentWidget(), self.window.honors)

    def test_new_member_is_saved_with_functions_and_a_twin_is_asked_for(self):
        from ui.member_dialog import MemberDialog
        values = {"last_name": "Neu", "first_name": "Nina", "gender": "weiblich",
                  "birthday": datetime.date(2001, 3, 4), "member_since": datetime.date(2026, 11, 1),
                  "ort": "Musterstadt"}
        with mock.patch.object(MemberDialog, "exec", self.filling(values, [("Jugendwart", None, None, "")])):
            self.assertTrue(self.window.actions.new_member())
        nina = self.member(3)
        self.assertEqual((nina.first_name, nina.status, nina.ort), ("Nina", "aktiv", "Musterstadt"))
        self.assertEqual([f.function for f in self.window.members.functions_of(3)], ["Jugendwart"])
        with mock.patch.object(MemberDialog, "exec", self.filling(values)):
            self.assertTrue(self.window.actions.new_member())
        self.assertIn("steht schon in der Liste", self.questions[0])
        self.assertEqual(len(self.window.members.members), 4)

    def test_new_member_needs_the_mandatory_fields(self):
        from ui.member_dialog import MemberDialog
        dialog = MemberDialog(self.window.members.settings, parent=self.window)
        dialog.widgets["last_name"].setText("Neu")
        dialog.accept()
        self.assertEqual(dialog.error_label.text(), "Vorname fehlt.")
        self.assertFalse(dialog.result())

    def test_only_changed_fields_are_saved(self):
        from ui.member_dialog import MemberDialog
        self.edit_in_excel({"E2": "irgendwann"})            # unreadable birthday of Max
        self.window.reload()
        with mock.patch.object(MemberDialog, "exec", self.filling({"phone": "0123 4567"})):
            self.assertTrue(self.window.actions.edit_member(self.member(1)))
        self.assertEqual(self.member(1).phone_number, "0123 4567")
        self.assertEqual(load_workbook(self.path)["Mitglieder"]["E2"].value, "irgendwann")   # not lost

    def test_conflict_with_a_change_in_excel_is_decided_per_field(self):
        from ui.conflict_dialog import ConflictDialog, TAKE_THEIRS
        from ui.member_dialog import MemberDialog
        max_ = self.member(1)

        def fill_and_meanwhile_change_excel(dialog):
            self.edit_in_excel({"N2": "Handystadt", "O2": "0999"})     # Ort and Telefon changed on a phone
            return self.filling({"ort": "Musterstadt", "phone": "0123", "email": "max@example.org"})(dialog)

        def choose(dialog):
            self.assertEqual([f.heading for f in dialog.conflict.fields], ["Ort", "Telefon"])
            dialog.choices["phone"].setCurrentText(TAKE_THEIRS)
            dialog.accept()
            return dialog.result()

        with mock.patch.object(MemberDialog, "exec", fill_and_meanwhile_change_excel), \
                mock.patch.object(ConflictDialog, "exec", choose):
            self.assertTrue(self.window.actions.edit_member(max_))
        max_ = self.member(1)
        self.assertEqual((max_.ort, max_.phone_number, max_.email), ("Musterstadt", "0999", "max@example.org"))

    def test_a_field_emptied_in_the_dialog_is_empty_in_the_file(self):
        from ui.member_dialog import MemberDialog
        self.edit_in_excel({"O2": "0123 4567"})
        self.window.reload()
        with mock.patch.object(MemberDialog, "exec", self.filling({"phone": ""})):
            self.assertTrue(self.window.actions.edit_member(self.member(1)))
        self.assertEqual(self.member(1).phone_number, "")
        self.assertIsNone(load_workbook(self.path)["Mitglieder"]["O2"].value)

    def test_exit_keeps_the_member(self):
        from ui.member_dialog import ExitDialog

        def fill(dialog):
            dialog.date_field.set_value(datetime.date(2026, 10, 31))
            dialog.reason_box.setCurrentText("Umzug")
            dialog.accept()
            return dialog.result()

        with mock.patch.object(ExitDialog, "exec", fill):
            self.assertTrue(self.window.actions.record_exit(self.member(2)))
        eva = self.member(2)
        self.assertEqual((eva.status, eva.exit_date, eva.exit_reason),
                         ("ausgetreten", pd.Timestamp("2026-10-31"), "Umzug"))
        log = [row for row in load_workbook(self.path)["Änderungsprotokoll"].iter_rows(min_row=2, values_only=True)]
        self.assertEqual({row[4] for row in log}, {"Austritt"})

    def test_rows_without_number_get_one_before_editing(self):
        self.edit_in_excel({"A4": None, "B4": "Ohne", "C4": "Nummer", "D4": "divers",
                            "E4": datetime.date(1990, 1, 1), "F4": datetime.date(2020, 1, 1), "G4": "aktiv"})
        self.window.reload()
        page = self.window.members_page
        self.assertFalse(page.numbers_button.isHidden())
        without = [m for m in self.window.members.members if m.nr is None][0]
        self.assertFalse(self.window.actions.edit_member(without))       # asks, then gives numbers
        self.assertIn("noch keine Mitgliedsnummer", self.questions[0])
        self.assertEqual(self.member(3).last_name, "Ohne")
        self.assertTrue(page.numbers_button.isHidden())


    def test_changes_from_outside_are_read_again(self):
        self.window.reload_if_changed()                                   # nothing changed: nothing happens
        self.assertEqual(self.window.statusBar().currentMessage(), "")
        self.edit_in_excel({"N2": "Handystadt"})
        self.window.on_file_changed(self.path)
        self.window.reload_if_changed()
        self.assertEqual(self.member(1).ort, "Handystadt")
        self.assertIn("außerhalb der App geändert", self.window.statusBar().currentMessage())
        self.assertIn(self.path, self.window.watcher.files())


class MergeUiTest(StandardFileBase):

    def setUp(self):
        super().setUp()
        self.window.ask = lambda title, text: self.questions.append(text) or True
        self.window.inform = lambda title, text: self.questions.append(text)
        self.questions = []

    def member(self, nr):
        return [m for m in self.window.members.members if m.nr == nr][0]

    def test_a_list_is_compared_and_the_user_decides(self):
        from openpyxl import Workbook
        from ui.merge_dialog import MergeDialog
        book = Workbook()
        for row in [["Name", "Vorname", "Geschlecht", "Geburtstag", "Eintritt", "E-Mail", "Ort"],
                    ["Muster", "Max", None, None, None, "max@example.org", "Neustadt"],     # in the file
                    ["Neu", "Nina", "w", "04.03.2001", "01.11.2026", "nina@example.org", None]]:
            book.active.append(row)
        path = os.path.join(self.tmp.name, "mails.xlsx")
        book.save(path)

        def run_wizard(wizard):
            wizard.restart()
            for _ in range(3):
                wizard.next()
            check = wizard.check_page
            self.assertTrue(check.isComplete())                 # Max needs no complete data: he is in the file
            self.assertIn("Nr 1", check.table.item(0, 9).text())
            wizard.next()
            wizard.accept()
            return wizard.result()

        def decide(dialog):
            self.assertEqual([(i.kind, i.name()) for i in dialog.items], [("geändert", "Max Muster"), ("neu", "Nina Neu")])
            self.assertEqual(dialog.items[0].chosen, {"email", "ort"})
            town = [row for row in dialog.field_items if row.data(0, Qt.ItemDataRole.UserRole)[1] == "ort"][0]
            town.setCheckState(0, Qt.CheckState.Unchecked)                           # keep the town
            dialog.leave_items[0].setCheckState(0, Qt.CheckState.Checked)            # Eva is not in the list
            dialog.accept()
            return dialog.result()

        with mock.patch.object(ImportWizard, "exec", run_wizard), mock.patch.object(MergeDialog, "exec", decide):
            self.assertTrue(self.window.actions.merge_list(path))
        self.assertEqual((self.member(1).email, self.member(1).ort), ("max@example.org", ""))
        self.assertEqual((self.member(3).first_name, self.member(3).email), ("Nina", "nina@example.org"))
        self.assertEqual(self.member(2).status, "ausgetreten")

    def test_conflict_copy_is_offered_compared_and_moved_away(self):
        from ui.merge_dialog import MergeDialog
        copy = os.path.join(self.tmp.name, "Mitglieder (Konfliktkopie von Eva).xlsx")
        book = load_workbook(self.path)
        book["Mitglieder"]["N2"] = "Kopiestadt"
        book.save(copy)
        self.window.reload()
        self.assertFalse(self.window.members_page.copies_button.isHidden())

        def take(dialog):
            self.assertEqual([d.incoming for d in dialog.items[0].differences], ["Kopiestadt"])
            dialog.accept()
            return dialog.result()

        with mock.patch.object(MergeDialog, "exec", take):
            self.window.offer_conflict_copies()
        self.assertIn("Konfliktkopie", self.questions[0])
        self.assertEqual(self.member(1).ort, "Kopiestadt")
        self.assertFalse(os.path.exists(copy))
        self.assertEqual(len([n for n in os.listdir(os.path.join(self.tmp.name, "Sicherungen"))
                              if "Konfliktkopie" in n]), 1)
        self.assertTrue(self.window.members_page.copies_button.isHidden())
        self.window.offer_conflict_copies()                                 # nothing left: no question
        self.assertEqual(len(self.questions), 1)


class DeleteUiTest(StandardFileBase):

    def setUp(self):
        super().setUp()
        book = load_workbook(self.path)
        book["Mitglieder"]["G3"], book["Mitglieder"]["H3"] = "ausgetreten", datetime.date(2010, 6, 30)   # Eva
        book["Einstellungen"]["K3"] = 10                                                                    # years
        book.save(self.path)
        self.window.reload()
        self.window.ask = lambda title, text: self.questions.append(text) or True
        self.questions = []

    def test_deletion_period_is_shown_and_deletes_after_confirmation(self):
        from ui.delete_dialog import DeleteDialog
        self.assertFalse(self.window.members_page.due_button.isHidden())
        self.assertIn("1 ausgetretenes Mitglied kann", self.window.overview.deletion_label.text())

        def confirm(dialog):
            self.assertEqual([m.first_name for m in dialog.chosen()], ["Eva"])
            dialog.accept()
            return dialog.result()

        with mock.patch.object(DeleteDialog, "exec", confirm):
            self.assertTrue(self.window.actions.delete_due())
        self.assertEqual([m.first_name for m in self.window.members.members], ["Max"])
        self.assertTrue(self.window.members_page.due_button.isHidden())
        self.assertFalse(self.window.overview.deletion_label.isVisible())

    def test_a_single_entry_is_deleted_with_a_warning_for_members(self):
        max_ = self.window.members.members[0]
        self.window.ask = lambda title, text: self.questions.append(text) or False
        self.assertFalse(self.window.actions.delete_member(max_))
        self.assertIn("kein ausgetretenes Mitglied", self.questions[0])
        self.window.ask = lambda title, text: True
        self.assertTrue(self.window.actions.delete_member(max_))
        self.assertEqual([m.first_name for m in self.window.members.members], ["Eva"])


class ImportUiTest(unittest.TestCase):

    def setUp(self):
        QSettings().clear()
        QSettings().setValue("editor_name", "Vorstand A")
        self.config = Config()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.window = MainWindow(self.config)
        self.addCleanup(self.window.close)
        self.window.inform = lambda title, text: self.messages.append(text)
        self.window.show_error = lambda title, text: self.messages.append(text)
        self.messages = []

    def copy(self, source, name):
        target = os.path.join(self.tmp.name, name)
        with open(source, "rb") as read, open(target, "wb") as write:
            write.write(read.read())
        return target

    @staticmethod
    def go_to_check_page(wizard):
        wizard.restart()
        for _ in range(3):              # columns, values, check
            wizard.next()
        return wizard.check_page

    def test_opening_an_old_list_runs_the_import_and_opens_the_new_file(self):
        old = self.copy(OLD_LIST, "alt.xlsx")
        before = read_bytes(old)

        def run(wizard):
            check = self.go_to_check_page(wizard)
            self.assertFalse(check.isComplete())                    # the gender is estimated: confirm first
            self.assertEqual(check.table.item(0, 4).text(), "männlich")
            check.confirm_estimates()
            self.assertTrue(check.isComplete())
            wizard.next()
            wizard.target_page.club_edit.setText("TSV Test")
            wizard.accept()
            return wizard.result()

        with mock.patch.object(ImportWizard, "exec", run):
            self.assertTrue(self.window.load_file(old))
        new = os.path.join(self.tmp.name, "Mitgliederliste.xlsx")
        self.assertEqual(self.window.filename, new)
        self.assertTrue(self.window.members.standard)
        self.assertEqual(self.window.members.members[0].last_name, "Mustermann")
        self.assertIn("TSV Test", self.window.file_label.text())
        self.assertIn("1 Mitglieder wurden", self.messages[0])
        self.assertEqual(read_bytes(old), before)
        self.assertEqual(QSettings().value("last_file"), new)

    def test_csv_without_entry_date_is_completed_for_many_rows_at_once(self):
        path = os.path.join(self.tmp.name, "export.csv")
        with open(path, "w", encoding="cp1252", newline="") as file:
            file.write("Mitgliederliste\n\nAnrede;Name;Geb.\nHerr;Müller, Jürgen;01.06.1967\n"
                       "Frau;Beispiel, Eva;13.02.1970\nFamilie;Probe, Kim;irgendwann\n")

        def run(wizard):
            self.assertEqual(wizard.source.delimiter, ";")
            check = self.go_to_check_page(wizard)
            self.assertFalse(check.isComplete())
            for row in range(3):                                    # select the empty entry dates
                check.table.item(row, 6).setSelected(True)
            check.ask_value = lambda heading, options: "01.01.2000"
            check.fill_selected()
            check.table.item(2, 5).setText("03.03.1980")            # typed in the table
            check.confirm_estimates()                               # Kim: gender of the majority
            self.assertTrue(check.isComplete())
            wizard.next()
            wizard.accept()
            return wizard.result()

        with mock.patch.object(ImportWizard, "exec", run):
            self.assertTrue(self.window.load_file(path))
        members = self.window.members.members
        self.assertEqual([(m.nr, m.first_name, m.gender, m.member_since) for m in members],
                         [(1, "Jürgen", "männlich", pd.Timestamp("2000-01-01")),
                          (2, "Eva", "weiblich", pd.Timestamp("2000-01-01")),
                          (3, "Kim", "männlich", pd.Timestamp("2000-01-01"))])
        self.assertEqual(members[2].birthday, pd.Timestamp("1980-03-03"))

    def test_unknown_dates_stay_empty_and_appear_in_the_data_check(self):
        from openpyxl import Workbook
        book = Workbook()
        for row in [["Name", "Vorname", "Geschlecht", "Geburtstag", "Eintritt", "Mitglied"],
                    ["Muster", "Max", "m", None, "2002-05-05", 1],          # birthday unknown
                    ["Beispiel", "Eva", "w", "1970-02-13", None, 1],        # entry unknown
                    ["Probe", "Udo", "m", "1960-01-01", "1990-01-01", 0]]:  # left, date unknown
            book.active.append(row)
        path = os.path.join(self.tmp.name, "alt.xlsx")
        book.save(path)

        def run(wizard):
            check = self.go_to_check_page(wizard)
            self.assertTrue(check.isComplete())                     # nothing has to be filled in
            self.assertIn("3 mit unbekanntem Datum", check.summary.text())
            wizard.next()
            wizard.accept()
            return wizard.result()

        with mock.patch.object(ImportWizard, "exec", run):
            self.assertTrue(self.window.load_file(path))
        found = [(issue.name, issue.active, issue.message.split(",")[0]) for issue in self.window.members.issues]
        self.assertEqual(found, [("Max Muster", True, "Geburtstag fehlt"), ("Eva Beispiel", True, "Eintritt fehlt"),
                                 ("Udo Probe", False, "Status ist „ausgetreten“")])
        self.assertEqual(self.window.tabs.tabText(TAB_ISSUES), "Datenprüfung (2)")

    def test_rows_can_be_left_out_and_cancel_changes_nothing(self):
        old = self.copy(OLD_LIST, "alt.xlsx")
        with mock.patch.object(ImportWizard, "exec", lambda wizard: 0):
            self.assertFalse(self.window.load_file(old))
        self.assertIs(self.window.stack.currentWidget(), self.window.welcome)
        self.assertEqual(sorted(os.listdir(self.tmp.name)), ["alt.xlsx"])

        def run(wizard):
            check = self.go_to_check_page(wizard)
            check.table.item(0, 0).setCheckState(Qt.CheckState.Unchecked)
            self.assertFalse(check.isComplete())                    # nothing left to take over
            return 0
        with mock.patch.object(ImportWizard, "exec", run):
            self.window.load_file(old)

    def test_unreadable_file_is_reported(self):
        path = os.path.join(self.tmp.name, "kaputt.xlsx")
        with open(path, "w") as file:
            file.write("kein Excel")
        self.assertFalse(self.window.load_file(path))
        self.assertIn("konnte nicht gelesen werden", self.messages[0])


if __name__ == "__main__":
    unittest.main()

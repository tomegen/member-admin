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
from PySide6.QtCore import QCoreApplication, QDate, QSettings
from PySide6.QtWidgets import QApplication

from openpyxl import load_workbook

from config.config import Config
from logic.template import write_member_template
from ui.main_window import MainWindow, TAB_ISSUES

app = QApplication.instance() or QApplication([])
# tests must not touch the settings of the real app
QCoreApplication.setOrganizationName("MitgliederverwaltungTest")
QCoreApplication.setApplicationName("tests")


class UiTest(unittest.TestCase):

    def setUp(self):
        QSettings().clear()
        self.config = Config()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.window = MainWindow(self.config)
        self.addCleanup(self.window.close)

    def write_excel(self, rows):
        c = self.config
        columns = [c.last_name_config, c.first_name_config, c.birthdays_config, c.member_since_config,
                   c.member_config, c.mobile_phone_config]
        path = os.path.join(self.tmp.name, "members.xlsx")
        pd.DataFrame(rows, columns=columns).to_excel(path, index=False)
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

    def test_settings_change_the_choices_and_are_remembered(self):
        self.window.load_file(self.sample())
        self.window.year_spin.setValue(2027)
        page = self.window.birthdays
        page.checkboxes[page.spec.numbers.index(75)].setChecked(False)
        self.window.set_numbers([60, 75, 80], [25])
        self.assertEqual([box.text() for box in page.checkboxes], ["60. Geburtstag", "75. Geburtstag", "80. Geburtstag"])
        self.assertFalse(page.checkboxes[1].isChecked())                       # unchecked stays unchecked
        self.assertEqual(page.table.rowCount(), 1)
        self.assertEqual(len(self.window.honors.checkboxes), 1)
        self.assertEqual(QSettings().value("birthday_numbers"), "60, 75, 80")
        # a new window (= next start of the app) uses the saved numbers
        again = MainWindow(Config())
        self.addCleanup(again.close)
        self.assertEqual(again.config.birthday_config, [60, 75, 80])
        # the defaults are not stored
        self.window.set_numbers(self.window.default_birthdays, self.window.default_honors)
        self.assertIsNone(QSettings().value("birthday_numbers"))

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
        self.assertEqual(QSettings().value("reminder_days"), 14)

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

    def test_old_lists_can_only_be_shown(self):
        path = os.path.join(self.tmp.name, "alt.xlsx")
        pd.DataFrame([["Muster", "Max", "1967-06-01", "2002-05-05", 1]],
                     columns=["Name", "Vorname", "Geburtstag", "Mitglied seit", "Mitglied"]).to_excel(path, index=False)
        self.window.load_file(path)
        page = self.window.members_page
        page.table.selectRow(0)
        self.assertEqual(page.table.rowCount(), 1)
        self.assertFalse(page.new_button.isEnabled())
        self.assertFalse(page.edit_button.isEnabled())
        self.assertIn("nicht im Standardformat", page.note_label.text())

    def test_changes_from_outside_are_read_again(self):
        self.window.reload_if_changed()                                   # nothing changed: nothing happens
        self.assertEqual(self.window.statusBar().currentMessage(), "")
        self.edit_in_excel({"N2": "Handystadt"})
        self.window.on_file_changed(self.path)
        self.window.reload_if_changed()
        self.assertEqual(self.member(1).ort, "Handystadt")
        self.assertIn("außerhalb der App geändert", self.window.statusBar().currentMessage())
        self.assertIn(self.path, self.window.watcher.files())


if __name__ == "__main__":
    unittest.main()

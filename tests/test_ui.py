import os
import sys
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
from PySide6.QtCore import QCoreApplication, QDate, QSettings
from PySide6.QtWidgets import QApplication

from config.config import Config
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
        self.assertIn("1 aktive", page.note_label.text())
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


if __name__ == "__main__":
    unittest.main()

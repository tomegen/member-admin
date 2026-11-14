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
        for page, kinds in ((self.window.birthdays, ("txt", "xlsx", "ics")), (self.window.honors, ("txt", "xlsx"))):
            for kind in kinds:
                path = os.path.join(self.tmp.name, page.spec.file_stem + "." + kind)
                page.write(kind, path)
                self.assertGreater(os.path.getsize(path), 0, kind)
        self.assertFalse(hasattr(self.window.honors, "ics_button"))

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


if __name__ == "__main__":
    unittest.main()

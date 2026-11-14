import contextlib
import io
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# the logic does not need a GUI: stub tkinter if this python has no Tk
try:
    import tkinter  # noqa: F401
    from tkinter import messagebox  # noqa: F401
except ImportError:
    tk_stub = types.ModuleType("tkinter")
    tk_stub.messagebox = types.ModuleType("tkinter.messagebox")
    sys.modules["tkinter"] = tk_stub
    sys.modules["tkinter.messagebox"] = tk_stub.messagebox

import pandas as pd
from config.config import Config
from logic.birthday_calculation import is_birthday, write_birthdays_into_ics, write_birthdays_into_txt
from logic.date_utils import shift_years
from logic.honor_calculation import is_honor
from model.member import Member
from model.members import Members, MemberListError

JAN_1_2027 = pd.Timestamp("2027-01-01")
DEC_31_2027 = pd.Timestamp("2027-12-31")


def make_member(birthday, member_since="2000-01-01", first_name="Max", last_name="Müßig", member=1):
    return Member(last_name, first_name, "", "", "", pd.Timestamp(birthday), "", "",
                  pd.Timestamp(member_since), "", "", member)


class LeapDayTest(unittest.TestCase):

    def test_shift_years_falls_back_to_28_february(self):
        self.assertEqual(shift_years(pd.Timestamp("1952-02-29"), 75), pd.Timestamp("2027-02-28"))
        self.assertEqual(shift_years(pd.Timestamp("1952-02-29"), 76), pd.Timestamp("2028-02-29"))
        self.assertEqual(shift_years(pd.Timestamp("2028-02-29"), -30), pd.Timestamp("1998-02-28"))

    def test_ics_export_with_leap_day_member_2027(self):
        # born 29.02.1952 turns 75 in 2027 (a non-leap year)
        member = make_member("1952-02-29")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "birthdays.ics")
            self.assertTrue(write_birthdays_into_ics([member], [75], JAN_1_2027, DEC_31_2027, path))
            with open(path, "rb") as file:
                self.assertIn(b"DTSTART:20270228T000000", file.read().replace(b"\r\n", b""))

    def test_range_starting_on_leap_day(self):
        member = make_member("1998-02-28")
        self.assertTrue(is_birthday(member, 30, pd.Timestamp("2028-02-29"), pd.Timestamp("2028-03-31")))


class CalculationTest(unittest.TestCase):

    def test_birthday_range_within_2027(self):
        self.assertTrue(is_birthday(make_member("1967-06-01"), 60, JAN_1_2027, DEC_31_2027))
        self.assertFalse(is_birthday(make_member("1966-06-01"), 60, JAN_1_2027, DEC_31_2027))

    def test_birthday_range_over_new_year(self):
        start, end = pd.Timestamp("2026-12-01"), pd.Timestamp("2027-01-31")
        self.assertTrue(is_birthday(make_member("1976-12-24"), 50, start, end))
        self.assertTrue(is_birthday(make_member("1977-01-15"), 50, start, end))
        self.assertFalse(is_birthday(make_member("1977-02-15"), 50, start, end))

    def test_honor_and_non_members(self):
        self.assertTrue(is_honor(make_member("1980-01-01", member_since="2002-05-05"), 25, JAN_1_2027, DEC_31_2027))
        self.assertFalse(is_honor(make_member("1980-01-01", member_since="2002-05-05", member=0), 25,
                                  JAN_1_2027, DEC_31_2027))

    def test_txt_is_utf8_without_doubled_carriage_returns(self):
        member = make_member("1967-06-01")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "birthdays.txt")
            write_birthdays_into_txt([member], [60], JAN_1_2027, DEC_31_2027, path)
            with open(path, "rb") as file:
                content = file.read()
        self.assertIn("Müßig".encode("utf-8"), content)
        self.assertNotIn(b"\r\r", content)


class MemberListTest(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write_excel(self, rows, drop=()):
        c = self.config
        columns = [c.last_name_config, c.first_name_config, c.birthdays_config, c.member_since_config,
                   c.member_config, c.mobile_phone_config]
        data = pd.DataFrame(rows, columns=columns).drop(columns=list(drop))
        path = os.path.join(self.tmp.name, "members.xlsx")
        data.to_excel(path, index=False)
        return path

    def test_config_is_found_independent_of_working_directory(self):
        old_cwd = os.getcwd()
        os.chdir(self.tmp.name)
        try:
            self.assertEqual(Config().birthday_config[0], self.config.birthday_config[0])
        finally:
            os.chdir(old_cwd)

    def test_missing_optional_column_is_allowed(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2020-03-01", 1, "0171"]],
                                drop=[self.config.mobile_phone_config])
        members = Members(path, self.config)
        self.assertEqual(len(members.members), 1)
        self.assertEqual(members.members[0].mobile_phone, "")

    def test_missing_mandatory_column_names_the_column(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2020-03-01", 1, "0171"]],
                                drop=[self.config.member_since_config])
        with self.assertRaises(MemberListError) as error:
            Members(path, self.config)
        self.assertIn(self.config.member_since_config, str(error.exception))

    def test_empty_member_cell_is_not_counted_and_warns(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2020-03-01", None, ""],
                                 ["Beispiel", "Eva", "1970-01-01", "2021-01-01", 1, ""]])
        with mock.patch("model.members.mb") as message_box:
            members = Members(path, self.config)
        message_box.showwarning.assert_called_once()
        self.assertEqual([m.member for m in members.members], [0, 1])
        self.assertEqual(members.calculate_members(), 1)

    def test_new_members_for_given_year(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2027-03-01", 1, ""],
                                 ["Beispiel", "Eva", "1970-01-01", "2021-01-01", 1, ""]])
        members = Members(path, self.config)
        self.assertEqual(members.calculate_new_members(2027), 1)
        self.assertEqual(members.calculate_new_members(2021), 1)

    def test_no_personal_data_on_console(self):
        path = self.write_excel([["Geheimname", "Max", "1967-06-01", "2020-03-01", 1, ""]])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            Members(path, self.config)
        self.assertNotIn("Geheimname", output.getvalue())


if __name__ == "__main__":
    unittest.main()

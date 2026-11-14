import contextlib
import io
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
from config.config import Config, ConfigError
from logic.birthday_calculation import find_birthdays, is_birthday, write_birthdays_into_ics, \
    write_birthdays_into_txt
from logic.date_utils import shift_years
from logic.export import write_entries_into_xlsx
from logic.honor_calculation import find_honors, is_honor
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
                content = file.read().replace(b"\r\n", b"")
        self.assertIn(b"DTSTART;VALUE=DATE:20270228", content)
        self.assertIn(b"DTEND;VALUE=DATE:20270301", content)

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

    def test_unknown_dates_are_skipped(self):
        member = make_member("1967-06-01")
        member.birthday = pd.NaT
        member.member_since = pd.NaT
        self.assertFalse(is_birthday(member, 60, JAN_1_2027, DEC_31_2027))
        self.assertFalse(is_honor(member, 25, JAN_1_2027, DEC_31_2027))

    def test_find_entries_have_the_occasion_date(self):
        member = make_member("1967-06-01", member_since="2002-05-05")
        birthdays = find_birthdays([member], [60, 65], JAN_1_2027, DEC_31_2027)
        honors = find_honors([member], [25, 30], JAN_1_2027, DEC_31_2027)
        self.assertEqual([(e.number, e.date) for e in birthdays], [(60, pd.Timestamp("2027-06-01"))])
        self.assertEqual([(e.number, e.date) for e in honors], [(25, pd.Timestamp("2027-05-05"))])

    def test_txt_is_utf8_without_doubled_carriage_returns(self):
        member = make_member("1967-06-01")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "birthdays.txt")
            write_birthdays_into_txt([member], [60], JAN_1_2027, DEC_31_2027, path)
            with open(path, "rb") as file:
                content = file.read()
        self.assertIn("Müßig".encode("utf-8"), content)
        self.assertNotIn(b"\r\r", content)

    def test_xlsx_export_has_real_dates_sorted_by_date(self):
        late = make_member("1967-11-01", first_name="Spät")
        early = make_member("1967-02-01", first_name="Früh")
        entries = find_birthdays([late, early], [60], JAN_1_2027, DEC_31_2027)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "result.xlsx")
            write_entries_into_xlsx(entries, lambda n: str(n) + ". Geburtstag", path)
            table = pd.read_excel(path)
        self.assertEqual(list(table["Vorname"]), ["Früh", "Spät"])
        self.assertEqual(table["Anlass"][0], "60. Geburtstag")
        self.assertEqual(pd.Timestamp(table["Datum"][0]), pd.Timestamp("2027-02-01"))


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

    def test_missing_config_raises_a_readable_error(self):
        with self.assertRaises(ConfigError):
            Config(path=os.path.join(self.tmp.name, "does-not-exist.ini"))

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

    def test_unreadable_file_raises_a_readable_error(self):
        path = os.path.join(self.tmp.name, "broken.xlsx")
        with open(path, "w") as file:
            file.write("das ist keine Excel-Datei")
        with self.assertRaises(MemberListError):
            Members(path, self.config)

    def test_empty_member_cell_is_not_counted_and_reported(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2020-03-01", None, ""],
                                 ["Beispiel", "Eva", "1970-01-01", "2021-01-01", 1, ""]])
        members = Members(path, self.config)
        self.assertEqual([m.member for m in members.members], [0, 1])
        self.assertEqual(members.calculate_members(), 1)
        self.assertEqual(members.calculate_inactive(), 1)
        self.assertEqual([(i.row, i.name) for i in members.issues], [(2, "Max Muster")])

    def test_missing_dates_are_collected_with_excel_row_and_activity(self):
        path = self.write_excel([["Muster", "Max", None, "2020-03-01", 1, ""],
                                 ["Beispiel", "Eva", "1970-01-01", None, 0, ""]])
        members = Members(path, self.config)
        found = [(i.row, i.name, i.active, i.message.split(" ")[0]) for i in members.issues]
        self.assertEqual(found, [(2, "Max Muster", True, "Geburtstag"), (3, "Eva Beispiel", False, "Mitglied")])
        self.assertTrue(pd.isna(members.members[0].birthday))

    def test_completely_empty_rows_are_skipped(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2020-03-01", 1, ""],
                                 [None, None, None, None, None, None]])
        members = Members(path, self.config)
        self.assertEqual(len(members.members), 1)
        self.assertEqual(members.issues, [])

    def test_new_members_for_given_year(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2027-03-01", 1, ""],
                                 ["Beispiel", "Eva", "1970-01-01", "2021-01-01", 1, ""]])
        members = Members(path, self.config)
        self.assertEqual(members.calculate_new_members(2027), 1)
        self.assertEqual(members.calculate_new_members(2021), 1)

    def test_excel_serial_numbers_and_german_text_dates(self):
        # number cells are excel serial days (28353 = 16.08.1977), text dates are day first (03.02. = 3 February)
        path = self.write_excel([["Muster", "Max", 28353, 36526, 1, ""],
                                 ["Beispiel", "Eva", "03.02.1970", "2021-01-01", 1, ""]])
        members = Members(path, self.config)
        self.assertEqual(members.members[0].birthday, pd.Timestamp("1977-08-16"))
        self.assertEqual(members.members[0].member_since, pd.Timestamp("2000-01-01"))
        self.assertEqual(members.members[1].birthday, pd.Timestamp("1970-02-03"))

    def test_iso_text_dates_are_not_read_day_first(self):
        # "1967-06-01" is 1 June (day first would make it 6 January), "13.02.1970" is 13 February
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2020-03-01", 1, ""],
                                 ["Beispiel", "Eva", "13.02.1970", "2021-12-01", 1, ""]])
        members = Members(path, self.config)
        self.assertEqual([m.birthday for m in members.members], [pd.Timestamp("1967-06-01"), pd.Timestamp("1970-02-13")])
        self.assertEqual(members.members[1].member_since, pd.Timestamp("2021-12-01"))

    def test_unreadable_date_text_is_reported(self):
        path = self.write_excel([["Muster", "Max", "irgendwann", "2020-03-01", 1, ""]])
        members = Members(path, self.config)
        self.assertTrue(pd.isna(members.members[0].birthday))
        self.assertIn("nicht lesbar: irgendwann", members.issues[0].message)

    def test_serial_numbers_in_a_pure_number_column(self):
        # a column with only numbers has an integer dtype (numpy.int64), not python ints
        path = self.write_excel([["Muster", "Max", 28353, 36526, 1, ""], ["Beispiel", "Eva", 29605, 36527, 1, ""]])
        members = Members(path, self.config)
        self.assertEqual([m.birthday for m in members.members], [pd.Timestamp("1977-08-16"), pd.Timestamp("1981-01-19")])

    def test_numbers_in_text_columns_have_no_decimal_point(self):
        path = self.write_excel([["Muster", "Max", "1967-06-01", "2020-03-01", 1, 1711234567.0]])
        self.assertEqual(Members(path, self.config).members[0].mobile_phone, "1711234567")

    def test_no_personal_data_on_console(self):
        path = self.write_excel([["Geheimname", "Max", "1967-06-01", "2020-03-01", 1, ""]])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            Members(path, self.config)
        self.assertNotIn("Geheimname", output.getvalue())


if __name__ == "__main__":
    unittest.main()

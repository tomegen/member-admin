import contextlib
import io
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
from unittest import mock

from config.config import Config, ConfigError, parse_numbers
from logic.birthday_calculation import find_birthdays, is_birthday, write_birthdays_into_ics, \
    write_birthdays_into_txt
from logic.date_utils import shift_years
from logic.export import write_entries_into_xlsx
from logic.honor_calculation import find_honors, is_honor, write_honors_into_ics, write_honors_into_txt
from logic.statistics import Statistics, write_statistics_into_xlsx
from logic.template import write_member_template
from logic.upcoming import find_upcoming
from model.checks import age_on
from model.columns import detect_columns, normalize
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


class CalendarTest(unittest.TestCase):

    def ics(self, writer, members, numbers, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "events.ics")
            writer(members, numbers, JAN_1_2027, DEC_31_2027, path, **kwargs)
            with open(path, "rb") as file:
                return file.read().replace(b"\r\n", b"")

    def test_reminder_is_nine_in_the_morning_n_days_before(self):
        content = self.ics(write_birthdays_into_ics, [make_member("1967-06-01")], [60], reminder_days=7)
        self.assertIn(b"BEGIN:VALARM", content)
        self.assertIn(b"TRIGGER:-P6DT15H", content)   # 7 days before 00:00, plus 9 hours

    def test_no_reminder_by_default(self):
        content = self.ics(write_birthdays_into_ics, [make_member("1967-06-01")], [60])
        self.assertNotIn(b"VALARM", content)

    def test_honors_can_be_exported_as_calendar(self):
        member = make_member("1980-01-01", member_since="2002-05-05")
        content = self.ics(write_honors_into_ics, [member], [25], reminder_days=3)
        self.assertIn(b"SUMMARY:25 Jahre Mitgliedschaft Max M", content)
        self.assertIn(b"DTSTART;VALUE=DATE:20270505", content)

    def test_birthday_and_honor_ids_differ_and_stay_stable(self):
        member = make_member("1967-06-01", member_since="1967-06-01")
        uid = lambda content: [line for line in content.split(b"UID:")[1:]][0][:36]
        birthday = self.ics(write_birthdays_into_ics, [member], [60])
        honor = self.ics(write_honors_into_ics, [member], [60])
        self.assertNotEqual(uid(birthday), uid(honor))
        self.assertEqual(uid(birthday), uid(self.ics(write_birthdays_into_ics, [member], [60], reminder_days=7)))


class MinimalExportTest(unittest.TestCase):

    def member(self):
        member = make_member("1967-06-01", member_since="2002-05-05")
        member.phone_number, member.street = "0123 4567", "Hauptstraße 1"
        return member

    def test_minimal_txt_has_only_name_and_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "birthdays.txt")
            write_birthdays_into_txt([self.member()], [60], JAN_1_2027, DEC_31_2027, path, minimal=True)
            with open(path, encoding="utf-8") as file:
                content = file.read()
        self.assertIn("Max Müßig – 01.06.2027", content)
        for hidden in ("0123", "Hauptstraße", "01.06.1967", "05.05.2002", "Mitglied seit"):
            self.assertNotIn(hidden, content)

    def test_full_txt_still_has_the_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "honors.txt")
            write_honors_into_txt([self.member()], [25], JAN_1_2027, DEC_31_2027, path)
            with open(path, encoding="utf-8") as file:
                content = file.read()
        self.assertIn("0123 4567", content)
        self.assertIn("Hauptstraße 1", content)

    def test_minimal_xlsx_has_only_four_columns(self):
        entries = find_birthdays([self.member()], [60], JAN_1_2027, DEC_31_2027)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "result.xlsx")
            write_entries_into_xlsx(entries, lambda n: str(n) + ". Geburtstag", path, minimal=True)
            table = pd.read_excel(path)
        self.assertEqual(list(table.columns), ["Anlass", "Datum", "Vorname", "Name"])


class UpcomingTest(unittest.TestCase):

    def test_next_30_days_across_the_new_year(self):
        january = make_member("1967-01-10", first_name="Jan")        # 60th on 10.01.2027
        december = make_member("1957-12-24", first_name="Dez", member_since="2001-12-30")  # 70th on 24.12.2027
        far = make_member("1967-03-01", first_name="Fern")
        found = find_upcoming([january, december, far], [60, 70], [25], pd.Timestamp("2026-12-20 15:30"))
        self.assertEqual([(d.strftime("%d.%m.%Y"), o) for d, o, _ in found],
                         [("30.12.2026", "25 Jahre Mitgliedschaft"), ("10.01.2027", "60. Geburtstag")])

    def test_window_includes_today_and_the_last_day(self):
        member = make_member("1967-06-01")
        self.assertEqual(len(find_upcoming([member], [60], [], pd.Timestamp("2027-06-01"))), 1)
        self.assertEqual(len(find_upcoming([member], [60], [], pd.Timestamp("2027-05-02"))), 1)
        self.assertEqual(len(find_upcoming([member], [60], [], pd.Timestamp("2027-05-01"))), 0)


class ColumnsTest(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    def test_headings_are_normalized(self):
        self.assertEqual(normalize(" Mitglied_Seit "), "mitgliedseit")
        self.assertEqual(normalize("Straße"), "strasse")
        self.assertEqual(normalize("Geburtsdatum"), "geburtsdatum")

    def test_usual_headings_are_recognized(self):
        found = detect_columns(["Nachname", "Vorname", "Geburtsdatum", "Eintritt", "Aktiv", "Straße", "Handy", "PLZ"],
                               self.config)
        self.assertEqual(found["last_name"], "Nachname")
        self.assertEqual(found["birthday"], "Geburtsdatum")
        self.assertEqual(found["member_since"], "Eintritt")
        self.assertEqual(found["member"], "Aktiv")
        self.assertEqual(found["street"], "Straße")
        self.assertEqual(found["mobile_phone"], "Handy")
        self.assertIsNone(found["iban"])

    def test_mitglied_and_mitglied_seit_are_not_mixed_up(self):
        found = detect_columns(["Mitglied seit", "Mitglied"], self.config)
        self.assertEqual((found["member_since"], found["member"]), ("Mitglied seit", "Mitglied"))

    def test_name_from_config_ini_wins(self):
        self.config.birthdays_config = "Geburtsjahr-Tag"
        found = detect_columns(["Geburtsdatum", "Geburtsjahr-Tag"], self.config)
        self.assertEqual(found["birthday"], "Geburtsjahr-Tag")

    def test_a_column_is_used_for_one_field_only(self):
        found = detect_columns(["Name", "Vorname"], self.config)
        self.assertEqual((found["last_name"], found["first_name"]), ("Name", "Vorname"))


class SettingsTest(unittest.TestCase):

    def test_parse_numbers(self):
        self.assertEqual(parse_numbers("60, 18 20;18"), [18, 20, 60])
        for text in ("", "abc", "0", "200", "18, x"):
            with self.assertRaises(ValueError):
                parse_numbers(text)

    def test_app_works_without_config_ini(self):
        with mock.patch.object(Config, "config_path", return_value=None):
            config = Config()
        self.assertIn(60, config.birthday_config)
        self.assertEqual(config.member_since_config, "Mitglied seit")

    def test_old_config_ini_without_all_keys_still_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "config.ini")
            with open(path, "w", encoding="utf-8") as file:
                file.write("[birthday]\npossibilities = 18,60\n")
            config = Config(path=path)
        self.assertEqual(config.birthday_config, [18, 60])
        self.assertEqual(config.member_config, "Mitglied")


class DataCheckTest(unittest.TestCase):
    TODAY = pd.Timestamp("2026-11-14")

    def setUp(self):
        self.config = Config()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def issues(self, rows, columns=("Name", "Vorname", "Geburtstag", "Mitglied seit", "Mitglied", "Mobil")):
        path = os.path.join(self.tmp.name, "members.xlsx")
        pd.DataFrame(rows, columns=list(columns)).to_excel(path, index=False)
        return Members(path, self.config, today=self.TODAY).issues

    def test_same_name_and_birthday_is_a_possible_duplicate(self):
        found = self.issues([["Muster", "Max", "1967-06-01", "2000-01-01", 1, ""],
                             ["Muster", "Max", "1967-06-01", "2001-01-01", 1, ""],
                             ["Muster", "Max", "1995-03-03", "2015-01-01", 1, ""]])   # same name only: family
        self.assertEqual([(i.row, "Zeile 2" in i.message) for i in found], [(3, True)])

    def test_entry_before_birth_and_far_in_the_future(self):
        found = self.issues([["Muster", "Max", "1967-06-01", "1960-01-01", 1, ""],
                             ["Beispiel", "Eva", "1970-01-01", "2062-01-01", 1, ""]])
        self.assertEqual([(i.row, i.message.split(" ")[0:3]) for i in found],
                         [(2, ["Mitglied", "seit", "liegt"]), (3, ["Mitglied", "seit", "liegt"])])
        self.assertIn("vor dem Geburtstag", found[0].message)
        self.assertIn("Zukunft", found[1].message)

    def test_implausible_age(self):
        found = self.issues([["Alt", "Karl", "1850-01-01", "2000-01-01", 1, ""],
                             ["Jung", "Eva", "2030-01-01", "2031-01-01", 1, ""],
                             ["Normal", "Max", "1960-01-01", "2000-01-01", 1, ""]])
        self.assertEqual(sorted({i.row for i in found}), [2, 3])
        self.assertTrue(any("Alter von 176" in i.message for i in found))

    def test_clean_list_has_no_findings(self):
        self.assertEqual(self.issues([["Muster", "Max", "1967-06-01", "2000-01-01", 1, ""]]), [])

    def test_unusual_headings_are_found_without_config(self):
        path = os.path.join(self.tmp.name, "other.xlsx")
        pd.DataFrame([["Muster", "Max", "1967-06-01", "2000-01-01", 1]],
                     columns=["Nachname", "Vorname", "Geburtsdatum", "Eintritt", "Aktiv"]).to_excel(path, index=False)
        members = Members(path, self.config)
        self.assertEqual(members.members[0].birthday, pd.Timestamp("1967-06-01"))
        self.assertEqual(members.members[0].member_since, pd.Timestamp("2000-01-01"))

    def test_missing_column_error_lists_the_found_headings(self):
        path = os.path.join(self.tmp.name, "wrong.xlsx")
        pd.DataFrame([["Muster", "Max", 1]], columns=["Nachname", "Vorname", "Aktiv"]).to_excel(path, index=False)
        with self.assertRaises(MemberListError) as error:
            Members(path, self.config)
        message = str(error.exception)
        self.assertIn("Geburtstag, Mitglied seit", message)
        self.assertIn("Nachname, Vorname, Aktiv", message)


class StatisticsTest(unittest.TestCase):
    STICHTAG = pd.Timestamp("2027-12-31")

    def test_age_counts_full_years_and_the_leap_day_rule(self):
        self.assertEqual(age_on(pd.Timestamp("1967-06-01"), pd.Timestamp("2027-05-31")), 59)
        self.assertEqual(age_on(pd.Timestamp("1967-06-01"), pd.Timestamp("2027-06-01")), 60)
        self.assertEqual(age_on(pd.Timestamp("1952-02-29"), pd.Timestamp("2027-02-28")), 75)
        self.assertEqual(age_on(pd.Timestamp("1952-02-29"), pd.Timestamp("2027-02-27")), 74)

    def test_age_groups_and_figures_of_active_members(self):
        members = [make_member("2015-05-05", member_since="2027-01-01"),     # 12, new in 2027
                   make_member("2000-01-01"),                                  # 27
                   make_member("1960-01-01"),                                  # 67
                   make_member("1990-01-01", member=0)]                        # not counted
        unknown = make_member("1990-01-01")
        unknown.birthday = pd.NaT
        stats = Statistics(members + [unknown], 2027, self.STICHTAG)
        self.assertEqual((stats.active, stats.new_members, stats.unknown_birthday), (4, 1, 1))
        self.assertEqual(dict(stats.groups)["7 bis 14 Jahre"], 1)
        self.assertEqual(dict(stats.groups)["27 bis 40 Jahre"], 1)
        self.assertEqual(dict(stats.groups)["über 60 Jahre"], 1)
        self.assertAlmostEqual(stats.average_age, (12 + 27 + 67) / 3)

    def test_statistics_without_members_do_not_crash_and_export(self):
        stats = Statistics([], 2027, self.STICHTAG)
        self.assertIsNone(stats.average_age)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "stats.xlsx")
            write_statistics_into_xlsx(stats, path)
            self.assertEqual(list(pd.read_excel(path, sheet_name=None)), ["Kennzahlen", "Altersgruppen"])


class TemplateTest(unittest.TestCase):

    def test_template_is_readable_with_dropdown_and_date_checks(self):
        from openpyxl import load_workbook
        config = Config()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "template.xlsx")
            write_member_template(path, config)
            members = Members(path, config)                         # no members, no problems, all columns found
            sheet = load_workbook(path)["Mitglieder"]
            self.assertEqual((len(members.members), len(members.issues)), (0, 0))
            self.assertEqual(len(sheet.data_validations.dataValidation), 2)
            self.assertEqual(sheet["C2"].number_format, "DD.MM.YYYY")
            self.assertEqual([cell.value for cell in sheet[1]][:5],
                             [config.last_name_config, config.first_name_config, config.birthdays_config,
                              config.member_since_config, config.member_config])


if __name__ == "__main__":
    unittest.main()

import getpass
import os

import pandas as pd
from PySide6.QtCore import QFileSystemWatcher, QSettings, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QInputDialog, QLabel, QMainWindow, QMessageBox,
                               QSpinBox, QStackedWidget, QTabWidget, QVBoxLayout, QWidget)

from config.config import parse_numbers
from logic.birthday_calculation import find_birthdays, write_birthdays_into_ics, write_birthdays_into_txt
from logic.honor_calculation import find_honors, write_honors_into_ics, write_honors_into_txt
from logic.template import write_member_template
from logic.upcoming import birthday_occasion, honor_occasion
from importer.reader import SourceError
from model.club_file import file_hash, is_standard_file, read_bytes
from model.members import MemberListError, Members
from model.schema import BIRTHDAY, HONOR
from store.changes import update_settings
from store.conflict_copies import conflict_copies
from store.errors import Conflict, Duplicate, FileLocked, SaveError
from store.transaction import save
from ui.club_settings_dialog import ClubSettingsDialog
from ui.import_wizard import ImportWizard
from ui.issues_page import IssuesPage
from ui.member_actions import MemberActions
from ui.members_page import MembersPage
from ui.overview_page import OverviewPage
from ui.result_page import ResultPage, ResultSpec
from ui.saving import save_file
from ui.statistics_page import StatisticsPage
from ui.theme import secondary_button
from ui.welcome_page import WelcomePage

TAB_OVERVIEW, TAB_MEMBERS, TAB_BIRTHDAYS, TAB_HONORS, TAB_STATISTICS, TAB_ISSUES = range(6)


# the evaluation is usually done for the coming year in the last months of a year
def default_year():
    today = pd.Timestamp.now()
    return today.year + 1 if today.month >= 10 else today.year


class MainWindow(QMainWindow):

    def __init__(self, config):
        super().__init__()
        self.config = config
        # the numbers from config.ini are the defaults; what was chosen in the settings wins
        self.default_birthdays = list(config.birthday_config)
        self.default_honors = list(config.honor_config)
        self.apply_saved_numbers()
        self.members = None
        self.filename = None
        self.loaded_hash = None
        self.actions = MemberActions(self)
        # the file is watched: changes from excel or the sync service are read in again automatically
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.on_file_changed)
        self.change_timer = QTimer(self)
        self.change_timer.setSingleShot(True)
        self.change_timer.setInterval(1500)   # sync services and excel write in several steps
        self.change_timer.timeout.connect(self.reload_if_changed)
        self.setWindowTitle("Mitglieder Management Portal")
        self.resize(1000, 780)
        self.setAcceptDrops(True)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome = WelcomePage()
        self.welcome.open_requested.connect(self.choose_file)
        self.welcome.recent_requested.connect(self.load_file)
        self.welcome.template_requested.connect(self.save_template)
        self.welcome.import_requested.connect(lambda: self.start_import())
        self.welcome.set_recent(QSettings().value("last_file"))
        self.stack.addWidget(self.welcome)

        self.view = self.build_view()
        self.stack.addWidget(self.view)

    def build_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # header: file, year, actions
        header = QHBoxLayout()
        header.setContentsMargins(30, 14, 30, 6)
        self.file_label = QLabel()
        font = self.file_label.font()
        font.setBold(True)
        self.file_label.setFont(font)
        header.addWidget(self.file_label)
        header.addStretch()
        header.addWidget(QLabel("Auswertungsjahr:"))
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1990, 2100)
        self.year_spin.setValue(default_year())
        self.year_spin.setToolTip("Für dieses Jahr werden Geburtstage, Ehrungen und neue Mitglieder berechnet.")
        self.year_spin.valueChanged.connect(self.on_year_changed)
        header.addWidget(self.year_spin)
        reload_button = secondary_button("Neu einlesen")
        reload_button.setToolTip("Die Excel-Datei erneut einlesen, z. B. nach einer Korrektur.")
        reload_button.clicked.connect(self.reload)
        other_button = secondary_button("Andere Datei …")
        other_button.clicked.connect(self.choose_file)
        settings_button = secondary_button("Einstellungen")
        settings_button.clicked.connect(self.open_settings)
        header.addWidget(reload_button)
        header.addWidget(other_button)
        header.addWidget(settings_button)
        layout.addLayout(header)

        self.overview = OverviewPage()
        self.overview.open_tab.connect(lambda name: self.tabs.setCurrentWidget(getattr(self, name)))
        self.members_page = MembersPage()
        self.members_page.new_requested.connect(self.actions.new_member)
        self.members_page.edit_requested.connect(self.actions.edit_member)
        self.members_page.exit_requested.connect(self.actions.record_exit)
        self.members_page.numbers_requested.connect(self.actions.assign_numbers)
        self.members_page.merge_requested.connect(lambda: self.actions.merge_list())
        self.members_page.delete_requested.connect(self.actions.delete_member)
        self.members_page.due_requested.connect(self.actions.delete_due)
        self.members_page.copies_requested.connect(lambda: self.actions.check_conflict_copies())
        self.asked_copies = set()   # conflict copies are offered once per start of the app
        self.birthdays = ResultPage(ResultSpec(
            title="Geburtstage",
            description="Runde Geburtstage im gewählten Zeitraum. Welche Geburtstage zur Auswahl stehen, "
                        "ändern Sie unter „Einstellungen“.",
            numbers=self.config.birthday_config,
            checkbox_text=birthday_occasion,
            occasion=birthday_occasion,
            file_stem="Geburtstage",
            finder=find_birthdays,
            txt_writer=write_birthdays_into_txt,
            ics_writer=write_birthdays_into_ics,
            purpose="birthdays"))
        self.honors = ResultPage(ResultSpec(
            title="Ehrungen",
            description="Mitglieder mit rundem Jubiläum im gewählten Zeitraum. Welche Jahre zur Auswahl "
                        "stehen, ändern Sie unter „Einstellungen“.",
            numbers=self.config.honor_config,
            checkbox_text=lambda n: str(n) + " Jahre",
            occasion=honor_occasion,
            file_stem="Ehrungen",
            finder=find_honors,
            txt_writer=write_honors_into_txt,
            ics_writer=write_honors_into_ics,
            purpose="honors"))
        self.statistics_page = StatisticsPage()
        self.issues = IssuesPage()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.overview, "Übersicht")
        self.tabs.addTab(self.members_page, "Mitglieder")
        self.tabs.addTab(self.birthdays, "Geburtstage")
        self.tabs.addTab(self.honors, "Ehrungen")
        self.tabs.addTab(self.statistics_page, "Statistik")
        self.tabs.addTab(self.issues, "Datenprüfung")
        layout.addWidget(self.tabs)

        # the pages start with the year shown in the header
        self.birthdays.set_year(self.year_spin.value())
        self.honors.set_year(self.year_spin.value())
        self.statistics_page.set_year(self.year_spin.value())
        return view

    # --- loading -----------------------------------------------------------------------------------------------

    def choose_file(self):
        settings = QSettings()
        last_file = settings.value("last_file")
        folder = os.path.dirname(last_file) if last_file else QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation)
        path, _ = QFileDialog.getOpenFileName(self, "Mitgliederliste auswählen", folder,
                                              "Mitgliederlisten (*.xlsx *.xls *.csv)")
        if path:
            self.load_file(path)

    def inform(self, title, text):
        QMessageBox.information(self, title, text)

    # a list in another format becomes a new standard file (import assistant), which is opened then;
    # without path the user chooses the list
    def start_import(self, path=None):
        if path is None:
            folder = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            path, _ = QFileDialog.getOpenFileName(self, "Liste zum Übernehmen auswählen", folder,
                                                  "Listen (*.xlsx *.xls *.csv)")
            if not path:
                return False
        try:
            wizard = ImportWizard(path, self.config, QSettings().value("editor_name") or getpass.getuser(), self)
        except SourceError as error:
            self.show_error("Liste konnte nicht gelesen werden", str(error))
            return False
        if not wizard.exec():
            return False
        self.inform("Übernommen", str(wizard.imported) + " Mitglieder wurden in die neue Mitgliederliste übernommen:\n"
                    + wizard.result_path + "\n\nIhre bisherige Liste ist unverändert. Ab jetzt arbeiten Sie mit der "
                    "neuen Datei.")
        return self.load_file(wizard.result_path)

    def show_error(self, title, text):
        QMessageBox.critical(self, title, text)

    def reload(self):
        if self.filename:
            self.load_file(self.filename)

    # a file in the standard format is opened; any other list goes to the import assistant first
    def load_file(self, path):
        if not is_standard_file(path):
            return self.start_import(path)
        QGuiApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            loaded_hash = file_hash(read_bytes(path))
            members = Members(path)
        except OSError as error:
            QGuiApplication.restoreOverrideCursor()
            self.show_error("Mitgliederliste konnte nicht geöffnet werden", str(error))
            return False
        except MemberListError as error:
            QGuiApplication.restoreOverrideCursor()
            self.show_error("Mitgliederliste konnte nicht geöffnet werden", str(error))
            return False
        QGuiApplication.restoreOverrideCursor()

        self.members = members
        self.filename = path
        self.loaded_hash = loaded_hash
        self.watch(path)
        QSettings().setValue("last_file", path)
        club = members.settings.club_name
        self.file_label.setText((club + " – " if club else "") + os.path.basename(path))
        self.setWindowTitle("Mitglieder Management Portal – " + os.path.basename(path))
        self.apply_club_settings(members)
        self.members_page.set_members(members)
        self.birthdays.set_members(members)
        self.honors.set_members(members)
        self.statistics_page.set_members(members)
        self.issues.set_members(members)
        self.refresh_overview()
        self.update_issue_tab()
        self.stack.setCurrentWidget(self.view)
        if self.update_conflict_copies() - self.asked_copies:
            QTimer.singleShot(0, self.offer_conflict_copies)   # after loading, not inside a running save
        return True

    # conflict copies of the open file (store.conflict_copies); shown on the members tab
    def update_conflict_copies(self):
        copies = set(conflict_copies(self.filename, self.members.file_id)) if self.members is not None else set()
        self.members_page.set_conflict_copies(len(copies))
        return copies

    def offer_conflict_copies(self):
        if QApplication.activeModalWidget() is not None:
            return
        copies = self.update_conflict_copies()
        if copies - self.asked_copies:
            self.asked_copies |= copies
            self.actions.check_conflict_copies(ask=True)

    def update_issue_tab(self):
        active_issues = sum(1 for issue in self.members.issues if issue.active)
        title = "Datenprüfung (" + str(active_issues) + ")" if active_issues else "Datenprüfung ✓"
        self.tabs.setTabText(TAB_ISSUES, title)

    def on_year_changed(self, year):
        self.birthdays.set_year(year)
        self.honors.set_year(year)
        self.statistics_page.set_year(year)
        self.refresh_overview()

    def refresh_overview(self):
        if self.members is not None:
            self.overview.refresh(self.members, self.year_spin.value(), self.birthdays.spec.numbers,
                                  self.honors.spec.numbers)

    # the file brings the settings of its club (numbers, gifts, reminder)
    def apply_club_settings(self, members):
        settings = members.settings
        self.birthdays.set_numbers(settings.numbers(BIRTHDAY, self.default_birthdays))
        self.honors.set_numbers(settings.numbers(HONOR, self.default_honors))
        self.birthdays.set_reminder(settings.reminder_days)
        self.honors.set_reminder(settings.reminder_days)
        self.birthdays.set_gifts(settings.gifts(BIRTHDAY))
        self.honors.set_gifts(settings.gifts(HONOR))

    # --- saving into the standard file ---------------------------------------------------------------------------

    # name for the change log, asked once on this computer; None if the user cancels
    def editor_name(self):
        name = QSettings().value("editor_name")
        if not name:
            name = self.ask_editor_name(getpass.getuser())
            if name:
                QSettings().setValue("editor_name", name)
        return name or None

    def ask_editor_name(self, suggestion):
        name, ok = QInputDialog.getText(self, "Ihr Name", "Ihr Name für das Änderungsprotokoll der Mitgliederliste "
                                        "(wird nur auf diesem Computer gespeichert):", text=suggestion)
        return name.strip() if ok else None

    def ask(self, title, text):
        return QMessageBox.question(self, title, text) == QMessageBox.StandardButton.Yes

    # saves a change (store.changes) into the open standard file and reads it again; False if nothing was saved.
    # retry(error) may answer a Conflict or Duplicate with a new change (after asking the user) or None
    def save_change(self, change, retry=None):
        editor = self.editor_name()
        if editor is None:
            return False
        ignore_lock = False
        while True:
            try:
                save(self.filename, change, editor, ignore_lock=ignore_lock)
                break
            except FileLocked as error:
                if ignore_lock or error.owner is None:   # windows keeps the file locked: no way to save anyway
                    self.show_error("Speichern nicht möglich", str(error))
                    return False
                if not self.ask("Datei ist geöffnet", str(error) + "\n\nWenn die Datei sicher nirgends mehr geöffnet "
                                "ist (z. B. nach einem Absturz von Excel), können Sie trotzdem speichern. Wird sie doch "
                                "noch in Excel bearbeitet, überschreibt das spätere Speichern in Excel Ihre Änderung."
                                "\n\nTrotzdem speichern?"):
                    return False
                ignore_lock = True
            except (Conflict, Duplicate) as error:
                change = retry(error) if retry is not None else None
                if change is None:
                    if retry is None:
                        self.show_error("Speichern nicht möglich", str(error))
                    return False
            except (SaveError, OSError) as error:
                self.show_error("Speichern nicht möglich", str(error))
                return False
        self.load_file(self.filename)
        return True

    # --- watching the file ---------------------------------------------------------------------------------------

    def watch(self, path):
        if self.watcher.files():
            self.watcher.removePaths(self.watcher.files())
        self.watcher.addPath(path)

    def on_file_changed(self, path):
        # a file that is replaced (excel, sync services, the app itself) is no longer watched: watch it again
        if path not in self.watcher.files() and os.path.exists(path):
            self.watcher.addPath(path)
        self.change_timer.start()

    # read the file again if its content changed (not after an own save, which reads it anyway); not while a
    # dialog is open, then a little later
    def reload_if_changed(self):
        if not self.filename or not os.path.exists(self.filename):
            return
        if QApplication.activeModalWidget() is not None:
            self.change_timer.start()
            return
        try:
            changed = file_hash(read_bytes(self.filename)) != self.loaded_hash
        except OSError:   # being written right now
            self.change_timer.start()
            return
        if changed and self.load_file(self.filename):
            self.statusBar().showMessage("Die Mitgliederliste wurde außerhalb der App geändert und neu eingelesen.",
                                         10000)

    # --- settings and template ---------------------------------------------------------------------------------

    # numbers chosen in the settings of version 0.1 on this computer: they go into the settings sheet of the files
    # that are created or imported here (write_member_template uses the config)
    def apply_saved_numbers(self):
        settings = QSettings()
        for key, attribute in (("birthday_numbers", "birthday_config"), ("honor_numbers", "honor_config")):
            text = settings.value(key)
            if text:
                try:
                    setattr(self.config, attribute, parse_numbers(text))
                except ValueError:
                    settings.remove(key)

    # the settings of the club are saved in the member file itself
    def open_settings(self):
        dialog = ClubSettingsDialog(self.members.settings, self.default_birthdays, self.default_honors,
                                    QSettings().value("editor_name") or getpass.getuser(), self)
        if not dialog.exec():
            return
        QSettings().setValue("editor_name", dialog.editor_name)
        if dialog.settings.areas() != self.members.settings.areas():
            self.save_change(update_settings(self.members.settings, dialog.settings))

    def save_template(self):
        save_file(self, "Mitgliederliste_Vorlage.xlsx", "Excel-Datei (*.xlsx)",
                  lambda path: write_member_template(path, self.config))

    # --- drag and drop of an excel file -------------------------------------------------------------------------

    @staticmethod
    def dropped_excel_path(event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith((".xlsx", ".xls", ".csv")):
                return path
        return None

    def dragEnterEvent(self, event):
        if self.dropped_excel_path(event):
            event.acceptProposedAction()

    def dropEvent(self, event):
        path = self.dropped_excel_path(event)
        if path:
            self.load_file(path)

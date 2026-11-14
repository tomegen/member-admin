import os

import pandas as pd
from PySide6.QtCore import QSettings, QStandardPaths, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QSpinBox,
                               QStackedWidget, QTabWidget, QVBoxLayout, QWidget)

from logic.birthday_calculation import find_birthdays, write_birthdays_into_ics, write_birthdays_into_txt
from logic.honor_calculation import find_honors, write_honors_into_txt
from model.members import MemberListError, Members
from ui.issues_page import IssuesPage
from ui.overview_page import OverviewPage
from ui.result_page import ResultPage, ResultSpec
from ui.theme import secondary_button
from ui.welcome_page import WelcomePage

TAB_OVERVIEW, TAB_BIRTHDAYS, TAB_HONORS, TAB_ISSUES = range(4)


# the evaluation is usually done for the coming year in the last months of a year
def default_year():
    today = pd.Timestamp.now()
    return today.year + 1 if today.month >= 10 else today.year


class MainWindow(QMainWindow):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.members = None
        self.filename = None
        self.setWindowTitle("Mitglieder Management Portal")
        self.resize(1000, 780)
        self.setAcceptDrops(True)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome = WelcomePage()
        self.welcome.open_requested.connect(self.choose_file)
        self.welcome.recent_requested.connect(self.load_file)
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
        header.addWidget(reload_button)
        header.addWidget(other_button)
        layout.addLayout(header)

        self.overview = OverviewPage()
        self.overview.open_tab.connect(lambda index: self.tabs.setCurrentIndex(index))
        self.birthdays = ResultPage(ResultSpec(
            title="Geburtstage",
            description="Runde Geburtstage im gewählten Zeitraum. Die Auswahl der Geburtstage steht in der config.ini.",
            numbers=self.config.birthday_config,
            checkbox_text=lambda n: str(n) + ". Geburtstag",
            occasion=lambda n: str(n) + ". Geburtstag",
            file_stem="Geburtstage",
            finder=find_birthdays,
            txt_writer=write_birthdays_into_txt,
            ics_writer=write_birthdays_into_ics))
        self.honors = ResultPage(ResultSpec(
            title="Ehrungen",
            description="Mitglieder mit rundem Jubiläum im gewählten Zeitraum. Die Auswahl der Jahre steht in der config.ini.",
            numbers=self.config.honor_config,
            checkbox_text=lambda n: str(n) + " Jahre",
            occasion=lambda n: str(n) + " Jahre Mitgliedschaft",
            file_stem="Ehrungen",
            finder=find_honors,
            txt_writer=write_honors_into_txt))
        self.issues = IssuesPage()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.overview, "Übersicht")
        self.tabs.addTab(self.birthdays, "Geburtstage")
        self.tabs.addTab(self.honors, "Ehrungen")
        self.tabs.addTab(self.issues, "Datenprüfung")
        layout.addWidget(self.tabs)

        # the pages start with the year shown in the header
        self.birthdays.set_year(self.year_spin.value())
        self.honors.set_year(self.year_spin.value())
        return view

    # --- loading -----------------------------------------------------------------------------------------------

    def choose_file(self):
        settings = QSettings()
        last_file = settings.value("last_file")
        folder = os.path.dirname(last_file) if last_file else QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation)
        path, _ = QFileDialog.getOpenFileName(self, "Mitgliederliste auswählen", folder,
                                              "Excel-Dateien (*.xlsx *.xls)")
        if path:
            self.load_file(path)

    def show_error(self, title, text):
        QMessageBox.critical(self, title, text)

    def reload(self):
        if self.filename:
            self.load_file(self.filename)

    def load_file(self, path):
        QGuiApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            members = Members(path, self.config)
        except MemberListError as error:
            QGuiApplication.restoreOverrideCursor()
            self.show_error("Mitgliederliste konnte nicht geöffnet werden", str(error))
            return False
        QGuiApplication.restoreOverrideCursor()

        self.members = members
        self.filename = path
        QSettings().setValue("last_file", path)
        self.file_label.setText(os.path.basename(path))
        self.setWindowTitle("Mitglieder Management Portal – " + os.path.basename(path))
        self.birthdays.set_members(members)
        self.honors.set_members(members)
        self.issues.set_members(members)
        self.overview.refresh(members, self.year_spin.value())
        self.update_issue_tab()
        self.stack.setCurrentWidget(self.view)
        return True

    def update_issue_tab(self):
        active_issues = sum(1 for issue in self.members.issues if issue.active)
        title = "Datenprüfung (" + str(active_issues) + ")" if active_issues else "Datenprüfung ✓"
        self.tabs.setTabText(TAB_ISSUES, title)

    def on_year_changed(self, year):
        self.birthdays.set_year(year)
        self.honors.set_year(year)
        if self.members is not None:
            self.overview.refresh(self.members, year)

    # --- drag and drop of an excel file -------------------------------------------------------------------------

    @staticmethod
    def dropped_excel_path(event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith((".xlsx", ".xls")):
                return path
        return None

    def dragEnterEvent(self, event):
        if self.dropped_excel_path(event):
            event.acceptProposedAction()

    def dropEvent(self, event):
        path = self.dropped_excel_path(event)
        if path:
            self.load_file(path)

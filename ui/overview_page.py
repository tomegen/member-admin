import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from logic.upcoming import find_upcoming
from ui.theme import heading, muted, primary_button

UPCOMING_DAYS = 30


def make_card(title):
    card = QFrame()
    card.setObjectName("card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 16, 20, 16)
    value = QLabel("–")
    value.setObjectName("cardValue")
    layout.addWidget(value)
    layout.addWidget(QLabel(title))
    note = muted("")
    layout.addWidget(note)
    return card, value, note


class OverviewPage(QWidget):
    open_tab = Signal(str)   # name of the page in the main window

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(16)
        layout.addWidget(heading("Übersicht"))

        grid = QGridLayout()
        grid.setSpacing(16)
        self.active_card = make_card("Mitglieder")
        self.new_card = make_card("Neue Mitglieder")
        self.inactive_card = make_card("Nicht gezählt")
        self.issues_card = make_card("Hinweise zur Mitgliederliste")
        grid.addWidget(self.active_card[0], 0, 0)
        grid.addWidget(self.new_card[0], 0, 1)
        grid.addWidget(self.inactive_card[0], 1, 0)
        grid.addWidget(self.issues_card[0], 1, 1)
        layout.addLayout(grid)
        self.deletion_label = QLabel()   # left members whose deletion period is over
        self.deletion_label.setStyleSheet("color: #b45309;")
        self.deletion_label.setWordWrap(True)
        layout.addWidget(self.deletion_label)

        # what is coming up in the next days (independent of the evaluation year)
        layout.addWidget(heading("Demnächst (nächste " + str(UPCOMING_DAYS) + " Tage)", 16))
        self.upcoming_label = muted("")
        layout.addWidget(self.upcoming_label)
        self.upcoming_table = QTableWidget(0, 3)
        self.upcoming_table.setHorizontalHeaderLabels(["Datum", "Anlass", "Name"])
        self.upcoming_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.upcoming_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.upcoming_table.setAlternatingRowColors(True)
        self.upcoming_table.verticalHeader().setVisible(False)
        self.upcoming_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.upcoming_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.upcoming_table, stretch=1)

        buttons = QHBoxLayout()
        for text, page in (("Geburtstage berechnen", "birthdays"), ("Ehrungen berechnen", "honors"),
                           ("Statistik anzeigen", "statistics_page")):
            button = primary_button(text)
            button.clicked.connect(lambda checked=False, name=page: self.open_tab.emit(name))
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)

    def refresh(self, members, year, birthdays=(), honors=(), today=None):
        active_issues = sum(1 for issue in members.issues if issue.active)
        self.active_card[1].setText(str(members.calculate_members()))
        self.new_card[1].setText(str(members.calculate_new_members(year)))
        self.new_card[2].setText("mit Eintritt im Jahr " + str(year))
        self.inactive_card[1].setText(str(members.calculate_inactive()))
        self.active_card[2].setText("aktiv und passiv")
        self.inactive_card[2].setText("ausgetreten oder ohne gültigen Status – zählen nicht für Geburtstage und "
                                      "Ehrungen")
        self.issues_card[1].setText(str(len(members.issues)))
        if active_issues:
            self.issues_card[2].setText(str(active_issues) + " davon bei Mitgliedern – siehe Tab „Datenprüfung“")
        else:
            self.issues_card[2].setText("Keine Auffälligkeiten bei Mitgliedern")

        due = len(members.deletion_due())
        self.deletion_label.setText(("1 ausgetretenes Mitglied kann" if due == 1 else str(due) + " ausgetretene "
                                     "Mitglieder können") + " laut Löschfrist endgültig gelöscht werden – Tab "
                                    "„Mitglieder“, Knopf „Löschfrist …“.")
        self.deletion_label.setVisible(bool(due))

        today = pd.Timestamp.now() if today is None else pd.Timestamp(today)
        rows = find_upcoming(members.counted("birthdays"), members.counted("honors"), birthdays, honors, today,
                             UPCOMING_DAYS)
        self.upcoming_table.setRowCount(len(rows))
        for row, (date, occasion, name) in enumerate(rows):
            for column, text in enumerate((date.strftime("%d.%m.%Y"), occasion, name)):
                self.upcoming_table.setItem(row, column, QTableWidgetItem(text))
        self.upcoming_label.setText(str(len(rows)) + " Termine" if rows else
                                    "In den nächsten " + str(UPCOMING_DAYS) + " Tagen steht nichts an.")

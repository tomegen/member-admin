import pandas as pd
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (QAbstractItemView, QDateEdit, QHBoxLayout, QHeaderView, QLabel, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from logic.statistics import Statistics, write_statistics_into_xlsx
from ui.saving import save_file
from ui.theme import heading, muted, primary_button


def german_number(value):
    if value is None:
        return "–"
    return str(value) if isinstance(value, int) else "{:.1f}".format(value).replace(".", ",")


def make_table(columns):
    table = QTableWidget(0, len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    table.horizontalHeader().setStretchLastSection(True)
    return table


# numbers for the general meeting or the report to the association (active members only)
class StatisticsPage(QWidget):

    def __init__(self):
        super().__init__()
        self.members = None
        self.year = pd.Timestamp.now().year
        self.statistics = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(12)
        layout.addWidget(heading("Statistik"))
        layout.addWidget(muted("Zahlen zu den aktiven Mitgliedern, z. B. für die Mitgliederversammlung oder die "
                               "Meldung an den Verband. Austritte lassen sich nicht auswerten, weil die Liste "
                               "kein Austrittsdatum enthält."))

        row = QHBoxLayout()
        row.addWidget(QLabel("Stichtag für das Alter:"))
        self.stichtag_edit = QDateEdit()
        self.stichtag_edit.setCalendarPopup(True)
        self.stichtag_edit.setDisplayFormat("dd.MM.yyyy")
        self.stichtag_edit.dateChanged.connect(self.refresh)
        row.addWidget(self.stichtag_edit)
        row.addStretch()
        layout.addLayout(row)

        tables = QHBoxLayout()
        self.figures_table = make_table(["Kennzahl", "Wert"])
        self.groups_table = make_table(["Altersgruppe", "Anzahl", "Anteil"])
        tables.addWidget(self.figures_table)
        tables.addWidget(self.groups_table)
        layout.addLayout(tables, stretch=1)

        self.note_label = muted("")
        layout.addWidget(self.note_label)
        self.xlsx_button = primary_button("Als Excel-Datei speichern")
        self.xlsx_button.clicked.connect(self.save)
        layout.addWidget(self.xlsx_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.set_year(self.year)

    def set_members(self, members):
        self.members = members
        self.refresh()

    # the age is counted on the last day of the evaluation year (can be changed)
    def set_year(self, year):
        self.year = year
        self.stichtag_edit.setDate(QDate(year, 12, 31))  # triggers refresh

    def stichtag(self):
        date = self.stichtag_edit.date()
        return pd.Timestamp(date.year(), date.month(), date.day())

    def refresh(self):
        if self.members is None:
            return
        self.statistics = Statistics(self.members.members, self.year, self.stichtag())
        rows = self.statistics.rows()
        self.figures_table.setRowCount(len(rows))
        for index, (name, value) in enumerate(rows):
            self.figures_table.setItem(index, 0, QTableWidgetItem(name))
            item = QTableWidgetItem(german_number(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.figures_table.setItem(index, 1, item)

        total = max(sum(count for _, count in self.statistics.groups), 1)
        self.groups_table.setRowCount(len(self.statistics.groups))
        for index, (label, count) in enumerate(self.statistics.groups):
            self.groups_table.setItem(index, 0, QTableWidgetItem(label))
            for column, text in ((1, str(count)), (2, german_number(count / total * 100) + " %")):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.groups_table.setItem(index, column, item)

        left_out = self.statistics.unknown_birthday + self.statistics.outside_groups
        self.note_label.setText(str(left_out) + " aktive Mitglieder sind in den Altersgruppen nicht enthalten "
                                "(Geburtstag fehlt oder unplausibel, siehe Datenprüfung)." if left_out else "")

    def save(self):
        if self.statistics is not None:
            save_file(self, "Statistik_" + str(self.year) + ".xlsx", "Excel-Datei (*.xlsx)",
                      lambda path: write_statistics_into_xlsx(self.statistics, path))

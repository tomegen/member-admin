from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QHeaderView, QLabel, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from ui.theme import heading, muted


# numbers sort as numbers (row 9 before row 10)
class NumberItem(QTableWidgetItem):

    def __lt__(self, other):
        return int(self.text()) < int(other.text())


class IssuesPage(QWidget):
    COLUMNS = ["Excel-Zeile", "Name", "Status", "Hinweis"]

    def __init__(self):
        super().__init__()
        self.members = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(12)
        layout.addWidget(heading("Datenprüfung"))
        layout.addWidget(muted("Diese Einträge in Ihrer Mitgliederliste sind unvollständig oder auffällig. "
                               "Fehlende Angaben führen dazu, dass Personen in den Auswertungen fehlen. Bitte in "
                               "Excel korrigieren, speichern und oben auf „Neu einlesen“ klicken."))

        self.only_active = QCheckBox("Nur Mitglieder anzeigen (ohne Ausgetretene)")
        self.only_active.setChecked(True)
        self.only_active.toggled.connect(self.refresh)
        layout.addWidget(self.only_active)

        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, stretch=1)

    def set_members(self, members):
        self.members = members
        self.refresh()

    def shown_issues(self):
        if self.members is None:
            return []
        return [issue for issue in self.members.issues if issue.active or not self.only_active.isChecked()]

    def refresh(self):
        issues = self.shown_issues()
        if not issues:
            self.summary_label.setText("✓ Keine Auffälligkeiten – die Liste ist vollständig.")
        else:
            self.summary_label.setText(str(len(issues)) + " Hinweise")

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(issues))
        for row, issue in enumerate(issues):
            self.table.setItem(row, 0, NumberItem(str(issue.row)))
            self.table.setItem(row, 1, QTableWidgetItem(issue.name))
            self.table.setItem(row, 2, QTableWidgetItem("Mitglied" if issue.active else "nicht gezählt"))
            self.table.setItem(row, 3, QTableWidgetItem(issue.message))
        self.table.setSortingEnabled(True)
        self.table.sortItems(0, Qt.SortOrder.AscendingOrder)

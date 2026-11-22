import pandas as pd
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QHeaderView, QLabel, QTableWidget,
                               QTableWidgetItem, QVBoxLayout)

from ui.theme import muted

KEEP_MINE, TAKE_THEIRS = "Ihren Wert speichern", "Wert aus der Datei behalten"


# a cell key (see model.club_file.cell_key) as the user knows it: dates as 24.12.1960, empty as "(leer)"
def shown(key):
    if not key:
        return "(leer)"
    if len(key) == 10 and key[4] == "-" and key[7] == "-":
        return pd.Timestamp(key).strftime("%d.%m.%Y")
    return key


# somebody else changed the same fields of a member in the meantime: per field, which value is saved
class ConflictDialog(QDialog):

    def __init__(self, conflict, name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gleichzeitig geändert")
        self.setMinimumWidth(640)
        self.conflict = conflict
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(name + " wurde inzwischen von jemand anderem geändert, auch an Feldern, die Sie "
                                       "geändert haben. Welcher Wert soll gelten?"))
        layout.addWidget(muted("Alle anderen Änderungen (Ihre und die der anderen) werden übernommen."))
        self.table = QTableWidget(len(conflict.fields), 4)
        self.table.setHorizontalHeaderLabels(["Feld", "Ihr Wert", "Jetzt in der Datei", "Speichern"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.choices = {}
        for row, field in enumerate(conflict.fields):
            for column, text in enumerate((field.heading, shown(field.mine), shown(field.theirs))):
                self.table.setItem(row, column, QTableWidgetItem(text))
            box = QComboBox()
            box.addItems([KEEP_MINE, TAKE_THEIRS])
            self.choices[field.field] = box
            self.table.setCellWidget(row, 3, box)
        layout.addWidget(self.table)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Speichern")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def keep_mine(self, field):
        return self.choices[field].currentText() == KEEP_MINE

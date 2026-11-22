import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QListWidget, QListWidgetItem, QVBoxLayout

from ui.theme import muted


# members to delete for good; each is ticked, deleting has to be confirmed. After accept: chosen()
class DeleteDialog(QDialog):

    def __init__(self, members, intro, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endgültig löschen")
        self.setMinimumSize(560, 420)
        layout = QVBoxLayout(self)
        text = QLabel(intro)
        text.setWordWrap(True)
        layout.addWidget(text)
        self.list = QListWidget()
        for member in members:
            exit_date = "" if pd.isna(member.exit_date) else " – ausgetreten am " + member.exit_date.strftime("%d.%m.%Y")
            item = QListWidgetItem(member.full_name() + " (Nr " + str(member.nr) + ")" + exit_date)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, member)
            self.list.addItem(item)
        layout.addWidget(self.list, stretch=1)
        layout.addWidget(muted("Gelöscht werden die Zeile in der Mitgliederliste und die Funktionen. Im "
                               "Änderungsprotokoll bleibt nur „Nr … gelöscht“ ohne Namen und Werte. In den "
                               "Sicherungen neben der Datei sind die Daten noch bis zu 12 Monate enthalten."))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Endgültig löschen")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def chosen(self):
        return [self.list.item(index).data(Qt.ItemDataRole.UserRole) for index in range(self.list.count())
                if self.list.item(index).checkState() == Qt.CheckState.Checked]

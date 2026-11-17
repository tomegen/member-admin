from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout

from config.config import parse_numbers
from ui.theme import muted


def as_text(numbers):
    return ", ".join(str(number) for number in numbers)


# which birthdays and honors can be selected; changes are valid for all following starts of the app
class SettingsDialog(QDialog):

    def __init__(self, birthdays, honors, default_birthdays, default_honors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.setMinimumWidth(760)
        self.defaults = (default_birthdays, default_honors)
        self.birthdays = birthdays
        self.honors = honors

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(muted("Welche Geburtstage und Jubiläen sollen zur Auswahl stehen? "
                               "Zahlen mit Komma trennen. Die Einstellung gilt auch beim nächsten Start."))
        form = QFormLayout()
        self.birthday_edit = QLineEdit(as_text(birthdays))
        self.honor_edit = QLineEdit(as_text(honors))
        form.addRow("Geburtstage (Alter):", self.birthday_edit)
        form.addRow("Ehrungen (Jahre Mitgliedschaft):", self.honor_edit)
        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #dc2626;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Speichern")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        reset = buttons.addButton("Standard wiederherstellen", QDialogButtonBox.ButtonRole.ResetRole)
        reset.clicked.connect(self.restore_defaults)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def restore_defaults(self):
        self.birthday_edit.setText(as_text(self.defaults[0]))
        self.honor_edit.setText(as_text(self.defaults[1]))
        self.error_label.clear()

    def accept(self):
        try:
            self.birthdays = parse_numbers(self.birthday_edit.text())
        except ValueError as error:
            self.error_label.setText("Geburtstage: " + str(error))
            return
        try:
            self.honors = parse_numbers(self.honor_edit.text())
        except ValueError as error:
            self.error_label.setText("Ehrungen: " + str(error))
            return
        super().accept()

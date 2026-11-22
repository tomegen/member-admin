from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                               QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QSpinBox,
                               QTableWidget, QTabWidget, QVBoxLayout, QWidget)

from model import schema
from model.club_settings import ClubSettings, Occasion
from ui.theme import muted

KINDS = [schema.BIRTHDAY, schema.HONOR]
PASSIVE_TEXTS = [(schema.PASSIVE_BIRTHDAYS, "Passive Mitglieder zählen bei Geburtstagen"),
                 (schema.PASSIVE_HONORS, "Passive Mitglieder zählen bei Ehrungen"),
                 (schema.PASSIVE_STATISTICS, "Passive Mitglieder zählen in der Statistik")]


def occasion_order(occasion):
    return KINDS.index(occasion.kind), -1 if occasion.years is None else occasion.years


# the occasions as they apply: the rows of the file, the defaults for a kind without rows
def effective_occasions(settings, default_birthdays, default_honors):
    found = list(settings.occasions)
    for kind, defaults in ((schema.BIRTHDAY, default_birthdays), (schema.HONOR, default_honors)):
        if not any(occasion.kind == kind for occasion in found):
            found += [Occasion(kind, years, "", "") for years in defaults]
    return sorted(found, key=occasion_order)


def without_notes(occasions):
    return sorted((occasion.kind, occasion.years, occasion.gift) for occasion in occasions)


# the settings of the club in its member file (sheet "Einstellungen"); they apply to everybody who uses the file.
# After accept: settings (ClubSettings) and editor_name (stored on this computer only)
class ClubSettingsDialog(QDialog):

    def __init__(self, settings, default_birthdays, default_honors, editor_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen des Vereins")
        self.setMinimumSize(760, 560)
        self.base = settings
        self.defaults = (default_birthdays, default_honors)
        self.effective = effective_occasions(settings, default_birthdays, default_honors)
        self.settings = settings
        self.editor_name = editor_name

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(muted("Diese Einstellungen stehen in der Mitgliederliste (Blatt „Einstellungen“) und gelten "
                               "für alle, die die Liste nutzen."))
        self.tabs = QTabWidget()
        self.tabs.addTab(self.build_occasions(), "Anlässe")
        self.tabs.addTab(self.build_lists(), "Auswahllisten")
        self.tabs.addTab(self.build_general(), "Allgemein")
        layout.addWidget(self.tabs, stretch=1)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #dc2626;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Speichern")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # --- occasions: which birthdays and anniversaries are celebrated, and with what ----------------------------

    def build_occasions(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(muted("Eine Zeile je Anlass, der gefeiert wird. Diese Zahlen stehen unter „Geburtstage“ "
                               "und „Ehrungen“ zur Auswahl. „keine“ = dieser Anlass wird nicht gefeiert."))
        self.occasion_table = QTableWidget(0, 3)
        self.occasion_table.setHorizontalHeaderLabels(["Anlass", "Jahre", "Geschenk/Maßnahme"])
        self.occasion_table.verticalHeader().setVisible(False)
        self.occasion_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.occasion_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.occasion_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.occasion_table, stretch=1)
        for occasion in self.effective:
            self.add_occasion_row(occasion)

        row = QHBoxLayout()
        add_button = QPushButton("Zeile hinzufügen")
        add_button.clicked.connect(lambda: self.add_occasion_row(Occasion(schema.BIRTHDAY, 60, "", "")))
        remove_button = QPushButton("Markierte Zeile entfernen")
        remove_button.clicked.connect(self.remove_occasion_rows)
        reset_button = QPushButton("Standard wiederherstellen")
        reset_button.clicked.connect(self.restore_default_occasions)
        for button in (add_button, remove_button, reset_button):
            row.addWidget(button)
        row.addStretch()
        layout.addLayout(row)
        return page

    def add_occasion_row(self, occasion):
        row = self.occasion_table.rowCount()
        self.occasion_table.insertRow(row)
        kind = QComboBox()
        kind.addItems(KINDS)
        kind.setCurrentText(occasion.kind)
        years = QSpinBox()
        years.setRange(0, 120)
        years.setSpecialValueText("keine")
        years.setValue(occasion.years or 0)
        gift = QLineEdit(occasion.gift)
        gift.setPlaceholderText("z. B. Präsentkorb, Urkunde, Besuch durch den Vorstand")
        for column, widget in enumerate((kind, years, gift)):
            self.occasion_table.setCellWidget(row, column, widget)

    def remove_occasion_rows(self):
        for row in sorted({index.row() for index in self.occasion_table.selectedIndexes()}, reverse=True):
            self.occasion_table.removeRow(row)

    def restore_default_occasions(self):
        self.occasion_table.setRowCount(0)
        for occasion in effective_occasions(ClubSettings(), *self.defaults):
            self.add_occasion_row(occasion)

    def occasions(self):
        found = []
        for row in range(self.occasion_table.rowCount()):
            kind, years, gift = (self.occasion_table.cellWidget(row, column) for column in range(3))
            found.append(Occasion(kind.currentText(), years.value() or None, gift.text().strip(), ""))
        return sorted(found, key=occasion_order)

    # --- value lists for the dropdowns in the member file ------------------------------------------------------

    def build_lists(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(muted("Diese Werte stehen in der Mitgliederliste als Auswahl zur Verfügung. "
                               "Ein Eintrag pro Zeile."))
        row = QHBoxLayout()
        self.list_edits = {}
        for name, _ in schema.VALUE_LISTS:
            column = QVBoxLayout()
            column.addWidget(QLabel(name))
            edit = QPlainTextEdit("\n".join(self.base.lists[name]))
            self.list_edits[name] = edit
            column.addWidget(edit)
            row.addLayout(column)
        layout.addLayout(row, stretch=1)
        return page

    def lists(self):
        return {name: list(dict.fromkeys(line.strip() for line in edit.toPlainText().splitlines() if line.strip()))
                for name, edit in self.list_edits.items()}

    # --- general settings and the name of the user ------------------------------------------------------------

    def build_general(self):
        page = QWidget()
        form = QFormLayout(page)
        self.club_edit = QLineEdit(self.base.club_name)
        form.addRow("Vereinsname:", self.club_edit)
        self.delete_spin = QSpinBox()
        self.delete_spin.setRange(0, 100)
        self.delete_spin.setSpecialValueText("nie")
        self.delete_spin.setSuffix(" Jahre nach dem Austritt")
        self.delete_spin.setValue(self.base.delete_after or 0)
        self.delete_spin.setToolTip("Ausgetretene, deren Austritt länger zurückliegt, schlägt die App zum "
                                    "endgültigen Löschen vor (nur nach Bestätigung).")
        form.addRow("Ausgetretene löschen:", self.delete_spin)
        self.reminder_spin = QSpinBox()
        self.reminder_spin.setRange(0, 60)
        self.reminder_spin.setSpecialValueText("keine")
        self.reminder_spin.setSuffix(" Tage vorher")
        self.reminder_spin.setValue(self.base.reminder_days)
        form.addRow("Kalender-Erinnerung:", self.reminder_spin)
        self.passive_checks = {}
        for key, text in PASSIVE_TEXTS:
            check = QCheckBox(text)
            check.setChecked(self.base.general[key])
            self.passive_checks[key] = check
            form.addRow("", check)
        form.addRow(QLabel(""))
        self.editor_edit = QLineEdit(self.editor_name)
        self.editor_edit.setToolTip("Steht im Änderungsprotokoll bei jeder Änderung, die Sie in der App machen. "
                                    "Wird nur auf diesem Computer gespeichert.")
        form.addRow("Ihr Name (Änderungsprotokoll):", self.editor_edit)
        return page

    def general(self):
        general = dict(self.base.general)
        general[schema.CLUB_NAME] = self.club_edit.text().strip()
        general[schema.DELETE_AFTER] = self.delete_spin.value() or None
        general[schema.REMINDER_DAYS] = self.reminder_spin.value()
        for key, check in self.passive_checks.items():
            general[key] = check.isChecked()
        return general

    def accept(self):
        occasions = self.occasions()
        seen = set()
        for occasion in occasions:
            key = (occasion.kind, occasion.years)
            if key in seen:
                self.tabs.setCurrentIndex(0)
                self.error_label.setText(occasion.kind + " " + ("keine" if occasion.years is None else
                                                                str(occasion.years)) + " steht doppelt in der Liste.")
                return
            seen.add(key)
        if not self.editor_edit.text().strip():
            self.tabs.setCurrentIndex(2)
            self.error_label.setText("Bitte Ihren Namen für das Änderungsprotokoll eintragen.")
            return
        # unchanged defaults are not written into the file: they stay defaults
        if without_notes(occasions) == without_notes(self.effective):
            occasions = self.base.occasions
        self.settings = ClubSettings(occasions, self.lists(), self.general())
        self.editor_name = self.editor_edit.text().strip()
        super().accept()

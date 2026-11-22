import datetime

import pandas as pd
from PySide6.QtCore import QDate, QEvent
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFormLayout,
                               QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QTableWidget,
                               QTabWidget, QToolButton, QVBoxLayout, QWidget)

from model import schema
from model.functions import Function, function_key
from ui.theme import muted

EMPTY_DATE = QDate(1800, 1, 1)
COLUMNS = {column.field: column for column in schema.MEMBER_COLUMNS}
ATTRIBUTES = {"phone": "phone_number"}   # field -> attribute of Member, where they differ
GROUPS = [("Mitglied", ["last_name", "first_name", "gender", "birthday", "member_since", "status", "exit_date",
                        "exit_reason", "department", "fee_class"]),
          ("Kontakt und Bank", ["street", "plz", "ort", "phone", "mobile_phone", "email", "iban", "reference", "note"])]
EXIT_REASONS = ["Kündigung", "Umzug", "Verstorben", "Ausschluss"]


def to_date(value):
    return None if value is None or pd.isna(value) else pd.Timestamp(value).date()


# a date that may stay empty: the calendar opens at today, "✕" empties it again
class DateField(QWidget):

    def __init__(self, value=None):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.edit = QDateEdit()
        self.edit.setCalendarPopup(True)
        self.edit.setDisplayFormat("dd.MM.yyyy")
        self.edit.setMinimumDate(EMPTY_DATE)
        self.edit.setMaximumDate(QDate(2100, 12, 31))
        self.edit.setSpecialValueText(" ")   # shown for the minimum date, which means "empty"
        self.edit.calendarWidget().installEventFilter(self)
        clear = QToolButton()
        clear.setText("✕")
        clear.setToolTip("Datum leeren")
        clear.clicked.connect(lambda: self.set_value(None))
        layout.addWidget(self.edit, stretch=1)
        layout.addWidget(clear)
        self.set_value(value)

    def set_value(self, value):
        date = to_date(value)
        self.edit.setDate(EMPTY_DATE if date is None else QDate(date.year, date.month, date.day))

    def value(self):
        date = self.edit.date()
        return None if date == EMPTY_DATE else datetime.date(date.year(), date.month(), date.day())

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Show and self.value() is None:
            today = QDate.currentDate()
            watched.setCurrentPage(today.year(), today.month())
        return False


def choice_box(values, current, editable=False):
    box = QComboBox()
    box.setEditable(editable)
    box.addItems(list(values) + ([current] if current and current not in values else []))
    box.setCurrentText(current)
    return box


# a member to add (member None) or to change. After accept: values() / changed_values() and functions()
class MemberDialog(QDialog):

    def __init__(self, settings, member=None, functions=(), parent=None):
        super().__init__(parent)
        self.member = member
        self.settings = settings
        self.setWindowTitle("Neues Mitglied" if member is None else
                            "Mitglied " + str(member.nr) + ": " + member.full_name())
        self.setMinimumSize(640, 560)
        self.widgets = {}

        layout = QVBoxLayout(self)
        layout.addWidget(muted("Felder mit * sind Pflicht. Gespeichert wird direkt in der Mitgliederliste; "
                               "Änderungen, die jemand anderes inzwischen gemacht hat, bleiben erhalten."))
        self.tabs = QTabWidget()
        for title, fields in GROUPS:
            page = QWidget()
            form = QFormLayout(page)
            if title == "Mitglied" and member is not None:
                form.addRow("Nr:", QLabel(str(member.nr)))
            for field in fields:
                column = COLUMNS[field]
                widget = self.make_widget(column, self.current(field))
                self.widgets[field] = widget
                form.addRow(column.heading + (" *" if column.mandatory else "") + ":", widget)
            self.tabs.addTab(page, title)
        self.tabs.addTab(self.build_functions(functions), "Funktionen")
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

        self.initial = self.values()
        self.initial_functions = self.function_keys()

    def current(self, field):
        if self.member is None:
            return schema.ACTIVE if field == "status" else None
        value = getattr(self.member, ATTRIBUTES.get(field, field))
        return to_date(value) if COLUMNS[field].kind == "date" else value

    def make_widget(self, column, value):
        if column.kind == "date":
            return DateField(value)
        if column.kind == "gender":
            return choice_box([""] + schema.GENDERS, value or "")
        if column.kind == "status":
            return choice_box(schema.STATUSES, value or schema.ACTIVE)
        if column.kind.startswith("list:"):
            return choice_box([""] + self.settings.lists[column.kind.split(":", 1)[1]], value or "", editable=True)
        if column.field == "note":
            edit = QPlainTextEdit(value or "")
            edit.setFixedHeight(80)
            return edit
        return QLineEdit(value or "")

    @staticmethod
    def widget_value(widget):
        if isinstance(widget, DateField):
            return widget.value()
        if isinstance(widget, QComboBox):
            return widget.currentText().strip()
        if isinstance(widget, QPlainTextEdit):
            return widget.toPlainText().strip()
        return widget.text().strip()

    def values(self):
        return {field: self.widget_value(widget) for field, widget in self.widgets.items()}

    # only what was changed here is saved: a value the dialog cannot show (e.g. an unreadable date) stays
    def changed_values(self):
        return {field: value for field, value in self.values().items() if value != self.initial[field]}

    # --- functions --------------------------------------------------------------------------------------------

    def build_functions(self, functions):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(muted("Ämter und Aufgaben im Verein (Blatt „Funktionen“). „bis“ leer = bis heute."))
        self.function_table = QTableWidget(0, 4)
        self.function_table.setHorizontalHeaderLabels(["Funktion", "von", "bis", "Bemerkung"])
        self.function_table.verticalHeader().setVisible(False)
        self.function_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.function_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.function_table.horizontalHeader().setStretchLastSection(True)
        for column, width in enumerate((180, 150, 150)):
            self.function_table.setColumnWidth(column, width)
        layout.addWidget(self.function_table, stretch=1)
        for function in functions:
            self.add_function_row(function.function, function.start, function.end, function.note)
        row = QHBoxLayout()
        add_button = QPushButton("Funktion hinzufügen")
        add_button.clicked.connect(lambda: self.add_function_row("", None, None, ""))
        remove_button = QPushButton("Markierte Funktion entfernen")
        remove_button.clicked.connect(self.remove_function_rows)
        row.addWidget(add_button)
        row.addWidget(remove_button)
        row.addStretch()
        layout.addLayout(row)
        return page

    def add_function_row(self, function, start, end, note):
        row = self.function_table.rowCount()
        self.function_table.insertRow(row)
        widgets = (choice_box([""] + self.settings.lists["Funktionen"], function, editable=True), DateField(start),
                   DateField(end), QLineEdit(note))
        for column, widget in enumerate(widgets):
            self.function_table.setCellWidget(row, column, widget)
        self.function_table.resizeRowsToContents()

    def remove_function_rows(self):
        for row in sorted({index.row() for index in self.function_table.selectedIndexes()}, reverse=True):
            self.function_table.removeRow(row)

    # [(function, from, to, note)] as entered
    def functions(self):
        return [tuple(self.widget_value(self.function_table.cellWidget(row, column)) for column in range(4))
                for row in range(self.function_table.rowCount())]

    def function_keys(self):
        return [function_key(Function(None, None, "", function, start, end, note))
                for function, start, end, note in self.functions()]

    def functions_changed(self):
        return self.function_keys() != self.initial_functions

    # --- checks before saving ---------------------------------------------------------------------------------

    def problems(self):
        values, changed = self.values(), self.changed_values()
        for field, column in COLUMNS.items():
            if column.mandatory and field in values and not values[field]:
                if self.member is None or field in changed:
                    return column.heading + " fehlt.", field
        if values["status"] == schema.LEFT and not values["exit_date"] and (
                self.member is None or {"status", "exit_date"} & set(changed)):
            return "Bei „ausgetreten“ bitte das Datum des Austritts angeben.", "exit_date"
        if values["status"] != schema.LEFT and values["exit_date"] and \
                values["exit_date"] <= datetime.date.today() and {"status", "exit_date"} & set(changed):
            return "Das Austrittsdatum liegt nicht in der Zukunft: bitte Status „ausgetreten“ wählen.", "status"
        birthday, since = values["birthday"], values["member_since"]
        if birthday and birthday > datetime.date.today():
            return "Der Geburtstag liegt in der Zukunft.", "birthday"
        if birthday and since and since < birthday:
            return "Der Eintritt liegt vor dem Geburtstag.", "member_since"
        for function, start, end, _ in self.functions():
            if not function:
                return "Bei einer Funktion fehlt die Bezeichnung.", None
            if start and end and end < start:
                return "Bei „" + function + "“ liegt „bis“ vor „von“.", None
        return None, None

    def accept(self):
        message, field = self.problems()
        if message:
            self.error_label.setText(message)
            if field is None:
                self.tabs.setCurrentIndex(len(GROUPS))
            else:
                self.tabs.setCurrentIndex(next(i for i, (_, fields) in enumerate(GROUPS) if field in fields))
                self.widgets[field].setFocus()
            return
        super().accept()


# the exit of a member: date and reason; the member stays in the list with status "ausgetreten"
class ExitDialog(QDialog):

    def __init__(self, member, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Austritt erfassen")
        layout = QVBoxLayout(self)
        text = QLabel(member.full_name() + " tritt aus. Die Person bleibt in der Liste (Status „ausgetreten“) und "
                      "zählt nicht mehr für Geburtstage, Ehrungen und Statistik.")
        text.setWordWrap(True)
        layout.addWidget(text)
        self.setMinimumWidth(480)
        form = QFormLayout()
        self.date_field = DateField(datetime.date.today())
        self.reason_box = choice_box([""] + EXIT_REASONS, "", editable=True)
        form.addRow("Austritt am *:", self.date_field)
        form.addRow("Grund:", self.reason_box)
        layout.addLayout(form)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #dc2626;")
        layout.addWidget(self.error_label)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Austritt speichern")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return {"status": schema.LEFT, "exit_date": self.date_field.value(),
                "exit_reason": self.reason_box.currentText().strip()}

    def accept(self):
        if self.date_field.value() is None:
            self.error_label.setText("Bitte das Datum des Austritts angeben.")
            return
        super().accept()

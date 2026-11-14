import os

import pandas as pd
from PySide6.QtCore import QDate, QSettings, QStandardPaths, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QDateEdit, QGridLayout, QHBoxLayout, QHeaderView,
                               QLabel, QMessageBox, QPushButton, QRadioButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QFileDialog)

from logic.export import write_entries_into_xlsx
from ui.theme import heading, muted, primary_button


# table item that is sorted by its date and not by the displayed text
class DateItem(QTableWidgetItem):

    def __init__(self, date):
        super().__init__(date.strftime("%d.%m.%Y"))
        self.sort_key = date

    def __lt__(self, other):
        return self.sort_key < other.sort_key


# describes what a ResultPage calculates (birthdays or honors)
class ResultSpec:

    def __init__(self, title, description, numbers, checkbox_text, occasion, file_stem, finder, txt_writer,
                 ics_writer=None):
        self.title = title
        self.description = description
        self.numbers = numbers
        self.checkbox_text = checkbox_text
        self.occasion = occasion
        self.file_stem = file_stem
        self.finder = finder
        self.txt_writer = txt_writer
        self.ics_writer = ics_writer


class ResultPage(QWidget):
    COLUMNS = ["Datum", "Anlass", "Name", "Telefon / Mobil"]

    def __init__(self, spec):
        super().__init__()
        self.spec = spec
        self.members = None
        self.year = pd.Timestamp.now().year
        self.checkboxes = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(12)
        layout.addWidget(heading(spec.title))
        layout.addWidget(muted(spec.description))

        # timeframe: whole year (default) or own dates
        range_row = QHBoxLayout()
        self.year_radio = QRadioButton()
        self.year_radio.setChecked(True)
        self.custom_radio = QRadioButton("Eigener Zeitraum:")
        self.from_edit = self.make_date_edit()
        self.to_edit = self.make_date_edit()
        range_row.addWidget(self.year_radio)
        range_row.addSpacing(16)
        range_row.addWidget(self.custom_radio)
        range_row.addWidget(self.from_edit)
        range_row.addWidget(QLabel("bis"))
        range_row.addWidget(self.to_edit)
        range_row.addStretch()
        layout.addLayout(range_row)

        # selection of the numbers (e.g. 18., 20., 30. birthday)
        select_row = QHBoxLayout()
        select_row.addWidget(QLabel("Auswahl:"))
        all_button = QPushButton("alle")
        none_button = QPushButton("keine")
        for button in (all_button, none_button):
            button.setObjectName("link")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        all_button.clicked.connect(lambda: self.set_all_checked(True))
        none_button.clicked.connect(lambda: self.set_all_checked(False))
        select_row.addWidget(all_button)
        select_row.addWidget(none_button)
        select_row.addStretch()
        layout.addLayout(select_row)

        self.checkbox_grid = QGridLayout()
        for index, number in enumerate(spec.numbers):
            checkbox = QCheckBox(spec.checkbox_text(number))
            checkbox.setChecked(True)
            checkbox.toggled.connect(self.refresh)
            self.checkboxes.append(checkbox)
            self.checkbox_grid.addWidget(checkbox, index // 5, index % 5)
        layout.addLayout(self.checkbox_grid)

        # preview
        self.count_label = QLabel()
        layout.addWidget(self.count_label)
        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, stretch=1)

        # export
        button_row = QHBoxLayout()
        self.txt_button = primary_button("Als Textdatei speichern")
        self.xlsx_button = primary_button("Als Excel-Datei speichern")
        self.txt_button.clicked.connect(lambda: self.save("txt"))
        self.xlsx_button.clicked.connect(lambda: self.save("xlsx"))
        button_row.addWidget(self.txt_button)
        button_row.addWidget(self.xlsx_button)
        self.export_buttons = [self.txt_button, self.xlsx_button]
        if spec.ics_writer:
            self.ics_button = primary_button("Als Kalender (ICS) speichern")
            self.ics_button.clicked.connect(lambda: self.save("ics"))
            button_row.addWidget(self.ics_button)
            self.export_buttons.append(self.ics_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        self.year_radio.toggled.connect(self.on_range_mode_changed)
        self.from_edit.dateChanged.connect(self.refresh)
        self.to_edit.dateChanged.connect(self.refresh)
        self.set_year(self.year)
        self.on_range_mode_changed()

    @staticmethod
    def make_date_edit():
        edit = QDateEdit()
        edit.setCalendarPopup(True)
        edit.setDisplayFormat("dd.MM.yyyy")
        return edit

    def set_members(self, members):
        self.members = members
        self.refresh()

    def set_year(self, year):
        self.year = year
        self.year_radio.setText("Ganzes Jahr " + str(year))
        # own dates start with the whole year, too
        self.from_edit.blockSignals(True)
        self.to_edit.blockSignals(True)
        self.from_edit.setDate(QDate(year, 1, 1))
        self.to_edit.setDate(QDate(year, 12, 31))
        self.from_edit.blockSignals(False)
        self.to_edit.blockSignals(False)
        self.refresh()

    def on_range_mode_changed(self):
        custom = self.custom_radio.isChecked()
        self.from_edit.setEnabled(custom)
        self.to_edit.setEnabled(custom)
        self.refresh()

    def set_all_checked(self, checked):
        for checkbox in self.checkboxes:
            checkbox.blockSignals(True)
            checkbox.setChecked(checked)
            checkbox.blockSignals(False)
        self.refresh()

    def date_range(self):
        if self.custom_radio.isChecked():
            start, end = self.from_edit.date(), self.to_edit.date()
            return (pd.Timestamp(start.year(), start.month(), start.day()),
                    pd.Timestamp(end.year(), end.month(), end.day()))
        return pd.Timestamp(self.year, 1, 1), pd.Timestamp(self.year, 12, 31)

    def checked_numbers(self):
        return [number for number, checkbox in zip(self.spec.numbers, self.checkboxes) if checkbox.isChecked()]

    def entries(self):
        if self.members is None:
            return []
        start, end = self.date_range()
        return self.spec.finder(self.members.members, self.checked_numbers(), start, end)

    def refresh(self):
        entries = self.entries()
        start, end = self.date_range()
        if end < start:
            self.count_label.setText("Das Ende des Zeitraums liegt vor dem Start.")
        else:
            self.count_label.setText(str(len(entries)) + " Treffer")

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            member = entry.member
            contact = " / ".join(value for value in (member.phone_number, member.mobile_phone) if value)
            self.table.setItem(row, 0, DateItem(entry.date))
            self.table.setItem(row, 1, QTableWidgetItem(self.spec.occasion(entry.number)))
            self.table.setItem(row, 2, QTableWidgetItem(member.full_name()))
            self.table.setItem(row, 3, QTableWidgetItem(contact))
        self.table.setSortingEnabled(True)
        self.table.sortItems(0, Qt.SortOrder.AscendingOrder)

        valid = bool(entries) and end >= start
        for button in self.export_buttons:
            button.setEnabled(valid)

    # write the result into a file; kind is "txt", "xlsx" or "ics"
    def write(self, kind, path):
        start, end = self.date_range()
        members, numbers = self.members.members, self.checked_numbers()
        if kind == "txt":
            return self.spec.txt_writer(members, numbers, start, end, path)
        if kind == "ics":
            return self.spec.ics_writer(members, numbers, start, end, path)
        return write_entries_into_xlsx(self.entries(), self.spec.occasion, path)

    def save(self, kind):
        settings = QSettings()
        folder = settings.value("save_dir") or QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation)
        name = self.spec.file_stem + "_" + str(self.year) + "." + kind
        filters = {"txt": "Textdatei (*.txt)", "xlsx": "Excel-Datei (*.xlsx)", "ics": "Kalenderdatei (*.ics)"}
        path, _ = QFileDialog.getSaveFileName(self, "Speichern unter", os.path.join(folder, name), filters[kind])
        if not path:
            return
        try:
            self.write(kind, path)
        except Exception as error:
            QMessageBox.critical(self, "Speichern nicht möglich",
                                 "Die Datei konnte nicht gespeichert werden.\n"
                                 "Ist sie eventuell noch in einem anderen Programm geöffnet?\n\n" + str(error))
            return
        settings.setValue("save_dir", os.path.dirname(path))
        box = QMessageBox(self)
        box.setWindowTitle("Datei erstellt")
        box.setText("Die Datei wurde gespeichert:\n" + path)
        open_button = box.addButton("Ordner öffnen", QMessageBox.ButtonRole.ActionRole)
        box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        box.exec()
        if box.clickedButton() is open_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))

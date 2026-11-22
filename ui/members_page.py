import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMenu,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from model import schema
from ui.theme import heading, muted, primary_button, secondary_button

ALL_DEPARTMENTS = "alle Abteilungen"
# status filter: label -> statuses shown
STATUS_FILTERS = {"Mitglieder (aktiv und passiv)": (schema.ACTIVE, schema.PASSIVE),
                  "aktiv": (schema.ACTIVE,), "passiv": (schema.PASSIVE,), "ausgetreten": (schema.LEFT,),
                  "alle Einträge": None}


# table item that sorts by a key and not by its text (numbers, dates, empty values last)
class SortItem(QTableWidgetItem):

    def __init__(self, text, key):
        super().__init__(text)
        self.key = key

    def __lt__(self, other):
        return self.key < other.key


def date_item(date):
    if pd.isna(date):
        return SortItem("", (1, pd.Timestamp.max))
    return SortItem(date.strftime("%d.%m.%Y"), (0, date))


# all people in the member list; adding, changing and the exit happen in dialogs (ui.member_actions)
class MembersPage(QWidget):
    COLUMNS = ["Nr", "Name", "Vorname", "Status", "Geburtstag", "Eintritt", "Abteilung", "Ort", "Telefon / Mobil"]
    new_requested = Signal()
    edit_requested = Signal(object)
    exit_requested = Signal(object)
    numbers_requested = Signal()
    merge_requested = Signal()
    delete_requested = Signal(object)
    due_requested = Signal()
    copies_requested = Signal()

    def __init__(self):
        super().__init__()
        self.members = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(12)
        layout.addWidget(heading("Mitglieder"))
        self.note_label = muted("")
        layout.addWidget(self.note_label)

        filters = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Suchen: Name, Ort, Nr …")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self.refresh)
        self.status_box = QComboBox()
        self.status_box.addItems(list(STATUS_FILTERS))
        self.status_box.currentIndexChanged.connect(self.refresh)
        self.department_box = QComboBox()
        self.department_box.currentIndexChanged.connect(self.refresh)
        filters.addWidget(self.search_edit, stretch=1)
        filters.addWidget(self.status_box)
        filters.addWidget(self.department_box)
        layout.addLayout(filters)

        self.count_label = QLabel()
        layout.addWidget(self.count_label)
        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSortIndicator(0, Qt.SortOrder.AscendingOrder)   # by nr, until clicked
        self.table.cellDoubleClicked.connect(lambda row, column: self.request(self.edit_requested))
        self.table.itemSelectionChanged.connect(self.update_buttons)
        layout.addWidget(self.table, stretch=1)

        buttons = QHBoxLayout()
        self.new_button = primary_button("Neues Mitglied …")
        self.new_button.clicked.connect(self.new_requested.emit)
        self.edit_button = secondary_button("Bearbeiten …")
        self.edit_button.clicked.connect(lambda: self.request(self.edit_requested))
        self.exit_button = secondary_button("Austritt erfassen …")
        self.exit_button.clicked.connect(lambda: self.request(self.exit_requested))
        self.numbers_button = secondary_button("Nummern vergeben")
        self.numbers_button.setToolTip("Mitglieder, die in Excel ohne Nr eingetragen wurden, bekommen die nächsten "
                                       "freien Nummern.")
        self.numbers_button.clicked.connect(self.numbers_requested.emit)
        # rarely used: in a menu, so the buttons fit on small screens
        self.more_button = secondary_button("Weitere …")
        menu = QMenu(self.more_button)
        self.merge_action = menu.addAction("Liste abgleichen … (z. B. Export des Verbands, neue E-Mail-Adressen)")
        self.merge_action.triggered.connect(self.merge_requested.emit)
        self.delete_action = menu.addAction("Markiertes Mitglied endgültig löschen … (nur falsch angelegte Einträge)")
        self.delete_action.triggered.connect(lambda: self.request(self.delete_requested))
        self.more_button.setMenu(menu)
        self.due_button = secondary_button("Löschfrist …")
        self.due_button.clicked.connect(self.due_requested.emit)
        self.copies_button = secondary_button("Konfliktkopie prüfen")
        self.copies_button.clicked.connect(self.copies_requested.emit)
        self.copies_button.hide()
        for button in (self.new_button, self.edit_button, self.exit_button, self.more_button, self.numbers_button,
                       self.due_button, self.copies_button):
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)

    def set_members(self, members):
        self.members = members
        selected = self.department_box.currentText()
        self.department_box.blockSignals(True)
        self.department_box.clear()
        departments = list(members.settings.lists["Abteilungen"])
        departments += sorted({m.department for m in members.members if m.department} - set(departments))
        self.department_box.addItems([ALL_DEPARTMENTS] + departments)
        self.department_box.setCurrentText(selected if selected in departments else ALL_DEPARTMENTS)
        self.department_box.setVisible(bool(departments))
        self.department_box.blockSignals(False)
        editable = members.standard
        self.note_label.setText("Doppelklick auf eine Zeile zum Bearbeiten. Gespeichert wird direkt in der "
                                "Mitgliederliste." if editable else
                                "Diese Liste ist noch nicht im Standardformat der App, deshalb kann sie hier nur "
                                "angezeigt werden. Bearbeiten Sie sie in Excel.")
        self.new_button.setEnabled(editable)
        self.merge_action.setEnabled(editable)
        self.numbers_button.setVisible(editable and any(m.nr is None for m in members.members))
        due = len(members.deletion_due())
        self.due_button.setText("Löschfrist: " + str(due) + " löschen …")
        self.due_button.setVisible(due > 0)
        self.refresh()

    def set_conflict_copies(self, count):
        self.copies_button.setText("Konfliktkopie prüfen (" + str(count) + ")")
        self.copies_button.setVisible(count > 0)

    def shown_members(self):
        if self.members is None:
            return []
        statuses = STATUS_FILTERS[self.status_box.currentText()]
        department = self.department_box.currentText()
        words = self.search_edit.text().casefold().split()
        found = []
        for member in self.members.members:
            if statuses is not None and member.status not in statuses:
                continue
            if department not in ("", ALL_DEPARTMENTS) and member.department != department:
                continue
            text = " ".join([str(member.nr or ""), member.last_name, member.first_name, member.ort,
                             member.street, member.email]).casefold()
            if all(word in text for word in words):
                found.append(member)
        return found

    def refresh(self):
        shown = self.shown_members()
        total = len(self.members.members) if self.members else 0
        self.count_label.setText(str(len(shown)) + " von " + str(total) + " Einträgen")
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(shown))
        for row, member in enumerate(shown):
            contact = " / ".join(value for value in (member.phone_number, member.mobile_phone) if value)
            items = [SortItem(str(member.nr or ""), (member.nr is None, member.nr or 0)),
                     QTableWidgetItem(member.last_name), QTableWidgetItem(member.first_name),
                     QTableWidgetItem(member.status or "(ungültig)"), date_item(member.birthday),
                     date_item(member.member_since), QTableWidgetItem(member.department),
                     QTableWidgetItem(member.ort), QTableWidgetItem(contact)]
            items[0].setData(Qt.ItemDataRole.UserRole, member)
            for column, item in enumerate(items):
                self.table.setItem(row, column, item)
        self.table.setSortingEnabled(True)
        self.update_buttons()

    def selected_member(self):
        rows = {index.row() for index in self.table.selectedIndexes()}
        if len(rows) != 1:
            return None
        return self.table.item(rows.pop(), 0).data(Qt.ItemDataRole.UserRole)

    def update_buttons(self):
        member = self.selected_member()
        editable = self.members is not None and self.members.standard
        self.edit_button.setEnabled(editable and member is not None)
        self.exit_button.setEnabled(editable and member is not None and member.status != schema.LEFT)
        self.delete_action.setEnabled(editable and member is not None)

    def request(self, signal):
        member = self.selected_member()
        if member is not None and self.members.standard:
            signal.emit(member)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QHeaderView, QLabel, QPushButton, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout)

from logic.merge import CHANGED, NEW, SAME, SIMILAR, key
from ui.conflict_dialog import shown
from ui.theme import muted

ROLE = Qt.ItemDataRole.UserRole


def short_description(values):
    parts = [shown(key(field, values.get(field))) for field in ("birthday", "ort") if values.get(field)]
    return ", ".join(parts)


# what a list (import) or a conflict copy would change in the member file; the user ticks what is taken over.
# After accept the MergeItems carry the decision (take, chosen); leave() are the nr to mark as left
class MergeDialog(QDialog):

    def __init__(self, items, only_in_file, title, intro, offer_leave=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(860, 600)
        self.items = items
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(intro))
        counts = {kind: sum(1 for item in items if item.kind == kind) for kind in (NEW, SIMILAR, CHANGED, SAME)}
        layout.addWidget(muted(str(counts[NEW]) + " neu, " + str(counts[SIMILAR]) + " ähnlich (bitte prüfen), " +
                               str(counts[CHANGED]) + " mit Änderungen, " + str(counts[SAME]) + " unverändert" +
                               (", " + str(len(only_in_file)) + " nur in der Mitgliederliste" if offer_leave else "") +
                               ". Leere Felder der Mitgliederliste werden standardmäßig gefüllt, abweichende Werte "
                               "nur, wenn Sie sie anhaken."))

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Person / Feld", "In der Mitgliederliste", "Neu", "Hinweis"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setStretchLastSection(True)
        layout.addWidget(self.tree, stretch=1)

        self.person_items, self.field_items, self.leave_items = [], [], []
        for kind, label in ((NEW, "Neue Personen"), (SIMILAR, "Ähnlich – bitte prüfen, ob es neue Personen sind"),
                            (CHANGED, "Änderungen")):
            chosen = [item for item in items if item.kind == kind]
            if not chosen:
                continue
            group = self.group(label + " (" + str(len(chosen)) + ")")
            for item in chosen:
                if kind == CHANGED:
                    person = QTreeWidgetItem(group, [item.name() + " (Nr " + str(item.nr) + ")", "", "", item.note])
                    person.setToolTip(3, item.note)
                    for difference in item.differences:
                        row = QTreeWidgetItem(person, [difference.heading, shown(difference.current),
                                                       shown(difference.incoming), ""])
                        self.checkable(row, difference.field in item.chosen)
                        row.setData(0, ROLE, (item, difference.field))
                        self.field_items.append(row)
                    person.setExpanded(True)
                else:
                    row = QTreeWidgetItem(group, [item.name(), "", short_description(item.values), item.note])
                    row.setToolTip(3, item.note)
                    self.checkable(row, item.take)
                    row.setData(0, ROLE, item)
                    self.person_items.append(row)
        if offer_leave and only_in_file:
            group = self.group("Nur in der Mitgliederliste (" + str(len(only_in_file)) + ") – nicht in Ihrer Liste")
            for member in only_in_file:
                row = QTreeWidgetItem(group, [member.full_name() + " (Nr " + str(member.nr) + ")", member.status, "",
                                              "anhaken = als ausgetreten markieren (Austritt heute)"])
                self.checkable(row, False)
                row.setData(0, ROLE, member.nr)
                self.leave_items.append(row)

        buttons_row = QHBoxLayout()
        for text, checked in (("Alle Änderungen anhaken", True), ("Keine Änderungen anhaken", False)):
            button = QPushButton(text)
            button.clicked.connect(lambda _=False, state=checked: self.check_all_fields(state))
            buttons_row.addWidget(button)
        buttons_row.addStretch()
        layout.addLayout(buttons_row)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Übernehmen")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def group(self, text):
        group = QTreeWidgetItem(self.tree, [text])
        font = QFont()
        font.setBold(True)
        group.setFont(0, font)
        group.setFirstColumnSpanned(True)
        group.setExpanded(True)
        return group

    @staticmethod
    def checkable(row, checked):
        row.setFlags(row.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        row.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def check_all_fields(self, checked):
        for row in self.field_items:
            row.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    @staticmethod
    def is_checked(row):
        return row.checkState(0) == Qt.CheckState.Checked

    # the ticks go into the MergeItems
    def accept(self):
        for row in self.person_items:
            row.data(0, ROLE).take = self.is_checked(row)
        for item in self.items:
            item.chosen = set()
        for row in self.field_items:
            item, field = row.data(0, ROLE)
            if self.is_checked(row):
                item.chosen.add(field)
        super().accept()

    def leave(self):
        return [row.data(0, ROLE) for row in self.leave_items if self.is_checked(row)]

    def has_changes(self):
        return any(item.take for item in self.items if item.member is None) or \
            any(item.chosen for item in self.items) or bool(self.leave())

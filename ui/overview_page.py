from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from ui.theme import heading, muted, primary_button


def make_card(title):
    card = QFrame()
    card.setObjectName("card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 16, 20, 16)
    value = QLabel("–")
    value.setObjectName("cardValue")
    layout.addWidget(value)
    layout.addWidget(QLabel(title))
    note = muted("")
    layout.addWidget(note)
    return card, value, note


class OverviewPage(QWidget):
    open_tab = Signal(int)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(16)
        layout.addWidget(heading("Übersicht"))

        grid = QGridLayout()
        grid.setSpacing(16)
        self.active_card = make_card("Aktive Mitglieder")
        self.new_card = make_card("Neue Mitglieder")
        self.inactive_card = make_card("Nicht gezählt (Mitglied = 0)")
        self.issues_card = make_card("Hinweise zur Mitgliederliste")
        grid.addWidget(self.active_card[0], 0, 0)
        grid.addWidget(self.new_card[0], 0, 1)
        grid.addWidget(self.inactive_card[0], 1, 0)
        grid.addWidget(self.issues_card[0], 1, 1)
        layout.addLayout(grid)

        layout.addSpacing(8)
        layout.addWidget(muted("Was möchten Sie auswerten? Das Auswertungsjahr stellen Sie oben ein."))
        birthday_button = primary_button("Geburtstage berechnen")
        birthday_button.clicked.connect(lambda: self.open_tab.emit(1))
        honor_button = primary_button("Ehrungen berechnen")
        honor_button.clicked.connect(lambda: self.open_tab.emit(2))
        layout.addWidget(birthday_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(honor_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()

    def refresh(self, members, year):
        active_issues = sum(1 for issue in members.issues if issue.active)
        self.active_card[1].setText(str(members.calculate_members()))
        self.new_card[1].setText(str(members.calculate_new_members(year)))
        self.new_card[2].setText("mit Eintritt im Jahr " + str(year))
        self.inactive_card[1].setText(str(members.calculate_inactive()))
        self.inactive_card[2].setText("zählen nicht für Geburtstage und Ehrungen")
        self.issues_card[1].setText(str(len(members.issues)))
        if active_issues:
            self.issues_card[2].setText(str(active_issues) + " davon bei aktiven Mitgliedern – siehe Tab „Datenprüfung“")
        else:
            self.issues_card[2].setText("Keine Auffälligkeiten bei aktiven Mitgliedern")

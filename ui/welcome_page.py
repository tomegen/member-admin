import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ui.theme import heading, muted, primary_button, secondary_button


class WelcomePage(QWidget):
    open_requested = Signal()
    recent_requested = Signal(str)
    template_requested = Signal()
    import_requested = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)
        layout.setContentsMargins(60, 40, 60, 40)

        title = heading("Mitglieder Management Portal", 28)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = muted("Mitglieder pflegen, Geburtstage und Ehrungen berechnen – mit Ihrer Mitgliederliste "
                         "(Excel).\nDie App sendet keine Daten ins Internet.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        self.open_button = primary_button("Mitgliederliste öffnen …")
        self.open_button.setMinimumHeight(52)
        self.open_button.setMinimumWidth(320)
        self.open_button.clicked.connect(self.open_requested.emit)
        layout.addWidget(self.open_button, alignment=Qt.AlignmentFlag.AlignCenter)

        dropzone = QLabel("… oder die Datei (.xlsx, .xls oder .csv) hierher ziehen")
        dropzone.setObjectName("dropzone")
        dropzone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(dropzone)

        self.recent_button = secondary_button("")
        self.recent_button.clicked.connect(lambda: self.recent_requested.emit(self.recent_path))
        self.recent_button.hide()
        self.recent_path = ""
        layout.addWidget(self.recent_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(12)
        for text, signal in (("Liste aus einem anderen Programm oder eigene Excel-Liste übernehmen …",
                              self.import_requested),
                             ("Noch keine Liste? Neue leere Mitgliederliste anlegen …", self.template_requested)):
            button = QPushButton(text)
            button.setObjectName("link")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(signal.emit)
            layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

    # offer the file that was used the last time
    def set_recent(self, path):
        if path and os.path.isfile(path):
            self.recent_path = path
            self.recent_button.setText("Zuletzt verwendet öffnen: " + os.path.basename(path))
            self.recent_button.show()
        else:
            self.recent_button.hide()

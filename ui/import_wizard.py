import os
from collections import Counter

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QFileDialog, QFormLayout, QGroupBox,
                               QHBoxLayout, QHeaderView, QInputDialog, QLabel, QLineEdit, QPushButton, QSpinBox,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWizard, QWizardPage)

from importer.mapping import (COLUMNS, NAME_BOTH, TARGETS, Table, convert, distinct_values, guess_header_row,
                              suggest_columns, suggest_value)
from importer.reader import DELIMITER_NAMES, ENCODINGS, read_source
from importer.writer import write_standard_file
from model import schema
from model.club_file import choice
from model.values import parse_date, to_text
from ui.theme import muted

RED, YELLOW = QColor("#fecaca"), QColor("#fef08a")
ENCODING_NAMES = {"utf-8-sig": "UTF-8", "cp1252": "Windows (ANSI)"}
CHECK_FIELDS = ["last_name", "first_name", "gender", "birthday", "member_since", "status", "exit_date"]
ESTIMATE = "(schätzen)"


def error_label():
    label = QLabel()
    label.setStyleSheet("color: #dc2626;")
    label.setWordWrap(True)
    return label


def make_table(columns):
    table = QTableWidget(0, len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    table.horizontalHeader().setStretchLastSection(True)
    return table


# a list of another program becomes a member list in the standard format; the original stays unchanged.
# After accept: result_path (the new file) and imported (number of members)
class ImportWizard(QWizard):

    def __init__(self, path, config, editor, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mitgliederliste importieren")
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)
        self.setMinimumSize(920, 660)
        for button, text in ((QWizard.WizardButton.BackButton, "< Zurück"),
                             (QWizard.WizardButton.NextButton, "Weiter >"),
                             (QWizard.WizardButton.FinishButton, "Importieren"),
                             (QWizard.WizardButton.CancelButton, "Abbrechen")):
            self.setButtonText(button, text)
        self.path, self.config, self.editor = path, config, editor
        self.source = read_source(path)   # SourceError goes to the caller
        self.header_row = guess_header_row(self.source.rows, config)
        self.table, self.targets, self.value_maps, self.rows = None, [], {}, []
        self.result_path, self.imported = None, 0
        self.source_page = SourcePage()
        self.columns_page = ColumnsPage()
        self.values_page = ValuesPage()
        self.check_page = CheckPage()
        self.target_page = TargetPage()
        for page in (self.source_page, self.columns_page, self.values_page, self.check_page, self.target_page):
            self.addPage(page)


class SourcePage(QWizardPage):

    def __init__(self):
        super().__init__()
        self.setTitle("1. Datei")
        self.setSubTitle("Prüfen Sie, ob die Überschriften Ihrer Liste richtig erkannt wurden.")
        layout = QVBoxLayout(self)
        self.file_label = QLabel()
        layout.addWidget(self.file_label)
        self.form = form = QFormLayout()
        self.sheet_box, self.encoding_box, self.delimiter_box = QComboBox(), QComboBox(), QComboBox()
        self.header_spin = QSpinBox()
        self.header_spin.setMinimum(1)
        form.addRow("Tabellenblatt:", self.sheet_box)
        form.addRow("Zeichensatz:", self.encoding_box)
        form.addRow("Trennzeichen:", self.delimiter_box)
        form.addRow("Überschriften stehen in Zeile:", self.header_spin)
        layout.addLayout(form)
        layout.addWidget(muted("Vorschau der ersten Zeilen (die Zeile mit den Überschriften ist hervorgehoben):"))
        self.preview = make_table([])
        self.preview.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.preview, stretch=1)
        self.error = error_label()
        layout.addWidget(self.error)
        self.sheet_box.currentTextChanged.connect(self.reread)
        self.encoding_box.currentIndexChanged.connect(self.reread)
        self.delimiter_box.currentIndexChanged.connect(self.reread)
        self.header_spin.valueChanged.connect(self.show_preview)

    def initializePage(self):
        wizard = self.wizard()
        source = wizard.source
        self.file_label.setText("Datei: " + os.path.basename(wizard.path))
        for box, items, current in ((self.sheet_box, [(name, name) for name in source.sheet_names], source.sheet),
                                    (self.encoding_box, [(ENCODING_NAMES[e], e) for e in ENCODINGS], source.encoding),
                                    (self.delimiter_box, list((name, d) for d, name in DELIMITER_NAMES.items()),
                                     source.delimiter)):
            box.blockSignals(True)
            box.clear()
            for text, data in items:
                box.addItem(text, data)
            box.setCurrentIndex(max(box.findData(current), 0))
            box.blockSignals(False)
        self.form.setRowVisible(0, len(source.sheet_names) > 1)
        self.form.setRowVisible(1, source.is_csv)
        self.form.setRowVisible(2, source.is_csv)
        self.show_preview()

    def reread(self):
        wizard = self.wizard()
        source = wizard.source
        wizard.source = read_source(wizard.path, sheet=self.sheet_box.currentData(),
                                    encoding=self.encoding_box.currentData() if source.is_csv else None,
                                    delimiter=self.delimiter_box.currentData() if source.is_csv else None)
        wizard.header_row = guess_header_row(wizard.source.rows, wizard.config)
        self.show_preview()

    def show_preview(self):
        wizard = self.wizard()
        rows = wizard.source.rows[:15]
        self.header_spin.blockSignals(True)
        self.header_spin.setMaximum(max(len(wizard.source.rows), 1))
        if self.sender() is not self.header_spin:
            self.header_spin.setValue(wizard.header_row + 1)
        self.header_spin.blockSignals(False)
        wizard.header_row = self.header_spin.value() - 1
        width = max((len(row) for row in rows), default=0)
        self.preview.setColumnCount(width)
        self.preview.setHorizontalHeaderLabels([str(index + 1) for index in range(width)])
        self.preview.setRowCount(len(rows))
        bold = QFont()
        bold.setBold(True)
        for row, values in enumerate(rows):
            for column in range(width):
                item = QTableWidgetItem(to_text(values[column]) if column < len(values) else "")
                if row == wizard.header_row:
                    item.setFont(bold)
                    item.setBackground(QBrush(QColor("#dbeafe")))
                self.preview.setItem(row, column, item)

    def validatePage(self):
        wizard = self.wizard()
        table = Table(wizard.source, wizard.header_row)
        if not table.rows:
            self.error.setText("Unter dieser Zeile stehen keine Daten. Bitte die Zeile mit den Überschriften oder "
                               "das Tabellenblatt prüfen.")
            return False
        self.error.clear()
        if wizard.table is None or wizard.table.headings != table.headings or wizard.table.rows != table.rows:
            wizard.targets = suggest_columns(table, wizard.config)
            wizard.value_maps, wizard.rows = {}, []
        wizard.table = table
        return True


class ColumnsPage(QWizardPage):

    def __init__(self):
        super().__init__()
        self.setTitle("2. Spalten zuordnen")
        self.setSubTitle("Welche Spalte Ihrer Liste gehört zu welchem Feld? Die Vorschläge der App können Sie "
                         "ändern. Pflicht sind Name, Vorname, Geschlecht, Geburtstag, Eintritt und Status.")
        layout = QVBoxLayout(self)
        self.table = make_table(["Spalte in Ihrer Liste", "Beispielwerte", "Übernehmen als"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 300)
        layout.addWidget(self.table, stretch=1)
        self.note = muted("")
        layout.addWidget(self.note)
        self.error = error_label()
        layout.addWidget(self.error)
        self.boxes = []

    def initializePage(self):
        wizard = self.wizard()
        self.table.setRowCount(len(wizard.table.headings))
        self.boxes = []
        for row, heading in enumerate(wizard.table.headings):
            self.table.setItem(row, 0, QTableWidgetItem(heading))
            self.table.setItem(row, 1, QTableWidgetItem(", ".join(wizard.table.examples(row))))
            box = QComboBox()
            for target, label in TARGETS:
                box.addItem(label + (" *" if target in COLUMNS and COLUMNS[target].mandatory else ""), target)
            box.setCurrentIndex(box.findData(wizard.targets[row]))
            box.currentIndexChanged.connect(self.update_note)
            self.boxes.append(box)
            self.table.setCellWidget(row, 2, box)
        self.update_note()

    def targets(self):
        return [box.currentData() for box in self.boxes]

    def update_note(self):
        targets = self.targets()
        notes = []
        if "gender" not in targets:
            notes.append("Ohne Spalte für das Geschlecht schätzt die App es aus dem Vornamen (Sie bestätigen das).")
        if "status" not in targets:
            notes.append("Ohne Spalte für den Status sind alle aktiv (mit Austrittsdatum in der Vergangenheit: "
                         "ausgetreten).")
        for field in ("birthday", "member_since"):
            if field not in targets:
                notes.append("Für „" + COLUMNS[field].heading + "“ gibt es keine Spalte: Sie können das Datum im "
                             "Schritt 4 eintragen, auch für viele Zeilen auf einmal.")
        self.note.setText("\n".join(notes))

    def validatePage(self):
        targets = self.targets()
        twice = [target for target, count in Counter(t for t in targets if t not in ("", "note+")).items()
                 if count > 1]
        if twice:
            labels = dict(TARGETS)
            self.error.setText("Diese Felder sind mehreren Spalten zugeordnet: " +
                               ", ".join(labels[target] for target in twice) + ".")
            return False
        if NAME_BOTH not in targets and not {"last_name", "first_name"} <= set(targets):
            self.error.setText("Bitte die Spalten für Name und Vorname zuordnen (oder „Name und Vorname (in einer "
                               "Spalte)“).")
            return False
        self.error.clear()
        wizard = self.wizard()
        if targets != wizard.targets:
            wizard.rows = []   # the rows are converted again
        wizard.targets = targets
        return True


class ValuesPage(QWizardPage):

    def __init__(self):
        super().__init__()
        self.setTitle("3. Werte zuordnen")
        self.setSubTitle("Was bedeuten die Einträge Ihrer Liste? Die App hat Vorschläge gemacht.")
        self.layout_ = QVBoxLayout(self)
        self.boxes = {}

    def initializePage(self):
        while self.layout_.count():
            widget = self.layout_.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()
        wizard = self.wizard()
        self.boxes = {}
        for field, options, title in (("status", schema.STATUSES, "Status (Spalte „{}“)"),
                                      ("gender", [ESTIMATE] + schema.GENDERS, "Geschlecht (Spalte „{}“)")):
            if field not in wizard.targets:
                continue
            column = wizard.targets.index(field)
            counts = Counter(to_text(value) for value in wizard.table.values(column))
            group = QGroupBox(title.format(wizard.table.headings[column]))
            group_layout = QVBoxLayout(group)
            table = make_table(["Eintrag in Ihrer Liste", "Anzahl", "bedeutet"])
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            raws = distinct_values(wizard.table, column)
            table.setRowCount(len(raws))
            self.boxes[field] = {}
            for row, raw in enumerate(raws):
                table.setItem(row, 0, QTableWidgetItem(raw or "(leer)"))
                table.setItem(row, 1, QTableWidgetItem(str(counts[raw])))
                box = QComboBox()
                box.addItems(options if field == "gender" else ["– bitte wählen –"] + options)
                current = wizard.value_maps.get(field, {}).get(raw, suggest_value(field, raw))
                box.setCurrentText(current or (ESTIMATE if field == "gender" else "– bitte wählen –"))
                self.boxes[field][raw] = box
                table.setCellWidget(row, 2, box)
            group_layout.addWidget(table)
            self.layout_.addWidget(group, stretch=1)
        if not self.boxes:
            self.layout_.addWidget(QLabel("Ihre Liste hat keine Spalten für Status oder Geschlecht. Weiter mit "
                                          "„Weiter“."))

    def validatePage(self):
        wizard = self.wizard()
        maps = {field: {raw: box.currentText() if box.currentText() in schema.STATUSES + schema.GENDERS else ""
                        for raw, box in boxes.items()} for field, boxes in self.boxes.items()}
        if maps != wizard.value_maps:
            wizard.rows = []
        wizard.value_maps = maps
        return True


class CheckPage(QWizardPage):
    HEADINGS = ["Übernehmen", "Zeile"] + [COLUMNS[field].heading for field in CHECK_FIELDS] + ["Hinweis"]

    def __init__(self):
        super().__init__()
        self.setTitle("4. Prüfen und ergänzen")
        self.setSubTitle("Rot: fehlt oder ist nicht lesbar – bitte ergänzen (Doppelklick) oder die Zeile abwählen. "
                         "Gelb: von der App geschätzt – bitte prüfen und bestätigen.")
        layout = QVBoxLayout(self)
        self.summary = QLabel()
        layout.addWidget(self.summary)
        row = QHBoxLayout()
        self.only_problems = QCheckBox("Nur Zeilen mit Problemen oder Schätzungen")
        self.only_problems.toggled.connect(self.apply_filter)
        self.fill_button = QPushButton("Markierte Zellen ausfüllen …")
        self.fill_button.setToolTip("Mehrere Zellen einer Spalte markieren, z. B. alle fehlenden Eintrittsdaten.")
        self.fill_button.clicked.connect(self.fill_selected)
        self.confirm_button = QPushButton()
        self.confirm_button.clicked.connect(self.confirm_estimates)
        for widget in (self.only_problems, self.fill_button, self.confirm_button):
            row.addWidget(widget)
        row.addStretch()
        layout.addLayout(row)
        self.table = make_table(self.HEADINGS)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.itemChanged.connect(self.item_changed)
        layout.addWidget(self.table, stretch=1)

    def initializePage(self):
        wizard = self.wizard()
        if not wizard.rows:
            wizard.rows = convert(wizard.table, wizard.targets, wizard.value_maps, pd.Timestamp.now().normalize())
        self.table.blockSignals(True)
        self.table.setRowCount(len(wizard.rows))
        for index, import_row in enumerate(wizard.rows):
            check = QTableWidgetItem()
            check.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            check.setCheckState(Qt.CheckState.Checked if import_row.include else Qt.CheckState.Unchecked)
            self.table.setItem(index, 0, check)
            number = QTableWidgetItem(str(import_row.number))
            number.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(index, 1, number)
            self.show_row(index)
        self.table.blockSignals(False)
        self.update_state()

    @staticmethod
    def text(import_row, field):
        if field in import_row.unreadable:
            return import_row.unreadable[field]
        value = import_row.values.get(field)
        if value is None or (not isinstance(value, str) and pd.isna(value)):
            return ""
        return value.strftime("%d.%m.%Y") if hasattr(value, "strftime") else str(value)

    def show_row(self, index):
        import_row = self.wizard().rows[index]
        problems = dict(import_row.problems())
        for offset, field in enumerate(CHECK_FIELDS, start=2):
            item = QTableWidgetItem(self.text(import_row, field))
            if field in problems:
                item.setBackground(QBrush(RED))
            elif field in import_row.estimated:
                item.setBackground(QBrush(YELLOW))
                item.setToolTip("geschätzt")
            self.table.setItem(index, offset, item)
        hint = QTableWidgetItem("; ".join([message for _, message in import_row.problems()] + import_row.hints()))
        hint.setToolTip(hint.text())
        hint.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table.setItem(index, len(self.HEADINGS) - 1, hint)

    def item_changed(self, item):
        import_row = self.wizard().rows[item.row()]
        if item.column() == 0:
            import_row.include = item.checkState() == Qt.CheckState.Checked
        elif 2 <= item.column() < 2 + len(CHECK_FIELDS):
            self.set_value(import_row, CHECK_FIELDS[item.column() - 2], item.text())
            self.table.blockSignals(True)
            self.show_row(item.row())
            self.table.blockSignals(False)
        self.update_state()

    # a value entered here: dates as 24.12.1960, gender and status also as "m" or "a"
    @staticmethod
    def set_value(import_row, field, text):
        text = text.strip()
        import_row.unreadable.pop(field, None)
        import_row.estimated.discard(field)
        kind = COLUMNS[field].kind
        if not text:
            import_row.values.pop(field, None)
            return
        if kind == "date":
            value = parse_date(text)
        elif kind in ("gender", "status"):
            value = choice(text, schema.GENDERS if kind == "gender" else schema.STATUSES) or None
        else:
            value = text
        if value is None or (kind == "date" and pd.isna(value)):
            import_row.values.pop(field, None)
            import_row.unreadable[field] = text
        else:
            import_row.values[field] = value

    def ask_value(self, heading, options):
        if options:
            value, ok = QInputDialog.getItem(self, "Ausfüllen", heading + ":", options, 0, False)
        else:
            value, ok = QInputDialog.getText(self, "Ausfüllen", heading + " (Datum z. B. 01.01.1990):")
        return value if ok else None

    def fill_selected(self):
        cells = [(index.row(), index.column()) for index in self.table.selectedIndexes()
                 if 2 <= index.column() < 2 + len(CHECK_FIELDS)]
        columns = {column for _, column in cells}
        if len(columns) != 1:
            self.summary.setText("Bitte Zellen in genau einer Spalte markieren (z. B. alle leeren Eintrittsdaten).")
            return
        field = CHECK_FIELDS[columns.pop() - 2]
        kind = COLUMNS[field].kind
        options = schema.GENDERS if kind == "gender" else schema.STATUSES if kind == "status" else None
        value = self.ask_value(COLUMNS[field].heading, options)
        if value is None:
            return
        self.table.blockSignals(True)
        for row, _ in cells:
            self.set_value(self.wizard().rows[row], field, value)
            self.show_row(row)
        self.table.blockSignals(False)
        self.update_state()

    def confirm_estimates(self):
        for import_row in self.wizard().rows:
            import_row.estimated.clear()
        self.table.blockSignals(True)
        for index in range(self.table.rowCount()):
            self.show_row(index)
        self.table.blockSignals(False)
        self.update_state()

    def apply_filter(self):
        for index, import_row in enumerate(self.wizard().rows):
            needs_look = bool(import_row.problems() or import_row.estimated)
            self.table.setRowHidden(index, self.only_problems.isChecked() and not needs_look)

    def counts(self):
        rows = [row for row in self.wizard().rows if row.include]
        return (len(rows), sum(1 for row in rows if row.problems()), sum(1 for row in rows if row.estimated),
                len(self.wizard().rows) - len(rows))

    def update_state(self):
        taken, problems, estimated, left_out = self.counts()
        parts = [str(taken) + " Zeilen werden übernommen"]
        if left_out:
            parts.append(str(left_out) + " abgewählt")
        if problems:
            parts.append(str(problems) + " mit fehlenden oder unlesbaren Angaben (rot)")
        if estimated:
            parts.append(str(estimated) + " mit geschätztem Geschlecht (gelb)")
        self.summary.setText(", ".join(parts) + ".")
        self.confirm_button.setText("Geschätzte Werte übernehmen (" + str(estimated) + ")")
        self.confirm_button.setEnabled(bool(estimated))
        self.apply_filter()
        self.completeChanged.emit()

    def isComplete(self):
        taken, problems, estimated, _ = self.counts()
        return taken > 0 and problems == 0 and estimated == 0


class TargetPage(QWizardPage):

    def __init__(self):
        super().__init__()
        self.setTitle("5. Speichern")
        self.setSubTitle("Die Mitglieder werden in eine neue Datei im Standardformat der App übernommen. "
                         "Ihre bisherige Liste bleibt unverändert.")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.club_edit = QLineEdit()
        self.club_edit.setPlaceholderText("z. B. TSV Musterdorf (freiwillig)")
        form.addRow("Vereinsname:", self.club_edit)
        path_row = QHBoxLayout()
        self.path_label = QLabel()
        change = QPushButton("Speicherort ändern …")
        change.clicked.connect(self.choose_path)
        path_row.addWidget(self.path_label, stretch=1)
        path_row.addWidget(change)
        form.addRow("Neue Datei:", path_row)
        self.folder_label = muted("")
        form.addRow("", self.folder_label)
        layout.addLayout(form)
        layout.addWidget(muted("Tipp: Legen Sie die neue Datei dort ab, wo der Vorstand sie teilt (z. B. Dropbox, "
                               "OneDrive, Nextcloud). Daneben entsteht später der Ordner „Sicherungen“."))
        self.summary = QLabel()
        layout.addWidget(self.summary)
        layout.addStretch()
        self.error = error_label()
        layout.addWidget(self.error)
        self.target = None

    def initializePage(self):
        wizard = self.wizard()
        if self.target is None:
            folder = os.path.dirname(os.path.abspath(wizard.path))
            self.target = os.path.join(folder, "Mitgliederliste.xlsx")
            counter = 2
            while os.path.exists(self.target):
                self.target = os.path.join(folder, "Mitgliederliste (" + str(counter) + ").xlsx")
                counter += 1
        self.show_target()
        taken = sum(1 for row in wizard.rows if row.include)
        self.summary.setText(str(taken) + " Mitglieder werden übernommen.")

    def choose_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "Neue Mitgliederliste speichern", self.target,
                                              "Excel-Datei (*.xlsx)")
        if path:
            self.target = path if path.lower().endswith(".xlsx") else path + ".xlsx"
            self.show_target()

    # file name, and the folder below it (it may break after every "/")
    def show_target(self):
        self.path_label.setText("<b>" + os.path.basename(self.target) + "</b>")
        self.folder_label.setText("im Ordner " + os.path.dirname(self.target).replace(os.sep, os.sep + "\u200b"))

    def validatePage(self):
        wizard = self.wizard()
        if os.path.abspath(self.target) == os.path.abspath(wizard.path):
            self.error.setText("Bitte einen anderen Namen wählen: Die bisherige Liste soll unverändert bleiben.")
            return False
        try:
            wizard.imported = write_standard_file(self.target, wizard.rows, wizard.config, wizard.path, wizard.editor,
                                                  self.club_edit.text().strip())
        except OSError as error:
            self.error.setText("Die Datei konnte nicht gespeichert werden: " + str(error))
            return False
        wizard.result_path = self.target
        return True

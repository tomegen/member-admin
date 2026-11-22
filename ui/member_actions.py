import datetime
import getpass
import os

from PySide6.QtCore import QSettings, QStandardPaths
from PySide6.QtWidgets import QFileDialog

from importer.mapping import given_fields
from importer.reader import SourceError
from logic.merge import CHANGED, NEW, SIMILAR, compare, member_values
from model.functions import function_key
from model.members import MemberListError, Members
from store.changes import add_member, assign_numbers, combine, merge_members, update_functions, update_member
from store.conflict_copies import conflict_copies, move_to_backups
from store.errors import Conflict, Duplicate
from ui.conflict_dialog import ConflictDialog
from ui.import_wizard import ImportWizard
from ui.member_dialog import ExitDialog, MemberDialog
from ui.merge_dialog import MergeDialog


# adding, changing and the exit of members: dialog, then MainWindow.save_change (reads the file again afterwards)
class MemberActions:

    def __init__(self, window):
        self.window = window

    @property
    def members(self):
        return self.window.members

    def new_member(self):
        dialog = MemberDialog(self.members.settings, parent=self.window)
        if not dialog.exec():
            return False
        values, functions = dialog.values(), dialog.functions()

        def retry(error):
            if isinstance(error, Duplicate) and self.window.ask(
                    "Mögliche Dublette", str(error) + "\n\nTrotzdem als neues Mitglied anlegen?"):
                return add_member(values, allow_duplicate=True, functions=functions)
            return None
        return self.window.save_change(add_member(values, functions=functions), retry)

    def edit_member(self, member):
        base = self.base_of(member)
        if base is None:
            return False
        functions_base = [function_key(function) for function in self.members.functions_of(member.nr)]
        dialog = MemberDialog(self.members.settings, member, self.members.functions_of(member.nr), self.window)
        if not dialog.exec():
            return False
        values = dialog.changed_values()
        functions = dialog.functions() if dialog.functions_changed() else None
        if not values and functions is None:
            return False

        def change(row_base, row_values):
            parts = [update_member(member.nr, row_base, row_values)]
            if functions is not None:
                parts.append(update_functions(member.nr, functions_base, functions))
            return combine(*parts)
        return self.window.save_change(change(base, values), lambda error: self.resolve(error, member, values, change))

    def record_exit(self, member):
        base = self.base_of(member)
        if base is None:
            return False
        dialog = ExitDialog(member, self.window)
        if not dialog.exec():
            return False
        values = dialog.values()

        def change(row_base, row_values):
            return update_member(member.nr, row_base, row_values, action="Austritt")
        return self.window.save_change(change(base, values), lambda error: self.resolve(error, member, values, change))

    def assign_numbers(self):
        return self.window.save_change(assign_numbers())

    # comparing needs a number for everybody in the file
    def numbers_ready(self):
        if not any(member.nr is None for member in self.members.members):
            return True
        if self.window.ask("Keine Mitgliedsnummer", "Einige Mitglieder haben noch keine Mitgliedsnummer (Nr). Für den "
                           "Abgleich braucht jedes Mitglied eine.\n\nJetzt Nummern vergeben?"):
            self.assign_numbers()
        return False

    # a list of another program (e.g. new e-mail addresses, the export of the association) is compared with the
    # open file; the user decides what is taken over
    def merge_list(self, path=None):
        if not self.numbers_ready():
            return False
        if path is None:
            folder = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            path, _ = QFileDialog.getOpenFileName(self.window, "Liste zum Abgleichen auswählen", folder,
                                                  "Listen (*.xlsx *.xls *.csv)")
            if not path:
                return False
        if os.path.abspath(path) == os.path.abspath(self.window.filename):
            self.window.show_error("Liste abgleichen", "Das ist die geöffnete Mitgliederliste selbst.")
            return False
        try:
            wizard = ImportWizard(path, self.window.config, QSettings().value("editor_name") or getpass.getuser(),
                                  self.window, merge_target=self.members)
        except SourceError as error:
            self.window.show_error("Liste konnte nicht gelesen werden", str(error))
            return False
        if not wizard.exec():
            return False
        fields = given_fields(wizard.targets)
        incoming = [(row.values, fields - row.estimated) for row in wizard.rows if row.include]
        items, only_in_file = compare(incoming, self.members.members, by_number="nr" in wizard.targets)
        return self.save_merge(items, only_in_file, "Liste abgleichen",
                               "Vergleich der Liste „" + os.path.basename(path) + "“ mit der Mitgliederliste.",
                               offer_leave=True, action="Import")

    def save_merge(self, items, only_in_file, title, intro, offer_leave, action):
        if not any(item.kind in (NEW, SIMILAR, CHANGED) for item in items) and not (offer_leave and only_in_file):
            self.window.inform(title, "Keine Unterschiede: Die Mitgliederliste ist bereits auf diesem Stand.")
            return True
        dialog = MergeDialog(items, only_in_file, title, intro, offer_leave, self.window)
        if not dialog.exec():
            return False
        if not dialog.has_changes():
            return True
        return self.window.save_change(merge_members(items, self.members.snapshot.rows, dialog.leave(),
                                                     datetime.date.today(), action))

    # copies made by the sync service when two people saved at the same time: compare, then move to the backups.
    # ask: first ask whether to compare now (after opening the file)
    def check_conflict_copies(self, ask=False):
        for copy in conflict_copies(self.window.filename, self.members.file_id):
            name = os.path.basename(copy)
            if ask and not self.window.ask("Konfliktkopie gefunden", "Neben der Mitgliederliste liegt eine Kopie, "
                                           "die vermutlich beim gleichzeitigen Speichern entstanden ist:\n" + name +
                                           "\n\nJetzt vergleichen und Unterschiede übernehmen?"):
                return False
            if not self.numbers_ready():
                return False
            try:
                other = Members(copy, self.window.config)
            except MemberListError as error:
                self.window.show_error("Konfliktkopie konnte nicht gelesen werden", str(error))
                return False
            incoming = [(dict(member_values(m), nr=m.nr), set(member_values(m))) for m in other.members]
            items, _ = compare(incoming, self.members.members, by_number=True)
            if not self.save_merge(items, [], "Konfliktkopie vergleichen",
                                   "Unterschiede zwischen der Kopie „" + name + "“ und der Mitgliederliste. "
                                   "Funktionen und Einstellungen der Kopie werden nicht übernommen.",
                                   offer_leave=False, action="zusammengeführt"):
                return False
            move_to_backups(copy, datetime.datetime.now())
            self.window.statusBar().showMessage("Die Konfliktkopie wurde in den Ordner „Sicherungen“ verschoben.",
                                                10000)
            self.window.update_conflict_copies()
        return True

    # the values of the member when the file was read; a member without (unique) nr has to get one first
    def base_of(self, member):
        if member.nr is None:
            if self.window.ask("Keine Mitgliedsnummer", member.full_name() + " hat noch keine Mitgliedsnummer "
                               "(Nr). Ohne Nummer kann die App das Mitglied nicht sicher wiederfinden.\n\n"
                               "Jetzt allen Mitgliedern ohne Nummer eine vergeben?"):
                self.assign_numbers()
            return None
        base = self.members.snapshot.rows.get(member.nr)
        if base is None:
            self.window.show_error("Mitgliedsnummer doppelt", "Die Mitgliedsnummer " + str(member.nr) + " steht "
                                   "mehrmals in der Liste. Bitte zuerst in Excel korrigieren (siehe Datenprüfung).")
        return base

    # somebody changed the same fields in the meantime: the user decides per field, then it is saved again
    def resolve(self, error, member, values, change):
        if not isinstance(error, Conflict):
            return None
        if error.missing:
            self.window.show_error("Mitglied nicht gefunden", str(error) + " Vielleicht wurde es in Excel gelöscht "
                                   "oder umnummeriert. Bitte „Neu einlesen“ und prüfen.")
            return None
        dialog = ConflictDialog(error, member.full_name(), self.window)
        if not dialog.exec():
            return None
        kept = {field.field for field in error.fields if not dialog.keep_mine(field.field)}
        return change(error.theirs, {field: value for field, value in values.items() if field not in kept})

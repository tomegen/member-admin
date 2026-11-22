from model.functions import function_key
from store.changes import add_member, assign_numbers, combine, update_functions, update_member
from store.errors import Conflict, Duplicate
from ui.conflict_dialog import ConflictDialog
from ui.member_dialog import ExitDialog, MemberDialog


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

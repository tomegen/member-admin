import datetime
import os
import re
import sys
import tempfile
import unicodedata

import pandas as pd
from PySide6.QtCore import QCoreApplication, QSettings, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from config.config import Config, ConfigError
from importer.mapping import Table, convert, guess_header_row, suggest_columns
from importer.reader import read_source
from importer.writer import write_standard_file
from model.club_file import is_standard_file
from logic.statistics import write_statistics_into_xlsx
from logic.template import write_member_template
from store.changes import add_member, update_member
from store.transaction import save
from model.members import Members
from ui.main_window import MainWindow
from ui.theme import apply_theme


# the checks need a file in the standard format: any other list would open the (interactive) import assistant
def checkable(path):
    if is_standard_file(path):
        return True
    print("Keine Mitgliederliste im Standardformat: " + path, file=sys.stderr)
    return False


# used by the build: load the file, write every export, write and read a new standard file, import the file and
# save changes into the copy, to find missing modules in the packaged app (the given file is not changed)
def smoke_test(window, path):
    window.show_error = lambda title, text: print(title + ": " + text, file=sys.stderr)  # no dialog that blocks
    if not checkable(path) or not window.load_file(path):
        return False
    with tempfile.TemporaryDirectory() as folder:
        for page in (window.birthdays, window.honors):
            for kind in ("txt", "xlsx", "ics"):
                target = os.path.join(folder, page.spec.file_stem + "." + kind)
                page.write(kind, target)
                if os.path.getsize(target) == 0:
                    return False
        target = os.path.join(folder, "Statistik.xlsx")
        write_statistics_into_xlsx(window.statistics_page.statistics, target)
        template = os.path.join(folder, "Vorlage.xlsx")
        write_member_template(template, window.config)
        if os.path.getsize(target) == 0 or not Members(template).standard:
            return False
        # the import assistant without its dialogs: the list itself becomes a new standard file
        source = read_source(path)
        table = Table(source, guess_header_row(source.rows, window.config))
        rows = convert(table, suggest_columns(table, window.config), {}, pd.Timestamp.now())
        imported = os.path.join(folder, "Import.xlsx")
        if not write_standard_file(imported, rows, window.config, path, "Smoke-Test") or \
                not Members(imported).standard:
            return False
        # saving (store/) on the imported copy: a new member and a change, with backup
        save(imported, add_member({"last_name": "Smoke", "first_name": "Test", "gender": "divers", "status": "aktiv",
                                   "birthday": datetime.date(2000, 1, 1), "member_since": datetime.date(2020, 1, 1)}),
             "Smoke-Test")
        first = Members(imported).members[0]
        save(imported, update_member(first.nr, Members(imported).snapshot.rows[first.nr], {"ort": "Smoke-Ort"}),
             "Smoke-Test")
        after = Members(imported)
        if after.members[0].ort != "Smoke-Ort" or after.members[-1].last_name != "Smoke" or \
                not os.listdir(os.path.join(folder, "Sicherungen")):
            return False
    return True


# used by the build: one picture of the start page and of every tab, to see the app on each system
def take_screenshots(window, path, folder):
    window.show_error = lambda title, text: print(title + ": " + text, file=sys.stderr)
    os.makedirs(folder, exist_ok=True)
    window.resize(1200, 800)
    QApplication.processEvents()
    pictures = [window.grab()]
    if not checkable(path) or not window.load_file(path):
        return False
    for index in range(window.tabs.count()):
        window.tabs.setCurrentIndex(index)
        QApplication.processEvents()
        pictures.append(window.grab())
    names = ["Start"] + [window.tabs.tabText(index) for index in range(window.tabs.count())]
    for number, (name, picture) in enumerate(zip(names, pictures)):
        ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()  # Übersicht -> Ubersicht
        if not picture.save(os.path.join(folder, "%d_%s.png" % (number, re.sub(r"\W+", "_", ascii_name).strip("_")))):
            return False
    return True


def main():
    # an excel file can be given as argument; --smoke-test checks the app and closes it again,
    # --screenshots=<folder> saves pictures of the app with this file and closes it again
    paths = [argument for argument in sys.argv[1:] if not argument.startswith("--")]
    screenshots = [argument.split("=", 1)[1] for argument in sys.argv[1:] if argument.startswith("--screenshots=")]
    check = screenshots or "--smoke-test" in sys.argv

    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("Mitgliederverwaltung")
    # the checks get own empty settings: they must not show or replace the last file of the real app
    QCoreApplication.setApplicationName("Mitglieder Management Portal" + (" Check" if check else ""))
    if check:
        QSettings().clear()
    apply_theme(app)

    try:
        config = Config()
    except ConfigError as error:
        QMessageBox.critical(None, "Problem mit der Konfigurationsdatei", str(error))
        return 1

    window = MainWindow(config)
    window.show()

    if screenshots:
        return 0 if paths and take_screenshots(window, paths[0], screenshots[0]) else 2
    if "--smoke-test" in sys.argv:
        try:
            return 0 if paths and smoke_test(window, paths[0]) else 2
        except Exception as error:
            print("Smoke test failed: " + repr(error), file=sys.stderr)
            return 2
    if paths:
        window.load_file(paths[0])
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

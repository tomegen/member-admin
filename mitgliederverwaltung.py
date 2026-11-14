import os
import sys
import tempfile

from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from config.config import Config, ConfigError
from ui.main_window import MainWindow
from ui.theme import apply_theme


# used by the build: load the file and write every export once, to find missing modules in the packaged app
def smoke_test(window, path):
    window.show_error = lambda title, text: print(title + ": " + text, file=sys.stderr)  # no dialog that blocks
    if not window.load_file(path):
        return False
    with tempfile.TemporaryDirectory() as folder:
        for page, kinds in ((window.birthdays, ("txt", "xlsx", "ics")), (window.honors, ("txt", "xlsx"))):
            for kind in kinds:
                target = os.path.join(folder, page.spec.file_stem + "." + kind)
                page.write(kind, target)
                if os.path.getsize(target) == 0:
                    return False
    return True


def main():
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("Mitgliederverwaltung")
    QCoreApplication.setApplicationName("Mitglieder Management Portal")
    apply_theme(app)

    try:
        config = Config()
    except ConfigError as error:
        QMessageBox.critical(None, "Problem mit der Konfigurationsdatei", str(error))
        return 1

    window = MainWindow(config)
    window.show()

    # an excel file can be given as argument; --smoke-test checks the app and closes it again
    paths = [argument for argument in sys.argv[1:] if not argument.startswith("--")]
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

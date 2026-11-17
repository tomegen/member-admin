import os

from PySide6.QtCore import QSettings, QStandardPaths, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QMessageBox


# ask where to save, write the file with write(path) and tell the user; returns the path or None
def save_file(parent, default_name, file_filter, write):
    settings = QSettings()
    folder = settings.value("save_dir") or QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DocumentsLocation)
    path, _ = QFileDialog.getSaveFileName(parent, "Speichern unter", os.path.join(folder, default_name), file_filter)
    if not path:
        return None
    try:
        write(path)
    except Exception as error:
        QMessageBox.critical(parent, "Speichern nicht möglich",
                             "Die Datei konnte nicht gespeichert werden.\n"
                             "Ist sie eventuell noch in einem anderen Programm geöffnet?\n\n" + str(error))
        return None
    settings.setValue("save_dir", os.path.dirname(path))
    box = QMessageBox(parent)
    box.setWindowTitle("Datei erstellt")
    box.setText("Die Datei wurde gespeichert:\n" + path)
    open_button = box.addButton("Ordner öffnen", QMessageBox.ButtonRole.ActionRole)
    box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
    box.exec()
    if box.clickedButton() is open_button:
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))
    return path

import io
import os
import uuid
import warnings
from collections import namedtuple
from datetime import datetime

from openpyxl import load_workbook

from model import schema
from model.club_file import file_hash, read_bytes
from store.backups import write_backup
from store.changes import append_log
from store.errors import FileLocked, SaveError
from store.repair import repair
from store.sheet import MemberSheet

ATTEMPTS = 3

Saved = namedtuple("Saved", "hash entries backup")


# who has the file open: the lock file of Excel ("~$Datei.xlsx") or LibreOffice (".~lock.Datei.xlsx#") next to it.
# None = no lock file, "" = locked by somebody unknown. Only works on this computer (sync services skip these files)
def lock_owner(path):
    folder, name = os.path.split(os.path.abspath(path))
    for lock in ("~$" + name, "~$" + name[2:], ".~lock." + name + "#"):
        lock_path = os.path.join(folder, lock)
        if os.path.isfile(lock_path):
            return owner_in(lock_path)
    return None


def owner_in(lock_path):
    try:
        with open(lock_path, "rb") as file:
            data = file.read(512)
    except OSError:
        return ""
    if os.path.basename(lock_path).startswith(".~lock."):
        return data.decode("utf-8", "ignore").split(",")[0].strip()
    length = data[0] if data else 0   # excel: length of the user name, then the name
    return data[1:1 + length].decode("latin-1", "ignore").strip() if 0 < length < 60 else ""


def open_for_writing(data):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")   # e.g. "extension is not supported": the repair puts our checks back
        return load_workbook(io.BytesIO(data))


def to_bytes(book):
    buffer = io.BytesIO()
    book.save(buffer)
    return buffer.getvalue()


# write next to the file first, then replace it in one step: a crash or full disk never leaves half a file.
# The prefix ~$ keeps Dropbox, OneDrive and Nextcloud from uploading the temporary file
def replace_file(path, data):
    temporary = os.path.join(os.path.dirname(os.path.abspath(path)), "~$member-admin-" + uuid.uuid4().hex + ".tmp")
    try:
        with open(temporary, "wb") as file:
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    except PermissionError:
        raise FileLocked(None)   # windows: the file is open in excel, saving anyway is not possible
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


# one change as a transaction: read the file as it is now, apply change(book, members) to it, repair, write the
# change log, keep a backup, replace the file and check it. If the file changes while this runs, it starts again.
# A change without log entries changed nothing: then nothing is written
def save(path, change, editor, now=None, ignore_lock=False):
    now = now or datetime.now().replace(microsecond=0)
    if not ignore_lock:
        owner = lock_owner(path)
        if owner is not None:
            raise FileLocked(owner)
    for _ in range(ATTEMPTS):
        data = read_bytes(path)
        book = open_for_writing(data)
        members = MemberSheet(book)
        missing = [column.heading for column in schema.MEMBER_COLUMNS
                   if column.mandatory and column.field not in members.columns]
        if missing:
            raise SaveError("In der Datei fehlen diese Spalten: " + ", ".join(missing) +
                            ". Bitte die Überschriften in Excel korrigieren, dann neu einlesen.")
        repair(book, members)
        entries = change(book, members)
        if not entries:
            return Saved(file_hash(data), [], None)   # nothing changed: the shared file is not touched
        append_log(book, entries, editor, now)
        new = to_bytes(book)
        if read_bytes(path) != data:
            continue   # saved by somebody else in the meantime: once more with the newer file
        backup = write_backup(path, data, now)
        replace_file(path, new)
        if read_bytes(path) != new:
            raise SaveError("Die gespeicherte Datei konnte nicht bestätigt werden. Bitte neu einlesen und prüfen; "
                            "der vorherige Stand liegt im Ordner „Sicherungen“.")
        return Saved(file_hash(new), entries, backup)
    raise SaveError("Die Datei wurde während des Speicherns mehrmals von außen geändert. "
                    "Bitte kurz warten und noch einmal speichern.")

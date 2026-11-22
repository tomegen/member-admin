import os

from model import schema
from model.club_file import open_book, read_bytes, read_info
from model.values import to_text
from store.backups import STAMP, backup_folder


# copies of the member file in its folder: their name starts like the file (Dropbox "… (Konfliktkopie …)", OneDrive
# "…-PC-Name", Nextcloud "… (conflicted copy …)", Google "… (1)") and they have the same file id in the sheet "Info"
def conflict_copies(path, file_id):
    if not file_id:
        return []
    folder, name = os.path.split(os.path.abspath(path))
    stem = os.path.splitext(name)[0]
    found = []
    for entry in sorted(os.listdir(folder)):
        if entry == name or entry.startswith("~$") or not entry.lower().endswith(".xlsx") or not entry.startswith(stem):
            continue
        candidate = os.path.join(folder, entry)
        try:
            info = read_info(open_book(read_bytes(candidate)))
        except Exception:   # not readable (e.g. being synced right now): next time
            continue
        if to_text(info.get(schema.FILE_ID_KEY)) == file_id:
            found.append(candidate)
    return found


# a conflict copy that was compared (or is not wanted) goes to the backups next to the file
def move_to_backups(copy, now):
    folder = backup_folder(copy)
    os.makedirs(folder, exist_ok=True)
    stem = os.path.splitext(os.path.basename(copy))[0]
    target = os.path.join(folder, stem + " " + now.strftime(STAMP) + ".xlsx")
    os.replace(copy, target)
    return target

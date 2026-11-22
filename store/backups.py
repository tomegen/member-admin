import os
import re
from datetime import datetime

FOLDER = "Sicherungen"
KEEP_LATEST = 30
KEEP_MONTHS = 12   # of older backups the first of each month is kept for this many months
STAMP = "%Y-%m-%d %H%M%S"


def backup_folder(path):
    return os.path.join(os.path.dirname(os.path.abspath(path)), FOLDER)


# the state before a change goes to "Sicherungen/<name> 2026-11-22 140212.xlsx" next to the file (it is shared with
# it, so every board member can get an old state back); returns the path of the backup
def write_backup(path, data, now):
    folder = backup_folder(path)
    os.makedirs(folder, exist_ok=True)
    stem = os.path.splitext(os.path.basename(path))[0]
    target = os.path.join(folder, stem + " " + now.strftime(STAMP) + ".xlsx")
    counter = 2
    while os.path.exists(target):   # two saves within one second
        target = os.path.join(folder, stem + " " + now.strftime(STAMP) + " (" + str(counter) + ").xlsx")
        counter += 1
    with open(target, "wb") as file:
        file.write(data)
    rotate(folder, stem, now)
    return target


# backups of this file: [(time, path)], oldest first; other files in the folder are not touched
def backups_of(folder, stem):
    pattern = re.compile(re.escape(stem) + r" (\d{4}-\d{2}-\d{2} \d{6})(?: \(\d+\))?\.xlsx$")
    found = []
    for name in os.listdir(folder):
        match = pattern.match(name)
        if match:
            found.append((datetime.strptime(match.group(1), STAMP), os.path.join(folder, name)))
    return sorted(found)


# keeps the latest backups and the first one of each of the last months, removes the others
def rotate(folder, stem, now):
    found = backups_of(folder, stem)
    keep = {path for _, path in found[-KEEP_LATEST:]}
    oldest_month = (now.year * 12 + now.month - 1) - KEEP_MONTHS
    months = set()
    for time, path in found:
        month = time.year * 12 + time.month - 1
        if month > oldest_month and month not in months:
            months.add(month)
            keep.add(path)
    for _, path in found:
        if path not in keep:
            os.remove(path)

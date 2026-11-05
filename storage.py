"""
storage.py

The only module that reads or writes the class CSV. Everything else works
with Student/Roster/Group objects in memory and calls into here to persist
changes. Centralizing this means:
  - config.FIELDS is read/written from exactly one place, so it can't drift
    out of sync between "the columns we read" and "the columns we write".
  - Every write goes through the same atomic temp-file-then-replace
    pattern, so a crash mid-save can't corrupt the class roster.
"""
from collections import Counter

import csv
import os
import tempfile
from datetime import date
from typing import List

import config
from models import Group, Roster, Student


def load_roster(path: str) -> Roster:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        students = []
        room = None
        for row in reader:
            room = row["room"]
            #print(f"row: {row}")
            counts = {cat: int(row.get(cat, 0) or 0) for cat in config.CATEGORIES}
            # .get(..., "") so an older CSV that predates the qLast/bLast/
            # jLast columns loads fine — those students just show "never"
            # until the next time they're called.
            last_called = {
                cat: row.get(col, "") for cat, col in config.LAST_CALLED_FIELD.items()
            }
            students.append(
                Student(
                    id=row["id"],
                    number=row["#"],
                    name=row["Name"],
                    gender=row["Gender"],
                    group=row.get("group", ""),
                    counts=counts,
                    last_called=last_called,
                )
            )
    return Roster(room=room or "", students=students)

# 21/10/26 -- Before
# def _atomic_rewrite(path: str, row_updater) -> None:
#     """Reads `path`, passes each row dict through row_updater(row) -> row,
#     and atomically replaces the file with the updated rows. Isolating this
#     here means save_counts() and save_groups() below are each ~5 lines and
#     can't accidentally diverge in how they handle the temp file / FIELDS."""
#     directory = os.path.dirname(os.path.abspath(path)) or "."
#     fd, tmp_path = tempfile.mkstemp(dir=directory, text=True)
#     while True:
#         try:
#             with open(path, "r", encoding="utf-8-sig", newline="") as src, os.fdopen(fd, "w", newline="") as tmp:
#                 reader = csv.DictReader(src)
#                 # restval="" means an older CSV missing the qLast/bLast/jLast
#                 # columns gets them added as blanks on the first save, rather
#                 # than DictWriter raising or writing "None".
#                 writer = csv.DictWriter(tmp, fieldnames=config.FIELDS, restval="")
#                 writer.writeheader()
#                 for row in reader:
#                     writer.writerow(row_updater(row))
#             os.replace(tmp_path, path)
#             print(f"SAVED SUCCESSFULLY AT: {path}")
#         except PermissionError:
#             os.remove(tmp_path)
#             print(f"Could not save to {path} — it's probably open in Excel or another program.")

# 21/10/26 -- After
def _atomic_rewrite(path: str, row_updater) -> None:
    directory = os.path.dirname(os.path.abspath(path)) or "."
    while True:
        # New temp file on every attempt, since fdopen closes the old fd.
        fd, tmp_path = tempfile.mkstemp(dir=directory, text=True)
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as src, \
                    os.fdopen(fd, "w", newline="") as tmp:
                reader = csv.DictReader(src)
                writer = csv.DictWriter(tmp, fieldnames=config.FIELDS, restval="")
                writer.writeheader()
                for row in reader:
                    writer.writerow(row_updater(row))
            os.replace(tmp_path, path)
            #print(f"SAVED SUCCESSFULLY AT: {path}")
            break  # success, leave the loop
        except PermissionError:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            print(f"Could not save to {path} — it's probably open in Excel or another program.")
            answer = input("Close it, then press ENTER to retry (or type Q to give up): ")
            if answer.strip().upper().startswith("Q"):
                raise PermissionError(f"Save to {path} was cancelled.")


def save_counts(path: str, called: List[Student], category: str) -> None:
    """Increments `category` by 1 and stamps today's date in the matching
    last-called column, for every student in `called`."""
    #called_ids = {s.id for s in called}
    times_called = Counter(s.id for s in called)
    last_called_col = config.LAST_CALLED_FIELD[category]
    today = date.today().isoformat()

    def bump(row):
        times = times_called.get(row["id"], 0)
        if times:
            row[category] = int(row.get(category, 0) or 0) + times
            row[last_called_col] = today
        # if row["id"] in called_ids:
        #     row[category] = int(row.get(category, 0) or 0) + 1
        #     row[last_called_col] = today
        return row

    _atomic_rewrite(path, bump)


def save_groups(path: str, groups: List[Group]) -> None:
    """Writes each student's current group name back to the CSV."""
    id_to_group = {s.id: g.name for g in groups for s in g.members}

    def set_group(row):
        if row["id"] in id_to_group:
            row["group"] = id_to_group[row["id"]]
        return row

    _atomic_rewrite(path, set_group)

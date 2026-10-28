"""
grouping.py

The six ways to divide a roster into Groups, plus the handful of edit
operations (rename/add/remove/move/shuffle) used afterward. Each divider
is a pure function: students in, list[Group] out. None of them print,
prompt, or touch the CSV — that keeps groups.py-in-the-original's mix of
"decide the groups" and "ask the user questions about it" separated, so
these are trivial to test and reuse (e.g. from a future GUI) without
dragging terminal I/O along.
"""

import random
from typing import List

from models import Group, Student


def by_gender(students: List[Student]) -> List[Group]:
    girls, boys = Group("GIRLS Team"), Group("BOYS Team")
    for s in students:
        (girls if s.gender.lower().startswith("g") else boys).members.append(s)
    return [girls, boys]


def by_odd_even(students: List[Student]) -> List[Group]:
    odds, evens = Group("ODDS Team"), Group("EVENS Team")
    for s in students:
        (odds if int(s.number) % 2 else evens).members.append(s)
    return [odds, evens]


def by_sections(students: List[Student], num_groups: int) -> List[Group]:
    groups = [Group(str(i + 1)) for i in range(num_groups)]
    base, rem = divmod(len(students), num_groups)
    sizes = [base + (1 if i < rem else 0) for i in range(num_groups)]
    idx = 0
    for g, size in zip(groups, sizes):
        g.members = students[idx: idx + size]
        idx += size
        if g.members:
            g.name = f"Group {g.name} (#{g.members[0].number}-{g.members[-1].number})"
    return groups


def random_groups(students: List[Student], num_groups: int) -> List[Group]:
    groups = [Group(str(i + 1)) for i in range(num_groups)]
    shuffled = students[:]
    random.shuffle(shuffled)
    # Round-robin after a shuffle gives evenly-sized, genuinely random
    # groups in one pass — the original tried to do this with a
    # random.choice() retry loop that could spin or leave groups uneven.
    for i, s in enumerate(shuffled):
        groups[i % num_groups].members.append(s)
    return groups


def every_nth(students: List[Student], num_groups: int) -> List[Group]:
    groups = [Group(str(i + 1)) for i in range(num_groups)]
    for i, s in enumerate(students):
        groups[i % num_groups].members.append(s)
    return groups


def from_saved(students: List[Student]) -> List[Group]:
    names = sorted({s.group for s in students if s.group})
    by_name = {name: Group(name) for name in names}
    for s in students:
        if s.group in by_name:
            by_name[s.group].members.append(s)
    return list(by_name.values())


DIVIDERS = {
    "1": ("GENDERS", by_gender, False),
    "2": ("ODDS/EVENS", by_odd_even, False),
    "3": ("SECTIONS", by_sections, True),
    "4": ("RANDOM GROUPS", random_groups, True),
    "5": ("EVERY NTH STUDENT", every_nth, True),
    "6": ("PREVIOUSLY SAVED GROUPS", from_saved, False),
}


# --- Editing an existing list of groups ---

def rename(groups: List[Group], target: Group, new_name: str) -> bool:
    if any(g.name.lower() == new_name.lower() for g in groups):
        return False
    target.name = new_name
    return True


def move_student(groups: List[Group], student: Student, destination: Group) -> None:
    for g in groups:
        if student in g.members:
            g.members.remove(student)
            break
    destination.members.append(student)


def remove_student(groups: List[Group], student: Student) -> bool:
    for g in groups:
        if student in g.members:
            g.members.remove(student)
            return True
    return False


def shuffle_all(groups: List[Group]) -> None:
    for g in groups:
        random.shuffle(g.members)

"""
activities.py

Each `run_*` function here is one menu option (Questions, Books, Jeopardy,
Spinner, Groups). This is the ONLY layer that's allowed to use models,
call_queue, grouping, storage, and ui all together — everything below it
only knows about the layer directly beneath it. That means adding a new
mode is "write one new run_* function here," not "touch five files."

The footer command line (blank / absent / next / choose / save / drumroll)
that used to be duplicated with subtle differences across callers.py and
responses.py is unified into one `_handle_command()` used by every calling
mode.
"""

import random
from typing import List
from collections import Counter

import fun
import grouping
import storage
import ui
from call_queue import CallQueue
from models import Group, Roster, Student



# --- Shared command handling for any "call students one by one" mode ---

COMMAND_HELP = (
    "ENTER = call them  |  A = absent  |  N = call next person instead  |  "
    "C <name> = choose a specific student  |  R <name> = remove from called  |  D = drumroll  |  S = stop & save"
)


def _handle_command(queue: CallQueue, roster: Roster, response: str) -> str:
    """Applies one footer command to `queue`. Returns 'stop' if the calling
    loop should end now, otherwise 'continue'."""
    response = response.strip()
    upper = response.upper()

    if response == "":
        queue.call_next()
    elif upper.startswith("A"):
        student = queue.mark_absent()
        if student:
            print(f"Marked {student} absent.")
            queue.call_next()
    elif upper.startswith("N"):
        queue.defer()
    elif upper.startswith("S"):
        return "stop"
    elif upper.startswith("R"):
        if upper.startswith("REMOVE"):
            name = response[6:].strip() or ui.ask_text("Remove who? ")
        else:
            name = response[1:].strip() or ui.ask_text("Remove who? ")
        student = queue.remove(name, roster)
        if student is None:
            print(f"{name} hasn't been called yet, or matches more than one student.")
    elif upper.startswith("D"):
        for i in range(3, 0, -1):
            print(f"{i}...  DRUMROLLLLLLLLL...")
            ui.pause(0.6)
    elif upper.startswith("C"):
        print(f"")
        if upper.startswith("CHOOSE"):
            name = response[6:].strip() or ui.ask_text("Choose who? ")
        else:
            name = response[1:].strip() or ui.ask_text("Choose who? ")
        student = queue.choose(name, roster)
        if student is None:
            print(f"Couldn't find a student matching '{name}'.")
        else:
            queue.call_next()  # actually call them now that they're at the front
    else:
        print(f"'{response}' isn't a recognized command.\n{COMMAND_HELP}")

    return "continue"


def _run_calling_loop(queue: CallQueue, roster: Roster, num: int, title: str, subtitle: str, category: str) -> None:
    continue_loop = False
    while True:
        ui.numbered_box([str(s) for s in queue.called], title=title, subtitle=subtitle)
        if len(queue.called) >= num and not continue_loop:
            print(f"\nAll done! {len(queue.called)} students called for {title}.")
            if ui.ask_yes_no("Are you finished calling?"):
                break
            else:
                ui.numbered_box([str(s) for s in queue.called], title=title)
            continue_loop = True
        response = ui.ask_text(">>> ")
        if _handle_command(queue, roster, response) == "stop":
            break

    ui.transition("Wrapping up")
    ui.numbered_box([str(s) for s in queue.called], title=f"{title} (done)")


def _offer_save(path, called, category):
    if not called:
        print("Nobody was called — nothing to save.")
        return
    if not ui.ask_yes_no(f"Save these {len(called)} call(s)?"):
        return
    try:
        storage.save_counts(path, called, category)
    except PermissionError as e:
        print(e)
        return                      # failed save: don't touch memory
    ui.transition("Saving")
    for i, (s, times) in enumerate(Counter(called).items(), 1):
        before = s.count(category)
        s.record_call(category, times)
        print(f"  {i}. {s}    {category}: {before} -> {s.count(category)}")
    print(f"Saved successfully to {path}.")
    ui.pause(4)


# --- Questions / Books / Brooms / Volunteers (all the same mechanic) ---

def run_task_caller(path: str, roster: Roster, category: str, label: str, num: int, sublabel: str = None) -> None:
    queue = CallQueue(roster.students, category)
    fun.offer_countdown()
    ui.transition("Alright, here we go")
    _run_calling_loop(queue, roster, num, title=f"Calling students for {label}:", subtitle=sublabel, category=category)
    _offer_save(path, queue.called, category)
    input("Press ENTER to return to the main menu.")


# --- Jeopardy: round-robin across groups ---

def run_jeopardy(path: str, roster: Roster, num_questions: int) -> None:
    groups = run_group_maker(path, roster, return_only=True)
    if not groups:
        print("No groups to run Jeopardy with.")
        return

    for g in groups:
        random.shuffle(g.members)

    fun.offer_countdown()
    ui.transition("Alright, here we go")

    called: List[Student] = []
    round_num = 0
    asked = 0

    while asked < num_questions:
        print(f"\n--- Round {round_num + 1} ---")
        for g in groups:
            if not g.members:
                continue
            student = g.members[round_num % len(g.members)]
            last = student.last_called_display("jCount")
            response = ui.ask_text(
                f"Q{asked + 1}. {g.name} - {student}  (last called: {last})\n"
                f"[ENTER=asked, A=absent, N=skip to next teammate, S=stop] "
            )
            upper = response.strip().upper()
            if upper.startswith("S"):
                asked = num_questions
                break
            elif upper.startswith("A"):
                print(f"{student} is absent.")
                if ui.ask_yes_no(f"Remove {student} from {g.name} for today?"):
                    g.members.remove(student)
            elif upper.startswith("N"):
                print(f"Skipping to the next teammate after {student}.")
            else:
                called.append(student)
                asked += 1
            if asked >= num_questions:
                break
        round_num += 1

    ui.transition("Wrapping up")
    _offer_save(path, called, "jCount")


# --- Spinner: fast-cycling random pick, stop with an empty ENTER ---

def run_spinner(path: str, roster: Roster) -> None:
    #queue_students = roster.students[:]
    queue = CallQueue(roster.students, category="sCount")
    _run_spinner_loop(queue, roster, num=1, title="Spinning for a student...")
    

    _offer_save(path, queue.called, "qCount")

def _run_spinner_loop(queue: CallQueue, roster: Roster, num: int, title: str) -> List[Student]:
    chosen: List[Student] = []
    speed = 0.5

    print("Press ENTER to stop the spinner and lock in a name.")
    print("(Type 'faster' or 'slower' after stopping to adjust the pace.)")
    ui.pause(1)

    while True:
        i = 0
        picked = None
        while picked is None:
            student = queue._queue[i % len(queue._queue)]
            queue.called.append(student)
            ui.numbered_box([str(s) for s in queue.called], title="Spinning...")
            queue.called.pop()
            try:
                ui.pause(speed)
            except KeyboardInterrupt:
                picked = student
                queue.called.append(picked)
                break
            i += 1
        

    # while True:
    #     i = 0
    #     picked = None
    #     while picked is None:
    #         student = queue._queue[i % len(queue._queue)]
    #         ui.clear()
    #         ui.box([str(student)], title="Spinning...")
    #         try:
    #             ui.pause(speed)
    #         except KeyboardInterrupt:
    #             picked = student
    #             break
    #         i += 1
    #     chosen.append(picked)
    #     ui.box([str(picked)], title="Chosen!")
    #     again = ui.ask_text("Spin again? (Y/N, or Y-FASTER / Y-SLOWER): ").strip().upper()
    #     if again.startswith("Y-FASTER"):
    #         speed /= 2
    #     elif again.startswith("Y-SLOWER"):
    #         speed *= 2
    #     if not again.startswith("Y"):
    #         break

    # return chosen


# --- Groups ---

def run_group_maker(path: str, roster: Roster, return_only: bool = False):
    prompt = "How should the class be divided?"
    key = ui.menu({k: v[0] for k, v in grouping.DIVIDERS.items()}, prompt=prompt)
    name, divider_fn, needs_count = grouping.DIVIDERS[key]

    if needs_count:
        num_groups = ui.ask_number("How many groups? ", minimum=2)
        groups = divider_fn(roster.students, num_groups)
    else:
        groups = divider_fn(roster.students)

    ui.transition("Sorting everyone into groups")

    for s in roster.students:
        for g in groups:
            if s in g.members:
                s.group = g.name

    _display_groups(groups)

    if return_only:
        return groups

    while True:
        if not ui.ask_yes_no("Does anything need to be changed?"):
            break
        _edit_groups(groups)
        _display_groups(groups)

    if ui.ask_yes_no("Save these groups to the class roster?"):
        storage.save_groups(path, groups)
        print("Saved.")

    return groups


def _display_groups(groups: List[Group]) -> None:
    lines = []
    for g in groups:
        lines.append(str(g))
        lines.append(", ".join(str(s) for s in g.members) or "(empty)")
        lines.append("")
    ui.box(lines, title="Groups")


def _edit_groups(groups: List[Group]) -> None:
    action = ui.menu({
        "1": "Rename a group",
        "2": "Move a student to another group",
        "3": "Remove a student",
        "4": "Shuffle everyone within their group",
    })

    if action == "1":
        target = _pick_group(groups, "Which group needs renaming?")
        new_name = ui.ask_text(f"New name for {target.name}: ")
        if not grouping.rename(groups, target, new_name):
            print(f"'{new_name}' is already in use.")
    elif action == "2":
        name = ui.ask_text("Who should be moved? ")
        student = _find_in_groups(groups, name)
        if student is None:
            print(f"Couldn't find '{name}'.")
            return
        destination = _pick_group(groups, f"Move {student} to which group?")
        grouping.move_student(groups, student, destination)
    elif action == "3":
        name = ui.ask_text("Who should be removed? ")
        student = _find_in_groups(groups, name)
        if student is None or not grouping.remove_student(groups, student):
            print(f"Couldn't find '{name}'.")
    elif action == "4":
        grouping.shuffle_all(groups)


def _pick_group(groups: List[Group], prompt: str) -> Group:
    options = {str(i + 1): g.name for i, g in enumerate(groups)}
    key = ui.menu(options, prompt=prompt)
    return groups[int(key) - 1]


def _find_in_groups(groups: List[Group], name: str) -> Student:
    name = name.strip().lower()
    for g in groups:
        for s in g.members:
            if s.name.lower() == name:
                return s
    return None

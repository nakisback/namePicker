"""
main.py

The only job here is: figure out which class file to load, then loop on
the main menu and dispatch to the right activity. All the actual behavior
lives in activities.py — this file should stay short forever.
"""

import os

import config
import console_window
import storage
import ui
from activities import (
    run_group_maker,
    run_jeopardy,
    run_spinner,
    run_task_caller,
)

MENU = {
    "1": "Questions",
    "2": "Books",
    "3": "Pointer",
    "4": "Brooms",
    "5": "Volunteers",
    "6": "Groups",
    "7": "Jeopardy",
    "8": "Spinner",
    "9": "Quit",
}

TASK_LABELS = {
    "2": ("bCount", "passing out books"),
    "3": ("pCount", "story pointing"),
    "4": ("bCount", "sweeping"),
    "5": ("bCount", "doing whatever is needed"),
}


def _class_path(class_number: str) -> str:
    # Matches your original naming scheme: typing "4" loads "G2-4.csv".
    here = os.path.dirname(os.path.abspath(__file__))
    room_name = "G2-" + class_number
    return os.path.join(here, "classes", f"{room_name}.csv")


def load_class() -> tuple:
    while True:
        response = ui.ask_text("Class (e.g. 4 for G2-4): ")
        if response and response[-1] in config.CLASSES:
            path = _class_path(response[-1])
            if os.path.exists(path):
                ui.transition("Loading class")
                print(f"Loaded {path}")
                return path, storage.load_roster(path)
            print(f"Couldn't find a class file at {path}")
        else:
            print(f"'{response}' isn't a recognized class.")


def main() -> None:
    console_window.apply_window_settings()

    path, roster = load_class()
    print(f"\nLoaded {roster.room} — {len(roster.students)} students.\n")

    while True:
        choice = ui.menu(MENU, prompt="What would you like to do?")

        if choice == "9":
            break

        ui.transition("Getting things ready")

        if choice == "1":
            num = ui.ask_number("How many students to call? ")
            run_task_caller(path, roster, "qCount", "questions", num)
        elif choice in TASK_LABELS:
            category, label = TASK_LABELS[choice]
            if label == "passing out books":
                sublabel = "Make sure to only carry 1-3 books at a time!"
            else:
                sublabel = None
            num = ui.ask_number("How many students to call? ")
            run_task_caller(path, roster, category, label, num, sublabel)
        elif choice == "6":
            run_group_maker(path, roster)
        elif choice == "7":
            num = ui.ask_number("How many questions? ")
            run_jeopardy(path, roster, num)
        elif choice == "8":
            num = ui.ask_number("How many students to call? ")
            #run_task_caller(path, roster, "sCount", "spinning", num)
            run_spinner(path, roster)

        print()


if __name__ == "__main__":
    main()

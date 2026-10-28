"""
ui.py

Everything that draws to the terminal or reads a raw line of input lives
here. The rule this module follows: a function in here is given plain data
(strings, numbers, lists) and returns plain data (a string the user typed,
a chosen key) — it never reaches into a Roster, CallQueue, or Group and
changes it. That's what makes it safe to reuse the same `box()` for called
students, group listings, or a menu without the display code needing to
know what kind of object it's showing.
"""

import os
import time

import config


def clear() -> None:
    if config.CLEAR_SCREEN:
        os.system("cls" if os.name == "nt" else "clear")


def pause(seconds: float) -> None: 
    time.sleep(seconds * config.TIME_STANDARD)


def transition(message: str) -> None:
    """A small ' . . .' beat between stages (e.g. after picking a task,
    before the calling screen appears) so things don't feel like they're
    just snapping from one screen to the next."""
    print(message, end="", flush=True)
    for _ in range(config.TRANSITION_DOTS):
        pause(config.TRANSITION_DELAY)
        print(" .", end="", flush=True)
    print()
    pause(config.TRANSITION_DELAY)


def _wall() -> str:
    return config.BORDER_CHAR * config.WALL_CHARS


def _content_width() -> int:
    return config.WIDTH - (config.WALL_CHARS * 2) - (config.PADDING * 2)


def _row(text: str = "") -> str:
    width = _content_width()
    text = text[:width].ljust(width)
    pad = " " * config.PADDING
    return f"{_wall()}{pad}{text}{pad}{_wall()}"


def box(lines, title: str = None) -> None:
    """Prints a bordered box. `lines` is a list of already-short strings
    (use textwrap.wrap yourself, or pass short lines) — one per row."""
    clear()
    #print(f"config.WIDTH: {config.WIDTH}")
    border = config.BORDER_CHAR * config.WIDTH
    for _ in range(config.BORDER_ROWS):
        print(border)
    print(_row())
    if title:
        print(_row(title))
        print(_row())
    for line in lines:
        print(_row(str(line)))
    print(_row())
    for _ in range(config.BORDER_ROWS):
        print(border)


def numbered_box(items, title: str = None) -> None:
    box([f"{i + 1}. {item}" for i, item in enumerate(items)], title=title)


def menu(options: dict, prompt: str = "Please choose an option:") -> str:
    """`options` maps a short key (e.g. '1') to a description. Loops until
    the user types a valid key and returns it."""
    while True:
        print(prompt)
        for key, description in options.items():
            print(f"  {key}. {description}")
        response = input(">>> ").strip()
        if response in options:
            return response
        print(f"'{response}' isn't one of the options above.\n")


def ask_yes_no(prompt: str) -> bool:
    while True:
        response = input(f"{prompt} (Y/N): ").strip().upper()
        if response.startswith("Y"):
            return True
        if response.startswith("N"):
            return False
        print(f"'{response}' isn't a valid input.")


def ask_number(prompt: str, minimum: int = 1) -> int:
    while True:
        response = input(prompt).strip()
        if response.isdigit() and int(response) >= minimum:
            return int(response)
        print(f"'{response}' isn't a valid number >= {minimum}.")


def ask_text(prompt: str) -> str:
    return input(prompt).strip()

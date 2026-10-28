"""
config.py

All the tunable constants for the app in one place. Everything here is a
plain module-level value — other modules just do `import config` and read
`config.WIDTH`, etc. There's no getWIDTH()/getHEIGHT() layer of indirection:
it added a function call for every constant without adding any actual
flexibility (nothing ever overrode the getters), so it's simpler to drop it.
"""

import shutil

# --- Terminal box sizing ---
WIDTH = min(56, shutil.get_terminal_size().columns - 2)
#print(f"shutil.get_terminal_size().columns: {shutil.get_terminal_size().columns}")
WALL_CHARS = 4          # how many BORDER_CHAR characters make up a side wall
PADDING = 3             # spaces of padding inside the wall on each side
#BORDER_CHAR = "█"       # solid block reads as a much bolder frame than "*"
BORDER_CHAR = "*"       
BORDER_ROWS = 2         # how many top/bottom border lines to stack
CLEAR_SCREEN = False    # set True if you want the screen wiped between boxes

# --- Pacing ---
TIME_STANDARD = 0.3    # multiplier for all time.sleep() calls; 0 = instant
TRANSITION_DOTS = 3     # how many ". . ." beats to show between stages
TRANSITION_DELAY = 0.5  # seconds between each dot (x TIME_STANDARD)

# --- Windows console window styling (best-effort, see console_window.py) ---
ENABLE_WINDOW_STYLING = True
WINDOW_WIDTH_PX = 1000
WINDOW_HEIGHT_PX = 700
FONT_NAME = "Consolas"
FONT_SIZE = 36 # Originally 36 (on laptop - 1920x1080)

# --- CSV shape ---
# This is the ONE place the column layout is defined. storage.py reads and
# writes using exactly this list, so adding a column means editing one line
# here instead of hunting through save.py/namePicker.py for every hardcoded
# dict literal that repeats the field names.
#
# qLast/bLast/jLast are new: the date (YYYY-MM-DD) a student was last
# called for that category, so "last called" can be shown without having
# to scan session history. If you load an older CSV that doesn't have
# these columns yet, storage.py fills them in blank and they'll start
# getting populated the next time you save.
FIELDS = [
    "room", "id", "#", "Name", "Gender",
    "qCount", "qLast",
    "bCount", "bLast",
    "jCount", "jLast",
    "pCount", "pLast",
    "group",
]

# Which CSV columns are "call counters" that a calling activity increments,
# and their friendly label.
CATEGORIES = {
    "qCount": "questions",
    "bCount": "tasks",
    "jCount": "jeopardy",
    "pCount": "pointer",
}

# category -> the column that stores the date it was last incremented.
LAST_CALLED_FIELD = {
    "qCount": "qLast",
    "bCount": "bLast",
    "jCount": "jLast",
    "pCount": "pLast",
}

CLASSES = ["1", "2", "3", "4", "5", "6", "7"]

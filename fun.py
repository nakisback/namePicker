"""
fun.py

The purely cosmetic bits from the original display.py — the countdown
chant, the star ascii-art spinner, the SpongeBob easter egg. None of this
affects who gets called or what gets saved, so it's kept separate from
call_queue.py / activities.py on purpose: you (or a future you) should be
able to delete this whole file and the app still works correctly, just
less fun.
"""

import time

import config
import ui

STAR = r"""
@@@@@@@@@@@@@@@@@@@@@@@@@@5JJ5@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@GJ7!JP@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@BJ?. ?JB@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@&YJ:  :JJ#@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@5J~    ^JY@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@PJ!      !JP@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@BJ?        ?JB@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@&&&&&&&&###BYJ.        .JYB###&&&&&&&@@@@@@@@@@
#PYYYYJJJJJJJ?????7777^          ^777?????JJJJJYYYYYY5P#
@@#PJJ!^.....                             ......^!?JP#@@
@@@@&B5J!^                 {n}                 :!J5G&@@@@@
@@@@@@@#PY?~.                              .~?YP#@@@@@@@
@@@@@@@@@&B5J7^                          ^!J5B&@@@@@@@@@
@@@@@@@@@@@@#PY?~.                    .~?YP#@@@@@@@@@@@@
@@@@@@@@@@@@@@&GYJ:                  ^JYB&@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@BJ7                    ?J#@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@YJ:                    ^JY@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@GJ7          ::          7JB@@@@@@@@@@@@@@
@@@@@@@@@@@@@&YJ:       :~7JJ7~:       :JY&@@@@@@@@@@@@@
@@@@@@@@@@@@@PJ!     :~7JPB&&B5J7~:     7JG@@@@@@@@@@@@@
@@@@@@@@@@@@#J?.  :!?YPB&@@@@@@&BPJ7~:  .JY&@@@@@@@@@@@@
@@@@@@@@@@@@PJ!:!?YPB&@@@@@@@@@@@@&BPY?~:!JP@@@@@@@@@@@@
@@@@@@@@@@@#JJ?YP#&@@@@@@@@@@@@@@@@@@&BPY?JJ&@@@@@@@@@@@
"""


def countdown_captain(seconds: int = 5) -> None:
    """The 'Are you ready kids?' countdown with the star ascii art."""
    script = ["Are you ready kids?"]
    ui.box(script)
    ui.pause(1.5)
    script.append("Aye! Aye! Captain!")
    ui.box(script)
    ui.pause(1.5)
    script.append("OHHHHHHHHHHHHHHHH!!!!!!!!!")
    ui.box(script) 
    ui.pause(2)

    for n in range(seconds, -1, -1):
        ui.pause(1.0)
        for row in STAR.splitlines():
            time.sleep(0.01)
            print(row.format(n=n))
        #print(STAR.format(n=n))
    ui.pause(1)
    ui.clear()


def countdown_eenie() -> None:
    """The short 'eenie, meenie, miney, mo' chant — quicker than the
    captain countdown, good for when you just want a beat of suspense
    before naming someone."""
    lines = [
        "Eenie, meenie, miney, mo...",
        "Catch a tiger by its toe...",
        "If he hollers, let him go...",
        "Eenie, meenie, miney, MO!",
    ]
    shown = []
    for line in lines:
        shown.append(line)
        ui.box(shown, title="Picking...")
        ui.pause(1.0)
    ui.pause(0.5)
    ui.clear()



COUNTDOWNS = {
    "1": ("Eenie meenie miney moe", countdown_eenie),
    "2": ("Are you ready, kids?! (with ascii countdown)", countdown_captain),
}


def offer_countdown() -> None:
    """Asks the teacher if they want a fun countdown before calling
    starts, and runs whichever one they pick."""
    if not ui.ask_yes_no("Want a fun countdown before we start calling?"):
        return
    # choice = ui.menu(
    #     {k: v[0] for k, v in COUNTDOWNS.items()}, prompt="Which countdown?"
    # )
    #COUNTDOWNS[choice][1]()
    countdown_captain()

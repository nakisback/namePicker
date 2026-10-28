"""
console_window.py

Best-effort, Windows-only styling of the console window itself: centers a
windowed (non-maximized) console on screen and sets a larger font size,
per config.py (WINDOW_WIDTH_PX / WINDOW_HEIGHT_PX / FONT_NAME / FONT_SIZE).

This is isolated in its own module and wrapped in try/except for two
reasons:
  1. There's no cross-platform way to resize/reposition/refont a terminal
     from Python — it's a Windows Console API thing. On macOS/Linux this
     just quietly does nothing.
  2. Even on Windows, this only works against the classic console host
     (conhost.exe — what you get from cmd.exe or a plain "python main.py"
     double-click / shortcut). If you're running inside Windows Terminal
     (the default terminal app on Windows 11), Windows Terminal owns the
     window and font itself and these legacy APIs mostly won't apply —
     in that case, set the font size and starting window size directly
     in Windows Terminal's own settings instead.

Either way, a failure here should never take down the app, so
apply_window_settings() swallows any exception.
"""

import ctypes
import os

import config


def apply_window_settings() -> None:
    if os.name != "nt" or not config.ENABLE_WINDOW_STYLING:
        return
    try:
        _resize_and_center()
    except Exception:
        pass
    try:
        _set_font()
    except Exception:
        pass


def _resize_and_center() -> None:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    hwnd = kernel32.GetConsoleWindow()
    if not hwnd:
        return

    SM_CXSCREEN, SM_CYSCREEN = 0, 1
    screen_w = user32.GetSystemMetrics(SM_CXSCREEN)
    screen_h = user32.GetSystemMetrics(SM_CYSCREEN)

    w, h = config.WINDOW_WIDTH_PX, config.WINDOW_HEIGHT_PX
    x = max(0, (screen_w - w) // 2)
    y = max(0, (screen_h - h) // 2)

    SW_RESTORE = 9  # un-maximize first, or MoveWindow won't visibly apply
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.MoveWindow(hwnd, x, y, w, h, True)


def _set_font() -> None:
    kernel32 = ctypes.windll.kernel32
    STD_OUTPUT_HANDLE = -11
    handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    class COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    class CONSOLE_FONT_INFOEX(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("nFont", ctypes.c_ulong),
            ("dwFontSize", COORD),
            ("FontFamily", ctypes.c_uint),
            ("FontWeight", ctypes.c_uint),
            ("FaceName", ctypes.c_wchar * 32),
        ]

    FF_MODERN_FIXED_PITCH = 0x31  # FF_MODERN (0x30) | FIXED_PITCH (0x01)
    FW_NORMAL = 400

    font = CONSOLE_FONT_INFOEX()
    font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
    font.nFont = 0
    font.dwFontSize = COORD(0, config.FONT_SIZE)
    font.FontFamily = FF_MODERN_FIXED_PITCH
    font.FontWeight = FW_NORMAL
    font.FaceName = config.FONT_NAME

    kernel32.SetCurrentConsoleFontEx(handle, False, ctypes.byref(font))

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

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class SMALL_RECT(ctypes.Structure):
    _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short),
                ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def apply_window_settings() -> None:
    if os.name != "nt" or not config.ENABLE_WINDOW_STYLING:
        return
    # Windows Terminal owns its own window; the legacy APIs break it.
    if os.environ.get("WT_SESSION"):
        return
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
    try:
        _set_font()           # 1st: font
    except Exception:
        pass
    try:
        _set_size()           # 2nd: size (in letters)
    except Exception:
        pass
    try:
        _center()             # 3rd: center it
    except Exception:
        pass


def _set_size() -> None:
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)

    # Ask Windows: with this font, what's the biggest window that fits?
    kernel32.GetLargestConsoleWindowSize.restype = ctypes.c_uint32
    largest = kernel32.GetLargestConsoleWindowSize(handle)
    max_cols = largest & 0xFFFF
    max_lines = (largest >> 16) & 0xFFFF

    cols = min(config.CONSOLE_COLS, max_cols)
    lines = min(config.CONSOLE_LINES, max_lines)

    # a) shrink the window to tiny so Windows lets us change the buffer
    kernel32.SetConsoleWindowInfo(handle, True, ctypes.byref(SMALL_RECT(0, 0, 0, 0)))
    # b) set the buffer: our width, 3000 lines of scroll-back
    kernel32.SetConsoleScreenBufferSize(handle, COORD(cols, 3000))
    # c) grow the window to the size we want
    kernel32.SetConsoleWindowInfo(handle, True, ctypes.byref(SMALL_RECT(0, 0, cols - 1, lines - 1)))


def _center() -> None:
    user32 = ctypes.windll.user32
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if not hwnd:
        return

    # Measure how big the window ACTUALLY ended up
    r = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    w = r.right - r.left
    h = r.bottom - r.top

    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    x = max(0, (screen_w - w) // 2)
    y = max(0, (screen_h - h) // 2)

    # Move only — don't change the size
    SWP_NOSIZE, SWP_NOZORDER = 0x0001, 0x0004
    user32.SetWindowPos(hwnd, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER)


def _set_font() -> None:
    kernel32 = ctypes.windll.kernel32
    STD_OUTPUT_HANDLE = -11
    handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

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

import re
from dataclasses import dataclass
from typing import List

from Xlib import X
from Xlib.display import Display
from Xlib.ext.xtest import fake_input
from pyxhook import HookManager
from pyxhook.pyxhook import PyxHookKeyEvent
from xkbgroup import XKeyboard

SCANCODE_ALT_GR = 108
SCANCODE_SHIFT_L = 50
SCANCODE_BACKSPACE = 22
SCANCODE_SPACE = 65


@dataclass
class KeyEvent:
    code: int
    altgr: bool = False
    shift: bool = False


BACKSPACE = KeyEvent(code=SCANCODE_BACKSPACE)


def is_altgr(event: PyxHookKeyEvent):
    return event.Key == "[65027]"


def is_ascii(event: PyxHookKeyEvent):
    return 0x20 <= event.Ascii < 0x7F


def is_backspace(event: PyxHookKeyEvent):
    return event.Key == "BackSpace"


def is_hotkey(event: PyxHookKeyEvent):
    return event.Key == "Pause"


def is_not_space(events: List[KeyEvent], event: PyxHookKeyEvent):
    return (
        event.ScanCode != SCANCODE_SPACE
        and events
        and events[-1].code == SCANCODE_SPACE
    )


def is_shift(event: PyxHookKeyEvent):
    return event.Key.startswith("Shift")


def is_terminator(event: PyxHookKeyEvent):
    return 110 <= event.ScanCode <= 119 or event.ScanCode in (9, 23, 36)


def press(display: Display, code: int, altgr=False, shift=False):
    if altgr:
        fake_input(display, X.KeyPress, SCANCODE_ALT_GR)
    if shift:
        fake_input(display, X.KeyPress, SCANCODE_SHIFT_L)

    fake_input(display, X.KeyPress, code)
    fake_input(display, X.KeyRelease, code)

    if altgr:
        fake_input(display, X.KeyRelease, SCANCODE_ALT_GR)
    if shift:
        fake_input(display, X.KeyRelease, SCANCODE_SHIFT_L)

    display.flush()


class KeyLogger:
    def __init__(self):
        self._xkbd: XKeyboard = XKeyboard()
        self._display: Display = Display()
        self._processing: bool = False
        self._window = None

        self.altgr: bool = False
        self.shift: bool = False
        self.key_events: List[KeyEvent] = []

    def check_window(self):
        window = self._window
        self._window = self._display.get_input_focus().focus
        if window != self._window:
            self.reset()

    def key_down(self, event: PyxHookKeyEvent):
        if self._processing:
            return

        self.check_window()

        if is_hotkey(event):
            self.press()
        elif is_altgr(event):
            self.altgr = True
        elif is_shift(event):
            self.shift = True
        elif is_terminator(event):
            self.reset()
        elif is_ascii(event):
            if is_not_space(self.key_events, event):
                self.reset()
            key_event = KeyEvent(
                code=event.ScanCode, altgr=self.altgr, shift=self.shift
            )
            self.key_events.append(key_event)
        elif is_backspace(event) and self.key_events:
            self.key_events.pop()

    def key_up(self, event: PyxHookKeyEvent):
        if self._processing:
            return

        if is_altgr(event):
            self.altgr = False
        elif is_shift(event):
            self.shift = False

    def mouse_down(self, _: PyxHookKeyEvent):
        self.reset()

    def press(self):
        self._processing = True

        self._xkbd.group_num += 1

        for key in [BACKSPACE] * len(self.key_events) + self.key_events:
            press(self._display, key.code, key.altgr, key.shift)

        self._processing = False

    def reset(self):
        self.key_events = []


def main():
    hook_man = HookManager()
    hook_man.shiftablechar = re.compile(r"(?!.*)")

    key_logger = KeyLogger()

    hook_man.KeyDown = key_logger.key_down
    hook_man.KeyUp = key_logger.key_up
    hook_man.MouseAllButtonsDown = key_logger.mouse_down
    hook_man.start()

    try:
        hook_man.join()
    except KeyboardInterrupt:
        pass
    finally:
        hook_man.cancel()

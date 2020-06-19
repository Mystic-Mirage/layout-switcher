from dataclasses import dataclass


@dataclass
class KeyEvent:
    code: int
    altgr: bool = False
    shift: bool = False

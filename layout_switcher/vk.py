from collections import defaultdict

from Onboard import osk
from Onboard.utils import Modifiers, permute_mask

from .keysym import keysym

vk = osk.Virtkey()


def _is_letters(data):
    return all(len(x) <= 1 for x in data) and not all(x == "" for x in data)


def get_labels(modifiers=Modifiers.SHIFT | Modifiers.ALTGR):
    result = {}
    mods_list = permute_mask(modifiers)

    for i in range(0x100):
        labels = [
            keysym.get(label, label)
            for label in vk.labels_from_keycode(i, mods_list)
        ]

        if _is_letters(labels):
            result[i] = labels

    return result


def get_keycodes(modifiers=Modifiers.SHIFT | Modifiers.ALTGR):
    result = defaultdict(list)
    mods_list = permute_mask(modifiers)
    labels = get_labels(modifiers)

    for code in sorted(labels.keys()):
        for label, mods in zip(labels[code], mods_list):
            if label:
                result[label].append((code, mods))

    return result

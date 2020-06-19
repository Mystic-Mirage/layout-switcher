def _get_keysym():
    import re
    import os

    result = {}

    pattern = re.compile(r"XK_([A-Za-z0-9]{1,30})\s{1,30}(0x[0-9a-fA-F]{4,7})")

    for prefix in (os.environ.get("SNAP", "/"), "/"):
        path = os.path.join(prefix, "usr/include/X11/keysymdef.h")
        if os.path.exists(path):
            data = open(path).read()
            break
    else:
        return result

    for key, code in pattern.findall(data):
        code = int(code, 0x10)

        if code & 0xff00 == 0xff00:
            continue

        try:
            sym = chr(code & 0xffffff)
        except ValueError:
            continue

        if key != sym:
            result[key] = sym

    return result


keysym = _get_keysym()

def rgb_to_hsv(r: int, g: int, b: int):
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    max_val = max(r_norm, g_norm, b_norm)
    min_val = min(r_norm, g_norm, b_norm)
    diff = max_val - min_val

    v = max_val

    if max_val == 0:
        s = 0.0
    else:
        s = diff / max_val

    if diff == 0:
        h = 0.0
    else:
        if max_val == r_norm:
            h = 60 * (((g_norm - b_norm) / diff) % 6)
        elif max_val == g_norm:
            h = 60 * (((b_norm - r_norm) / diff) + 2)
        else:
            h = 60 * (((r_norm - g_norm) / diff) + 4)

    return (h, s, v)

def hsv_to_rgb(hsv):
    h, s, v = hsv
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r1, g1, b1 = c, x, 0
    elif 60 <= h < 120:
        r1, g1, b1 = x, c, 0
    elif 120 <= h < 180:
        r1, g1, b1 = 0, c, x
    elif 180 <= h < 240:
        r1, g1, b1 = 0, x, c
    elif 240 <= h < 300:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x

    r = int((r1 + m) * 255)
    g = int((g1 + m) * 255)
    b = int((b1 + m) * 255)

    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    return bytes([r, g, b])

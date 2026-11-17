"""Detailed footwear at the bottom of the legs (right-leg convention; mirrored to the left leg).

legs.shoe_style: basic | sneaker | boot | loafer        legs.shoe_palette: [upper, sole, accent]
Shoes never rise above row 96 (bottom quarter); sneakers and loafers start at the R15 foot line (106).
"""
from clothing import H, M, OUTFIT, rgba, shade

STYLES = ("basic", "sneaker", "boot", "loafer")


def _lace_x(c, x0, x1, v0, v1, col, n=4):
    step = (v1 - v0) / n
    for i in range(n):
        y = v0 + i * step
        c.line([(x0, y), (x1, y + step)], rgba(col), 0.7)
        c.line([(x1, y), (x0, y + step)], rgba(col), 0.7)


def sneaker(c, fx, up, sole, acc):
    top, st = OUTFIT["shoe_top"], OUTFIT["sole_top"]
    c.band(top, st, rgba(up))
    c.band(top, top + 1.6, rgba(shade(up, 0.75)))                             # padded collar
    for o in (0, 128):                                                         # toe cap (front) / heel counter (back)
        c.rect(o + 2, st - 6, o + 62, st, rgba(shade(up, 0.93)))
        c.line([(o + 2, st - 6), (o + 62, st - 6)], rgba(shade(up, 0.7)), 0.6)
    c.polygon([(66, st), (100, st - 9), (126, st)], rgba(acc))                 # side overlay (inner)
    c.polygon([(194, st), (222, st - 10), (254, st)], rgba(acc))               # side overlay (outer): one plain curve
    c.rect(22, top + 1, 42, st - 7, rgba(shade(up, 0.88)))                     # eyestay
    _lace_x(c, 24, 40, top + 2, st - 8, shade(acc, 0.85) if sum(acc) < 600 else shade(up, 0.55))
    c.band(st, st + 4, rgba(sole))                                             # midsole
    c.band(st + 3.2, st + 4, rgba(shade(sole, 0.75)))
    c.band(st + 4, H + M, rgba(shade(sole, 0.82)))                             # outsole
    for v in range(H + 3, H + M, 3):
        c.band(v, v + 1, rgba(shade(sole, 0.62)))                              # tread rings on the sole face
    fx["hi"].band(st + 0.4, st + 1.2, 24)
    fx["sh"].band(top + 1.6, top + 3, 26)
    fx["hi"].ellipse(32, st - 3, 12, 2.5, 20)


def boot(c, fx, up, sole, acc):
    top = 98
    st = OUTFIT["sole_top"] + 1
    c.band(top, st, rgba(up))
    c.band(top, top + 2, rgba(shade(up, 0.7)))                                 # shaft top
    c.rect(150, top - 1, 170, top + 6, rgba(shade(up, 0.85)))                  # pull tab
    c.rect(22, top + 1, 42, st - 6, rgba(shade(up, 0.9)))
    for v in range(int(top) + 3, int(st) - 6, 3):                              # eyelets + laces
        c.ellipse(23.5, v, 0.8, 0.8, rgba(acc)); c.ellipse(40.5, v, 0.8, 0.8, rgba(acc))
    _lace_x(c, 24, 40, top + 3, st - 7, shade(up, 0.55), n=6)
    c.line([(2, st - 7), (62, st - 7)], rgba(shade(up, 0.7)), 0.5)             # toe-cap stitch
    c.band(st, H + M, rgba(sole))                                              # thick lug sole
    for u in range(0, 256, 4):
        c.rect(u, st + 2, u + 2, st + 5.5, rgba(shade(sole, 0.7)))
    for v in range(H + 2, H + M, 3):
        c.band(v, v + 1.2, rgba(shade(sole, 0.6)))
    fx["hi"].line([(10, top + 6), (10, st - 2)], 22, 1.2)
    fx["sh"].band(top + 2, top + 4, 24)


def loafer(c, fx, up, sole, acc):
    top, st = OUTFIT["shoe_top"] + 4, OUTFIT["sole_top"] + 2
    c.band(top, st, rgba(up))
    c.band(top, top + 1.2, rgba(shade(up, 0.65)))
    c.rect(18, top + 1.5, 46, top + 4.5, rgba(shade(up, 0.85)))                # saddle strap
    c.rect(29, top + 2.4, 35, top + 3.6, rgba(shade(up, 0.4)))                 # strap slot
    c.line([(14, top + 5), (14, st - 1)], rgba(shade(up, 0.7)), 0.5)          # apron stitch
    c.line([(50, top + 5), (50, st - 1)], rgba(shade(up, 0.7)), 0.5)
    c.band(st, H + M, rgba(sole))
    c.rect(130, st - 2, 190, st, rgba(shade(sole, 0.9)))                       # heel
    fx["hi"].ellipse(32, st - 2, 13, 2, 26)                                    # polished toe
    fx["sh"].band(top + 1.2, top + 2.4, 22)


def basic(c, fx, up, sole, acc):
    top, st = OUTFIT["shoe_top"], OUTFIT["sole_top"]
    c.band(top, st, rgba(up))
    c.band(st, H + M, rgba(sole))
    for v in range(H + 3, H + M, 4):
        c.band(v, v + 1.2, rgba(shade(sole, 0.82)))
    c.band(top, top + 1.4, rgba(shade(up, 0.78)))
    c.rect(23, top, 41, top + 8, rgba(shade(up, 0.93)))
    for v in (top + 2.5, top + 5, top + 7.5):
        c.line([(24.5, v), (39.5, v)], rgba(shade(up, 0.6)), 0.9)
    c.rect(155, top, 165, top + 7, rgba(shade(up, 0.85)))
    fx["sh"].line([(22, top + 9), (42, top + 9)], 20, 1.5)


def draw(style, c, fx, up, sole, acc):
    {"sneaker": sneaker, "boot": boot, "loafer": loafer}.get(style, basic)(c, fx, up, sole, acc)


def shoe_top(style):
    return 98 if style == "boot" else (OUTFIT["shoe_top"] + 4 if style == "loafer" else OUTFIT["shoe_top"])

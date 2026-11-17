"""Write the original elements of the motif library: styles/references/library/<id>.json.

Every element here is an original geometric construction (no traced or copied artwork).
Public-domain elements are added separately by tools/import_public_domain.py.
Run: python tools/build_library.py   (then tools/library_sheets.py for previews and LICENSES.md)
"""
import json
import math
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "styles" / "references" / "library"
TOP5 = ["y2k", "vamp-goth", "emo", "baddie", "grunge"]
ELEMENTS = []


# ---------------------------------------------------------------- shape helpers

def P(pts, tone=0, stroke=None):
    d = {"t": "poly", "pts": [[round(x, 4), round(y, 4)] for x, y in pts], "tone": tone}
    if stroke:
        d["stroke"] = stroke
    return d


def E(c, r, tone=0, stroke=None):
    d = {"t": "ellipse", "c": [round(c[0], 4), round(c[1], 4)], "r": [round(r[0], 4), round(r[1], 4)], "tone": tone}
    if stroke:
        d["stroke"] = stroke
    return d


def L(pts, w=0.08, tone=0):
    return {"t": "line", "pts": [[round(x, 4), round(y, 4)] for x, y in pts], "w": w, "tone": tone}


def star(n, ro, ri, cx=0.0, cy=0.0, rot=0.0):
    return [(cx + math.sin(rot + i * math.pi / n) * (ro if i % 2 == 0 else ri),
             cy - math.cos(rot + i * math.pi / n) * (ro if i % 2 == 0 else ri)) for i in range(2 * n)]


def circ(cx, cy, r, n=28, ry=None, a0=0.0, a1=2 * math.pi):
    ry = ry if ry is not None else r
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def heart(cx=0.0, cy=0.0, s=1.0, n=48):
    return [(cx + s * 16 * math.sin(t) ** 3 / 17, cy + s * (-(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t)
                                                             - math.cos(4 * t)) / 17 + 0.1))
            for t in [2 * math.pi * i / n for i in range(n)]]


def mirror(right):
    """right half (x >= 0) listed top -> bottom; returns a closed symmetric polygon."""
    return right + [(-x, y) for x, y in reversed(right)]


def flipx(pts):
    return [(-x, y) for x, y in pts]


def scale(pts, s, dx=0.0, dy=0.0):
    return [(x * s + dx, y * s + dy) for x, y in pts]


def rot(pts, a, cx=0.0, cy=0.0):
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def add(eid, name, motif, styles, shapes, mood=(), size="medium", families=("decorated", "print"), symmetric=True,
        band=False):
    ELEMENTS.append({"id": eid, "name": name, "motif": motif, "styles": list(styles), "mood": list(mood),
                     "size": size, "families": list(families), "symmetric": symmetric, "band": band,
                     "source": "original", "shapes": shapes})


# ---------------------------------------------------------------- stars, sparkles, celestial

add("star-5", "Five-point star", "star", TOP5 + ["gen-z", "christmas", "athleisure", "preppy"], [P(star(5, 1, 0.42))], ["bold"], "small")
add("star-5-outline", "Outlined star", "star", TOP5 + ["gen-z", "archive"], [P(star(5, 1, 0.42), stroke=0.12)], ["minimal"], "small")
add("star-4", "Four-point star", "star", ["y2k", "baddie", "emo", "gen-z"], [P(star(4, 1, 0.3))], ["sparkly"], "small")
add("star-6", "Six-point star", "star", ["y2k", "emo", "grunge", "christmas"], [P(star(6, 1, 0.55))], ["bold"], "small")
add("star-8", "Eight-point compass star", "star", ["y2k", "grunge", "archive", "athleisure", "preppy"],
    [P(star(8, 1, 0.38)), P(star(4, 0.62, 0.22, rot=math.pi / 4), tone=1)], ["bold"], "small")
add("star-double", "Double-tone star", "star", TOP5 + ["christmas"], [P(star(5, 1, 0.42)), P(star(5, 0.55, 0.23), tone=2)], ["bold"], "small")
add("star-nautical", "Split-tone nautical star", "star", ["grunge", "emo", "baddie", "y2k", "archive"],
    [P(star(5, 1, 0.42))] + [P([(0, 0), star(5, 1, 0.42)[2 * i], star(5, 1, 0.42)[2 * i + 1]], tone=1) for i in range(5)],
    ["tattoo"], "medium")
add("star-burst", "Twelve-point burst", "star", ["y2k", "baddie", "emo", "gen-z", "athleisure"], [P(star(12, 1, 0.62))], ["loud"], "small")
add("star-shooting", "Shooting star", "star", ["y2k", "emo", "baddie", "gen-z"],
    [L([(-0.95, 0.75), (0.2, -0.05)], 0.1, 1), L([(-0.8, 0.95), (0.25, 0.15)], 0.07, 2), L([(-0.98, 0.45), (0.1, -0.2)], 0.06, 2),
     P(star(5, 0.55, 0.23, 0.38, -0.32))], ["dreamy"], "medium", symmetric=False)
add("star-cluster", "Star cluster", "star", TOP5 + ["christmas", "gen-z"],
    [P(star(5, 0.62, 0.26, -0.2, -0.15)), P(star(5, 0.36, 0.15, 0.62, -0.55)), P(star(5, 0.3, 0.13, 0.5, 0.6), tone=2)],
    ["dreamy"], "medium", symmetric=False)
add("sparkle-4", "Four-point sparkle", "sparkle", ["y2k", "baddie", "soft-girl", "christmas", "gen-z", "vamp-goth"], [P(star(4, 1, 0.2))], ["sparkly"], "small")
add("sparkle-cluster", "Sparkle cluster", "sparkle", ["y2k", "baddie", "soft-girl", "christmas", "gen-z"],
    [P(star(4, 0.8, 0.16, -0.15, 0.1)), P(star(4, 0.38, 0.08, 0.6, -0.55), tone=2), P(star(4, 0.3, 0.07, 0.55, 0.65))],
    ["sparkly"], "small", symmetric=False)
add("sparkle-twinkle", "Twinkle with rays", "sparkle", ["y2k", "baddie", "christmas", "emo"],
    [P(star(4, 1, 0.18)), P(star(4, 0.55, 0.1, rot=math.pi / 4), tone=2)], ["sparkly"], "small")
add("moon-crescent", "Crescent moon", "moon", ["vamp-goth", "y2k", "emo", "grunge", "gen-z"],
    [P(circ(0, 0, 1, 32, a0=math.pi * 0.5, a1=math.pi * 1.5) + circ(0.34, 0, 0.8, 32, a0=math.pi * 1.5, a1=math.pi * 0.5))],
    ["night"], "small", symmetric=False)
add("moon-stars", "Moon with stars", "moon", ["vamp-goth", "y2k", "emo", "gen-z", "soft-girl"],
    [P(circ(-0.25, 0, 0.8, 28, a0=math.pi * 0.5, a1=math.pi * 1.5) + circ(0.05, 0, 0.64, 28, a0=math.pi * 1.5, a1=math.pi * 0.5)),
     P(star(5, 0.3, 0.13, 0.55, -0.45), tone=2), P(star(4, 0.22, 0.05, 0.62, 0.35))], ["night"], "medium", symmetric=False)
add("moon-phases", "Moon phases row", "moon", ["vamp-goth", "emo", "y2k", "archive", "grunge"],
    [E((-0.8, 0), (0.16, 0.16), stroke=0.05), P(circ(-0.4, 0, 0.16, 16, a0=math.pi / 2, a1=3 * math.pi / 2)),
     E((-0.4, 0), (0.16, 0.16), stroke=0.05), E((0, 0), (0.18, 0.18)), E((0.4, 0), (0.16, 0.16), stroke=0.05),
     P(circ(0.4, 0, 0.16, 16, a0=-math.pi / 2, a1=math.pi / 2)), E((0.8, 0), (0.16, 0.16), stroke=0.05)],
    ["night"], "large", band=True)
add("sun-tribal", "Tribal sunburst", "sun", ["y2k", "grunge", "gen-z", "athleisure", "baddie"],
    [P(star(12, 1, 0.55)), E((0, 0), (0.45, 0.45), tone="cut"), E((0, 0), (0.32, 0.32))], ["bold"], "medium")
add("planet-ring", "Ringed planet", "planet", ["y2k", "gen-z", "emo"],
    [E((0, 0), (0.55, 0.55)), L([(x, y) for x, y in circ(0, 0.05, 1.0, 40, ry=0.28)], 0.09, 2), E((-0.18, -0.2), (0.14, 0.12), tone=2)],
    ["dreamy"], "small")
add("snowflake", "Snowflake", "snowflake", ["christmas", "soft-girl", "y2k"],
    [L([(0, 0), (math.cos(a) * 1, math.sin(a) * 1)], 0.11) for a in [i * math.pi / 3 for i in range(6)]] +
    [L([(math.cos(a) * 0.55 + math.cos(a + b) * 0.3, math.sin(a) * 0.55 + math.sin(a + b) * 0.3),
        (math.cos(a) * 0.55, math.sin(a) * 0.55)], 0.08) for a in [i * math.pi / 3 for i in range(6)] for b in (0.8, -0.8)],
    ["winter"], "small")

# ---------------------------------------------------------------- hearts

H0 = heart()
add("heart", "Heart", "heart", TOP5 + ["soft-girl", "gen-z", "christmas", "cottagecore"], [P(H0)], ["cute"], "small")
add("heart-outline", "Outlined heart", "heart", TOP5 + ["soft-girl", "gen-z"], [P(H0, stroke=0.13)], ["minimal"], "small")
add("heart-double", "Double-tone heart", "heart", ["y2k", "baddie", "soft-girl", "emo", "gen-z"], [P(H0), P(heart(0, -0.05, 0.55), tone=2)], ["cute"], "small")
add("heart-cracked", "Cracked heart", "heart", ["emo", "grunge", "vamp-goth", "baddie", "y2k"],
    [P(H0), L([(0.02, -0.55), (-0.15, -0.2), (0.12, 0.05), (-0.1, 0.35), (0.02, 0.85)], 0.11, "cut")], ["sad"], "small", symmetric=False)
WL = [(0.0, 0.0), (0.45, -0.55), (1.0, -0.75), (0.85, -0.45), (1.0, -0.4), (0.8, -0.15), (0.92, -0.05), (0.6, 0.15)]
add("heart-winged", "Winged heart", "heart", TOP5 + ["soft-girl"],
    [P(scale(WL, 0.95, 0.35, -0.05), tone=1), P(scale(flipx(WL), 0.95, -0.35, -0.05), tone=1), P(heart(0, 0, 0.62))],
    ["romantic"], "medium")
add("heart-thorns", "Heart wrapped in thorns", "heart", ["vamp-goth", "emo", "grunge", "baddie"],
    [P(heart(0, 0, 0.9)), L([(-0.95, -0.05), (-0.3, 0.3), (0.4, -0.25), (0.95, 0.15)], 0.08, 1)] +
    [P([(x - 0.06, y), (x + 0.06, y), (x + dx, y + dy)], tone=1) for x, y, dx, dy in
     [(-0.62, 0.12, -0.05, -0.18), (-0.1, 0.18, 0.02, 0.2), (0.15, -0.08, 0.0, -0.2), (0.7, 0.02, 0.05, 0.2)]],
    ["dark", "romantic"], "medium", symmetric=False)
add("heart-flaming", "Flaming heart", "heart", ["emo", "grunge", "baddie", "y2k", "vamp-goth"],
    [P([(-0.55, -0.35), (-0.5, -0.8), (-0.3, -0.55), (-0.15, -1.0), (0.05, -0.62), (0.25, -0.95), (0.35, -0.55), (0.55, -0.8), (0.55, -0.35)], tone=1),
     P(heart(0, 0.15, 0.78))], ["tattoo"], "medium")
add("heart-pierced", "Heart pierced by an ornamental dagger", "heart", ["emo", "vamp-goth", "grunge", "baddie"],
    [P(heart(0, 0.05, 0.8)), L([(-0.95, 0.85), (0.85, -0.75)], 0.09, 1), P([(0.85, -0.75), (0.98, -0.98), (0.72, -0.82)], tone=1),
     L([(-0.78, 0.55), (-0.55, 0.78)], 0.1, 2)], ["tattoo", "dark"], "medium", symmetric=False)
add("heart-stitched", "Stitched heart", "heart", ["emo", "y2k", "soft-girl", "grunge", "gen-z"],
    [P(H0)] + [L([(-0.08 + 0.0, y - 0.07), (0.08, y + 0.07)], 0.07, 2) for y in (-0.35, -0.1, 0.15, 0.4)] +
    [L([(0.08, y - 0.07), (-0.08, y + 0.07)], 0.07, 2) for y in (-0.35, -0.1, 0.15, 0.4)], ["cute"], "small")
add("heart-lock", "Heart padlock", "heart", ["soft-girl", "y2k", "baddie", "emo"],
    [L(circ(0, -0.55, 0.38, 20, a0=math.pi, a1=2 * math.pi), 0.12, 1), P(heart(0, 0.15, 0.75)),
     E((0, 0.05), (0.12, 0.12), tone="cut"), P([(-0.06, 0.08), (0.06, 0.08), (0.04, 0.38), (-0.04, 0.38)], tone="cut")],
    ["cute"], "small")
add("heart-anatomical", "Stylised anatomical heart", "heart", ["vamp-goth", "grunge", "emo"],
    [P([(-0.3, -0.55), (-0.3, -0.95), (-0.12, -0.95), (-0.12, -0.5)], tone=1), P([(0.08, -0.5), (0.1, -1.0), (0.3, -1.0), (0.28, -0.45)], tone=1),
     P([(0.35, -0.4), (0.7, -0.75), (0.82, -0.62), (0.5, -0.3)], tone=1),
     P([(-0.55, -0.45), (0.3, -0.55), (0.7, -0.2), (0.6, 0.35), (0.1, 0.95), (-0.45, 0.5), (-0.7, -0.05)]),
     L([(-0.2, -0.35), (-0.05, 0.1), (0.15, 0.45)], 0.06, 2), L([(0.3, -0.3), (0.25, 0.1)], 0.05, 2)],
    ["dark", "tattoo"], "large", families=["print"], symmetric=False)

# ---------------------------------------------------------------- butterflies, moths, wings

def wing_pair(up_r=(0.5, 0.36), lo_r=(0.34, 0.26), tone=0):
    out = []
    for k in (1, -1):
        out.append(P([(0.48 * k + math.cos(a) * up_r[0] * math.cos(-0.55 * k) - math.sin(a) * up_r[1] * math.sin(-0.55 * k),
                       -0.32 + math.cos(a) * up_r[0] * math.sin(-0.55 * k) + math.sin(a) * up_r[1] * math.cos(-0.55 * k))
                      for a in [i * math.pi / 14 for i in range(28)]], tone))
        out.append(P([(0.36 * k + math.cos(a) * lo_r[0] * math.cos(0.5 * k) - math.sin(a) * lo_r[1] * math.sin(0.5 * k),
                       0.36 + math.cos(a) * lo_r[0] * math.sin(0.5 * k) + math.sin(a) * lo_r[1] * math.cos(0.5 * k))
                      for a in [i * math.pi / 14 for i in range(28)]], tone))
    return out


add("butterfly", "Butterfly", "butterfly", ["y2k", "baddie", "soft-girl", "gen-z", "cottagecore"],
    wing_pair() + [L([(0, -0.55), (0, 0.6)], 0.12, 1)], ["dreamy"], "small")
add("butterfly-spotted", "Spotted butterfly", "butterfly", ["y2k", "baddie", "soft-girl", "emo"],
    wing_pair() + [E((0.5, -0.35), (0.14, 0.11), 2), E((-0.5, -0.35), (0.14, 0.11), 2), E((0.36, 0.38), (0.09, 0.08), 2),
                   E((-0.36, 0.38), (0.09, 0.08), 2), L([(0, -0.55), (0, 0.6)], 0.12, 1)], ["dreamy"], "small")
TW = [(0.05, -0.1), (0.4, -0.95), (0.55, -0.5), (0.95, -0.85), (0.75, -0.25), (1.0, 0.05), (0.6, 0.12), (0.8, 0.7), (0.35, 0.35), (0.12, 0.6)]
add("butterfly-tribal", "Tribal butterfly", "butterfly", ["y2k", "baddie", "grunge", "emo"],
    [P(mirror(TW)), L([(0, -0.6), (0, 0.65)], 0.1, 1)], ["tattoo", "loud"], "medium")
MOTH = [(0.08, -0.35), (0.55, -0.62), (1.0, -0.55), (0.92, -0.1), (0.62, 0.12), (0.75, 0.45), (0.38, 0.62), (0.1, 0.4)]
add("moth", "Moth", "moth", ["vamp-goth", "grunge", "emo", "archive", "cottagecore", "y2k"],
    [P(mirror(MOTH)), E((0.55, -0.3), (0.17, 0.15), 2), E((-0.55, -0.3), (0.17, 0.15), 2), E((0.55, -0.3), (0.07, 0.06), 1),
     E((-0.55, -0.3), (0.07, 0.06), 1), E((0, 0.05), (0.13, 0.5), 1), L([(-0.05, -0.42), (-0.32, -0.85)], 0.04, 1),
     L([(0.05, -0.42), (0.32, -0.85)], 0.04, 1)], ["dark", "dreamy"], "medium")
MOTH2 = [(0.08, -0.3), (0.7, -0.55), (0.95, -0.25), (0.55, 0.1), (0.42, 0.55), (0.3, 1.0), (0.12, 0.5)]
add("moth-tailed", "Long-tailed moth", "moth", ["vamp-goth", "y2k", "cottagecore", "grunge", "emo"],
    [P(mirror(MOTH2)), E((0.55, -0.22), (0.12, 0.12), 2), E((-0.55, -0.22), (0.12, 0.12), 2), E((0, 0.0), (0.11, 0.42), 1)],
    ["dreamy"], "medium")
FEATH = [(0.0, -0.1), (0.25, -0.55), (0.6, -0.85), (1.0, -0.95), (0.92, -0.62), (1.0, -0.55), (0.85, -0.3), (0.92, -0.2),
         (0.7, 0.0), (0.78, 0.12), (0.5, 0.25), (0.55, 0.38), (0.25, 0.4), (0.05, 0.2)]
add("wing-feather", "Feathered wing (right)", "wings", TOP5 + ["soft-girl", "archive"],
    [P(FEATH), L([(0.15, -0.2), (0.9, -0.82)], 0.05, 1), L([(0.12, 0.0), (0.82, -0.32)], 0.05, 1), L([(0.1, 0.18), (0.6, 0.1)], 0.05, 1),
     P([(0.2, -0.25), (0.5, -0.55), (0.45, -0.3)], tone=2)], ["romantic"], "medium", symmetric=False)
add("wings-angel", "Angel wings pair", "wings", TOP5 + ["soft-girl"],
    [P(scale(FEATH, 1, 0.06)), P(scale(flipx(FEATH), 1, -0.06)), L([(0.2, -0.2), (0.95, -0.82)], 0.05, 1),
     L([(-0.2, -0.2), (-0.95, -0.82)], 0.05, 1), L([(0.18, 0.02), (0.88, -0.32)], 0.05, 1), L([(-0.18, 0.02), (-0.88, -0.32)], 0.05, 1)],
    ["romantic"], "large")
BATW = [(0.0, -0.05), (0.35, -0.7), (0.62, -0.62), (1.0, -0.85), (0.92, -0.35), (1.0, 0.1), (0.75, -0.02), (0.6, 0.3), (0.42, 0.05), (0.25, 0.32), (0.05, 0.12)]
add("wing-bat", "Bat wing (right)", "wings", ["vamp-goth", "emo", "grunge", "baddie", "y2k"],
    [P(BATW), L([(0.05, 0.0), (0.62, -0.6)], 0.05, 1), L([(0.05, 0.02), (0.92, -0.3)], 0.05, 1), L([(0.05, 0.05), (0.6, 0.28)], 0.05, 1)],
    ["dark"], "medium", symmetric=False)
TRW = [(0.0, 0.0), (0.35, -0.35), (0.6, -0.95), (0.62, -0.45), (0.95, -0.7), (0.78, -0.2), (1.0, -0.05), (0.62, 0.08), (0.75, 0.42), (0.35, 0.2)]
add("wings-tribal", "Tribal spike wings", "wings", ["y2k", "grunge", "emo", "baddie", "vamp-goth"],
    [P(scale(TRW, 1, 0.08)), P(scale(flipx(TRW), 1, -0.08)), E((0, 0), (0.12, 0.12), 1)], ["tattoo", "loud"], "large")

# ---------------------------------------------------------------- skulls (stylised, no gore)

CRAN = [(0.0, -0.95), (0.42, -0.88), (0.72, -0.62), (0.8, -0.2), (0.7, 0.18), (0.5, 0.35), (0.48, 0.55), (0.3, 0.62)]
JAW = [(0.0, 0.55), (0.32, 0.55), (0.35, 0.85), (0.12, 0.97)]
def skull_face(cut_eye=0.22):
    return [E((-0.32, -0.12), (cut_eye, cut_eye * 1.1), "cut"), E((0.32, -0.12), (cut_eye, cut_eye * 1.1), "cut"),
            P([(0, 0.12), (0.1, 0.32), (-0.1, 0.32)], "cut")] + \
           [L([(x, 0.58), (x, 0.82)], 0.045, "cut") for x in (-0.18, -0.06, 0.06, 0.18)]


add("skull-classic", "Stylised skull", "skull", ["grunge", "emo", "vamp-goth", "baddie", "archive", "y2k"],
    [P(mirror(CRAN)), P(mirror(JAW))] + skull_face() + [P([(-0.6, -0.55), (-0.3, -0.85), (-0.45, -0.5)], tone=2)],
    ["dark", "tattoo"], "medium")
add("skull-cute", "Cute rounded skull", "skull", ["emo", "y2k", "baddie", "grunge", "gen-z"],
    [E((0, -0.2), (0.82, 0.72)), P(mirror([(0.0, 0.3), (0.45, 0.3), (0.42, 0.8), (0.0, 0.88)])),
     E((-0.32, -0.15), (0.24, 0.27), "cut"), E((0.32, -0.15), (0.24, 0.27), "cut"), E((-0.26, -0.22), (0.07, 0.07), 2),
     E((0.38, -0.22), (0.07, 0.07), 2), P([(0, 0.18), (0.09, 0.35), (-0.09, 0.35)], "cut")], ["cute", "dark"], "small")
CROWN = [(-0.6, -0.55), (-0.62, -1.0), (-0.32, -0.75), (0.0, -1.05), (0.32, -0.75), (0.62, -1.0), (0.6, -0.55)]
add("skull-crowned", "Crowned skull", "skull", ["grunge", "baddie", "emo", "vamp-goth", "y2k"],
    [P(scale(mirror(CRAN), 0.85, 0, 0.12)), P(scale(mirror(JAW), 0.85, 0, 0.12))] +
    [dict(s, pts=[[p[0] * 0.85, p[1] * 0.85 + 0.12] for p in s["pts"]]) if s["t"] != "ellipse" else
     dict(s, c=[s["c"][0] * 0.85, s["c"][1] * 0.85 + 0.12], r=[s["r"][0] * 0.85, s["r"][1] * 0.85]) for s in skull_face()] +
    [P(CROWN, tone=1), E((0, -0.82), (0.07, 0.07), 2)], ["tattoo", "loud"], "medium")
BONE = [(-0.9, -0.08), (0.9, -0.08), (0.9, 0.08), (-0.9, 0.08)]
add("skull-bones", "Skull and bones", "skull", ["grunge", "emo", "baddie", "y2k"],
    [P(rot(BONE, 0.6, 0, 0.4), tone=1), P(rot(BONE, -0.6, 0, 0.4), tone=1)] +
    [E((x, y), (0.11, 0.11), 1) for x, y in [(-0.74, -0.05), (0.74, -0.05), (-0.74, 0.86), (0.74, 0.86)]] +
    [P(scale(mirror(CRAN), 0.7, 0, -0.2)), P(scale(mirror(JAW), 0.7, 0, -0.2))] +
    [dict(s, pts=[[p[0] * 0.7, p[1] * 0.7 - 0.2] for p in s["pts"]]) if s["t"] != "ellipse" else
     dict(s, c=[s["c"][0] * 0.7, s["c"][1] * 0.7 - 0.2], r=[s["r"][0] * 0.7, s["r"][1] * 0.7]) for s in skull_face()],
    ["tattoo"], "medium")

# ---------------------------------------------------------------- roses, thorns, botanicals

def rose_head(cx, cy, r, tone_out=0):
    """Scalloped bloom with spiral petal folds (reads as a rose, not concentric rings)."""
    outer = [(cx + r * (0.92 + 0.1 * math.cos(5 * a)) * math.cos(a), cy + r * (0.86 + 0.1 * math.cos(5 * a)) * math.sin(a))
             for a in [i * 2 * math.pi / 60 for i in range(60)]]
    out = [P(outer, tone_out)]
    for k, (r0, a0, a1, w) in enumerate([(0.72, 0.3, 2.9, 0.09), (0.7, 3.4, 5.9, 0.09), (0.48, 1.2, 4.4, 0.08), (0.46, 4.6, 7.3, 0.08),
                                          (0.26, 0.0, 4.2, 0.07)]):
        out.append(L([(cx + r * r0 * math.cos(a) * (1 - 0.12 * (a - a0) / (a1 - a0)), cy + r * r0 * math.sin(a) * 0.92)
                      for a in [a0 + (a1 - a0) * i / 14 for i in range(15)]], w, 1))
    out.append(E((cx + 0.04 * r, cy - 0.04 * r), (r * 0.12, r * 0.1), 1))
    return out


LEAF = [(0.0, 0.0), (0.35, -0.18), (0.75, -0.12), (0.45, 0.12)]
add("rose-bloom", "Rose bloom", "rose", ["vamp-goth", "grunge", "baddie", "emo", "soft-girl", "cottagecore"],
    [P(scale(LEAF, 1.1, 0.35, 0.45), 1), P(scale(flipx(LEAF), 1.1, -0.35, 0.45), 1)] + rose_head(0, -0.05, 0.72),
    ["romantic", "dark"], "medium")
add("rose-stem", "Rose on a thorny stem", "rose", ["vamp-goth", "grunge", "emo", "baddie", "cottagecore"],
    rose_head(0, -0.55, 0.42) + [L([(0, -0.15), (0.06, 0.4), (-0.02, 0.98)], 0.09, 1), P(scale(LEAF, 0.8, 0.05, 0.25), 1),
                                 P(scale(flipx(LEAF), 0.7, 0.0, 0.55), 1)] +
    [P([(x, y), (x + 0.12, y - 0.05), (x + 0.03, y + 0.08)], 1) for x, y in [(0.04, 0.05), (-0.04, 0.7)]],
    ["romantic"], "medium", symmetric=False)
add("rose-bud", "Rose bud", "rose", ["soft-girl", "cottagecore", "vamp-goth", "baddie"],
    [P([(0, -0.9), (0.35, -0.55), (0.3, -0.1), (0, 0.05), (-0.3, -0.1), (-0.35, -0.55)]), P([(0, -0.75), (0.15, -0.35), (0, -0.15), (-0.12, -0.45)], 1),
     L([(0, 0.0), (0, 0.95)], 0.08, 1), P(scale(LEAF, 0.7, 0.0, 0.45), 1)], ["romantic"], "small", symmetric=False)
add("thorn-vine", "Thorn vine band", "thorns", ["vamp-goth", "grunge", "emo", "archive", "baddie"],
    [L([(-1, 0.05), (-0.6, -0.12), (-0.2, 0.1), (0.2, -0.1), (0.6, 0.12), (1, -0.05)], 0.07)] +
    [P([(x - 0.04, y), (x + 0.04, y), (x + dx, y + dy)]) for x, y, dx, dy in
     [(-0.8, -0.04, -0.03, -0.22), (-0.4, 0.0, 0.02, 0.22), (0.0, 0.0, -0.02, -0.22), (0.4, 0.0, 0.03, 0.22), (0.8, 0.04, -0.02, -0.22)]],
    ["dark"], "medium", band=True, symmetric=False)
add("thorn-branch", "Thorn branch (vertical)", "thorns", ["vamp-goth", "grunge", "emo", "archive"],
    [L([(0.05, -1), (-0.08, -0.5), (0.08, 0.0), (-0.06, 0.5), (0.04, 1)], 0.08)] +
    [P([(x, y - 0.04), (x, y + 0.04), (x + dx, y + dy)]) for x, y, dx, dy in
     [(0.0, -0.75, 0.25, -0.05), (0.0, -0.25, -0.25, -0.02), (0.02, 0.25, 0.25, 0.04), (-0.01, 0.75, -0.25, 0.0)]],
    ["dark"], "medium", symmetric=False)
add("leaf-sprig", "Leaf sprig", "leaf", ["cottagecore", "soft-girl", "preppy", "gen-z"],
    [L([(0, 0.95), (0, -0.9)], 0.06, 1)] + [P(scale(LEAF, 0.7, 0, y)) for y in (-0.6, 0.0)] + [P(scale(flipx(LEAF), 0.7, 0, y)) for y in (-0.3, 0.3)],
    ["calm"], "small", symmetric=False)
LAUREL_LEAF = [(0, 0), (0.12, -0.08), (0.28, 0), (0.12, 0.08)]
_laurel = [P(rot(scale(LAUREL_LEAF, 2.3, 0.8 * math.cos(a), 0.05 + 0.8 * math.sin(a)), a + 1.2, 0.8 * math.cos(a), 0.05 + 0.8 * math.sin(a)))
           for a in [0.62 * math.pi + i * 0.2 for i in range(5)]]
add("laurel-wreath", "Laurel wreath", "wreath", ["preppy", "archive", "athleisure", "christmas"],
    [L(circ(0, 0.05, 0.8, 20, a0=0.6 * math.pi, a1=1.45 * math.pi), 0.05, 1), L(circ(0, 0.05, 0.8, 20, a0=-0.45 * math.pi, a1=0.4 * math.pi), 0.05, 1)] +
    _laurel + [dict(s, pts=[[-x, y] for x, y in s["pts"]]) for s in _laurel],
    ["classic"], "medium")
add("daisy", "Daisy", "flower", ["y2k", "soft-girl", "cottagecore", "gen-z"],
    [E((math.cos(a) * 0.58, math.sin(a) * 0.58), (0.36, 0.36)) for a in [i * math.pi / 4 for i in range(8)]] + [E((0, 0), (0.36, 0.36), 2)],
    ["cute"], "small")
add("flower-ditsy", "Ditsy five-petal flower", "flower", ["cottagecore", "soft-girl", "gen-z", "y2k"],
    [E((math.cos(a) * 0.5, math.sin(a) * 0.5), (0.42, 0.42)) for a in [i * 2 * math.pi / 5 - math.pi / 2 for i in range(5)]] +
    [E((0, 0), (0.3, 0.3), 2)], ["cute"], "small")
add("tulip", "Tulip", "flower", ["cottagecore", "soft-girl", "preppy"],
    [P([(-0.45, -0.75), (-0.2, -0.45), (0, -0.85), (0.2, -0.45), (0.45, -0.75), (0.4, -0.15), (0, 0.05), (-0.4, -0.15)]),
     L([(0, 0.0), (0, 0.95)], 0.08, 1), P(scale(LEAF, 0.7, 0, 0.5), 1)], ["cute"], "small", symmetric=False)
add("mushroom", "Mushroom", "mushroom", ["cottagecore", "gen-z", "soft-girl", "y2k"],
    [P(circ(0, 0, 0.95, 24, ry=0.75, a0=math.pi, a1=2 * math.pi)), P([(-0.3, 0), (0.3, 0), (0.25, 0.9), (-0.25, 0.9)], 1)] +
    [E((x, y), (0.13, 0.11), 2) for x, y in [(-0.45, -0.35), (0.1, -0.55), (0.5, -0.25)]], ["cute"], "small", symmetric=False)
add("cherry", "Cherries", "cherry", ["y2k", "soft-girl", "cottagecore", "gen-z", "baddie"],
    [L([(-0.45, 0.2), (0.1, -0.9), (0.45, 0.25)], 0.08, 1), P(scale(LEAF, 0.6, 0.1, -0.85), 1), E((-0.45, 0.45), (0.42, 0.42)),
     E((0.45, 0.45), (0.42, 0.42)), E((-0.55, 0.32), (0.1, 0.09), 2), E((0.35, 0.32), (0.1, 0.09), 2)], ["cute"], "small", symmetric=False)
add("strawberry", "Strawberry", "strawberry", ["cottagecore", "soft-girl", "gen-z"],
    [P([(0, 0.95), (-0.62, 0.0), (-0.55, -0.45), (0, -0.55), (0.55, -0.45), (0.62, 0.0)]),
     P([(-0.5, -0.5), (-0.2, -0.85), (0, -0.6), (0.2, -0.85), (0.5, -0.5), (0, -0.4)], 1)] +
    [E((x, y), (0.05, 0.07), 2) for x, y in [(-0.25, -0.15), (0.2, -0.2), (0, 0.15), (-0.3, 0.3), (0.28, 0.3), (0, 0.55)]],
    ["cute"], "small")

# ---------------------------------------------------------------- bats, spiders, webs

BAT = [(0, -0.35), (0.12, -0.6), (0.2, -0.3), (0.55, -0.55), (1.0, -0.4), (0.92, 0.0), (0.72, -0.05), (0.62, 0.22), (0.42, 0.08), (0.28, 0.34), (0, 0.18)]
add("bat", "Bat", "bat", ["vamp-goth", "emo", "grunge", "y2k"], [P(mirror(BAT))], ["dark"], "small")
add("bat-detailed", "Bat with wing ribs", "bat", ["vamp-goth", "emo", "grunge", "baddie"],
    [P(mirror(BAT))] + [L([(0.15 * k, -0.1), (x * k, y)], 0.035, 1) for k in (1, -1) for x, y in [(0.55, -0.5), (0.9, -0.3), (0.62, 0.15)]] +
    [E((-0.07, -0.25), (0.035, 0.035), 2), E((0.07, -0.25), (0.035, 0.035), 2)], ["dark"], "medium")
add("bat-swarm", "Bat swarm", "bat", ["vamp-goth", "emo", "grunge", "archive"],
    [P(scale(mirror(BAT), 0.6, -0.3, 0.2)), P(scale(mirror(BAT), 0.38, 0.55, -0.45), 1), P(scale(mirror(BAT), 0.3, 0.45, 0.6))],
    ["dark"], "medium", symmetric=False)
add("spider", "Spider", "spider", ["vamp-goth", "emo", "grunge", "y2k"],
    [L([(0, 0), (k * x1, y1), (k * x2, y2)], 0.06) for k in (1, -1) for x1, y1, x2, y2 in
     [(0.45, -0.35, 0.8, -0.75), (0.5, -0.1, 0.95, -0.25), (0.5, 0.12, 0.95, 0.3), (0.42, 0.32, 0.75, 0.8)]] +
    [E((0, -0.18), (0.2, 0.18)), E((0, 0.25), (0.3, 0.36)), E((0, 0.25), (0.08, 0.14), 2)], ["dark"], "small")
add("spider-hanging", "Spider on a thread", "spider", ["vamp-goth", "emo", "grunge"],
    [L([(0, -1), (0, 0.15)], 0.03, 1)] + [L([(0, 0.45), (k * x1, 0.45 + y1), (k * x2, 0.45 + y2)], 0.045) for k in (1, -1)
                                            for x1, y1, x2, y2 in [(0.3, -0.2, 0.55, -0.45), (0.33, -0.05, 0.62, -0.1), (0.33, 0.08, 0.6, 0.22), (0.28, 0.2, 0.5, 0.5)]] +
    [E((0, 0.3), (0.13, 0.12)), E((0, 0.55), (0.2, 0.24))], ["dark"], "medium")


def web(cx, cy, r, spokes=8, rings=(0.35, 0.65, 0.95), a0=0.0, a1=2 * math.pi, w=0.035):
    out = []
    ang = [a0 + (a1 - a0) * i / spokes for i in range(spokes + (0 if abs(a1 - a0 - 2 * math.pi) < 1e-6 else 1))]
    for a in ang:
        out.append(L([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r)], w))
    for rr in rings:
        pts = []
        full = abs(a1 - a0 - 2 * math.pi) < 1e-6
        seq = ang + ([ang[0]] if full else [])
        for (p, q) in zip(seq, seq[1:]):
            x0, y0 = cx + math.cos(p) * r * rr, cy + math.sin(p) * r * rr
            x1, y1 = cx + math.cos(q) * r * rr, cy + math.sin(q) * r * rr
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            pts += [(x0, y0), (mx + (cx - mx) * 0.12, my + (cy - my) * 0.12)]
        pts.append((cx + math.cos(seq[-1]) * r * rr, cy + math.sin(seq[-1]) * r * rr))
        out.append(L(pts, w))
    return out


add("web-full", "Spider web", "web", ["vamp-goth", "emo", "grunge", "y2k", "archive"], web(0, 0, 1), ["dark"], "medium")
add("web-corner", "Corner web", "web", ["vamp-goth", "emo", "grunge", "archive"],
    web(-1, -1, 1.9, spokes=5, a0=0, a1=math.pi / 2, w=0.04), ["dark"], "medium", symmetric=False)

# ---------------------------------------------------------------- chains, wire, metal

def chain_band(y=0.0, n=9, w=2.0, link=0.13):
    out = []
    for i in range(n):
        x = -w / 2 + w * (i + 0.5) / n
        rx, ry = (w / n * 0.62, link) if i % 2 == 0 else (w / n * 0.45, link * 0.7)
        out.append(E((x, y), (rx, ry), 0 if i % 2 == 0 else 1, stroke=0.045))
    return out


add("chain-band", "Chain band", "chain", ["grunge", "emo", "baddie", "vamp-goth", "y2k", "archive"], chain_band(), ["metal"], "medium", band=True)
add("chain-drape", "Draped chain", "chain", ["grunge", "emo", "baddie", "vamp-goth", "archive"],
    [E((math.sin(a) * 0.9, 0.55 * math.cos(a) - 0.2), (0.11, 0.07) if i % 2 == 0 else (0.07, 0.1), i % 2, stroke=0.05)
     for i, a in enumerate([-1.45 + j * 2.9 / 15 for j in range(16)])], ["metal"], "medium")
add("chain-loop", "Chain ring", "chain", ["grunge", "emo", "baddie", "archive"],
    [E((math.cos(a) * 0.82, math.sin(a) * 0.82), (0.12, 0.08) if i % 2 == 0 else (0.08, 0.12), i % 2, stroke=0.05)
     for i, a in enumerate([j * 2 * math.pi / 16 for j in range(16)])], ["metal"], "medium")


def barbed(y=0.0, w=2.0, n=5):
    out = [L([(-w / 2 + w * i / 24, y + 0.06 * math.sin(i * 1.3)) for i in range(25)], 0.045),
           L([(-w / 2 + w * i / 24, y - 0.06 * math.sin(i * 1.3)) for i in range(25)], 0.045, 1)]
    for i in range(n):
        x = -w / 2 + w * (i + 0.5) / n
        out += [L([(x - 0.12, y - 0.16), (x + 0.12, y + 0.16)], 0.045), L([(x + 0.12, y - 0.16), (x - 0.12, y + 0.16)], 0.045)]
    return out


add("barbed-wire", "Barbed wire band", "barbed-wire", ["grunge", "emo", "vamp-goth", "archive", "baddie", "y2k"], barbed(), ["edgy"], "medium", band=True)
add("barbed-ring", "Barbed wire ring", "barbed-wire", ["grunge", "emo", "vamp-goth", "archive", "baddie"],
    [L(circ(0, 0, 0.82, 36), 0.045), L(circ(0, 0, 0.76, 36), 0.04, 1)] +
    [L([(math.cos(a) * 0.62, math.sin(a) * 0.62), (math.cos(a) * 1.0, math.sin(a) * 1.0)], 0.045) for a in [i * math.pi / 4 + 0.2 for i in range(8)]],
    ["edgy"], "medium")
add("barbed-heart", "Barbed wire heart", "barbed-wire", ["emo", "grunge", "baddie", "y2k", "vamp-goth"],
    [P(heart(), stroke=0.07), P(heart(0, 0, 0.9), tone=1, stroke=0.035)] +
    [L([(x - 0.1, y - 0.1), (x + 0.1, y + 0.1)], 0.045) for x, y in [(-0.7, -0.45), (0.7, -0.45), (-0.5, 0.35), (0.5, 0.35), (0, -0.3), (0, 0.85)]] +
    [L([(x + 0.1, y - 0.1), (x - 0.1, y + 0.1)], 0.045) for x, y in [(-0.7, -0.45), (0.7, -0.45), (-0.5, 0.35), (0.5, 0.35), (0, -0.3), (0, 0.85)]],
    ["edgy", "tattoo"], "medium")
add("safety-pin", "Safety pin", "pin", ["grunge", "emo", "archive"],
    [L([(-0.9, -0.12), (0.75, -0.12)], 0.1), L([(-0.75, 0.15), (0.75, 0.15)], 0.08, 1), P(circ(0.85, 0.02, 0.17, 12), stroke=0.08),
     P([(-1.0, -0.3), (-0.65, -0.3), (-0.65, 0.3), (-1.0, 0.3)])], ["punk"], "small", symmetric=False)
add("stud-row", "Pyramid stud row", "stud", ["emo", "grunge", "baddie", "y2k"],
    [P(star(4, 0.22, 0.16, x, 0, math.pi / 4)) for x in (-0.75, -0.25, 0.25, 0.75)] + [E((x, 0), (0.06, 0.06), 2) for x in (-0.75, -0.25, 0.25, 0.75)],
    ["punk"], "small", band=True)
add("gem", "Faceted gem", "gem", ["y2k", "baddie", "soft-girl", "gen-z"],
    [P([(-0.8, -0.3), (-0.45, -0.75), (0.45, -0.75), (0.8, -0.3), (0, 0.9)]), P([(-0.45, -0.75), (0, -0.3), (0.45, -0.75)], 2),
     P([(-0.8, -0.3), (0, -0.3), (0, 0.9)], 1)], ["sparkly"], "small")
add("crown", "Crown", "crown", ["baddie", "y2k", "preppy", "grunge", "emo"],
    [P([(-0.85, 0.5), (-0.95, -0.55), (-0.45, -0.05), (0, -0.75), (0.45, -0.05), (0.95, -0.55), (0.85, 0.5)]),
     P([(-0.85, 0.5), (0.85, 0.5), (0.85, 0.75), (-0.85, 0.75)], 1)] + [E((x, y), (0.1, 0.1), 2) for x, y in [(-0.95, -0.6), (0, -0.8), (0.95, -0.6)]],
    ["loud"], "small")

# ---------------------------------------------------------------- flames, lightning, tribal

FL = [(0, 1), (-0.62, 0.62), (-0.7, 0.1), (-0.45, -0.35), (-0.5, -0.75), (-0.22, -0.4), (-0.12, -1.0), (0.06, -0.48), (0.3, -0.82),
      (0.33, -0.3), (0.62, -0.5), (0.7, 0.12), (0.62, 0.62)]
add("flame", "Flame", "flame", ["y2k", "emo", "grunge", "baddie", "athleisure"], [P(FL), P(scale(FL, 0.55, 0, 0.35), 2)], ["loud"], "small", symmetric=False)
add("flame-band", "Flame band", "flame", ["y2k", "emo", "grunge", "baddie"],
    [P([(-1, 0.5)] + [pt for i in range(7) for pt in [(-1 + (i + 0.15) * 2 / 7, 0.1 - 0.25 * (i % 2)),
                                                      (-1 + (i + 0.5) * 2 / 7, -0.75 + 0.3 * ((i * 3) % 2)),
                                                      (-1 + (i + 0.85) * 2 / 7, 0.05)]] + [(1, 0.5)]),
     P([(-1, 0.5), (1, 0.5), (1, 0.32), (-1, 0.32)], 1)], ["loud"], "medium", band=True, symmetric=False)
TF = [(0.0, 1.0), (-0.4, 0.55), (-0.25, 0.15), (-0.6, -0.15), (-0.2, -0.25), (-0.35, -0.75), (0.05, -0.4), (0.15, -1.0),
      (0.3, -0.35), (0.6, -0.6), (0.45, -0.05), (0.55, 0.45)]
add("flame-tribal", "Tribal flame", "flame", ["y2k", "grunge", "emo", "baddie"], [P(TF), P(scale(TF, 0.5, 0.0, 0.3), 2)], ["tattoo", "loud"], "medium", symmetric=False)
add("flame-ring", "Ring of flames", "flame", ["emo", "grunge", "y2k", "baddie"],
    [P([(math.cos(a) * (0.95 if i % 2 == 0 else 0.7), math.sin(a) * (0.95 if i % 2 == 0 else 0.7)) for i, a in enumerate([j * math.pi / 10 for j in range(20)])]),
     E((0, 0), (0.6, 0.6), "cut")], ["loud"], "medium")
BOLT = [(0.15, -1), (-0.45, 0.1), (-0.05, 0.1), (-0.25, 1), (0.45, -0.2), (0.05, -0.2), (0.3, -1)]
add("lightning", "Lightning bolt", "lightning", ["emo", "athleisure", "grunge", "y2k", "gen-z"], [P(BOLT)], ["loud"], "small", symmetric=False)
add("lightning-double", "Double bolt", "lightning", ["emo", "athleisure", "grunge", "y2k"],
    [P(scale(BOLT, 0.75, -0.35, 0)), P(scale(BOLT, 0.75, 0.35, 0.1), 1)], ["loud"], "small", symmetric=False)
SP = [(0.0, -0.15), (0.2, -0.9), (0.35, -0.2), (0.6, -0.75), (0.65, -0.1), (1.0, -0.35), (0.85, 0.15), (0.0, 0.15)]
add("tribal-spikes", "Tribal spike band", "tribal", ["y2k", "grunge", "emo", "baddie", "athleisure"], [P(mirror(SP))], ["tattoo", "loud"], "medium", band=True)
add("tribal-armband", "Tribal armband swirl", "tribal", ["y2k", "grunge", "baddie", "emo"],
    [P([(-1, 0.1), (-0.7, -0.3), (-0.45, 0.05), (-0.2, -0.55), (0.0, -0.1), (0.2, -0.55), (0.45, 0.05), (0.7, -0.3), (1, 0.1),
        (0.65, 0.0), (0.45, 0.35), (0.2, 0.05), (0.0, 0.42), (-0.2, 0.05), (-0.45, 0.35), (-0.65, 0.0)])], ["tattoo"], "medium", band=True)

# ---------------------------------------------------------------- ornament, gothic, objects

def scroll(cx, cy, s, k=1):
    return L([(cx + k * s * (0.0 + 0.6 * t * math.cos(5 * t)), cy + s * 0.6 * t * math.sin(5 * t)) for t in [i / 20 for i in range(21)]], 0.05)


add("filigree-scroll", "Filigree scroll band", "filigree", ["vamp-goth", "baddie", "preppy", "archive"],
    [L([(-1, 0), (1, 0)], 0.05)] + [scroll(x, -0.05 if i % 2 else 0.05, 0.45, 1 if i % 2 else -1) for i, x in enumerate((-0.75, -0.25, 0.25, 0.75))],
    ["ornate"], "medium", band=True, symmetric=False)
add("filigree-corner", "Filigree corner", "filigree", ["vamp-goth", "baddie", "archive", "preppy"],
    [L([(-1, -1), (0.6, -1)], 0.05), L([(-1, -1), (-1, 0.6)], 0.05), scroll(-0.4, -0.55, 0.9), scroll(-0.65, -0.3, 0.6, -1),
     E((-0.85, -0.85), (0.1, 0.1), 1)], ["ornate"], "medium", symmetric=False)
add("damask-medallion", "Damask medallion", "filigree", ["vamp-goth", "baddie", "preppy", "archive"],
    [P([(0, -1), (0.35, -0.45), (0.65, 0), (0.35, 0.45), (0, 1), (-0.35, 0.45), (-0.65, 0), (-0.35, -0.45)]),
     P([(0, -0.6), (0.2, -0.25), (0.38, 0), (0.2, 0.25), (0, 0.6), (-0.2, 0.25), (-0.38, 0), (-0.2, -0.25)], "cut"),
     P(star(4, 0.32, 0.12), 1), L([(0.65, 0), (0.95, -0.25), (0.85, -0.45)], 0.06), L([(-0.65, 0), (-0.95, -0.25), (-0.85, -0.45)], 0.06),
     L([(0.65, 0), (0.95, 0.25), (0.85, 0.45)], 0.06), L([(-0.65, 0), (-0.95, 0.25), (-0.85, 0.45)], 0.06)], ["ornate"], "medium")
add("filigree-frame", "Oval filigree frame", "filigree", ["vamp-goth", "baddie", "archive", "soft-girl"],
    [E((0, 0), (0.62, 0.85), stroke=0.08), E((0, 0), (0.52, 0.75), 1, stroke=0.04)] +
    [scroll(0.62, y, 0.4) for y in (-0.3, 0.3)] + [scroll(-0.62, y, 0.4, -1) for y in (-0.3, 0.3)] +
    [P(star(4, 0.16, 0.06, 0, -0.95), 2), P(star(4, 0.16, 0.06, 0, 0.95), 2)], ["ornate"], "large", families=["print"])
add("chandelier", "Chandelier", "chandelier", ["vamp-goth", "baddie", "archive"],
    [L([(0, -1), (0, -0.35)], 0.05, 1), E((0, -0.3), (0.16, 0.12)), L([(-0.8, 0.05), (-0.4, 0.2), (0, 0.1), (0.4, 0.2), (0.8, 0.05)], 0.07),
     L([(-0.55, -0.05), (-0.25, 0.3), (0, 0.25), (0.25, 0.3), (0.55, -0.05)], 0.05, 1)] +
    [P([(x - 0.06, 0.05), (x + 0.06, 0.05), (x + 0.06, -0.3), (x - 0.06, -0.3)], 2) for x in (-0.8, -0.4, 0.0, 0.4, 0.8)] +
    [P(scale(FL, 0.1, x, -0.42)) for x in (-0.8, -0.4, 0.0, 0.4, 0.8)] +
    [P([(x - 0.05, 0.45), (x, 0.65), (x + 0.05, 0.45)], 1) for x in (-0.5, -0.2, 0.2, 0.5)], ["ornate", "dark"], "large", families=["print"])
add("candle", "Dripping candle", "candle", ["vamp-goth", "grunge", "archive", "christmas"],
    [P([(-0.25, -0.35), (0.25, -0.35), (0.25, 0.85), (-0.25, 0.85)]), P([(-0.25, -0.35), (-0.25, -0.05), (-0.15, 0.1), (-0.05, -0.1), (0.05, 0.2),
                                                                           (0.12, -0.05), (0.25, 0.0), (0.25, -0.35)], 2),
     P(scale(FL, 0.28, 0, -0.65)), P([(-0.45, 0.85), (0.45, 0.85), (0.4, 1.0), (-0.4, 1.0)], 1)], ["dark", "ornate"], "small", symmetric=False)
add("candelabra", "Candelabra", "candle", ["vamp-goth", "archive", "baddie"],
    [L([(0, 1), (0, -0.2)], 0.08), L([(-0.7, -0.35), (-0.7, 0.05), (-0.35, 0.3), (0, 0.3), (0.35, 0.3), (0.7, 0.05), (0.7, -0.35)], 0.07),
     P([(-0.35, 0.95), (0.35, 0.95), (0.25, 0.8), (-0.25, 0.8)], 1)] +
    [P([(x - 0.08, -0.3), (x + 0.08, -0.3), (x + 0.08, -0.7), (x - 0.08, -0.7)], 2) for x in (-0.7, 0.0, 0.7)] +
    [P(scale(FL, 0.13, x, -0.85)) for x in (-0.7, 0.0, 0.7)], ["ornate", "dark"], "medium", families=["print"])
add("key-ornate", "Ornate key", "key", ["vamp-goth", "archive", "cottagecore", "emo"],
    [P(circ(0, -0.62, 0.32, 18), stroke=0.1), P(star(4, 0.2, 0.08, 0, -0.62), 1), L([(0, -0.3), (0, 0.95)], 0.1),
     P([(0, 0.6), (0.3, 0.6), (0.3, 0.72), (0.18, 0.72), (0.18, 0.85), (0, 0.85)]), P([(0, 0.35), (0.22, 0.35), (0.22, 0.47), (0, 0.47)])],
    ["ornate"], "small", symmetric=False)
add("key-skeleton", "Skeleton key", "key", ["vamp-goth", "archive", "grunge", "emo"],
    [P(scale(mirror([(0.0, -0.95), (0.3, -0.85), (0.35, -0.55), (0.12, -0.42)]), 1), stroke=0.1), L([(0, -0.42), (0, 0.95)], 0.1),
     P([(0, 0.55), (0.35, 0.55), (0.35, 0.95), (0, 0.95)], 1)], ["ornate"], "small", symmetric=False)
# dagger: drawn on a diagonal with downswept curved quillons and a ring pommel, so it never reads as a cross
_DAG = [P([(0, 1), (-0.13, 0.12), (0.0, 0.02), (0.13, 0.12)]), L([(0, 0.92), (0, 0.18)], 0.03, 2),
        L([(-0.42, 0.28), (-0.3, 0.08), (-0.1, 0.0), (0.1, 0.0), (0.3, 0.08), (0.42, 0.28)], 0.09, 1),
        P([(-0.07, 0.0), (0.07, 0.0), (0.08, -0.55), (-0.08, -0.55)], 1),
        L([(-0.08, -0.12), (0.08, -0.2)], 0.035, 2), L([(-0.08, -0.3), (0.08, -0.38)], 0.035, 2),
        E((0, -0.72), (0.17, 0.17), 0, stroke=0.08)]


def _rot_shapes(shapes, a):
    out = []
    for s in shapes:
        s = dict(s)
        if "pts" in s:
            s["pts"] = [list(p) for p in rot([tuple(p) for p in s["pts"]], a)]
        if "c" in s:
            s["c"] = list(rot([tuple(s["c"])], a)[0])
        out.append(s)
    return out


add("dagger-ornate", "Ornamental dagger (diagonal, curved guard)", "dagger", ["vamp-goth", "emo", "grunge", "archive"],
    _rot_shapes(_DAG, 0.62), ["ornate", "dark"], "medium", symmetric=False)
ARCH = [(0.0, -1.0), (0.3, -0.75), (0.5, -0.35), (0.55, 0.05), (0.55, 1.0)]
add("gothic-window", "Gothic window tracery", "gothic", ["vamp-goth", "archive", "grunge"],
    [P(mirror(ARCH), stroke=0.06), L([(0, -0.15), (0, 1.0)], 0.05), P(circ(0, -0.42, 0.24, 20), stroke=0.05, tone=1)] +
    [P(circ(x, -0.02, 0.17, 10, a0=math.pi, a1=2 * math.pi) + [(x + 0.17, 1.0), (x - 0.17, 1.0)], stroke=0.04, tone=1) for x in (-0.27, 0.27)] +
    [E((math.cos(a) * 0.13, -0.42 + math.sin(a) * 0.13), (0.07, 0.07), 2) for a in [i * 2 * math.pi / 3 - math.pi / 2 for i in range(3)]],
    ["ornate", "dark"], "large", families=["print"])
add("gothic-rosette", "Gothic rosette (six-petal tracery)", "gothic", ["vamp-goth", "archive"],
    [E((0, 0), (0.95, 0.95), stroke=0.07)] + [E((math.cos(a) * 0.5, math.sin(a) * 0.5), (0.42, 0.42), 1, stroke=0.045)
                                            for a in [i * math.pi / 3 for i in range(6)]] + [E((0, 0), (0.18, 0.18), 2)],
    ["ornate"], "medium")

# ---------------------------------------------------------------- y2k / gen-z / misc objects

add("alien-head", "Alien head", "alien", ["y2k", "emo", "gen-z", "grunge"],
    [P(mirror([(0.0, -0.95), (0.55, -0.82), (0.82, -0.35), (0.6, 0.35), (0.25, 0.85), (0.0, 0.95)])),
     P(rot(scale([(-0.3, 0), (0.0, -0.18), (0.3, 0), (0.0, 0.14)], 1, -0.38, -0.05), 0.5, -0.38, -0.05), "cut"),
     P(rot(scale([(-0.3, 0), (0.0, -0.18), (0.3, 0), (0.0, 0.14)], 1, 0.38, -0.05), -0.5, 0.38, -0.05), "cut")], ["weird"], "small")
add("bow", "Bow", "bow", ["soft-girl", "cottagecore", "y2k", "baddie", "christmas"],
    [P([(0, 0), (-0.95, -0.62), (-1.05, 0.0), (-0.9, 0.6)]), P([(0, 0), (0.95, -0.62), (1.05, 0.0), (0.9, 0.6)]),
     P([(-0.08, 0.1), (-0.5, 0.95), (-0.28, 1.0), (0.02, 0.25)], 1), P([(0.08, 0.1), (0.5, 0.95), (0.28, 1.0), (-0.02, 0.25)], 1),
     E((0, 0), (0.2, 0.24), 2)], ["cute"], "small")
add("bow-ribbon", "Long-tail ribbon bow", "bow", ["soft-girl", "cottagecore", "baddie", "y2k", "preppy"],
    [P([(0, 0), (-0.8, -0.5), (-0.85, 0.05), (-0.7, 0.4)]), P([(0, 0), (0.8, -0.5), (0.85, 0.05), (0.7, 0.4)]),
     L([(-0.05, 0.1), (-0.35, 0.55), (-0.2, 0.98)], 0.1, 1), L([(0.05, 0.1), (0.35, 0.55), (0.2, 0.98)], 0.1, 1), E((0, 0), (0.18, 0.2), 2)],
    ["cute"], "small")
add("lace-doily", "Lace doily", "lace", ["soft-girl", "cottagecore", "vamp-goth"],
    [E((math.cos(a) * 0.82, math.sin(a) * 0.82), (0.2, 0.2)) for a in [i * math.pi / 8 for i in range(16)]] +
    [E((0, 0), (0.82, 0.82)), E((0, 0), (0.55, 0.55), "cut")] + [E((math.cos(a) * 0.68, math.sin(a) * 0.68), (0.05, 0.05), "cut") for a in [i * math.pi / 8 for i in range(16)]] +
    [P(star(6, 0.35, 0.18), 1)], ["cute", "ornate"], "medium")
add("bunny-head", "Bunny head", "bunny", ["soft-girl", "y2k", "cottagecore"],
    [E((-0.28, -0.55), (0.16, 0.45)), E((0.28, -0.55), (0.16, 0.45)), E((0, 0.3), (0.6, 0.5)), E((-0.28, -0.55), (0.07, 0.3), 2),
     E((0.28, -0.55), (0.07, 0.3), 2), E((-0.22, 0.22), (0.06, 0.07), "cut"), E((0.22, 0.22), (0.06, 0.07), "cut")], ["cute"], "small")
add("anchor", "Anchor", "anchor", ["preppy", "grunge", "archive"],
    [P(circ(0, -0.78, 0.17, 14), stroke=0.08), L([(0, -0.6), (0, 0.85)], 0.11), L([(-0.38, -0.35), (0.38, -0.35)], 0.09),
     L(circ(0, 0.25, 0.65, 16, a0=0.15 * math.pi, a1=0.85 * math.pi), 0.11), P([(0.62, 0.42), (0.85, 0.32), (0.66, 0.6)]),
     P([(-0.62, 0.42), (-0.85, 0.32), (-0.66, 0.6)])], ["classic"], "small")
add("sailboat", "Sailboat", "boat", ["preppy", "gen-z"],
    [P([(0.05, -0.95), (0.05, 0.4), (0.75, 0.4)]), P([(-0.05, -0.6), (-0.05, 0.4), (-0.6, 0.4)], 2),
     P([(-0.85, 0.5), (0.85, 0.5), (0.6, 0.85), (-0.6, 0.85)], 1)], ["classic"], "small", symmetric=False)
add("tennis-racket", "Tennis racket", "sport", ["preppy", "athleisure"],
    [E((0, -0.35), (0.48, 0.6), stroke=0.1)] + [L([(x, -0.9), (x, 0.2)], 0.025, 1) for x in (-0.24, 0.0, 0.24)] +
    [L([(-0.45, y), (0.45, y)], 0.025, 1) for y in (-0.6, -0.35, -0.1)] + [L([(0, 0.25), (0, 0.98)], 0.13)], ["classic"], "small")
add("rosette-ribbon", "Prize rosette", "rosette", ["preppy", "soft-girl", "athleisure"],
    [P([(-0.3, 0.3), (-0.55, 1.0), (-0.3, 0.88), (-0.1, 1.0), (0.05, 0.3)], 1), P([(0.3, 0.3), (0.55, 1.0), (0.3, 0.88), (0.1, 1.0), (-0.05, 0.3)], 1),
     P(star(14, 0.62, 0.5, 0, -0.15)), E((0, -0.15), (0.32, 0.32), 2)], ["classic"], "small")
add("argyle-diamond", "Argyle diamond", "diamond", ["preppy", "archive", "gen-z"],
    [P([(0, -1), (0.6, 0), (0, 1), (-0.6, 0)]), L([(-0.6, -1), (0.6, 1)], 0.04, 2), L([(0.6, -1), (-0.6, 1)], 0.04, 2)], ["classic"], "small")
add("holly", "Holly sprig", "holly", ["christmas", "cottagecore"],
    [P([(0, 0), (-0.35, -0.35), (-0.55, -0.25), (-0.7, -0.5), (-0.95, -0.35), (-0.75, -0.1), (-0.5, 0.05)]),
     P([(0, 0), (0.35, -0.35), (0.55, -0.25), (0.7, -0.5), (0.95, -0.35), (0.75, -0.1), (0.5, 0.05)]),
     E((-0.12, 0.15), (0.18, 0.18), 1), E((0.15, 0.2), (0.18, 0.18), 1), E((0, -0.08), (0.18, 0.18), 1)], ["festive"], "small", symmetric=False)
add("candy-cane", "Candy cane", "candy", ["christmas"],
    [L([(-0.2, 0.95), (-0.2, -0.45)] + circ(0.15, -0.45, 0.35, 14, a0=math.pi, a1=2 * math.pi), 0.22)] +
    [L([(-0.2, y), (-0.2, y + 0.12)], 0.22, 2) for y in (0.75, 0.45, 0.15, -0.15)], ["festive"], "small", symmetric=False)
add("gift-box", "Gift box", "gift", ["christmas", "soft-girl"],
    [P([(-0.75, -0.25), (0.75, -0.25), (0.75, 0.9), (-0.75, 0.9)]), P([(-0.12, -0.25), (0.12, -0.25), (0.12, 0.9), (-0.12, 0.9)], 2),
     P([(-0.85, -0.45), (0.85, -0.45), (0.85, -0.2), (-0.85, -0.2)], 1), P([(0, -0.45), (-0.5, -0.9), (-0.6, -0.55)], 2), P([(0, -0.45), (0.5, -0.9), (0.6, -0.55)], 2)],
    ["festive"], "small")
add("ornament-ball", "Ornament bauble", "bauble", ["christmas"],
    [E((0, 0.2), (0.75, 0.75)), P([(-0.2, -0.62), (0.2, -0.62), (0.2, -0.45), (-0.2, -0.45)], 1), L(circ(0, -0.72, 0.12, 10), 0.05, 1),
     L([(-0.72, 0.1), (-0.3, 0.25), (0, 0.1), (0.3, 0.25), (0.72, 0.1)], 0.07, 2), E((-0.3, -0.1), (0.12, 0.1), 2)], ["festive"], "small")
add("pine-tree", "Pine tree", "tree", ["christmas", "cottagecore"],
    [P([(0, -1), (0.45, -0.4), (0.25, -0.4), (0.65, 0.2), (0.35, 0.2), (0.8, 0.75), (-0.8, 0.75), (-0.35, 0.2), (-0.65, 0.2), (-0.25, -0.4), (-0.45, -0.4)]),
     P([(-0.12, 0.75), (0.12, 0.75), (0.12, 1.0), (-0.12, 1.0)], 1), P(star(5, 0.18, 0.08, 0, -0.98), 2)], ["festive"], "small")
add("bell", "Bell", "bell", ["christmas"],
    [P([(-0.7, 0.55), (-0.5, -0.15), (-0.35, -0.6), (0, -0.75), (0.35, -0.6), (0.5, -0.15), (0.7, 0.55)]), E((0, 0.68), (0.16, 0.16), 1),
     P(circ(0, -0.82, 0.12, 10), stroke=0.06), L([(-0.35, 0.15), (-0.25, -0.35)], 0.06, 2)], ["festive"], "small")
add("gingerbread", "Gingerbread figure", "gingerbread", ["christmas", "soft-girl"],
    [E((0, -0.62), (0.3, 0.3)), P([(-0.3, -0.35), (0.3, -0.35), (0.85, -0.2), (0.8, 0.05), (0.32, 0.0), (0.45, 0.9), (0.15, 0.95), (0, 0.4),
                                    (-0.15, 0.95), (-0.45, 0.9), (-0.32, 0.0), (-0.8, 0.05), (-0.85, -0.2)])] +
    [E((x, -0.65), (0.05, 0.05), 2) for x in (-0.1, 0.1)] + [E((0, y), (0.06, 0.06), 2) for y in (-0.2, 0.05)], ["festive", "cute"], "small")
add("mitten", "Mitten", "mitten", ["christmas", "soft-girl"],
    [P([(-0.45, 0.95), (-0.5, -0.45), (-0.25, -0.85), (0.15, -0.8), (0.35, -0.3), (0.65, -0.35), (0.7, 0.0), (0.4, 0.3), (0.42, 0.95)]),
     P([(-0.5, 0.65), (0.45, 0.65), (0.45, 0.95), (-0.48, 0.95)], 2)], ["festive"], "small", symmetric=False)
add("chevron", "Chevron stack", "chevron", ["athleisure", "gen-z", "preppy"],
    [P([(-0.9, y + 0.15), (0, y - 0.35), (0.9, y + 0.15), (0.9, y + 0.45), (0, y - 0.05), (-0.9, y + 0.45)], t) for y, t in ((-0.5, 0), (0.3, 1))],
    ["sporty"], "small")
add("wave-lines", "Wave lines", "wave", ["athleisure", "gen-z", "y2k"],
    [L([(-1 + i / 10, y + 0.18 * math.sin(i * 0.95)) for i in range(21)], 0.12, t) for y, t in ((-0.45, 0), (0.0, 1), (0.45, 0))],
    ["calm"], "small", band=True, symmetric=False)
add("target-rings", "Target rings", "target", ["athleisure", "gen-z", "archive"],
    [E((0, 0), (0.95, 0.95), stroke=0.12), E((0, 0), (0.6, 0.6), 1, stroke=0.12), E((0, 0), (0.25, 0.25))], ["sporty"], "small")
add("arrow-up", "Arrow", "arrow", ["athleisure", "gen-z"],
    [P([(0, -1), (0.65, -0.25), (0.25, -0.25), (0.25, 0.95), (-0.25, 0.95), (-0.25, -0.25), (-0.65, -0.25)])], ["sporty"], "small")
add("hexagon-grid", "Hexagon cluster", "hexagon", ["athleisure", "gen-z", "archive"],
    [P(circ(x, y, 0.3, 6, a0=math.pi / 6, a1=math.pi / 6 + 2 * math.pi), stroke=0.07, tone=t)
     for (x, y), t in zip([(0, 0), (0.55, -0.32), (0.55, 0.32), (-0.55, -0.32), (-0.55, 0.32), (0, -0.64), (0, 0.64)], (0, 1, 1, 1, 1, 0, 0))],
    ["sporty"], "small")
add("stitched-patch", "Stitched square patch", "patch", ["archive", "grunge", "emo"],
    [P([(-0.9, -0.75), (0.9, -0.75), (0.9, 0.75), (-0.9, 0.75)])] +
    [L([(x, -0.6), (x + 0.12, -0.6)], 0.05, 2) for x in [-0.7 + i * 0.25 for i in range(6)]] +
    [L([(x, 0.6), (x + 0.12, 0.6)], 0.05, 2) for x in [-0.7 + i * 0.25 for i in range(6)]], ["worn"], "small")
add("stitch-x", "Stitched X mark", "stitch", ["archive", "grunge", "emo"],
    [L([(-0.7, -0.7), (0.7, 0.7)], 0.16), L([(0.7, -0.7), (-0.7, 0.7)], 0.16, 1)], ["worn"], "small")


def main():
    LIB.mkdir(parents=True, exist_ok=True)
    for old in LIB.glob("*.json"):
        el = json.loads(old.read_text(encoding="utf-8"))
        if el.get("source") == "original":
            old.unlink()
    ids = set()
    for el in ELEMENTS:
        assert el["id"] not in ids, el["id"]
        ids.add(el["id"])
        (LIB / f"{el['id']}.json").write_text(json.dumps(el, indent=1), encoding="utf-8")
    print("wrote", len(ELEMENTS), "original elements")


if __name__ == "__main__":
    main()

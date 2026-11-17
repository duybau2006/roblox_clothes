"""Realistic family: crisp material textures, garment wrinkle maps and material highlight response.

Everything is generated on the continuous strip (see clothing.py) before panels are cut, so
textures and folds cross every seam. Textures are periodic every 64 px and mirror-symmetric,
which also keeps the shoulder and hip seams continuous.

Spec (per section):  material: cotton | knit | denim | leather | satin | nylon
                     garment_kind: tee | hoodie | sweater | jacket | shirt | suit | corset |
                                   jeans | trousers | joggers | shorts | skirt
Top level:           shading: {mode: realistic, seed: 4, wrinkles: 1.0, layer: <custom layer id>, strength: 0.6}
"""
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from clothing import S, M, H, Canvas, seeded_noise

MATERIALS = {
    # texture kind, texture amplitude, wrinkle contrast, highlight gamma (>1 = narrower), highlight gain, fold blur (px)
    "cotton":  {"tex": "jersey",  "amp": 6,  "contrast": 1.0, "gamma": 0.9, "gain": 0.9, "blur": 2.2},
    "knit":    {"tex": "knit",    "amp": 22, "contrast": 0.8, "gamma": 0.8, "gain": 0.8, "blur": 3.0},
    "denim":   {"tex": "twill",   "amp": 18, "contrast": 1.05, "gamma": 1.2, "gain": 1.0, "blur": 1.8},
    "leather": {"tex": "pebble",  "amp": 9,  "contrast": 1.35, "gamma": 2.4, "gain": 1.9, "blur": 1.2},
    "satin":   {"tex": "smooth",  "amp": 3,  "contrast": 1.25, "gamma": 2.0, "gain": 1.7, "blur": 1.6},
    "nylon":   {"tex": "ripstop", "amp": 6,  "contrast": 1.15, "gamma": 1.8, "gain": 1.5, "blur": 1.5},
}


# ---------------------------------------------------------------- textures (crisp, no blur)

def _sym_tile(tile):
    """Make a 32-wide tile periodic + mirror-symmetric at 64 px (seams and shoulders match)."""
    out = Image.new("L", (tile.width * 2, tile.height))
    out.paste(tile, (0, 0))
    out.paste(tile.transpose(Image.FLIP_LEFT_RIGHT), (tile.width, 0))
    return out


def texture_map(part, material, seed=0):
    """L map (128 = neutral) at 4x, wrap-canvas sized. Drawn directly at 4x: crisp, not blurred."""
    mat = MATERIALS.get(material, MATERIALS["cotton"])
    h4 = (H + 2 * M) * S
    w4 = 32 * S
    amp = mat["amp"]
    kind = mat["tex"]
    rnd = random.Random(seed * 31 + len(material))
    tile = Image.new("L", (w4, h4), 128)
    d = ImageDraw.Draw(tile)
    if kind == "jersey":                     # fine knit columns (1 px) + per-stitch noise
        n = seeded_noise(w4 // 2, h4 // 2, amp * 0.6, seed + 1).resize((w4, h4), Image.NEAREST)
        tile = n
        d = ImageDraw.Draw(tile)
        for x in range(0, w4, S):
            d.line([(x, 0), (x, h4)], fill=128 - amp // 2, width=1)
    elif kind == "knit":                     # chunky V stitches, 3 px columns
        for x in range(0, w4, 3 * S):
            for y in range(0, h4, 3 * S):
                d.line([(x + 2, y), (x + 1.5 * S, y + 2 * S), (x + 3 * S - 2, y)], fill=128 - amp, width=2)
                d.line([(x + 1.5 * S, y + 2 * S), (x + 1.5 * S, y + 2 * S + 2)], fill=128 + amp, width=2)
    elif kind == "twill":                    # diagonal twill + vertical slubs
        for k in range(-h4, w4 + h4, 2 * S):
            d.line([(k, 0), (k + h4, h4)], fill=128 + amp, width=2)
        slub = seeded_noise(w4 // S, 8, amp * 0.5, seed + 2).resize((w4, h4), Image.BILINEAR)
        tile = ImageChops.add(tile, slub, 1.0, -128)
    elif kind == "pebble":                   # leather pebble grain: small irregular cells
        for _ in range(int(w4 * h4 / (S * S * 9))):
            x, y, r = rnd.uniform(0, w4), rnd.uniform(0, h4), rnd.uniform(0.6, 1.4) * S
            d.ellipse([x - r, y - r, x + r, y + r], outline=128 - amp, fill=128 + amp // 3, width=1)
    elif kind == "ripstop":                  # nylon ripstop grid
        for x in range(0, w4, 4 * S):
            d.line([(x, 0), (x, h4)], fill=128 + amp, width=1)
        for y in range(0, h4, 4 * S):
            d.line([(0, y), (w4, y)], fill=128 + amp, width=1)
    else:                                     # satin: almost flat
        tile = seeded_noise(w4 // 4, h4 // 4, amp, seed + 3).resize((w4, h4), Image.BILINEAR)
    tile = _sym_tile(tile)
    wide = Image.new("L", (3 * part.P * S, h4), 128)
    for x in range(0, wide.width, tile.width):
        wide.paste(tile, (x, 0))
    return wide


# ---------------------------------------------------------------- wrinkles

def _fold(cs, ch, pts, depth, width, blur, offset, hi_val):
    """One fold: dark crease along pts and a highlight ridge offset to one side."""
    cs.line(pts, depth, width)
    if hi_val:
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        L = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / L * offset, (x1 - x0) / L * offset
        ch.line([(x + nx, y + ny) for x, y in pts], hi_val, width * 0.8)


def wrinkle_maps(part, region, kind, material, seed, strength=1.0):
    """(shadow, highlight) wrap canvases for one part. region: torso | arm | leg."""
    mat = MATERIALS.get(material, MATERIALS["cotton"])
    rnd = random.Random(seed * 101 + {"torso": 1, "arm": 2, "leg": 3}.get(region, 0))
    cs, ch = Canvas(part, "L", 0), Canvas(part, "L", 0)
    k = mat["contrast"] * strength
    dv, hv = int(46 * k), int(38 * k)
    stiff = kind in ("jacket", "suit", "corset")
    soft = material in ("cotton", "knit", "satin")

    def jit(a=3.0):
        return rnd.uniform(-a, a)

    if region == "torso":
        if kind == "corset":                      # boning: vertical seams with narrow highlights
            for u in (20, 44, 84, 108, 212, 236, 276, 300):
                _fold(cs, ch, [(u, 6), (u + jit(1), 60), (u, 120)], dv // 2, 1.0, 0, 1.6, hv)
        n = 3 if stiff else 6
        for side in (0, 1):                       # armpit diagonals toward the waist, front and back
            for j in range(n):
                sx = 128 if side == 0 else 0
                tx = 64 + (22 if side == 0 else -22) + jit(8)
                y0 = 10 + j * (8 if not stiff else 14) + jit(2)
                pts = [(sx + (-4 if side == 0 else 4), y0), ((sx + tx) / 2, y0 + 18 + jit()), (tx, y0 + 40 + jit(4))]
                _fold(cs, ch, pts, dv, 2.2 if soft else 1.6, 0, 2.6, hv)
                bpts = [(p[0] + 192 + jit(4), p[1] + 6 + jit(5)) for p in pts]   # back folds: own jitter, not a copy of the front
                _fold(cs, ch, bpts, int(dv * 0.8), 2.0, 0, 2.6, int(hv * 0.7))
        for j in range(4 if not stiff else 2):    # waist bunching above the hem
            y = 70 + j * 7 + jit(2)
            for o in (0, 192):
                _fold(cs, ch, [(o + 10 + jit(4), y), (o + 64, y + 3 + jit(2)), (o + 118 + jit(4), y + jit(2))], int(dv * 0.7), 1.8, 0, 2.2, int(hv * 0.8))
        if stiff:                                 # long vertical drape folds
            for u in (16, 112, 210, 302):
                _fold(cs, ch, [(u, 20), (u + jit(3), 70), (u + jit(2), 110)], int(dv * 0.6), 1.6, 0, 2.0, hv)
    elif region == "arm":
        for j in range(5 if not stiff else 3):    # elbow cluster (R15 elbow at ~50)
            y = 44 + j * 4.5 + jit(1.5)
            for o in (0, 64, 128, 192):
                _fold(cs, ch, [(o + 4 + jit(2), y + jit(2)), (o + 32, y - 3 + jit(2)), (o + 60 + jit(2), y + 2 + jit(2))], int(dv * 0.85), 1.8, 0, 2.2, hv)
        for j in range(4):                        # forearm spiral folds
            y = 66 + j * 8 + jit(2)
            _fold(cs, ch, [(0 + jit(2), y), (64, y + 10), (128, y + 2), (192, y + 12), (256, y + 4)], int(dv * 0.6), 1.6, 0, 2.0, int(hv * 0.7))
        for j in range(3):                        # bunching above the cuff
            y = 88 + j * 3 + jit(1)
            _fold(cs, ch, [(0, y), (64, y + 1.5), (128, y), (192, y + 1.5), (256, y)], int(dv * 0.7), 1.4, 0, 1.8, int(hv * 0.6))
    else:  # leg
        if kind == "skirt":
            for u in range(4, part.P, 8):         # pleat-like vertical shading
                _fold(cs, ch, [(u, -30), (u + jit(1), 20), (u, 60)], int(dv * 0.6), 1.4, 0, 2.6, hv)
        else:
            for j in range(4):                    # hip / crotch diagonals (on the front, visible in the hip zone)
                _fold(cs, ch, [(64 - j * 5 + jit(2), -14 + j * 6), (40, 2 + j * 6), (18 + jit(3), 16 + j * 6)], int(dv * 0.7), 1.8, 0, 2.2, int(hv * 0.8))
            for j in range(4 if kind in ("jeans", "joggers") else 2):   # knee whiskers (R15 knee ~51)
                y = 42 + j * 4 + jit(1.5)
                _fold(cs, ch, [(6 + jit(2), y + 2), (32, y - 2 + jit()), (58 + jit(2), y + 2)], dv, 1.8, 0, 2.2, hv)
            if kind == "jeans":                   # honeycomb behind the knee
                for j in range(3):
                    y = 48 + j * 5
                    _fold(cs, ch, [(134, y), (148, y + 3), (160, y), (172, y + 3), (186, y)], int(dv * 0.9), 1.6, 0, 1.8, int(hv * 0.8))
            for j in range(5 if kind in ("jeans", "joggers", "trousers") else 0):   # ankle stacking
                y = 78 + j * 3.6 + jit(1)
                _fold(cs, ch, [(0, y), (32, y - 2 + jit()), (64, y + 1), (96, y - 1), (128, y + 1), (160, y - 2), (192, y), (224, y - 1), (256, y)],
                      int(dv * 0.8), 1.5, 0, 1.8, int(hv * 0.7))
    cs.blur(mat["blur"])
    ch.blur(mat["blur"] * (0.6 if not soft else 1.3))
    return cs, ch


def respond(hi, material):
    """Material highlight response: leather/satin/nylon -> narrow bright; cotton/knit -> soft broad."""
    mat = MATERIALS.get(material, MATERIALS["cotton"])
    g, gain = mat["gamma"], mat["gain"]
    return hi.point(lambda v: max(0, min(255, int(255 * ((v / 255) ** g) * gain))))


def shading_map(part, region, kind, material, seed, base=None, base_weight=0.7, strength=1.0):
    """Full L map (strip size): shared base form shading + wrinkles + material response + texture."""
    cs, ch = wrinkle_maps(part, region, kind, material, seed, strength)
    tex = texture_map(part, material, seed)
    mid = Image.new("L", cs.img.size, 128)
    out = ImageChops.add(mid, respond(ch.img, material))
    out = ImageChops.subtract(out, cs.img)
    out = ImageChops.add(out, tex, 1.0, -128)
    out = out.crop((part.P * S, 0, 2 * part.P * S, out.height))
    if base is not None:   # keep the shared form shading (cuffs, hems, under-arm) at reduced weight
        b = base.point(lambda v: int(128 + (v - 128) * base_weight))
        out = ImageChops.add(out, b, 1.0, -128)
    # material response on the broad base highlights too
    mat = MATERIALS.get(material, MATERIALS["cotton"])
    if mat["gamma"] > 1.5:
        out = out.point(lambda v: v if v <= 150 else min(255, int(150 + (v - 150) * mat["gain"])))
    return out

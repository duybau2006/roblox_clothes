"""Original decoration motifs and layouts for render.py (spec field `decor` on torso / arms / legs).

Every motif is an original vector shape drawn in strip coordinates (see clothing.py), so it gets
the shared shading (folds, highlights) like the fabric. No text, logos, brand marks, crosses or
skulls exist here on purpose; validate.py only accepts the names in MOTIFS and LAYOUTS.

decor entry:  {motif: star, layout: chest, colour: "#hex", size: 14, accent: "#hex"}
  size    motif radius in output px (default depends on layout)
  accent  second colour (threads of a rip, highlight of a stud, centre of a flower, knot of a bow)
"""
import math
import random
import zlib

from PIL import Image, ImageDraw

from clothing import H, M, S, OUTFIT, hex_rgb, rgba, shade
import library
import prints

# ---------------------------------------------------------------- shapes (unit size, centred, y down)


def _ellipse_pts(cx, cy, rx, ry, rot=0.0, n=24):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return out


STAR = [(math.sin(i * math.pi / 5) * (1 if i % 2 == 0 else 0.42), -math.cos(i * math.pi / 5) * (1 if i % 2 == 0 else 0.42))
        for i in range(10)]
SPARKLE = [(math.sin(i * math.pi / 4) * (1 if i % 2 == 0 else 0.22), -math.cos(i * math.pi / 4) * (1 if i % 2 == 0 else 0.22))
           for i in range(8)]
HEART = [(16 * math.sin(t) ** 3 / 17, -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17 + 0.1)
         for t in [2 * math.pi * i / 40 for i in range(40)]]
FLAME = [(0, 1), (-0.62, 0.62), (-0.7, 0.1), (-0.45, -0.35), (-0.5, -0.75), (-0.22, -0.4), (-0.12, -1.0),
         (0.06, -0.48), (0.3, -0.82), (0.33, -0.3), (0.62, -0.5), (0.7, 0.12), (0.62, 0.62)]
BAT = [(0, -0.35), (0.12, -0.6), (0.2, -0.3), (0.55, -0.55), (1.0, -0.4), (0.92, 0.0), (0.72, -0.05), (0.62, 0.22),
       (0.42, 0.08), (0.28, 0.34), (0, 0.18), (-0.28, 0.34), (-0.42, 0.08), (-0.62, 0.22), (-0.72, -0.05),
       (-0.92, 0.0), (-1.0, -0.4), (-0.55, -0.55), (-0.2, -0.3), (-0.12, -0.6)]
LIGHTNING = [(0.15, -1), (-0.45, 0.1), (-0.05, 0.1), (-0.25, 1), (0.45, -0.2), (0.05, -0.2), (0.3, -1)]
BOW_LOOP = [(0, 0), (-0.95, -0.62), (-1.05, 0.0), (-0.9, 0.6)]
BOW_TAIL = [(-0.08, 0.1), (-0.5, 0.95), (-0.28, 1.0), (0.02, 0.25)]


def _poly(c, shape, u, v, s, col, outline=True, flip=False):
    pts = [(u + (-x if flip else x) * s, v + y * s) for x, y in shape]
    if outline:
        c.polygon(pts, None, rgba(shade(col, 0.55)), 0.9)
    c.polygon(pts, rgba(col))


def m_star(c, u, v, s, col, acc):
    _poly(c, STAR, u, v, s, col)


def m_sparkle(c, u, v, s, col, acc):
    _poly(c, SPARKLE, u, v, s, col, outline=False)


def m_heart(c, u, v, s, col, acc):
    _poly(c, HEART, u, v, s, col)


def m_flame(c, u, v, s, col, acc):
    _poly(c, FLAME, u, v, s, col)
    _poly(c, [(x * 0.55, y * 0.55 + 0.35) for x, y in FLAME], u, v, s, acc, outline=False)


def m_bat(c, u, v, s, col, acc):
    _poly(c, BAT, u, v, s, col)


def m_lightning(c, u, v, s, col, acc):
    _poly(c, LIGHTNING, u, v, s, col)


def m_moon(c, u, v, s, col, acc):
    outer = [(math.cos(a) * 1.0, math.sin(a) * 1.0) for a in [math.pi * (0.5 + i / 20) for i in range(21)]]
    inner = [(math.cos(a) * 0.78 + 0.32, math.sin(a) * 0.78) for a in [math.pi * (1.5 - i / 20) for i in range(21)]]
    _poly(c, outer + inner, u, v, s, col)


def m_butterfly(c, u, v, s, col, acc):
    for flip in (False, True):
        k = -1 if flip else 1
        up = _ellipse_pts(0.48 * k, -0.32, 0.5, 0.36, rot=-0.55 * k)
        lo = _ellipse_pts(0.36 * k, 0.36, 0.34, 0.26, rot=0.5 * k)
        for shp in (up, lo):
            _poly(c, shp, u, v, s, col)
        c.ellipse(u + 0.5 * k * s, v - 0.32 * s, 0.14 * s, 0.11 * s, rgba(acc))
    c.line([(u, v - 0.55 * s), (u, v + 0.6 * s)], rgba(shade(col, 0.4)), max(0.8, s * 0.12))


def m_bow(c, u, v, s, col, acc):
    for flip in (False, True):
        _poly(c, BOW_LOOP, u, v, s, col, flip=flip)
        _poly(c, BOW_TAIL, u, v, s, col, flip=flip)
    c.ellipse(u, v, 0.2 * s, 0.24 * s, rgba(acc), rgba(shade(acc, 0.55)), 0.6)


def m_rose(c, u, v, s, col, acc):
    for flip in (False, True):  # leaves
        k = -1 if flip else 1
        _poly(c, _ellipse_pts(0.85 * k, 0.55, 0.45, 0.2, rot=0.5 * k, n=12), u, v, s, acc)
    _poly(c, _ellipse_pts(0, 0, 0.62, 0.6), u, v, s, col)
    spiral = [(u + math.cos(a) * r * s, v + math.sin(a) * r * s)
              for a, r in [(i * 0.5, 0.52 - i * 0.022) for i in range(22)]]
    c.line(spiral, rgba(shade(col, 0.55)), max(0.6, s * 0.07))


def m_web(c, u, v, s, col, acc):
    w = max(0.5, s * 0.06)
    for i in range(8):
        a = math.pi * i / 4
        c.line([(u, v), (u + math.cos(a) * s, v + math.sin(a) * s)], rgba(col), w)
    for r in (0.35, 0.65, 0.95):
        ring = [(u + math.cos(math.pi * i / 4) * r * s, v + math.sin(math.pi * i / 4) * r * s) for i in range(9)]
        sag = []
        for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            sag += [(x0, y0), (mx + (u - mx) * 0.12, my + (v - my) * 0.12)]
        c.line(sag + [ring[-1]], rgba(col), w)


def m_flower(c, u, v, s, col, acc):
    for i in range(5):
        a = 2 * math.pi * i / 5 - math.pi / 2
        c.ellipse(u + math.cos(a) * 0.5 * s, v + math.sin(a) * 0.5 * s, 0.42 * s, 0.42 * s, rgba(col))
    c.ellipse(u, v, 0.3 * s, 0.3 * s, rgba(acc))


def m_stud(c, u, v, s, col, acc):
    c.ellipse(u, v, s, s, rgba(shade(col, 0.6)))
    c.ellipse(u, v, 0.8 * s, 0.8 * s, rgba(col))
    c.ellipse(u - 0.3 * s, v - 0.3 * s, 0.3 * s, 0.3 * s, rgba(acc))


def m_cherry(c, u, v, s, col, acc):
    c.line([(u - 0.45 * s, v + 0.2 * s), (u + 0.1 * s, v - 0.9 * s), (u + 0.45 * s, v + 0.25 * s)], rgba(acc), max(0.6, s * 0.1))
    for dx in (-0.45, 0.45):
        c.ellipse(u + dx * s, v + 0.45 * s, 0.42 * s, 0.42 * s, rgba(col), rgba(shade(col, 0.55)), 0.5)


MOTIFS = {"star": m_star, "sparkle": m_sparkle, "heart": m_heart, "flame": m_flame, "bat": m_bat,
          "lightning": m_lightning, "moon": m_moon, "butterfly": m_butterfly, "bow": m_bow, "rose": m_rose,
          "web": m_web, "flower": m_flower, "stud": m_stud, "cherry": m_cherry}
# layout-only decorations (not single motifs)
SPECIAL = {"chain", "rip", "patch", "stitch", "lace", "safety_pin"}

LAYOUTS = {
    "torso": {"border": None, "chest": (64, 44, 18), "pocket": (90, 30, 6), "back": (256, 44, 22), "scatter": None, "row": None,
              "necklace": None, "stitch": None, "lace_hem": None, "lace_neck": None, "patch": (98, 76, 9)},
    "arms": {"border": None, "sleeve": (224, 30, 9), "scatter": None, "row": None, "lace_cuff": None, "patch": (160, 56, 8),
             "stitch": None},
    "legs": {"border": None, "thigh": (34, 28, 9), "knees": (32, 54, 9), "scatter": None, "row": None, "hip_chain": None,
             "lace_hem": None, "patch": (32, 54, 8), "stitch": None, "pin": (10, 16, 5)},
}


# ---------------------------------------------------------------- special decorations

def chain(c, path, col, link=2.2):
    pts = []
    for (u0, v0), (u1, v1) in zip(path, path[1:]):
        n = max(1, int(math.hypot(u1 - u0, v1 - v0) / link))
        pts += [(u0 + (u1 - u0) * i / n, v0 + (v1 - v0) * i / n) for i in range(n)]
    for i, (u, v) in enumerate(pts):
        rx, ry = (link * 0.65, link * 0.4) if i % 2 == 0 else (link * 0.4, link * 0.55)
        c.ellipse(u, v, rx, ry, None, rgba(shade(col, 0.55)), 0.75)
        c.ellipse(u, v, rx * 0.85, ry * 0.85, None, rgba(col), 0.45)


def rip(c, u, v, s, body, thread, fx):
    rnd = random.Random(int(u * 13 + v * 7))
    n = 18
    hole = []
    for i in range(n):                                                    # ragged, wider than tall
        a = 2 * math.pi * i / n
        r = 0.75 + 0.45 * rnd.random()
        hole.append((u + math.cos(a) * s * r, v + math.sin(a) * s * 0.5 * r))
    c.polygon(hole, rgba(shade(body, 0.3)))                               # dark backing, never skin
    for k in (-1.5, -0.5, 0.5, 1.5):                                       # loose horizontal threads
        y = v + k * s * 0.17
        pts = [(u - s * 0.9 + j * s * 0.3, y + rnd.uniform(-0.5, 0.5)) for j in range(7)]
        c.line(pts, rgba(thread), 0.7)
    for (x, y) in hole[::2]:                                               # frayed fringe around the edge
        c.line([(x, y), (x + (x - u) * 0.12, y + (y - v) * 0.25)], rgba(shade(thread, 0.85)), 0.45)
    fx["sh"].ellipse(u, v + s * 0.45, s * 0.95, s * 0.2, 26)
def patch(c, u, v, s, col, stitch):
    c.rect(u - s, v - s * 0.8, u + s, v + s * 0.8, rgba(col))
    dashed(c, [(u - s + 1, v - s * 0.8 + 1), (u + s - 1, v - s * 0.8 + 1), (u + s - 1, v + s * 0.8 - 1),
               (u - s + 1, v + s * 0.8 - 1), (u - s + 1, v - s * 0.8 + 1)], stitch)


def dashed(c, path, col, dash=1.6, gap=1.2, width=0.5):
    for (u0, v0), (u1, v1) in zip(path, path[1:]):
        L = math.hypot(u1 - u0, v1 - v0)
        t = 0.0
        while t < L:
            a, b = t / L, min(L, t + dash) / L
            c.line([(u0 + (u1 - u0) * a, v0 + (v1 - v0) * a), (u0 + (u1 - u0) * b, v0 + (v1 - v0) * b)], rgba(col), width)
            t += dash + gap


def lace(c, v, col, down=True, r=3.0, P=None, spans=None):
    """Scalloped lace edge hanging from row v (period 2r = 6 px wraps the 384 / 256 px strips).
    spans: optional [(u0, u1), ...] to draw only part of the circumference (e.g. a neckline)."""
    for u0, u1 in (spans or [(0, P)]):
        if spans:
            c.rect(u0, v - 1.4, u1, v, rgba(col))
        else:
            c.band(v - 1.4, v, rgba(col))
    u = 0.0
    while u < P:
        if spans and not any(u0 <= u + r <= u1 for u0, u1 in spans):
            u += 2 * r
            continue
        c.ellipse(u + r, v, r, r * 0.95, rgba(col))
        c.ellipse(u + r, v + r * 0.25, r * 0.4, r * 0.4, rgba(shade(col, 0.6)))   # eyelet
        c.ellipse(u, v - 0.6, 0.55, 0.55, rgba(shade(col, 0.6)))                  # picot between scallops
        u += 2 * r


def safety_pin(c, u, v, s, col):
    dark = rgba(shade(col, 0.55))
    c.line([(u - s, v - 0.8), (u + s * 0.85, v - 0.8)], dark, 1.3)
    c.line([(u - s, v - 0.8), (u + s * 0.85, v - 0.8)], rgba(col), 0.8)       # pin bar
    c.line([(u - s * 0.8, v + 1.2), (u + s * 0.85, v + 1.2)], rgba(col), 0.8)  # needle
    c.ellipse(u + s, v + 0.2, 1.4, 1.3, None, rgba(col), 0.8)                  # spring coil
    c.rect(u - s - 1.8, v - 2.0, u - s + 0.8, v + 2.2, rgba(shade(col, 0.85)))  # clasp head


# ---------------------------------------------------------------- placement

def _seams(kind, P):
    return [0, 128, 192, 320, P] if kind == "torso" else [0, 64, 128, 192, P]


def scatter_points(kind, P, v0, v1, s, seed, spacing=None, avoid_rows=()):
    """Deterministic scatter that keeps every motif clear of seams (so seam checks are unaffected).
    avoid_rows: strip rows that are seams too (legs: row 0 is the hip seam with the torso)."""
    rnd = random.Random(seed)
    sp = spacing or s * 3.2
    pts, seams = [], _seams(kind, P)
    row = 0
    v = v0 + s
    while v < v1 - s:
        u = (sp / 2) * (row % 2) + s + 1
        while u < P:
            uu, vv = u + rnd.uniform(-sp * 0.2, sp * 0.2), v + rnd.uniform(-sp * 0.15, sp * 0.15)
            if all(abs(uu - x) > s + 2 for x in seams) and v0 + s <= vv <= v1 - s and                     all(abs(vv - r) > s + 2 for r in avoid_rows):
                pts.append((uu, vv))
            u += sp
        v += sp * 0.8
        row += 1
    return pts


def draw_decor(c, section_kind, decor, colours, fx, ctx, warnings):
    """section_kind: torso | arms | legs.  ctx: dict with hem / cuff / leg limits for this outfit."""
    P = c.P
    for i, d in enumerate(decor or []):
        if "print" in d:                                            # print family
            if section_kind != "torso":
                warnings.append(f"{section_kind}: prints go on the torso only; not drawn")
            else:
                prints.draw_print(c, c.part, d["print"], ctx, warnings)
            continue
        if "element" in d:                                          # library element (both families)
            draw_element_decor(c, section_kind, d, colours, ctx, warnings, i)
            continue
        motif, layout = str(d.get("motif", "")).lower(), str(d.get("layout", "")).lower()
        col = hex_rgb(d["colour"]) if d.get("colour") else colours.accent
        acc = hex_rgb(d["accent"]) if d.get("accent") else shade(col, 1.45)
        if layout not in LAYOUTS[section_kind]:
            warnings.append(f"{section_kind}: decor layout '{layout}' not available here; not drawn")
            continue
        if motif not in MOTIFS and motif not in SPECIAL:
            warnings.append(f"{section_kind}: decor motif '{motif}' not available; not drawn")
            continue
        preset = LAYOUTS[section_kind][layout]
        s = float(d.get("size", preset[2] if preset else 4))
        fn = MOTIFS.get(motif)
        if layout in ("chest", "pocket", "back", "sleeve", "thigh") and fn:
            u, v, _ = preset
            if layout == "back" and ctx.get("hood"):           # fit back prints between hood and hem
                lo, hi = 50, ctx["band_top"]
                v = (lo + hi) / 2
                s = min(s, (hi - lo) / 2 - 1)
            fn(c, u, v, s, col, acc)
            if layout in ("chest", "back") and d.get("pair"):            # flanking smaller motifs
                for du in (-1, 1):
                    fn(c, u + du * s * 1.6, v + s * 0.55, s * 0.45, col, acc)
        elif layout == "scatter" and fn:
            v0, v1 = ctx["scatter"]
            for (u, v) in scatter_points(section_kind, P, v0, v1, s, seed=zlib.crc32(f"{section_kind}:{motif}:{i}".encode()),
                                         spacing=d.get("spacing"), avoid_rows=ctx.get("avoid_rows", ())):
                fn(c, u, v, s, col, acc)
        elif layout == "row" and fn:
            v = float(d.get("row", ctx["row"]))
            if any(abs(v - r) <= s + 2 for r in ctx.get("avoid_rows", ())):
                warnings.append(f"{section_kind}: decor row {v:g} sits on a seam; not drawn")
                continue
            seams = _seams(section_kind, P)
            u = s + 2
            while u < P:
                if all(abs(u - x) > s + 1.5 for x in seams):
                    fn(c, u, v, s, col, acc)
                u += float(d.get("spacing", s * 2.6))
        elif layout == "necklace" and motif == "chain":
            chain(c, [(42, -1), (50, 10), (64, 17), (78, 10), (86, -1)], col)
            if d.get("pendant") in MOTIFS:
                MOTIFS[d["pendant"]](c, 64, 22, 3.2, acc, shade(acc, 1.4))
        elif layout == "hip_chain" and motif == "chain":
            w = ctx["waist_leg"]
            low = min(w + 24, -5)        # never reaches leg row 0 (the hip seam)
            top = min(w + 10, low - 8)
            chain(c, [(14, top), (6, (top + low) / 2), (-6, low), (-22, low), (-32, low - 6)], col)
        elif layout == "knees" and motif == "rip":
            rip(c, 32, 54, s, ctx["body"], col, fx)
            if d.get("both"):
                rip(c, 160, 58, s * 0.7, ctx["body"], col, fx)
        elif layout == "patch" and motif == "patch":
            u, v, _ = preset
            patch(c, u, v, s, col, acc)
        elif layout == "pin" and motif == "safety_pin":
            u, v, _ = preset
            safety_pin(c, u, v, s, col)
        elif layout == "stitch" and motif == "stitch":
            for x in ctx["stitch_cols"]:
                dashed(c, [(x, ctx["scatter"][0] - 6), (x, ctx["scatter"][1])], col)
            if section_kind == "torso":
                dashed(c, [(2, 26), (126, 26)], col); dashed(c, [(194, 24), (318, 24)], col)
        elif layout in ("lace_hem", "lace_cuff", "lace_neck") and motif == "lace":
            v = {"lace_hem": ctx.get("lace_hem"), "lace_cuff": ctx.get("lace_cuff"), "lace_neck": 6.0}[layout]
            lace(c, v, col, P=P, spans=[(34, 94), (226, 286)] if layout == "lace_neck" else None)
        else:
            warnings.append(f"{section_kind}: motif '{motif}' cannot use layout '{layout}'; not drawn")


def element_positions(section_kind, layout, d, ctx, P, s, seed):
    preset = LAYOUTS[section_kind].get(layout)
    if layout in ("chest", "pocket", "back", "sleeve", "thigh", "knees", "patch"):
        u, v, _ = preset
        if layout == "back" and ctx.get("hood"):
            lo, hi = 50, ctx["band_top"]
            v, s = (lo + hi) / 2, min(s, (hi - lo) / 2 - 1)
        return [(u, v, s)]
    if layout == "scatter":
        v0, v1 = ctx["scatter"]
        return [(u, v, s) for u, v in scatter_points(section_kind, P, v0, v1, s, seed, spacing=d.get("spacing"),
                                                     avoid_rows=ctx.get("avoid_rows", ()))]
    if layout == "row":
        v = float(d.get("row", ctx["row"]))
        seams = _seams(section_kind, P)
        out, u = [], s + 2
        while u < P:
            if all(abs(u - x) > s + 1.5 for x in seams):
                out.append((u, v, s))
            u += float(d.get("spacing", s * 2.6))
        return out
    return None


def draw_element_decor(c, section_kind, d, colours, ctx, warnings, i):
    try:
        el = library.element(str(d["element"]))
    except KeyError as e:
        warnings.append(f"{section_kind}: {e}; not drawn")
        return
    layout = str(d.get("layout", "")).lower()
    col = hex_rgb(d["colour"]) if d.get("colour") else colours.accent
    if layout == "border":                       # owner-generated border tile repeated round the part
        if not el.get("tile"):
            warnings.append(f"{section_kind}: element '{el['id']}' has no border tile; not drawn")
            return
        default_row = {"torso": ctx.get("band_top", 100) - 12, "arms": ctx.get("lace_cuff", 92) - 6,
                       "legs": ctx.get("lace_hem", 90) - 6}[section_kind]
        h = float(d.get("height", 8))
        row = float(d.get("row", default_row))
        period = 128 if c.P % 128 == 0 and float(d.get("height", 8)) >= 12 else 64
        t = library.tile_image(el, None if d.get("original") else library.ink_tones(col), period, max(2, round(h)))
        t = t.resize((period * S, max(1, round(h * S))), Image.LANCZOS)
        y = int((row + M) * S)
        for x in range(0, c.img.width, period * S):
            c.img.paste(t, (x, y), t)
        c.d = ImageDraw.Draw(c.img)
        ctx_fx = ctx.get("fx")
        if ctx_fx:
            ctx_fx["sh"].band(row + h, row + h + 1.2, 20)
        return
    preset = LAYOUTS[section_kind].get(layout, (0, 0, 8))
    s = float(d.get("size", preset[2] if preset else 4))
    pos = element_positions(section_kind, layout, d, ctx, c.P, s,
                            zlib.crc32(f"{section_kind}:{d['element']}:{i}".encode()))
    if pos is None:
        warnings.append(f"{section_kind}: element layout '{layout}' not available; not drawn")
        return
    m = library.Masks(c.part)
    orig = bool(d.get("original"))
    for u, v, ss in pos:
        m.draw(el, u, v, ss, original=orig)
    if layout in ("chest", "back") and d.get("pair") and pos:
        pel = library.element(d["pair"]) if isinstance(d["pair"], str) and d["pair"] in library.load_library() else el
        u, v, ss = pos[0]
        for k in (-1, 1):
            m.draw(pel, u + k * ss * 1.65, v + ss * 0.55, ss * 0.42, flip=k < 0, original=orig)
    m.composite(c, library.ink_tones(col))


def decor_colours(spec):
    """Every hex used by decor entries (for the palette check)."""
    out = []
    for key in ("torso", "arms", "legs"):
        for d in (spec.get(key) or {}).get("decor") or []:
            out += [d[k] for k in ("colour", "accent") if d.get(k)]
            if d.get("original") and d.get("element") and d["element"] in library.load_library():
                out += library.element(d["element"])["colours"] if "colours" in library.element(d["element"]) else []
                if d.get("pair") in library.load_library():
                    out += library.element(d["pair"]).get("colours", [])
            if "print" in d and d["print"].get("ink"):
                out.append(d["print"]["ink"])
    return out

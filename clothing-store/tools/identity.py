"""Identity graphics: numbers 0-99 in original lettering, invented emblems, racing / sports layouts.

Spec (top level):
  identity:
    number: 27                 # 0-99 only; no letters or words, ever
    number_style: varsity      # block | varsity | racing | stencil
    number_colour: "#hex"      # outline colour comes from `number_outline`
    number_outline: "#hex"
    number_places: [back, chest, sleeve]
    emblem: {frame: shield|circle|wreath, element: <library id>, colour: "#hex", accent: "#hex"}   # chest badge + back emblem
    layout: racing             # racing side panels + piping; colours: panel, piping
    panel: "#hex"
    piping: "#hex"
Real team kits, flags, organisations, brands and words stay blocked (validate.py checks number and elements).
"""
import math

from clothing import hex_rgb, rgba, shade
import library

STYLES = ("block", "varsity", "racing", "stencil")
# 7-segment layout on a 0..1 x 0..1 box: a top, b upper-right, c lower-right, d bottom, e lower-left, f upper-left, g middle
SEG = {"a": ((0.08, 0.0), (0.92, 0.0)), "b": ((1.0, 0.06), (1.0, 0.47)), "c": ((1.0, 0.53), (1.0, 0.94)),
       "d": ((0.08, 1.0), (0.92, 1.0)), "e": ((0.0, 0.53), (0.0, 0.94)), "f": ((0.0, 0.06), (0.0, 0.47)),
       "g": ((0.08, 0.5), (0.92, 0.5))}
DIGITS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
          "7": "abc", "8": "abcdefg", "9": "abcfgd"}


def _seg_poly(seg, x, y, w, h, t, shear, gap):
    (x0, y0), (x1, y1) = SEG[seg]
    if gap:                                   # stencil: shorten every segment
        if x0 == x1:
            y0, y1 = y0 + 0.07, y1 - 0.07
        else:
            x0, x1 = x0 + 0.1, x1 - 0.1
    pts = []
    if x0 == x1:                              # vertical
        pts = [(x0 - t / 2, y0), (x0 + t / 2, y0), (x1 + t / 2, y1), (x1 - t / 2, y1)]
    else:
        pts = [(x0, y0 - t / 2), (x1, y1 - t / 2), (x1, y1 + t / 2), (x0, y0 + t / 2)]
    return [(x + (px + shear * (1 - py)) * w, y + py * h) for px, py in pts]


def draw_number(c, fx, text, cx, cy, h, style, col, outline):
    w, t = h * 0.56, 0.2 if style != "racing" else 0.22
    shear = 0.22 if style == "racing" else 0.0
    gap = style == "stencil"
    total = len(text) * w + (len(text) - 1) * h * 0.18
    x = cx - total / 2
    for ch in text:
        polys = [_seg_poly(s, x, cy - h / 2, w, h, t * (h / w) * 0.5, shear, gap) for s in DIGITS[ch]]
        if style == "varsity":                # thick outline in a second colour, then the face
            for pts in polys:
                c.polygon(pts, rgba(outline), rgba(outline), max(1.4, h * 0.07))
        for pts in polys:
            fx["sh"].polygon([(u + h * 0.05, v + h * 0.05) for u, v in pts], 22)
            c.polygon(pts, rgba(col))
            fx["hi"].line(pts[:2], 18, 0.6)
        x += w + h * 0.18


def shield(cx, cy, s):
    return [(cx - s, cy - s * 0.95), (cx + s, cy - s * 0.95), (cx + s, cy - s * 0.1),
            (cx + s * 0.7, cy + s * 0.6), (cx, cy + s * 1.05), (cx - s * 0.7, cy + s * 0.6), (cx - s, cy - s * 0.1)]


def draw_emblem(c, fx, em, cx, cy, s, part):
    col, acc = hex_rgb(em.get("colour", "#E8E4DC")), hex_rgb(em.get("accent", "#C0A060"))
    frame = em.get("frame", "shield")
    if frame == "shield":
        c.polygon(shield(cx, cy, s), rgba(shade(col, 0.8)), rgba(acc), max(0.8, s * 0.08))
        c.polygon(shield(cx, cy, s * 0.82), None, rgba(acc), max(0.5, s * 0.03))
    elif frame == "circle":
        c.ellipse(cx, cy, s, s, rgba(shade(col, 0.8)), rgba(acc), max(0.8, s * 0.08))
        for i in range(12):
            a = i * math.pi / 6
            c.ellipse(cx + math.cos(a) * s * 0.86, cy + math.sin(a) * s * 0.86, s * 0.05, s * 0.05, rgba(acc))
    else:  # wreath
        m = library.Masks(part)
        m.draw(library.element("laurel-wreath"), cx, cy + s * 0.05, s * 1.1)
        m.composite(c, library.ink_tones(acc))
    fx["sh"].ellipse(cx + s * 0.1, cy + s * 1.05, s * 0.8, s * 0.15, 20)
    if em.get("element") and em["element"] in library.load_library():   # unknown ids are not drawn; validate.py fails them
        m = library.Masks(part)
        m.draw(library.element(em["element"]), cx, cy, s * 0.58)
        m.composite(c, library.ink_tones(col if frame == "wreath" else acc))


def torso_identity(c, fx, ident, ctx, part):
    if not ident:
        return
    if ident.get("layout") == "racing":
        pc, pp = hex_rgb(ident.get("panel", "#C8102E")), hex_rgb(ident.get("piping", "#FFFFFF"))
        for u0, u1 in ((120, 200), (312, 392)):
            # from the armpit (row 34, below the shoulder seam zone) to the hem; curved edge bulges onto the front
            v0, v1 = 34, ctx["band_top"]
            edge = [(u0 - 6 * math.sin((v - v0) / (v1 - v0) * math.pi), v) for v in range(v0, int(v1) + 1, 4)]
            c.polygon([(u1, v0)] + edge + [(u1, v1)], rgba(pc))
            c.line(edge, rgba(pp), 1.4)
            fx["hi"].line(edge, 16, 0.5)
    num = ident.get("number")
    if num is not None and not (str(num).isdigit() and int(num) <= 99):
        num = None                            # letters / words / 100+ are never drawn (validate.py fails the spec)
    if num is not None:
        txt = str(int(num))
        col, out = hex_rgb(ident.get("number_colour", "#FFFFFF")), hex_rgb(ident.get("number_outline", "#111111"))
        style = ident.get("number_style", "block")
        places = ident.get("number_places", ["back", "chest"])
        top = 52 if ctx.get("hood") else 18
        if "back" in places:
            draw_number(c, fx, txt, 256, (top + ctx["band_top"]) / 2 + 2, min(46, ctx["band_top"] - top - 14), style, col, out)
        if "chest" in places:
            draw_number(c, fx, txt, 88 if ident.get("emblem") else 64, 36, 16, style, col, out)
    em = ident.get("emblem")
    if em:
        draw_emblem(c, fx, em, 40 if num is not None and "chest" in ident.get("number_places", []) else 88, 32, 8, part)
        if num is None or "back" not in ident.get("number_places", ["back"]):
            draw_emblem(c, fx, em, 256, (52 if ctx.get("hood") else 50), 26, part)


def arm_identity(c, fx, ident, ctx):
    if not ident:
        return
    if ident.get("layout") == "racing":
        pc, pp = hex_rgb(ident.get("panel", "#C8102E")), hex_rgb(ident.get("piping", "#FFFFFF"))
        c.rect(206, -48, 242, ctx["cuff"], rgba(pc))          # runs over the top face too: arm seams stay continuous
        c.line([(206, -48), (206, ctx["cuff"])], rgba(pp), 1.2)
        c.line([(242, -48), (242, ctx["cuff"])], rgba(pp), 1.2)
    num = ident.get("number")
    if num is not None and str(num).isdigit() and int(num) <= 99 and "sleeve" in ident.get("number_places", []):
        draw_number(c, fx, str(int(num)), 224, 24, 12, ident.get("number_style", "block"),
                    hex_rgb(ident.get("number_colour", "#FFFFFF")), hex_rgb(ident.get("number_outline", "#111111")))


def leg_identity(c, fx, ident, ctx):
    if ident and ident.get("layout") == "racing":
        pc, pp = hex_rgb(ident.get("panel", "#C8102E")), hex_rgb(ident.get("piping", "#FFFFFF"))
        c.rect(212, ctx["wv"] + 8, 236, ctx["bottom"], rgba(pc))
        c.line([(212, ctx["wv"] + 8), (212, ctx["bottom"])], rgba(pp), 1.2)
        c.line([(236, ctx["wv"] + 8), (236, ctx["bottom"])], rgba(pp), 1.2)

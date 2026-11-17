"""Render one outfit spec (YAML) to two 585x559 transparent PNGs: <id>-shirt.png and <id>-pants.png.

Usage:
    python tools/render.py specs/<id>.yaml [more specs...] [-o OUTDIR]   (default OUTDIR: renders/)

One outfit = one design:
  * the torso (front, back, left, right, top, bottom) is rendered ONCE and pasted pixel-for-pixel
    into both files, so the outfit looks complete even if a buyer wears only one half;
  * the shirt file adds the arms, the pants file adds the legs;
  * torso rows below torso.hem_line are cut from the rendered leg strips (waistband, trousers or
    skirt), so the torso always flows into the legs at the hip. A cropped top (hem above the
    waistband) leaves the rows between hem and waistband transparent;
  * the arms share the torso fabric and pattern phase unless arms.sleeve_contrast is true.

Spec sections (full reference: specs/_template.yaml):
  torso: palette, base_pattern, pattern, details, hem (rib|plain|belt|none), hem_line (80-120)
  arms:  palette, base_pattern, pattern, details, sleeves (long|short), sleeve_contrast,
         under {palette, base_pattern, pattern, details} (long under-sleeve for layered looks),
         mirror, left (overrides when mirror is false)
  legs:  type (trousers|skirt), waist_line, waistband (elastic|plain|none), palette, base_pattern,
         pattern, details, skirt_length, legwear (tights|socks|bare), legwear_palette, sock_top,
         shoes, shoe_palette, mirror, left
Palette roles inside each section: [0] body, [1] trim, [2] accent. Missing roles derive from [0].
Unrecognised details are printed as WARNINGs and NOT drawn. The template guide is never loaded.
"""
import argparse
import math
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import construction
import cuts
import identity
import motifs
import prints
import realistic
import recipes
import shading_custom
import shoes as shoe_styles
from clothing import (ROOT, S, H, M, OUTFIT, Part, Canvas, hex_rgb, shade, rgba, load_regions,
                      load_shading, apply_shading, mirror_strip, build_pieces, paste_pieces, seeded_noise)

SHADING_STRENGTH = 1.4   # contrast boost applied to the shared shading layers (1.0 = as stored)

# keyword in a details entry -> feature flag ("_..." = recognised, nothing extra to draw)
FEATURES = {
    "torso": [("hood", "hood"), ("drawstring", "drawstrings"), ("drawcord", "drawstrings"),
              ("kangaroo", "kangaroo_pocket"), ("crew", "crew_collar"), ("zip", "zip"),
              ("hem", "_hem"), ("collar", "crew_collar"), ("crop", "_crop")],
    "arms": [("cuff", "rib_cuffs"), ("sleeve", "_sleeve")],
    "legs": [("cuff", "rib_cuffs"), ("side pocket", "side_pockets"), ("sneaker", "_shoes"), ("shoe", "_shoes"),
             ("waistband", "_waist"), ("drawstring", "drawstrings"), ("drawcord", "drawstrings"),
             ("elastic", "_waist"), ("pleat", "pleats"), ("belt loop", "belt_loops"), ("button", "button")],
}
HEMS = ("rib", "plain", "belt", "none")
WARN = []   # warnings collected while drawing limbs (reset per render)
RS = {}     # per-render shading setup: real (realistic family), layer, strength, seed, wrinkles
COVERAGE = ("full", "top_only", "bottom_only")
LEG_TYPES = ("trousers", "skirt", "shorts")
KIND_MATERIAL = {"tee": "cotton", "shirt": "cotton", "hoodie": "cotton", "sweater": "knit", "jacket": "nylon",
                 "bomber": "nylon", "suit": "cotton", "corset": "leather", "jeans": "denim", "trousers": "cotton",
                 "joggers": "cotton", "shorts": "nylon", "skirt": "cotton"}
WAISTBANDS = ("elastic", "plain", "none")
LEGWEAR = ("tights", "socks", "bare")


def parse_features(sec, name):
    flags, warnings = set(), []
    for item in sec.get("details") or []:
        low = str(item).lower()
        hit = [flag for key, flag in FEATURES[name] if key in low]
        if not hit:
            warnings.append(f"{name}: detail not supported by renderer, not drawn: '{item}'")
        flags.update(hit)
    return flags, warnings


class Colours:
    def __init__(self, palette):
        pal = [hex_rgb(h) for h in (palette or ["#808080"])]
        self.pal = pal
        self.body = pal[0]
        self.trim = pal[1] if len(pal) > 1 else shade(self.body, 0.9)
        lum = sum(self.body) / 3
        self.accent = pal[2] if len(pal) > 2 else (shade(self.body, 1.7) if lum < 110 else shade(self.body, 0.5))

    def get(self, i):
        return self.pal[i % len(self.pal)]


# ---------------------------------------------------------------- patterns

def paint_pattern(c, pattern, col, params):
    """Periodic patterns; phases put every seam in the middle of a band, and accent lines are
    mirror-symmetric, so patterns meet at side seams, the shoulder and the hip."""
    P = c.P
    c.band(-M, H + M, rgba(col.body))
    if pattern in (None, "", "solid"):
        return
    if pattern == "swatch":                         # owner-generated fabric swatch, tiled (64 px, mirrored: seams meet)
        import library
        el = library.element(str(params.get("element")))
        tones = None if params.get("recolour") is False else (col.body, col.trim, col.accent)
        t = library.tile_image(el, tones, int(params.get("period", 64)))
        t = t.resize((t.width * S, t.height * S), Image.LANCZOS)
        for y in range(0, c.img.height, t.height):
            for x in range(0, c.img.width, t.width):
                c.img.paste(t, (x, y), t)
        # top / bottom faces are built from the rows just outside 0..H: repeat the edge rows there so fine
        # swatches meet the top and bottom faces (the same trick the stripe phases use)
        for edge, rng in ((0, range(-4, 0)), (H - 1, range(H, H + 4))):
            row = c.img.crop((0, (edge + M) * S, c.img.width, (edge + M + 1) * S))
            for v in rng:
                c.img.paste(row, (0, (v + M) * S))
        c.d = ImageDraw.Draw(c.img)
        return
    if pattern == "stripes":
        w = int(params.get("width", 8))
        if 128 % (2 * w):
            raise SystemExit("stripe width must be 2, 4, 8, 16, 32 or 64 so stripes wrap and line up")
        if params.get("direction", "horizontal") == "vertical":
            for u in range(0, P, 2 * w):
                c.rect(u + w / 2, -M, u + w / 2 + w, H + M, rgba(col.get(1)))
        else:
            for v in range(-M - 2 * w, H + M, 2 * w):
                c.band(v + w / 2, v + w / 2 + w, rgba(col.get(1)))
        return
    if pattern == "plaid":
        period, band, ph = 32, 12, -6
        hb, vb = Canvas(c.part, "L", 0), Canvas(c.part, "L", 0)
        for v in range(-64, H + M, period):
            hb.band(v + ph, v + ph + band, 140)
        for u in range(0, P, period):
            vb.rect(u + ph, -M, u + ph + band, H + M, 140)
        over = Image.new("RGBA", c.img.size, rgba(col.get(1)))
        c.img = Image.composite(over, c.img, hb.img)
        c.img = Image.composite(over, c.img, vb.img)
        c.d = ImageDraw.Draw(c.img)
        for v in range(-64, H + M, period):
            c.band(v + 15.25, v + 16.75, rgba(col.get(2)))
        for u in range(0, P, period):
            c.rect(u + 15.25, -M, u + 16.75, H + M, rgba(col.get(2)))
        return
    if pattern == "gradient":
        a, b = col.get(0), col.get(1)
        for v in range(-M, H + M):
            t = min(1, max(0, v / H))
            c.band(v, v + 1, rgba(tuple(round(x + (y - x) * t) for x, y in zip(a, b))))
        return
    if pattern == "colour-block":
        c.band(52, H + M, rgba(col.get(1)))
        return
    if pattern == "knit":
        dark = rgba(shade(col.body, 0.84))
        for u in range(0, P, 4):
            for v in range(-M, H + M, 3):
                c.line([(u + 0.4, v), (u + 2, v + 2.2), (u + 3.6, v)], dark, 0.6)
        return
    if pattern == "denim":
        light = rgba(shade(col.body, 1.14))
        for k in range(-(H + 2 * M) - P, 2 * P, 2):
            c.d.line([((k + P) * S, 0), ((k + P + H + 2 * M) * S, (H + 2 * M) * S)], fill=light, width=2)
        return
    if pattern in prints.WASHES:                   # washed fabrics (periodic, mirror-symmetric)
        c.img = apply_shading(c.img, prints.wash_map(c.part, pattern), 1.0)
        c.d = ImageDraw.Draw(c.img)
        return
    if pattern == "checker":                       # 8 px squares, seams fall mid-square
        for v in range(-M - 4, H + M, 8):
            for u in range(-4, P, 8):
                if ((u + 4) // 8 + (v + 4) // 8) % 2:
                    c.rect(u, v, u + 8, v + 8, rgba(col.get(1)))
        return
    if pattern == "argyle":                        # diamonds centred on every 32 px column (mirror-symmetric)
        for v in range(-64, H + M + 32, 32):
            for u in range(0, P + 32, 32):
                cc = col.get(1) if ((u // 32) + (v // 32)) % 2 else col.body
                c.polygon([(u, v - 16), (u + 16, v), (u, v + 16), (u - 16, v)], rgba(cc))
        # dotted overcheck along the diamond edges: dots rasterise symmetrically, so the lines meet
        # cleanly where they cross a seam (solid thin diagonals did not)
        dot = rgba(col.get(2))
        for n in range(0, P, 32):
            for v in range(-M, H + M, 2):
                for u in (v + 16 + n, -v + 16 + n):
                    c.ellipse(u % P, v, 0.42, 0.42, dot)
        return
    if pattern == "cable":                         # knit ground + cable columns between seams
        paint_pattern(c, "knit", col, params)
        dark, light = rgba(shade(col.body, 0.7)), rgba(shade(col.body, 1.18))
        for u0 in range(16, P, 32):
            c.line([(u0 - 6, -M), (u0 - 6, H + M)], dark, 0.9)
            c.line([(u0 + 6, -M), (u0 + 6, H + M)], dark, 0.9)
            for ph, colr in ((0, dark), (math.pi, light)):
                pts = [(u0 + 3.5 * math.sin(v / 12 * 2 * math.pi + ph), v) for v in range(-M, H + M)]
                c.line(pts, colr, 1.3)
        return
    if pattern == "leopard":                       # symmetric 32 px tile of rosettes
        spots = [(6, 5, 3.2), (16, 14, 2.6), (6, 24, 3.0), (0, 14, 2.2), (11, 30, 2.0)]
        for v in range(-64, H + M, 32):
            for u in range(0, P + 32, 32):
                for sx, sy, r in spots:
                    for x in {sx, -sx}:
                        c.ellipse(u + x, v + sy, r, r * 0.8, rgba(col.get(2)), rgba(col.get(1)), 0.9)
        return
    raise SystemExit(f"unknown base_pattern '{pattern}'")


def grain(part, amount, streaks=False):
    """Periodic fabric noise as an L shading map (128 = neutral), wrap-canvas sized."""
    tile = seeded_noise(64, H + 2 * M, amount, 11 + part.P)
    if streaks:
        st = seeded_noise(64, 6, amount * 1.4, 17 + part.P).resize((64, H + 2 * M), Image.BILINEAR)
        tile = ImageChops.add(tile, st, 1.0, -128)
    wide = Image.new("L", (3 * part.P, H + 2 * M))
    for x in range(0, wide.width, 64):
        wide.paste(tile, (x, 0))
    return wide.resize((wide.width * S, wide.height * S), Image.NEAREST).filter(ImageFilter.GaussianBlur(0.9 * S))  # correlated grain: seams agree


def rib(c, v0, v1, colour, u0=None, u1=None):
    """Ribbed band: solid colour with fine vertical rib lines (period 2 px, wraps cleanly)."""
    if u0 is None:
        c.band(v0, v1, rgba(colour))
        u0, u1 = 0, c.P
    else:
        c.rect(u0, v0, u1, v1, rgba(colour))
    dark = rgba(shade(colour, 0.86))
    for u in range(int(u0), int(u1), 2):
        c.rect(u + 1.2, v0, u + 1.9, v1, dark)


def rows_from(dst, src, v0, v1=H + M):
    """Copy strip rows [v0, v1) of src into dst (both wrap canvases of the same part)."""
    box = (0, int((v0 + M) * S), dst.img.width, int((v1 + M) * S))
    dst.img.paste(src.img.crop(box), box[:2])
    dst.d = ImageDraw.Draw(dst.img)


# ---------------------------------------------------------------- torso

def torso_features(c, col, flags, fx, hem_type, hem, warnings):
    """Top garment from the neckline down to `hem` (rows below are replaced by the legs)."""
    band_top = {"rib": hem - 12, "plain": hem - 2, "belt": hem - 6, "none": hem}[hem_type]
    if hem_type == "rib":
        rib(c, band_top, hem, col.trim)
    elif hem_type == "plain":
        c.band(band_top, hem, rgba(shade(col.body, 0.8)))
    elif hem_type == "belt":
        c.band(band_top, hem, rgba(col.trim))
        c.band(band_top, band_top + 0.7, rgba(shade(col.trim, 1.25)))
        c.rect(59, band_top - 1, 69, hem + 1, rgba(col.accent))              # plain buckle, no emblem
        c.rect(61.5, band_top + 1, 66.5, hem - 1, rgba(col.trim))
    if hem_type != "none":
        fx["sh"].band(band_top - 1.2, band_top, 40)
        fx["hi"].band(band_top + 0.5, band_top + 1.5, 18)
    fx["sh"].band(hem, hem + 2.5, 30)                                       # top garment casts onto what is below
    lining = rgba(shade(col.body, 0.5))
    if "hood" in flags:
        c.band(-M, -22, lining)
        c.band(-22, -15, rgba(col.trim))
        rim = [(32, -19), (36, -6), (46, 6), (64, 13), (82, 6), (92, -6), (96, -19)]
        c.line(rim, rgba(shade(col.trim, 0.7)), 9)
        c.line(rim, rgba(col.trim), 6.5)
        fx["sh"].line([(38, -2), (48, 10), (64, 17), (80, 10), (90, -2)], 34, 3)
        hood = [(212, -15), (300, -15), (302, 10), (296, 30), (280, 42), (256, 47), (232, 42), (216, 30), (210, 10)]
        c.polygon(hood, None, rgba(shade(col.body, 0.72)), 1.2)
        fx["sh"].polygon(hood, 8)
        c.line([(256, -15), (256, 46)], rgba(shade(col.body, 0.82)), 0.9)
        fx["sh"].line([(214, 34), (234, 47), (256, 52), (278, 47), (298, 34)], 40, 4)
        fx["sh"].line([(222, 4), (230, 26)], 18, 3); fx["sh"].line([(290, 4), (282, 26)], 18, 3)
        fx["hi"].ellipse(256, 14, 26, 12, 14)
    else:
        c.band(-M, -9, lining)
        rib(c, -9, -2, col.trim)
        rib(c, -2, 3, col.trim, 40, 88)
        fx["sh"].line([(40, 4), (88, 4)], 24, 1.5)
    sec = fx.get("sec") or {}
    construction.draw("torso", sec.get("parts"), c, col, fx, {"band_top": band_top, "hem": hem}, warnings)
    identity.torso_identity(c, fx, fx.get("identity"), {"band_top": band_top, "hood": "hood" in flags}, c.part)
    cuts.torso_cut(fx, sec.get("cut"), col.trim, c, rgba, shade)
    if "zip" in flags:
        c.line([(64, 3), (64, band_top)], rgba(shade(col.body, 0.55)), 1.6)
        for v in range(4, int(band_top), 2):
            c.line([(63.2, v), (64.8, v)], rgba(shade(col.trim, 1.2)), 0.5)
        c.rect(62.6, 4, 65.4, 9, rgba(col.accent))
        fx["sh"].line([(65.5, 3), (65.5, band_top)], 22, 1.5)
    if "drawstrings" in flags:
        for top, bot in (((55, 10), (53, 42)), ((73, 10), (75, 45))):
            c.ellipse(top[0], top[1], 1.6, 1.6, rgba(shade(col.body, 0.45)))
            c.line([top, bot], rgba(shade(col.accent, 0.7)), 2.2)
            c.line([top, bot], rgba(col.accent), 1.4)
            c.rect(bot[0] - 1.1, bot[1], bot[0] + 1.1, bot[1] + 3.5, rgba(shade(col.accent, 0.75)))
            fx["sh"].line([(top[0] + 1.5, top[1] + 2), (bot[0] + 1.5, bot[1] + 4)], 22, 1.8)
    if "kangaroo_pocket" in flags:
        if band_top - 64 < 28:
            warnings.append("torso: kangaroo pocket needs hem_line >= 104 with a rib hem; not drawn")
        else:
            pts = [(36, 64), (92, 64), (106, 88), (106, band_top), (22, band_top), (22, 88)]
            stitch = rgba(shade(col.body, 0.8))
            c.line([(36, 65.2), (92, 65.2)], stitch, 0.7)
            c.line([(23.2, 88), (23.2, band_top)], stitch, 0.7)
            c.line([(104.8, 88), (104.8, band_top)], stitch, 0.7)
            for a, b in ((pts[0], pts[5]), (pts[1], pts[2])):
                c.line([a, b], rgba(shade(col.body, 0.55)), 1.5)
            fx["sh"].line([(37, 68), (25, 89)], 40, 3.5); fx["sh"].line([(91, 68), (103, 89)], 40, 3.5)
            fx["sh"].line([(36, 67), (92, 67)], 16, 2.5)
            fx["hi"].line([(38, 62.8), (90, 62.8)], 14, 1.2)
    motifs.draw_decor(c, "torso", fx.get("decor"), col, fx,
                      {"scatter": (6, band_top - 4), "row": 30, "lace_hem": hem - 5, "hood": "hood" in flags, "band_top": band_top,
                       "stitch_cols": [24, 104, 216, 296]}, warnings)


# ---------------------------------------------------------------- arms

def arm_features(c, col, flags, fx, sec, under):
    """`under` = (canvas, colours, flags) of a long under-sleeve, or None."""
    cuff, end, short = OUTFIT["cuff_top"], OUTFIT["sleeve_end"], OUTFIT["short_sleeve"]
    is_short = str(sec.get("sleeves", "long")).lower() == "short"
    motifs.draw_decor(c, "arms", sec.get("decor"), col, fx,
                      {"scatter": (6, (short if is_short else cuff) - 4), "row": 20,
                       "lace_cuff": (short if is_short else end) - 5, "stitch_cols": [32, 160]}, WARN)
    if sec.get("sleeve_contrast"):                                        # visible shoulder seam
        c.band(-3, 1.4, rgba(shade(col.body, 0.55)))                      # continues onto the arm's top face
        for u in range(0, c.P, 3):
            c.rect(u + 0.5, 3.2, u + 2, 3.9, rgba(shade(col.body, 0.7)))
        fx["sh"].band(3, 4.5, 20)                                          # kept below the edge rows
    is_short_now = str(sec.get("sleeves", "long")).lower() == "short"
    actx = {"cuff": short - 4 if is_short_now else cuff, "end": short if is_short_now else end}
    construction.draw("arms", sec.get("parts"), c, col, fx, actx, WARN)
    identity.arm_identity(c, fx, sec.get("_identity"), actx)
    cuts.arm_cut(fx, sec.get("_cut"))
    if str(sec.get("sleeves", "long")).lower() == "short":
        if under:
            uc, ucol, uflags = under
            rows_from(c, uc, short)                                       # long under-sleeve below the short one
            if "rib_cuffs" in uflags:
                rib(c, cuff, end, ucol.trim)
            else:
                c.band(end - 2, end, rgba(shade(ucol.body, 0.8)))
            fx["alpha"].band(end, H + M, 0)
        else:
            fx["alpha"].band(short, H + M, 0)
        c.band(short - 4, short, rgba(shade(col.body, 0.92)))
        fx["sh"].band(short, short + 2.5, 34)
        return
    if "rib_cuffs" in flags:
        rib(c, cuff, end, col.trim)
    else:
        c.band(end - 2, end, rgba(shade(col.body, 0.8)))
    fx["alpha"].band(end, H + M, 0)


# ---------------------------------------------------------------- legs (right-leg convention:
# front u 0-64 (u=0 is the outer edge, u=64 the centre front), inner face 64-128, back 128-192,
# outer face 192-256; rows v < 0 become the torso hip)

def waistband(c, col, flags, fx, wv, kind):
    b = OUTFIT["band"]
    if kind == "elastic":
        rib(c, wv, wv + b, col.trim)
    elif kind == "plain":
        c.band(wv, wv + b, rgba(shade(col.body, 0.92)))
        c.band(wv + b - 0.8, wv + b, rgba(shade(col.body, 0.7)))
    if kind != "none":
        fx["hi"].band(wv + 0.3, wv + 1.3, 18)
        fx["sh"].band(wv + b, wv + b + 1.5, 34)
    if "belt_loops" in flags:
        for u in (14, 44, 150, 176, 222):
            c.rect(u, wv - 0.5, u + 2.2, wv + b + 1, rgba(shade(col.body, 0.82)))
    if "button" in flags:
        # centred on the front seam: the mirrored left leg supplies the other half -> one button
        c.ellipse(64, wv + b / 2, 2.4, 2.4, rgba(col.accent), rgba(shade(col.accent, 0.6)), 0.6)
    if "drawstrings" in flags:
        c.ellipse(60, wv + b / 2, 1.3, 1.3, rgba(shade(col.trim, 0.45)))
        c.ellipse(61, wv + b / 2 + 3, 3, 2, None, rgba(col.accent), 1.1)
        c.line([(61, wv + b / 2 + 4), (58, wv + b + 14)], rgba(shade(col.accent, 0.7)), 2.0)
        c.line([(61, wv + b / 2 + 4), (58, wv + b + 14)], rgba(col.accent), 1.3)
        fx["sh"].line([(60, wv + b + 2), (60, wv + b + 16)], 18, 2)


def shoes(c, col, fx, sec):
    top, sole_top = OUTFIT["shoe_top"], OUTFIT["sole_top"]
    sp = [hex_rgb(h) for h in (sec.get("shoe_palette") or ["#f2f2f2", "#d4d4d4"])]
    upper, sole = sp[0], sp[1] if len(sp) > 1 else shade(sp[0], 0.85)
    c.band(top, sole_top, rgba(upper))
    c.band(sole_top, H + M, rgba(sole))
    for v in range(H + 3, H + M, 4):
        c.band(v, v + 1.2, rgba(shade(sole, 0.82)))
    c.band(top, top + 1.4, rgba(shade(upper, 0.78)))
    c.line([(-2, sole_top - 3.5), (c.P + 2, sole_top - 3.5)], rgba(shade(upper, 0.86)), 0.6)
    c.rect(23, top, 41, top + 8, rgba(shade(upper, 0.93)))
    lace = rgba(shade(col.accent, 0.8) if sum(col.accent) < 600 else shade(upper, 0.6))
    for v in (top + 2.5, top + 5, top + 7.5):
        c.line([(24.5, v), (39.5, v)], lace, 0.9)
    c.rect(155, top, 165, top + 7, rgba(shade(upper, 0.85)))
    fx["sh"].line([(22, top + 9), (42, top + 9)], 20, 1.5)


def leg_features(c, col, flags, fx, sec):
    cuff, top = OUTFIT["leg_cuff_top"], OUTFIT["shoe_top"]
    wv = int(sec.get("waist_line", OUTFIT["waist_line"])) - H     # waistband top in leg rows (< 0)
    fx["alpha"].band(-M, wv, 0)                                    # nothing above the waistband
    has_shoes = str(sec.get("shoes") or "").strip().lower() not in ("", "none", "no", "barefoot")
    kind = str(sec.get("type", "trousers")).lower()
    style = str(sec.get("shoe_style", "basic")).lower()
    if has_shoes and style != "basic":
        top = shoe_styles.shoe_top(style)
    if kind in ("skirt", "shorts"):
        length = float(sec.get("skirt_length" if kind == "skirt" else "shorts_length", 40))
        if kind == "shorts":                                         # split hem + a side vent on the outer face
            c.band(length - 3, length, rgba(shade(col.body, 0.85)))
            c.line([(224, length - 8), (224, length)], rgba(shade(col.body, 0.55)), 0.9)
            fx["sh"].line([(225, length - 8), (225, length)], 20, 1.2)
        if "pleats" in flags:
            for u in range(0, c.P, 8):
                c.line([(u + 4, wv + OUTFIT["band"]), (u + 4, length)], rgba(shade(col.body, 0.78)), 0.8)
                c.line([(u + 5, wv + OUTFIT["band"]), (u + 5, length)], rgba(shade(col.body, 1.12)), 0.5)
                fx["sh"].rect(u + 4, wv + OUTFIT["band"], u + 8, length, 10)
        c.band(length - 2, length, rgba(shade(col.body, 0.8)))
        legwear = str(sec.get("legwear", "tights" if kind == "skirt" else "bare")).lower()
        lp = [hex_rgb(h) for h in (sec.get("legwear_palette") or ["#1a1a1a"])]
        if legwear == "tights":
            c.band(length, top, rgba(lp[0]))
        elif legwear == "socks":
            sock_top = float(sec.get("sock_top", 70))
            c.band(sock_top, top, rgba(lp[0]))
            rib(c, sock_top, sock_top + 4, shade(lp[0], 0.95))
            fx["alpha"].band(length, sock_top, 0)
        else:
            fx["alpha"].band(length, top if has_shoes else H + M, 0)
        fx["sh"].band(length, length + 3, 34)                       # skirt casts onto the legs
    else:
        if "side_pockets" in flags:
            pv = wv + OUTFIT["band"]
            c.line([(5, pv + 1), (13, pv + 15)], rgba(shade(col.body, 0.55)), 1.3)
            fx["sh"].line([(8, pv + 1), (15, pv + 15)], 30, 3)
        if "rib_cuffs" in flags:
            rib(c, cuff, top, col.trim)
        else:
            c.band(top - 2, top, rgba(shade(col.body, 0.8)))
    bottom = (float(sec.get("skirt_length" if kind == "skirt" else "shorts_length", 40)) if kind in ("skirt", "shorts")
              else (cuff if "rib_cuffs" in flags else top - 2))
    motifs.draw_decor(c, "legs", sec.get("decor"), col, fx,
                      {"scatter": (wv + OUTFIT["band"] + 4, bottom - 4), "row": 40, "lace_hem": bottom - 5,
                       "waist_leg": wv, "body": col.body, "stitch_cols": [32, 224], "avoid_rows": (0,)}, WARN)
    identity.leg_identity(c, fx, sec.get("_identity"), {"wv": wv, "bottom": bottom - 3})
    waistband(c, col, flags, fx, wv, str(sec.get("waistband", "elastic")).lower())
    construction.draw("legs", sec.get("parts"), c, col, fx, {"wv": wv, "bottom": bottom}, WARN)
    if has_shoes:
        if style == "basic":
            shoes(c, col, fx, sec)
        else:
            sp = [hex_rgb(h) for h in (sec.get("shoe_palette") or ["#f2f2f2", "#d4d4d4"])]
            up = sp[0]
            sole = sp[1] if len(sp) > 1 else shade(up, 0.85)
            acc = sp[2] if len(sp) > 2 else col.accent
            shoe_styles.draw(style, c, fx, up, sole, acc)
    elif kind == "trousers" or str(sec.get("legwear", "tights" if kind == "skirt" else "bare")).lower() != "bare":
        fx["alpha"].band(top, H + M, 0)


# ---------------------------------------------------------------- pipeline

def start(part, sec):
    col = Colours(sec.get("palette"))
    c = Canvas(part)
    pattern = sec.get("base_pattern") or "solid"
    paint_pattern(c, pattern, col, sec.get("pattern") or {})
    if not RS.get("real"):            # realistic family: crisp material texture comes with the shading map instead
        c.img = apply_shading(c.img, grain(part, 12 if pattern == "denim" else 5, streaks=pattern == "denim"), 1.0)
    c.d = ImageDraw.Draw(c.img)
    fx = {"c": c, "sh": Canvas(part, "L", 0), "hi": Canvas(part, "L", 0), "alpha": Canvas(part, "L", 255)}
    return c, col, fx


def boost(shading, weight=1.0):
    k = SHADING_STRENGTH * weight
    return shading.point(lambda s: max(0, min(255, round(128 + (s - 128) * k))))


def material_of(sec, region):
    kind = str(sec.get("garment_kind") or ("skirt" if region == "leg" and str(sec.get("type")) == "skirt" else
                                          "shorts" if region == "leg" and str(sec.get("type")) == "shorts" else
                                          "trousers" if region == "leg" else "tee")).lower()
    return str(sec.get("material") or KIND_MATERIAL.get(kind, "cotton")).lower(), kind


def body_shading(part, region, sec, shading):
    """The base shading map for one strip: shared layers (decorated / print), weaker when a collected
    layer adds the form later, or the realistic material + wrinkle map."""
    layered = bool(RS.get("layer")) and (region in ("torso", "arm") or (region == "leg" and RS.get("layer_legs")))
    if RS.get("real") and region:
        mat, kind = material_of(sec or {}, region)
        out = realistic.shading_map(part, region, kind, mat, RS.get("seed", 0), base=boost(shading),
                                    base_weight=0.3 if layered else 0.7,
                                    strength=RS.get("wrinkles", 1.0) * (0.35 if layered else 1.0))   # the layer brings the folds
        if region == "leg":   # footwear keeps the plain shared shading: no fabric texture or folds on shoes
            has_shoes = str(sec.get("shoes") or "").strip().lower() not in ("", "none", "no", "barefoot")
            if has_shoes:
                style = str(sec.get("shoe_style", "basic")).lower()
                top = shoe_styles.shoe_top(style) if style != "basic" else OUTFIT["shoe_top"]
                y = int((top + M) * S)
                out.paste(boost(shading).crop((0, y, out.width, out.height)), (0, y))
        return out
    return boost(shading, 0.35 if layered else 1.0)


def finish(part, strip, fx, shading, before_features=None, region=None, sec=None):
    strip = apply_shading(strip, body_shading(part, region, sec, shading))
    if before_features:
        strip = before_features(strip)
    fx["sh"].blur(1.2); fx["hi"].blur(1.2)
    feat = ImageChops.subtract(ImageChops.add(Image.new("L", fx["sh"].img.size, 128), fx["hi"].img), fx["sh"].img)
    strip = apply_shading(strip, feat.crop((part.P * S, 0, 2 * part.P * S, feat.height)))
    strip.putalpha(ImageChops.multiply(strip.getchannel("A"), fx["alpha"].strip()))
    return strip


def render_limb(part, sec, kind, flags, shading, under_sec=None):
    c, col, fx = start(part, sec)
    if kind == "arm":
        under = None
        if under_sec:
            uc, ucol, _ = start(part, under_sec)
            uflags, _ = parse_features(under_sec, "arms")
            under = (uc, ucol, uflags)
        arm_features(c, col, flags, fx, sec, under)
    else:
        leg_features(c, col, flags, fx, sec)
    return finish(part, c.strip(), fx, shading, region=kind, sec=sec)


def limb_pair(right, sec, kind, flags):
    """Right limb strip + left limb strip. The left limb is always drawn in the right-limb
    convention and mirrored, so inner/outer features land on the correct faces."""
    shading = load_shading(kind)
    under = sec.get("under") if kind == "arm" else None
    r = render_limb(right, sec, kind, flags, shading, under)
    if sec.get("mirror", True):
        return r, mirror_strip(r, right)
    lsec = {**sec, **(sec.get("left") or {})}
    lflags, _ = parse_features(lsec, "arms" if kind == "arm" else "legs")
    return r, mirror_strip(render_limb(right, lsec, kind, lflags, shading, lsec.get("under") if kind == "arm" else None), right)


def legs_into_torso(torso_strip, cut, rleg_strip, lleg_strip):
    """Replace torso rows v >= cut with the matching leg-strip rows (leg v = torso v - 128)."""
    spans = [((0, 64), rleg_strip, 0), ((64, 128), lleg_strip, 0), ((128, 192), lleg_strip, 64),
             ((192, 256), lleg_strip, 128), ((256, 320), rleg_strip, 128), ((320, 384), rleg_strip, 192)]
    out = torso_strip.copy()
    y_t0, y_t1 = int((cut + M) * S), (H + 2 * M) * S
    y_l0 = int((cut - H + M) * S)
    for (u0, u1), leg, lu in spans:
        out.paste(leg.crop((lu * S, y_l0, (lu + u1 - u0) * S, y_l0 + (y_t1 - y_t0))), (u0 * S, y_t0))
    return out


def sections(spec, spec_path):
    for key in ("torso", "arms", "legs"):
        if not isinstance(spec.get(key), dict):
            raise SystemExit(f"{spec_path}: missing '{key}' section (one-outfit spec required)")
    tsec, lsec = spec["torso"], spec["legs"]
    asec = {"palette": tsec.get("palette"), "base_pattern": tsec.get("base_pattern"),
            "pattern": tsec.get("pattern"), "material": tsec.get("material"),
            "garment_kind": tsec.get("garment_kind"), **spec["arms"]}
    asec["_cut"] = tsec.get("cut")
    asec["_identity"] = lsec["_identity"] = spec.get("identity")
    if str(lsec.get("type", "trousers")).lower() not in LEG_TYPES:
        raise SystemExit(f"{spec_path}: legs.type must be one of {LEG_TYPES}")
    if str(lsec.get("shoe_style", "basic")).lower() not in shoe_styles.STYLES:
        raise SystemExit(f"{spec_path}: legs.shoe_style must be one of {shoe_styles.STYLES}")
    if str(spec.get("coverage", "full")) not in COVERAGE:
        raise SystemExit(f"{spec_path}: coverage must be one of {COVERAGE}")
    under = asec.get("under")
    if under:
        if str(asec.get("sleeves", "long")).lower() != "short":
            raise SystemExit(f"{spec_path}: arms.under (layered long sleeve) needs arms.sleeves: short")
        asec["under"] = {"base_pattern": "solid", **under}
    hem_type = str(tsec.get("hem", "rib")).lower()
    if hem_type not in HEMS:
        raise SystemExit(f"{spec_path}: torso.hem must be one of {HEMS}")
    if str(lsec.get("waistband", "elastic")).lower() not in WAISTBANDS:
        raise SystemExit(f"{spec_path}: legs.waistband must be one of {WAISTBANDS}")
    if str(lsec.get("type", "trousers")).lower() in ("skirt", "shorts") and str(lsec.get("legwear", "tights")).lower() not in LEGWEAR:
        raise SystemExit(f"{spec_path}: legs.legwear must be one of {LEGWEAR}")
    return tsec, asec, lsec, hem_type


def render(spec_path, outdir):
    raw = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    spec = recipes.resolve(raw)                    # recipes -> concrete decor entries (same seed, same design)
    oid = spec.get("id") or Path(spec_path).stem
    tsec, asec, lsec, hem_type = sections(spec, spec_path)
    hem = float(tsec.get("hem_line", OUTFIT["hem_line"]))
    regions = load_regions()
    warnings = []
    tflags, w = parse_features(tsec, "torso"); warnings += w
    aflags, w = parse_features(asec, "arms"); warnings += w
    if asec.get("under"):
        warnings += parse_features(asec["under"], "arms")[1]
    lflags, w = parse_features(lsec, "legs"); warnings += w

    torso = Part("shirt", "torso", regions)
    rarm, larm = Part("shirt", "right_arm", regions), Part("shirt", "left_arm", regions)
    rleg, lleg = Part("pants", "right_leg", regions), Part("pants", "left_leg", regions)

    WARN.clear()
    sh = spec.get("shading") or {}
    RS.clear()
    RS.update({"real": spec.get("family") == "realistic" or sh.get("mode") == "realistic",
               "layer": shading_custom.effective_layer(spec),     # default for every family: the owner's three templates stacked
               "strength": float(sh.get("strength", 1.0)), "seed": int(sh.get("seed", 0)),
               "wrinkles": float(sh.get("wrinkles", 1.0))})
    if RS["layer"]:
        try:
            RS["layer_legs"] = "legs" in (shading_custom.load_layer(RS["layer"])[1].get("parts") or [])
        except SystemExit:
            warnings.append(f"shading layer '{RS['layer']}' not found: not applied (validate.py fails this spec)")
            RS["layer"] = None
    coverage = str(spec.get("coverage", "full"))
    rleg_s, lleg_s = limb_pair(rleg, lsec, "leg", lflags)
    rarm_s, larm_s = limb_pair(rarm, asec, "arm", aflags)

    c, col, fx = start(torso, tsec)
    fx["decor"] = tsec.get("decor")
    fx["sec"] = tsec
    fx["identity"] = spec.get("identity")
    if coverage == "bottom_only":                            # separates: torso shows only the bottom garment
        wl = float(lsec.get("waist_line", OUTFIT["waist_line"]))
        fx["alpha"].band(-M, wl, 0)
        cut_row = min(hem, wl)
    else:
        torso_features(c, col, tflags, fx, hem_type, hem, warnings)
        cut_row = hem
    if coverage == "top_only":                               # nothing below the top's hem
        fx["alpha"].band(hem, H + M, 0)
    torso_s = finish(torso, c.strip(), fx, load_shading("torso"),
                     before_features=lambda s: legs_into_torso(s, cut_row, rleg_s, lleg_s), region="torso", sec=tsec)

    warnings += sorted(set(WARN))
    torso_pieces = build_pieces(torso_s, torso)            # built once, pasted into both files
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    outs = []
    files = {"full": ("shirt", "pants"), "top_only": ("shirt",), "bottom_only": ("pants",)}[coverage]
    for garment, limbs in (("shirt", ((rarm, rarm_s), (larm, larm_s))), ("pants", ((rleg, rleg_s), (lleg, lleg_s)))):
        if garment not in files:
            continue
        canvas = Image.new("RGBA", tuple(regions["canvas"]), (0, 0, 0, 0))
        paste_pieces(canvas, torso_pieces)
        for part, strip in limbs:
            paste_pieces(canvas, build_pieces(strip, part))
        if RS["layer"]:
            canvas = shading_custom.apply_layer(canvas, RS["layer"], RS["strength"], garment, regions)
        out = outdir / f"{oid}-{garment}.png"
        canvas.save(out, "PNG")
        outs.append(out)
    if raw.get("recipes"):
        (outdir / f"{oid}-resolved.yaml").write_text(yaml.safe_dump(spec, sort_keys=False, width=200), encoding="utf-8")
        recipes.log_recipes(raw, spec_path)
    return outs, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", nargs="+")
    ap.add_argument("-o", "--outdir", default=str(ROOT / "renders"))
    a = ap.parse_args()
    for sp in a.specs:
        outs, warnings = render(sp, a.outdir)
        print(f"rendered {sp} -> " + ", ".join(str(o) for o in outs))
        for w in warnings:
            print("  WARNING:", w)


if __name__ == "__main__":
    sys.exit(main())

"""Reusable element library: styles/references/library/<id>.json (+ optional <id>.png mask).

Element file (JSON):
  id, name, motif (category, e.g. "skull"), styles [..], mood [..], size (small|medium|large: smallest
  size it reads well at), families [decorated, print], symmetric, band (true = wide horizontal element),
  source ("original" or "public-domain"), shapes [...] or mask "<id>.png".
Shapes use a unit box (-1..1, y down) and are painted in order, like layers:
  {"t": "poly", "pts": [[x, y], ...], "tone": 0|1|2|"cut", "stroke": w?}
  {"t": "ellipse", "c": [x, y], "r": [rx, ry], "tone": .., "stroke": w?}
  {"t": "line", "pts": [[x, y], ...], "w": width, "tone": ..}
Tones: 0 = main ink, 1 = shadow tone, 2 = highlight tone, "cut" = punch through to the fabric.
Mask elements: L-mode PNG where 255 = tone 0, 170 = tone 1, 85 = tone 2, 0 = empty.
"""
import json
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops

from clothing import ROOT, S, M, H, Canvas, rgba, shade

LIB = ROOT / "styles" / "references" / "library"
BLOCKED_WORDS = ("cross", "crucifix", "church", "religio", "pentagram", "swastika", "occult", "text", "letter",
                 "logo", "brand", "gore", "blood", "wound", "flag")
WHOLE_WORDS = ("text", "gore")   # matched as whole words only ("texture", "gorgeous" are fine)


def blocked(text):
    """Blocked subjects in an element's id / name / motif: word-start match (cross, crossed, logos ...)."""
    import re
    low = text.lower()
    return [w for w in BLOCKED_WORDS
            if re.search(r"(?<![a-z])" + w + (r"s?(?![a-z])" if w in WHOLE_WORDS else ""), low)]


MIN_LINE_PX = 1.0     # thinnest stroke drawn (output px); see calibration/print-linewidth


@lru_cache(maxsize=1)
def load_library():
    lib = {}
    for p in sorted(LIB.glob("*.json")):
        el = json.loads(p.read_text(encoding="utf-8"))
        lib[el["id"]] = el
    return lib


def element(eid):
    lib = load_library()
    if eid not in lib:
        raise KeyError(f"element '{eid}' is not in styles/references/library")
    return lib[eid]


class Masks:
    """Three tone masks (wrap canvases) painted like layers, then composited in ink colours."""

    def __init__(self, part):
        self.part = part
        self.m = [Canvas(part, "L", 0) for _ in range(3)]
        self.col = None          # original-colour elements (owner artwork drawn as-is), composited on top

    def _paint(self, tone, draw):
        if tone == "cut":
            for mk in self.m:
                draw(mk, 0)
            return
        for i, mk in enumerate(self.m):
            draw(mk, 255 if i == tone else 0)

    def draw(self, el, cu, cv, s, flip=False, rot=0.0, tone_shift=None, original=False):
        """Paint element `el` centred at strip (cu, cv), half-size s output px.
        original=True draws an element's colour version unchanged (its colours then count toward the palette)."""
        if original and el.get("colour"):
            self._colour(el, cu, cv, s, flip, rot)
            return
        if el.get("mask"):
            self._mask(el, cu, cv, s, flip, rot)
            return
        cr, sr = math.cos(rot), math.sin(rot)

        def tr(x, y):
            x = -x if flip else x
            return (cu + (x * cr - y * sr) * s, cv + (x * sr + y * cr) * s)

        for sh in el["shapes"]:
            tone = sh.get("tone", 0)
            if tone_shift and tone != "cut":
                tone = tone_shift.get(tone, tone)
            t = sh["t"]
            if t == "poly":
                pts = [tr(x, y) for x, y in sh["pts"]]
                if sh.get("stroke"):
                    w = max(MIN_LINE_PX, sh["stroke"] * s)
                    self._paint(tone, lambda mk, v: mk.line(pts + [pts[0]], v, w))
                else:
                    self._paint(tone, lambda mk, v: mk.polygon(pts, v))
            elif t == "ellipse":
                (x, y), (rx, ry) = sh["c"], sh["r"]
                if abs(rot) > 1e-3 or abs(rx - ry) > 1e-6 and abs(rot) > 1e-3:
                    pts = [tr(x + rx * math.cos(a), y + ry * math.sin(a)) for a in [i * math.pi / 14 for i in range(28)]]
                    if sh.get("stroke"):
                        w = max(MIN_LINE_PX, sh["stroke"] * s)
                        self._paint(tone, lambda mk, v: mk.line(pts + [pts[0]], v, w))
                    else:
                        self._paint(tone, lambda mk, v: mk.polygon(pts, v))
                else:
                    cx, cy = tr(x, y)
                    if sh.get("stroke"):
                        w = max(MIN_LINE_PX, sh["stroke"] * s)
                        self._paint(tone, lambda mk, v: mk.ellipse(cx, cy, rx * s, ry * s, None, v, w))
                    else:
                        self._paint(tone, lambda mk, v: mk.ellipse(cx, cy, rx * s, ry * s, v))
            elif t == "line":
                pts = [tr(x, y) for x, y in sh["pts"]]
                w = max(MIN_LINE_PX, sh.get("w", 0.08) * s)
                self._paint(tone, lambda mk, v: mk.line(pts, v, w))

    def _colour(self, el, cu, cv, s, flip, rot):
        if self.col is None:
            self.col = Canvas(self.part, "RGBA", (0, 0, 0, 0))
        src = Image.open(LIB / el["colour"]).convert("RGBA")
        if flip:
            src = src.transpose(Image.FLIP_LEFT_RIGHT)
        if abs(rot) > 1e-3:
            src = src.rotate(-math.degrees(rot), resample=Image.BICUBIC, expand=True)
        aspect = src.height / src.width
        w = max(1, int(2 * s * S)); h = max(1, int(2 * s * S * aspect))
        x0 = int((cu - s + self.part.P) * S); y0 = int((cv - s * aspect + M) * S)
        im = src.resize((w, h), Image.LANCZOS)
        for k in (-1, 0, 1):
            self.col.img.paste(im, (x0 + k * self.part.P * S, y0), im)
            for mk in self.m:                    # colour art covers any ink drawn below it
                mk.img.paste(0, (x0 + k * self.part.P * S, y0), im.getchannel("A"))

    def _mask(self, el, cu, cv, s, flip, rot):
        path = el["mask"]
        if el.get("bold") and 2 * s < el.get("bold_below", 0):      # small use: the simplified bold version
            path = el["bold"]
        src = Image.open(LIB / path).convert("L")
        if flip:
            src = src.transpose(Image.FLIP_LEFT_RIGHT)
        if abs(rot) > 1e-3:
            src = src.rotate(-math.degrees(rot), resample=Image.NEAREST, expand=True)
        aspect = src.height / src.width
        w = max(1, int(2 * s * S)); h = max(1, int(2 * s * S * aspect))
        x0 = int((cu - s + self.part.P) * S); y0 = int((cv - s * aspect + M) * S)
        for code, tone in ((255, 0), (170, 1), (85, 2)):
            layer = src.point(lambda p, c=code: 255 if abs(p - c) < 30 else 0).resize((w, h), Image.LANCZOS)
            for k in (-1, 0, 1):
                for i, mk in enumerate(self.m):
                    if i == tone:
                        mk.img.paste(255, (x0 + k * self.part.P * S, y0), layer)
                    else:
                        mk.img.paste(0, (x0 + k * self.part.P * S, y0), layer)

    def union(self):
        u = ImageChops.lighter(self.m[0].img, self.m[1].img)
        return ImageChops.lighter(u, self.m[2].img)

    def multiply(self, keep):
        """Keep ink only where `keep` (L, canvas size) is bright (used by distress)."""
        for mk in self.m:
            mk.img = ImageChops.multiply(mk.img, keep)
        if self.col is not None:
            r, g, b, a = self.col.img.split()
            self.col.img = Image.merge("RGBA", (r, g, b, ImageChops.multiply(a, keep)))

    def composite(self, c, colours):
        """colours: (tone0, tone1, tone2) RGB tuples. Paints the inks onto canvas c."""
        for mk, col in zip(self.m, colours):
            c.img.paste(Image.new("RGBA", c.img.size, rgba(col)), (0, 0), mk.img)
        if self.col is not None:
            c.img.alpha_composite(self.col.img)
        from PIL import ImageDraw
        c.d = ImageDraw.Draw(c.img)


def ink_tones(ink, fabric=None):
    """Main ink plus two tones of the same ink for depth (shadow, highlight)."""
    lum = sum(ink) / 3
    return (tuple(ink), shade(ink, 0.68 if lum > 90 else 0.6), shade(ink, 1.35 if lum < 200 else 0.85))


def find(styles=None, motif=None, family=None, tag=None, kinds=None):
    """Library query used by the recipe engine (deterministic order).
    kinds: element kinds to allow (hero, motif, border, swatch, part, texture); code-drawn elements count as motif."""
    out = []
    for eid, el in load_library().items():
        if kinds and el.get("kind", "motif") not in kinds:
            continue
        if styles and not set(styles) & set(el.get("styles", [])):
            continue
        if motif and el.get("motif") != motif:
            continue
        if family and family not in el.get("families", []):
            continue
        if tag and tag != el.get("motif") and tag not in el.get("mood", []) and tag not in eid:
            continue
        out.append(el)
    return out


# ---------------------------------------------------------------- tiles (owner-generated borders and swatches)

def tile_image(el, recolour_tones=None, period=64, height=None):
    """A wrap-safe tile for a border or swatch element.
    Swatches: `period` x `period`, mirrored in both axes (32 px halves) so every seam pair, the shoulder and
    the hip meet. Borders: `period` wide (64 or 128) x `height`, mirrored horizontally.
    recolour_tones=(tone0, tone1, tone2) maps the tile's ink mask to palette colours; None keeps the original colours."""
    src = Image.open(LIB / el["tile"]).convert("RGBA")
    if recolour_tones:
        m = Image.open(LIB / el["tile_mask"]).convert("L")
        out = Image.new("RGBA", src.size, rgba(recolour_tones[0]))
        for code, col in ((170, recolour_tones[1]), (85, recolour_tones[2])):
            out.paste(rgba(col), (0, 0), m.point(lambda p, c=code: 255 if abs(p - c) < 30 else 0))
        out.putalpha(src.getchannel("A"))
        src = out
    half = period // 2
    if el.get("kind") == "swatch":
        q = src.resize((half, half), Image.LANCZOS)
        t = Image.new("RGBA", (period, period))
        t.paste(q, (0, 0)); t.paste(q.transpose(Image.FLIP_LEFT_RIGHT), (half, 0))
        t.paste(q.transpose(Image.FLIP_TOP_BOTTOM), (0, half))
        t.paste(q.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM), (half, half))
        return t
    h = height or max(4, round(src.height * period / src.width))
    q = src.resize((half, h), Image.LANCZOS)
    t = Image.new("RGBA", (period, h))
    t.paste(q, (0, 0)); t.paste(q.transpose(Image.FLIP_LEFT_RIGHT), (half, 0))
    return t

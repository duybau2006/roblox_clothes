"""Shared geometry and drawing helpers for render.py, make_shading.py, preview.py and validate.py.

Coordinate model
----------------
Each body part (torso, right/left arm, right/left leg) is unwrapped into a *strip*:
    u (horizontal) runs around the part: front -> left -> back -> right -> (wraps to front)
    v (vertical) runs top -> bottom, 0..128 on the side faces.
Rows with v < 0 feed the part's top face and rows with v > 128 feed its bottom face
(each top/bottom pixel copies the strip pixel just beyond its nearest edge), so
every seam in regions.json is continuous by construction.

Everything is drawn at S x resolution and downscaled per panel with LANCZOS.
Units passed to the helpers are always *output pixels* (floats are fine).
"""
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
S = 4            # supersampling factor
H = 128          # side-face height in output px
M = 48           # strip margin above / below (feeds top/bottom faces + bleed)
FM = 4           # extra output px rendered around each panel before downscaling
BLEED = 2        # colour bleed written past each panel edge
FACES = ("front", "left", "back", "right", "top", "bottom")
SIDE_ORDER = ("front", "left", "back", "right")

# Shared construction lines for one outfit (v positions, output px from the top of the side
# panels). The shading layers in templates/shading/outfit/ are drawn against these, so
# render.py must use the same ones.
OUTFIT = {
    "hem_line": 112,     # torso: default end of the top garment (spec: torso.hem_line, 80-120)
    "waist_line": 92,    # torso: default top of the waistband (spec: legs.waist_line, 88-110) = R15 LowerTorso split (measured)
    "band": 8,           # waistband height
    "max_crop_gap": 16,  # cropped tops: max transparent rows between hem and waistband
    "min_hem": 80,       # tops never end above this line (chest always covered)
    "cuff_top": 98,      # arms: sleeve cuff 98-110, bare hand below (R15 hand split measured at ~110)
    "sleeve_end": 110,
    "short_sleeve": 40,  # arms: short sleeves end here
    "leg_cuff_top": 94,  # legs: ankle cuff 94-106
    "shoe_top": 106,     # legs: shoes 106-128, sole from 122 (R15 foot split measured at ~106)
    "sole_top": 122,
    "min_skirt": 32,     # skirts: shortest skirt over bare legs / socks (24 with tights)
    "min_skirt_tights": 24,
    "shoulder_rows": 32,  # rows checked for torso<->arm continuity
}


def load_regions():
    return json.loads((ROOT / "templates" / "regions.json").read_text(encoding="utf-8"))


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(x))) for x in c[:3])


def shade(c, k):
    """k < 1 darkens toward black, k > 1 lightens toward white."""
    c = c[:3]
    if k <= 1:
        out = tuple(round(x * k) for x in c)
    else:
        t = k - 1
        out = tuple(round(x + (255 - x) * t) for x in c)
    return out


def rgba(c, a=255):
    return tuple(c[:3]) + (a,)


class Part:
    def __init__(self, garment, name, regions=None):
        regions = regions or load_regions()
        g = regions["garments"][garment]
        self.garment, self.name = garment, name
        self.kind = "torso" if name == "torso" else "limb"
        self.panels = {f: g["panels"][f"{name}.{f}"] for f in FACES}
        self.off, u = {}, 0
        for f in SIDE_ORDER:
            self.off[f] = u
            u += self.panels[f]["w"]
        self.P = u
        self.w = {f: self.panels[f]["w"] for f in SIDE_ORDER}
        self.depth = self.panels["top"]["h"]
        self.strip_size = (self.P * S, (H + 2 * M) * S)


class Canvas:
    """A wrap-aware drawing surface 3 strips wide; call .strip() for the middle copy."""

    def __init__(self, part, mode="RGBA", fill=(0, 0, 0, 0)):
        self.part, self.P = part, part.P
        self.img = Image.new(mode, (3 * self.P * S, (H + 2 * M) * S), fill)
        self.d = ImageDraw.Draw(self.img)

    def _xy(self, pts, k):
        return [((u + self.P * (k + 1)) * S, (v + M) * S) for u, v in pts]

    def polygon(self, pts, fill=None, outline=None, width=0):
        for k in (-1, 0, 1):
            self.d.polygon(self._xy(pts, k), fill=fill, outline=outline, width=max(0, round(width * S)))

    def line(self, pts, fill, width=1.0):
        for k in (-1, 0, 1):
            self.d.line(self._xy(pts, k), fill=fill, width=max(1, round(width * S)), joint="curve")

    def rect(self, u0, v0, u1, v1, fill):
        for k in (-1, 0, 1):
            (x0, y0), (x1, y1) = self._xy([(u0, v0), (u1, v1)], k)
            self.d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=fill)

    def ellipse(self, cu, cv, ru, rv, fill=None, outline=None, width=0):
        for k in (-1, 0, 1):
            (x0, y0), (x1, y1) = self._xy([(cu - ru, cv - rv), (cu + ru, cv + rv)], k)
            self.d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline, width=max(0, round(width * S)))

    def band(self, v0, v1, fill):
        y0, y1 = (v0 + M) * S, (v1 + M) * S
        self.d.rectangle([0, y0, self.img.width - 1, y1 - 1], fill=fill)

    def blur(self, radius):
        self.img = self.img.filter(ImageFilter.GaussianBlur(radius * S))
        self.d = ImageDraw.Draw(self.img)

    def strip(self):
        return self.img.crop((self.P * S, 0, 2 * self.P * S, self.img.height))


def tiled(strip):
    t = Image.new(strip.mode, (strip.width * 3, strip.height))
    for i in range(3):
        t.paste(strip, (i * strip.width, 0))
    return t


def mirror_strip(strip, part):
    """Strip of the opposite limb, mirrored: [F L B R] -> [F' R' B' L'] (each flipped)."""
    flipped = strip.transpose(Image.FLIP_LEFT_RIGHT)
    t = tiled(flipped)
    x0 = strip.width + (part.P - part.w["front"]) * S
    return t.crop((x0, 0, x0 + strip.width, strip.height))


def _cap_uv(face, part, x, y):
    """Map a point on a top/bottom face (output px, face-local, may lie in the margin) to strip (u, v)."""
    w, d = part.panels[face]["w"], part.panels[face]["h"]
    wF, wL, wB = part.w["front"], part.w["left"], part.w["back"]
    if face == "top":
        cand = ((d - y, x, y - d),                      # bottom edge <-> front.top
                (w - x, wF + (d - y), -(w - x)),        # right edge  <-> left.top (reversed)
                (y, wF + wL + (w - x), -y),             # top edge    <-> back.top (reversed)
                (x, wF + wL + wB + y, -x))              # left edge   <-> right.top
    else:
        cand = ((y, x, H + y),                          # top edge    <-> front.bottom
                (w - x, wF + y, H + (w - x)),           # right edge  <-> left.bottom
                (d - y, wF + wL + (w - x), H + (d - y)),  # bottom edge <-> back.bottom (reversed)
                (x, wF + wL + wB + (d - y), H + x))     # left edge   <-> right.bottom (reversed)
    _, u, v = min(cand, key=lambda c: c[0])
    return u, v


def face_image(strip, part, face, tiles=None):
    """Hi-res image of one face incl. FM margin, cut from (or mapped out of) the strip."""
    p = part.panels[face]
    w, h = p["w"], p["h"]
    if face in SIDE_ORDER:
        t = tiles or tiled(strip)
        x0 = strip.width + (part.off[face] - FM) * S
        return t.crop((x0, (M - FM) * S, x0 + (w + 2 * FM) * S, (M + H + FM) * S))
    src = strip.load()
    sw, sh = strip.size
    out = Image.new(strip.mode, ((w + 2 * FM) * S, (h + 2 * FM) * S))
    dst = out.load()
    for Y in range(out.height):
        y = (Y + 0.5) / S - FM
        for X in range(out.width):
            x = (X + 0.5) / S - FM
            u, v = _cap_uv(face, part, x, y)
            sx = int(u * S) % sw
            sy = min(sh - 1, max(0, int((v + M) * S)))
            dst[X, Y] = src[sx, sy]
    return out


def build_pieces(strip, part):
    """Downscale every face of `part` from its strip: list of (panel box, image incl. FM margin)."""
    t = tiled(strip)
    pieces = []
    for face in FACES:
        p = part.panels[face]
        hi = face_image(strip, part, face, t)
        pieces.append((p, hi.resize((p["w"] + 2 * FM, p["h"] + 2 * FM), Image.LANCZOS)))
    return pieces


def paste_pieces(canvas, pieces, bleed=BLEED):
    """Paste downscaled faces into a 585x559 canvas: bleed first, then the exact panel cores."""
    for p, lo in pieces:
        canvas.paste(lo.crop((FM - bleed, FM - bleed, FM + p["w"] + bleed, FM + p["h"] + bleed)),
                     (p["x"] - bleed, p["y"] - bleed))
    for p, lo in pieces:
        canvas.paste(lo.crop((FM, FM, FM + p["w"], FM + p["h"])), (p["x"], p["y"]))


def paste_part(canvas, strip, part, bleed=BLEED):
    paste_pieces(canvas, build_pieces(strip, part), bleed)


def apply_shading(img, shade_l, highlight_gain=1.2):
    """Apply an L-mode shading map (128 = neutral) to an RGBA image of the same size."""
    r, g, b, a = img.split()
    rgb = Image.merge("RGB", (r, g, b))
    dark = shade_l.point(lambda s: min(255, s * 2))
    light = shade_l.point(lambda s: max(0, min(255, int((s - 128) * highlight_gain))))
    rgb = ImageChops.multiply(rgb, Image.merge("RGB", (dark, dark, dark)))
    rgb = ImageChops.screen(rgb, Image.merge("RGB", (light, light, light)))
    out = rgb.convert("RGBA")
    out.putalpha(a)
    return out


def shading_path(kind):
    """kind: torso | arm | leg"""
    return ROOT / "templates" / "shading" / "outfit" / f"{kind}.png"


def load_shading(kind):
    return Image.open(shading_path(kind)).convert("L")


def panel_mask(garment, regions=None, grow=0):
    """L-mode 585x559 mask: 255 inside panels (grown by `grow` px), else 0."""
    regions = regions or load_regions()
    m = Image.new("L", tuple(regions["canvas"]), 0)
    d = ImageDraw.Draw(m)
    for p in regions["garments"][garment]["panels"].values():
        d.rectangle([p["x"] - grow, p["y"] - grow, p["x"] + p["w"] - 1 + grow, p["y"] + p["h"] - 1 + grow], fill=255)
    return m


def seeded_noise(w, h, sigma, seed):
    """Deterministic Gaussian noise image (L, centred on 128). Replaces Image.effect_noise,
    which cannot be seeded, so the same spec always renders the same pixels."""
    import random as _r
    rnd = _r.Random(seed)
    data = bytes(max(0, min(255, int(128 + rnd.gauss(0, sigma)))) for _ in range(w * h))
    return Image.frombytes("L", (w, h), data)

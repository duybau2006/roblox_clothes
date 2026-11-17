"""Print family: one large composition on the torso front or back, plus distress and fabric washes.

decor entry (torso only):
  {print: {placement: front|back, template: centered_stack|symmetric_pair|offcentre_figure|allover_faded,
           elements: [library ids, main first], ink: "#hex", distress: 0-3 or {drips, splatter, scratches,
           halftone, cracked, worn: 0-3}, seed: int, wrap: bool, scale: 0.7-1.3}}
The print is one ink in 3 tones (ink, shadow, highlight). Everything is seeded (same seed = same print).
Prints keep clear of the shoulder rows near the side seams, so the shoulder check still holds.
"""
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from clothing import S, M, H, Canvas, hex_rgb, shade, seeded_noise
import library

TEMPLATES = ("centered_stack", "symmetric_pair", "offcentre_figure", "allover_faded")
DISTRESS_KINDS = ("drips", "splatter", "scratches", "halftone", "cracked", "worn")
DISTRESS_PRESETS = {0: {}, 1: {"worn": 1, "cracked": 1}, 2: {"worn": 2, "cracked": 2, "scratches": 1, "halftone": 1},
                    3: {"worn": 3, "cracked": 3, "scratches": 2, "halftone": 2, "splatter": 1}}
SHOULDER_ROWS = 36


def distress_levels(d):
    if isinstance(d, dict):
        return {k: int(d.get(k, 0)) for k in DISTRESS_KINDS}
    base = DISTRESS_PRESETS.get(int(d or 0), DISTRESS_PRESETS[3])
    return {k: base.get(k, 0) for k in DISTRESS_KINDS}


def _paste3(img, patch, u, v, P, op="multiply"):
    """Apply an L patch at strip (u, v) on all three wrap copies of a canvas-sized L image."""
    out = img
    for k in (-1, 0, 1):
        x, y = int((u + P * (k + 1)) * S), int((v + M) * S)
        region = out.crop((x, y, x + patch.width, y + patch.height))
        merged = ImageChops.multiply(region, patch) if op == "multiply" else ImageChops.lighter(region, patch)
        out.paste(merged, (x, y))
    return out


def _elements(ids):
    return [library.element(i) for i in ids]


def compose(masks, template, els, area, rnd, scale=1.0, P=384):
    u0, u1, v0, v1 = area
    W, Hh = u1 - u0, v1 - v0
    cx, mid = (u0 + u1) / 2, v0 + Hh * 0.5
    m = min(W * 0.47, Hh * 0.43) * scale          # main element half-size: fills most of the panel
    E = els + [None] * 4

    def draw(el, u, v, s, flip=False, rot=0.0):
        if el is not None:
            masks.draw(el, u, v, s, flip=flip, rot=rot)

    # seed-driven layout choices: a new seed moves, scales or mirrors the composition
    jit = {"main_v": rnd.uniform(0.45, 0.58), "main_s": rnd.uniform(0.9, 1.1), "spread": rnd.uniform(0.24, 0.34),
           "side_dv": rnd.uniform(-0.12, 0.06), "side_s": rnd.uniform(0.25, 0.33), "mirror": rnd.random() < 0.5,
           "pair_k": rnd.uniform(0.8, 1.15), "accents": rnd.randint(0, 3)}
    if template == "centered_stack":
        draw(E[0], cx, v0 + Hh * jit["main_v"], m * 1.05 * jit["main_s"])
        if E[1]:
            if E[1].get("band"):
                draw(E[1], cx, v0 + Hh * 0.1, W * 0.4 * scale)
            else:
                draw(E[1], cx, v0 + Hh * 0.13, m * 0.4)
        if E[2]:
            if E[2].get("band"):
                draw(E[2], cx, v1 - Hh * 0.08, W * 0.44 * scale)
            else:
                draw(E[2], cx - m * 0.95 * jit["pair_k"], v1 - Hh * 0.14, m * 0.34)
                draw(E[2], cx + m * 0.95 * jit["pair_k"], v1 - Hh * 0.14, m * 0.34, flip=True)
        for el in els[3:]:
            draw(el, cx + rnd.choice((-1, 1)) * m * 1.05, v0 + Hh * rnd.uniform(0.25, 0.4), m * 0.22)
    elif template == "symmetric_pair":
        side = E[1] or E[0]
        sw = min(W * jit["side_s"] * scale, W * (0.47 - jit["spread"]))   # side elements stay inside the panel
        sv = mid + Hh * jit["side_dv"]
        draw(side, cx - W * jit["spread"], sv, sw, flip=bool(side.get("symmetric") is False))
        draw(side, cx + W * jit["spread"], sv, sw, flip=False)
        draw(E[0], cx, mid, m * 0.9 * jit["main_s"])
        small = els[-1]
        for _ in range(jit["accents"]):
            k = rnd.choice((-1, 1))
            draw(small, cx + k * W * rnd.uniform(0.3, 0.44), v0 + Hh * rnd.uniform(0.08, 0.92), m * 0.13)
        if E[2]:
            if E[2].get("band"):
                draw(E[2], cx, v1 - Hh * 0.08, W * 0.42 * scale)
            else:
                draw(E[2], cx, v0 + Hh * 0.12, m * 0.3)
        for i, el in enumerate(els[3:]):
            k = -1 if i % 2 else 1
            draw(el, cx + k * W * 0.4, v0 + Hh * 0.15, m * 0.18, flip=k < 0)
    elif template == "offcentre_figure":
        side_l = jit["mirror"]                       # figure left or right, ornament opposite
        fx = u0 + W * (0.62 if side_l else 0.38)
        ox = u0 + W * (0.14 if side_l else 0.86)
        draw(E[0], fx, v0 + Hh * jit["main_v"], m * 1.02 * jit["main_s"], flip=side_l)
        if E[1]:
            if E[1].get("band"):
                draw(E[1], ox, mid, Hh * 0.42 * scale, rot=math.pi / 2)
            else:
                draw(E[1], ox, mid, Hh * 0.38 * scale, flip=side_l)
        for el in els[2:]:
            for _ in range(2):
                draw(el, fx + rnd.uniform(-1, 1) * m * 1.1, mid + rnd.choice((-1, 1)) * rnd.uniform(0.75, 1.0) * m, m * rnd.uniform(0.14, 0.22))
    elif template == "allover_faded":
        n = 0
        tries = 0
        pts = []
        target = int(P * Hh / 380)
        while n < target and tries < target * 20:
            tries += 1
            u, v = rnd.uniform(0, P), rnd.uniform(v0 + 4, v1 - 4)
            s = rnd.uniform(7, 12) * scale
            if v < SHOULDER_ROWS + s and any(abs(u - x) < s + 3 for x in (0, 128, 192, 320, P)):
                continue
            if any(math.hypot(u - a, v - b) < (s + c) * 1.05 for a, b, c in pts):
                continue
            el = els[n % len(els)]
            masks.draw(el, u, v, s, flip=rnd.random() < 0.5, rot=rnd.uniform(-0.45, 0.45))
            pts.append((u, v, s))
            n += 1
    else:
        raise ValueError(f"unknown print template '{template}'")


def distress(masks, area, levels, rnd, P):
    """Additive (drips, splatter) then subtractive (cracked, scratches, worn, halftone) ink damage."""
    u0, u1, v0, v1 = area
    W, Hh = u1 - u0, v1 - v0
    # --- additive: drips run down from the lowest ink in random columns, splatter around the print
    if levels["drips"]:
        low = masks.union().resize((masks.m[0].img.width // S, masks.m[0].img.height // S), Image.BILINEAR)
        px = low.load()
        cols = [u for u in range(int(u0), int(u1)) if any(px[u + P, y] > 128 for y in range(int(v0 + M), int(v1 + M)))]
        for u in rnd.sample(cols, min(len(cols), 4 * levels["drips"])) if cols else []:
            bottom = max(y for y in range(int(v0 + M), int(v1 + M)) if px[u + P, y] > 128) - M
            ln = rnd.uniform(3, 6 + 4 * levels["drips"])
            w = rnd.uniform(0.8, 1.6)
            masks._paint(0, lambda mk, val: mk.line([(u, bottom - 1), (u, bottom + ln)], val, w))
            masks._paint(0, lambda mk, val: mk.ellipse(u, bottom + ln, w * 0.7, w * 0.8, val))
    if levels["splatter"]:
        cx, cy = (u0 + u1) / 2, (v0 + v1) / 2
        for _ in range(14 * levels["splatter"]):
            u, v = rnd.gauss(cx, W * 0.32), rnd.gauss(cy, Hh * 0.3)
            if u0 - 4 < u < u1 + 4 and v0 < v < v1:
                r = rnd.uniform(0.35, 1.2)
                masks._paint(0, lambda mk, val: mk.ellipse(u, v, r, r * rnd.uniform(0.7, 1.2), val))
    # --- subtractive: build a keep mask (255 = keep ink)
    keep = Canvas(masks.part, "L", 255)
    if levels["cracked"]:
        for _ in range(int(W * Hh / 900 * levels["cracked"])):
            u, v = rnd.uniform(u0, u1), rnd.uniform(v0, v1)
            pts = [(u, v)]
            a = rnd.uniform(0, 2 * math.pi)
            for _ in range(rnd.randint(3, 6)):
                a += rnd.uniform(-1.0, 1.0)
                u, v = u + math.cos(a) * rnd.uniform(2, 5), v + math.sin(a) * rnd.uniform(2, 5)
                pts.append((u, v))
            keep.line(pts, 0, 0.32)
    if levels["scratches"]:
        for _ in range(4 * levels["scratches"]):
            u, v = rnd.uniform(u0, u1), rnd.uniform(v0, v1)
            a = rnd.uniform(-0.5, 0.5) + rnd.choice((0, math.pi / 2.6))
            ln = rnd.uniform(14, 40)
            keep.line([(u, v), (u + math.cos(a) * ln, v + math.sin(a) * ln)], 0, rnd.uniform(0.3, 0.55))
    img = keep.img
    pw, ph = int(W * S), int(Hh * S)
    if levels["worn"] and pw > 0 and ph > 0:
        noise = seeded_noise(max(4, int(W / 3)), max(4, int(Hh / 3)), 70, rnd.randint(0, 10 ** 9)).resize((pw, ph), Image.BICUBIC)
        noise = noise.filter(ImageFilter.GaussianBlur(S * 1.2))
        cut = 172 - 12 * levels["worn"]          # worn spots fade the ink, they do not erase the design
        worn = noise.point(lambda p: 255 if p < cut else max(110, 255 - (p - cut) * 4))
        img = _paste3(img, worn, u0, v0, P)
    if levels["halftone"] and pw > 0 and ph > 0:
        ht = Image.new("L", (pw, ph), 0)
        d = ImageDraw.Draw(ht)
        sp = 3.0 * S
        start = 0.45 - 0.08 * levels["halftone"]            # fade begins this far down the print
        y = 0.0
        while y < ph:
            t = y / ph
            f = 1.0 if t < start else max(0.08, 1 - (t - start) / (1 - start) * (0.55 + 0.15 * levels["halftone"]))
            x = (sp / 2) * ((int(y / sp)) % 2)
            r = sp * 0.72 * math.sqrt(f)
            while x < pw:
                if f >= 0.98:
                    d.rectangle([x - sp / 2, y - sp / 2, x + sp / 2, y + sp / 2], fill=255)
                else:
                    d.ellipse([x - r, y - r, x + r, y + r], fill=255)
                x += sp
            y += sp
        img = _paste3(img, ht, u0, v0, P)
    keep.img = img
    masks.multiply(keep.img)


def draw_print(c, part, p, ctx, warnings):
    placement = str(p.get("placement", "front")).lower()   # front first (owner note 2026-11-16)
    template = str(p.get("template", "centered_stack")).lower()
    if template not in TEMPLATES:
        warnings.append(f"print: template '{template}' unknown; not drawn")
        return
    try:
        els = _elements(p.get("elements") or [])
    except KeyError as e:
        warnings.append(f"print: {e}; not drawn")
        return
    if not els:
        warnings.append("print: no elements; not drawn")
        return
    rnd = random.Random(int(p.get("seed", 0)) * 7919 + len(els))
    P = part.P
    v0 = 10.0
    if placement == "back" and ctx.get("hood"):
        v0 = 50.0
    v1 = float(ctx["band_top"]) - 4
    base = (6.0, 122.0) if placement == "front" else (198.0, 314.0)
    wrap = bool(p.get("wrap"))
    u0, u1 = (base[0] - 22, base[1] + 22) if wrap else base
    area = (u0, u1, v0, v1)
    masks = library.Masks(part)
    compose(masks, template, els, area, rnd, float(p.get("scale", 1.0)), P)
    levels = distress_levels(p.get("distress", 0))
    if template == "allover_faded":
        levels["halftone"] = max(levels["halftone"], 1)
        area = (0.0, float(P), v0, v1)
    distress(masks, area, levels, rnd, P)
    if not wrap and template != "allover_faded":   # a placed print never leaves its panel
        inside = Canvas(part, "L", 0)
        inside.rect(area[0], -M, area[1], H + M, 255)
        masks.multiply(inside.img)
    if wrap or template == "allover_faded":   # keep clear of the shoulder rows beside the side seams
        clear = Canvas(part, "L", 255)
        for x in (0, 128, 192, 320):
            clear.rect(x - 8, -M, x + 8, SHOULDER_ROWS, 0)
        masks.multiply(clear.img)
    masks.composite(c, library.ink_tones(hex_rgb(p.get("ink", "#FFFFFF"))))


# ---------------------------------------------------------------- fabric washes (base_pattern)

WASHES = ("acid_wash", "mineral_wash", "heather", "faded_black")


def _sym_tile(w, h, sigma, blur, seed):
    """Noise tile (width w*2) that is periodic and mirror-symmetric, so washes meet at every seam."""
    half = seeded_noise(w, h, sigma, seed)
    if blur:
        wide = Image.new("L", (w * 3, h))
        for i in range(3):
            wide.paste(half, (i * w, 0))
        half = wide.filter(ImageFilter.GaussianBlur(blur)).crop((w, 0, 2 * w, h))
    tile = Image.new("L", (w * 2, h))
    tile.paste(half, (0, 0))
    tile.paste(half.transpose(Image.FLIP_LEFT_RIGHT), (w, 0))
    return tile


def wash_map(part, kind):
    """L shading map (128 = neutral) for a wash, wrap-canvas sized, periodic every 64 px."""
    h = H + 2 * M
    if kind == "acid_wash":
        marble = _sym_tile(32, h, 80, 2.2, 1)
        veins = marble.point(lambda p: 255 if abs(p - 128) < 9 else 0).filter(ImageFilter.GaussianBlur(0.6))
        mott = _sym_tile(32, h, 60, 4.5, 2)
        tile = ImageChops.add(mott.point(lambda p: 128 + (p - 128) // 5), veins.point(lambda p: p // 4), 1.0, 0)
    elif kind == "mineral_wash":
        mott = _sym_tile(32, h, 90, 5.5, 3)
        tile = mott.point(lambda p: 128 + max(-14, min(40, (p - 128))))
    elif kind == "heather":
        fine = _sym_tile(32, h, 45, 0, 4)
        tile = fine.point(lambda p: 128 + (p - 128) // 3)
    else:  # faded_black
        mott = _sym_tile(32, h, 80, 7, 5)
        tile = mott.point(lambda p: 150 + max(-10, min(45, (p - 128) // 1)))
    wide = Image.new("L", (3 * part.P, h))
    for x in range(0, wide.width, 64):
        wide.paste(tile, (x, 0))
    return wide.resize((wide.width * S, wide.height * S), Image.BILINEAR)

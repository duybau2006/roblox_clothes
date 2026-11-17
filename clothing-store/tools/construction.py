"""Garment construction parts. Each part draws its own shapes plus highlight / shadow strokes into the
feature shading layers (fx["hi"], fx["sh"]), so it reads as sewn cloth, not a flat sticker.

Spec: a section's `parts:` list, each a name or {name: ..., colour: "#hex", ...}.
  torso: collar_polo collar_shirt collar_stand lapels tie waistcoat placket buttons zip_full chest_pocket
         piping trim_hem epaulettes
  arms:  cuff_button trim_cuff piping
  legs:  belt jeans_fly jeans_pockets cargo_pockets crease piping
Strip coordinates: torso front u 0-128 (centre 64), back 192-320 (centre 256); limb front 0-64,
outer face 192-256 (right-limb convention, mirrored to the left limb).
"""
import math

from clothing import hex_rgb, rgba, shade

PARTS = {
    "torso": ("collar_polo", "collar_shirt", "collar_stand", "lapels", "tie", "waistcoat", "placket", "buttons",
              "zip_full", "chest_pocket", "piping", "trim_hem", "epaulettes", "lacing"),
    "arms": ("cuff_button", "trim_cuff", "piping"),
    "legs": ("belt", "jeans_fly", "jeans_pockets", "cargo_pockets", "crease", "piping"),
}


def _col(p, key, default):
    return hex_rgb(p[key]) if isinstance(p, dict) and p.get(key) else default


def _dashed(c, pts, col, dash=1.4, gap=1.0, w=0.5):
    for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
        L = math.hypot(u1 - u0, v1 - v0)
        t = 0.0
        while t < L and L > 0:
            a, b = t / L, min(L, t + dash) / L
            c.line([(u0 + (u1 - u0) * a, v0 + (v1 - v0) * a), (u0 + (u1 - u0) * b, v0 + (v1 - v0) * b)], rgba(col), w)
            t += dash + gap


def _button(c, fx, u, v, col, r=1.6):
    c.ellipse(u, v, r, r, rgba(shade(col, 0.75)))
    c.ellipse(u, v, r * 0.72, r * 0.72, rgba(col))
    c.ellipse(u - r * 0.3, v - r * 0.3, r * 0.25, r * 0.25, rgba(shade(col, 1.6)))
    fx["sh"].ellipse(u + 0.6, v + r + 0.4, r, r * 0.45, 26)


def _panel(c, fx, pts, col, edge=0.6):
    c.polygon(pts, rgba(col), rgba(shade(col, edge)), 0.8)


def torso_part(name, p, c, col, fx, ctx):
    bt = ctx["band_top"]
    body, trim, acc = col.body, col.trim, col.accent
    if name in ("collar_polo", "collar_shirt"):
        long = name == "collar_shirt"
        cc = _col(p, "colour", trim if name == "collar_polo" else body)
        for k in (-1, 1):
            pts = [(64 + k * 24, 0), (64 + k * 1.5, 3), (64 + k * (8 if long else 10), 16 if long else 13), (64 + k * 28, 9 if long else 7)]
            _panel(c, fx, pts, shade(cc, 1.05))
            fx["sh"].line([pts[2], pts[3]], 34, 2.2)                         # collar casts a shadow below its edge
            fx["hi"].line([(64 + k * 22, 0.5), (64 + k * 4, 3)], 26, 1.0)     # fold highlight
        c.band(-7, -2, rgba(shade(cc, 0.95)))                                  # collar band around the neck (top face)
        end = bt if long else 30
        c.rect(60.5, 3, 67.5, end, rgba(shade(body, 0.97)))                     # placket
        c.line([(60.5, 3), (60.5, end)], rgba(shade(body, 0.7)), 0.6)
        c.line([(67.5, 3), (67.5, end)], rgba(shade(body, 0.7)), 0.6)
        fx["sh"].line([(68.5, 4), (68.5, end)], 18, 1.4)
        for v in range(8, int(end) - 2, 11 if long else 9):
            _button(c, fx, 64, v, _col(p, "buttons", shade(body, 1.35) if sum(body) < 360 else shade(body, 0.6)), 1.4)
    elif name == "collar_stand":
        cc = _col(p, "colour", trim)
        c.band(-6, -2, rgba(cc))                                                            # stops 2 rows above the top seam
        c.rect(36, -2, 92, 4, rgba(cc))
        fx["hi"].line([(36, -0.5), (92, -0.5)], 26, 0.9)
        fx["sh"].line([(36, 4.6), (92, 4.6)], 30, 1.6)
    elif name == "lapels":
        inner = _col(p, "shirt", (240, 240, 236))
        c.polygon([(44, -2), (64, 46), (84, -2)], rgba(inner))                     # shirt in the V
        fx["sh"].polygon([(46, -2), (64, 40), (82, -2)], 10)
        c.rect(52, -6, 76, 2, rgba(inner))                                         # shirt collar band
        for k in (-1, 1):
            lap = [(64 + k * 20, -2), (64 + k * 1, 46), (64 + k * 9, 50), (64 + k * 34, 24), (64 + k * 28, 15), (64 + k * 34, 11)]
            _panel(c, fx, lap, _col(p, "colour", shade(body, 1.08)), 0.55)
            fx["hi"].line([(64 + k * 20, -2), (64 + k * 2, 44)], 30, 1.0)          # lapel roll highlight
            fx["sh"].line([(64 + k * 34, 24), (64 + k * 10, 52)], 30, 2.4)         # lapel shadow on the jacket
        _button(c, fx, 64, 62, _col(p, "buttons", shade(body, 0.6)), 1.8)
        _button(c, fx, 64, 80, _col(p, "buttons", shade(body, 0.6)), 1.8)
        c.line([(64, 50), (64, bt)], rgba(shade(body, 0.7)), 0.6)                  # front edge
        for k in (-1, 1):                                                         # flap pockets
            c.rect(64 + k * 34 - 9, 78, 64 + k * 34 + 9, 81.5, rgba(shade(body, 1.05)))
            fx["sh"].line([(64 + k * 34 - 9, 82), (64 + k * 34 + 9, 82)], 26, 1.2)
    elif name == "tie":
        tc = _col(p, "colour", acc)
        c.polygon([(61, 1), (67, 1), (66, 6), (62, 6)], rgba(shade(tc, 0.9)))          # knot
        c.polygon([(62, 6), (66, 6), (69, 40), (64, 46), (59, 40)], rgba(tc))           # blade
        fx["hi"].line([(63, 8), (62, 38)], 24, 0.8)
        fx["sh"].line([(66.5, 7), (68, 40)], 26, 1.2)
        for v in range(10, 40, 6):                                                     # small woven stripe
            c.line([(61, v), (67, v + 3)], rgba(shade(tc, 0.8)), 0.5)
    elif name == "waistcoat":
        wc = _col(p, "colour", shade(body, 0.85))
        c.polygon([(34, 4), (64, 40), (94, 4), (104, 6), (104, bt + 6), (64, bt + 10), (24, bt + 6), (24, 6)], rgba(wc))   # jacket fronts stay visible
        c.line([(30, 4), (64, 40), (98, 4)], rgba(shade(wc, 0.6)), 0.8)
        fx["sh"].line([(31, 6), (64, 42), (97, 6)], 26, 2.0)
        c.line([(64, 40), (64, bt + 10)], rgba(shade(wc, 0.6)), 0.6)
        for v in range(46, int(bt) + 2, 10):
            _button(c, fx, 64, v, _col(p, "buttons", (200, 170, 90)), 1.5)
        for k in (-1, 1):
            c.line([(64 + k * 18, 70), (64 + k * 34, 68)], rgba(shade(wc, 0.55)), 0.9)   # welt pockets
            fx["hi"].line([(64 + k * 18, 71.5), (64 + k * 34, 69.5)], 16, 0.6)
        c.polygon([(200, 6), (312, 6), (312, bt + 6), (200, bt + 6)], rgba(shade(wc, 0.9)))  # back panel
        c.rect(244, 60, 268, 63, rgba(shade(wc, 0.75)))                                   # back strap
    elif name == "placket":
        c.rect(60.5, 2, 67.5, bt, rgba(shade(body, 0.97)))
        _dashed(c, [(61.5, 3), (61.5, bt)], shade(body, 0.6))
        _dashed(c, [(66.5, 3), (66.5, bt)], shade(body, 0.6))
        fx["sh"].line([(68.5, 3), (68.5, bt)], 16, 1.2)
    elif name == "buttons":
        for v in range(8, int(bt) - 2, 11):
            _button(c, fx, 64, v, _col(p, "colour", shade(body, 0.6) if sum(body) > 360 else shade(body, 1.5)), 1.5)
    elif name == "zip_full":
        zc = _col(p, "colour", (190, 190, 196))
        c.rect(62.6, 2, 65.4, bt, rgba(shade(body, 0.55)))
        for v in range(3, int(bt), 1):
            c.rect(63.1 if v % 2 else 64.0, v, 64.0 if v % 2 else 64.9, v + 0.6, rgba(zc))
        c.rect(62.0, 4, 66.0, 10, rgba(shade(zc, 1.1)))                                   # puller
        c.ellipse(64, 11.5, 1.4, 1.4, None, rgba(zc), 0.6)
        fx["hi"].line([(63, 4), (63, 10)], 30, 0.6)
        fx["sh"].line([(66.4, 2), (66.4, bt)], 26, 1.6)
    elif name == "chest_pocket":
        pc = _col(p, "colour", shade(body, 0.95))
        x0, y0 = 82, 22
        c.rect(x0, y0, x0 + 18, y0 + 20, rgba(pc))
        _dashed(c, [(x0 + 1, y0 + 1), (x0 + 1, y0 + 19), (x0 + 17, y0 + 19), (x0 + 17, y0 + 1)], shade(pc, 0.62))
        c.rect(x0 - 0.5, y0 - 1, x0 + 18.5, y0 + 6, rgba(shade(pc, 1.04)))                  # flap
        c.line([(x0 - 0.5, y0 + 6), (x0 + 18.5, y0 + 6)], rgba(shade(pc, 0.55)), 0.7)
        _button(c, fx, x0 + 9, y0 + 4, _col(p, "buttons", shade(pc, 0.55)), 1.2)
        fx["sh"].line([(x0, y0 + 7.5), (x0 + 18, y0 + 7.5)], 30, 1.4)
        fx["sh"].line([(x0 + 18.8, y0), (x0 + 18.8, y0 + 20)], 20, 1.2)
    elif name == "piping":
        pc = _col(p, "colour", acc)
        pts = [(u, 40 + 9 * math.sin(u / 384 * 4 * math.pi)) for u in range(-4, 389, 4)]   # one closed wave around the torso
        c.line(pts, rgba(shade(pc, 0.7)), 2.0)
        c.line(pts, rgba(pc), 1.3)
        fx["hi"].line([(u, v - 0.4) for u, v in pts], 20, 0.5)
    elif name == "trim_hem":
        tc = _col(p, "colour", acc)
        y = bt - 7
        c.band(y, y + 0.9, rgba(tc))
        c.band(y + 5.1, y + 6, rgba(tc))
        for u in range(0, 384, 6):                                                        # diamond row (period 6 wraps)
            c.polygon([(u + 3, y + 1.2), (u + 5.4, y + 3), (u + 3, y + 4.8), (u + 0.6, y + 3)], rgba(tc))
        fx["hi"].band(y, y + 0.5, 22)
    elif name == "lacing":                                                                 # corset-style front lacing over a solid panel
        lc = _col(p, "colour", acc)
        top = float(p.get("top", 18)) if isinstance(p, dict) else 18
        c.rect(57, top - 2, 71, bt, rgba(shade(body, 0.8)))                                  # modesty panel: solid, never a gap
        for v in range(int(top), int(bt) - 2, 5):
            for u in (58.5, 69.5):
                c.ellipse(u, v, 1.1, 1.1, rgba(shade(lc, 0.5)), rgba((200, 196, 186)), 0.4)     # eyelets
            c.line([(58.5, v), (69.5, v + 5)], rgba(lc), 0.8)
            c.line([(69.5, v), (58.5, v + 5)], rgba(shade(lc, 0.8)), 0.8)
        c.line([(64, top - 1), (60, top - 6), (58, top - 1)], rgba(lc), 0.9)                  # small bow at the top
        c.line([(64, top - 1), (68, top - 6), (70, top - 1)], rgba(lc), 0.9)
        fx["sh"].line([(56, top), (56, bt)], 26, 1.4); fx["sh"].line([(72, top), (72, bt)], 26, 1.4)
        fx["hi"].line([(58, top), (58, bt)], 18, 0.6)
    elif name == "epaulettes":
        ec = _col(p, "colour", trim)
        c.rect(-8, -3, 8, 1, rgba(ec))
        c.rect(120, -3, 136, 1, rgba(ec))
        _button(c, fx, 0, -1, shade(ec, 1.4), 1.0)
        _button(c, fx, 128, -1, shade(ec, 1.4), 1.0)


def arm_part(name, p, c, col, fx, ctx):
    body, acc = col.body, col.accent
    cuff, end = ctx["cuff"], ctx["end"]
    if name == "cuff_button":
        cc = _col(p, "colour", shade(body, 0.97))
        c.band(cuff, end, rgba(cc))
        c.band(cuff, cuff + 0.7, rgba(shade(cc, 0.6)))
        _button(c, fx, 224, (cuff + end) / 2, _col(p, "buttons", shade(body, 0.6)), 1.2)
        c.line([(214, cuff - 14), (214, cuff)], rgba(shade(body, 0.7)), 0.6)              # sleeve placket
        fx["sh"].band(cuff - 1.5, cuff, 26)
    elif name == "trim_cuff":
        tc = _col(p, "colour", acc)
        y = cuff - 7
        c.band(y, y + 0.9, rgba(tc))
        c.band(y + 5.1, y + 6, rgba(tc))
        for u in range(0, 256, 6):
            c.polygon([(u + 3, y + 1.2), (u + 5.4, y + 3), (u + 3, y + 4.8), (u + 0.6, y + 3)], rgba(tc))
    elif name == "piping":
        pc = _col(p, "colour", acc)
        pts = [(224 + 10 * math.sin(v / 40 * math.pi), v) for v in range(-2, int(end), 2)]   # gentle curve down the outer arm
        c.line(pts, rgba(shade(pc, 0.7)), 2.0)
        c.line(pts, rgba(pc), 1.3)


def leg_part(name, p, c, col, fx, ctx):
    body, acc = col.body, col.accent
    wv = ctx["wv"]
    if name == "belt":
        bc = _col(p, "colour", (60, 42, 30))
        c.band(wv + 0.5, wv + 6, rgba(bc))
        c.band(wv + 0.5, wv + 1.1, rgba(shade(bc, 1.4)))
        _dashed(c, [(0, wv + 2), (256, wv + 2)], shade(bc, 1.5), 1.2, 1.2, 0.35)
        bk = _col(p, "buckle", (200, 196, 186))
        c.rect(58, wv - 0.5, 70, wv + 7, rgba(shade(bk, 0.7)))                            # buckle (centred on the front seam)
        c.rect(59.2, wv + 0.7, 68.8, wv + 5.8, rgba(bc))
        c.rect(58.5, wv, 69.5, wv + 0.8, rgba(shade(bk, 1.3)))
        fx["sh"].band(wv + 6, wv + 7.8, 34)
        for u in (16, 44, 150, 176, 222):
            c.rect(u, wv - 0.5, u + 2.4, wv + 7, rgba(shade(body, 0.85)))
    elif name == "jeans_fly":
        st = _col(p, "stitch", (210, 160, 80))
        _dashed(c, [(56, wv + 9), (56, wv + 26), (60, wv + 31), (64, wv + 32)], st)
        c.line([(64, wv + 8), (64, wv + 32)], rgba(shade(body, 0.6)), 0.7)
        fx["sh"].line([(57, wv + 9), (57, wv + 27)], 16, 1.0)
    elif name == "jeans_pockets":
        st = _col(p, "stitch", (210, 160, 80))
        arc = [(2 + 16 * (1 - math.cos(t)), wv + 8 + 14 * math.sin(t)) for t in [i * math.pi / 2 / 10 for i in range(11)]]
        c.line(arc, rgba(shade(body, 0.6)), 0.8)
        _dashed(c, [(x + 1.4, y + 0.4) for x, y in arc], st)
        c.rect(36, wv + 9, 44, wv + 15, rgba(shade(body, 0.92)))                             # coin pocket
        _dashed(c, [(36.5, wv + 9.5), (43.5, wv + 9.5)], st)
        fx["sh"].line([(x + 0.8, y + 1.2) for x, y in arc], 22, 1.4)
        x0, y0 = 140, wv + 12                                                                # back patch pocket
        pts = [(x0, y0), (x0 + 22, y0), (x0 + 22, y0 + 18), (x0 + 11, y0 + 22), (x0, y0 + 18), (x0, y0)]
        c.polygon(pts[:-1], rgba(shade(body, 0.95)), rgba(shade(body, 0.6)), 0.6)
        _dashed(c, [(x + (0.8 if x < x0 + 11 else -0.8), y + 0.8) for x, y in pts], st)
        fx["sh"].line([(x0 + 22.8, y0), (x0 + 22.8, y0 + 18), (x0 + 11, y0 + 23)], 24, 1.2)
    elif name == "cargo_pockets":
        cc = _col(p, "colour", shade(body, 0.94))
        x0, y0 = 212, 30
        c.rect(x0, y0, x0 + 24, y0 + 24, rgba(cc))
        c.rect(x0 - 1, y0 - 2, x0 + 25, y0 + 6, rgba(shade(cc, 1.05)))
        c.line([(x0 - 1, y0 + 6), (x0 + 25, y0 + 6)], rgba(shade(cc, 0.55)), 0.8)
        _dashed(c, [(x0 + 1, y0 + 7), (x0 + 1, y0 + 23), (x0 + 23, y0 + 23), (x0 + 23, y0 + 7)], shade(cc, 0.6))
        _button(c, fx, x0 + 12, y0 + 3, shade(cc, 0.55), 1.3)
        fx["sh"].line([(x0, y0 + 7.5), (x0 + 24, y0 + 7.5)], 30, 1.6)
        fx["sh"].line([(x0 + 25, y0), (x0 + 25, y0 + 25)], 26, 1.8)
        fx["hi"].line([(x0 + 2, y0 + 9), (x0 + 2, y0 + 22)], 16, 1.0)
    elif name == "crease":
        fx["hi"].line([(32, 2), (32, 104)], 26, 0.9)
        fx["sh"].line([(33.5, 2), (33.5, 104)], 14, 1.2)
        fx["hi"].line([(160, 2), (160, 104)], 18, 0.9)
    elif name == "piping":
        pc = _col(p, "colour", acc)
        c.line([(224, wv + 8), (224, 104)], rgba(shade(pc, 0.7)), 2.0)                       # one line only (never stripes)
        c.line([(224, wv + 8), (224, 104)], rgba(pc), 1.3)


def draw(region, parts, c, col, fx, ctx, warnings):
    fn = {"torso": torso_part, "arms": arm_part, "legs": leg_part}[region]
    for p in parts or []:
        name = p if isinstance(p, str) else p.get("name")
        if name not in PARTS[region]:
            warnings.append(f"{region}: part '{name}' not available; not drawn")
            continue
        fn(name, p if isinstance(p, dict) else {}, c, col, fx, ctx)

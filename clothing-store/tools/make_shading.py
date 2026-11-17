"""Build the shared outfit shading layers: templates/shading/outfit/{torso,arm,leg}.png.

Each file is an L-mode strip (see clothing.py) where 128 = no change, lower = shadow,
higher = highlight. Every outfit reuses the same three files, so all items share one
construction: folds, highlights, seam darkening, collar / hem / cuff / shoe lines at the
positions in clothing.OUTFIT.

Continuity rules baked in here:
  * torso and arm use the same top gradient and shoulder light, and keep their own
    features away from the edges that touch at the shoulder (validate.py checks it);
  * torso rows below the outfit's hem line are replaced by leg-strip pixels in render.py, and
    the hem itself moves per outfit, so hem shadows are render features, not part of this layer.

Also writes templates/shading/outfit_preview.png (all layers on mid-grey) to check by eye.
Run: python tools/make_shading.py
"""
from PIL import Image, ImageChops
from clothing import (Part, Canvas, H, M, S, OUTFIT, load_regions, paste_part, mirror_strip,
                      apply_shading, shading_path, ROOT)

TOP_LIGHT = 10        # shared by torso and arm so the shoulder rows match
SHOULDER_LIGHT = 8


class Shade:
    """Two wrap canvases (shadow, highlight) drawn in layers, each blurred by its own radius."""

    def __init__(self, part):
        self.part = part
        self.sh = Image.new("L", Canvas(part, "L", 0).img.size, 0)
        self.hi = self.sh.copy()

    def _layer(self, which, blur, draw):
        c = Canvas(self.part, "L", 0)
        draw(c)
        if blur:
            c.blur(blur)
        if which == "sh":
            self.sh = ImageChops.add(self.sh, c.img)
        else:
            self.hi = ImageChops.add(self.hi, c.img)

    def shadow(self, blur, draw):
        self._layer("sh", blur, draw)

    def light(self, blur, draw):
        self._layer("hi", blur, draw)

    def gradient(self, top_light, bottom_dark, start=60):
        def draw_hi(c):
            for v in range(-M, H + M):
                val = max(0, round(top_light * (1 - (v + M) / (M + start))))
                if val:
                    c.band(v, v + 1, val)

        def draw_sh(c):
            for v in range(start, H + M):
                c.band(v, v + 1, min(bottom_dark, round(bottom_dark * (v - start) / (H - start))))
        self.light(0, draw_hi)
        if bottom_dark:
            self.shadow(0, draw_sh)

    def corners(self, val=22, width=2.5, blur=3.0):
        """Darken every box corner (side-face seams) equally on both sides."""
        us = [self.part.off[f] for f in ("front", "left", "back", "right")]
        self.shadow(blur, lambda c: [c.line([(u, 4), (u, H + M)], val, width) for u in us])

    def result(self):
        base = Image.new("L", self.sh.size, 128)
        out = ImageChops.subtract(ImageChops.add(base, self.hi), self.sh)
        return out.crop((self.part.P * S, 0, 2 * self.part.P * S, out.height))


def torso(part):
    s = Shade(part)
    s.gradient(top_light=TOP_LIGHT, bottom_dark=12)
    s.light(4, lambda c: c.band(-M, 0, SHOULDER_LIGHT))           # shoulders catch light
    s.light(14, lambda c: c.ellipse(64, 34, 34, 20, 26))          # chest highlight
    s.light(14, lambda c: c.ellipse(256, 30, 40, 18, 16))         # shoulder blades
    # under arms: kept below the top row, which meets the arm's top face at the shoulder
    s.shadow(8, lambda c: (c.ellipse(160, 32, 16, 20, 34), c.ellipse(352, 32, 16, 20, 34)))
    s.shadow(5, lambda c: c.ellipse(64, 0, 30, 10, 30))           # under collar / neckline
    s.shadow(4, lambda c: c.line([(40, 58), (64, 61), (88, 58)], 12, 3))  # under-chest crease
    s.shadow(3.5, lambda c: [c.line(p, 24, 2.5) for p in (
        [(16, 72), (38, 96)], [(112, 72), (90, 96)], [(26, 86), (44, 98)], [(102, 86), (84, 98)],
        [(210, 78), (234, 98)], [(302, 78), (278, 98)], [(142, 64), (174, 96)], [(370, 64), (338, 96)])])
    s.corners()
    # hem lines are drawn per outfit by render.py, because torso.hem_line moves (crop / full length)
    return s.result()


def arm(part):
    s = Shade(part)
    s.gradient(top_light=TOP_LIGHT, bottom_dark=10)
    s.shadow(6, lambda c: c.rect(72, 10, 120, H, 18))               # inner face (kept off the edges)
    s.light(10, lambda c: c.ellipse(224, 18, 22, 22, 22))           # outer shoulder
    s.light(10, lambda c: c.ellipse(30, 34, 14, 22, 12))            # front of upper arm
    s.light(4, lambda c: c.band(-M, 0, SHOULDER_LIGHT))
    s.shadow(2.5, lambda c: [c.line(p, v, 2) for p, v in (
        # elbow creases sit on the measured R15 elbow (~row 50)
        ([(6, 54), (30, 50), (56, 56)], 24), ([(10, 64), (34, 60), (54, 66)], 18),
        ([(74, 52), (96, 55), (118, 58)], 26), ([(76, 64), (96, 66), (116, 68)], 18),
        ([(136, 50), (184, 54)], 14))])
    s.shadow(2, lambda c: [c.line([(o + a, 88 + (i % 2) * 4), (o + a + 18, 92 + (i % 2) * 4)], 18, 1.6)
                           for o in (0, 64, 128, 192) for i, a in enumerate((6, 30, 40))])
    s.corners()
    cuff, end = OUTFIT["cuff_top"], OUTFIT["sleeve_end"]
    s.shadow(1.5, lambda c: (c.band(cuff - 1.2, cuff, 36), c.band(end - 1, end, 22)))
    s.light(1.0, lambda c: c.band(cuff + 0.5, cuff + 1.5, 16))
    return s.result()


def leg(part):
    """The leg strip also supplies the torso hip zone (its rows v < 0), so keep that area smooth."""
    s = Shade(part)
    s.gradient(top_light=0, bottom_dark=6, start=40)
    s.shadow(8, lambda c: c.rect(72, 6, 120, H, 16))                # inner face
    s.light(10, lambda c: c.ellipse(30, 26, 18, 24, 22))            # thigh
    s.light(10, lambda c: c.ellipse(224, 26, 18, 24, 14))           # outer hip
    s.light(5, lambda c: c.ellipse(32, 46, 14, 8, 14))              # knee
    s.shadow(4, lambda c: [c.line(p, 18, 2.5) for p in (            # crotch folds in the hip zone
        [(48, -14), (62, -1)], [(80, -14), (66, -1)])])
    s.shadow(2.5, lambda c: [c.line(p, v, 2) for p, v in (
        ([(8, 54), (32, 50), (56, 56)], 24), ([(12, 64), (32, 61), (52, 66)], 16),
        ([(138, 56), (162, 59), (186, 60)], 26), ([(142, 64), (162, 66), (182, 66)], 18),
        ([(74, 52), (118, 58)], 14))])
    s.shadow(2, lambda c: [c.line(p, v, 1.8) for o in (0, 64, 128, 192) for p, v in (
        ([(o + 6, 86), (o + 30, 82), (o + 58, 88)], 22), ([(o + 4, 92), (o + 34, 89), (o + 60, 93)], 18))])
    s.corners()
    cuff, shoe, sole = OUTFIT["leg_cuff_top"], OUTFIT["shoe_top"], OUTFIT["sole_top"]
    s.shadow(1.5, lambda c: (c.band(cuff - 1.2, cuff, 36), c.band(shoe - 0.5, shoe + 1.0, 34),
                             c.band(sole - 0.6, sole + 0.4, 20)))
    s.light(1.0, lambda c: c.band(cuff + 0.5, cuff + 1.5, 16))
    s.light(4, lambda c: c.ellipse(32, 115, 16, 5, 18))               # toe cap
    s.shadow(4, lambda c: c.band(H, H + M, 16))                        # sole underside
    return s.result()


def main():
    regions = load_regions()
    builders = (("torso", "shirt", "torso", torso), ("arm", "shirt", "right_arm", arm), ("leg", "pants", "right_leg", leg))
    for kind, garment, name, fn in builders:
        path = shading_path(kind)
        path.parent.mkdir(parents=True, exist_ok=True)
        fn(Part(garment, name, regions)).save(path)
    # preview: every layer applied to flat mid-grey, laid out as shirt (left) and pants (right) templates
    sheets = []
    for garment, parts in (("shirt", ("torso", "right_arm", "left_arm")), ("pants", ("torso", "right_leg", "left_leg"))):
        canvas = Image.new("RGBA", tuple(regions["canvas"]), (0, 0, 0, 0))
        for name in parts:
            part = Part(garment, name, regions)
            kind = "torso" if name == "torso" else ("arm" if "arm" in name else "leg")
            layer = Image.open(shading_path(kind)).convert("L")
            grey = apply_shading(Image.new("RGBA", layer.size, (150, 150, 150, 255)), layer)
            if name.startswith("left"):
                grey = mirror_strip(grey, part)
            paste_part(canvas, grey, part)
        sheets.append(canvas)
    out = Image.new("RGBA", (585 * 2 + 10, 559), (0, 0, 0, 0))
    out.paste(sheets[0], (0, 0)); out.paste(sheets[1], (595, 0))
    out.save(ROOT / "templates" / "shading" / "outfit_preview.png")
    print("wrote", ", ".join(str(shading_path(k).relative_to(ROOT)) for k in ("torso", "arm", "leg")))


if __name__ == "__main__":
    main()

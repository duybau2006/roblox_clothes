"""Render the calibration outfit: calibration/calibration-shirt.png and calibration-pants.png.

Every panel gets a distinct colour, its name, an arrow pointing to the top of the panel image,
a 16 px grid, and tags on each edge naming the panel regions.json says it joins. Assumed split
points are drawn as labelled lines:
  torso  LOWER TORSO split (R15 UpperTorso / LowerTorso)    = OUTFIT["waist_line"]
  arms   HAND area starts (sleeves end here)                = OUTFIT["sleeve_end"]
  legs   FOOT/SHOE area starts                              = OUTFIT["shoe_top"]
Values were measured in Studio on 2026-11-16 (see calibration/README.md, Results).
  limbs  y=52   template dotted guide line
Compare the in-Studio look against these labels to correct regions.json / clothing.OUTFIT.
Run: python tools/calibration.py
"""
import colorsys
from PIL import Image, ImageDraw, ImageFont

from clothing import ROOT, load_regions, OUTFIT

S = 4
ABBR = {"torso": "TORSO", "right_arm": "R ARM", "left_arm": "L ARM", "right_leg": "R LEG", "left_leg": "L LEG"}
SHORT = {"torso": "T", "right_arm": "RA", "left_arm": "LA", "right_leg": "RL", "left_leg": "LL"}
FACE_SHORT = {"front": "F", "back": "B", "left": "L", "right": "R", "top": "TOP", "bottom": "BOT"}
LINES = {  # part kind -> [(y, label, colour)]
    "torso": [(OUTFIT["waist_line"], f"LOWER TORSO {OUTFIT['waist_line']}", (255, 255, 255))],
    "arm": [(52, "guide 52", (40, 40, 40)), (OUTFIT["sleeve_end"], f"HAND {OUTFIT['sleeve_end']}", (255, 255, 255))],
    "leg": [(52, "guide 52", (40, 40, 40)), (OUTFIT["shoe_top"], f"FOOT {OUTFIT['shoe_top']}", (255, 255, 255))],
}


def font(px):
    try:
        return ImageFont.truetype("arialbd.ttf", px)
    except OSError:
        return ImageFont.load_default()


def draw_panel(d, name, p, colour, neighbours, tag):
    x, y, w, h = p["x"] * S, p["y"] * S, p["w"] * S, p["h"] * S
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=colour)
    for g in range(16, max(p["w"], p["h"]), 16):          # 16 px grid
        if g < p["w"]:
            d.line([(x + g * S, y), (x + g * S, y + h)], fill=(0, 0, 0, 70), width=2)
        if g < p["h"]:
            d.line([(x, y + g * S), (x + w, y + g * S)], fill=(0, 0, 0, 70), width=2)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=(0, 0, 0), width=3)
    part, face = name.split(".")
    kind = "torso" if part == "torso" else ("arm" if "arm" in part else "leg")
    if face not in ("top", "bottom"):
        for ly, label, lc in LINES[kind]:
            yy = y + ly * S
            for xx in range(x, x + w, 24):                    # dashed
                d.line([(xx, yy), (min(xx + 14, x + w), yy)], fill=lc, width=5)
            d.text((x + w - 6, yy + 6), label, fill=lc, font=font(24), anchor="rt", stroke_width=3, stroke_fill=(0, 0, 0))
    # arrow pointing to the top of the panel image
    cx, top = x + w / 2, y + 14 * S
    d.polygon([(cx, top), (cx - 24, top + 34), (cx + 24, top + 34)], fill=(255, 255, 255), outline=(0, 0, 0))
    d.rectangle([cx - 8, top + 34, cx + 8, top + 34 + 50], fill=(255, 255, 255), outline=(0, 0, 0))
    label = f"{tag} {ABBR[part]}\n{face.upper()}"
    ty = y + h / 2 if face in ("top", "bottom") else (y + h * 0.55 if part == "torso" else y + 82 * S)
    d.multiline_text((x + w / 2, ty), label, fill=(255, 255, 255),
                     font=font(44 if p["w"] >= 128 else 34), anchor="mm", align="center",
                     stroke_width=4, stroke_fill=(0, 0, 0))
    # edge tags: which panel regions.json says this edge joins
    pos = {"top": (x + w / 2, y + 22), "bottom": (x + w / 2, y + h - 22),
           "left": (x + 30, y + h * 0.36), "right": (x + w - 30, y + h * 0.36)}
    for edge, other in neighbours.items():
        ex, ey = pos[edge]
        d.text((ex, ey), other, fill=(255, 255, 0), font=font(26), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))


def main():
    regions = load_regions()
    out_dir = ROOT / "calibration"
    out_dir.mkdir(exist_ok=True)
    for garment, tag in (("shirt", "S"), ("pants", "P")):
        g = regions["garments"][garment]
        names = list(g["panels"])
        neighbours = {n: {} for n in names}
        for sm in g["seams"]:
            a, b = sm["a"].split("."), sm["b"].split(".")
            neighbours[sm["a"]][sm["a_edge"]] = f"{SHORT[b[0]]}-{FACE_SHORT[b[1]]}" + ("~" if sm["reversed"] else "")
            neighbours[sm["b"]][sm["b_edge"]] = f"{SHORT[a[0]]}-{FACE_SHORT[a[1]]}" + ("~" if sm["reversed"] else "")
        img = Image.new("RGBA", (585 * S, 559 * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(img, "RGBA")
        for i, n in enumerate(names):
            r, gg, b = colorsys.hsv_to_rgb((i * 0.618034) % 1, 0.75, 0.82)
            draw_panel(d, n, g["panels"][n], (round(r * 255), round(gg * 255), round(b * 255), 255), neighbours[n], tag)
        img.resize((585, 559), Image.LANCZOS).save(out_dir / f"calibration-{garment}.png")
        img.resize((585 * 2, 559 * 2), Image.LANCZOS).save(out_dir / f"calibration-{garment}-2x-preview.png")
    print("wrote", out_dir)


if __name__ == "__main__":
    main()

"""Line-width calibration print: calibration/print-linewidth-shirt.png and -pants.png (585x559).

Torso front (light ink on dark fabric) and torso back (dark ink on light fabric) each show, at exact
pixel sizes with no smoothing: horizontal lines 1-6 px, vertical lines 1-6 px, ring outlines 1-6 px,
dots 1-6 px across, and stars 4/6/8/12/16 px. Numbers label each width. Arms and legs are plain.
View in Studio from normal play distance and note the thinnest line that still reads; that becomes
library.MIN_LINE_PX and the smallest decor size in the guides.
Run: python tools/calibration_print.py
"""
import math
from PIL import Image, ImageDraw, ImageFont

from clothing import ROOT, load_regions

DARK, LIGHT = (40, 40, 44, 255), (232, 228, 218, 255)


def font(px):
    try:
        return ImageFont.truetype("arialbd.ttf", px)
    except OSError:
        return ImageFont.load_default()


def star(cx, cy, r):
    return [(cx + math.sin(i * math.pi / 5) * (r if i % 2 == 0 else r * 0.42),
             cy - math.cos(i * math.pi / 5) * (r if i % 2 == 0 else r * 0.42)) for i in range(10)]


def panel(d, p, bg, ink):
    x, y, w, h = p["x"], p["y"], p["w"], p["h"]
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=bg)
    if w < 128 or h < 128:
        return
    f = font(7)
    for i in range(6):                                   # horizontal lines, widths 1-6
        yy = y + 6 + i * 9
        d.rectangle([x + 10, yy, x + 52, yy + i], fill=ink)
        d.text((x + 3, yy - 2), str(i + 1), fill=ink, font=f)
    for i in range(6):                                   # vertical lines, widths 1-6
        xx = x + 62 + i * 10
        d.rectangle([xx, y + 6, xx + i, y + 54], fill=ink)
        d.text((xx, y + 56), str(i + 1), fill=ink, font=f)
    for i in range(6):                                   # rings with outline widths 1-6
        cx, cy = x + 12 + i * 20, y + 80
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=ink, width=i + 1)
        d.text((cx - 2, cy + 10), str(i + 1), fill=ink, font=f)
    for i in range(6):                                   # dots 1-6 px across
        cx, cy = x + 10 + i * 9, y + 108
        d.rectangle([cx, cy, cx + i, cy + i], fill=ink)
    for j, r in enumerate((2, 3, 4, 6, 8)):              # stars 4-16 px across
        d.polygon(star(x + 64 + j * 11 + r / 2, y + 112, r), fill=ink)
    d.text((x + 60, y + 98), "4 6 8 12 16", fill=ink, font=f)


def main():
    regions = load_regions()
    out = ROOT / "calibration"
    for garment in ("shirt", "pants"):
        g = regions["garments"][garment]
        img = Image.new("RGBA", tuple(regions["canvas"]), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for name, p in g["panels"].items():
            if name == "torso.front":
                panel(d, p, DARK, LIGHT)
            elif name == "torso.back":
                panel(d, p, LIGHT, DARK)
            else:
                d.rectangle([p["x"], p["y"], p["x"] + p["w"] - 1, p["y"] + p["h"] - 1], fill=(120, 120, 126, 255))
        img.save(out / f"print-linewidth-{garment}.png")
        img.resize((585 * 3, 559 * 3), Image.NEAREST).save(out / f"print-linewidth-{garment}-3x-preview.png")
    print("wrote", out / "print-linewidth-shirt.png", "and pants")


if __name__ == "__main__":
    main()

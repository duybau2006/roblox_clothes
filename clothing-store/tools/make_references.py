"""Render the per-style reference swatches: styles/references/<style>/<item>.png and sheet.png.

Every swatch is drawn by the same code render.py uses (tools/motifs.py + render.paint_pattern), so a
reference is exactly what an outfit can use. Nothing here is copied from other creators' items.
Run: python tools/make_references.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import motifs                                              # noqa: E402
from clothing import ROOT, S, M, Part, Canvas, hex_rgb, rgba, shade, load_regions   # noqa: E402
from render import Colours, paint_pattern                  # noqa: E402

# style -> list of (label, kind, spec) ; kind "motif" uses decor-style entries, "pattern" uses base_pattern
REFS = {
    "y2k": [("butterfly", "motif", ("butterfly", "#C8A2C8", "#C9CED6", "#F7B6D2")),
            ("star", "motif", ("star", "#C9CED6", None, "#8FD3FF")),
            ("sparkle", "motif", ("sparkle", "#FFFFFF", None, "#F7B6D2")),
            ("heart", "motif", ("heart", "#FF69B4", None, "#FFFFFF")),
            ("flame", "motif", ("flame", "#FF69B4", "#FFD1E8", "#111111")),
            ("leopard", "pattern", ("leopard", ["#F7B6D2", "#111111", "#C8A2C8"]))],
    "vamp-goth": [("bat", "motif", ("bat", "#111111", None, "#5C0A1E")),
                  ("rose", "motif", ("rose", "#7A0A1E", "#1F3D2B", "#111111")),
                  ("web", "motif", ("web", "#C9CED6", None, "#111111")),
                  ("moon", "motif", ("moon", "#E8E8E8", None, "#111111")),
                  ("lace", "lace", ("#111111", "#E8E8E8")),
                  ("plaid", "pattern", ("plaid", ["#111111", "#5C0A1E", "#8A8A8A"]))],
    "grunge": [("rip", "rip", ("#2A2A2A", "#E8E4DC")),
               ("safety pin", "pin", ("#C0C0C0", "#3A3A3A")),
               ("patch", "patch", ("#5E6B47", "#E8E4DC", "#2A2A2A")),
               ("plaid", "pattern", ("plaid", ["#9B3B3B", "#141414", "#5E6B47"])),
               ("stripes", "pattern", ("stripes", ["#141414", "#9B3B3B"])),
               ("checker", "pattern", ("checker", ["#141414", "#E8E4DC"]))],
    "emo": [("star", "motif", ("star", "#FF1493", None, "#111111")),
            ("heart", "motif", ("heart", "#7B2CBF", None, "#111111")),
            ("lightning", "motif", ("lightning", "#39FF14", None, "#111111")),
            ("studs", "motif", ("stud", "#C0C0C0", "#FFFFFF", "#111111")),
            ("chain", "chain", ("#C0C0C0", "#111111")),
            ("stripes", "pattern", ("stripes", ["#111111", "#FF1493"]))],
    "archive": [("contrast stitch", "stitch", ("#E8E4DC", "#1A1A1A")),
                ("patch", "patch", ("#3A3A3A", "#E8E4DC", "#1A1A1A")),
                ("distress", "rip", ("#1A1A1A", "#8A8580")),
                ("washed solid", "pattern", ("solid", ["#2B2B2B"])),
                ("colour block", "pattern", ("colour-block", ["#1A1A1A", "#8A8580"]))],
    "gen-z": [("pocket star", "motif", ("star", "#111111", None, "#F5F5F2")),
              ("pocket heart", "motif", ("heart", "#9DB5D6", None, "#F5F5F2")),
              ("sparkle", "motif", ("sparkle", "#B9C7A5", None, "#F5F5F2")),
              ("heather solid", "pattern", ("solid", ["#8E9199"])),
              ("light denim", "pattern", ("denim", ["#9DB5D6"]))],
    "baddie": [("heart", "motif", ("heart", "#E0115F", None, "#111111")),
               ("butterfly", "motif", ("butterfly", "#C0C0C0", "#E0115F", "#111111")),
               ("flame", "motif", ("flame", "#E0115F", "#FFD1E8", "#111111")),
               ("chain", "chain", ("#C0C0C0", "#111111")),
               ("leopard", "pattern", ("leopard", ["#C19A6B", "#111111", "#8B5A2B"]))],
    "soft-girl": [("bow", "motif", ("bow", "#F7B6D2", "#FFFFFF", "#FFFFFF")),
                  ("heart", "motif", ("heart", "#F7B6D2", None, "#FFFFFF")),
                  ("cherry", "motif", ("cherry", "#D62839", "#2E6B3F", "#FFFFFF")),
                  ("flower", "motif", ("flower", "#A7C7E7", "#FFF3B0", "#FFFFFF")),
                  ("lace", "lace", ("#FFFFFF", "#F7B6D2")),
                  ("gingham", "pattern", ("plaid", ["#FFFFFF", "#F7B6D2", "#FFFFFF"]))],
    "preppy": [("argyle", "pattern", ("argyle", ["#1C2A4A", "#2E4A36", "#F3EBDD"])),
               ("cable knit", "pattern", ("cable", ["#F3EBDD"])),
               ("rugby stripe", "pattern", ("stripes", ["#1C2A4A", "#F3EBDD"])),
               ("plaid", "pattern", ("plaid", ["#1C2A4A", "#7A1F2B", "#FFFFFF"])),
               ("pocket star", "motif", ("star", "#F3EBDD", None, "#1C2A4A"))],
    "cottagecore": [("ditsy flower", "motif", ("flower", "#C99A9E", "#D9A93F", "#F3EBDD")),
                    ("cherry", "motif", ("cherry", "#B22222", "#5E6B47", "#F3EBDD")),
                    ("bow", "motif", ("bow", "#9CAF88", "#F3EBDD", "#F3EBDD")),
                    ("lace", "lace", ("#F3EBDD", "#9CAF88")),
                    ("gingham", "pattern", ("plaid", ["#F3EBDD", "#C99A9E", "#F3EBDD"])),
                    ("knit", "pattern", ("knit", ["#9CAF88"]))],
    "christmas": [("star", "motif", ("star", "#D4AF37", None, "#B22222")),
                  ("snow sparkle", "motif", ("sparkle", "#FFFFFF", None, "#1F5E3A")),
                  ("heart", "motif", ("heart", "#FFFFFF", None, "#B22222")),
                  ("candy stripe", "pattern", ("stripes", ["#B22222", "#FFFFFF"])),
                  ("cable knit", "pattern", ("cable", ["#1F5E3A"])),
                  ("tartan", "pattern", ("plaid", ["#B22222", "#1F5E3A", "#D4AF37"]))],
    "athleisure": [("lightning", "motif", ("lightning", "#9CAF88", None, "#151515")),
                   ("star", "motif", ("star", "#C8A2C8", None, "#151515")),
                   ("colour block", "pattern", ("colour-block", ["#151515", "#A6A6A6"])),
                   ("heather", "pattern", ("solid", ["#A6A6A6"]))],
}

TILE, ZOOM = 64, 3


def swatch(part, label, kind, spec):
    c = Canvas(part)
    if kind == "pattern":
        name, pal = spec
        paint_pattern(c, name, Colours(pal), {"width": 4} if name == "stripes" else {})
    else:
        bg = spec[{"motif": -1, "lace": 1, "chain": 1, "rip": 0, "pin": 1, "patch": 2, "stitch": 1}[kind]]
        c.band(-M, 200, rgba(hex_rgb(bg)))
        fx = {"sh": Canvas(part, "L", 0)}
        if kind == "motif":
            m, col, acc, _ = spec
            motifs.MOTIFS[m](c, 64, 40, 3.5 if m == "stud" else 17, hex_rgb(col), hex_rgb(acc) if acc else shade(hex_rgb(col), 1.45))
            if m == "stud":
                for du in (-12, 12):
                    motifs.MOTIFS[m](c, 64 + du, 40, 3.5, hex_rgb(col), hex_rgb(acc))
        elif kind == "lace":
            motifs.lace(c, 40, hex_rgb(spec[0]), P=part.P)
        elif kind == "chain":
            motifs.chain(c, [(36, 22), (50, 44), (64, 50), (78, 44), (92, 22)], hex_rgb(spec[0]), link=3.0)
        elif kind == "rip":
            motifs.rip(c, 64, 40, 18, hex_rgb(spec[0]), hex_rgb(spec[1]), fx)
        elif kind == "pin":
            motifs.safety_pin(c, 64, 40, 12, hex_rgb(spec[0]))
        elif kind == "patch":
            motifs.patch(c, 64, 40, 18, hex_rgb(spec[0]), hex_rgb(spec[1]))
        elif kind == "stitch":
            for x in (44, 84):
                motifs.dashed(c, [(x, 8), (x, 72)], hex_rgb(spec[0]), width=0.7)
            motifs.dashed(c, [(32, 30), (96, 30)], hex_rgb(spec[0]), width=0.7)
    strip = c.strip()
    tile = strip.crop((32 * S, (M + 8) * S, 96 * S, (M + 72) * S)).resize((TILE, TILE), Image.LANCZOS)
    return tile.resize((TILE * ZOOM, TILE * ZOOM), Image.NEAREST)


def main():
    part = Part("shirt", "torso", load_regions())
    try:
        font = ImageFont.truetype("arialbd.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    out = ROOT / "styles" / "references"
    for style, items in REFS.items():
        d = out / style
        d.mkdir(parents=True, exist_ok=True)
        tiles = []
        for label, kind, spec in items:
            t = swatch(part, label, kind, spec)
            t.convert("RGB").save(d / f"{label.replace(' ', '-')}.png")
            tiles.append((label, t))
        w = TILE * ZOOM
        sheet = Image.new("RGB", (len(tiles) * (w + 10) + 10, w + 50), "white")
        dr = ImageDraw.Draw(sheet)
        for i, (label, t) in enumerate(tiles):
            sheet.paste(t.convert("RGB"), (10 + i * (w + 10), 10))
            dr.text((10 + i * (w + 10) + w / 2, w + 30), label, fill=(30, 30, 30), font=font, anchor="mm")
        sheet.save(d / "sheet.png")
    print("wrote references for", ", ".join(REFS))


if __name__ == "__main__":
    main()

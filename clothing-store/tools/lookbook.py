"""Lookbook of every guide example: render + preview each one, then one front sheet and one back sheet,
one row per design family.

    python tools/lookbook.py      -> styles/guides/lookbook.png, lookbook-back.png
                                     (renders in styles/guides/examples/renders/, previews in examples/previews/<id>/)
"""
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clothing import ROOT          # noqa: E402
from render import render          # noqa: E402

EX = ROOT / "styles" / "guides" / "examples"
FAMILIES = ("decorated", "print", "combined", "realistic", "owner")
TILE_H = 300


def font(px):
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    rows = {f: [] for f in FAMILIES}
    for sp in sorted(EX.glob("*.yaml")):
        spec = yaml.safe_load(sp.read_text(encoding="utf-8"))
        oid = spec.get("id") or sp.stem
        render(sp, EX / "renders")
        subprocess.run([sys.executable, str(ROOT / "tools" / "preview.py"), str(sp), "--renders", str(EX / "renders"),
                        "--out", str(EX / "previews" / oid)], check=True, capture_output=True)
        label = (spec.get("listings") or {}).get("words", {})
        rows["owner" if oid.startswith("owner-") else spec.get("family", "decorated")].append((oid, f"{spec.get('style')}: {label.get('colour', '')} {label.get('garment', '')}"))
    rows["print"] += rows.pop("combined")
    for view, name in (("front", "lookbook.png"), ("back", "lookbook-back.png")):
        tiles = {}
        for fam, items in rows.items():
            tiles[fam] = []
            for oid, label in items:
                im = Image.open(EX / "previews" / oid / f"together_{view}.png").convert("RGB")
                im = im.resize((round(im.width * TILE_H / im.height), TILE_H), Image.LANCZOS)
                tiles[fam].append((label, im))
        cols = max(len(t) for t in tiles.values())
        tw = max(im.width for t in tiles.values() for _, im in t)
        lab, head, gap = 26, 44, 10
        W = 20 + cols * (tw + gap)
        H = sum(head + TILE_H + lab + gap for _ in tiles) + 10
        out = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(out)
        f_head, f_lab = font(26), font(14)
        y = 10
        titles = {"decorated": "Decorated family", "print": "Print + combined families", "realistic": "Realistic family",
                  "owner": "Owner artwork (imported 2026-11-16), one outfit per style, all three families"}
        for fam, t in tiles.items():
            d.text((14, y + 8), titles[fam], fill=(20, 20, 20), font=f_head)
            y += head
            for i, (label, im) in enumerate(t):
                x = 14 + i * (tw + gap)
                out.paste(im, (x + (tw - im.width) // 2, y))
                d.text((x + tw / 2, y + TILE_H + 12), label[:34], fill=(60, 60, 60), font=f_lab, anchor="mm")
            y += TILE_H + lab + gap
        out.save(ROOT / "styles" / "guides" / name)
        print("wrote", ROOT / "styles" / "guides" / name, out.size)


if __name__ == "__main__":
    main()

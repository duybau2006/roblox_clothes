"""Local avatar preview (no upload): put an outfit's shirt and pants PNGs on a blocky R15-style rig.

Usage:
    python tools/preview.py specs/<id>.yaml [--renders DIR] [--out previews/<id>]

Writes previews/<id>/<wear>_<view>.png for wear = together | shirt_only | pants_only and
view = front | back | left | right (plus together_three_quarter.png), and sheet.png with
one row per wear. "shirt_only" / "pants_only" show what a buyer who owns only one half sees.
Layering follows Roblox: skin, then pants, then shirt on top (shirt torso covers pants torso).
This approximates the in-game look (orthographic camera, flat light, no limb joints); it is a
check for seams, alignment and shading, not a replacement for a final in-Studio test.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from clothing import ROOT, load_regions

SKIN = (214, 178, 140, 255)
BG_TOP, BG_BOT = (236, 238, 242), (206, 210, 218)
ZOOM = 3
HEAD_W, HEAD_H = 76, 64


def face(textures, regions, part_shirt, part_pants, face_name, size):
    """Composite one body-part face: skin -> pants -> shirt."""
    img = Image.new("RGBA", size, SKIN)
    for garment, part in (("pants", part_pants), ("shirt", part_shirt)):
        tex = textures.get(garment)
        if tex is None or part is None:
            continue
        p = regions["garments"][garment]["panels"][f"{part}.{face_name}"]
        img.alpha_composite(tex.crop((p["x"], p["y"], p["x"] + p["w"], p["y"] + p["h"])))
    return img


def head(w=HEAD_W, h=HEAD_H, side=False):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=14, fill=SKIN)
    if not side:  # plain neutral face marks so front/back are easy to tell apart
        d.ellipse([w * 0.3 - 3, h * 0.42 - 4, w * 0.3 + 3, h * 0.42 + 4], fill=(40, 40, 40, 255))
        d.ellipse([w * 0.7 - 3, h * 0.42 - 4, w * 0.7 + 3, h * 0.42 + 4], fill=(40, 40, 40, 255))
        d.arc([w * 0.35, h * 0.5, w * 0.65, h * 0.72], 20, 160, fill=(40, 40, 40, 255), width=2)
    return img


def background(w, h):
    bg = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOT)) + (255,))
    return bg


def ortho(textures, regions, view):
    F = lambda ps, pp, f, s: face(textures, regions, ps, pp, f, s)
    pad = 24
    if view in ("front", "back"):
        W, Hh = 256 + 2 * pad, HEAD_H + 256 + 2 * pad
        img = background(W, Hh)
        x0, y0 = pad, pad + HEAD_H
        if view == "front":
            arms = (("right_arm", 0), ("left_arm", 192)); legs = (("right_leg", 64), ("left_leg", 128))
        else:
            arms = (("left_arm", 0), ("right_arm", 192)); legs = (("left_leg", 64), ("right_leg", 128))
        hd = head(side=view == "back")
        img.alpha_composite(hd, (x0 + 128 - HEAD_W // 2, y0 - HEAD_H + 2))
        img.alpha_composite(F("torso", "torso", view, (128, 128)), (x0 + 64, y0))
        for name, dx in arms:
            img.alpha_composite(F(name, None, view, (64, 128)), (x0 + dx, y0))
        for name, dx in legs:
            img.alpha_composite(F(None, name, view, (64, 128)), (x0 + dx, y0 + 128))
        return img
    # side views: the arm covers the torso side (same depth), the near leg covers the far leg
    W, Hh = 64 + 2 * pad + 24, HEAD_H + 256 + 2 * pad
    img = background(W, Hh)
    x0, y0 = pad + 12, pad + HEAD_H
    arm, leg = ("right_arm", "right_leg") if view == "right" else ("left_arm", "left_leg")
    img.alpha_composite(head(64, HEAD_H, side=True), (x0, y0 - HEAD_H + 2))
    img.alpha_composite(F(arm, None, view, (64, 128)), (x0, y0))
    img.alpha_composite(F(None, leg, view, (64, 128)), (x0, y0 + 128))
    return img


def skew_side(face_img, depth_px=32, rise=16):
    """Map a 64-wide side face onto a receding parallelogram to the LEFT of a front face."""
    w, h = face_img.size
    out_w, out_h = depth_px, h + rise
    # output (x, y) -> input (u, v); far edge (x=0) sits `rise` px higher than the near edge
    a, c = w / depth_px, 0
    d, f = -rise / depth_px, 0
    img = face_img.transform((out_w, out_h), Image.AFFINE, (a, 0, c, d, 1, f), Image.BILINEAR)
    return ImageEnhance.Brightness(img).enhance(0.86)


def three_quarter(textures, regions):
    F = lambda ps, pp, f, s: face(textures, regions, ps, pp, f, s)
    pad, depth, rise = 24, 32, 16
    W, Hh = 256 + depth + 2 * pad, HEAD_H + 256 + rise + 2 * pad
    img = background(W, Hh)
    x0, y0 = pad + depth, pad + HEAD_H + rise
    # back to front: left arm, torso, left leg, right leg (+side), right arm (+side), head
    img.alpha_composite(F("left_arm", None, "front", (64, 128)), (x0 + 192, y0))
    img.alpha_composite(F("torso", "torso", "front", (128, 128)), (x0 + 64, y0))
    img.alpha_composite(F(None, "left_leg", "front", (64, 128)), (x0 + 128, y0 + 128))
    img.alpha_composite(skew_side(F(None, "right_leg", "right", (64, 128)), depth, rise), (x0 + 64 - depth, y0 + 128 - rise))
    img.alpha_composite(F(None, "right_leg", "front", (64, 128)), (x0 + 64, y0 + 128))
    img.alpha_composite(skew_side(F("right_arm", None, "right", (64, 128)), depth, rise), (x0 - depth, y0 - rise))
    img.alpha_composite(F("right_arm", None, "front", (64, 128)), (x0, y0))
    hx = x0 + 128 - HEAD_W // 2
    img.alpha_composite(skew_side(head(64, HEAD_H, side=True), 20, 10), (hx - 20, y0 - HEAD_H - 8))
    img.alpha_composite(head(), (hx, y0 - HEAD_H + 2))
    return img


WEARS = (("together", ("shirt", "pants")), ("shirt_only", ("shirt",)), ("pants_only", ("pants",)))
VIEWS = ("front", "back", "left", "right")


def label_font(size):
    try:
        return ImageFont.truetype("arialbd.ttf", size)
    except OSError:
        return ImageFont.load_default()


def main():
    import yaml
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--renders", default=str(ROOT / "renders"))
    ap.add_argument("--out")
    a = ap.parse_args()
    spec = yaml.safe_load(Path(a.spec).read_text(encoding="utf-8"))
    oid = spec.get("id") or Path(a.spec).stem
    regions = load_regions()
    tex = {g: Image.open(Path(a.renders) / f"{oid}-{g}.png").convert("RGBA") for g in ("shirt", "pants")
           if (Path(a.renders) / f"{oid}-{g}.png").exists()}       # separates (coverage top_only / bottom_only) have one file
    out = Path(a.out) if a.out else ROOT / "previews" / oid
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for wear, garments in WEARS:
        if not all(g in tex for g in garments):
            continue
        textures = {g: tex[g] for g in garments}
        views = [(v, ortho(textures, regions, v)) for v in VIEWS]
        if wear == "together":
            views.insert(1, ("three_quarter", three_quarter(textures, regions)))
        big = []
        for name, im in views:
            b = im.resize((im.width * ZOOM, im.height * ZOOM), Image.NEAREST)
            b.convert("RGB").save(out / f"{wear}_{name}.png")
            big.append((name, b))
        rows.append((wear, big))
    gap, head, side = 12, 40, 210
    width = side + max(sum(b.width for _, b in big) + gap * len(big) for _, big in rows)
    height = sum(max(b.height for _, b in big) + head + gap for _, big in rows) + gap
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    font, big_font = label_font(24), label_font(30)
    y = gap
    for wear, big in rows:
        d.text((16, y + head + 60), wear.replace("_", " "), fill=(20, 20, 20), font=big_font)
        x = side
        for name, b in big:
            d.text((x + b.width / 2, y + head / 2), name.replace("_", " "), fill=(60, 60, 60), font=font, anchor="mm")
            sheet.paste(b, (x, y + head))
            x += b.width + gap
        y += max(b.height for _, b in big) + head + gap
    sheet.save(out / "sheet.png")
    print("wrote previews to", out)


if __name__ == "__main__":
    main()

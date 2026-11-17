"""Measure the official classic clothing templates and write templates/regions.json
plus labelled overlay PNGs (templates/regions_overlay_shirt.png / _pants.png).

Run from anywhere:  python tools/build_regions.py
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = ROOT / "templates" / "official"
TEMPLATES = {"shirt": "Template-Shirts-R15.png", "pants": "Template-Pants-R15.png"}

# Approximate layout (from the template art) used only as search windows; exact
# boxes are measured from the pixel colours below.
APPROX = {
    "torso":      {"top": (231, 8, 128, 64), "right": (165, 74, 64, 128), "front": (231, 74, 128, 128),
                   "left": (361, 74, 64, 128), "back": (427, 74, 128, 128), "bottom": (231, 204, 128, 64)},
    "right_limb": {"top": (217, 289, 64, 64), "left": (19, 355, 64, 128), "back": (85, 355, 64, 128),
                   "right": (151, 355, 64, 128), "front": (217, 355, 64, 128), "bottom": (217, 485, 64, 64)},
    "left_limb":  {"top": (308, 289, 64, 64), "front": (308, 355, 64, 128), "left": (374, 355, 64, 128),
                   "back": (440, 355, 64, 128), "right": (506, 355, 64, 128), "bottom": (308, 485, 64, 64)},
}
PART_NAMES = {"shirt": {"torso": "torso", "right_limb": "right_arm", "left_limb": "left_arm"},
              "pants": {"torso": "torso", "right_limb": "right_leg", "left_limb": "left_leg"}}

# Every part's side faces wrap in the same cyclic order front -> left -> back -> right -> front.
# Edge direction convention: horizontal edges are read left->right, vertical edges top->bottom.
# "reversed": true means the two edges run in opposite directions.
SEAM_RULES = [
    ("front", "right", "left", "left", False),
    ("left", "right", "back", "left", False),
    ("back", "right", "right", "left", False),
    ("right", "right", "front", "left", False),
    ("top", "bottom", "front", "top", False),
    ("top", "right", "left", "top", True),
    ("top", "top", "back", "top", True),
    ("top", "left", "right", "top", False),
    ("bottom", "top", "front", "bottom", False),
    ("bottom", "right", "left", "bottom", False),
    ("bottom", "bottom", "back", "bottom", True),
    ("bottom", "left", "right", "bottom", True),
]

# Outfit seams: where the torso physically meets the arms (shoulder) and the legs (hip) on the
# avatar. Ranges are [start, end) pixel indices along each edge (same reading direction as above).
SHOULDER_ROWS = 32
OUTFIT_SEAMS = {
    "shoulder": [  # checked in the shirt file
        ("torso.front", "left", (0, SHOULDER_ROWS), "right_arm.front", "right", (0, SHOULDER_ROWS)),
        ("torso.front", "right", (0, SHOULDER_ROWS), "left_arm.front", "left", (0, SHOULDER_ROWS)),
        ("torso.back", "left", (0, SHOULDER_ROWS), "left_arm.back", "right", (0, SHOULDER_ROWS)),
        ("torso.back", "right", (0, SHOULDER_ROWS), "right_arm.back", "left", (0, SHOULDER_ROWS)),
        ("torso.top", "left", (0, 64), "right_arm.top", "right", (0, 64)),
        ("torso.top", "right", (0, 64), "left_arm.top", "left", (0, 64)),
    ],
    "hip": [  # checked in the pants file
        ("torso.front", "bottom", (0, 64), "right_leg.front", "top", (0, 64)),
        ("torso.front", "bottom", (64, 128), "left_leg.front", "top", (0, 64)),
        ("torso.left", "bottom", (0, 64), "left_leg.left", "top", (0, 64)),
        ("torso.back", "bottom", (0, 64), "left_leg.back", "top", (0, 64)),
        ("torso.back", "bottom", (64, 128), "right_leg.back", "top", (0, 64)),
        ("torso.right", "bottom", (0, 64), "right_leg.right", "top", (0, 64)),
    ],
}


def saturated(c):
    return max(c[:3]) - min(c[:3]) > 60


def measure(img, box):
    """Exact bbox of the dominant saturated colour inside a +-6 px window around box."""
    px = img.load()
    x0, y0, w, h = box
    cx, cy = x0 + w // 2, y0 + h // 4  # sample above the centre label text
    colour = px[cx, cy][:3]
    if not saturated(colour):
        raise SystemExit(f"no panel colour at {cx},{cy}")
    xs, ys = [], []
    for y in range(max(0, y0 - 6), min(img.height, y0 + h + 6)):
        for x in range(max(0, x0 - 6), min(img.width, x0 + w + 6)):
            c = px[x, y][:3]
            if sum(abs(a - b) for a, b in zip(c, colour)) <= 6:
                xs.append(x); ys.append(y)
    return [min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1], colour


def dashed_line_offset(img, box):
    """Row (relative to panel top) of the white dotted guide line inside a limb side panel."""
    px = img.load()
    x0, y0, w, h = box
    best = None
    for dy in range(h):
        whites = sum(1 for x in range(x0, x0 + w) if min(px[x, y0 + dy][:3]) > 240)
        if 0 < whites < w and (best is None or whites > best[1]):
            best = (dy, whites)
    return best[0] if best else None


def build():
    out = {
        "canvas": [585, 559],
        "bleed_px": 2,
        "edge_convention": "horizontal edges read left->right, vertical edges top->bottom; reversed=true means the two edges run in opposite directions",
        "side_order": ["front", "left", "back", "right"],
        "notes": [
            "Measured from the official R15 templates (Classic-Clothing-Templates.zip). Both templates share one layout.",
            "Limb 'left'/'right' faces are named from the avatar's point of view: on the right limb 'left' is the inner face, on the left limb 'left' is the outer face.",
            "top/bottom faces of every part attach to its front face (top above front, bottom below front).",
            "The pants torso is mostly hidden under the shirt torso; R15 LowerTorso uses roughly the bottom quarter of the torso panels.",
        ],
        "guide_colours": [],
        "garments": {},
    }
    guide = set()
    for garment, fname in TEMPLATES.items():
        img = Image.open(OFFICIAL / fname).convert("RGBA")
        assert img.size == (585, 559), (fname, img.size)
        guide.add(tuple(img.getpixel((2, 2))[:3]))
        panels, seams = {}, []
        for part, faces in APPROX.items():
            pname = PART_NAMES[garment][part]
            for face, approx in faces.items():
                box, colour = measure(img, approx)
                guide.add(tuple(colour))
                exp = (64 if face in ("left", "right") or part != "torso" else 128,
                       64 if face in ("top", "bottom") else 128)
                assert tuple(box[2:]) == exp, (garment, pname, face, box, exp)
                panels[f"{pname}.{face}"] = {"x": box[0], "y": box[1], "w": box[2], "h": box[3]}
            for a, ae, b, be, rev in SEAM_RULES:
                seams.append({"a": f"{pname}.{a}", "a_edge": ae, "b": f"{pname}.{b}", "b_edge": be, "reversed": rev})
        limb_front = panels[f"{PART_NAMES[garment]['right_limb']}.front"]
        torso_front = panels["torso.front"]
        out["garments"][garment] = {
            "template": f"templates/official/{fname}",
            "parts": list(PART_NAMES[garment].values()),
            "panels": panels,
            "seams": seams,
            "guide_lines": {
                "limb_dotted_line_from_panel_top": dashed_line_offset(img, tuple(limb_front.values())),
                "torso_dotted_line_from_panel_top": dashed_line_offset(img, tuple(torso_front.values())),
                "meaning": "template note: max height of gloves (shirt) / shoes and lower-leg details (pants) on R15",
            },
        }
    out["outfit_seams"] = {
        zone: [{"file": "shirt" if zone == "shoulder" else "pants", "a": a, "a_edge": ae, "a_range": list(ar),
                "b": b, "b_edge": be, "b_range": list(br), "reversed": False}
               for a, ae, ar, b, be, br in pairs]
        for zone, pairs in OUTFIT_SEAMS.items()}
    out["notes"].append("outfit_seams: torso<->arm (shoulder, top 32 rows + top faces) and torso<->leg (hip) edges that touch on the avatar; one outfit renders the torso once into both files.")
    out["rig_calibration"] = {
        "checked": "2026-11-16 in Roblox Studio with calibration/calibration-*.png on R15 and R6 block rigs",
        "panel_map": "confirmed: every panel on the expected face, upright, not mirrored, on both rigs",
        "seams": "confirmed: all edge tags (incl. top/bottom faces) name the panel they touch; shoulder and hip neighbours as in outfit_seams",
        "r6": "one part per body part; each side panel maps whole and uniformly (no splits)",
        "r15_splits_rows_from_panel_top": {"torso_upper_lower": 92, "elbow": 50, "hand": 110, "knee": 51, "foot": 106},
        "r15_note": "each R15 part maps its own slice of the panel at its own scale; splits measured +-2 px from screenshots",
    }
    out["guide_colours"] = sorted(["#%02x%02x%02x" % c for c in guide])
    (ROOT / "templates" / "regions.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


EDGE_COLOURS = ["#ff1744", "#2979ff", "#00c853", "#ffab00", "#d500f9", "#00b8d4",
                "#ff6d00", "#6200ea", "#aeea00", "#c51162", "#0091ea", "#64dd17"]


def edge_segment(p, edge, s):
    x, y, w, h = p["x"] * s, p["y"] * s, p["w"] * s, p["h"] * s
    i = 3 * s // 2
    return {"top": ((x, y + i), (x + w, y + i)), "bottom": ((x, y + h - i), (x + w, y + h - i)),
            "left": ((x + i, y), (x + i, y + h)), "right": ((x + w - i, y), (x + w - i, y + h))}[edge]


def overlay(data, garment):
    s = 2
    g = data["garments"][garment]
    base = Image.open(ROOT / g["template"]).convert("RGBA").resize((585 * s, 559 * s), Image.NEAREST)
    veil = Image.new("RGBA", base.size, (255, 255, 255, 170))
    img = Image.alpha_composite(base, veil)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arialbd.ttf", 15); small = ImageFont.truetype("arialbd.ttf", 12)
    except OSError:
        font = small = ImageFont.load_default()
    for name, p in g["panels"].items():
        x, y, w, h = p["x"] * s, p["y"] * s, p["w"] * s, p["h"] * s
        d.rectangle([x, y, x + w - 1, y + h - 1], outline="#000000", width=2)
        part, face = name.split(".")
        d.text((x + w / 2, y + h / 2 - 9), part.replace("_", " "), fill="#000", font=small, anchor="mm")
        d.text((x + w / 2, y + h / 2 + 8), face.upper(), fill="#000", font=font, anchor="mm")
        d.text((x + w / 2, y + h / 2 + 28), f"{p['x']},{p['y']} {p['w']}x{p['h']}", fill="#444", font=small, anchor="mm")
    # seams: same number + colour on both edges; arrow marks edge reading direction
    for i, sm in enumerate(g["seams"]):
        col = EDGE_COLOURS[i % 12]
        label = f"S{i + 1}" + ("r" if sm["reversed"] else "")
        for pn, edge, rev in ((sm["a"], sm["a_edge"], False), (sm["b"], sm["b_edge"], sm["reversed"])):
            (x0, y0), (x1, y1) = edge_segment(g["panels"][pn], edge, s)
            d.line([(x0, y0), (x1, y1)], fill=col, width=3)
            # direction tick at the end the edge "starts" from (start of a; start or end of b)
            sx, sy = ((x1, y1) if rev else (x0, y0))
            d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=col)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            off = {"top": (0, 12), "bottom": (0, -12), "left": (16, 0), "right": (-16, 0)}[edge]
            tx, ty = mx + off[0] + (14 if edge in ("top", "bottom") else 0), my + off[1] + (14 if edge in ("left", "right") else 0)
            d.rectangle([tx - 15, ty - 8, tx + 15, ty + 8], fill="#ffffff")
            d.text((tx, ty), label, fill=col, font=small, anchor="mm")
    framed = Image.new("RGBA", (img.width, img.height + 34), "#ffffff")
    framed.paste(img, (0, 0)); img = framed; d = ImageDraw.Draw(img)
    d.text((10, 559 * s + 10), f"{garment.upper()} region map: black boxes = panels; matching Sx labels = seam pairs; "
           "dot = start of the shared edge; 'r' = edges run in opposite directions",
           fill="#000", font=small)
    img.save(ROOT / "templates" / f"regions_overlay_{garment}.png")


def overlay_outfit(data):
    """Side-by-side map of the outfit seams: shoulder pairs on the shirt layout, hip pairs on the pants layout."""
    s = 2
    try:
        font = ImageFont.truetype("arialbd.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    halves = []
    for garment, zone, tag in (("shirt", "shoulder", "SH"), ("pants", "hip", "HP")):
        g = data["garments"][garment]
        base = Image.open(ROOT / g["template"]).convert("RGBA").resize((585 * s, 559 * s), Image.NEAREST)
        img = Image.alpha_composite(base, Image.new("RGBA", base.size, (255, 255, 255, 200)))
        d = ImageDraw.Draw(img)
        for name, p in g["panels"].items():
            d.rectangle([p["x"] * s, p["y"] * s, (p["x"] + p["w"]) * s - 1, (p["y"] + p["h"]) * s - 1], outline="#000", width=2)
            d.text(((p["x"] + p["w"] / 2) * s, (p["y"] + p["h"] / 2) * s), name.replace(".", "\n").replace("_", " "),
                   fill="#000", font=font, anchor="mm", align="center")
        for i, sm in enumerate(data["outfit_seams"][zone]):
            col = EDGE_COLOURS[i % 12]
            for pn, edge, rng in ((sm["a"], sm["a_edge"], sm["a_range"]), (sm["b"], sm["b_edge"], sm["b_range"])):
                (x0, y0), (x1, y1) = edge_segment(g["panels"][pn], edge, s)
                if edge in ("top", "bottom"):
                    x0, x1 = x0 + rng[0] * s, x0 + rng[1] * s
                else:
                    y0, y1 = y0 + rng[0] * s, y0 + rng[1] * s
                d.line([(x0, y0), (x1, y1)], fill=col, width=5)
                tx, ty = (x0 + x1) / 2, (y0 + y1) / 2
                d.rectangle([tx - 17, ty - 9, tx + 17, ty + 9], fill=col)
                d.text((tx, ty), f"{tag}{i + 1}", fill="#fff", font=font, anchor="mm")
        d.text((12, 12), f"{garment.upper()} file: {zone} seams (same label = edges that touch on the avatar)", fill="#000", font=font)
        halves.append(img)
    out = Image.new("RGBA", (halves[0].width * 2 + 10, halves[0].height), "#ffffff")
    out.paste(halves[0], (0, 0)); out.paste(halves[1], (halves[0].width + 10, 0))
    out.save(ROOT / "templates" / "regions_overlay_outfit.png")


if __name__ == "__main__":
    data = build()
    for gname in data["garments"]:
        overlay(data, gname)
    overlay_outfit(data)
    print("panels:", len(data["garments"]["shirt"]["panels"]), "seams:", len(data["garments"]["shirt"]["seams"]),
          "guide colours:", data["guide_colours"],
          "dotted lines:", data["garments"]["shirt"]["guide_lines"], data["garments"]["pants"]["guide_lines"])

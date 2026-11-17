"""Collected (outside) shading layers: import, seam-heal, check, save and apply.

Saved layers live in templates/shading/custom/<id>.png (L, 585x559 shirt layout, 128 = neutral)
with <id>.json (source, author, licence, fetched date, garment, style, seam results).

Import (run once per source; raw downloads stay outside the repo):
    python tools/shading_custom.py import <raw_dir>
Contact sheet (collected + skipped, with reasons):
    python tools/shading_custom.py sheet

Use in a spec:  shading: {layer: pd-pezsmistic-shirt-2, strength: 0.6}
The layer replaces the procedural torso/arm shading; legs keep procedural shading (no pants layers exist).
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clothing import ROOT, load_regions, panel_mask   # noqa: E402

CUSTOM = ROOT / "templates" / "shading" / "custom"
SKIPPED = ROOT / "styles" / "references" / "skipped.json"

PEZ = {"source_url": "https://devforum.roblox.com/t/free-shirt-shadows-and-shading/1607565",
       "author": "PeZsmistic (Roblox DevForum)",
       "licence": "Public-domain dedication by the author: 'I, PeZsmistic have waived all copyright and related or neighboring "
                  "rights to these clothing shadow templates ... The Work may be freely used for any purpose. You do not need to "
                  "ask for permission to use it or give me any credit.'",
       "credit": "not required (appreciated): PeZsmistic", "fetched": "2026-11-16"}
# raw file -> (id, garment, style, recommended strength)
LAYERS = {
    "blouse-1-v3.png": ("pd-pezsmistic-blouse-1", "blouse", "painted", 0.55),
    "blouse-2-v3.png": ("pd-pezsmistic-blouse-2", "blouse", "painted", 0.55),
    "shirt-1-v3.png": ("pd-pezsmistic-shirt-1", "shirt", "painted", 0.55),
    "shirt-2-v3.png": ("pd-pezsmistic-shirt-2", "shirt", "painted", 0.55),
    "shirt-3-v3.png": ("pd-pezsmistic-shirt-3", "shirt", "painted", 0.55),
    "template-v3.png": ("pd-pezsmistic-soft", "generic", "painted-soft", 0.5),
    "shirt-1-flat-v1.png": ("pd-pezsmistic-flat-1", "shirt", "flat", 0.45),
    "shirt-2-flat-v1.png": ("pd-pezsmistic-flat-2", "shirt", "flat", 0.45),
    "shirt-3-flat-v1.png": ("pd-pezsmistic-flat-3", "shirt", "flat", 0.45),
}
EXAMPLE_SUFFIXES = ("-v1.png", "-v2.png", "-hard.png", "-hard-simple-v1.png", "-hard-v1.png")


def to_map(raw):
    """Greyscale layer with alpha -> L map around 128 (alpha folded in)."""
    lum = raw.convert("LA")
    l, a = lum.split()
    neutral = Image.new("L", raw.size, 128)
    return Image.composite(l, neutral, a)


def edge_coords(p, edge, depth):
    x, y, w, h = p["x"], p["y"], p["w"], p["h"]
    if edge == "top":
        return [(x + i, y + depth) for i in range(w)]
    if edge == "bottom":
        return [(x + i, y + h - 1 - depth) for i in range(w)]
    if edge == "left":
        return [(x + depth, y + i) for i in range(h)]
    return [(x + w - 1 - depth, y + i) for i in range(h)]


def seam_pairs(regions):
    g = regions["garments"]["shirt"]
    out = [(s["a"], s["a_edge"], None, s["b"], s["b_edge"], None, s["reversed"]) for s in g["seams"]]
    out += [(s["a"], s["a_edge"], s["a_range"], s["b"], s["b_edge"], s["b_range"], False) for s in regions["outfit_seams"]["shoulder"]]
    return g["panels"], out


def heal(m, regions, band=4, extra=None):
    """Blend both sides of every seam toward their average over `band` px so edges meet.
    `extra` adds seam pairs (the hip, for layers that also shade the legs)."""
    px = m.load()
    panels, pairs = seam_pairs(regions)
    pairs = pairs + (extra or [])
    for a, ae, ar, b, be, br, rev in pairs:
        for d in range(band):
            ca, cb = edge_coords(panels[a], ae, d), edge_coords(panels[b], be, d)
            if ar:
                ca, cb = ca[ar[0]:ar[1]], cb[br[0]:br[1]]
            if rev:
                cb = cb[::-1]
            a0, b0 = edge_coords(panels[a], ae, 0), edge_coords(panels[b], be, 0)
            if ar:
                a0, b0 = a0[ar[0]:ar[1]], b0[br[0]:br[1]]
            if rev:
                b0 = b0[::-1]
            wgt = 1 - d / band
            for (pa, pb, ea, eb) in zip(ca, cb, a0, b0):
                t = (px[ea] + px[eb]) / 2
                px[pa] = round(px[pa] + (t - px[pa]) * wgt)
                px[pb] = round(px[pb] + (t - px[pb]) * wgt)
    return m


def seam_report(m, regions):
    """Worst mean seam difference of the layer applied to mid grey (0-255 scale)."""
    from validate import check_seam_list
    base = Image.merge("RGBA", (m, m, m, Image.new("L", m.size, 255)))
    g = regions["garments"]["shirt"]
    f1, w1 = check_seam_list(base, g["panels"], g["seams"])
    f2, w2 = check_seam_list(base, g["panels"], regions["outfit_seams"]["shoulder"])
    return {"failing_pairs": len(f1) + len(f2), "worst_mean": round(max(w1, w2), 1)}


def import_layers(raw_dir):
    regions = load_regions()
    CUSTOM.mkdir(parents=True, exist_ok=True)
    mask = panel_mask("shirt", regions)
    for name, (lid, garment, style, strength) in LAYERS.items():
        raw = Image.open(Path(raw_dir) / name).convert("RGBA")
        if raw.size != (585, 559):
            print("SKIP", name, raw.size)
            continue
        m = to_map(raw)
        m = Image.composite(m, Image.new("L", m.size, 128), mask)          # bounds: nothing outside the panels
        before = seam_report(m, regions)
        for _ in range(4):                       # several gentle passes: seams meet without a visible band
            m = heal(m, regions, band=5)
            after = seam_report(m, regions)
            if after["failing_pairs"] == 0:
                break
        m.save(CUSTOM / f"{lid}.png")
        meta = dict(PEZ, id=lid, file=f"{lid}.png", raw_name=name, garment=garment, style=style,
                    strength=strength, parts=["torso", "arms"], seams_before=before, seams_after=after)
        (CUSTOM / f"{lid}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(f"{lid}: seams before {before} -> after heal {after}")
    skipped = json.loads(SKIPPED.read_text(encoding="utf-8")) if SKIPPED.exists() else []
    skipped = [s for s in skipped if s.get("group") != "pezsmistic-examples"]
    for f in sorted(Path(raw_dir).glob("*.png")):
        if f.name not in LAYERS:
            skipped.append({"group": "pezsmistic-examples", "item": f.name, "source_url": PEZ["source_url"],
                            "reason": "example render on the author's demo shirt (blue / frog artwork), not a shading layer; "
                                      "the frog artwork is not covered by the waiver"})
    SKIPPED.write_text(json.dumps(skipped, indent=1), encoding="utf-8")


def load_layer(lid):
    p = CUSTOM / f"{lid}.png"
    if not p.exists():
        raise SystemExit(f"shading layer '{lid}' not found in templates/shading/custom/")
    return Image.open(p).convert("L"), json.loads((CUSTOM / f"{lid}.json").read_text(encoding="utf-8"))


def layers():
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(CUSTOM.glob("*.json"))}


def apply_layer(canvas, lid, strength, garment, regions):
    """Apply a collected layer to the torso (both files) and arms (shirt file), incl. 2 px bleed.
    Layers whose metadata lists "legs" also shade the legs in the pants file: the pants template puts the legs
    exactly where the shirt template puts the arms, and those layers are seam-healed across the hip too.
    Other layers fade out over the torso's last 20 rows so the hip meets the procedurally shaded legs."""
    from clothing import apply_shading
    m, meta = load_layer(lid)
    legs = "legs" in (meta.get("parts") or [])
    m = m.point(lambda v: max(0, min(255, round(128 + (v - 128) * strength))))
    m = m.copy()
    g = regions["garments"]["shirt"]["panels"]
    if not legs:
        neutral = Image.new("L", m.size, 128)
        ramp = Image.new("L", m.size, 0)
        rd = ImageDraw.Draw(ramp)
        for name, p in g.items():
            if name in ("torso.front", "torso.back", "torso.left", "torso.right"):
                for dy in range(p["h"] - 20, p["h"]):
                    k = (dy - (p["h"] - 20) + 1) / 20
                    rd.line([(p["x"], p["y"] + dy), (p["x"] + p["w"] - 1, p["y"] + dy)], fill=round(255 * k))
            elif name == "torso.bottom":
                rd.rectangle([p["x"], p["y"], p["x"] + p["w"] - 1, p["y"] + p["h"] - 1], fill=255)
        m = Image.composite(neutral, m, ramp)
    full = Image.new("L", m.size, 128)
    for name, p in g.items():                     # extend each panel's map into its 2 px bleed by edge replication
        if garment == "pants" and not name.startswith("torso.") and not legs:
            continue
        crop = m.crop((p["x"], p["y"], p["x"] + p["w"], p["y"] + p["h"]))
        big = crop.resize((p["w"] + 4, p["h"] + 4), Image.NEAREST)
        big.paste(crop, (2, 2))
        full.paste(big, (p["x"] - 2, p["y"] - 2))
    for name, p in g.items():
        if garment == "pants" and not name.startswith("torso.") and not legs:
            continue
        full.paste(m.crop((p["x"], p["y"], p["x"] + p["w"], p["y"] + p["h"])), (p["x"], p["y"]))
    return apply_shading(canvas, full, 1.0)


# ---------------------------------------------------------------- owner-supplied layers

OWNER = {"source_url": "made by the store owner (own work; confirmed in chat 2026-11-16)",
         "author": "the store owner", "licence": "owner's own work; the owner holds the rights (confirmed 2026-11-16)",
         "credit": "none needed", "fetched": "2026-11-16", "provenance": "owner-supplied", "licence_confirmed": True}
# raw file -> (id, style, recommended strength, how it was stored)
OWNER_LAYERS = {
    "1.png": ("own-shade-1", "soft scribble folds (black overlay)", 1.0, "overlay"),
    "2.png": ("own-shade-2", "radial folds with highlights (black + white overlay)", 1.0, "overlay"),
    "3.jpg": ("own-shade-3", "bold painted folds, shadows only (JPEG flattened on a checkerboard)", 0.8, "checker"),
}
CHECKER = {"sx": 1.3125, "ox": -16.0, "sy": 1.32, "oy": 53.0, "period": 35.2, "white": 254.0, "grey": 237.0}


def _hip_pairs(regions):
    """Hip seams expressed on shirt-template panel names (pants legs sit where the shirt arms are)."""
    out = []
    for s in regions["outfit_seams"]["hip"]:
        out.append((s["a"].replace("_leg", "_arm"), s["a_edge"], s["a_range"], s["b"].replace("_leg", "_arm"),
                    s["b_edge"], s["b_range"], False))
    return out


def _from_checker(raw, regions):
    """Undo a flattened checkerboard: map = 128 * observed / predicted checker, sampled at the fitted scale."""
    from PIL import ImageFilter
    c = CHECKER
    src = raw.convert("L")
    sp = src.load()
    half = c["period"] / 2
    # ratio map at source resolution, then a median filter removes the thin lines left at square edges
    # (JPEG blur + sub-pixel phase error), then it is resampled onto the template
    ratio = Image.new("L", src.size, 128)
    rp = ratio.load()
    for Y in range(src.height):
        for X in range(src.width):
            bg = c["white"] if (int(X // half) + int(Y // half)) % 2 == 0 else c["grey"]   # squares measured at 17.6 px
            r = sp[X, Y] / bg
            rp[X, Y] = max(0, min(255, round(128 * r if r <= 1 else 128 + (r - 1) * 1270)))
    ratio = ratio.filter(ImageFilter.MedianFilter(5))
    rp = ratio.load()
    out = Image.new("L", (585, 559), 128)
    op = out.load()
    missing = []
    for name, p in regions["garments"]["shirt"]["panels"].items():
        X1 = (p["x"] + p["w"]) * c["sx"] + c["ox"]
        Y1 = (p["y"] + p["h"]) * c["sy"] + c["oy"]
        X0, Y0 = p["x"] * c["sx"] + c["ox"], p["y"] * c["sy"] + c["oy"]
        if X0 < 0 or Y0 < 0 or X1 > src.width - 1 or Y1 > src.height - 1:
            missing.append(name)                     # (partly) cropped out of the source: filled later
            continue
        for y in range(p["y"], p["y"] + p["h"]):
            for x in range(p["x"], p["x"] + p["w"]):
                op[x, y] = rp[int(x * c["sx"] + c["ox"]), int(y * c["sy"] + c["oy"])]
    return out, missing


def _fill_missing(m, regions, missing):
    """Faces cropped out of the source: fill with the layer's mean (form only, no folds)."""
    vals = list(m.get_flattened_data())
    mean = round(sum(vals) / len(vals))
    d = ImageDraw.Draw(m)
    for name in missing:
        p = regions["garments"]["shirt"]["panels"][name]
        d.rectangle([p["x"], p["y"], p["x"] + p["w"] - 1, p["y"] + p["h"] - 1], fill=mean)
    return m


def import_owner(raw_dir):
    regions = load_regions()
    mask = panel_mask("shirt", regions)
    for name, (lid, style, strength, kind) in OWNER_LAYERS.items():
        f = Path(raw_dir) / name
        if not f.exists():
            print("missing", f)
            continue
        raw = Image.open(f)
        missing = []
        if kind == "checker":
            m, missing = _from_checker(raw, regions)
            from PIL import ImageFilter
            m = m.filter(ImageFilter.MedianFilter(3))          # removes the last checker flecks
            m = m.point(lambda v: min(v, 130))                  # residue reads as white scratches on dark cloth: shadows only
            m = _fill_missing(m, regions, missing)
        else:
            rgba = raw.convert("RGBA")
            if rgba.size != (585, 559):            # 2.png is 585 x 558: pad one transparent row at the bottom
                pad = Image.new("RGBA", (585, 559), (0, 0, 0, 0))
                pad.paste(rgba, (0, 0))
                rgba = pad
            m = to_map(rgba)
        m = Image.composite(m, Image.new("L", m.size, 128), mask)
        before = seam_report(m, regions)
        after = before
        for _ in range(20):                      # heal until seams hold on near-white fabric too (worst < 3 on grey)
            m = heal(m, regions, band=6, extra=_hip_pairs(regions))
            after = seam_report(m, regions)
            if after["failing_pairs"] == 0 and after["worst_mean"] < 3:
                break
        m.save(CUSTOM / f"{lid}.png")
        if kind == "checker":
            notes = (f"rescaled from {raw.size[0]}x{raw.size[1]}; checkerboard divided out; faces missing in the source "
                     f"filled flat: {', '.join(missing) or 'none'}")
        else:
            notes = f"{raw.size[0]}x{raw.size[1]} transparent overlay, alpha folded into the map"
        meta = dict(OWNER, id=lid, file=f"{lid}.png", raw_name=name, garment="shirt + pants", style=style,
                    strength=strength, parts=["torso", "arms", "legs"], seams_before=before, seams_after=after, notes=notes)
        (CUSTOM / f"{lid}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(f"{lid}: seams before {before} -> after heal {after}; missing faces: {missing or 'none'}")


DEFAULT_LAYER = "own-shade-all"     # applied to every outfit in every family unless the spec says `shading: {layer: none}`
STACK = {"own-shade-1": 1.0, "own-shade-2": 1.0, "own-shade-3": 0.8}
STACK_GAIN = 0.7


def compose_all():
    """Stack the three owner templates into one map: 128 + gain * sum(weight * (layer - 128)).
    Each input is already seam-healed, and a weighted sum of healed maps stays healed."""
    regions = load_regions()
    maps = {lid: load_layer(lid) for lid in STACK}
    data = {lid: list(m.get_flattened_data()) for lid, (m, _) in maps.items()}
    n = len(next(iter(data.values())))
    vals = [max(0, min(255, round(128 + STACK_GAIN * sum(w * (data[lid][i] - 128) for lid, w in STACK.items()))))
            for i in range(n)]
    m = Image.new("L", (585, 559))
    m.putdata(vals)
    rep = seam_report(m, regions)
    meta = dict(OWNER, id=DEFAULT_LAYER, file=f"{DEFAULT_LAYER}.png", raw_name="1.png + 2.png + 3.jpg",
                garment="shirt + pants", style="all three owner templates stacked", strength=1.0,
                parts=["torso", "arms", "legs"], seams_before=rep, seams_after=rep,
                notes=f"stack of {', '.join(f'{k} x{w}' for k, w in STACK.items())}, gain {STACK_GAIN}")
    m.save(CUSTOM / f"{DEFAULT_LAYER}.png")
    (CUSTOM / f"{DEFAULT_LAYER}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"{DEFAULT_LAYER}: seams {rep}")


def effective_layer(spec):
    """The layer an outfit is shaded with: its own `shading.layer`, else the default stack; `none` = no layer."""
    sh = spec.get("shading") or {}
    lid = sh.get("layer", DEFAULT_LAYER)
    return None if lid in (None, "", "none") else lid


def sheet():
    regions = load_regions()
    try:
        f = ImageFont.truetype("arialbd.ttf", 14)
        fs = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        f = fs = ImageFont.load_default()
    items = layers()
    tw, th = 292, 280
    cols = 3
    skipped = json.loads(SKIPPED.read_text(encoding="utf-8")) if SKIPPED.exists() else []
    rows = (len(items) + cols - 1) // cols
    text_h = 22 + 16 * len(skipped)
    img = Image.new("RGB", (cols * (tw + 10) + 10, 40 + rows * (th + 44) + text_h + 40), "white")
    d = ImageDraw.Draw(img)
    d.text((10, 10), f"COLLECTED shading layers ({len(items)}): applied to mid grey, after seam-heal", fill=(0, 0, 0), font=f)
    for i, (lid, meta) in enumerate(items.items()):
        m, _ = load_layer(lid)
        base = Image.new("RGBA", m.size, (150, 150, 150, 255))
        from clothing import apply_shading
        shaded = apply_shading(base, m.point(lambda v: max(0, min(255, round(128 + (v - 128) * 1.6)))), 1.0)
        x, y = 10 + (i % cols) * (tw + 10), 40 + (i // cols) * (th + 44)
        img.paste(shaded.convert("RGB").resize((tw, th)), (x, y))
        d.text((x, y + th + 2), f"{lid}  ({meta['garment']}, {meta['style']})", fill=(0, 0, 0), font=fs)
        d.text((x, y + th + 18), f"seams worst {meta['seams_before']['worst_mean']} -> {meta['seams_after']['worst_mean']}, "
                                 f"failing pairs {meta['seams_before']['failing_pairs']} -> {meta['seams_after']['failing_pairs']}",
               fill=(60, 60, 60), font=fs)
    y = 40 + rows * (th + 44) + 10
    d.text((10, y), f"SKIPPED ({len(skipped)})", fill=(150, 0, 0), font=f)
    for j, s in enumerate(skipped):
        d.text((10, y + 22 + 16 * j), f"- {s['item']}: {s['reason']}"[:190], fill=(60, 0, 0), font=fs)
    out = ROOT / "styles" / "references" / "shading-contact-sheet.png"
    img.save(out)
    print("wrote", out)


if __name__ == "__main__":
    if sys.argv[1] == "import":
        import_layers(sys.argv[2])
    elif sys.argv[1] == "import-owner":
        import_owner(sys.argv[2])
        compose_all()
    elif sys.argv[1] == "compose":
        compose_all()
    else:
        sheet()

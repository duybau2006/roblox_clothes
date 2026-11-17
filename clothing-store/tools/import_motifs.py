"""Import the owner's generated motif sheets (styles/references/inbox/sheet-NN.png) into the element library.

    python tools/import_motifs.py detect      boxes per sheet -> inbox/work/sheet-NN.json + inbox/contact/sheet-NN.png
    python tools/import_motifs.py build       cut, classify, hold, tile, scale-test and register (needs inbox/classify.yaml)

The sheets arrive already background-removed (colour-to-alpha): element pixels have alpha ~224-254 and the
leftover halo / background stays below ~120. Detection thresholds alpha at 200; cut-outs ramp alpha from
120 (clear) to 220 (solid), which drops the halo and keeps soft edges.
"""
import json
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clothing import ROOT   # noqa: E402

REF = ROOT / "styles" / "references"
INBOX = REF / "inbox"
WORK = INBOX / "work"
CONTACT = INBOX / "contact"
DETECT_ALPHA = 200
CELL = 3            # detection grid: 3x3 px cells
GAP = 2             # cells of dilation: parts closer than ~6 px join one element
MIN_SIDE = 22       # px: smaller blobs are crumbs (sparkle dust, halo specks), listed but not imported
MARGIN = 6


def font(px):
    for n in ("arialbd.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(n, px)
        except OSError:
            pass
    return ImageFont.load_default()


def detect_boxes(img):
    a = img.getchannel("A").point(lambda v: 255 if v >= DETECT_ALPHA else 0)
    a = a.filter(ImageFilter.MaxFilter(3))
    gw, gh = img.width // CELL, img.height // CELL
    g = a.resize((gw, gh), Image.BOX).point(lambda v: 255 if v > 20 else 0)
    for _ in range(GAP):
        g = g.filter(ImageFilter.MaxFilter(3))
    px = g.load()
    seen = [[False] * gw for _ in range(gh)]
    boxes = []
    for y in range(gh):
        for x in range(gw):
            if px[x, y] and not seen[y][x]:
                q = deque([(x, y)]); seen[y][x] = True
                x0 = x1 = x; y0 = y1 = y; n = 0
                while q:
                    cx, cy = q.popleft(); n += 1
                    x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < gw and 0 <= ny < gh and px[nx, ny] and not seen[ny][nx]:
                            seen[ny][nx] = True; q.append((nx, ny))
                boxes.append([x0 * CELL, y0 * CELL, (x1 + 1) * CELL, (y1 + 1) * CELL, n])
    big = [b[:4] for b in boxes if max(b[2] - b[0], b[3] - b[1]) >= MIN_SIDE]
    crumbs = len(boxes) - len(big)
    big.sort(key=lambda b: (round((b[1] + b[3]) / 2 / 90), b[0]))     # reading order: rows of ~90 px, then left to right
    return big, crumbs


def contact_sheet(img, boxes, title, path, held=None):
    bg = Image.new("RGBA", img.size, (236, 236, 236, 255))
    d0 = ImageDraw.Draw(bg)
    for y in range(0, img.height, 24):                    # light checker so transparency is visible
        for x in range(0, img.width, 24):
            if (x // 24 + y // 24) % 2:
                d0.rectangle([x, y, x + 23, y + 23], fill=(222, 222, 222, 255))
    bg.alpha_composite(img)
    out = Image.new("RGB", (img.width, img.height + 40), "white")
    out.paste(bg.convert("RGB"), (0, 40))
    d = ImageDraw.Draw(out)
    d.text((8, 8), title, fill=(0, 0, 0), font=font(22))
    f = font(18)
    for i, b in enumerate(boxes, 1):
        col = (200, 0, 0) if not held or i not in held else (120, 0, 160)
        d.rectangle([b[0], b[1] + 40, b[2], b[3] + 40], outline=col, width=2)
        d.rectangle([b[0], b[1] + 40, b[0] + 30, b[1] + 62], fill=col)
        d.text((b[0] + 3, b[1] + 41), str(i), fill=(255, 255, 255), font=f)
    out.save(path)


def detect():
    WORK.mkdir(parents=True, exist_ok=True); CONTACT.mkdir(parents=True, exist_ok=True)
    for p in sorted(INBOX.glob("sheet-*.png")):
        img = Image.open(p).convert("RGBA")
        boxes, crumbs = detect_boxes(img)
        manual = WORK / f"{p.stem}-manual.json"          # hand-set boxes replace / extend detection
        if manual.exists():
            m = json.loads(manual.read_text(encoding="utf-8"))
            boxes = [b for i, b in enumerate(boxes, 1) if i not in set(m.get("drop", []))] + m.get("add", [])
            boxes.sort(key=lambda b: (round((b[1] + b[3]) / 2 / 90), b[0]))
        (WORK / f"{p.stem}.json").write_text(json.dumps({"boxes": boxes, "crumbs": crumbs}), encoding="utf-8")
        contact_sheet(img, boxes, f"{p.stem}: {len(boxes)} elements detected ({crumbs} crumbs ignored)",
                      CONTACT / f"{p.stem}.png")
        print(p.stem, len(boxes), "elements,", crumbs, "crumbs")


# ---------------------------------------------------------------- build

LIB = REF / "library"
OWN = LIB / "owner"
HELD = REF / "held"
STYLES = {"gz": "gen-z", "y2k": "y2k", "vg": "vamp-goth", "emo": "emo", "bad": "baddie", "gr": "grunge",
          "xm": "christmas", "sg": "soft-girl", "prep": "preppy", "ath": "athleisure", "cc": "cottagecore",
          "arc": "archive"}
FAMS = {"d": "decorated", "p": "print", "r": "realistic"}
TARGET = {"hero": 100, "motif": 24, "border": 128, "swatch": 64, "part": 64, "texture": 96}
LICENCE = {"licence": "the store owner's own artwork, generated with ChatGPT; owner holds the rights",
           "generated": "2026-11-16"}
RAMP_LO, RAMP_HI = 120, 220


def _components(mask, box):
    """Keep only the connected pieces of `mask` (L, crop) whose centre lies inside `box` (crop coords)."""
    half = mask.resize((max(1, mask.width // 2), max(1, mask.height // 2)), Image.BOX).point(lambda v: 255 if v > 60 else 0)
    w, h = half.size
    px = half.load()
    seen = bytearray(w * h)
    keep = Image.new("L", (w, h), 0)
    kp = keep.load()
    bx0, by0, bx1, by1 = (v / 2 for v in box)
    for y in range(h):
        for x in range(w):
            if px[x, y] and not seen[y * w + x]:
                comp = []
                q = deque([(x, y)]); seen[y * w + x] = 1
                while q:
                    cx, cy = q.popleft(); comp.append((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and px[nx, ny] and not seen[ny * w + nx]:
                            seen[ny * w + nx] = 1; q.append((nx, ny))
                mx = sum(c[0] for c in comp) / len(comp); my = sum(c[1] for c in comp) / len(comp)
                cx0 = min(c[0] for c in comp); cx1 = max(c[0] for c in comp) + 1
                cy0 = min(c[1] for c in comp); cy1 = max(c[1] for c in comp) + 1
                ix = max(0, min(cx1, bx1) - max(cx0, bx0)); iy = max(0, min(cy1, by1) - max(cy0, by0))
                inside = ix * iy / max(1, (cx1 - cx0) * (cy1 - cy0))          # share of the piece's own box inside
                if bx0 <= mx <= bx1 and by0 <= my <= by1 and inside >= 0.8:
                    for cx, cy in comp:
                        kp[cx, cy] = 255
    return keep.resize(mask.size, Image.NEAREST).filter(ImageFilter.MaxFilter(5))


def cut(img, box):
    x0, y0, x1, y1 = box
    ex = 30
    X0, Y0 = max(0, x0 - ex), max(0, y0 - ex)
    X1, Y1 = min(img.width, x1 + ex), min(img.height, y1 + ex)
    crop = img.crop((X0, Y0, X1, Y1))
    a = crop.getchannel("A")
    keep = _components(a.point(lambda v: 255 if v >= DETECT_ALPHA else 0), (x0 - X0, y0 - Y0, x1 - X0, y1 - Y0))
    ramp = a.point(lambda v: max(0, min(255, round((v - RAMP_LO) * 255 / (RAMP_HI - RAMP_LO)))))
    from PIL import ImageChops
    alpha = ImageChops.multiply(ramp, keep.filter(ImageFilter.GaussianBlur(1)))
    crop.putalpha(alpha)
    bb = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
    if not bb:
        return None
    bb = (max(0, bb[0] - MARGIN), max(0, bb[1] - MARGIN), min(crop.width, bb[2] + MARGIN), min(crop.height, bb[3] + MARGIN))
    return crop.crop(bb)


def lum(rgba):
    return rgba.convert("RGB").convert("L")


def quantiles(rgba):
    l, a = lum(rgba).get_flattened_data(), rgba.getchannel("A").get_flattened_data()
    vals = sorted(v for v, al in zip(l, a) if al >= 128)
    if not vals:
        return 85, 170
    return vals[len(vals) // 3], vals[2 * len(vals) // 3]


def tone_mask(rgba):
    """3-tone renderer mask: 255 main ink (mid tones), 170 shadow tone (darkest third), 85 highlight (brightest)."""
    q1, q2 = quantiles(rgba)
    l = lum(rgba).load(); a = rgba.getchannel("A").load()
    m = Image.new("L", rgba.size, 0); mp = m.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            if a[x, y] >= 128:
                v = l[x, y]
                mp[x, y] = 170 if v < q1 else (85 if v > q2 else 255)
    return m


def ink_grey(rgba):
    """Continuous greyscale ink version (luminance + alpha) for reference / custom recolouring."""
    out = Image.merge("LA", (lum(rgba), rgba.getchannel("A")))
    return out


def survival(alpha, tw):
    """How much of the solid area survives at target width tw (thin lines fade below alpha 128)."""
    th = max(1, round(alpha.height * tw / alpha.width))
    full = sum(1 for v in alpha.get_flattened_data() if v >= 128) / (alpha.width * alpha.height)
    small = alpha.resize((tw, th), Image.LANCZOS)
    sm = sum(1 for v in small.get_flattened_data() if v >= 128) / (tw * th)
    return sm / full if full else 0.0


def noise(mask, alpha, tw):
    """Fraction of opaque target pixels that disagree with their 3x3 median: speckle = engraving turned to mud."""
    th = max(1, round(mask.height * tw / mask.width))
    tone = mask.point(lambda v: {255: 150, 170: 60, 85: 230}.get(v, 0)).resize((tw, th), Image.LANCZOS)
    al = alpha.resize((tw, th), Image.LANCZOS)
    med = tone.filter(ImageFilter.MedianFilter(3))
    t, m, a = tone.load(), med.load(), al.load()
    n = bad = 0
    for y in range(th):
        for x in range(tw):
            if a[x, y] >= 128:
                n += 1
                bad += abs(t[x, y] - m[x, y]) > 45
    return bad / n if n else 1.0


def stroke(alpha, tw):
    """Average stroke width at target width tw: 2 * area / perimeter of the solid shape, scaled. Readable >= 1 px."""
    b = alpha.point(lambda v: 255 if v >= 128 else 0)
    from PIL import ImageChops
    edge = ImageChops.subtract(b, b.filter(ImageFilter.MinFilter(3)))
    area = sum(1 for v in b.get_flattened_data() if v)
    per = sum(1 for v in edge.get_flattened_data() if v)
    return (2 * area / max(1, per)) * tw / alpha.width


def fill(alpha, tw):
    """Opaque share of the element's box at target width: line art that thins to a few specks scores low."""
    th = max(1, round(alpha.height * tw / alpha.width))
    small = alpha.resize((tw, th), Image.LANCZOS)
    return sum(1 for v in small.get_flattened_data() if v >= 128) / (tw * th)


def bold_version(rgba, tw):
    """Simplified bold mask for small use: smoothed silhouette (main ink) + merged dark masses (shadow tone)."""
    k = rgba.width / tw
    r = max(1.0, k * 0.8)
    a = rgba.getchannel("A")
    sil = a.point(lambda v: 255 if v >= 128 else 0).filter(ImageFilter.GaussianBlur(r)).point(lambda v: 255 if v >= 90 else 0)
    q1, _ = quantiles(rgba)
    dark = lum(rgba).point(lambda v: 255 if v < q1 else 0)
    from PIL import ImageChops
    dark = ImageChops.multiply(dark, sil).filter(ImageFilter.GaussianBlur(r * 1.3)).point(lambda v: 255 if v >= 128 else 0)
    m = Image.new("L", rgba.size, 0)
    m.paste(255, (0, 0), sil)
    m.paste(170, (0, 0), dark)
    return m, sil


def seamless(img, axes):
    """Offset-and-blend tile: edges come from the rolled image, so the tile wraps without a seam."""
    from PIL import ImageChops
    w, h = img.size
    rolled = ImageChops.offset(img, w // 2 if "x" in axes else 0, h // 2 if "y" in axes else 0)
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            dx = min(x, w - 1 - x) / (w / 2) if "x" in axes else 1.0
            dy = min(y, h - 1 - y) / (h / 2) if "y" in axes else 1.0
            mp[x, y] = round(255 * min(1.0, min(dx, dy) * 2.2))
    return Image.composite(img, rolled, mask)


def make_tile(rgba, kind):
    if kind == "swatch":                       # inner fabric only (no torn edges), tiled both ways
        a = rgba.getchannel("A").point(lambda v: 255 if v >= 220 else 0)
        bb = a.getbbox() or (0, 0, rgba.width, rgba.height)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        inner = rgba.crop((bb[0] + int(w * .14), bb[1] + int(h * .14), bb[2] - int(w * .14), bb[3] - int(h * .14)))
        inner = inner.resize((128, 128), Image.LANCZOS)
        inner.putalpha(255)
        return seamless(inner, "xy")
    h = 32                                     # border: 32 px tall strip, tiles horizontally
    w = max(64, round(rgba.width * h / rgba.height))
    w = 128 if w < 192 else 256
    strip = rgba.resize((w, h), Image.LANCZOS)
    return seamless(strip, "x")


def dominant(rgba, n=3):
    a = rgba.getchannel("A").point(lambda v: 255 if v >= 200 else 0)
    flat = Image.new("RGB", rgba.size, (0, 0, 0))
    flat.paste(rgba.convert("RGB"), (0, 0), a)
    q = flat.quantize(colors=n + 1, method=Image.MEDIANCUT)
    pal = q.getpalette()[: (n + 1) * 3]
    counts = sorted(((c, i) for c, i in q.getcolors()), reverse=True)
    out = []
    for c, i in counts:
        rgb = tuple(pal[i * 3: i * 3 + 3])
        if rgb == (0, 0, 0) and c > 0 and len(out) < n and sum(1 for v in a.get_flattened_data() if v == 0) > 0:
            continue
        out.append("#%02X%02X%02X" % rgb)
    return out[:n]


def build():
    import yaml
    cfg = yaml.safe_load((INBOX / "classify.yaml").read_text(encoding="utf-8"))
    reasons = cfg["reasons"]
    overrides = cfg.get("overrides") or {}
    OWN.mkdir(parents=True, exist_ok=True); HELD.mkdir(parents=True, exist_ok=True)
    for old in OWN.glob("*.png"):
        old.unlink()
    for old in LIB.glob("g[01][0-9]-*.json"):
        old.unlink()
    for old in HELD.glob("*.png"):
        old.unlink()
    report, held_rows, scale_rows = {}, [], []
    for sheet, entries in cfg["sheets"].items():
        img = Image.open(INBOX / f"{sheet}.png").convert("RGBA")
        rep = report.setdefault(sheet, {"imported": 0, "simplified": 0, "print_only": 0, "dropped": 0, "held": 0,
                                        "dropped_ids": [], "print_only_ids": [], "simplified_ids": []})
        boxes, held_idx = [], set()
        for n, e in enumerate(entries, 1):
            box, eid = e[:4], e[4]
            boxes.append(box)
            el = cut(img, box)
            if e[5] == "HOLD":
                held_idx.add(n)
                rep["held"] += 1
                if el is None or el.width * el.height < 0.25 * (box[2] - box[0]) * (box[3] - box[1]):
                    el = img.crop(tuple(box))                    # piece runs past its box: show the raw box for review
                if el:
                    el.save(HELD / f"{sheet}-{n:02d}-{eid}.png")
                held_rows.append((sheet, n, eid, reasons[e[6]], el))
                continue
            motif, styles, kind, place, fams, moods = e[5:11]
            if el is None:
                rep["dropped"] += 1; rep["dropped_ids"].append(eid)
                continue
            tw = TARGET[kind]
            mask = tone_mask(el)
            alpha = el.getchannel("A")
            surv, nz = survival(alpha, tw), noise(mask, alpha, tw)
            status, bold = "ok", None
            if kind in ("hero", "motif", "border", "part") and (surv < 0.6 or nz > 0.18):
                bmask, bsil = bold_version(el, tw)
                bsurv = survival(bsil, tw)
                if stroke(alpha, tw) >= 1.0 and surv >= 0.45:            # thin but clean line art (sparkles, outlines)
                    status, bold = "simplified", bmask
                elif bsurv >= 0.6 and stroke(bsil, tw) >= 1.0:
                    status, bold = "simplified", bmask
                elif kind in ("motif", "border", "part") and stroke(alpha, 100) >= 1.0:
                    status = "print-size only"
                elif kind == "hero" and survival(bsil, 160) >= 0.6:
                    status, bold = "print-size only", bmask
                else:
                    status = "dropped"
            if eid in overrides:                                 # judged by eye on the scale-test sheets
                status = overrides[eid]
                if status != "ok" and bold is None and status != "dropped":
                    bold = bold_version(el, tw)[0]
            if status == "dropped":
                rep["dropped"] += 1; rep["dropped_ids"].append(eid)
                scale_rows.append((sheet, eid, el, mask, None, tw, status))
                continue
            el.save(OWN / f"{eid}-colour.png")
            mask.save(OWN / f"{eid}.png")
            ink_grey(el).save(OWN / f"{eid}-ink.png")
            fam_list = [FAMS[f] for f in fams.split()]
            if status == "print-size only":
                fam_list = ["print"]
                rep["print_only"] += 1; rep["print_only_ids"].append(eid)
            meta = {"id": eid, "name": eid[4:].replace("-", " ").capitalize(), "motif": motif,
                    "styles": [STYLES[s] for s in styles.split()], "mood": moods.split(),
                    "size": {"motif": "small", "border": "small", "part": "medium", "swatch": "small",
                             "texture": "large", "hero": "large"}[kind] if status == "ok" else
                            ("medium" if status == "simplified" else "large"),
                    "families": fam_list, "symmetric": False, "band": kind == "border", "kind": kind,
                    "placement": place, "readability": status, "source": "owner-generated",
                    "mask": f"owner/{eid}.png", "colour": f"owner/{eid}-colour.png", "ink": f"owner/{eid}-ink.png",
                    "colours": dominant(el), "sheet": sheet, "box": box,
                    "license": dict(LICENCE, source_url=f"styles/references/inbox/{sheet}.png")}
            if bold is not None:
                bold.save(OWN / f"{eid}-bold.png")
                meta["bold"] = f"owner/{eid}-bold.png"
                meta["bold_below"] = 2 * tw if kind not in ("hero", "texture") else 70   # px wide: below this the bold version is drawn
                if status == "simplified":
                    rep["simplified"] += 1; rep["simplified_ids"].append(eid)
            if kind in ("swatch", "border"):
                tile = make_tile(el, kind)
                tile.save(OWN / f"{eid}-tile.png")
                tone_mask(tile).save(OWN / f"{eid}-tile-mask.png")
                meta["tile"] = f"owner/{eid}-tile.png"
                meta["tile_mask"] = f"owner/{eid}-tile-mask.png"
            (LIB / f"{eid}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
            rep["imported"] += 1
            scale_rows.append((sheet, eid, el, mask, bold, tw, status))
        contact_sheet(img, boxes, f"{sheet}: {len(boxes)} elements, {len(held_idx)} held (purple), rest imported (red)",
                      CONTACT / f"{sheet}.png", held_idx)
    held_sheet(held_rows)
    scale_sheets(scale_rows)
    (INBOX / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    for s, r in report.items():
        print(s, {k: v for k, v in r.items() if not k.endswith("_ids")})


def held_sheet(rows):
    lines = ["# Held elements (not imported)", "",
             "Cut from the owner's generated sheets but held back from the library. Kept here only so the owner can review them.", "",
             "| sheet | # | element | reason |", "|---|---|---|---|"]
    lines += [f"| {s} | {n} | `{eid}` | {why} |" for s, n, eid, why, _ in rows]
    (HELD / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    cols, tw, th = 6, 200, 200
    out = Image.new("RGB", (cols * (tw + 10) + 10, ((len(rows) + cols - 1) // cols) * (th + 50) + 50), "white")
    d = ImageDraw.Draw(out)
    d.text((10, 10), f"HELD: {len(rows)} elements (not imported)", fill=(120, 0, 120), font=font(22))
    f = font(13)
    for i, (s, n, eid, why, el) in enumerate(rows):
        x, y = 10 + (i % cols) * (tw + 10), 45 + (i // cols) * (th + 50)
        tile = Image.new("RGBA", (tw, th), (236, 236, 236, 255))
        if el:
            t = el.copy(); t.thumbnail((tw, th))
            tile.alpha_composite(t, ((tw - t.width) // 2, (th - t.height) // 2))
        out.paste(tile.convert("RGB"), (x, y))
        d.text((x, y + th + 2), f"{s} #{n} {eid}"[:32], fill=(0, 0, 0), font=f)
        d.text((x, y + th + 18), why[:34], fill=(120, 0, 120), font=f)
    out.save(HELD / "held-contact.png")


def scale_sheets(rows):
    """Per sheet: each element at its real size (and its bold version), on light and dark fabric."""
    by = {}
    for r in rows:
        by.setdefault(r[0], []).append(r)
    for sheet, items in by.items():
        cw, ch = 300, 150
        cols = 4
        out = Image.new("RGB", (cols * cw, ((len(items) + cols - 1) // cols) * ch + 40), "white")
        d = ImageDraw.Draw(out)
        d.text((8, 8), f"{sheet}: scale test at real use size (left: original colour, middle: ink mask in one ink, right: bold)",
               fill=(0, 0, 0), font=font(16))
        f = font(12)
        for i, (_, eid, el, mask, bold, tw, status) in enumerate(items):
            x, y = (i % cols) * cw, 40 + (i // cols) * ch
            bg = Image.new("RGBA", (cw - 6, ch - 26), (196, 190, 184, 255))
            def put(im, ox):
                t = im.copy()
                if t.width > tw:
                    t = t.resize((tw, max(1, round(t.height * tw / t.width))), Image.LANCZOS)
                if t.height > ch - 30:
                    t = t.resize((max(1, round(t.width * (ch - 30) / t.height)), ch - 30), Image.LANCZOS)
                bg.alpha_composite(t, (ox, max(0, (ch - 26 - t.height) // 2)))
                return t.width
            w1 = put(el, 4)
            ink = Image.new("RGBA", mask.size, (40, 30, 50, 0))
            ink.putalpha(mask.point(lambda v: 255 if v else 0))
            tone = mask.point(lambda v: {255: 70, 170: 25, 85: 150}.get(v, 0))
            ink = Image.merge("RGBA", (tone, tone, tone.point(lambda v: min(255, v + 20)), mask.point(lambda v: 255 if v else 0)))
            w2 = put(ink, min(cw - 20, 10 + w1))
            if bold is not None:
                bt = bold.point(lambda v: {255: 70, 170: 20}.get(v, 0))
                put(Image.merge("RGBA", (bt, bt, bt, bold.point(lambda v: 255 if v else 0))), min(cw - 20, 20 + w1 + w2))
            out.paste(bg.convert("RGB"), (x + 3, y))
            col = {"ok": (0, 110, 0), "simplified": (0, 70, 160), "print-size only": (170, 90, 0), "dropped": (200, 0, 0)}[status]
            d.text((x + 4, y + ch - 24), f"{eid} [{tw}px] {status}"[:44], fill=col, font=f)
        out.save(CONTACT / f"{sheet}-scale.png")


if __name__ == "__main__":
    {"detect": detect, "build": build}[sys.argv[1]]()

"""Validate rendered outfits. Prints a pass/fail report per outfit; exit code 1 if any fail.

Usage:
    python tools/validate.py specs/<id>.yaml [more specs ...] [--renders DIR]   (default DIR: renders/)
    python tools/validate.py --all            (every outfit spec in specs/, skipping _template)

Outfit checks
  files       both <id>-shirt.png and <id>-pants.png exist
  torso       the six torso panels are pixel-identical in the two files
  shoulder    shirt file: torso edges meet the arm edges (top 32 rows + top faces) within tolerance;
              skipped when arms.sleeve_contrast is true
  hip         pants file: torso bottom edges meet the leg top edges within tolerance
  listings    names = listings.words (colour + garment + up to 4 style words from the newest
              trends/*-catalog.md) + "Outfit Top" / "Outfit Pants"; <= 50 chars; no brand,
              character, game or platform names; no repeated words; each description names the other
  cut         hem 80-120, waist 88-110, crop gap <= 16 px, skirt length minimums, no skin-tone
              legwear / under-sleeves; transparent torso rows only inside the crop gap
  palette     every colour in the sections and decorations is in the outfit palette (max 4 + 1 neutral)
  decor       decorations use only library motifs / elements / prints, on layouts that exist
  family      `family` is decorated | print | combined and matches what the outfit contains
  library     every library element is original or CC0 with a LICENSES.md entry; no blocked subjects
  duplicate   design signature overlap < 80% and renders not near-identical vs every spec in specs/
Per-file checks (shirt and pants)
  size        exactly 585x559
  format      PNG with an alpha channel
  outside     no opaque pixel (alpha > 8) outside the panels + 2 px bleed
  guide       no leftover template panel-fill colours inside the panels (leftover background
              grey outside the panels is caught by "outside"; grey is a legitimate fabric colour)
  seams       all 36 seam pairs of that file agree in colour (+-1 px slack) and coverage
  shoes       pants only: shoe-coloured pixels stay in the bottom quarter of the leg side panels
"""
import argparse
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageChops

from clothing import ROOT, OUTFIT, load_regions, panel_mask, hex_rgb
import construction
import cuts
import identity
import library
import motifs
import realistic
import shading_custom
import shoes
import prints
import recipes

SEAM_MEAN_TOL = 10.0     # mean per-channel difference along a seam (0-255)
SEAM_P95_TOL = 28.0      # 95th percentile per-pixel difference along a seam
COVERAGE_TOL = 0.04      # share of seam pixels where one side is opaque and the other transparent
GUIDE_TOL = 4            # max channel distance to count a pixel as a guide colour
GUIDE_MAX_PIXELS = 12
SHOE_TOL = 70            # max channel distance to the nearest shoe colour (allows for shading)
SHOE_ROW_SHARE = 0.35    # a row counts as "shoe" when this share of its pixels match
NAME_MAX = 50
DUP_SIMILARITY = 0.8     # design-signature overlap that counts as a near-duplicate
DUP_PIXEL_MAE = 4.0      # mean torso difference (0-255) below which two renders count as the same design
TORSO_FACES = ("front", "back", "left", "right", "top", "bottom")


# ---------------------------------------------------------------- helpers

def edge_pixels(px, p, edge, rng=None):
    x, y, w, h = p["x"], p["y"], p["w"], p["h"]
    if edge == "top":
        out = [px[x + i, y] for i in range(w)]
    elif edge == "bottom":
        out = [px[x + i, y + h - 1] for i in range(w)]
    elif edge == "left":
        out = [px[x, y + i] for i in range(h)]
    else:
        out = [px[x + w - 1, y + i] for i in range(h)]
    return out[rng[0]:rng[1]] if rng else out


CUT_EDGES = False   # set per outfit: the spec has a strap / strapless / off-shoulder cut (bare shoulders by design)


def cut_edge_pair(name):
    """Seam pairs where a deliberate cut-out may leave one side transparent: torso top / side faces and shoulders."""
    return CUT_EDGES and ("torso.top" in name or "torso.left" in name or "torso.right" in name or "_arm" in name)


def compare_edges(a, b, name):
    """Return (failure string or None, mean difference)."""
    if len(a) != len(b):
        return f"{name}: edge lengths differ", 0.0
    diffs, cover_bad = [], 0
    for i, pa in enumerate(a):
        pb = b[i]
        oa, ob = pa[3] > 128, pb[3] > 128
        if oa != ob:
            cover_bad += 1
        elif oa:
            # +-1 px slack along the seam: an outline crossing the seam at an angle shifts by a
            # pixel between the two rows; a real colour or pattern break still fails.
            diffs.append(min(sum(abs(pa[c] - q[c]) for c in range(3)) / 3
                             for q in b[max(0, i - 1):i + 2] if q[3] > 128))
    if cover_bad / len(a) > COVERAGE_TOL and not cut_edge_pair(name):
        return f"{name}: one side transparent on {cover_bad}/{len(a)} px", 0.0
    if not diffs:
        return None, 0.0
    diffs.sort()
    mean = sum(diffs) / len(diffs)
    p95 = diffs[min(len(diffs) - 1, int(0.95 * len(diffs)))]
    if mean > SEAM_MEAN_TOL or p95 > SEAM_P95_TOL:
        return f"{name}: mean diff {mean:.1f}, p95 {p95:.1f}", mean
    return None, mean


def check_seam_list(img, panels, seams):
    px = img.load()
    fails, worst = [], 0.0
    for sm in seams:
        a = edge_pixels(px, panels[sm["a"]], sm["a_edge"], sm.get("a_range"))
        b = edge_pixels(px, panels[sm["b"]], sm["b_edge"], sm.get("b_range"))
        if sm["reversed"]:
            b = b[::-1]
        name = f"{sm['a']}.{sm['a_edge']}{sm.get('a_range', '')} <-> {sm['b']}.{sm['b_edge']}{sm.get('b_range', '')}"
        f, mean = compare_edges(a, b, name)
        worst = max(worst, mean)
        if f:
            fails.append(f)
    return fails, worst


def check_guide(img, guide_colours):
    targets = [c for c in (hex_rgb(h) for h in guide_colours) if max(c) - min(c) > 60]
    hits = {}
    for p in img.get_flattened_data():
        if p[3] < 128:
            continue
        for t in targets:
            if abs(p[0] - t[0]) <= GUIDE_TOL and abs(p[1] - t[1]) <= GUIDE_TOL and abs(p[2] - t[2]) <= GUIDE_TOL:
                hits[t] = hits.get(t, 0) + 1
    return {("#%02x%02x%02x" % k): n for k, n in hits.items() if n > GUIDE_MAX_PIXELS}


def dist(a, b):
    return max(abs(a[i] - b[i]) for i in range(3))


def is_shoe(p, shoe_cols, body_cols):
    """Nearest-colour test: the pixel is closer to a shoe colour than to any trouser colour."""
    if p[3] < 128:
        return False
    ds = min(dist(p, s) for s in shoe_cols)
    db = min((dist(p, b) for b in body_cols), default=999)
    return ds <= SHOE_TOL and ds < db


def check_shoes(img, g, legs):
    shoes = str(legs.get("shoes") or "").strip().lower()
    if shoes in ("", "none", "no", "barefoot"):
        return [], "no shoes in spec"
    shoe_cols = [hex_rgb(h) for h in (legs.get("shoe_palette") or ["#f2f2f2", "#d4d4d4"])]
    base = [hex_rgb(h) for h in (legs.get("palette") or [])[:2] + (legs.get("legwear_palette") or [])]
    # include shaded / highlighted versions so dark folds in the fabric are not mistaken for dark shoes
    body = [tuple(min(255, round(c * k)) for c in b) for b in base for k in (0.55, 0.7, 0.85, 1.0, 1.15)]
    # shoes the same colour as the main fabric or legwear (e.g. all-black looks) cannot be told apart
    # by colour: report what was found as a WARN to check in the previews instead of a false FAIL
    main = [hex_rgb(h) for h in (legs.get("palette") or [])[:1] + (legs.get("legwear_palette") or [])]
    clash = any(dist(b, s) < 40 for b in main for s in shoe_cols)
    note = "shoes share the trouser/legwear colour: shoe check unreliable, review by eye" if clash else ""
    px = img.load()
    fails = []
    for leg in ("right_leg", "left_leg"):
        for face in ("front", "left", "back", "right"):
            p = g["panels"][f"{leg}.{face}"]
            limit = p["h"] - p["h"] // 4
            for dy in range(limit):
                row = [px[p["x"] + i, p["y"] + dy] for i in range(p["w"])]
                if sum(is_shoe(c, shoe_cols, body) for c in row) / len(row) >= SHOE_ROW_SHARE:
                    fails.append(f"{leg}.{face}: shoe colour at row {dy} (must start at row {limit} or lower)")
                    break
    if clash and fails:
        return [], f"{note} (colour matches above the bottom quarter on {len(fails)} panels)"
    return fails, note


# ---------------------------------------------------------------- checks

class Report:
    def __init__(self):
        self.lines, self.ok, self.results = [], True, []

    def res(self, name, passed, msg="", warn=False):
        self.ok &= passed
        tag = "WARN" if (passed and warn) else ("PASS" if passed else "FAIL")
        self.results.append((name, tag))
        self.lines.append(f"  [{tag}] {name}" + (f": {msg}" if msg else ""))


def check_file(rep, path, garment, regions, legs=None):
    label = f"{garment}:"
    img = Image.open(path)
    rep.res(f"{label} size", img.size == tuple(regions["canvas"]), f"{img.size[0]}x{img.size[1]}")
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    rep.res(f"{label} format", img.format == "PNG" and has_alpha, f"{img.format} {img.mode}")
    if img.size != tuple(regions["canvas"]):
        return None
    img = img.convert("RGBA")
    g = regions["garments"][garment]
    allowed = panel_mask(garment, regions, grow=regions["bleed_px"])
    opaque = img.getchannel("A").point(lambda a: 255 if a > 8 else 0)
    n = sum(1 for v in ImageChops.subtract(opaque, allowed).get_flattened_data() if v)
    rep.res(f"{label} outside", n == 0, f"{n} opaque px outside panels+bleed" if n else "")
    hits = check_guide(img, regions["guide_colours"])
    rep.res(f"{label} guide", not hits, ", ".join(f"{k} x{v}" for k, v in hits.items()))
    fails, worst = check_seam_list(img, g["panels"], g["seams"])
    rep.res(f"{label} seams", not fails, ("; ".join(fails[:5]) + (" ..." if len(fails) > 5 else "")) if fails
            else f"{len(g['seams'])} pairs, worst mean diff {worst:.1f}")
    if garment == "pants" and legs is not None:
        fails, note = check_shoes(img, g, legs)
        rep.res(f"{label} shoes", not fails, "; ".join(fails) if fails else note, warn=bool(note))
    return img


COLOURS = set("""black white grey gray silver charcoal red crimson burgundy maroon wine pink rose blush
lilac lavender purple violet plum blue navy denim teal turquoise aqua cyan mint green sage olive khaki
forest emerald lime yellow mustard gold orange rust peach coral brown chocolate tan camel beige cream
ivory oatmeal stone taupe""".split())
COLOUR_MODIFIERS = set("light dark hot baby pastel heather washed neon deep pale bright".split())
GARMENTS = set("""hoodie zip tee shirt top sweater sweatshirt cardigan jacket bomber puffer vest polo blazer
flannel jersey tank cami blouse corset crop turtleneck henley overshirt coat fleece suit tuxedo uniform
dress skirt jeans jogger joggers cargo cargos trousers sweatpants leggings shorts overalls pajama pajamas
pj pjs set tracksuit""".split())
# brand, character, game and platform names (lower case; matched as whole words or phrases)
BANNED = {"supreme", "bape", "umbro", "champion", "nelk", "chrome hearts", "chromehearts", "true religion",
          "affliction", "aeropostale", "alpinestars", "mcdonalds", "nike", "adidas", "puma", "gucci", "prada",
          "louis vuitton", "lv", "balenciaga", "stussy", "carhartt", "north face", "patagonia", "converse",
          "vans", "jordan", "ugg", "uggs", "spiderman", "spider-man", "gojo", "hello kitty", "kitty", "sanrio",
          "kuromi", "my little pony", "barbie", "nba", "nfl", "fifa", "kobe", "deftones", "rockstar", "monster",
          "roblox", "da hood", "dahood", "dh", "evade", "bloxburg", "brookhaven", "adopt me", "grow a garden",
          "mm2", "pokemon", "naruto", "disney", "marvel", "minecraft", "fortnite", "free"}


def newest_trend_words():
    """Style vocabulary: the 'Most-used name words' section of the newest trends/*-catalog.md,
    plus any brand / character / game names listed in its brand paragraph (added to BANNED)."""
    files = sorted((ROOT / "trends").glob("*-catalog.md"))
    if not files:
        return set(), set(), None
    text = files[-1].read_text(encoding="utf-8")
    words, banned = set(), set()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## Most-used name words"):
            body = next((l for l in lines[i + 1:] if l.strip()), "")
            for entry in body.split(","):
                w = " ".join(t for t in entry.strip().rstrip(".").split() if not t.isdigit()).lower()
                if w:
                    words.add(w)
        if line.lower().startswith("brand, character, or game-name items") and "(" in line:
            inside = line[line.index("(") + 1:line.index(")")]
            banned.update(x.strip().strip('"').lower() for x in inside.split(",") if x.strip())
    return words, banned, files[-1].name


def check_listings(rep, spec):
    ls = spec.get("listings") or {}
    sh, pa, wd = ls.get("shirt") or {}, ls.get("pants") or {}, ls.get("words") or {}
    sn, pn = str(sh.get("name") or "").strip(), str(pa.get("name") or "").strip()
    colour, garment = str(wd.get("colour") or "").strip(), str(wd.get("garment") or "").strip()
    style = [str(s).strip() for s in (wd.get("style") or [])]
    vocab, banned_trend, source = newest_trend_words()
    problems = []
    outfit_words = " ".join(x for x in [colour, garment, *style] if x)
    if not colour or not garment:
        problems.append("listings.words needs colour and garment")
    coverage = str(spec.get("coverage", "full"))
    if coverage == "bottom_only":
        if pn.lower() != f"{outfit_words} Pants".lower():
            problems.append(f"separate pants name must be '{outfit_words} Pants'")
    elif coverage == "top_only":
        if sn.lower() != f"{outfit_words} Top".lower():
            problems.append(f"separate top name must be '{outfit_words} Top'")
    else:
        if sn.lower() != f"{outfit_words} Outfit Top".lower():
            problems.append(f"shirt name must be '{outfit_words} Outfit Top' (any capitalisation)")
        if pn.lower() != f"{outfit_words} Outfit Pants".lower():
            problems.append(f"pants name must be '{outfit_words} Outfit Pants' (any capitalisation)")
    cw = colour.lower().split()
    if cw and (not any(w in COLOURS for w in cw) or any(w not in COLOURS | COLOUR_MODIFIERS for w in cw)):
        problems.append(f"colour '{colour}' is not a plain colour word")
    if garment and not any(w in GARMENTS for w in garment.lower().split()):
        problems.append(f"garment '{garment}' has no garment word")
    if len(style) > 4:
        problems.append(f"{len(style)} style words (max 4)")
    for s in style:
        if s.lower() not in vocab:
            problems.append(f"style word '{s}' is not in {source or 'trends/'} name words")
    tokens = outfit_words.lower().split()
    repeats = sorted({t for t in tokens if tokens.count(t) > 1})
    if repeats:
        problems.append("repeated words: " + ", ".join(repeats))
    low = f" {outfit_words.lower()} "
    hits = sorted(b for b in BANNED | banned_trend if f" {b} " in low)
    if hits:
        problems.append("brand/character/game names: " + ", ".join(hits))
    for n in (sn, pn):
        if len(n) > NAME_MAX:
            problems.append(f"'{n}' is {len(n)} chars (max {NAME_MAX})")
    if coverage == "full":
        if not pn or pn not in str(sh.get("description") or ""):
            problems.append("shirt description must name the pants listing")
        if not sn or sn not in str(pa.get("description") or ""):
            problems.append("pants description must name the shirt listing")
    elif not str((pa if coverage == "bottom_only" else sh).get("description") or "").strip():
        problems.append("the separate listing needs a description")
    rep.res("listings", not problems, "; ".join(problems) if problems else f"'{sn}' / '{pn}'")


def skin_like(hexcol):
    """Rough skin-tone test (warm hue, mid saturation): used to block skin-look fabric."""
    import colorsys
    r, g, b = (x / 255 for x in hex_rgb(hexcol))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return 0.02 <= h <= 0.11 and 0.15 <= s <= 0.65 and v >= 0.35


def check_cut(rep, spec, shirt=None):
    """Hem, crop, waist and skirt rules from the spec, plus what the torso panels actually show."""
    t, a, l = spec.get("torso") or {}, spec.get("arms") or {}, spec.get("legs") or {}
    hem = float(t.get("hem_line", OUTFIT["hem_line"]))
    waist = float(l.get("waist_line", OUTFIT["waist_line"]))
    problems, warns = [], []
    if not OUTFIT["min_hem"] <= hem <= 120:
        problems.append(f"torso.hem_line {hem:g} outside {OUTFIT['min_hem']}-120")
    if not 88 <= waist <= 110:
        problems.append(f"legs.waist_line {waist:g} outside 88-110")
    gap = waist - hem
    if gap > OUTFIT["max_crop_gap"]:
        problems.append(f"crop gap {gap:g} px (max {OUTFIT['max_crop_gap']})")
    coverage = str(spec.get("coverage", "full"))
    cut = t.get("cut") or {}
    if cut:
        if cut.get("neckline", "crew") not in cuts.NECKLINES:
            problems.append(f"cut.neckline must be one of {cuts.NECKLINES}")
        if cut.get("style", "sleeved") not in cuts.STYLES:
            problems.append(f"cut.style must be one of {cuts.STYLES}")
        if float(cut.get("depth", 6)) > cuts.MAX_DEPTH:
            problems.append(f"neckline depth {cut.get('depth')} too deep (max {cuts.MAX_DEPTH})")
        if float(cut.get("width", 16)) > 30:
            problems.append("neckline width over 30")
        if float(cut.get("top", 10)) > cuts.MAX_TOP:
            problems.append(f"strapless / off-shoulder top edge below row {cuts.MAX_TOP}")
        if "strap_width" in cut and float(cut["strap_width"]) < 5:
            problems.append("straps narrower than 5 px")
        if "hood" in " ".join(str(d) for d in t.get("details") or []).lower() and cut.get("style", "sleeved") != "sleeved":
            problems.append("a hood cannot go with a strap or strapless cut")
    kind = str(l.get("type", "trousers")).lower()
    if kind == "shorts":
        length = float(l.get("shorts_length", 40))
        if length < OUTFIT["min_skirt"]:
            problems.append(f"shorts_length {length:g} too short (min {OUTFIT['min_skirt']})")
        for h in l.get("legwear_palette") or []:
            if skin_like(h):
                problems.append(f"legwear colour {h} reads as skin")
    if kind == "skirt":
        length = float(l.get("skirt_length", 40))
        wear = str(l.get("legwear", "tights")).lower()
        need = OUTFIT["min_skirt_tights"] if wear == "tights" else OUTFIT["min_skirt"]
        if length < need:
            problems.append(f"skirt_length {length:g} too short for legwear '{wear}' (min {need})")
        for h in l.get("legwear_palette") or []:
            if skin_like(h):
                problems.append(f"legwear colour {h} reads as skin")
    for h in ((a.get("under") or {}).get("palette") or []):
        if skin_like(h):
            problems.append(f"under-sleeve colour {h} reads as skin")
    for key in ("torso", "arms", "legs"):
        pal = (spec.get(key) or {}).get("palette") or []
        if pal and skin_like(pal[0]):
            warns.append(f"{key} body colour {pal[0]} is close to skin tones: check the previews")
    if shirt is not None:  # transparent rows on the torso front must sit inside the crop gap only
        regions = load_regions()
        p = regions["garments"]["shirt"]["panels"]["torso.front"]
        px = shirt.load()
        clear = [dy for dy in range(p["h"])
                 if sum(px[p["x"] + i, p["y"] + dy][3] < 128 for i in range(p["w"])) > p["w"] // 2]
        lo, hi = hem - 1, waist                                   # allowed transparent rows
        if coverage == "top_only":
            lo, hi = hem - 1, p["h"]
        elif coverage == "bottom_only":
            lo, hi = 0, waist
        top_open = {"strapless": cuts.MAX_TOP, "off_shoulder": cuts.MAX_TOP, "halter": 18}.get(cut.get("style"), 0)
        bad = [dy for dy in clear if not (lo <= dy <= hi) and dy >= top_open]
        if bad:
            problems.append(f"torso front transparent outside the crop gap at rows {bad[0]}-{bad[-1]}")
        if coverage == "full" and len([d for d in clear if d >= top_open]) > OUTFIT["max_crop_gap"]:
            problems.append(f"{len(clear)} transparent torso rows (max {OUTFIT['max_crop_gap']})")
        if coverage != "bottom_only":   # chest always covered: rows 24 to the hem (or 80) fully opaque across the front
            holes = [dy for dy in range(24, int(min(hem, 80))) if any(px[p["x"] + i, p["y"] + dy][3] < 200 for i in range(8, p["w"] - 8))]
            if holes:
                problems.append(f"chest not covered at torso rows {holes[0]}-{holes[-1]} (cut-outs must stay above row 24)")
    if coverage not in ("full", "top_only", "bottom_only"):
        problems.append("coverage must be full, top_only or bottom_only")
    msg = "; ".join(problems + warns) if (problems or warns) else (
        (f"{coverage}; " if coverage != "full" else "") + (f"cropped: {gap:g} px gap" if gap > 0 else "full-length top")
        + (f"; cut {cut.get('style', 'sleeved')}/{cut.get('neckline', 'crew')}" if cut else ""))
    rep.res("cut", not problems, msg, warn=bool(warns) and not problems)


def check_palette(rep, spec):
    outfit = [str(h).upper() for h in (spec.get("palette") or [])]
    used = set()
    for key in ("torso", "arms", "legs"):
        sec = spec.get(key) or {}
        for field in ("palette", "shoe_palette", "legwear_palette"):
            used.update(str(h).upper() for h in (sec.get(field) or []))
        used.update(str(h).upper() for h in ((sec.get("left") or {}).get("palette") or []))
        used.update(str(h).upper() for h in ((sec.get("under") or {}).get("palette") or []))
    used.update(str(h).upper() for h in motifs.decor_colours(spec))
    for key in ("torso", "arms", "legs"):           # swatch fabric drawn in its original colours counts too
        sec = spec.get(key) or {}
        pat = sec.get("pattern") or {}
        if sec.get("base_pattern") == "swatch" and pat.get("recolour") is False and pat.get("element") in library.load_library():
            used.update(str(h).upper() for h in library.element(pat["element"]).get("colours", []))
    ident = spec.get("identity") or {}
    for f in ("number_colour", "number_outline", "panel", "piping"):
        if ident.get(f):
            used.add(str(ident[f]).upper())
    for f in ("colour", "accent"):
        if (ident.get("emblem") or {}).get(f):
            used.add(str(ident["emblem"][f]).upper())
    for key in ("torso", "arms", "legs"):   # construction part colours (hardware defaults: zips, buckles, stitching)
        for prt in (spec.get(key) or {}).get("parts") or []:
            if isinstance(prt, dict):
                used.update(str(prt[f]).upper() for f in ("colour", "shirt") if prt.get(f))
    missing = sorted(used - set(outfit))
    problems = []
    if len(outfit) > 5:
        problems.append(f"outfit palette has {len(outfit)} colours (max 4 + 1 neutral)")
    if missing:
        problems.append("colours used but not in the outfit palette: " + ", ".join(missing))
    rep.res("palette", not problems, "; ".join(problems))


def check_decor(rep, spec):
    """Decorations must come from the library: legacy motifs (tools/motifs.py), library elements or prints."""
    lib = library.load_library()
    problems, n = [], 0
    for key in ("torso", "arms", "legs"):
        for d in (spec.get(key) or {}).get("decor") or []:
            n += 1
            if "print" in d:
                pr = d["print"]
                if key != "torso":
                    problems.append(f"{key}: prints go on the torso only")
                if pr.get("template") not in prints.TEMPLATES:
                    problems.append(f"print template '{pr.get('template')}' unknown")
                for e in pr.get("elements") or []:
                    if e not in lib:
                        problems.append(f"print element '{e}' is not in the library")
                if not pr.get("elements"):
                    problems.append("print has no elements")
                continue
            lay = str(d.get("layout", "")).lower()
            if "element" in d:
                if d["element"] not in lib:
                    problems.append(f"{key}: element '{d['element']}' is not in the library")
                elif lib[d["element"]].get("readability") == "print-size only" and lay != "border" and                         float(d.get("size", (motifs.LAYOUTS[key].get(lay) or (0, 0, 8))[2] if lay in motifs.LAYOUTS[key] else 8)) < 15:
                    problems.append(f"{key}: '{d['element']}' is print-size only (detail turns to mud below ~30 px); use it in a print or at size >= 15")
                if lay == "border" and not lib.get(d["element"], {}).get("tile"):
                    problems.append(f"{key}: '{d['element']}' has no border tile; layout border needs an owner border element")
            else:
                m = str(d.get("motif", "")).lower()
                if m not in motifs.MOTIFS and m not in motifs.SPECIAL:
                    problems.append(f"{key}: motif '{m}' is not in the motif library")
            if lay not in motifs.LAYOUTS[key]:
                problems.append(f"{key}: layout '{lay}' is not available on {key}")
    rep.res("decor", not problems, "; ".join(problems) if problems else f"{n} decorations")


def check_realistic(rep, spec):
    """Materials, garment kinds, construction parts, shoes and the shading layer (licence on file)."""
    problems, notes, warns = [], [], []
    for key, region in (("torso", "torso"), ("arms", "arms"), ("legs", "legs")):
        sec = spec.get(key) or {}
        if sec.get("material") and str(sec["material"]).lower() not in realistic.MATERIALS:
            problems.append(f"{key}: material '{sec['material']}' unknown ({', '.join(realistic.MATERIALS)})")
        for prt in sec.get("parts") or []:
            name = prt if isinstance(prt, str) else (prt or {}).get("name")
            if name not in construction.PARTS[region]:
                problems.append(f"{key}: part '{name}' not available")
    style = str((spec.get("legs") or {}).get("shoe_style", "basic")).lower()
    if style not in shoes.STYLES:
        problems.append(f"legs.shoe_style '{style}' unknown")
    sh = spec.get("shading") or {}
    if sh.get("mode") not in (None, "realistic", "shared"):
        problems.append("shading.mode must be realistic or shared")
    if not problems and not recipes.realistic_used(spec):
        rep.res("realistic", True, "not used")
        return
    rep.res("realistic", not problems, "; ".join(problems) if problems else "materials and parts ok")


def check_shading(rep, spec):
    """Every outfit is shaded with a layer (default: the owner's three templates stacked) unless `layer: none`;
    the layer must exist, be in LICENSES.md, and an unconfirmed licence is a WARN."""
    problems, notes, warns = [], [], []
    sh = spec.get("shading") or {}
    lid = shading_custom.effective_layer(spec)
    if lid:
        meta = shading_custom.layers().get(lid)
        lic = (ROOT / "styles" / "references" / "LICENSES.md")
        lic_text = lic.read_text(encoding="utf-8") if lic.exists() else ""
        if meta is None:
            problems.append(f"shading layer '{lid}' not in templates/shading/custom/")
        else:
            L = meta.get("license") or meta
            if not (L.get("source_url") and L.get("licence")):
                problems.append(f"shading layer '{lid}' has no source URL / licence")
            if f"`{lid}`" not in lic_text:
                problems.append(f"shading layer '{lid}' missing from LICENSES.md")
            if meta.get("licence_confirmed") is False:
                warns.append(f"shading layer '{lid}' is owner-supplied with no stated source or licence: "
                             f"confirm both in templates/shading/custom/{lid}.json before uploading")
        st = float(sh.get("strength", 1.0))
        if not 0.15 <= st <= 1.0:
            problems.append(f"shading.strength {st:g} outside 0.15-1.0")
        notes.append(f"layer {lid}" + (" (default)" if "layer" not in sh else ""))
    else:
        notes.append("no layer (shading.layer: none): shared shading only")
    rep.res("shading", not problems, "; ".join(problems + warns) if (problems or warns) else ", ".join(notes),
            warn=bool(warns) and not problems)


def check_identity(rep, spec):
    """Numbers are digits 0-99 only; emblems are library elements in an invented frame; no words, flags or kits."""
    ident = spec.get("identity")
    if not ident:
        return
    lib = library.load_library()
    problems = []
    allowed = {"number", "number_style", "number_colour", "number_outline", "number_places", "emblem", "layout", "panel", "piping"}
    extra = sorted(set(ident) - allowed)
    if extra:
        problems.append(f"identity fields not allowed (no text, names, flags or team kits): {', '.join(extra)}")
    n = ident.get("number")
    if n is not None:
        if isinstance(n, bool) or not (isinstance(n, int) or (isinstance(n, str) and n.isdigit())) or not 0 <= int(n) <= 99:
            problems.append(f"identity.number must be a whole number 0-99 (got {n!r}); letters and words are blocked")
        if str(ident.get("number_style", "block")) not in identity.STYLES:
            problems.append(f"number_style must be one of {identity.STYLES}")
        bad = [x for x in ident.get("number_places") or [] if x not in ("back", "chest", "sleeve")]
        if bad:
            problems.append(f"number_places unknown: {bad}")
    em = ident.get("emblem")
    if em:
        if em.get("frame", "shield") not in ("shield", "circle", "wreath"):
            problems.append("emblem frame must be shield, circle or wreath")
        if em.get("element") and em["element"] not in lib:
            problems.append(f"emblem element '{em['element']}' is not in the library")
        extra = sorted(set(em) - {"frame", "element", "colour", "accent"})
        if extra:
            problems.append(f"emblem fields not allowed: {', '.join(extra)}")
    if ident.get("layout") not in (None, "racing"):
        problems.append("identity.layout must be racing (or left out)")
    rep.res("identity", not problems, "; ".join(problems) if problems else
            "digits only" if n is not None else "emblem / layout only")


def check_family(rep, raw, resolved):
    fam = str(raw.get("family", "")).lower()
    used = recipes.families_used(resolved)
    problems = []
    if fam not in ("decorated", "print", "combined", "realistic"):
        problems.append("family must be decorated, print, combined or realistic")
    elif fam == "realistic":
        if "print" in used:
            problems.append("family realistic cannot contain a print (identity graphics and small decor are fine)")
        if not recipes.realistic_used(resolved):
            problems.append("family realistic needs a material or garment_kind on torso or legs")
        used = used | {"realistic"}
    elif fam == "print" and "print" not in used:
        problems.append("family print needs a print (torso decor `print` or a print recipe)")
    elif fam == "decorated" and "print" in used:
        problems.append("family decorated cannot contain a print (use combined)")
    elif fam == "combined" and used != {"print", "decorated"}:
        problems.append("family combined needs a print and at least one small decoration")
    rep.res("family", not problems, "; ".join(problems) if problems else f"{fam} ({', '.join(sorted(used)) or 'plain'})")


def _thumb(path):
    regions = load_regions()
    tp = regions["garments"]["shirt"]["panels"]
    img = Image.open(path).convert("RGB")
    parts = [img.crop((tp[f]["x"], tp[f]["y"], tp[f]["x"] + tp[f]["w"], tp[f]["y"] + tp[f]["h"])).resize((16, 16), Image.BILINEAR)
             for f in ("torso.front", "torso.back")]
    return [v for im in parts for px in im.get_flattened_data() for v in px]


def check_duplicates(rep, spec_path, resolved, renders):
    """Reject a design that is nearly identical to one already in specs/ (or in the same folder)."""
    me = Path(spec_path).resolve()
    others = {q.resolve() for q in list((ROOT / "specs").glob("*.yaml")) + list(me.parent.glob("*.yaml"))
              if not q.name.startswith("_") and q.resolve() != me}
    sig = recipes.signature(resolved)
    my_png = Path(renders) / f"{resolved.get('id')}-shirt.png"
    my_thumb = _thumb(my_png) if my_png.exists() else None
    worst, hits = 0.0, []
    for q in sorted(others):
        try:
            other = recipes.resolve(yaml.safe_load(q.read_text(encoding="utf-8")))
        except SystemExit:
            continue
        if other.get("id") == resolved.get("id"):
            continue
        s = recipes.similarity(sig, recipes.signature(other))
        worst = max(worst, s)
        if s >= DUP_SIMILARITY:
            hits.append(f"{other.get('id')} (design overlap {s:.0%})")
            continue
        for rdir in {Path(renders), q.parent / "renders", ROOT / "renders"}:
            op = rdir / f"{other.get('id')}-shirt.png"
            if my_thumb and op.exists():
                b = _thumb(op)
                mae = sum(abs(x - y) for x, y in zip(my_thumb, b)) / len(b)
                if mae < DUP_PIXEL_MAE:
                    hits.append(f"{other.get('id')} (renders differ by only {mae:.1f}/255)")
                break
    rep.res("duplicate", not hits, ("near-duplicate of " + ", ".join(hits)) if hits else f"closest design overlap {worst:.0%}")


def check_library(rep):
    """Every library element is original or has a CC0 / public-domain licence entry; nothing blocked."""
    lib = library.load_library()
    lic = (ROOT / "styles" / "references" / "LICENSES.md")
    lic_text = lic.read_text(encoding="utf-8") if lic.exists() else ""
    problems = []
    for eid, el in lib.items():
        text = f"{eid} {el.get('name', '')} {el.get('motif', '')}".lower()
        bad = library.blocked(text)
        if bad:
            problems.append(f"{eid}: blocked subject ({', '.join(bad)})")
        if el.get("source") == "original":
            continue
        if el.get("source") == "owner-generated":          # one LICENSES.md line per source sheet
            if f"`{el.get('sheet')}.png`" not in lic_text:
                problems.append(f"{eid}: source sheet {el.get('sheet')} missing from LICENSES.md")
            continue
        L = el.get("license") or {}
        if not (L.get("source_url") and L.get("licence")):
            problems.append(f"{eid}: public-domain element without source URL and licence")
        elif f"`{eid}`" not in lic_text:
            problems.append(f"{eid}: missing from LICENSES.md")
    n_pd = sum(1 for e in lib.values() if e.get("source") == "public-domain")
    n_own = sum(1 for e in lib.values() if e.get("source") == "owner-generated")
    rep.res("library", not problems, "; ".join(problems[:5]) if problems else
            f"{len(lib)} elements ({n_pd} public domain, {n_own} owner-generated, all licensed)")


def validate_outfit(spec_path, renders):
    regions = load_regions()
    raw = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    spec = recipes.resolve(raw)
    oid = spec.get("id") or Path(spec_path).stem
    rep = Report()
    global CUT_EDGES
    CUT_EDGES = str(((spec.get("torso") or {}).get("cut") or {}).get("style", "sleeved")) != "sleeved"
    if raw.get("uploaded"):                          # duplicate protection: never queue an outfit twice
        up = raw.get("upload") or {}
        rep.res("upload", False, f"already uploaded (shirt {up.get('shirt_asset_id', '?')}, pants {up.get('pants_asset_id', '?')}, "
                                 f"{up.get('date', '?')}); refusing to queue it again")
    coverage = str(spec.get("coverage", "full"))
    garments = {"top_only": ("shirt",), "bottom_only": ("pants",)}.get(coverage, ("shirt", "pants"))
    files = {g: Path(renders) / f"{oid}-{g}.png" for g in garments}
    missing = [str(p) for p in files.values() if not p.exists()]
    rep.res("files", not missing, ("missing: " + ", ".join(missing)) if missing else " + ".join(garments) + " present")
    check_listings(rep, spec)
    check_palette(rep, spec)
    check_decor(rep, spec)
    check_family(rep, raw, spec)
    check_realistic(rep, spec)
    check_shading(rep, spec)
    check_identity(rep, spec)
    check_library(rep)
    check_duplicates(rep, spec_path, spec, renders)
    if missing:
        return oid, rep
    if coverage != "full":   # separates: one file, so no torso-identity or cross-file checks
        img = check_file(rep, files[garments[0]], garments[0], regions, spec.get("legs") if garments[0] == "pants" else None)
        if img is None:
            return oid, rep
        check_cut(rep, spec, img)
        zone = "shoulder" if garments[0] == "shirt" else "hip"
        fails, worst = check_seam_list(img, regions["garments"][garments[0]]["panels"], regions["outfit_seams"][zone])
        if zone == "hip" or not (spec.get("arms") or {}).get("sleeve_contrast"):
            rep.res(zone, not fails, "; ".join(fails[:4]) if fails else f"worst mean diff {worst:.1f}")
        return oid, rep
    shirt = check_file(rep, files["shirt"], "shirt", regions)
    pants = check_file(rep, files["pants"], "pants", regions, spec.get("legs") or {})
    if shirt is None or pants is None:
        return oid, rep
    tp = regions["garments"]["shirt"]["panels"]
    diff_faces = []
    for f in TORSO_FACES:
        p = tp[f"torso.{f}"]
        box = (p["x"], p["y"], p["x"] + p["w"], p["y"] + p["h"])
        if ImageChops.difference(shirt.crop(box), pants.crop(box)).getbbox(alpha_only=False):  # RGB + alpha
            diff_faces.append(f)
    rep.res("torso", not diff_faces, ("differs on: " + ", ".join(diff_faces)) if diff_faces
            else "6 torso panels identical in both files")
    check_cut(rep, spec, shirt)
    contrast = bool((spec.get("arms") or {}).get("sleeve_contrast"))
    for zone, img, garment in (("shoulder", shirt, "shirt"), ("hip", pants, "pants")):
        if zone == "shoulder" and contrast:
            rep.lines.append("  [SKIP] shoulder: arms.sleeve_contrast is true (visible shoulder seam drawn)")
            continue
        fails, worst = check_seam_list(img, regions["garments"][garment]["panels"], regions["outfit_seams"][zone])
        hint = " (contrast sleeves? set arms.sleeve_contrast: true)" if zone == "shoulder" and fails else ""
        rep.res(zone, not fails, ("; ".join(fails[:4]) + hint) if fails
                else f"{len(regions['outfit_seams'][zone])} pairs, worst mean diff {worst:.1f}")
    return oid, rep


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--renders", default=str(ROOT / "renders"))
    a = ap.parse_args()
    specs = list(a.specs)
    if a.all:
        specs += [str(p) for p in sorted((ROOT / "specs").glob("*.yaml")) if not p.name.startswith("_")]
    if not specs:
        ap.error("give outfit spec paths or --all")
    all_ok = True
    for sp in specs:
        oid, rep = validate_outfit(sp, a.renders)
        all_ok &= rep.ok
        print(f"{'PASS' if rep.ok else 'FAIL'}  outfit {oid}")
        print("\n".join(rep.lines))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

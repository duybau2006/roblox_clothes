"""Recipe engine: request a design by recipe instead of placing every element by hand.

Spec field (top level):
  recipes:
    - family: print                      # print | decorated
      style: vamp-goth                   # picks elements tagged with this style
      template: symmetric_pair           # print: centered_stack | symmetric_pair | offcentre_figure | allover_faded
                                         # decorated: chest_sleeves | pocket_back | chest_scatter | scatter_all | thigh_knees
      placement: front                   # print only: front (default: main graphic on the front) | back
      tags: [skull, wings, rose]         # 2-5 element tags (motif names such as skull, wings, rose, star, moth ...)
      ink: "#E8E8E8"                     # one ink colour (print) or motif colour (decorated)
      distress: 2                        # print only: 0-3 or {drips, splatter, scratches, halftone, cracked, worn}
      seed: 7                            # same recipe + same seed = same design; new seed = new arrangement
      wrap: false                        # print only: let the print wrap onto the sides

resolve(spec) expands recipes into concrete `decor` entries (written to renders/<id>-resolved.yaml).
CLI:
  python tools/recipes.py suggest --style vamp-goth [--family print]   untried template x main-element combos
  python tools/recipes.py log                                           show the recipe log
"""
import argparse
import copy
import csv
import datetime
import random
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import library                     # noqa: E402
from clothing import ROOT          # noqa: E402
from prints import TEMPLATES as PRINT_TEMPLATES   # noqa: E402

DECOR_TEMPLATES = {
    "chest_sleeves": [("torso", "chest", 16), ("arms", "sleeve", 8)],
    "pocket_back": [("torso", "pocket", 6), ("torso", "back", 20)],
    "chest_scatter": [("torso", "chest", 15), ("arms", "scatter", 3)],
    "scatter_all": [("torso", "scatter", 3.2), ("arms", "scatter", 3)],
    "thigh_knees": [("legs", "thigh", 8), ("legs", "scatter", 3)],
    "border_trim": [("torso", "border", 8), ("arms", "border", 6), ("legs", "border", 6)],   # owner border tiles
}
SMALL_KINDS = ("motif", "hero")             # what chest / sleeve / print placements may pick
BORDER_KINDS = ("border",)
# Realistic-family archetypes: garment structure only. "$0".."$3" are replaced by the recipe's `colours`
# (body, second, accent, shoes). Anything the spec sets itself wins over the archetype.
ARCHETYPES = {
    "basic_tee_jeans": {
        "torso": {"garment_kind": "tee", "material": "cotton", "palette": ["$0"], "details": ["crew collar"], "hem": "plain", "hem_line": 98},
        "arms": {"sleeves": "short"},
        "legs": {"type": "trousers", "garment_kind": "jeans", "material": "denim", "waist_line": 96, "waistband": "plain",
                 "palette": ["$1"], "parts": ["belt", "jeans_fly", "jeans_pockets"], "shoes": "sneakers",
                 "shoe_style": "sneaker", "shoe_palette": ["$3", "$3", "$2"]}},
    "knit_stripes": {
        "torso": {"garment_kind": "sweater", "material": "knit", "palette": ["$0", "$1"], "base_pattern": "stripes",
                  "pattern": {"width": 8}, "details": ["crew collar"], "hem": "rib", "hem_line": 108},
        "arms": {"sleeves": "long", "details": ["rib cuffs"]},
        "legs": {"type": "trousers", "garment_kind": "trousers", "material": "cotton", "waist_line": 96, "waistband": "plain",
                 "palette": ["$2"], "parts": ["crease"], "shoes": "loafers", "shoe_style": "loafer", "shoe_palette": ["$3", "$3"]}},
    "racing_jersey": {
        "torso": {"garment_kind": "tee", "material": "nylon", "palette": ["$0", "$1"], "details": ["crew collar"], "hem": "plain", "hem_line": 104},
        "arms": {"sleeves": "short"},
        "legs": {"type": "trousers", "garment_kind": "joggers", "material": "nylon", "waist_line": 96, "waistband": "elastic",
                 "palette": ["$0", "$1"], "details": ["rib cuffs"], "shoes": "sneakers", "shoe_style": "sneaker",
                 "shoe_palette": ["$3", "$3", "$2"]},
        "identity": {"number_style": "racing", "number_colour": "$1", "number_outline": "$0", "number_places": ["back", "chest", "sleeve"],
                     "layout": "racing", "panel": "$2", "piping": "$1"}},
    "suit_waistcoat": {
        "torso": {"garment_kind": "suit", "material": "cotton", "palette": ["$0", "$0", "$2"], "details": [], "hem": "none", "hem_line": 108,
                  "parts": [{"name": "waistcoat", "colour": "$1"}, {"name": "lapels", "shirt": "$3"}, {"name": "tie", "colour": "$2"},
                            {"name": "trim_hem", "colour": "$2"}]},
        "arms": {"sleeves": "long", "parts": ["cuff_button", {"name": "trim_cuff", "colour": "$2"}]},
        "legs": {"type": "trousers", "garment_kind": "trousers", "material": "cotton", "waist_line": 96, "waistband": "plain",
                 "palette": ["$0"], "parts": ["crease"], "shoes": "loafers", "shoe_style": "loafer", "shoe_palette": ["$1", "$1"]}},
    "bomber_badge": {
        "torso": {"garment_kind": "bomber", "material": "nylon", "palette": ["$0", "$1", "$2"], "details": [], "hem": "rib", "hem_line": 104,
                  "parts": ["collar_stand", "zip_full", "chest_pocket"]},
        "arms": {"sleeves": "long", "details": ["rib cuffs"]},
        "legs": {"type": "trousers", "garment_kind": "trousers", "material": "cotton", "waist_line": 96, "waistband": "plain",
                 "palette": ["$1"], "parts": ["belt", "cargo_pockets"], "shoes": "boots", "shoe_style": "boot",
                 "shoe_palette": ["$1", "$1", "$2"]},
        "identity": {"emblem": {"frame": "shield", "element": "star-5", "colour": "$3", "accent": "$2"}}},
    "corset_trousers": {
        "torso": {"garment_kind": "corset", "material": "leather", "palette": ["$0", "$0", "$2"], "details": [], "hem": "plain", "hem_line": 100,
                  "cut": {"style": "tank", "neckline": "square", "depth": 8, "width": 18, "strap_width": 8}, "parts": ["lacing"]},
        "arms": {"sleeves": "long"},
        "legs": {"type": "trousers", "garment_kind": "trousers", "material": "cotton", "waist_line": 98, "waistband": "plain",
                 "palette": ["$1"], "parts": ["belt"], "shoes": "boots", "shoe_style": "boot", "shoe_palette": ["$0", "$0", "$2"]}},
    "pleated_skirt_bows": {
        "torso": {"garment_kind": "shirt", "material": "cotton", "palette": ["$0", "$0", "$2"], "details": [], "hem": "none", "hem_line": 98,
                  "parts": ["collar_shirt"]},
        "arms": {"sleeves": "short"},
        "legs": {"type": "skirt", "garment_kind": "skirt", "material": "cotton", "waist_line": 96, "waistband": "plain", "palette": ["$1"],
                 "details": ["pleats"], "skirt_length": 44, "legwear": "socks", "legwear_palette": ["$0"], "sock_top": 74,
                 "shoes": "loafers", "shoe_style": "loafer", "shoe_palette": ["$3", "$3"]}},
    "sports_shorts": {
        "torso": {"garment_kind": "tee", "material": "cotton", "palette": ["$0", "$1"], "details": ["crew collar"], "hem": "plain", "hem_line": 104,
                  "parts": [{"name": "piping", "colour": "$2"}]},
        "arms": {"sleeves": "short"},
        "legs": {"type": "shorts", "garment_kind": "shorts", "material": "nylon", "waist_line": 96, "waistband": "elastic",
                 "palette": ["$1", "$1"], "shorts_length": 44, "legwear": "socks", "legwear_palette": ["$0"], "sock_top": 84,
                 "parts": [{"name": "piping", "colour": "$2"}], "shoes": "sneakers", "shoe_style": "sneaker", "shoe_palette": ["$3", "$3", "$2"]}},
    "crop_lowrise": {
        "torso": {"garment_kind": "tee", "material": "cotton", "palette": ["$0"], "details": ["crew collar"], "hem": "plain", "hem_line": 88},
        "arms": {"sleeves": "short"},
        "legs": {"type": "trousers", "garment_kind": "jeans", "material": "denim", "waist_line": 104, "waistband": "plain",
                 "palette": ["$1"], "parts": ["belt", "jeans_fly", "jeans_pockets"], "shoes": "sneakers", "shoe_style": "sneaker",
                 "shoe_palette": ["$3", "$3", "$2"]}},
}
# default shading layers for realistic recipes (owner-supplied templates; `procedural: true` opts out)
DEFAULT_LAYERS = ["own-shade-all", "own-shade-1", "own-shade-2", "own-shade-3"]
DEFAULT_STRENGTH = {"own-shade-1": 1.0, "own-shade-2": 1.0, "own-shade-3": 0.8}
LOG = ROOT / "trends" / "recipe-log.csv"
LOG_FIELDS = ["date", "spec", "style", "family", "template", "main_element", "elements", "ink", "seed"]


def _rnd(recipe):
    key = f"{recipe.get('style')}|{recipe.get('family')}|{recipe.get('template')}|{','.join(recipe.get('tags', []))}|{recipe.get('seed', 0)}"
    return random.Random(zlib.crc32(key.encode()))


def pick_elements(recipe, family, kinds=SMALL_KINDS):
    rnd = _rnd(recipe)
    style = recipe.get("style")
    chosen = []
    for tag in recipe.get("tags", []):
        cands = [e for e in library.find(styles=[style] if style else None, family=family, tag=tag, kinds=kinds) if e["id"] not in chosen]
        if not cands:
            cands = [e for e in library.find(family=family, tag=tag, kinds=kinds) if e["id"] not in chosen]
        if not cands:
            raise SystemExit(f"recipe: no library element matches tag '{tag}' (family {family})")
        if family == "decorated":   # small placements need elements that read small
            small = [e for e in cands if e.get("size") in ("small", "medium")]
            cands = small or cands
        chosen.append(rnd.choice(sorted(cands, key=lambda e: e["id"]))["id"])
    return chosen


def expand(recipe):
    """-> list of (section, decor entry)."""
    family = recipe.get("family")
    tags = recipe.get("tags") or []
    if not 2 <= len(tags) <= 5:
        raise SystemExit("recipe: give 2-5 tags")
    els = pick_elements(recipe, family, BORDER_KINDS if recipe.get("template") == "border_trim" else SMALL_KINDS)
    ink = recipe.get("ink", "#FFFFFF")
    if family == "print":
        t = recipe.get("template", "centered_stack")
        if t not in PRINT_TEMPLATES:
            raise SystemExit(f"recipe: print template must be one of {PRINT_TEMPLATES}")
        return [("torso", {"print": {"placement": recipe.get("placement", "front"), "template": t, "elements": els,
                                     "ink": ink, "distress": recipe.get("distress", 1), "seed": int(recipe.get("seed", 0)),
                                     "wrap": bool(recipe.get("wrap", False)), "scale": recipe.get("scale", 1.0)}})]
    if family == "decorated":
        t = recipe.get("template", "chest_sleeves")
        if t not in DECOR_TEMPLATES:
            raise SystemExit(f"recipe: decorated template must be one of {list(DECOR_TEMPLATES)}")
        if t == "border_trim":
            els = pick_elements(recipe, family, BORDER_KINDS)
            return [(section, {"element": els[i % len(els)], "layout": "border", "colour": ink, "height": size})
                    for i, (section, _, size) in enumerate(DECOR_TEMPLATES[t])]
        out = []
        for i, (section, layout, size) in enumerate(DECOR_TEMPLATES[t]):
            e = {"element": els[i % len(els)], "layout": layout, "colour": ink, "size": size}
            if layout in ("chest", "back") and len(els) > 2:
                e["pair"] = els[2]
            out.append((section, e))
        return out
    raise SystemExit("recipe: family must be print or decorated")


def _fill(v, cols):
    if isinstance(v, str) and len(v) == 2 and v[0] == "$":
        return cols[min(int(v[1]), len(cols) - 1)]
    if isinstance(v, list):
        return [_fill(x, cols) for x in v]
    if isinstance(v, dict):
        return {k: _fill(x, cols) for k, x in v.items()}
    return v


def _merge(base, top):
    """Deep merge: values in `top` (the spec) win; dicts merge, lists are replaced."""
    out = dict(base)
    for k, v in top.items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def expand_realistic(recipe):
    """-> partial spec from an archetype, coloured by recipe.colours, with shading seed / layer and identity."""
    t = recipe.get("template")
    if t not in ARCHETYPES:
        raise SystemExit(f"recipe: realistic template must be one of {list(ARCHETYPES)}")
    cols = recipe.get("colours") or ["#808080"]
    part = _fill(copy.deepcopy(ARCHETYPES[t]), cols)
    part["shading"] = {"mode": "realistic", "seed": int(recipe.get("seed", 0)), "wrinkles": recipe.get("wrinkles", 1.0)}
    layer = recipe.get("layer")                              # default (no layer given): own-shade-all, set by render.py
    if recipe.get("procedural"):
        layer = "none"
    if layer:
        part["shading"].update(layer=layer, strength=recipe.get("strength", DEFAULT_STRENGTH.get(layer, 1.0)))
    if recipe.get("number") is not None:
        part.setdefault("identity", {})["number"] = int(recipe["number"])
    ink = recipe.get("ink") or cols[min(2, len(cols) - 1)]
    sub = {**recipe, "family": "decorated"}
    if recipe.get("tags"):                                   # small library motifs: chest badge (+ sleeve)
        els = pick_elements(sub, "decorated")
        part["torso"].setdefault("decor", []).append({"element": els[0], "layout": "chest", "colour": ink, "size": 12, "_recipe": True})
        if len(els) > 1:
            part["arms"].setdefault("decor", []).append({"element": els[1], "layout": "sleeve", "colour": ink, "size": 7, "_recipe": True})
    if recipe.get("swatch"):                                 # owner fabric swatch as the torso fabric (recoloured)
        el = pick_elements({**sub, "tags": [recipe["swatch"]]}, None, ("swatch",))[0]
        part["torso"].update(base_pattern="swatch", pattern={"element": el})
    if recipe.get("border"):                                 # owner border tile at the torso hem
        el = pick_elements({**sub, "tags": [recipe["border"]]}, None, BORDER_KINDS)[0]
        part["torso"].setdefault("decor", []).append({"element": el, "layout": "border", "colour": ink, "height": 7, "_recipe": True})
    if recipe.get("emblem"):
        part.setdefault("identity", {})["emblem"] = _merge((part.get("identity") or {}).get("emblem") or {}, recipe["emblem"])
    return part


def resolve(spec):
    """Copy of spec with every recipe expanded: decorated / print recipes into decor entries,
    realistic recipes into archetype structure (spec fields win)."""
    out = copy.deepcopy(spec)
    for r in [r for r in out.get("recipes") or [] if r.get("family") == "realistic"]:
        out = _merge(expand_realistic(r), out)
    for r in out.get("recipes") or []:
        if r.get("family") == "realistic":
            continue
        for section, entry in expand(r):
            out.setdefault(section, {}).setdefault("decor", []).append(dict(entry, _recipe=True))
    return out


def families_used(resolved):
    fams = set()
    for key in ("torso", "arms", "legs"):
        for d in (resolved.get(key) or {}).get("decor") or []:
            fams.add("print" if "print" in d else "decorated")
    return fams


def realistic_used(resolved):
    """True when the spec uses realistic-family features (materials, garment kinds, realistic shading)."""
    if (resolved.get("shading") or {}).get("mode") == "realistic":
        return True
    return any((resolved.get(k) or {}).get(f) for k in ("torso", "legs") for f in ("material", "garment_kind"))


def signature(resolved):
    """Design tokens for the near-duplicate check."""
    tok = set()
    for key in ("torso", "arms", "legs"):
        sec = resolved.get(key) or {}
        tok.add(f"{key}:pattern:{sec.get('base_pattern', 'solid')}")
        pal = sec.get("palette") or []
        if pal:
            tok.add(f"{key}:body:{pal[0].upper()}")
        tok.add(f"{key}:type:{sec.get('type', '')}:{sec.get('hem_line', '')}:{sec.get('sleeves', '')}")
        for d in sec.get("decor") or []:
            if "print" in d:
                p = d["print"]
                tok.add(f"print:{p.get('placement')}:{p.get('template')}")
                tok.add(f"print:main:{(p.get('elements') or ['?'])[0]}")
                tok.update(f"print:el:{e}" for e in p.get("elements") or [])
                tok.add(f"print:ink:{str(p.get('ink', '')).upper()}")
            else:
                tok.add(f"{key}:decor:{d.get('element') or d.get('motif')}:{d.get('layout')}")
        # realistic-family tokens (material, garment kind, construction parts, cut, shoes)
        for f in ("material", "garment_kind", "shoe_style"):
            if sec.get(f):
                tok.add(f"{key}:{f}:{sec[f]}")
        for prt in sec.get("parts") or []:
            tok.add(f"{key}:part:{prt if isinstance(prt, str) else prt.get('name')}")
        if sec.get("cut"):
            c = sec["cut"]
            tok.add(f"{key}:cut:{c.get('style', 'sleeved')}:{c.get('neckline', 'crew')}")
    ident = resolved.get("identity") or {}
    if ident.get("number") is not None:
        tok.add(f"id:number:{ident['number']}:{ident.get('number_style', 'block')}")
    if ident.get("emblem"):
        tok.add(f"id:emblem:{ident['emblem'].get('frame')}:{ident['emblem'].get('element')}")
    if ident.get("layout"):
        tok.add(f"id:layout:{ident['layout']}")
    sh = resolved.get("shading") or {}
    if sh.get("layer"):
        tok.add(f"shading:layer:{sh['layer']}")
    if resolved.get("coverage", "full") != "full":
        tok.add(f"coverage:{resolved['coverage']}")
    return tok


def similarity(a, b):
    return len(a & b) / max(1, len(a | b))


def log_recipes(spec, spec_path):
    """Record each recipe of a store spec (specs/ only) in trends/recipe-log.csv (one row per recipe)."""
    if Path(spec_path).resolve().parent != (ROOT / "specs").resolve():
        return
    rows = []
    if LOG.exists():
        with LOG.open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["spec"] != spec.get("id")]
    for r in spec.get("recipes") or []:
        if r.get("family") == "realistic":
            rows.append({"date": datetime.date.today().isoformat(), "spec": spec.get("id"), "style": r.get("style"),
                         "family": "realistic", "template": r.get("template"), "main_element": r.get("layer") or "procedural",
                         "elements": "", "ink": " ".join(r.get("colours") or []), "seed": r.get("seed", 0)})
            continue
        els = pick_elements(r, r.get("family"))
        rows.append({"date": datetime.date.today().isoformat(), "spec": spec.get("id"), "style": r.get("style"),
                     "family": r.get("family"), "template": r.get("template"), "main_element": els[0],
                     "elements": " ".join(els), "ink": r.get("ink"), "seed": r.get("seed", 0)})
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        w.writeheader()
        w.writerows(rows)


def suggest(style, family=None, limit=15):
    used = set()
    if LOG.exists():
        with LOG.open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["style"] == style]
        used = {(r["family"], r["template"], library.element(r["main_element"])["motif"])
                for r in rows if r["main_element"] in library.load_library()}
        used |= {("realistic", r["template"], r["main_element"]) for r in rows if r["family"] == "realistic"}
    if family == "realistic":     # archetype x shading source (procedural or a collected layer)
        import shading_custom
        out = [("realistic", t, src) for t in ARCHETYPES for src in [*DEFAULT_LAYERS, "procedural"]
               if ("realistic", t, src) not in used]
        random.Random(len(used)).shuffle(out)
        return out[:limit]
    fams = [family] if family else ["print", "decorated"]
    motifs = sorted({e["motif"] for e in library.find(styles=[style])})
    out = []
    for fam in fams:
        temps = PRINT_TEMPLATES if fam == "print" else list(DECOR_TEMPLATES)
        for t in temps:
            for m in motifs:
                if not library.find(styles=[style], motif=m, family=fam):
                    continue
                if (fam, t, m) not in used:
                    out.append((fam, t, m))
    random.Random(len(used)).shuffle(out)
    return out[:limit]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("suggest")
    s.add_argument("--style", required=True)
    s.add_argument("--family", choices=["print", "decorated", "realistic"])
    sub.add_parser("log")
    a = ap.parse_args()
    if a.cmd == "suggest":
        for fam, t, m in suggest(a.style, a.family):
            print(f"{fam:10} {t:18} " + (f"shading: {m}" if fam == "realistic" else f"main element tag: {m}"))
    else:
        print(LOG.read_text(encoding="utf-8") if LOG.exists() else "(no recipes logged yet)")


if __name__ == "__main__":
    main()

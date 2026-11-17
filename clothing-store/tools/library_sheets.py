"""Element previews, per-style library sheets and LICENSES.md for styles/references/library/.

Writes:
  styles/references/library/previews/<id>.png     one tile per element (ink on dark fabric)
  styles/references/<style>/library.png             every element tagged with that style
  styles/references/LICENSES.md                     provenance of every element (original or CC0 with source)
  styles/references/library/INDEX.md               table of elements with tags
Run: python tools/library_sheets.py
"""
import collections
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import library                                   # noqa: E402
from clothing import ROOT, S, M, Part, Canvas, rgba, load_regions   # noqa: E402

TILE, ZOOM = 64, 2
BG, INK = (36, 36, 40), (236, 232, 222)
STYLES = ["y2k", "vamp-goth", "emo", "baddie", "grunge", "gen-z", "archive", "soft-girl", "preppy", "cottagecore",
          "christmas", "athleisure"]


def tile(part, el):
    c = Canvas(part)
    c.band(-M, 200, rgba(BG))
    m = library.Masks(part)
    m.draw(el, 64, 40, 26)
    m.composite(c, library.ink_tones(INK))
    t = c.strip().crop((32 * S, (M + 8) * S, 96 * S, (M + 72) * S)).resize((TILE, TILE), Image.LANCZOS)
    return t.resize((TILE * ZOOM, TILE * ZOOM), Image.NEAREST).convert("RGB")


def font(px):
    try:
        return ImageFont.truetype("arialbd.ttf", px)
    except OSError:
        return ImageFont.load_default()


def sheet(items, cols=8):
    w = TILE * ZOOM
    rows = (len(items) + cols - 1) // cols
    img = Image.new("RGB", (cols * (w + 8) + 8, rows * (w + 30) + 8), "white")
    d = ImageDraw.Draw(img)
    for i, (eid, t) in enumerate(items):
        x, y = 8 + (i % cols) * (w + 8), 8 + (i // cols) * (w + 30)
        img.paste(t, (x, y))
        d.text((x + w / 2, y + w + 12), eid[:22], fill=(30, 30, 30), font=font(11), anchor="mm")
    return img


def main():
    lib = library.load_library()
    part = Part("shirt", "torso", load_regions())
    prev = library.LIB / "previews"
    prev.mkdir(exist_ok=True)
    tiles = {}
    for eid, el in lib.items():
        tiles[eid] = tile(part, el)
        tiles[eid].save(prev / f"{eid}.png")
    counts = collections.Counter()
    for style in STYLES:
        ids = [e for e in lib if style in lib[e].get("styles", [])]
        counts[style] = len(ids)
        d = ROOT / "styles" / "references" / style
        d.mkdir(parents=True, exist_ok=True)
        sheet([(e, tiles[e]) for e in ids]).save(d / "library.png")
    # INDEX.md
    lines = ["# Element library", "", f"{len(lib)} elements. Previews in [previews/](previews/). Regenerate with "
             "`python tools/build_library.py`, `python tools/import_public_domain.py <dir>`, `python tools/library_sheets.py`.",
             "", "| Elements per style | " + " | ".join(STYLES) + " |", "|---|" + "---|" * len(STYLES),
             "| count | " + " | ".join(str(counts[s]) for s in STYLES) + " |", "",
             "| id | motif | styles | mood | size | families | source |", "|---|---|---|---|---|---|---|"]
    for eid, el in lib.items():
        lines.append(f"| `{eid}` | {el['motif']} | {', '.join(el['styles'])} | {', '.join(el.get('mood', []))} | "
                     f"{el.get('size')} | {', '.join(el['families'])} | {el['source']} |")
    (library.LIB / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # LICENSES.md
    lic = ["# Licences and provenance of library elements", "",
           "Every element in `library/` is either **original** (drawn as code in `tools/build_library.py`, owned by this "
           "project) or **public domain / CC0** (imported by `tools/import_public_domain.py` after the museum API "
           "confirmed `isPublicDomain = true`). Elements with an unclear licence are never imported.", "",
           "## Public domain / CC0", "", "| element | licence | source | title, artist, date | checked |", "|---|---|---|---|---|"]
    for eid, el in lib.items():
        if el["source"] == "public-domain":
            L = el.get("license") or {}
            lic.append(f"| `{eid}` | {L.get('licence')} | [{L.get('source_url')}]({L.get('source_url')}) | "
                       f"{L.get('title')}, {L.get('artist')}, {L.get('date')} | {L.get('checked')} |")
    lic += ["", "## Original", "", "Drawn for this project: " + ", ".join(f"`{e}`" for e, el in lib.items() if el["source"] == "original") + "."]
    own = {}
    for e, el in lib.items():
        if el["source"] == "owner-generated":
            own.setdefault(el["sheet"], []).append(e)
    if own:
        lic += ["", "## Owner-generated artwork", "",
                "Motif sheets made by the store owner with ChatGPT and handed over as the owner's own artwork. "
                "Elements are cut out by `tools/import_motifs.py`; held items (crosses, halos, figures, brand look-alikes, "
                "money, lips, blood, wounds, words) are in `styles/references/held/` and never enter the library.", "",
                "| source sheet | licence | elements imported |", "|---|---|---|"]
        for sh in sorted(own):
            lic.append(f"| `{sh}.png` | generated by the owner with ChatGPT, 2026-11-16 | {len(own[sh])} (ids `{sh.replace('sheet-', 'g')}-*`) |")
    # collected shading layers (templates/shading/custom/, imported by tools/shading_custom.py)
    import json
    import shading_custom
    lic += ["", "## Shading layers (templates/shading/custom/)", "",
            "Greyscale shadow maps on the 585x559 template, seam-healed by `tools/shading_custom.py`. "
            "Any family may name one in `shading.layer`.", "",
            "| layer | author | licence | credit | source | fetched |", "|---|---|---|---|---|---|"]
    all_layers = shading_custom.layers()
    for lid, m in all_layers.items():
        if m.get("provenance") == "owner-supplied":
            continue
        lic.append(f"| `{lid}` | {m.get('author')} | {m.get('licence')} | {m.get('credit')} | "
                   f"[{m.get('source_url')}]({m.get('source_url')}) | {m.get('fetched')} |")
    owner = {k: v for k, v in all_layers.items() if v.get("provenance") == "owner-supplied"}
    if owner:
        lic += ["", "### Owner-supplied shading layers (the owner's own work, confirmed 2026-11-16)", "",
                "Made by the store owner, who confirmed on 2026-11-16 that they hold the rights. Used on every outfit.", "",
                "| layer | style | received | source | licence | how it was converted |", "|---|---|---|---|---|---|"]
        for lid, m in owner.items():
            lic.append(f"| `{lid}` | {m.get('style')} | {m.get('fetched')} | {m.get('source_url')} | {m.get('licence')} | {m.get('notes')} |")
    skipped = json.loads(shading_custom.SKIPPED.read_text(encoding="utf-8")) if shading_custom.SKIPPED.exists() else []
    lic += ["", "## Skipped (not imported)", "",
            "Unclear, personal-use-only, credit-required (credits cannot ride along in listings), unlicensed or "
            "not-a-texture items. Nothing here is in the repo.", "", "| group | item | source | reason |", "|---|---|---|---|"]
    for s in skipped:
        lic.append(f"| {s.get('group')} | {s.get('item')} | {s.get('source_url') or '-'} | {s.get('reason')} |")
    (ROOT / "styles" / "references" / "LICENSES.md").write_text("\n".join(lic) + "\n", encoding="utf-8")
    sheet([(e, tiles[e]) for e in lib], cols=12).save(library.LIB / "all.png")
    print("elements:", len(lib), "| per style:", dict(counts))


if __name__ == "__main__":
    main()
